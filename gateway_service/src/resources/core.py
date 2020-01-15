import requests
from flask import Response, request
from flask_restful import Resource


class Proxy(Resource):

    def __init__(self, base_forwarding_url: str, inter_services_token: str):
        super().__init__()
        self.__excluded_headers = [
            'content-encoding', 'content-length',
            'transfer-encoding', 'connection'
        ]
        self.__base_forwarding_url = base_forwarding_url
        self.__inter_services_token = inter_services_token

    def _forward_message(self, target_path: str) -> Response:
        if not target_path.startswith('/'):
            target_path = f'/{target_path}'
        target_url = f'{self.__base_forwarding_url}{target_path}'
        headers = {
            key: value for (key, value) in request.headers if key != 'Host'
        }
        headers['Authorization'] = f'Bearer {self.__inter_services_token}'
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            allow_redirects=False,
            verify=False
        )
        headers = [
            (name, value) for (name, value) in resp.raw.headers.items()
            if name.lower() not in self.__excluded_headers
        ]
        response = Response(resp.content, resp.status_code, headers)
        return response
