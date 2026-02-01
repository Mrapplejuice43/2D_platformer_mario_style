from dataclasses import dataclass


@dataclass
class Config:
    window_size: tuple[int, int]
