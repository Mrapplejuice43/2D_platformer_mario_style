import numpy as np
import pygame

CAMERA_TRIGGER = pygame.USEREVENT

class Camera:
    def __init__(self, size, caseSize):
        self.size = np.array(size)
        self.width = size[0]
        self.height = size[1]
        self.xmin = 8 * caseSize[0]
        self.xmax = self.xmin + 20 * caseSize[0]
        self.ymin = 4 * caseSize[1]
        self.ymax = self.ymin + 20 * caseSize[1]
        self.pos = np.array(((self.xmax - self.xmin) // 2 + self.xmin, (self.ymax - self.ymin) // 2 + self.ymin))
        self.triggerBounds = ((self.xmin, self.ymin), (self.xmax - self.xmin, self.ymax - self.ymin))

        self.initialValues = (self.xmin, self.xmax, self.ymin, self.ymax, tuple(self.pos), self.triggerBounds)

    def setPos(self, pos):
        self.pos = np.array(pos)

    def draw(self, screen, coords):
        pygame.draw.ellipse(screen, (0, 0, 0), pygame.Rect(coords[0] - 3, (6, 6)), 0)
        pygame.draw.rect(screen, (200, 50, 50), pygame.Rect(coords[1]), 2)

    def reset(self):
        self.xmin, self.xmax, self.ymin, self.ymax, self.pos, self.triggerBounds = self.initialValues

    def checkPlayerPos(self, player, caseSize):
        dx, dy = 0, 0
        trigger = None
        if self.initialValues[0] < player.pos[0] < self.xmin:
            dx += player.pos[0] - self.xmin
            trigger = pygame.USEREVENT
        elif player.pos[0] + player.width * caseSize[0] > self.xmax:
            trigger = pygame.USEREVENT
            dx += player.pos[0] + player.width * caseSize[0] - self.xmax

        if self.initialValues[2] < player.pos[1] < self.ymin:
            dy += player.pos[1] - self.ymin
            trigger = pygame.USEREVENT
        elif player.pos[1] + player.height * caseSize[1] > self.ymax:
            dy += (player.pos[1] + player.height * caseSize[1]) - self.ymax
            trigger = pygame.USEREVENT

        if trigger:
            pygame.event.post(pygame.event.Event(trigger, {'dx' : dx, 'dy' : dy}))
            self.move(dx, dy)

    def move(self, dx, dy):
        self.xmin += dx
        self.xmax += dx
        self.ymin += dy
        self.ymax += dy
        self.pos = np.array(((self.xmax - self.xmin) // 2 + self.xmin, (self.ymax - self.ymin) // 2 + self.ymin))
