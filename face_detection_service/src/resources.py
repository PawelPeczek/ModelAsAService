import json
from typing import Tuple

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource


BoundingBox = Tuple[Tuple[int, int], Tuple[int, int]]


class FacesDetection(Resource):

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files or 'people' not in request.files:
            return make_response({'msg': 'Required fields not provided.'}, 500)
        people = json.load(request.files['people'])
        return make_response({'faces': people}, 200)

