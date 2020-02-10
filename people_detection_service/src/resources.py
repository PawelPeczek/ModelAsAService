import io

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
import numpy as np
import cv2

from .utils import generate_random_bboxes


class PeopleDetection(Resource):

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files:
            return make_response({'msg': 'Field named "image" required.'}, 500)
        in_memory_file = io.BytesIO()
        request.files['image'].save(in_memory_file)
        data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        bboxes = generate_random_bboxes(image.shape)
        return make_response({'people': bboxes}, 200)
