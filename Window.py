from Game import *
from World import *
from Overlay import *
from Editor import *
import numpy as np

GAME_STATE = 0
MAIN_MENU = 1
EDITOR_MODE = 2
BASESIZE = (1280, 720)


class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.sizeRatio = np.array((self.width, self.height)) / BASESIZE
        self.scale = 1

        self.clock = pygame.time.Clock()
        self.targetFPS = 60
        self.fps = self.clock.get_fps()
        self.time = pygame.time.get_ticks()

        self.shouldClose = False
        self.debugMode = False
        self.isGridDrawn = False
        self.tileSize = np.array((self.width // 48, self.height // 27)) * self.scale

        self.screen = pygame.display.set_mode((self.width, self.height), SWSURFACE | DOUBLEBUF | RESIZABLE)

        self.state = MAIN_MENU
        self.game = Game((self.width, self.height), self.tileSize, self.scale)
        self.editor = Editor((self.width, self.height), self.tileSize, self.scale)
        self.game.readWorld(r"worldTest.wd")

        self.menu = Menu(self.width, self.height)

        # For editor events
        self.mouseGrab = False
        self.mousePos = [0,0]

    def drawGame(self):
        """
        Drawing function of the game
        """
        self.game.draw(self.screen)

        if self.debugMode:
            self.screen.blit(
                pygame.font.SysFont("Consolas", 14, bold=True).render(
                    "fps : {0}".format(self.fps), False, (0, 0, 0)), (0, 20))

    def drawMenu(self):
        """
        Draws the menu at the 1st screen
        :return:
        """
        self.menu.draw(self.screen)

    def drawPauseMenu(self):
        """
        Draws the pause menu of the game
        :return:
        """
        self.game.pauseOverlay.draw(self.screen)

    def getKeys(self):
        """
        :return: list of keys pressed
        """
        return pygame.key.get_pressed()

    def update(self):
        """
        Updates the time to keep track of the physics
        :return:
        """
        self.fps = self.clock.get_fps()
        self.time = pygame.time.get_ticks()

    def resize(self, width, height):
        self.screen = pygame.display.set_mode((width, height),
                                              SWSURFACE | DOUBLEBUF | RESIZABLE)
        self.width = width
        self.height = height
        self.tileSize = np.array((self.width // 48, self.height // 27)) * self.scale
        self.sizeRatio = np.array((self.width, self.height)) / BASESIZE
        if self.state == MAIN_MENU:
            self.menu.resize(width, height)
        elif self.state == GAME_STATE:
            self.game.resize((width, height), self.tileSize)

    def resetWorld(self):
        self.game.reset()

    def handleEvents(self):
        """
        Retrieve events from pygame and process them to interact with the program and make the overlays work
        :return:
        """
        for event in pygame.event.get():

            if event.type == QUIT:
                self.shouldClose = True

            if self.state == GAME_STATE:
                if event.type == VIDEORESIZE:
                    self.resize(event.__dict__['w'], event.__dict__['h'])

                if event.type == CAMERA_TRIGGER:
                    self.game.moveCamera(event.__dict__["dx"], event.__dict__["dy"])

                if event.type == MENU_EVENT:
                    id = event.__dict__['id']

                    if id == PLAY_ID:
                        self.game.pause = not self.game.pause

                    if id == RESET_WORLD:
                        self.game.pause = not self.game.pause
                        self.game.reset()

                    if id == MAIN_MENU_ID:
                        self.game.reset()
                        self.game.pause = not self.game.pause
                        self.state = MAIN_MENU

                if event.type == MOUSEBUTTONDOWN:
                    if self.game.pause:
                        self.game.pauseOverlay.checkClickPos(event.pos)

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game.pause = not self.game.pause

                    if event.key == K_g:
                        self.isGridDrawn = not self.isGridDrawn

                    if event.key == K_F10:
                        self.debugMode = not self.debugMode
                        self.game.switchDebugMode()

                    if event.key == K_r:
                        self.worldOrigin = np.array((0, self.height))
                        self.game.reset()

                    if event.key == K_t:
                        self.targetFPS += 5

                    if event.key == K_y:
                        self.targetFPS -= 5

            elif self.state == MAIN_MENU:
                if event.type == VIDEORESIZE:
                    self.resize(event.__dict__['w'], event.__dict__['h'])

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.shouldClose = True

                if event.type == MOUSEBUTTONDOWN:
                    self.menu.checkClickPos(event.pos)

                if event.type == MENU_EVENT:
                    id = event.__dict__['id']

                    if id == PLAY_ID:
                        self.state = GAME_STATE

                    if id == QUIT_ID:
                        self.shouldClose = True

                    if id == EDITOR_ID:
                        self.state = EDITOR_MODE
                        self.editor = Editor((self.width, self.height), self.tileSize, self.scale)

            elif self.state == EDITOR_MODE:
                if event.type == KEYDOWN:
                    if event.__dict__['key'] == K_ESCAPE:
                        self.editor.pause = not self.editor.pause

                    elif event.__dict__['key'] == K_TAB:
                        self.editor.showOverlay = not self.editor.showOverlay

                elif event.type == MOUSEBUTTONDOWN:
                    if self.editor.pause:
                        self.editor.pauseOverlay.checkClickPos(event.pos)
                    else:
                        if self.editor.showOverlay and not self.editor.overlay.checkClickPos(event.pos):
                            if event.__dict__["button"] == 3:
                                self.mouseGrab = True
                                self.mousePos = event.__dict__['pos']
                            elif event.__dict__["button"] == 1:
                                self.editor.place(event.pos)

                elif event.type == MOUSEBUTTONUP:
                    if event.__dict__["button"] == 3:
                        self.mouseGrab = False

                elif event.type == MOUSEMOTION:
                    if self.mouseGrab:
                        self.mousePos = event.__dict__['pos']
                        dx, dy = event.__dict__['rel']
                        self.editor.move(-dx, dy)

                elif event.type == GAME_EVENT:
                    pass

                elif event.type == MENU_EVENT:
                    id = event.__dict__['id']

                    if id == PLAY_ID:
                        self.editor.pause = False

                    elif id == SAVE_ID:
                        pass

                    elif id == MAIN_MENU_ID:
                        self.state = MAIN_MENU

                elif event.type == EDITOR_EVENT:
                    id = event.__dict__['id']

                    if id == SELECT_GROUND:
                        self.editor.changeType(GROUND_TYPE)
                    elif id == SELECT_BLOCK:
                        self.editor.changeType(BLOCK_TYPE)
                    elif id == SELECT_PLAYER:
                        self.editor.changeType(PLAYER_TYPE)

    def run(self):
        """
        Main loop of the game
        """
        while not self.shouldClose:
            self.clock.tick(self.targetFPS)
            self.update()

            if self.state == MAIN_MENU:
                self.screen.fill((50, 50, 50))
                self.drawMenu()

            elif self.state == GAME_STATE:
                if self.fps > 0:
                    if not self.game.pause:
                        self.game.update(self.getKeys(), self.clock.get_time() / 1000, self.sizeRatio)
                        self.drawGame()

                    else:
                        self.drawGame()
                        self.drawPauseMenu()

            elif self.state == EDITOR_MODE:
                self.editor.draw(self.screen)

                if self.editor.showOverlay:
                    self.editor.drawOverlay(self.screen)
                if self.editor.pause:
                    self.editor.drawPauseOverlay(self.screen)

            self.handleEvents()
            pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    w, h = BASESIZE
    win = Window(w, h)
    win.run()
