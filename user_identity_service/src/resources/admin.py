from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_required, jwt_refresh_token_required, get_jwt_identity, get_jwt_claims
from flask_restful import Resource, reqparse
from flask import Response, make_response
from sqlalchemy.exc import SQLAlchemyError

from ..privileges import Privilege
from .generic import CredentialsBasedResource
from ..model import User, commit_db_changes, remove_from_db


class AdminLogin(CredentialsBasedResource):

    def post(self) -> Response:
        data = self._parser.parse_args()
        user = User.find_by_credentials(
            login=data['login'],
            password=data['password']
        )
        if user is None or user.access_level < Privilege.ADMIN.value:
            return make_response(
                {'msg': 'Admin mode login failed.'}, 401
            )
        access_token = create_access_token(
            identity=user.login, user_claims={'access_level': user.access_level}
        )
        refresh_token = create_refresh_token(
            identity=user.login, user_claims={'access_level': user.access_level}
        )
        return make_response(
            {'access_token': access_token, 'refresh_token': refresh_token}, 200
        )


class AdminTokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        login = get_jwt_identity()
        user_claims = get_jwt_claims()
        access_token = create_access_token(
            identity=login,
            user_claims=user_claims
        )
        return make_response({'access_token': access_token}, 200)


class AdminLevelControlResource(Resource):

    def _admin_cannot_control_user(self, user: User) -> bool:
        admin_level = self.__fetch_admin_level()
        print(f'Admin level {admin_level} vs {user.access_level} user level')
        return admin_level < user.access_level

    def __fetch_admin_level(self) -> int:
        user_claims = get_jwt_claims()
        return int(user_claims['access_level'])


class ChangeAccessLevel(AdminLevelControlResource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    @jwt_required
    def post(self) -> Response:
        data = self.__parser.parse_args()
        new_access_level = data['new_access_level']
        if self.__access_level_invalid(level=new_access_level):
            return make_response(
                {'msg': 'Access level must be integer from range <1;3>'},
                422
            )
        user = User.find_by_login(login=data['login'])
        if user is None or self._admin_cannot_control_user(user=user):
            return make_response(
                {'msg': 'User does not exist or cannot be modify.'},
                422
            )
        user.access_level = new_access_level
        try:
            commit_db_changes()
        except SQLAlchemyError:
            return make_response(
                {'msg': 'Request could not be processed.'}, 500
            )
        return make_response({'msg': 'OK'}, 200)

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'login',
            help='Field "login" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'new_access_level',
            help='Field "login" must be specified in this request.',
            required=True,
            type=int
        )
        return parser

    def __access_level_invalid(self, level: int) -> bool:
        return level < Privilege.ASYNCHRONOUS_USER.value or \
            level > Privilege.ADMIN.value


class DeleteUser(AdminLevelControlResource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    @jwt_required
    def post(self) -> Response:
        data = self.__parser.parse_args()
        user = User.find_by_login(login=data['login'])
        if user is None or self._admin_cannot_control_user(user=user):
            return make_response(
                {'msg': 'User does not exist or cannot be modify.'},
                422
            )
        try:
            remove_from_db(instance=user)
        except SQLAlchemyError:
            return make_response(
                {'msg': 'Request could not be processed.'}, 500
            )
        return make_response({'msg': 'OK'}, 200)

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'login',
            help='Field "login" must be specified in this request.',
            required=True
        )
        return parser


class AdminLogoutAccessToken(Resource):

    # stub class to mimic access token logout

    @jwt_required
    def post(self):
        return make_response({'msg': 'OK'}, 200)


class AdminLogoutRefreshToken(Resource):

    # stub class to mimic refresh token logout

    @jwt_refresh_token_required
    def post(self):
        return make_response({'msg': 'OK'}, 200)
