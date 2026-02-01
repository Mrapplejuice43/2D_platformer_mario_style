from dataclasses import dataclass, field
import logging
from typing import Callable


@dataclass
class EventCallback:
    event_name: str
    callback: Callable

    def __call__(self, *args, event, window, **kwargs) -> None:
        self.callback(event, window)


@dataclass
class EventRegistery:
    __logger = logging.getLogger(__name__)
    event_callbacks: dict[int, dict[str, EventCallback]] = field(default_factory=dict)

    def get_events_from_type(self, event_type: int) -> dict[str, EventCallback] | None:
        return self.event_callbacks.get(event_type)

    def register_event_callback(
        self, event_type: int, event_callback: EventCallback, replace_if_event_name_exists: bool = True
    ) -> None:
        """
        Adds or replace a callback in the registery

        Structure example :
        ```
        {
            pg.QUIT: {
                "set_should_close_to_true": (lambda ev, window: window._should_close = True),
                "do_something_else": reference_tu_function
            },
            pg.MOUSEBUTTONDOWN: {
                "do_something_with_mouse_position": do_something_function
            }
        }
        ```

        :param event_type: type of pygame event
        :type event_type: int
        :param event_callback: EventCallback object to register
        :type event_callback: EventCallback
        :param replace_if_event_name_exists: Replace callback if name already present in callback map for a specified event
        :type replace_if_event_name_exists: bool
        """
        if event_callbacks_map := self.event_callbacks.get(event_type):
            if event_callback.event_name in event_callbacks_map:
                if replace_if_event_name_exists:
                    self.__logger.debug(f"Event {event_callback.event_name} from {event_type} replaced")
                    event_callbacks_map.update({event_callback.event_name: event_callback})
                else:
                    self.__logger.warning(f"Event {event_callback.event_name} from {event_type} ignored")
            else:
                self.__logger.debug(f"Event {event_callback.event_name} added to {event_type} registery")
                event_callbacks_map.update({event_callback.event_name: event_callback})
        else:
            self.__logger.debug(f"Event {event_type} added to registery with event {event_callback.event_name}")
            self.event_callbacks.update({event_type: {event_callback.event_name: event_callback}})
