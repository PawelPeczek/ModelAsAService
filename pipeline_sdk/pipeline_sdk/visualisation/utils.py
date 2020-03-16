from typing import Tuple

import numpy as np
import cv2 as cv

from ..primitives import BoundingBox


def draw_bbox(input_image: np.ndarray,
              people_detection: BoundingBox,
              color: Tuple[int, int, int],
              thickness: int = 3
              ) -> np.ndarray:
    cv.rectangle(
        img=input_image,
        pt1=people_detection.left_top.to_tuple(),
        pt2=people_detection.right_bottom.to_tuple(),
        color=color,
        thickness=thickness
    )
    return input_image
