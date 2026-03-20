from dataclasses import dataclass, field
from enum import IntEnum

from pygame import RESIZABLE


class FPSTarget(IntEnum):
    TWENTY_FIVE = 25
    THIRTY = 30
    SIXTY = 60
    ONE_TWENTY = 120
    ONE_FOURTY_FOUR = 144
    TWO_FOURTY = 240
    THREE_SIXTY = 360
    UNCAPPED = 960


@dataclass
class WindowConfig:
    caption: str = "M2D"
    fullscreen: bool = False
    resizable: bool = False
    target_fps: FPSTarget = field(default=FPSTarget.SIXTY)
    vsync: bool = False
    window_size: tuple[int, int] = (1280, 720)

    @property
    def flags(self) -> int:
        if self.resizable:
            return RESIZABLE

        return 0


@dataclass
class Config:
    window: WindowConfig = field(default_factory=WindowConfig)
