from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple

PointTuple = Tuple[int, int]
CompactPoint = Dict[str, int]
BoundingBoxTuple = Tuple[PointTuple, PointTuple]
CompactBoundingBox = Dict[str, CompactPoint]


@dataclass
class Point:
    x: int
    y: int

    def to_tuple(self) -> PointTuple:
        return self.x, self.y

    def to_dict(self) -> CompactPoint:
        return {
            'x': self.x,
            'y': self.y
        }

    @classmethod
    def from_dict(cls, point_dict: CompactPoint) -> Point:
        x = point_dict['x']
        y = point_dict['y']
        return cls(
            x=x,
            y=y
        )


@dataclass
class BoundingBox:
    left_top: Point
    right_bottom: Point

    def to_tuple(self) -> BoundingBoxTuple:
        return self.left_top.to_tuple(), self.right_bottom.to_tuple()

    def to_dict(self) -> CompactBoundingBox:
        return {
            'left_top': self.left_top.to_dict(),
            'right_bottom': self.right_bottom.to_dict()
        }

    @property
    def size(self) -> int:
        height = self.right_bottom.y - self.left_top.y
        width = self.right_bottom.x - self.left_top.y
        return height * width

    @classmethod
    def from_dict(cls, bounding_box_dict: CompactBoundingBox) -> BoundingBox:
        left_top = Point.from_dict(bounding_box_dict['left_top'])
        right_bottom = Point.from_dict(bounding_box_dict['right_bottom'])
        return cls(
            left_top=left_top,
            right_bottom=right_bottom
        )
