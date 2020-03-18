from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from pipeline_sdk.proxies import ServiceJWT, ServerIdentityClient, \
    DiscoveryServiceClient
from pipeline_sdk.utils import compose_relative_resource_url

from .resources import AgeEstimation
from .config import SERVICE_NAME, API_VERSION, SERVICE_SECRET, \
    IDENTITY_SERVICE_SPECS, DISCOVERY_SERVICE_SPECS

INTER_SERVICES_TOKEN = None
app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)


def create_api() -> Api:
    global INTER_SERVICES_TOKEN
    secret, INTER_SERVICES_TOKEN = _fetch_config_from_identity_service()
    app.config['JWT_SECRET_KEY'] = secret
    api = Api(app)
    api.add_resource(
        AgeEstimation,
        compose_relative_resource_url(SERVICE_NAME, API_VERSION, 'estimate_age'),
    )
    return api


def _fetch_config_from_identity_service() -> ServiceJWT:
    client = ServerIdentityClient(
        server_identity_specs=IDENTITY_SERVICE_SPECS
    )
    return client.obtain_service_jwt_safely(
        service_name=SERVICE_NAME,
        service_secret=SERVICE_SECRET
    )


def _fetch_port() -> int:
    client = DiscoveryServiceClient(
        discovery_service_specs=DISCOVERY_SERVICE_SPECS,
        service_token=INTER_SERVICES_TOKEN
    )
    discovery_info = client.obtain_discovery_info_safely(
        service_names=[SERVICE_NAME]
    )
    service_info = discovery_info.get(SERVICE_NAME)
    if service_info is None:
        raise RuntimeError(
            f"Could not fetch data about {SERVICE_NAME} from discovery service"
        )
    return service_info.port


api = create_api()


if __name__ == '__main__':
    port = _fetch_port()
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
