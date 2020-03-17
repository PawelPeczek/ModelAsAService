import os

from pipeline_sdk.proxies import ServiceSpecs

API_VERSION = 'v1'
SERVICE_NAME = os.environ['FACE_DETECTION_SERVICE_NAME']
SERVICE_SECRET = os.environ['FACE_DETECTION_SERVICE_SECRET']
IDENTITY_SERVICE_SPECS = ServiceSpecs(
    host=os.environ['SERVER_IDENTITY_SERVICE_HOST'],
    port=os.environ['SERVER_IDENTITY_SERVICE_PORT'],
    service_name=os.environ['SERVER_IDENTITY_SERVICE_NAME'],
    version='v1'
)
DISCOVERY_SERVICE_SPECS = ServiceSpecs(
    host=os.environ['DISCOVERY_SERVICE_HOST'],
    port=os.environ['DISCOVERY_SERVICE_PORT'],
    service_name=os.environ['DISCOVERY_SERVICE_NAME'],
    version='v1'
)
WEIGHTS_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'weights', 'weights.pth'
)
CONFIDENCE_THRESHOLD = 0.3
TOP_K_PREDICTIONS_TO_TAKE = 20
NMS_THRESHOLD = 0.4
