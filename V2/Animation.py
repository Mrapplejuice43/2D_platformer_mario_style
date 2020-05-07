import pygame
import numpy as np


class spriteAnimation:
    def __init__(self, sprite, size, nbFrames=20):
        self.image = pygame.image.load(sprite)
        self.image.set_colorkey((255, 255, 255))
        self.nbFrames = nbFrames
        self.sprite = []
        self.size = size
        self.sprite = [(self.image.subsurface(pygame.Rect(
            self.size[0] * i, 0, self.size[0], self.size[1]))) for i in range(self.nbFrames)]

        self.currentFrame = 0

    def getFrame(self):
        k = self.currentFrame
        if self.currentFrame < self.nbFrames - 1:
            self.currentFrame += 1
        else:
            self.currentFrame = 0
        return self.sprite[k]
