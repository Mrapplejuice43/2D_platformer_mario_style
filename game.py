from camera import Camera
import numpy as np
from overlay import PauseMenu
from world import World


class Game:
    def __init__(self, windowSize, tileSize, gameScale, level=None):
        self.world = World(windowSize, tileSize, gameScale, level)
        self.windowSize = windowSize
        self.tileSize = tileSize
        self.scale = gameScale
        self.pause = False
        self.pauseOverlay = PauseMenu(windowSize[0], windowSize[1])

        self.worldOrigin = np.array((0, self.windowSize[1]))

        self.debugMode = False

    def update(self, keys, dt, sizeRatio):
        """
        Updates player's states and gameObjects' states
        """
        self.world.update(keys, dt, sizeRatio)

    def moveCamera(self, dx, dy):
        self.world.moveCamera(dx, dy)

    def switchDebugMode(self):
        self.debugMode = not self.debugMode
        self.world.switchDebugMode()

    def readWorld(self, fic):
        """
        Reads a formatted file which determine what is in the world
        :param fic: Path of the file to read
        """
        self.world.readWorld(fic)

    def changeLevel(self, level):
        self.world.changeLevel(level)

    def reset(self):
        self.world.resetWorld()

    def calculateDrawingCoordinates(self, obj):
        if isinstance(obj, Camera):
            return (
                (obj.initialValues[4] - self.worldOrigin) * np.array((1, -1)),
                (
                    (obj.initialValues[0] * self.tileSize[0],
                     self.worldOrigin[1] - obj.initialValues[2] * self.tileSize[1]),
                    ((obj.xmax - obj.xmin), obj.ymin - obj.ymax)
                )
            )

    def resize(self, windowSize, tileSize):
        self.world.resize(windowSize, tileSize)
        self.windowSize = windowSize
        self.tileSize = tileSize
        self.pauseOverlay.resize(windowSize[0], windowSize[1])

    def draw(self, screen):
        """
        Drawing function of the game
        """
        self.world.draw(screen)
