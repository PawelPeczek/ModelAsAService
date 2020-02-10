import random
from typing import Tuple, List

BoundingBox = Tuple[Tuple[int, int], Tuple[int, int]]


def generate_random_bboxes(image_size: Tuple[int, int, int]
                           ) -> List[BoundingBox]:
    bboxes_number = random.randint(0, 6)
    result = []
    for _ in range(bboxes_number):
        random_bbox = _generate_random_bbox(image_size=image_size)
        result.append(random_bbox)
    return result


def _generate_random_bbox(image_size: Tuple[int, int, int]
                          ) -> BoundingBox:
    height, width = image_size[:2]
    center_x, center_y = random.randint(0, width), random.randint(0, height)
    bbox_height, bbox_width = \
        random.randint(0, int(width / 3)), random.randint(0, int(height / 3))
    half_bbox_height, half_bbox_width = \
        int(bbox_height / 2), int(bbox_width / 2)
    return (
        (
            max(center_x - half_bbox_width, 0),
            max(center_y - half_bbox_height, 0)
        ),
        (
            min(center_x + half_bbox_width, width),
            min(center_y + half_bbox_height, height)
        )
    )
