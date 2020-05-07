import pygame
import numpy as np


class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.shouldClose = False
        self.showFPS = False
        self.isGridDrawn = False
        self.caseSize = np.array((self.width // 48, self.height // 27))

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)

    def resizeScreen(self, event=None):
        if event == None:
            self.height = int(9 / 16 * self.width)
        else:
            if (self.width > event.dict['w'] and event.dict['w'] < self.height and event.dict['w'] < event.dict[
                'h']) or (
                    self.width < event.dict['w'] and event.dict['w'] > self.height and event.dict['w'] > event.dict[
                'h']):
                if event.dict['w'] > 1000:
                    self.width = 1000
                elif event.dict['w'] < 400:
                    self.width = 400
                else:
                    self.width = event.dict['w']

            elif (self.height > event.dict['h'] and event.dict['h'] < self.height and event.dict['h'] < event.dict[
                'w']) or (self.height < event.dict['h'] and event.dict['h'] > self.height and event.dict['h'] >
                          event.dict['w']):
                if event.dict['h'] > 1000:
                    self.width = 1000
                elif event.dict['h'] < 400:
                    self.width = 400
                else:
                    self.width = event.dict['h']

            else:
                self.width = event.dict['w']

            self.height = int(9 / 16 * self.width)

    def drawGrid(self):
        for l in range(self.height // 20):
            pygame.draw.line(
                self.screen, (0, 0, 0), (0, self.height - l * self.caseSize[1]),
                (self.width, self.height - l * self.caseSize[1]))

        for j in range(self.width // 20):
            pygame.draw.line(self.screen, (0, 0, 0),
                             (j * self.caseSize[0], 0), (j * self.caseSize[0], self.height))
