import json
import random
from typing import Tuple

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource


BoundingBox = Tuple[Tuple[int, int], Tuple[int, int]]


class AgeEstimation(Resource):

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files or 'faces' not in request.files:
            return make_response({'msg': 'Required fields not provided.'}, 500)
        bboxes = json.load(request.files['faces'])
        bboxes = list(map(
            lambda bbox: {'bounding_box': bbox, 'age': random.randint(4, 99)},
            bboxes
        ))
        return make_response({'age_estimation': bboxes}, 200)

