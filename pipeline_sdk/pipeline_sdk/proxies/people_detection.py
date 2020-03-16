from typing import List

import requests
from flask import Response

from ..primitives import BoundingBox
from .errors import RequestProcessingError
from ..config import DETECT_PEOPLE_PATH

from .primitives import ServiceSpecs


import numpy as np


class PeopleDetectionServiceClient:

    def __init__(self,
                 people_detection_service_specs: ServiceSpecs,
                 service_token: str):
        self.__people_detection_service_specs = people_detection_service_specs
        self.__service_token = service_token

    def detect_people(self, image: np.ndarray) -> List[BoundingBox]:
        from ..utils import compose_url, image_to_jpeg_bytes
        headers = {
            'Authorization': f'Bearer {self.__service_token}'
        }
        raw_image = image_to_jpeg_bytes(image=image)
        files = {'image': raw_image}
        url = compose_url(
            service_specs=self.__people_detection_service_specs,
            path_postfix=DETECT_PEOPLE_PATH
        )
        response = requests.post(
            url, headers=headers, files=files, verify=False
        )
        if response.status_code == 200:
            return self.__convert_valid_output(response=response)
        else:
            raise RequestProcessingError(
                f'Error code: {response.status_code}, Cause: {response.text}'
            )

    def __convert_valid_output(self, response: Response) -> List[BoundingBox]:
        raw_bboxes = response.json()['people']
        return [BoundingBox.from_dict(raw_bbox) for raw_bbox in raw_bboxes]
