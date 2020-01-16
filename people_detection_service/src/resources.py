import io
import random
from typing import Tuple, List

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource

import numpy as np
import cv2


BoundingBox = Tuple[Tuple[int, int], Tuple[int, int]]


class PeopleDetection(Resource):

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files:
            return make_response({'msg': 'Field named "image" required.'}, 500)
        in_memory_file = io.BytesIO()
        request.files['image'].save(in_memory_file)
        data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        bboxes = self.__generate_random_bboxes(image.shape)
        return make_response({'people': bboxes}, 200)

    def __generate_random_bboxes(self,
                                 image_size: Tuple[int, int, int]
                                 ) -> List[BoundingBox]:
        bboxes_number = random.randint(0, 6)
        result = []
        for _ in range(bboxes_number):
            random_bbox = self.__generate_random_bbox(image_size=image_size)
            result.append(random_bbox)
        return result

    def __generate_random_bbox(self,
                               image_size: Tuple[int, int, int]
                               ) -> BoundingBox:
        height, width = image_size[:2]
        center_x, center_y = random.randint(0, width), random.randint(0, height)
        bbox_height, bbox_width = \
            random.randint(0, int(width/3)), random.randint(0, int(height/3))
        half_bbox_height, half_bbox_width = \
            int(bbox_height / 2), int(bbox_width / 2)
        return (
            (
                max(center_x - half_bbox_width, 0),
                max(center_y - half_bbox_height, 0)
            ),
            (
                min(center_x + half_bbox_width, width),
                min(center_y + half_bbox_height, height)
            )
        )
