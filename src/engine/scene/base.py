from typing import Protocol

from engine.commons.window import Render


class BaseScene(Protocol):
    def render(self) -> Render: ...
