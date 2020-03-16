from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from pipeline_sdk.utils import compose_relative_resource_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pipeline_sdk.proxies import ServerIdentityClient

from .resources import ServiceLocationResource
from .config import SERVICE_NAME, DB_CONN_STRING, SERVICE_SECRET, \
    SERVER_IDENTITY_SPECS, API_VERSION
from .model import db, ServiceLocation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN_STRING
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

jwt = JWTManager(app)


def create_api() -> Api:
    server_identity_client = ServerIdentityClient(
        server_identity_specs=SERVER_IDENTITY_SPECS
    )
    service_jwt = server_identity_client.obtain_service_jwt(
        service_name=SERVICE_NAME,
        service_secret=SERVICE_SECRET
    )
    app.config['JWT_SECRET_KEY'] = service_jwt.token_secret
    api = Api(app)
    api.add_resource(
        ServiceLocationResource,
        compose_relative_resource_url(
            SERVICE_NAME, API_VERSION, '/locate_services'
        )
    )
    return api


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
