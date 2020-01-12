import jwt
from flask import Response, make_response
from flask_restful import Resource, reqparse

from .model import Service


class VerifyServiceIdentity(Resource):

    def __init__(self, token_secret: str):
        self.__parser = self.__initialize_request_parser()
        self.__token_secret = token_secret

    def post(self) -> Response:
        data = self.__parser.parse_args()
        service = Service.find_by_credentials(
            service_name=data['service_name'],
            password=data['password']
        )
        if service is None:
            return make_response(
                {'msg': 'Service login failed.'}, 401
            )
        service_access_token = jwt.encode(
            payload={}, key=self.__token_secret, algorithm='HS256'
        )
        response_body = {
            'token_secret': self.__token_secret,
            'service_access_token': service_access_token.decode("utf-8")
        }
        return make_response(response_body, 200)

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'service_name',
            help='Field "login" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'password',
            help='Field "password" must be specified in this request.',
            required=True
        )
        return parser
