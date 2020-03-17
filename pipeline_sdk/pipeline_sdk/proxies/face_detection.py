import json
from typing import List

import numpy as np
import requests
from flask import Response

from ..config import DETECT_FACES_PATH
from ..primitives import BoundingBox
from .errors import RequestProcessingError
from .primitives import ServiceSpecs


class FaceDetectionServiceClient:

    def __init__(self,
                 face_detection_service_specs: ServiceSpecs,
                 service_token: str):
        self.__face_detection_service_specs = face_detection_service_specs
        self.__service_token = service_token

    def detect_faces(self, image: np.ndarray) -> List[BoundingBox]:
        from ..utils import create_bounding_box_covering_image
        bounding_box_covering_image = create_bounding_box_covering_image(
            image=image
        )
        return self.detect_faces_with_prior(
            image=image,
            rois=[bounding_box_covering_image]
        )

    def detect_faces_with_prior(self,
                                image: np.ndarray,
                                rois: List[BoundingBox]
                                ) -> List[BoundingBox]:
        from ..utils import compose_url, image_to_jpeg_bytes
        headers = {'Authorization': f'Bearer {self.__service_token}'}
        raw_image = image_to_jpeg_bytes(image=image)
        rois = [roi.to_dict() for roi in rois]
        files = {'image': raw_image, 'people': json.dumps(rois)}
        url = compose_url(
            service_specs=self.__face_detection_service_specs,
            path_postfix=DETECT_FACES_PATH
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
        faces_detected = response.json()['faces']
        return [BoundingBox.from_dict(raw_bbox) for raw_bbox in faces_detected]
