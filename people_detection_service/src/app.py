from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from keras_retinanet.models import load_model
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from pipeline_sdk.proxies import ServerIdentityClient, ServiceJWT, \
    DiscoveryServiceClient
from pipeline_sdk.utils import compose_relative_resource_url

from .resources import PeopleDetection
from .config import SERVICE_NAME, API_VERSION, SERVICE_SECRET, \
    WEIGHTS_PATH, CONFIDENCE_THRESHOLD, CLASSES_TO_FETCH, \
    MAX_IMAGE_DIM, IDENTITY_SERVICE_SPECS, DISCOVERY_SERVICE_SPECS

INTER_SERVICES_TOKEN = None
app = Flask(__name__)
GRAPH = None
TF_SESSION = None
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)


def create_api() -> Api:
    global INTER_SERVICES_TOKEN
    service_jwt = _fetch_config_from_identity_service()
    INTER_SERVICES_TOKEN = service_jwt.token
    app.config['JWT_SECRET_KEY'] = service_jwt.token_secret
    api = Api(app)
    global TF_SESSION
    global GRAPH
    GRAPH = tf.get_default_graph()
    TF_SESSION = tf.Session(graph=GRAPH)
    set_session(TF_SESSION)
    model = load_model(WEIGHTS_PATH)
    api.add_resource(
        PeopleDetection,
        compose_relative_resource_url(
            SERVICE_NAME, API_VERSION, 'detect_people'
        ),
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
