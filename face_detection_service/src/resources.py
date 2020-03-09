import json
from typing import List

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
import numpy as np
import cv2 as cv
from retina_face_net import RetinaFaceNet
from .utils import take_image_crop, translate_results, flatten
from .primitives import BoundingBox


class FacesDetection(Resource):

    def __init__(self, model: RetinaFaceNet):
        self.__model = model

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files or 'people' not in request.files:
            return make_response({'msg': 'Required fields not provided.'}, 500)
        data = np.fromstring(request.files['image'].read(), dtype=np.uint8)
        image = cv.imdecode(data, cv.IMREAD_COLOR)
        people_detection = json.load(request.files['people'])
        people_detection = [
            BoundingBox.from_dict(bounding_box_dict)
            for bounding_box_dict in people_detection
        ]
        face_detections = self.__infer_face_positions(
            image=image,
            people_detection=people_detection
        )
        return make_response({'faces': face_detections}, 200)

    def __infer_face_positions(self,
                               image: np.ndarray,
                               people_detection: List[BoundingBox]
                               ) -> List[BoundingBox]:
        image_crops = [
            take_image_crop(image=image, bounding_box=bounding_box)
            for bounding_box in people_detection
        ]
        inferences_results = [
            self.__model.infer(image=crop) if crop is not None else None
            for crop in image_crops
        ]
        translated_results = [
            translate_results(
                inference_results=inference_results,
                reference_bbox=reference_bbox
            )
            for inference_results, reference_bbox
            in zip(inferences_results, people_detection)
        ]
        return flatten(input_list=translated_results)
