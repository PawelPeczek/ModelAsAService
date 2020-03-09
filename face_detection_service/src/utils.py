from typing import Optional, List, TypeVar

import numpy as np
from retina_face_net import RetinaFaceNetPrediction
from retina_face_net import BoundingBox as RetinaBoundingBox

from .primitives import BoundingBox, Point


T = TypeVar('T')


def take_image_crop(image: np.ndarray,
                    bounding_box: BoundingBox
                    ) -> Optional[np.ndarray]:
    return image[
        bounding_box.left_top.y:bounding_box.right_bottom.y,
        bounding_box.left_top.x:bounding_box.right_bottom.x
    ]


def translate_results(inference_results: Optional[List[RetinaFaceNetPrediction]],
                      reference_bbox: BoundingBox
                      ) -> List[BoundingBox]:
    if inference_results is None:
        return []
    infered_bboxes = (
        retina_bbox2pipeline_bbox(inference_result.bbox)
        for inference_result in inference_results
    )
    return [
        translate_bounding_box(
            bounding_box=bbox,
            reference_bounding_box=reference_bbox
        ) for bbox in infered_bboxes
    ]


def retina_bbox2pipeline_bbox(retina_bbox: RetinaBoundingBox) -> BoundingBox:
    left_top = Point(
        x=retina_bbox.left_top.x,
        y=retina_bbox.left_top.y
    )
    right_bottom = Point(
        x=retina_bbox.right_bottom.x,
        y=retina_bbox.right_bottom.y
    )
    return BoundingBox(
        left_top=left_top,
        right_bottom=right_bottom
    )


def translate_bounding_box(bounding_box: BoundingBox,
                           reference_bounding_box: BoundingBox
                           ) -> BoundingBox:
    x_shift, y_shift = reference_bounding_box.left_top.to_tuple()
    translated_left_top = Point(
        x=bounding_box.left_top.x + x_shift,
        y=bounding_box.left_top.y + y_shift
    )
    translated_right_bottom = Point(
        x=bounding_box.right_bottom.x + x_shift,
        y=bounding_box.right_bottom.y + y_shift
    )
    return BoundingBox(
        left_top=translated_left_top,
        right_bottom=translated_right_bottom
    )


def flatten(input_list: List[List[T]]) -> List[T]:
    return [
        e for inner_list in input_list for e in inner_list
    ]
