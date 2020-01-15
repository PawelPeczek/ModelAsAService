import os

DB_ENGINE = 'postgres'
DB_USER = os.environ['DB_USER']
DB_SECRET = os.environ['DB_SECRET']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
TOKEN_SECRET = os.environ['TOKEN_SECRET']
API_VERSION = 'v1'
SERVICE_NAME = 'server_identity_service'
SERVICE_PORT = 50002
DB_CONN_STRING = f'{DB_ENGINE}://{DB_USER}:{DB_SECRET}@{DB_HOST}/{DB_NAME}'
