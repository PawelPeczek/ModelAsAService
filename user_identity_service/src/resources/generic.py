from flask_restful import Resource, reqparse


class CredentialsBasedResource(Resource):

    def __init__(self):
        self._parser = self._initialize_request_parser()

    def _initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'login',
            help='Field "login" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'password',
            help='Field "password" must be specified in this request.',
            required=True
        )
        return parser
