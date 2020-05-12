import pygame
from pygame.locals import NOEVENT
import numpy as np


class Component:
    def __init__(self, parent, width=None, height=None, content=None, pos=None):
        self.width = width
        self.height = height
        self.pos = pos
        self.content = content
        self.eventType = NOEVENT
        self.children = []
        self.parent = parent

    def throwEvent(self):
        pygame.event.post(pygame.event.Event(self.eventType, {}))

    def resize(self, oldWidth, width, oldHeight, height):
        self.width = width * self.width // oldWidth
        self.height = height * self.height // oldHeight
        if isinstance(self, Background):
            self.content = pygame.Surface((width, height)).convert_alpha()

    def move(self, dx, dy):
        self.pos[0] += dx
        self.pos[1] += dy
        for child in self.children:
            child.move(dx, dy)

    def changeEvent(self, ev):
        self.eventType = ev

    def draw(self, screen):
        screen.blit(self.content, self.pos)

        if isinstance(self, Background):
            self.content.fill(self.color)

        for child in self.children:
            child.draw(screen)

    def addChild(self, component):
        if isinstance(component, Component):
            component.pos = [self.pos[0] + component.pos[0], self.pos[1] + component.pos[1]]
            self.children.append(component)


class Button(Component):
    def __init__(self, parent, width, height, content, eventType, pos, **kwargs):
        super().__init__(parent,
                         width,
                         height,
                         pygame.transform.scale(pygame.image.load(content), (width, height)))

        self.eventType = eventType

        if ('posType' in kwargs):
            if (kwargs['posType'] == 'percentFromCenter'):
                self.pos = np.array((parent.width, parent.height)) * pos // 100 - np.array(
                    (self.width, self.height)) // 2
            elif kwargs['posType'] == 'percent':
                self.pos = np.array((parent.width, parent.height)) * pos // 100
        else:
            self.pos = pos


class Image(Component):
    def __init__(self, parent, width, height, pos, content):
        super().__init__(parent, width, height, pygame.transform.scale(pygame.image.load(content), (width, height)),
                         pos)


class Text(Component):
    def __init__(self, **kwargs):
        super().__init__(kwargs['parent'])

        self.content = pygame.font.SysFont("Consolas", 25).render(kwargs['content'], False, (255, 255, 255))
        self.width = self.content.get_width()
        self.height = self.content.get_height()

        if 'pos' in kwargs.keys():
            self.pos = kwargs['pos']
        else:
            self.pos = [0, 0]

        if 'centered' in kwargs.keys():
            if kwargs['centered']:
                self.pos = [(self.parent.width - self.width) // 2, (self.parent.height - self.height) // 2]



class Background(Component):
    def __init__(self, parent, width, height, color=(0, 0, 0, 150)):
        super().__init__(parent, width, height, pos=[0, 0])
        if len(color) == 4 : self.color = color
        self.content = pygame.Surface((width, height)).convert_alpha()
