from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from .resources.admin import AdminLogin, AdminTokenRefresh, \
    ChangeAccessLevel, AdminLogoutAccessToken, AdminLogoutRefreshToken, \
    DeleteUser
from .resources.user import Register, VerifyCredentials
from .config import JWT_SECRET, SERVICE_NAME, API_VERSION,\
    SERVICE_PORT, DB_CONN_STRING
from .model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN_STRING

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET
jwt = JWTManager(app)
db.init_app(app)


def create_api() -> Api:
    api = Api(app)
    api.add_resource(Register, construct_api_url('/register_user'))
    api.add_resource(
        VerifyCredentials, construct_api_url('/verify_credentials')
    )
    api.add_resource(AdminLogin, construct_api_url('/admin/login'))
    api.add_resource(
        AdminTokenRefresh, construct_api_url('/admin/refresh_token')
    )
    api.add_resource(
        ChangeAccessLevel, construct_api_url('/admin/change_user_access_level')
    )
    api.add_resource(DeleteUser, construct_api_url('/admin/delete_user'))
    api.add_resource(
        AdminLogoutAccessToken, construct_api_url('/admin/logout_access_token')
    )
    api.add_resource(
        AdminLogoutRefreshToken,
        construct_api_url('/admin/logout_refresh_token')
    )
    return api


def construct_api_url(resource_postfix: str) -> str:
    return f'/{API_VERSION}/{SERVICE_NAME}{resource_postfix}'


api = create_api()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT, ssl_context='adhoc')
