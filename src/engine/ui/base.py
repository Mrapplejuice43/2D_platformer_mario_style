from __future__ import annotations

from typing import Protocol, Self

from pygame import Surface

from engine.commons.window import Render


class Ui(Protocol):
    components: list[UiComponent]

    def render(self) -> Render: ...


class UiComponent(Protocol):
    children: list[Self]
    parent: Self

    def draw(self) -> Surface: ...
