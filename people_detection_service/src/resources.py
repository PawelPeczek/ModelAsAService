import logging
from typing import Set, List, Tuple

from flask import Response, request, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
import numpy as np
import cv2 as cv
from tensorflow.python.keras import Model
import tensorflow as tf
from tensorflow.python.keras.backend import set_session

from .primitives import InferenceResults, BoundingBox, Point


logging.getLogger().setLevel(logging.INFO)


class PeopleDetection(Resource):

    def __init__(self,
                 model: Model,
                 session: tf.Session,
                 graph: tf.Graph,
                 confidence_threshold: float,
                 classes_to_fetch: Set[int],
                 max_image_dim: int):
        self.__model = model
        self.__session = session
        self.__graph = graph
        self.__confidence_threshold = confidence_threshold
        self.__classes_to_fetch = classes_to_fetch
        self.__max_image_dim = max_image_dim

    @jwt_required
    def post(self) -> Response:
        if 'image' not in request.files:
            return make_response({'msg': 'Field named "image" required.'}, 500)
        data = np.fromstring(request.files['image'].read(), dtype=np.uint8)
        image = cv.imdecode(data, cv.IMREAD_COLOR)
        results = self.__infer_from_image(image=image)
        return make_response({'people': results}, 200)

    def __infer_from_image(self,
                           image: np.ndarray
                           ) -> InferenceResults:
        image, scale = self.__standardize_image(image=image)
        logging.info(f"Standardized image shape: {image.shape}. scale: {scale}")
        expanded_image = np.expand_dims(image, axis=0)
        set_session(self.__session)
        with self.__graph.as_default():
            boxes, scores, labels = self.__model.predict_on_batch(
                x=expanded_image
            )
        boxes /= scale
        return self.__post_process_inference(
            boxes=boxes[0],
            scores=scores[0],
            labels=labels[0]
        )

    def __standardize_image(self,
                            image: np.ndarray
                            ) -> Tuple[np.ndarray, float]:
        max_shape = max(image.shape[:2])
        if max_shape <= self.__max_image_dim:
            return image, 1.0
        scale = self.__max_image_dim / max_shape
        resized_image = cv.resize(image, dsize=None, fx=scale, fy=scale)
        return resized_image, scale

    def __post_process_inference(self,
                                 boxes: np.ndarray,
                                 scores: np.ndarray,
                                 labels: np.ndarray
                                 ) -> InferenceResults:
        inference_results = []
        for bbox, score, label in zip(boxes, scores, labels):
            if self.__result_does_not_match(score=score, label=label):
                continue
            inference_result = self.__wrap_bounding_box(
                bbox_specs=bbox
            )
            if inference_result.size > 0:
                inference_results.append(inference_result)
        return inference_results

    def __result_does_not_match(self, score: float, label: int) -> bool:
        return score < self.__confidence_threshold or \
            label not in self.__classes_to_fetch

    def __wrap_bounding_box(self, bbox_specs: List[float]) -> BoundingBox:
        left_top = Point(
            x=int(round(bbox_specs[0])),
            y=int(round(bbox_specs[1]))
        )
        right_bottom = Point(
            x=int(round(bbox_specs[2])),
            y=int(round(bbox_specs[3]))
        )
        return BoundingBox(
            left_top=left_top,
            right_bottom=right_bottom
        )
