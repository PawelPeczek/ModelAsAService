import json
from typing import Tuple, List, Optional

import numpy as np
from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from age_estimator import AgeEstimator
from pipeline_sdk.primitives import AgeEstimationResult
from pipeline_sdk.utils import image_from_str, decode_bboxes, take_image_crops

BoundingBox = Tuple[Tuple[int, int], Tuple[int, int]]


class AgeEstimation(Resource):

    def __init__(self, model: AgeEstimator):
        self.__model = model

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files or 'faces' not in request.files:
            return make_response({'msg': 'Required fields not provided.'}, 500)
        image = image_from_str(raw_image=request.files['image'].read())
        faces_bboxes = json.load(request.files['faces'])
        faces_bboxes = decode_bboxes(raw_bboxes=faces_bboxes)
        faces_crops = take_image_crops(image=image, bounding_boxes=faces_bboxes)
        inference_results = self.__infer(faces_crops=faces_crops)
        age_estimations = [
            AgeEstimationResult(face_bbox, inferred_age)
            for face_bbox, inferred_age in zip(faces_bboxes, inference_results)
        ]
        return make_response({'age_estimation': age_estimations}, 200)

    def __infer(self,
                faces_crops: List[Optional[np.ndarray]]
                ) -> List[Optional[int]]:
        return [
            self.__model.estimate_age(image=crop) if crop is not None else None
            for crop in faces_crops
        ]
