from flask import Flask
from flask_restful import Api

from .resources import VerifyServiceIdentity
from .config import SERVICE_PORT, API_VERSION, SERVICE_NAME, TOKEN_SECRET, \
    DB_CONN_STRING
from .model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN_STRING
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def create_api() -> Api:
    api = Api(app)
    api.add_resource(
        VerifyServiceIdentity,
        construct_api_url('/verify_service_identity'),
        resource_class_kwargs={'token_secret': TOKEN_SECRET}
    )
    return api


def construct_api_url(resource_postfix: str) -> str:
    return f'/{API_VERSION}/{SERVICE_NAME}{resource_postfix}'


api = create_api()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT, ssl_context='adhoc')
