from dataclasses import dataclass
from typing import Protocol

from pygame import Surface, Vector2

from _types.commons import RectValue


@dataclass
class SceneRender:
    source: Surface
    dest: tuple[float, float] | Vector2
    area: RectValue | None = None
    special_flags: int = 0


class BaseScene(Protocol):
    def render(self) -> SceneRender: ...
