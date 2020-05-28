from Component import *

# Events ids used inside pygame events not to get limited
PLAY_EVENT = 1
OPTION_EVENT = 2
BACK_EVENT = 3
EDITOR_EVENT = 4
MAIN_MENU_EVENT = 5
SELECT_GROUND = 6
SELECT_BLOCK = 7
SELECT_PLAYER = 8
RESET_WORLD = 9
QUIT_EVENT = 10


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
            if not isinstance(cp, Background) and cp.pos[0] < pos[0] < cp.pos[0] + cp.width and cp.pos[1] < pos[1] < \
                    cp.pos[1] + cp.height:
                cp.throwEvent()

    def resize(self, width, height):
        for cp in self.components:
            cp.resize(self.width, width, self.height, height)
            cp.move(cp.pos[0] * width // self.width - cp.pos[0],
                    cp.pos[1] * height // self.height - cp.pos[1])

        self.width = width
        self.height = height

# TODO Create a game overlay to get various infos like health
class GameOverlay(Overlay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.addComponent(

        )


class Menu(Overlay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.addComponent(
            Button(self, 300, 100, r"assets\\testButton.png", PLAY_EVENT, [50, 25], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", EDITOR_EVENT, [50, 50], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", QUIT_EVENT, [50, 75], posType='percentFromCenter'),
            Button(self, 50, 50, r"assets\\testButton.png", BACK_EVENT, [95, 5], posType='percentFromCenter')
        )
        self.components[0].addChild(Text(parent=self.components[0], content="Play", centered=True))
        self.components[1].addChild(Text(parent=self.components[1], content="Editor", centered=True))
        self.components[2].addChild(Text(parent=self.components[2], content="Quit", centered=True))


class PauseMenu(Overlay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.addComponent(
            Background(self, width, height),
            Button(self, 300, 100, r"assets\\testButton.png", PLAY_EVENT, [50, 25], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", RESET_WORLD, [50, 50], posType='percentFromCenter'),
            Button(self, 300, 100, r"assets\\testButton.png", MAIN_MENU_EVENT, [50, 75], posType='percentFromCenter')

        )

        self.components[1].addChild(Text(parent=self.components[1], content="Continue", centered=True))
        self.components[2].addChild(Text(parent=self.components[2], content="Restart", centered=True))
        self.components[3].addChild(Text(parent=self.components[3], content="Return to Menu", centered=True))


class EditorMenu(Overlay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.addComponent(
            Button(self, 50, 50, r"assets\testButton.png", SELECT_GROUND, [10, 90], posType='percentFromCenter'),
            Button(self, 50, 50, r"assets\testButton.png", SELECT_BLOCK, [20, 90], posType='percentFromCenter'),
            Button(self, 50, 50, r"assets\testButton.png", SELECT_PLAYER, [30, 90], posType='percentFromCenter')
        )

        self.components[0].addChild(Image(self.components[0], 50, 50, [0, 0], r"assets\topGround.png"))
        self.components[1].addChild(Image(self.components[1], 50, 50, [0, 0], r"assets\block.png"))
        self.components[2].addChild(Image(self.components[2], 50, 50, [0, 0], r"assets\balkany.png"))
