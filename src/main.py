import logging
import sys
import pygame as pg
from engine.config import Config
from engine.window import Window


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="[%(levelname)s] [%(threadName)s] - %(asctime)s - %(name)s:%(funcName)s:%(lineno)s - %(message)s")
    pg.init()
    pg.font.init()
    pg.mixer.init()
    logging.getLogger(__name__).debug(pg.joystick.get_count())
    config = Config()
    win = Window().set_config(config)
    win.run()
    pg.quit()


if __name__ == "__main__":
    main()
