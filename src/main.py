import logging
import sys
import pygame as pg
from engine.config import Config
from engine.window import Window


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    pg.init()
    pg.font.init()
    pg.mixer.init()
    config = Config(window_size=(1280, 720))
    win = Window()
    win.config = config
    win.run()
    pg.quit()


if __name__ == "__main__":
    main()
