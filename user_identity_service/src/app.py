import logging
from time import sleep
from typing import Tuple

import requests
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from .resources.admin import AdminLogin, AdminTokenRefresh, \
    ChangeAccessLevel, AdminLogoutAccessToken, AdminLogoutRefreshToken, \
    DeleteUser
from .resources.user import Register, VerifyCredentials
from .config import ADMIN_RESOURCES_JWT_SECRET, SERVICE_NAME, API_VERSION, \
    DB_CONN_STRING, SERVICE_SECRET, SERVER_IDENTITY_URL, \
    DISCOVERY_URL
from .model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN_STRING

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_RESOURCES_JWT_SECRET_KEY'] = ADMIN_RESOURCES_JWT_SECRET
INTER_SERVICES_TOKEN = None
jwt = JWTManager(app)
db.init_app(app)


def create_api() -> Api:
    global INTER_SERVICES_TOKEN
    secret, INTER_SERVICES_TOKEN = _fetch_config_from_identity_service()
    app.config['USER_RESOURCES_JWT_SECRET'] = secret
    api = Api(app)
    api.add_resource(Register, construct_api_url('/register_user'))
    api.add_resource(
        VerifyCredentials, construct_api_url('/verify_credentials')
    )
    api.add_resource(AdminLogin, construct_api_url('/admin/login'))
    api.add_resource(
        AdminTokenRefresh, construct_api_url('/admin/refresh_token')
    )
    api.add_resource(
        ChangeAccessLevel, construct_api_url('/admin/change_user_access_level')
    )
    api.add_resource(DeleteUser, construct_api_url('/admin/delete_user'))
    api.add_resource(
        AdminLogoutAccessToken, construct_api_url('/admin/logout_access_token')
    )
    api.add_resource(
        AdminLogoutRefreshToken,
        construct_api_url('/admin/logout_access_token')
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


@jwt.decode_key_loader
def key_loader(unverified_claims: dict, unverified_header: dict) -> str:
    admin_resource_protection = unverified_claims.get(
        'admin_resource_protection', False
    )
    if admin_resource_protection:
        return app.config['ADMIN_RESOURCES_JWT_SECRET_KEY']
    else:
        return app.config['USER_RESOURCES_JWT_SECRET']


@jwt.encode_key_loader
def encode_key_loader(identity: str) -> str:
    if identity == 'gateway_service':
        return app.config['USER_RESOURCES_JWT_SECRET']
    else:
        return app.config['ADMIN_RESOURCES_JWT_SECRET_KEY']


api = create_api()


if __name__ == '__main__':
    port = fetch_port()
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
