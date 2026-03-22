import json
import logging
from typing import Self

import pygame as pg

from engine.commons.window import WindowType

from .config import Config
from .event import EventCallback, EventRegistery


class Window(WindowType):
    __logger = logging.getLogger(__name__)

    _clock = pg.time.Clock()

    _registered_events: EventRegistery = EventRegistery()
    _should_close = False

    _record_events = False
    _recorded_events = {}

    active_scene = None

    def _configure_window(self) -> None:
        self._screen = pg.display.set_mode(
            size=self._config.window.window_size,
            flags=self._config.window.flags,
            display=0,
            vsync=self._config.window.vsync,
            depth=0,
        )
        pg.display.set_caption(self._config.window.caption)

        def window_close(event: pg.event.Event, window: WindowType) -> None:
            window._should_close = True

        def window_close_keyboard(event: pg.event.Event, window: WindowType) -> None:
            if (key := event.dict.get("key")) and (key == pg.K_ESCAPE):
                window._should_close = True

        def toggle_recording(event: pg.event.Event, window: WindowType) -> None:
            if (key := event.dict.get("key")) and (key == pg.K_r):
                window._record_events = not window._record_events
                self.__logger.debug(f"{'Started' if window._record_events else 'Stopped'} recording events")

        self.register_event(pg.QUIT, EventCallback("set_should_close_to_true", window_close))
        self.register_event(pg.KEYDOWN, EventCallback("set_should_close_to_true", window_close_keyboard))
        self.register_event(pg.KEYDOWN, EventCallback("toggle_event_recording", toggle_recording))

    def _process_events(self) -> None:
        events = pg.event.get()
        for event in events:
            self.__logger.debug(f"Event {pg.event.event_name(event.type)} : {event.dict}")
            if self._record_events:
                self._record_event(event)
            if event_callbacks := self._registered_events.get_events_from_type(event.type):
                for callback_name in event_callbacks:
                    self.__logger.debug(f"Event {callback_name} called from event {pg.event.event_name(event.type)}")
                    event_callbacks[callback_name](event=event, window=self)

    def _record_event(self, event: pg.event.Event) -> None:
        event_name = pg.event.event_name(event.type)
        if event_name not in self._recorded_events.keys():
            self._recorded_events.update({event_name: event.dict})

    def _update_screen(self) -> None:
        if self.active_scene:
            render = self.active_scene.render()
            self._screen.blit(
                source=render.source, dest=render.dest, area=render.area, special_flags=render.special_flags
            )
            return

        self._screen.fill(pg.Color(50, 50, 50))

    def _update_time(self) -> None:
        self._clock.tick(self._config.window.target_fps.value)

    def register_event(self, event_type: int, callback: EventCallback, replace_if_exists: bool = True) -> None:
        self.__logger.debug(f"Registering event {event_type} with callback {callback}")
        self._registered_events.register_event_callback(
            event_type=event_type, event_callback=callback, replace_if_event_name_exists=replace_if_exists
        )

    def run(self) -> None:
        self._configure_window()
        while not self._should_close:
            self._update_time()
            self._update_screen()
            self._process_events()
            pg.display.flip()

        if self._recorded_events:
            with open("event_records.txt", "+w") as f:
                json.dump(self._recorded_events, f)

    def set_config(self, config: Config) -> Self:
        self._config = config
        return self
