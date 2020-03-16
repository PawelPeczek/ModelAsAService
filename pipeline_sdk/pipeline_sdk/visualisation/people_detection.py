from typing import List

import numpy as np

from ..config import PEOPLE_DETECTION_COLOR
from ..primitives import BoundingBox
from .utils import draw_bbox


def draw_people_detections(image: np.ndarray,
                           people_detections: List[BoundingBox]
                           ) -> np.ndarray:
    image = image.copy()
    for people_detection in people_detections:
        image = draw_bbox(
            input_image=image,
            people_detection=people_detection,
            color=PEOPLE_DETECTION_COLOR
        )
    return image

