from flask import Flask
from flask_restful import Api

from pipeline_sdk.utils import compose_relative_resource_url
from .resources import ServiceIdentityResource
from .config import TOKEN_SECRET, DB_CONN_STRING, SERVICE_NAME, \
    SERVICE_VERSION, SERVICE_PORT
from .model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN_STRING
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def create_api() -> Api:
    api = Api(app)
    api.add_resource(
        ServiceIdentityResource,
        compose_relative_resource_url(
            SERVICE_NAME, SERVICE_VERSION, '/verify_service_identity'
        ),
        resource_class_kwargs={'token_secret': TOKEN_SECRET}
    )
    return api


api = create_api()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT, ssl_context='adhoc')
