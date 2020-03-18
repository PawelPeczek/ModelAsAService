import json
from typing import List, Optional

import numpy as np
import requests
from requests import Response

from pipeline_sdk.pipeline_sdk.config import ESTIMATE_AGE_PATH
from ..primitives import AgeEstimationResult, BoundingBox
from .primitives import ServiceSpecs
from .errors import RequestProcessingError


class AgeEstimationServiceClient:

    def __init__(self,
                 age_estimation_service_specs: ServiceSpecs,
                 service_token: str):
        self.__age_estimation_service_specs = age_estimation_service_specs
        self.__service_token = service_token

    def estimate_age(self, image: np.ndarray) -> Optional[int]:
        from ..utils import create_bounding_box_covering_image
        bounding_box_covering_image = create_bounding_box_covering_image(
            image=image
        )
        estimated_age = self.estimate_age_with_prior(
            image=image,
            rois=[bounding_box_covering_image]
        )
        return estimated_age[0].associated_age

    def estimate_age_with_prior(self,
                                image: np.ndarray,
                                rois: List[BoundingBox]
                                ) -> List[AgeEstimationResult]:
        from ..utils import compose_url, image_to_jpeg_bytes
        headers = {'Authorization': f'Bearer {self.__service_token}'}
        raw_image = image_to_jpeg_bytes(image=image)
        rois = [roi.to_dict() for roi in rois]
        files = {'image': raw_image, 'faces': json.dumps(rois)}
        url = compose_url(
            service_specs=self.__age_estimation_service_specs,
            path_postfix=ESTIMATE_AGE_PATH
        )
        response = requests.post(url, headers=headers, files=files, verify=False)
        if response.status_code == 200:
            return self.__convert_valid_output(response=response)
        else:
            raise RequestProcessingError(
                f'Error code: {response.status_code}, Cause: {response.text}'
            )

    def __convert_valid_output(self,
                               response: Response
                               ) -> List[AgeEstimationResult]:
        age_estimation_results = response.json()['age_estimation']
        return [
            AgeEstimationResult.from_dict(age_estimation_result)
            for age_estimation_result in age_estimation_results
        ]
