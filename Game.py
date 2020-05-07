from V2.Overlay import *
from V2.Camera import *
from V2.World import *
import numpy as np


class Game:
    def __init__(self, windowSize, tileSize, gameScale):

        self.world = World(windowSize, tileSize, gameScale)
        self.camera = Camera(windowSize, tileSize, gameScale)
        self.windowSize = windowSize
        self.tileSize = tileSize
        self.scale = gameScale
        self.pause = False
        self.pauseOverlay = PauseMenu(windowSize[0], windowSize[1])

        self.worldOrigin = np.array((0, self.windowSize[1]))

        self.debugMode = False

    def update(self, keys, dt, sizeRatio):
        """
        Updates players states and gameObjects states
        """
        for go in self.world.gameObjects:

            if not go.onScreen:
                if ((go.pos[0] + go.width) * self.tileSize[0] > self.camera.xmin - self.camera.initialValues[0] * self.tileSize[0] and
                        go.pos[0] < self.camera.xmax - self.camera.initialValues[0] * self.tileSize[0]):
                    go.onScreen = True
                else:
                    go.onScreen = False

        for player in self.world.players:
            player.update(keys, dt, sizeRatio, self.world.gameObjects, self.tileSize, self.scale)
            self.camera.checkPlayerPos(player)

            if player.pos[1] + player.height * self.tileSize[1] < 0:
                self.reset()

    def moveCamera(self, dx, dy):
        self.world.worldOrigin += (dx, dy)
        self.camera.move(dx, dy)

    def switchDebugMode(self):
        self.debugMode = not self.debugMode
        self.world.switchDebugMode()

    def readWorld(self, fic):
        """
        Reads a formatted file which determine what is in the world
        :param fic: Path of the file to read
        """
        self.world.readWorld(fic)

    def reset(self):
        for player in self.world.players:
            player.reset()
        self.camera.reset()
        self.world.worldOrigin = np.array((0, self.windowSize[1]))

    def calculateDrawingCoordinates(self, obj):
        if isinstance(obj, Camera):
            # return (pos, rect) position of the camera and boundaries
            # return ((obj.pos - self.worldOrigin) * np.array((1, -1)),  # pos
            #         ((obj.xmin, self.worldOrigin[1] - obj.ymin),  # rect part 1
            #         ((obj.initialValues[1] - obj.initialValues[0]), -(self.worldOrigin[1] - obj.ymin + (obj.ymax - self.worldOrigin[1])))))  # rect part 2

            return (
                (obj.initialValues[4] - self.worldOrigin) * np.array((1, -1)),
                (
                    (obj.initialValues[0] * self.tileSize[0], self.worldOrigin[1] - obj.initialValues[2] * self.tileSize[1]),
                    ((obj.xmax - obj.xmin), obj.ymin - obj.ymax)
                )
            )

    def resize(self, windowSize, caseSize):
        self.world.resize(windowSize, caseSize)
        self.windowSize = windowSize
        self.tileSize = caseSize
        self.pauseOverlay.resize(windowSize[0], windowSize[1])
        self.camera.resize(windowSize, caseSize)

    def draw(self, screen):
        """
        Drawing function of the game
        """
        self.world.draw(screen)
        if self.debugMode:
            self.camera.draw(screen, self.calculateDrawingCoordinates(self.camera))