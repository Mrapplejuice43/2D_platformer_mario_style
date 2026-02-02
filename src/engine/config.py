from dataclasses import dataclass

from pygame import DOUBLEBUF, OPENGL, RESIZABLE

class WindowConfig:
    caption: str = "M2D"
    fullscreen: bool = False
    resizable: bool = True
    window_size: tuple[int, int] = (1280, 720)

    @property
    def flags(self) -> int:
        return OPENGL | RESIZABLE | DOUBLEBUF

@dataclass
class Config:
    window: WindowConfig = WindowConfig()
