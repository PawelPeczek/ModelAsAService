from flask import Response, make_response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .generic import CredentialsBasedResource
from ..model import User, persist_model_instance


class Register(CredentialsBasedResource):

    @jwt_required
    def post(self) -> Response:
        data = self._parser.parse_args()
        user_with_given_login = User.find_by_login(login=data['login'])
        if user_with_given_login is not None:
            return make_response(
                {'msg': 'User with given login already exists.'}, 409
            )
        try:
            new_user = User(login=data['login'], access_level=1)
            new_user.set_password(password=data['password'])
            persist_model_instance(instance=new_user)
            return make_response({'message': 'OK'}, 200)
        except SQLAlchemyError:
            return make_response(
                {'msg': 'Request could not be processed.'}, 500
            )


class VerifyCredentials(CredentialsBasedResource):

    @jwt_required
    def post(self) -> Response:
        data = self._parser.parse_args()
        user = User.find_by_credentials(
            login=data['login'],
            password=data['password']
        )
        if user is None:
            return make_response(
                {'msg': 'Login try failed.'}, 403
            )
        return make_response(
            {'login': user.login, 'access_level': user.access_level}
        )
