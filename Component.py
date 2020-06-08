import pygame
from pygame.locals import NOEVENT, USEREVENT
import numpy as np

# Event type used by pygame
GAME_EVENT = USEREVENT + 1
MENU_EVENT = USEREVENT + 2
EDITOR_EVENT = USEREVENT + 3


class Component:
    def __init__(self, parent, width=None, height=None, content=None, pos=None):
        self.width = width
        self.height = height
        self.pos = pos
        self.content = content
        self.eventType = NOEVENT
        self.eventId = 0
        self.children = []
        self.parent = parent

    def throwEvent(self):
        pygame.event.post(pygame.event.Event(self.eventType, {'id': self.eventId}))

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

    def changeEventType(self, ev):
        self.eventType = ev

    def changeEventId(self, id):
        self.eventId = id

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
    def __init__(self, parent, width, height, content, eventId, pos, **kwargs):
        super().__init__(parent,
                         width,
                         height,
                         pygame.transform.scale(pygame.image.load(content), (width, height)))

        self.eventId = eventId

        if 'eventType' in kwargs:
            self.eventType = kwargs['eventType']
        else:
            self.eventType = MENU_EVENT

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
    def __init__(self, parent, size=25, color=(255, 255, 255), pos=(0, 0), centered=True, **kwargs):
        super().__init__(parent)

        self.content = pygame.font.SysFont("Consolas", size).render(kwargs['content'], False, color)
        self.width = self.content.get_width()
        self.height = self.content.get_height()
        self.pos = pos

        if centered:
            self.pos = [(self.parent.width - self.width) // 2, (self.parent.height - self.height) // 2]


class Background(Component):
    def __init__(self, parent, width, height, color=(0, 0, 0, 150)):
        super().__init__(parent, width, height, pos=[0, 0])
        if len(color) == 4: self.color = color
        self.content = pygame.Surface((width, height)).convert_alpha()
