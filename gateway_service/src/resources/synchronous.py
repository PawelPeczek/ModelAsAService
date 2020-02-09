import io
import json
from typing import List, Tuple

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
import requests

BoundingBox = Tuple[Tuple[int, int], Tuple[int, int]]


class ProcessingPipeline(Resource):

    def __init__(self,
                 base_people_detection_url: str,
                 base_face_detection_url: str,
                 base_age_estimation_url: str,
                 inter_services_token: str):
        self.__base_people_detection_url = base_people_detection_url
        self.__base_face_detection_url = base_face_detection_url
        self.__base_age_estimation_url = base_age_estimation_url
        self.__inter_services_token = inter_services_token

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files:
            return make_response(
                {'msg': 'Field called "image" must be specified'}, 500
            )
        in_memory_file = io.BytesIO()
        request.files['image'].save(in_memory_file)
        raw_image = in_memory_file.getvalue()
        return self.__processing_started(raw_image=raw_image)

    def __processing_started(self, raw_image: bytes) -> Response:
        headers = {
            'Authorization': f'Bearer {self.__inter_services_token}'
        }
        files = {'image': raw_image}
        url = f'{self.__base_people_detection_url}/v1/people_detection_service/' \
            f'detect_people'
        response = requests.post(
            url, headers=headers, files=files, verify=False
        )
        people_detected = response.json()['people']
        return self.__people_detected(
            raw_image=raw_image, people_detected=people_detected
        )

    def __people_detected(self,
                          raw_image: bytes,
                          people_detected: List[BoundingBox]
                          ) -> Response:
        headers = {'Authorization': f'Bearer {self.__inter_services_token}'}
        files = {'image': raw_image, 'people': json.dumps(people_detected)}
        url = f'{self.__base_face_detection_url}/v1/face_detection_service/' \
            f'detect_faces'
        response = requests.post(
            url,
            headers=headers,
            files=files,
            verify=False
        )
        faces_detected = response.json()['faces']
        return self.__faces_detected(
            raw_image=raw_image, faces_detected=faces_detected
        )

    def __faces_detected(self,
                         raw_image: bytes,
                         faces_detected: List[BoundingBox]
                         ) -> Response:
        headers = {'Authorization': f'Bearer {self.__inter_services_token}'}
        files = {'image': raw_image, 'faces': json.dumps(faces_detected)}
        url = f'{self.__base_age_estimation_url}/v1/age_estimation_service/' \
            f'estimate_age'
        response = requests.post(
            url,
            headers=headers,
            files=files,
            verify=False
        )
        return make_response(response.json(), 200)
