import pygame
from pygame.locals import NOEVENT, USEREVENT, USEREVENT_DROPFILE


class Component:
    def __init__(self, width, height, pos, image):
        self.width = width
        self.height = height
        self.pos = pos
        self.image = image
        self.eventType = NOEVENT

    def throwEvent(self):
        pygame.event.post(self.eventType)

    def resize(self, width, height):
        self.width = width
        self.height = height

    def changeEvent(self, ev):
        self.eventType = ev

    def draw(self, screen):
        screen.blit(pygame.image.load(self.image), self.pos)


class Button(Component):
    def __init__(self, width, height, pos, image, eventType):
        super().__init__(width, height, pos, image)
        self.eventType = eventType


class Overlay(Component):
    def __init__(self, width, height, pos, image, eventType):
        super().__init__(width, height, pos, image)
        self.eventType = eventType