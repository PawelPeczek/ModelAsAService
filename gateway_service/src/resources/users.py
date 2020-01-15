from flask import Response, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity, get_jwt_claims, jwt_required
from flask_restful import Resource

from .core import Proxy


class Register(Proxy):

    def post(self) -> Response:
        return self._forward_message(
            target_path='/v1/user_identity_service/register_user'
        )


class Login(Proxy):

    def post(self) -> Response:
        response = self._forward_message(
            target_path='/v1/user_identity_service/verify_credentials'
        )
        if response.status_code != 200:
            return response
        response_content = response.json
        access_token = create_access_token(
            identity=response_content['login'],
            user_claims={'access_level': response_content['access_level']},
            headers={'admin_resource_protection': True}
        )
        refresh_token = create_refresh_token(
            identity=response_content['login'],
            user_claims={'access_level': response_content['access_level']},
            headers={'admin_resource_protection': True}
        )
        return make_response(
            {'access_token': access_token, 'refresh_token': refresh_token}, 200
        )


class TokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        login = get_jwt_identity()
        user_claims = get_jwt_claims()
        access_token = create_access_token(
            identity=login,
            user_claims=user_claims
        )
        return make_response({'access_token': access_token}, 200)


class LogoutAccessToken(Resource):

    @jwt_required
    def post(self):
        return make_response({'msg': 'OK'}, 200)


class LogoutRefreshToken(Resource):

    @jwt_refresh_token_required
    def post(self):
        return make_response({'msg': 'OK'}, 200)
