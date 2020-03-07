import logging
from time import sleep
from typing import Tuple, List

import requests
from flask import Flask, Response
from flask_jwt_extended import JWTManager
from flask_restful import Api

from .resources import InputRegistrationResource, \
    IntermediateResultRegistrationResource, IntermediateResultFetchingResource, \
    InputFetchingResource, BatchFetchingResource
from .config import API_VERSION, SERVICE_NAME, SERVER_IDENTITY_URL, \
    SERVICE_SECRET, DISCOVERY_URL

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt = JWTManager(app)
INTER_SERVICES_TOKEN = None


def create_api() -> Api:
    global INTER_SERVICES_TOKEN
    jwt_secret, INTER_SERVICES_TOKEN = _fetch_config_from_identity_service()
    app.config['JWT_SECRET_KEY'] = jwt_secret
    api = Api(app)
    api.add_resource(
        InputRegistrationResource,
        construct_api_url('/register_input_image')
    )
    api.add_resource(
        IntermediateResultRegistrationResource,
        construct_api_url('/register_intermediate_result')
    )
    api.add_resource(
        IntermediateResultFetchingResource,
        construct_api_url('/fetch_intermediate_results')
    )
    api.add_resource(
        InputFetchingResource,
        construct_api_url('/fetch_input_image')
    )
    api.add_resource(
        BatchFetchingResource,
        construct_api_url('/fetch_resources_batch')
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


def _call_discovery_resource(services: List[str]) -> Response:
    headers = {'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'}
    payload = {'service_names': services}
    return requests.get(
        DISCOVERY_URL, headers=headers, json=payload, verify=False
    )


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
    service_port = _fetch_port()
    app.run(host='0.0.0.0', port=service_port, ssl_context='adhoc')
