import numpy as np
import cv2 as cv

from .primitives import BoundingBox, Point
from .proxies.primitives import ServiceSpecs


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


def create_bounding_box_covering_image(image: np.ndarray) -> BoundingBox:
    height, width = image.shape[:2]
    left_top, right_bottom = Point(x=0, y=0), Point(x=width, y=height)
    return BoundingBox(
        left_top=left_top,
        right_bottom=right_bottom
    )
