from typing import Optional, List, TypeVar

from pipeline_sdk.utils import translate_bounding_box
from retina_face_net import RetinaFaceNetPrediction
from retina_face_net import BoundingBox as RetinaBoundingBox

from .primitives import BoundingBox, Point


T = TypeVar('T')


def translate_results(inference_results: Optional[List[RetinaFaceNetPrediction]],
                      reference_bbox: BoundingBox
                      ) -> List[BoundingBox]:
    if inference_results is None:
        return []
    inferred_bboxes = (
        retina_bbox2pipeline_bbox(inference_result.bbox)
        for inference_result in inference_results
    )
    return [
        translate_bounding_box(
            bounding_box=bbox,
            reference_bounding_box=reference_bbox
        ) for bbox in inferred_bboxes
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

