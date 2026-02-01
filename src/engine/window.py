import pygame as pg

from engine.event import EventCallback, EventRegistery

from .config import Config


class Window:
    config: Config

    _clock = pg.time.Clock()
    _screen: pg.Surface

    _registered_events: EventRegistery = EventRegistery()
    _should_close: bool = False

    def register_event(self, event_type: int, callback: EventCallback, replace_if_exists: bool = True) -> None:
        self._registered_events.register_event_callback(
            event_type=event_type, event_callback=callback, replace_if_event_name_exists=replace_if_exists
        )

    def _configure_window(self) -> None:
        self._screen = pg.display.set_mode(
            size=(self.config.window_size), flags=(pg.RESIZABLE), display=0, vsync=0, depth=0
        )

        def window_close(_, window: "Window") -> None:
            window._should_close = True

        self.register_event(pg.QUIT, EventCallback("set_should_close_to_true", window_close))

    def _process_events(self) -> None:
        events = pg.event.get()
        for event in events:
            if event_callbacks := self._registered_events.get_events_from_type(event.type):
                for callback_name in event_callbacks:
                    event_callbacks[callback_name](event=event, window=self)

    def _update_screen(self) -> None:
        pass

    def _update_time(self) -> None:
        pass

    def run(self) -> None:
        self._configure_window()
        while not self._should_close:
            self._update_time()
            self._update_screen()
            self._process_events()
            pg.display.flip()
