from Game import *
from World import *
from Overlay import *
import numpy as np

GAME_STATE = 0
MAIN_MENU = 1
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
        self.game.readWorld(r"worldTest.wd")

        self.menu = Menu(self.width, self.height)

    def drawGrid(self):
        for l in range(self.height // self.tileSize[1] + 1):
            pygame.draw.line(
                self.screen, (0, 0, 0), (0, self.height - l * self.tileSize[1]),
                (self.width, self.height - l * self.tileSize[1]))

        for t in range(self.width // self.tileSize[0] + 1):
            pygame.draw.line(self.screen, (0, 0, 0),
                             (t * self.tileSize[0], 0), (t * self.tileSize[0], self.height))

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
        self.menu.draw(self.screen)

    def drawPauseMenu(self):
        self.game.pauseOverlay.draw(self.screen)

    def getKeys(self):
        """
        :return: list of keys pressed
        """
        return pygame.key.get_pressed()

    def update(self):
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
        for event in pygame.event.get():

            if self.state == GAME_STATE:
                if event.type == VIDEORESIZE:
                    self.resize(event.__dict__['w'], event.__dict__['h'])

                if event.type == QUIT:
                    self.shouldClose = True

                if event.type == CAMERA_TRIGGER:
                    self.game.moveCamera(event.__dict__["dx"], event.__dict__["dy"])

                if event.type == GAME_EVENT:
                    id = event.__dict__['id']

                    if id == PLAY_EVENT:
                        self.game.pause = not self.game.pause

                    if id == RESET_WORLD:
                        self.game.pause = not self.game.pause
                        self.game.reset()

                    if id == MAIN_MENU_EVENT:
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

                if event.type == GAME_EVENT:
                    id = event.__dict__['id']

                    if id == PLAY_EVENT:
                        self.state = GAME_STATE

                    if id == QUIT_EVENT:
                        self.shouldClose = True

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

            if self.isGridDrawn:
                self.drawGrid()

            self.handleEvents()
            pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    w, h = BASESIZE
    win = Window(w, h)
    win.run()
