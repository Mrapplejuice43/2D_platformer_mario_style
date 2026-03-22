from typing import Any, Protocol, Self

from pygame import Surface, Vector2
from pygame.event import Event
from pygame.time import Clock

from engine.commons.core import RectValue
from engine.scene.base import BaseScene
from engine.window.config import Config
from engine.window.event import EventCallback, EventRegistery


class Render(Protocol):
    source: Surface
    dest: tuple[float, float] | Vector2
    area: RectValue | None = None
    special_flags: int = 0


class WindowType(Protocol):
    _clock = Clock
    _screen: Surface

    _config: Config
    _registered_events: EventRegistery
    _should_close: bool

    _record_events: bool
    _recorded_events: dict[str, dict[str, Any]]

    active_scene: BaseScene | None

    def _configure_window(self) -> None: ...
    def _process_events(self) -> None: ...
    def _record_event(self, event: Event) -> None: ...
    def _update_screen(self) -> None: ...
    def _update_time(self) -> None: ...

    def register_event(self, event_type: int, callback: EventCallback, replace_if_exists: bool = True) -> None: ...
    def run(self) -> None: ...
    def set_config(self, config: Config) -> Self: ...
