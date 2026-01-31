import pygame as pg
from _old.window import Window, BASESIZE

def main() -> None:
    pg.init()
    pg.font.init()
    pg.mixer.init()
    w, h = BASESIZE
    win = Window(w, h)
    win.run()


if __name__ == "__main__":
    main()
