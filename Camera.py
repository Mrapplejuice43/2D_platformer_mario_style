import numpy as np
import pygame

CAMERA_TRIGGER = pygame.USEREVENT

class Camera:
    def __init__(self, size, tileSize, gameScale):
        self.size = np.array(size)
        self.tileSize = tileSize
        self.scale = gameScale
        self.width = size[0]
        self.height = size[1]
        self.xmin = int((8 * self.tileSize[0]) / self.scale)
        self.xmax = int((self.xmin + 20 * self.tileSize[0]) / self.scale)
        self.ymin = int((4 * self.tileSize[1]) / self.scale)
        self.ymax = int((self.ymin + 20 * self.tileSize[1]) / self.scale)
        self.pos = np.array(((self.xmax - self.xmin) // 2 + self.xmin, (self.ymin - self.ymax) // 2 - self.ymin))
        self.triggerBounds = np.array(((self.xmin, self.ymin), (self.xmax - self.xmin, self.ymax - self.ymin)))

        self.initialValues = (8, 28, 4, 24, tuple(self.pos), self.triggerBounds)

    def setPos(self, pos):
        self.pos = np.array(pos)

    def draw(self, screen, coords):
        pygame.draw.ellipse(screen, (0, 0, 0), pygame.Rect(coords[0] - 3, (6, 6)), 0)
        pygame.draw.rect(screen, (200, 50, 50), pygame.Rect(coords[1]), 2)

    def reset(self):
        self.xmin = int(self.initialValues[0] * self.tileSize[0] / self.scale)
        self.xmax = int(self.initialValues[1] * self.tileSize[0] / self.scale)
        self.ymin = int(self.initialValues[2] * self.tileSize[1] / self.scale)
        self.ymax = int(self.initialValues[3] * self.tileSize[1] / self.scale)
        self.pos = self.initialValues[4]
        self.triggerBounds = self.initialValues[5]

    def resize(self, size, caseSize):

        self.width = size[0]
        self.height = size[1]
        self.xmin = self.xmin * caseSize[0] // self.tileSize[0]
        self.xmax = self.xmax * caseSize[0] // self.tileSize[0]
        self.ymin = self.ymin * caseSize[1] // self.tileSize[1]
        self.ymax = self.ymax * caseSize[1] // self.tileSize[1]
        self.pos = np.array(((self.xmax - self.xmin) // 2 + self.xmin, (self.ymax - self.ymin) // 2 + self.ymin))
        self.triggerBounds = np.array(((self.xmin, self.ymin), (self.xmax - self.xmin, self.ymax - self.ymin)))

        e = np.array(self.initialValues[4]) * size // self.size * np.array((1, -1))
        f = ((self.initialValues[0] * caseSize[0], self.initialValues[2] * caseSize[1]),
             (self.initialValues[1] * caseSize[0] - self.initialValues[0] * caseSize[0], self.initialValues[3] * caseSize[1] - self.initialValues[2] * caseSize[1]))
        self.initialValues = (8, 28, 4, 24, e, f)
        self.size = np.array(size)
        self.tileSize = caseSize

    def checkPlayerPos(self, player):
        dx, dy = 0, 0
        trigger = False
        tileSize = self.tileSize
        tmpSpeed = np.int32(np.round(player.speed))
        if (self.initialValues[0] * tileSize[0]) < player.pos[0] + tmpSpeed[0] < self.xmin:
            dx += player.pos[0] + tmpSpeed[0] - self.xmin
            trigger = pygame.USEREVENT
        elif player.pos[0] + tmpSpeed[0] + (player.width * tileSize[0]) > self.xmax:
            trigger = pygame.USEREVENT
            dx += player.pos[0] + tmpSpeed[0] + (player.width * tileSize[0]) - self.xmax

        if (self.initialValues[2] * tileSize[1]) < player.pos[1] + tmpSpeed[1] < self.ymin:
            dy += player.pos[1] + tmpSpeed[1] - self.ymin
            trigger = pygame.USEREVENT
        elif player.pos[1] + tmpSpeed[1] + (player.height * tileSize[1]) > self.ymax:
            dy += (player.pos[1] + tmpSpeed[1] + player.height * tileSize[1]) - self.ymax
            trigger = pygame.USEREVENT

        if trigger:
            pygame.event.post(pygame.event.Event(trigger, {'dx': int(dx), 'dy': int(dy)}))

    def move(self, dx, dy):
        self.xmin += dx
        self.xmax += dx
        self.ymin += dy
        self.ymax += dy
        self.pos += (dx, dy)
