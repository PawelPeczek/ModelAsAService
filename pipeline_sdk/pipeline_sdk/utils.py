import random
from typing import List, TypeVar, Optional, Tuple

import numpy as np
import cv2 as cv

from .primitives import BoundingBox, Point
from .proxies.primitives import ServiceSpecs


T = TypeVar('T')


def compose_url(service_specs: ServiceSpecs,
                path_postfix: str) -> str:
    relative_resource_url = compose_relative_resource_url(
        service_name=service_specs.service_name,
        service_version=service_specs.version,
        path_postfix=path_postfix
    )
    return f"{service_specs.host}:{service_specs.port}{relative_resource_url}"


def compose_relative_resource_url(service_name: str,
                                  service_version: str,
                                  path_postfix: str
                                  ) -> str:
    if path_postfix.startswith('/'):
        path_postfix = path_postfix.lstrip('/')
    return f"/{service_version}/{service_name}/{path_postfix}"


def image_to_jpeg_bytes(image: np.ndarray,
                        compression_rate: int = 90
                        ) -> bytes:
    if compression_rate <= 0 or compression_rate > 100:
        raise ValueError("Compression rate must be in range (0; 100]")
    encode_param = [int(cv.IMWRITE_JPEG_QUALITY), compression_rate]
    _, raw_image = cv.imencode('.jpg', image, encode_param)
    return raw_image


def image_from_str(raw_image: str) -> np.ndarray:
    data = np.fromstring(raw_image, dtype=np.uint8)
    return cv.imdecode(data, cv.IMREAD_COLOR)


def create_bounding_box_covering_image(image: np.ndarray) -> BoundingBox:
    height, width = image.shape[:2]
    left_top, right_bottom = Point(x=0, y=0), Point(x=width, y=height)
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


def take_image_crops(image: np.ndarray,
                     bounding_boxes: List[BoundingBox]
                     ) -> List[Optional[np.ndarray]]:
    return [
        take_image_crop(image, bounding_box) for bounding_box in bounding_boxes
    ]


def take_image_crop(image: np.ndarray,
                    bounding_box: BoundingBox
                    ) -> Optional[np.ndarray]:
    return image[
        bounding_box.left_top.y:bounding_box.right_bottom.y,
        bounding_box.left_top.x:bounding_box.right_bottom.x
    ]


def generate_random_bboxes(image_size: Tuple[int, int, int]
                           ) -> List[BoundingBox]:
    return [
        _generate_random_bbox(image_size=image_size)
        for _ in range(random.randint(0, 6))
    ]


def _generate_random_bbox(image_size: Tuple[int, int, int]
                          ) -> BoundingBox:
    height, width = image_size[:2]
    center_x, center_y = random.randint(0, width), random.randint(0, height)
    bbox_height, bbox_width = \
        random.randint(0, int(width / 3)), random.randint(0, int(height / 3))
    half_bbox_height, half_bbox_width = int(bbox_height / 2), int(bbox_width / 2)
    left_top = Point(
        x=max(center_x - half_bbox_width, 0),
        y=max(center_y - half_bbox_height, 0)
    )
    right_bottom = Point(
        x=min(center_x + half_bbox_width, width),
        y=min(center_y + half_bbox_height, height)
    )
    return BoundingBox(
        left_top=left_top,
        right_bottom=right_bottom
    )


def decode_bboxes(raw_bboxes: List[dict]) -> List[BoundingBox]:
    return [
        BoundingBox.from_dict(raw_bbox) for raw_bbox in raw_bboxes
    ]
