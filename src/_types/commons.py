from __future__ import annotations

from typing import Sequence

from pygame import Rect, Vector2

Coordinate = tuple[float, float] | Vector2 | Sequence[float]
Number = float | int

RectValue = (
    Rect
    | tuple[Number, Number, Number, Number]
    | tuple[Coordinate, Coordinate]
    | Sequence[Number]
    | Sequence[Coordinate]
)
