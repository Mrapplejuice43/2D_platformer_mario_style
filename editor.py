from overlay import EditorPauseMenu,  EditorMenu
import os
import re
import numpy as np
import pygame

from world import World

# Editing modes
PLACE_MODE = 0
REMOVE_MODE = 1

# Object types of the game
GROUND_TYPE = 0
BLOCK_TYPE = 1
PLAYER_TYPE = 2


class Editor():
    def __init__(self, windowSize, tileSize, gameScale):
        self.world = World(windowSize, tileSize, gameScale)
        self.worldSize = [200, 50]

        self.tmpWorld = self.generateEmptyWorld()

        num = 1
        while os.path.exists(r"worlds/newWorld{}.w".format(num)):
            num += 1
        self.worldFile = r"worlds/newWorld{}.w".format(num)

        self.windowSize = windowSize
        self.tileSize = tileSize
        self.gameScale = gameScale
        self.pause = False
        self.overlay = EditorMenu(windowSize[0], windowSize[1])
        self.pauseOverlay = EditorPauseMenu(windowSize[0], windowSize[1])
        self.showOverlay = True
        self.pause = False

        self.worldOrigin = np.array((0, self.windowSize[1]))
        self.offset = [0, 0]
        self.mode = PLACE_MODE
        self.type = GROUND_TYPE

        self.debugMode = False

    def move(self, dx, dy):
        """
        Change the location of where we are moving in the level we are editing and also moves the "game's view" not to keep everything loaded
        We also keep the camera inbounds not to edit outside of the area causing a crash
        :param dx, dy: The movement of the mouse in pixels
        :return:
        """
        x, y = dx, dy
        if self.worldOrigin[0] + dx < 0:
            x = - self.worldOrigin[0]
        elif self.worldOrigin[0] + self.windowSize[0] + dx >= self.worldSize[0] * self.tileSize[0]:
            x = (self.worldSize[0] * self.tileSize[0]) - \
                (self.worldOrigin[0] + self.windowSize[0])

        if self.worldOrigin[1] - self.windowSize[1] + dy < 0:
            y = self.windowSize[1] - self.worldOrigin[1]
        elif self.worldOrigin[1] + dy >= self.worldSize[1] * self.tileSize[1]:
            y = (self.worldSize[1] * self.tileSize[1]) - self.worldOrigin[1]

        self.world.moveCamera(x, y)
        self.worldOrigin += (x, y)

    def draw(self, screen):
        self.world.draw(screen)
        self.drawGameGrid(screen)

    def drawOverlay(self, screen):
        self.overlay.draw(screen)
        screen.blit(
            pygame.font.SysFont("Consolas", 18, True).render(
                "Mode : {}".format(self.mode), False, (50, 50, 50)),
            [10, 20]
        )

    def drawPauseOverlay(self, screen):
        self.pauseOverlay.draw(screen)

    def drawGameGrid(self, screen):
        # We calculate the number of pixels between the first tile (bottom left corner of the screen) to snap the grid
        # Onto game tiles and makes lines appear like the actual grid of the game
        offset = self.offset
        offset[0] = self.worldOrigin[0] % self.tileSize[0]
        offset[1] = (self.worldOrigin[1] -
                     self.windowSize[1]) % self.tileSize[1]

        for c in range((screen.get_width() // self.tileSize[0]) + 1):
            pygame.draw.line(screen, (70, 70, 70), [self.tileSize[0] * c - offset[0], 0],
                             [self.tileSize[0] * c - offset[0], self.windowSize[1]])

        for l in range((screen.get_height() // self.tileSize[1]) + 2):
            pygame.draw.line(screen, (70, 70, 70), [0, self.windowSize[1] + offset[1] - (self.tileSize[0] * l)],
                             [self.windowSize[0], self.windowSize[1] + offset[1] - (self.tileSize[0] * l)])

    def checkClickPos(self, pos):
        """
        Retrieve which tile is edited with the position of the mouse click on the screen
        :param pos: Position of the click in pixels
        :return: [x, y] the coordinates of the updated tile
        """
        xOffset, yOffset = (self.worldOrigin -
                            (0, self.windowSize[1])) // self.tileSize
        xPos = (pos[0] + self.offset[0]) // self.tileSize[0]
        yPos = (self.windowSize[1] - pos[1] +
                self.offset[1]) // self.tileSize[1]

        return xOffset + xPos, yOffset + yPos

    def readWorld(self, fic):
        self.world.readWorld(fic)

    def place(self, pos):
        """
        Updates the tmpWorld created and reads it to update the world displayed
        :param pos: The coordinates of the tile we click on (x, y)
        :return:
        """
        tilePos = self.checkClickPos(pos)
        world = self.tmpWorld
        if self.mode == PLACE_MODE:
            if self.type == GROUND_TYPE:
                world[tilePos[1]][tilePos[0]] = 'g'

            elif self.type == BLOCK_TYPE:
                world[tilePos[1]][tilePos[0]] = 'b'

            elif self.type == PLAYER_TYPE and tilePos[1] < self.worldSize[1]:
                if self.world.player is not None:
                    for line in range(len(world)):
                        if 'P' in world[line]:
                            world[line][world[line].index('P')] = '.'
                    self.world.player = None

                world[tilePos[1]][tilePos[0]] = 'P'
                world[tilePos[1] + 1][tilePos[0]] = 'P'

        if self.mode == REMOVE_MODE:
            if world[tilePos[1]][tilePos[0]] == 'P':
                if tilePos[1] > 0:
                    if world[tilePos[1] - 1][tilePos[0]] == 'P':
                        world[tilePos[1] - 1][tilePos[0]] = '.'

                if tilePos[1] < self.worldSize[1] - 1:
                    if world[tilePos[1] + 1][tilePos[0]] == 'P':
                        world[tilePos[1] + 1][tilePos[0]] = '.'

            world[tilePos[1]][tilePos[0]] = '.'

        self.renderWorld()
        self.readWorld(self.worldFile)

    def changeType(self, type):
        self.type = type

    def changeMode(self):
        if self.mode == REMOVE_MODE:
            self.mode = PLACE_MODE
        else:
            self.mode = REMOVE_MODE

    def renameWorldFile(self, name):
        os.rename(self.worldFile, name)
        self.worldFile = name

    def generateEmptyWorld(self):
        world = []
        for line in range(self.worldSize[1]):
            tmp = []
            for col in range(self.worldSize[0]):
                tmp += '.'
            world.append(tmp)
        return world

    def renderWorld(self):
        """
        Reads from a world of this shape :
        [". g g g g . . . . . . . . . . . . . . . . ",
         ". g g g g . . . . . . . . . . . . . . . . ",
         ". . . . . . b b b b b . . . . . . . . . . ",
         ...
        ]

        To a format that's easier to generate blocks without having tons of instances :

        type width height x y
        g 4 2 1 0
        b 1 1 6 2
        b 1 1 7 2
        ...

        :return:
        """
        w = self.tmpWorld

        flattenedWorld = []
        flattenedWorldX = []

        for line in w:
            objType = line[0]
            startPos = 0
            count = 0
            tmp = []

            for col in range(1, len(line)):
                if objType == line[col] and objType != 'b':
                    count += 1
                else:
                    if objType != '.':
                        tmp.append(str(startPos) + ';' +
                                   str(startPos + count) + ';' + objType)
                    count = 0
                    startPos = col
                    objType = line[col]

            flattenedWorldX.append(tmp)

        objType = None
        startPos = 0
        count = 0
        tmp = []
        test = True

        while test:
            test = False
            for line in range(len(flattenedWorldX)):
                if 0 < len(flattenedWorldX[line]):
                    if objType is None:
                        objType = flattenedWorldX[line][0]
                        startPos = line
                        test = True

                    if objType in flattenedWorldX[line] and not objType.endswith("b"):
                        count += 1
                        flattenedWorldX[line].remove(objType)
                    else:
                        tmp.append(str(startPos) + ';' +
                                   str(startPos + count - 1) + ';' + objType)
                        count = 1
                        startPos = line
                        objType = flattenedWorldX[line][0]
                        flattenedWorldX[line].remove(objType)

            if objType is not None:
                tmp.append(str(startPos) + ';' +
                           str(startPos + count - 1) + ';' + objType)
                flattenedWorld.append(tmp)
            objType = None
            startPos = 0
            count = 0
            tmp = []

        objs = []

        outFic = open(self.worldFile, 'w')
        for i in flattenedWorld:
            for k in i:
                obj = k.split(";")
                if len(obj[4]) > 1:
                    props = []
                    words = re.split(r'\W+', obj[4][1:])
                    for i in range(0, (len(words) - 2) // 2):
                        key, value = words[2 * i + 1], words[2 * i + 2]
                        props.append((key, value))

                    s = obj[4][0] + " " + str(int(obj[3]) - int(obj[2]) + 1) + " " + str(
                        int(obj[1]) - int(obj[0]) + 1) + " " + obj[2] + " " + str(int(obj[0])) + " " + str(props) + '\n'
                else:
                    s = obj[4] + " " + str(int(obj[3]) - int(obj[2]) + 1) + " " + str(
                        int(obj[1]) - int(obj[0]) + 1) + " " + obj[2] + " " + str(int(obj[0])) + '\n'
                objs.append(s)

        outFic.writelines(objs)
        outFic.close()
