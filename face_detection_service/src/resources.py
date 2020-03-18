import json
from typing import List

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
import numpy as np
from pipeline_sdk.utils import flatten, decode_bboxes, \
    image_from_str, take_image_crops
from retina_face_net import RetinaFaceNet
from .utils import translate_results
from .primitives import BoundingBox


class FacesDetection(Resource):

    def __init__(self, model: RetinaFaceNet):
        self.__model = model

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files or 'people' not in request.files:
            return make_response({'msg': 'Required fields not provided.'}, 500)
        image = image_from_str(raw_image=request.files['image'].read())
        people_detection = json.load(request.files['people'])
        people_detection = decode_bboxes(raw_bboxes=people_detection)
        face_detections = self.__infer_face_positions(
            image=image,
            people_detection=people_detection
        )
        return make_response({'faces': face_detections}, 200)

    def __infer_face_positions(self,
                               image: np.ndarray,
                               people_detection: List[BoundingBox]
                               ) -> List[BoundingBox]:
        image_crops = take_image_crops(
            image=image,
            bounding_boxes=people_detection
        )
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
