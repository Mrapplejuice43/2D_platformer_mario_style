# Events ids used inside pygame events not to get limited
from component import EDITOR_EVENT, Background, Button, Component, Image, Text
from constants import BALKANY_PATH, BLOCK_PATH, TEST_BUTTON_PATH, TOP_GROUND_PATH


PLAY_ID = 1
OPTION_ID = 2
BACK_ID = 3
EDITOR_ID = 4
MAIN_MENU_ID = 5
SELECT_GROUND = 6
SELECT_BLOCK = 7
SELECT_PLAYER = 8
RESET_WORLD = 9
QUIT_ID = 10
SAVE_ID = 11
CHANGE_MODE = 12


class Overlay:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.components = []

	def add_component(self, *args):
		for cp in args:
			if isinstance(cp, Component):
				self.components.append(cp)

	def draw(self, screen):
		for cp in self.components:
			cp.draw(screen)

	def check_click_pos(self, pos):
		for cp in self.components:
			if not isinstance(cp, Background) and cp.pos[0] < pos[0] < cp.pos[0] + cp.width and cp.pos[1] < pos[1] < cp.pos[1] + cp.height:
				cp.throwEvent()
				return True

	def resize(self, width, height):
		for cp in self.components:
			cp.resize(self.width, width, self.height, height)
			cp.move(
				cp.pos[0] * width // self.width - cp.pos[0],
				cp.pos[1] * height // self.height - cp.pos[1],
			)

		self.width = width
		self.height = height


class GameOverlay(Overlay):
	def __init__(self, width, height):
		super().__init__(width, height)
		self.add_component()


class Menu(Overlay):
	def __init__(self, width, height):
		super().__init__(width, height)
		self.add_component(
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				PLAY_ID,
				[50, 25],
				posType="percentFromCenter",
			),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				EDITOR_ID,
				[50, 50],
				posType="percentFromCenter",
			),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				QUIT_ID,
				[50, 75],
				posType="percentFromCenter",
			),
			Button(
				self,
				50,
				50,
				TEST_BUTTON_PATH,
				BACK_ID,
				[95, 5],
				posType="percentFromCenter",
			),
		)
		self.components[0].addChild(Text(parent=self.components[0], content="Play", centered=True))
		self.components[1].addChild(Text(parent=self.components[1], content="Editor", centered=True))
		self.components[2].addChild(Text(parent=self.components[2], content="Quit", centered=True))


class PauseMenu(Overlay):
	def __init__(self, width, height):
		super().__init__(width, height)
		self.add_component(
			Background(self, width, height),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				PLAY_ID,
				[50, 25],
				posType="percentFromCenter",
			),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				RESET_WORLD,
				[50, 50],
				posType="percentFromCenter",
			),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				MAIN_MENU_ID,
				[50, 75],
				posType="percentFromCenter",
			),
		)

		self.components[1].addChild(Text(parent=self.components[1], content="Continue", centered=True))
		self.components[2].addChild(Text(parent=self.components[2], content="Restart", centered=True))
		self.components[3].addChild(Text(parent=self.components[3], content="Return to Menu", centered=True))


class EditorMenu(Overlay):
	def __init__(self, width, height):
		super().__init__(width, height)
		self.add_component(
			Button(
				self,
				50,
				50,
				TEST_BUTTON_PATH,
				SELECT_GROUND,
				[10, 90],
				posType="percentFromCenter",
				eventType=EDITOR_EVENT,
			),
			Button(
				self,
				50,
				50,
				TEST_BUTTON_PATH,
				SELECT_BLOCK,
				[20, 90],
				posType="percentFromCenter",
				eventType=EDITOR_EVENT,
			),
			Button(
				self,
				50,
				50,
				TEST_BUTTON_PATH,
				SELECT_PLAYER,
				[30, 90],
				posType="percentFromCenter",
				eventType=EDITOR_EVENT,
			),
			Button(
				self,
				100,
				30,
				TEST_BUTTON_PATH,
				CHANGE_MODE,
				[50, 50],
				eventType=EDITOR_EVENT,
			),
		)

		self.components[0].addChild(Image(self.components[0], 50, 50, [0, 0], TOP_GROUND_PATH))
		self.components[1].addChild(Image(self.components[1], 50, 50, [0, 0], BLOCK_PATH))
		self.components[2].addChild(Image(self.components[2], 50, 50, [0, 0], BALKANY_PATH))
		self.components[3].addChild(Text(parent=self.components[3], content="Switch Mode", centered=True, size=14))


class EditorPauseMenu(Overlay):
	def __init__(self, width, height):
		super().__init__(width, height)
		self.add_component(
			Background(self, width, height),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				PLAY_ID,
				[50, 25],
				posType="percentFromCenter",
			),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				SAVE_ID,
				[50, 50],
				posType="percentFromCenter",
			),
			Button(
				self,
				300,
				100,
				TEST_BUTTON_PATH,
				MAIN_MENU_ID,
				[50, 75],
				posType="percentFromCenter",
			),
		)

		self.components[1].addChild(Text(parent=self.components[1], content="Continue", centered=True))
		self.components[2].addChild(Text(parent=self.components[2], content="Save World", centered=True))
		self.components[3].addChild(Text(parent=self.components[3], content="Return to Menu", centered=True))
