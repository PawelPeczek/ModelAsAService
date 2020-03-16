import os

from pipeline_sdk.proxies import ServiceSpecs

DB_ENGINE = 'postgres'
DB_USER = os.environ['DB_USER']
DB_SECRET = os.environ['DB_SECRET']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DISCOVERY_SERVICE_DB_NAME']
SERVER_IDENTITY_SPECS = ServiceSpecs(
    host=os.environ['SERVER_IDENTITY_SERVICE_HOST'],
    port=os.environ['SERVER_IDENTITY_SERVICE_PORT'],
    service_name=os.environ['SERVER_IDENTITY_SERVICE_NAME'],
    version='v1'
)
API_VERSION = 'v1'
SERVICE_NAME = os.environ['DISCOVERY_SERVICE_NAME']
SERVICE_SECRET = os.environ['DISCOVERY_SERVICE_SECRET']
DB_CONN_STRING = f'{DB_ENGINE}://{DB_USER}:{DB_SECRET}@{DB_HOST}/{DB_NAME}'
