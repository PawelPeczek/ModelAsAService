import logging
from time import sleep
from typing import Tuple, List, Dict

import pika
import requests
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from requests import Response

from .resources.asynchronous import \
    AsynchronousProcessingStart, AsynchronousProcessingResultsFetch
from .resources.synchronous import ProcessingPipeline
from .resources.users import Register, Login, TokenRefresh, LogoutAccessToken, \
    LogoutRefreshToken
from .config import API_VERSION, SERVICE_NAME, \
    SERVER_IDENTITY_URL, DISCOVERY_URL, SERVICE_SECRET, JWT_SECRET, \
    OBJECT_DETECTION_CHANNEL

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET
jwt = JWTManager(app)
INTER_SERVICES_TOKEN = None
MESSAGE_CHANNEL = None


def create_api() -> Api:
    global INTER_SERVICES_TOKEN
    jwt_secret, INTER_SERVICES_TOKEN = _fetch_config_from_identity_service()
    app.config['JWT_SECRET_KEY'] = jwt_secret
    api = Api(app)
    services_info = _fetch_services_info(
        services=[
            'user_identity_service', 'people_detection_service',
            'face_detection_service', 'age_estimation_service',
            'message_broker', 'resource_manager_service'
        ]
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=services_info['message_broker']['service_address'],
            port=services_info['message_broker']['service_port']
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=OBJECT_DETECTION_CHANNEL)
    user_identity_url = \
        f"{services_info['user_identity_service']['service_address']}:" \
        f"{services_info['user_identity_service']['service_port']}"
    api.add_resource(
        Register,
        construct_api_url('/register_user'),
        resource_class_kwargs={
            'base_forwarding_url': user_identity_url,
            'inter_services_token': INTER_SERVICES_TOKEN
        }
    )
    api.add_resource(
        Login,
        construct_api_url('/user_login'),
        resource_class_kwargs={
            'base_forwarding_url': user_identity_url,
            'inter_services_token': INTER_SERVICES_TOKEN
        }
    )
    api.add_resource(
        TokenRefresh,
        construct_api_url('/refresh_token'),
    )
    api.add_resource(
        LogoutAccessToken,
        construct_api_url('/logout_access'),
    )
    api.add_resource(
        LogoutRefreshToken,
        construct_api_url('/logout_refresh'),
    )
    people_detection_url = \
        f"{services_info['people_detection_service']['service_address']}:" \
        f"{services_info['people_detection_service']['service_port']}"
    face_detection_url = \
        f"{services_info['face_detection_service']['service_address']}:" \
        f"{services_info['face_detection_service']['service_port']}"
    age_estimation_url = \
        f"{services_info['age_estimation_service']['service_address']}:" \
        f"{services_info['age_estimation_service']['service_port']}"
    base_resources_manager_path = \
        f"{services_info['resource_manager_service']['service_address']}:" \
        f"{services_info['resource_manager_service']['service_port']}"
    api.add_resource(
        ProcessingPipeline,
        construct_api_url('/sync/process_image'),
        resource_class_kwargs={
            'base_people_detection_url': people_detection_url,
            'base_face_detection_url': face_detection_url,
            'base_age_estimation_url': age_estimation_url,
            'inter_services_token': INTER_SERVICES_TOKEN
        }
    )
    api.add_resource(
        AsynchronousProcessingStart,
        construct_api_url('/async/process_image'),
        resource_class_kwargs={
            'base_resources_manager_path': base_resources_manager_path,
            'inter_services_token': INTER_SERVICES_TOKEN,
            'message_channel': channel
        }
    )
    api.add_resource(
        AsynchronousProcessingResultsFetch,
        construct_api_url('/async/fetch_results'),
        resource_class_kwargs={
            'base_resources_manager_path': base_resources_manager_path,
            'inter_services_token': INTER_SERVICES_TOKEN,
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


def _fetch_services_info(services: List[str]) -> Dict[str, dict]:
    response = _call_discovery_resource(services)
    if response.status_code == 200:
        response_content = response.json()
        return _fetch_services_info_from_response(
            content=response_content
        )
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return _fetch_services_info(services)


def _call_discovery_resource(services: List[str]) -> Response:
    headers = {'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'}
    payload = {'service_names': services}
    return requests.get(
        DISCOVERY_URL, headers=headers, json=payload, verify=False
    )


def _fetch_services_info_from_response(content: dict) -> Dict[str, dict]:
    services_found = content.get('services_found', [])
    return dict(map(lambda s: (s['service_name'], s), services_found))


def _fetch_port() -> int:
    response = _call_discovery_resource(services=[SERVICE_NAME])
    if response.status_code == 200:
        response_content = response.json()
        return _fetch_port_from_response(content=response_content)
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return _fetch_port()


def _fetch_port_from_response(content: dict) -> int:
    services_found = content.get('services_found', [])
    services_matching = list(filter(
        lambda srv_desc: srv_desc['service_name'] == SERVICE_NAME,
        services_found
    ))
    if len(services_matching) != 1:
        raise RuntimeError('Cannot get proper response from discovery service.')
    return services_matching[0]['service_port']


if __name__ == '__main__':
    api = create_api()
    port = _fetch_port()
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
