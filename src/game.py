from camera import Camera
import numpy as np
from overlay import PauseMenu
from world import World


class Game:
	def __init__(self, window_size, tile_size, game_scale, level=None):
		self.world = World(window_size, tile_size, game_scale, level)
		self.window_size = window_size
		self.tile_size = tile_size
		self.scale = game_scale
		self.pause = False
		self.pause_sverlay = PauseMenu(window_size[0], window_size[1])

		self.world_origin = np.array((0, self.window_size[1]))

		self.debug_mode = False

	def update(self, keys, dt, sizeRatio):
		"""
		Updates player's states and gameObjects' states
		"""
		self.world.update(keys, dt, sizeRatio)

	def move_camera(self, dx, dy):
		self.world.move_camera(dx, dy)

	def switch_debug_mode(self):
		self.debug_mode = not self.debug_mode
		self.world.switch_debug_mode()

	def read_world(self, fic):
		"""
		Reads a formatted file which determine what is in the world
		:param fic: Path of the file to read
		"""
		self.world.read_world(fic)

	def change_level(self, level):
		self.world.change_level(level)

	def reset(self):
		self.world.reset_world()

	def calculate_drawing_coordinates(self, obj):
		if isinstance(obj, Camera):
			return (
				(obj.initialValues[4] - self.world_origin) * np.array((1, -1)),
				(
					(
						obj.initialValues[0] * self.tile_size[0],
						self.world_origin[1] - obj.initialValues[2] * self.tile_size[1],
					),
					((obj.xmax - obj.xmin), obj.ymin - obj.ymax),
				),
			)

	def resize(self, window_size, tile_size):
		self.world.resize(window_size, tile_size)
		self.window_size = window_size
		self.tile_size = tile_size
		self.pause_sverlay.resize(window_size[0], window_size[1])

	def draw(self, screen):
		"""
		Drawing function of the game
		"""
		self.world.draw(screen)
