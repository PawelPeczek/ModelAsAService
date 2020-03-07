import logging
from time import sleep
from typing import Tuple

import requests
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .resources import ServiceLocationResource
from .config import API_VERSION, SERVICE_NAME, DB_CONN_STRING, \
    SERVER_IDENTITY_URL, SERVICE_SECRET
from .model import db, ServiceLocation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN_STRING
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

jwt = JWTManager(app)


def create_api() -> Api:
    jwt_secret, _ = _fetch_config_from_identity_service()
    app.config['JWT_SECRET_KEY'] = jwt_secret
    api = Api(app)
    api.add_resource(
        ServiceLocationResource,
        construct_api_url('/locate_services')
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


def fetch_service_port() -> int:
    engine = create_engine(DB_CONN_STRING, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    query = \
        session.query(ServiceLocation).filter_by(service_name=SERVICE_NAME)
    service_location = session.execute(query).first()
    session.close()
    if service_location is None:
        raise RuntimeError(
            f'Cannnot find service location for service {SERVICE_NAME}'
        )
    else:
        return service_location[3]


if __name__ == '__main__':
    api = create_api()
    service_port = fetch_service_port()
    app.run(host='0.0.0.0', port=service_port, ssl_context='adhoc')
