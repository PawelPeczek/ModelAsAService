from functools import partial
from typing import List, Tuple

import cv2 as cv
import numpy as np

from ..config import AGE_ESTIMATION_COLOR, AGE_BLURRING_THRESHOLD
from .utils import for_each
from ..primitives import AgeEstimationResult


def place_age_estimation_on_image(image: np.ndarray,
                                  age_estimations: List[AgeEstimationResult]
                                  ) -> np.ndarray:
    image = image.copy()
    place_age_estimation_on_image = partial(
        place_age_estimation, image=image, color=AGE_ESTIMATION_COLOR
    )
    for_each(iterable=age_estimations, side_effect=place_age_estimation_on_image)
    return image


def blind_image_according_to_age(image: np.ndarray,
                                 age_estimations: List[AgeEstimationResult]
                                 ) -> np.ndarray:
    image = image.copy()
    blind_region = partial(
        blind_region_according_to_age_estimation,
        image=image,
        age_threshold=AGE_BLURRING_THRESHOLD
    )
    for_each(iterable=age_estimations, side_effect=blind_region)
    return image


def place_age_estimation(age_estimation: AgeEstimationResult,
                         image: np.ndarray,
                         color: Tuple[int, int, int]
                         ) -> None:
    prior_bbox_center = age_estimation.bounding_box.center
    if age_estimation.associated_age is not None :
        text = f'{age_estimation.associated_age}'
    else:
        text = 'N/A'
    cv.putText(
        image,
        text,
        prior_bbox_center.to_tuple(),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        color
    )


def blind_region_according_to_age_estimation(age_estimation: AgeEstimationResult,
                                             image: np.ndarray,
                                             age_threshold: int
                                             ) -> None:
    estimated_age = age_estimation.associated_age
    if estimated_age is not None and estimated_age > age_threshold:
        return None
    left_top = age_estimation.bounding_box.left_top
    right_bottom = age_estimation.bounding_box.right_bottom
    image[left_top.y:right_bottom.y, left_top.x:right_bottom.x] = 127

