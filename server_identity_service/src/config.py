import os

from pipeline_sdk.proxies import ServiceSpecs

DB_ENGINE = 'postgres'
DB_USER = os.environ['DB_USER']
DB_SECRET = os.environ['DB_SECRET']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['SERVER_IDENTITY_DB_NAME']
TOKEN_SECRET = os.environ['SERVER_IDENTITY_TOKEN_SECRET']
SERVICE_SPECS = ServiceSpecs(
    host=os.environ['SERVER_IDENTITY_SERVICE_HOST'],
    port=os.environ['SERVER_IDENTITY_SERVICE_PORT'],
    service_name=os.environ['SERVER_IDENTITY_SERVICE_NAME'],
    version='v1'
)
DB_CONN_STRING = f'{DB_ENGINE}://{DB_USER}:{DB_SECRET}@{DB_HOST}/{DB_NAME}'
