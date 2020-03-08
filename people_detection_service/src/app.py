import logging
from time import sleep
from typing import Tuple

import requests
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from keras_retinanet.models import load_model
import tensorflow as tf
from tensorflow.python.keras.backend import set_session

from .resources import PeopleDetection
from .config import SERVICE_NAME, API_VERSION, SERVICE_SECRET, \
    SERVER_IDENTITY_URL, DISCOVERY_URL, WEIGHTS_PATH, CONFIDENCE_THRESHOLD, \
    CLASSES_TO_FETCH, MAX_IMAGE_DIM

INTER_SERVICES_TOKEN = None
app = Flask(__name__)
GRAPH = None
TF_SESSION = None
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)


def create_api() -> Api:
    global INTER_SERVICES_TOKEN
    secret, INTER_SERVICES_TOKEN = _fetch_config_from_identity_service()
    app.config['JWT_SECRET_KEY'] = secret
    api = Api(app)
    global TF_SESSION
    global GRAPH
    GRAPH = tf.get_default_graph()
    TF_SESSION = tf.Session(graph=GRAPH)
    set_session(TF_SESSION)
    model = load_model(WEIGHTS_PATH)
    api.add_resource(
        PeopleDetection,
        construct_api_url('/detect_people'),
        resource_class_kwargs={
            'model': model,
            'session': TF_SESSION,
            'graph': GRAPH,
            'confidence_threshold': CONFIDENCE_THRESHOLD,
            'classes_to_fetch': CLASSES_TO_FETCH,
            'max_image_dim': MAX_IMAGE_DIM
        }
    )
    return api


def construct_api_url(resource_postfix: str) -> str:
    return f'/{API_VERSION}/{SERVICE_NAME}{resource_postfix}'


def _fetch_config_from_identity_service() -> Tuple[str, str]:
    payload = {'service_name': SERVICE_NAME, 'password': SERVICE_SECRET}
    response = requests.get(
        SERVER_IDENTITY_URL, json=payload, verify=False
    )
    if response.status_code == 200:
        logging.info('Obtained access token and token secret.')
        content = response.json()
        return content['token_secret'], content['service_access_token']
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return _fetch_config_from_identity_service()


def fetch_port() -> int:
    headers = {'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'}
    payload = {'service_names': [SERVICE_NAME]}
    response = requests.get(
        DISCOVERY_URL, headers=headers, json=payload, verify=False
    )
    if response.status_code == 200:
        response_content = response.json()
        return _fetch_port_from_response(response_content=response_content)
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return fetch_port()


def _fetch_port_from_response(response_content: dict) -> int:
    services_found = response_content.get('services_found', [])
    services_matching = list(filter(
        lambda srv_desc: srv_desc['service_name'] == SERVICE_NAME,
        services_found
    ))
    if len(services_matching) != 1:
        raise RuntimeError('Cannot get proper response from discovery service.')
    return services_matching[0]['service_port']


api = create_api()


if __name__ == '__main__':
    port = fetch_port()
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
