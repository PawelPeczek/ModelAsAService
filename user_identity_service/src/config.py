import os

DB_ENGINE = 'postgres'
DB_USER = os.environ['DB_USER']
DB_SECRET = os.environ['DB_SECRET']
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
JWT_SECRET = os.environ['JWT_SECRET']
API_VERSION = 'v1'
SERVICE_NAME = 'identity'
SERVICE_PORT = 50001
