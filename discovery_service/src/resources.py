from typing import List, Union

from flask import Response, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from .model import ServiceLocation


class ServiceLocationResource(Resource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    @jwt_required
    def get(self) -> Response:
        data = self.__parser.parse_args()
        if self.__caller_identity_not_recognised():
            return make_response({'msg': 'Identity not recognised.'}, 401)
        lookup_results = self.__find_services(to_find=data['service_names'])
        return make_response(lookup_results, 200)

    def __caller_identity_not_recognised(self) -> bool:
        identity = get_jwt_identity()
        service_location = ServiceLocation.find_by_name(service_name=identity)
        return service_location is None

    def __find_services(self, to_find: Union[str, List[str]]) -> dict:
        if type(to_find) is str:
            to_find = [to_find]
        found = list(map(ServiceLocation.find_by_name, to_find))
        missing = [
            s_name for s_name, lookup_res in zip(to_find, found)
            if lookup_res is None
        ]
        found = filter(lambda s: s is not None, found)
        found = list(map(
            lambda s: {
                'service_name': s.service_name,
                'service_address': s.service_address,
                'service_port': s.service_port
            },
            found
        ))
        return {'services_found': found, 'services_missing': missing}

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        help_msg = \
            'Field "service_names" must be specified in this ' \
            'request and must be a list.'
        parser.add_argument(
            'service_names',
            help=help_msg,
            required=True,
            action='append'
        )
        return parser
