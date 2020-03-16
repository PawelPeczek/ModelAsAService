import os


DB_ENGINE = 'postgres'
DB_USER = os.environ['DB_USER']
DB_SECRET = os.environ['DB_SECRET']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['SERVER_IDENTITY_DB_NAME']
TOKEN_SECRET = os.environ['SERVER_IDENTITY_TOKEN_SECRET']
SERVICE_PORT = os.environ['SERVER_IDENTITY_SERVICE_PORT']
SERVICE_NAME = os.environ['SERVER_IDENTITY_SERVICE_NAME']
SERVICE_VERSION = 'v1'
DB_CONN_STRING = f'{DB_ENGINE}://{DB_USER}:{DB_SECRET}@{DB_HOST}/{DB_NAME}'
