import io
from typing import Tuple
import json

import requests
from flask import Response, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from pika.channel import Channel

from ..config import OBJECT_DETECTION_CHANNEL


class AsynchronousProcessingStart(Resource):

    def __init__(self,
                 base_resources_manager_path: str,
                 inter_services_token: str,
                 message_channel: Channel
                 ):
        self.__base_resources_manager_path = base_resources_manager_path
        self.__inter_services_token = inter_services_token
        self.__message_channel = message_channel

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files:
            return make_response(
                {'msg': 'Field called "image" must be specified'}, 500
            )
        in_memory_file = io.BytesIO()
        request.files['image'].save(in_memory_file)
        raw_image = in_memory_file.getvalue()
        processing_response, return_code = \
            self.__start_processing(raw_image=raw_image)
        return make_response(processing_response, return_code)

    def __start_processing(self, raw_image: bytes) -> Tuple[dict, int]:
        headers = {
            'Authorization': f'Bearer {self.__inter_services_token}'
        }
        payload = {'login': get_jwt_identity()}
        files = {'image': raw_image}
        url = f'{self.__base_resources_manager_path}' \
            f'/v1/resource_manager_service/register_input_image'
        response = requests.post(
            url, files=files, data=payload, headers=headers, verify=False
        )
        if response.status_code != 200:
            return {'msg': 'Something went wrong, try again.'}, 500
        resource_identifiers = response.json()
        self.__message_channel.basic_publish(
            exchange='',
            routing_key=OBJECT_DETECTION_CHANNEL,
            body=json.dumps(resource_identifiers)
        )
        processing_response = {
            'request_identifier': resource_identifiers['request_identifier']
        }
        return processing_response, 200
