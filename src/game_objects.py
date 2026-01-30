from constants import (
	BLOCK_PATH,
	BOTH_SIDE_TOP_GROUND_PATH,
	BROKEN_BLOCK_PATH,
	LOW_GROUND_PATH,
	SIDE_TOP_GROUND_LEFT_PATH,
	SIDE_TOP_GROUND_RIGHT_PATH,
	TOP_GROUND_PATH,
)
import numpy as np
import pygame


class GameObject:
	def __init__(self, *args):
		"""args[0] -> width of the object (integer counted in squares) \n
		args[1] -> height of the object (integer in squares) \n
		args[2] -> pos of the object (tuple of int in squares)"""
		self.width = args[0]
		self.height = args[1]
		self.pos = np.array(args[2])
		self.color = np.array((0, 0, 0))
		self.on_screen = True
		self.debug_mode = False

	def to_string(self):
		return "width : {0}, height : {1}, pos : {2}".format(self.width, self.height, self.pos)

	def draw(self, screen, coords, width, height):
		if self.on_screen:
			pygame.draw.rect(screen, self.color, pygame.Rect(coords, (int(width), int(height))))


class Plateforme(GameObject):
	def __init__(self, *args, **kwargs):
		"""args[0] -> width of the object (integer counted in squares) \n
		args[1] -> height of the object (integer in squares) \n
		args[2] -> pos of the object (tuple of int in squares)"""
		super().__init__(args[0], args[1], args[2])
		self.color = (200, 30, 30)


class Ground(GameObject):
	def __init__(self, *args, **kwargs):
		"""args[0] -> width of the object (integer counted in squares) \n
		args[1] -> height of the object (integer in squares) \n
		args[2] -> pos of the object (tuple of int in squares)"""
		super().__init__(args[0], args[1], args[2])
		self.color = (30, 200, 30)
		self.sprites = [
			pygame.image.load(TOP_GROUND_PATH),
			pygame.image.load(LOW_GROUND_PATH),
			pygame.image.load(SIDE_TOP_GROUND_LEFT_PATH),
			pygame.image.load(SIDE_TOP_GROUND_RIGHT_PATH),
			pygame.image.load(BOTH_SIDE_TOP_GROUND_PATH),
		]

		surfarrays = [
			np.array(pygame.surfarray.pixels3d(self.sprites[0])).transpose((1, 0, 2)),
			np.array(pygame.surfarray.pixels3d(self.sprites[1])).transpose((1, 0, 2)),
			np.array(pygame.surfarray.pixels3d(self.sprites[2])).transpose((1, 0, 2)),
			np.array(pygame.surfarray.pixels3d(self.sprites[3])).transpose((1, 0, 2)),
			np.array(pygame.surfarray.pixels3d(self.sprites[4])).transpose((1, 0, 2)),
		]

		if self.width > 1:
			im_array = surfarrays[2]
			for i in range(self.width - 1):
				if i != self.width - 2:
					im_array = np.concatenate((im_array, surfarrays[0]), axis=1)
				else:
					im_array = np.concatenate((im_array, surfarrays[3]), axis=1)

			for j in range(self.height):
				tmp = surfarrays[1]
				for i in range(self.width - 1):
					tmp = np.concatenate((tmp, surfarrays[1]), axis=1)

				im_array = np.concatenate((im_array, tmp))

			self.sprite = pygame.image.fromstring(im_array.tobytes(), ((self.width) * 27, (self.height + 1) * 27), "RGB")
			self.sprite.set_colorkey((255, 255, 255))

		elif self.width == 1:
			im_array = surfarrays[4]
			for j in range(self.height):
				im_array = np.concatenate((im_array, surfarrays[1]))

			self.sprite = pygame.image.fromstring(im_array.tobytes(), ((self.width) * 27, (self.height + 1) * 27), "RGB")
			self.sprite.set_colorkey((255, 255, 255))

		else:
			im_array = surfarrays[2]
			for j in range(self.height):
				np.concatenate((im_array, surfarrays[1]), axis=1)

			self.sprite = pygame.image.fromstring(
				im_array.tobytes(),
				((self.width + 1) * 27, (self.height + 1) * 27),
				"RGB",
			).convert()
			self.sprite.set_colorkey((255, 255, 255))

	def draw(self, screen, coords, width, height):
		if self.on_screen:
			screen.blit(pygame.transform.scale(self.sprite, (int(width), int(height))), coords)
			if self.debug_mode:
				pygame.draw.ellipse(screen, (0, 0, 0), pygame.Rect([coords - (3, 3), (6, 6)]), 0)


class Box(GameObject):
	def __init__(self, *args):
		super().__init__(args[0], args[1], args[2])
		self.color = (255, 60, 0)
		self.sprite = pygame.image.load(BLOCK_PATH)
		self.isBroken = False

	def draw(self, screen, coords, width, height):
		if self.on_screen:
			screen.blit(pygame.transform.scale(self.sprite, (int(width), int(height))), coords)
			if self.debug_mode:
				pygame.draw.ellipse(screen, (0, 0, 0), pygame.Rect([coords - (3, 3), (6, 6)]), 0)

	def activate(self):
		if not self.isBroken:
			self.isBroken = True
			self.sprite = pygame.image.load(BROKEN_BLOCK_PATH)
