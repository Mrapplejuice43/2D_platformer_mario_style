from pygame.locals import *
from Component import *

GAME_EVENT = USEREVENT + 1
OPTION_EVENT = USEREVENT + 2
BACK_EVENT = USEREVENT + 3
EDITOR_EVENT = USEREVENT + 4
MAIN_MENU_EVENT = USEREVENT + 5

class Overlay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.components = []

    def addComponent(self, *args):
        for cp in args:
            if isinstance(cp, Component):
                self.components.append(cp)

    def draw(self, screen):
        for cp in self.components:
            cp.draw(screen)

    def checkClickPos(self, pos):
        for cp in self.components:
            if cp.pos[0] < pos[0] < cp.pos[0] + cp.width and cp.pos[1] < pos[1] < cp.pos[1] + cp.height:
                cp.throwEvent()

    def resize(self, width, height):
        for cp in self.components:
            cp.resize(self.width, width, self.height, height)
            cp.move(cp.pos[0] * width // self.width - cp.pos[0],
                    cp.pos[1] * height // self.height - cp.pos[1])

        self.width = width
        self.height = height


class Menu(Overlay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.addComponent(
            Button(self, 300, 100, r"assets\\testButton.png", GAME_EVENT, [50, 25], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", EDITOR_EVENT, [50, 50], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", QUIT, [50, 75], posType='percentFromCenter'),
            Button(self, 50, 50, r"assets\\testButton.png", BACK_EVENT, [95, 5], posType='percentFromCenter')
        )
        self.components[0].addChild(Text(parent=self.components[0], content="Play"))
        self.components[1].addChild(Text(parent=self.components[1], content="Editor"))
        self.components[2].addChild(Text(parent=self.components[2], content="Quit"))


class PauseMenu(Overlay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.addComponent(
            Background(self, width, height),
            Button(self, 300, 100, r"assets\\testButton.png", GAME_EVENT, [50, 25], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", GAME_EVENT, [50, 50], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", MAIN_MENU_EVENT, [50, 75], posType='percentFromCenter')

        )

        self.components[1].addChild(Text(parent=self.components[1], content="1"))
        self.components[2].addChild(Text(parent=self.components[2], content="2"))
        self.components[3].addChild(Text(parent=self.components[3], content="Return to Menu"))