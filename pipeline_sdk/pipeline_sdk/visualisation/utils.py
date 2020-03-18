from typing import Tuple, TypeVar, Iterable, Callable

import numpy as np
import cv2 as cv

from ..primitives import BoundingBox


T = TypeVar('T')


def draw_bbox(bounding_box: BoundingBox,
              input_image: np.ndarray,
              color: Tuple[int, int, int],
              thickness: int = 3
              ) -> None:
    cv.rectangle(
        img=input_image,
        pt1=bounding_box.left_top.to_tuple(),
        pt2=bounding_box.right_bottom.to_tuple(),
        color=color,
        thickness=thickness
    )


def for_each(iterable: Iterable[T], side_effect: Callable[[T], None]) -> None:
    for element in iterable:
        side_effect(element)
