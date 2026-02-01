from logging import Logger
import os
import pygame as pg
import numpy as np

from .constants import WORLDS_PATH

from .editor import Editor
from .game import Game
from .overlay import Menu
from pygame.locals import (
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    KEYDOWN,
    K_ESCAPE,
    K_TAB,
    K_g,
    K_F10,
    K_r,
    K_t,
    K_y,
    QUIT,
    VIDEORESIZE,
    SWSURFACE,
    DOUBLEBUF,
    RESIZABLE,
)
from .camera import CAMERA_TRIGGER
from .component import MENU_EVENT, GAME_EVENT, EDITOR_EVENT
from .overlay import (
    PLAY_ID,
    EDITOR_ID,
    MAIN_MENU_ID,
    SELECT_GROUND,
    SELECT_BLOCK,
    SELECT_PLAYER,
    RESET_WORLD,
    QUIT_ID,
    SAVE_ID,
    CHANGE_MODE,
)
from .editor import GROUND_TYPE, BLOCK_TYPE, PLAYER_TYPE


GAME_STATE = 0
MAIN_MENU = 1
EDITOR_MODE = 2
BASESIZE = (1280, 720)

_logger = Logger("WindowLogger")
_logger.setLevel("INFO")


class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size_ratio = np.array((self.width, self.height)) / BASESIZE
        self.scale = 1

        self.clock = pg.time.Clock()
        self.target_fps = 60
        self.fps = self.clock.get_fps()
        self.time = pg.time.get_ticks()

        self.should_close = False
        self.debug_mode = False
        self.is_grid_drawn = False
        self.tile_size = np.array((self.width // 48, self.height // 27)) * self.scale

        self.screen = pg.display.set_mode((self.width, self.height))

        self.state = MAIN_MENU
        self.game = Game((self.width, self.height), self.tile_size, self.scale)
        self.editor = Editor((self.width, self.height), self.tile_size, self.scale)
        self.game.read_world(os.path.join(WORLDS_PATH, "worldTest.wd"))

        self.menu = Menu(self.width, self.height)

        # For editor events
        self.mouse_grab = False
        self.mouse_pos = [0, 0]

    def draw_game(self):
        """
        Drawing function of the game
        """
        self.game.draw(self.screen)

        if self.debug_mode:
            self.screen.blit(
                pg.font.SysFont("Consolas", 14, bold=True).render("fps : {0}".format(self.fps), False, (0, 0, 0)),
                (0, 20),
            )

    def draw_menu(self):
        """
        Draws the menu at the 1st screen
        :return:
        """
        self.menu.draw(self.screen)

    def draw_pause_menu(self):
        """
        Draws the pause menu of the game
        :return:
        """
        self.game.pause_sverlay.draw(self.screen)

    def get_keys(self):
        """
        :return: list of keys pressed
        """
        return pg.key.get_pressed()

    def update(self):
        """
        Updates the time to keep track of the physics
        :return:
        """
        self.fps = self.clock.get_fps()
        self.time = pg.time.get_ticks()

    def resize(self, width, height):
        self.screen = pg.display.set_mode((width, height), SWSURFACE | DOUBLEBUF | RESIZABLE)
        self.width = width
        self.height = height
        self.tile_size = np.array((self.width // 48, self.height // 27)) * self.scale
        self.size_ratio = np.array((self.width, self.height)) / BASESIZE
        if self.state == MAIN_MENU:
            self.menu.resize(width, height)
        elif self.state == GAME_STATE:
            self.game.resize((width, height), self.tile_size)

    def reset_world(self):
        self.game.reset()

    def handle_events(self):
        """
        Retrieve events from pygame and process them to interact with the program and make the overlays work
        :return:
        """
        for event in pg.event.get():
            _logger.info(event)
            if event.type == QUIT:
                self.should_close = True

            if self.state == GAME_STATE:
                if event.type == VIDEORESIZE:
                    self.resize(event.__dict__["w"], event.__dict__["h"])

                if event.type == CAMERA_TRIGGER:
                    self.game.move_camera(event.__dict__["dx"], event.__dict__["dy"])

                if event.type == MENU_EVENT:
                    event_id = event.__dict__["id"]

                    if event_id == PLAY_ID:
                        self.game.pause = not self.game.pause

                    if event_id == RESET_WORLD:
                        self.game.pause = not self.game.pause
                        self.game.reset()

                    if event_id == MAIN_MENU_ID:
                        self.game.reset()
                        self.game.pause = not self.game.pause
                        self.state = MAIN_MENU

                if event.type == MOUSEBUTTONDOWN and self.game.pause:
                    self.game.pause_sverlay.check_click_pos(event.pos)

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game.pause = not self.game.pause

                    if event.key == K_g:
                        self.is_grid_drawn = not self.is_grid_drawn

                    if event.key == K_F10:
                        self.debug_mode = not self.debug_mode
                        self.game.switch_debug_mode()

                    if event.key == K_r:
                        self.game.reset()

                    if event.key == K_t:
                        self.target_fps += 5

                    if event.key == K_y:
                        self.target_fps -= 5

            elif self.state == MAIN_MENU:
                if event.type == VIDEORESIZE:
                    self.resize(event.__dict__["w"], event.__dict__["h"])

                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.should_close = True

                if event.type == MOUSEBUTTONDOWN:
                    self.menu.check_click_pos(event.pos)

                if event.type == MENU_EVENT:
                    event_id = event.__dict__["id"]

                    if event_id == PLAY_ID:
                        self.state = GAME_STATE

                    if event_id == QUIT_ID:
                        self.should_close = True

                    if event_id == EDITOR_ID:
                        self.state = EDITOR_MODE
                        self.editor = Editor((self.width, self.height), self.tile_size, self.scale)

            elif self.state == EDITOR_MODE:
                if event.type == KEYDOWN:
                    if event.__dict__["key"] == K_ESCAPE:
                        self.editor.pause = not self.editor.pause

                    elif event.__dict__["key"] == K_TAB:
                        self.editor.show_overlay = not self.editor.show_overlay

                elif event.type == MOUSEBUTTONDOWN:
                    if self.editor.pause:
                        self.editor.pause_overlay.check_click_pos(event.pos)
                    else:
                        if self.editor.show_overlay and not self.editor.overlay.check_click_pos(event.pos):
                            if event.__dict__["button"] == 3:
                                self.mouse_grab = True
                                self.mouse_pos = event.__dict__["pos"]
                            elif event.__dict__["button"] == 1:
                                self.editor.place(event.pos)
                        elif not self.editor.show_overlay:
                            if event.__dict__["button"] == 1:
                                self.editor.place(event.pos)

                elif event.type == MOUSEBUTTONUP:
                    if event.__dict__["button"] == 3:
                        self.mouse_grab = False

                elif event.type == MOUSEMOTION:
                    if self.mouse_grab:
                        self.mouse_pos = event.__dict__["pos"]
                        dx, dy = event.__dict__["rel"]
                        self.editor.move(-dx, dy)

                elif event.type == GAME_EVENT:
                    pass

                elif event.type == MENU_EVENT:
                    event_id = event.__dict__["id"]

                    if event_id == PLAY_ID:
                        self.editor.pause = False

                    elif event_id == SAVE_ID:
                        pass

                    elif event_id == MAIN_MENU_ID:
                        self.state = MAIN_MENU

                elif event.type == EDITOR_EVENT:
                    event_id = event.__dict__["id"]

                    if event_id == SELECT_GROUND:
                        self.editor.change_type(GROUND_TYPE)
                    elif event_id == SELECT_BLOCK:
                        self.editor.change_type(BLOCK_TYPE)
                    elif event_id == SELECT_PLAYER:
                        self.editor.change_type(PLAYER_TYPE)
                    elif event_id == CHANGE_MODE:
                        self.editor.change_mode()

    def run(self):
        """
        Main loop of the game
        """
        while not self.should_close:
            self.clock.tick(self.target_fps)
            self.update()

            if self.state == MAIN_MENU:
                self.screen.fill((50, 50, 50))
                self.draw_menu()

            elif self.state == GAME_STATE:
                if self.fps > 0:
                    if not self.game.pause:
                        self.game.update(self.get_keys(), self.clock.get_time() / 1000, self.size_ratio)
                        self.draw_game()

                    else:
                        self.draw_game()
                        self.draw_pause_menu()

            elif self.state == EDITOR_MODE:
                self.editor.draw(self.screen)

                if self.editor.show_overlay:
                    self.editor.draw_overlay(self.screen)
                if self.editor.pause:
                    self.editor.draw_pause_overlay(self.screen)

            self.handle_events()
            pg.display.flip()


if __name__ == "__main__":
    pg.init()
    w, h = BASESIZE
    win = Window(w, h)
    win.run()
