from overlay import EditorPauseMenu, EditorMenu
import os
import re
import numpy as np
import pygame

from world import World

# Editing modes
PLACE_MODE = 0
REMOVE_MODE = 1

# Object types of the game
GROUND_TYPE = 0
BLOCK_TYPE = 1
PLAYER_TYPE = 2


class Editor:
	def __init__(self, window_size, tile_size, game_scale):
		self.world = World(window_size, tile_size, game_scale)
		self.world_size = [200, 50]

		self.tmp_world = self.generate_empty_world()

		num = 1
		while os.path.exists(r"worlds/newWorld{}.w".format(num)):
			num += 1
		self.world_file = r"worlds/newWorld{}.w".format(num)

		self.window_size = window_size
		self.tile_size = tile_size
		self.game_scale = game_scale
		self.pause = False
		self.overlay = EditorMenu(window_size[0], window_size[1])
		self.pause_overlay = EditorPauseMenu(window_size[0], window_size[1])
		self.show_overlay = True
		self.pause = False

		self.world_origin = np.array((0, self.window_size[1]))
		self.offset = [0, 0]
		self.mode = PLACE_MODE
		self.type = GROUND_TYPE

		self.debug_mode = False

	def move(self, dx, dy):
		"""
		Change the location of where we are moving in the level we are editing and also moves the "game's view" not to keep everything loaded
		We also keep the camera inbounds not to edit outside of the area causing a crash
		:param dx, dy: The movement of the mouse in pixels
		:return:
		"""
		x, y = dx, dy
		if self.world_origin[0] + dx < 0:
			x = -self.world_origin[0]
		elif self.world_origin[0] + self.window_size[0] + dx >= self.world_size[0] * self.tile_size[0]:
			x = (self.world_size[0] * self.tile_size[0]) - (self.world_origin[0] + self.window_size[0])

		if self.world_origin[1] - self.window_size[1] + dy < 0:
			y = self.window_size[1] - self.world_origin[1]
		elif self.world_origin[1] + dy >= self.world_size[1] * self.tile_size[1]:
			y = (self.world_size[1] * self.tile_size[1]) - self.world_origin[1]

		self.world.move_camera(x, y)
		self.world_origin += (x, y)

	def draw(self, screen):
		self.world.draw(screen)
		self.draw_game_grid(screen)

	def draw_overlay(self, screen):
		self.overlay.draw(screen)
		screen.blit(
			pygame.font.SysFont("Consolas", 18, True).render("Mode : {}".format(self.mode), False, (50, 50, 50)),
			[10, 20],
		)

	def draw_pause_overlay(self, screen):
		self.pause_overlay.draw(screen)

	def draw_game_grid(self, screen):
		# We calculate the number of pixels between the first tile (bottom left corner of the screen) to snap the grid
		# Onto game tiles and makes lines appear like the actual grid of the game
		offset = self.offset
		offset[0] = self.world_origin[0] % self.tile_size[0]
		offset[1] = (self.world_origin[1] - self.window_size[1]) % self.tile_size[1]

		for c in range((screen.get_width() // self.tile_size[0]) + 1):
			pygame.draw.line(
				screen,
				(70, 70, 70),
				[self.tile_size[0] * c - offset[0], 0],
				[self.tile_size[0] * c - offset[0], self.window_size[1]],
			)

		for line in range((screen.get_height() // self.tile_size[1]) + 2):
			pygame.draw.line(
				screen,
				(70, 70, 70),
				[0, self.window_size[1] + offset[1] - (self.tile_size[0] * line)],
				[
					self.window_size[0],
					self.window_size[1] + offset[1] - (self.tile_size[0] * line),
				],
			)

	def check_click_pos(self, pos):
		"""
		Retrieve which tile is edited with the position of the mouse click on the screen
		:param pos: Position of the click in pixels
		:return: [x, y] the coordinates of the updated tile
		"""
		x_offset, y_offset = (self.world_origin - (0, self.window_size[1])) // self.tile_size
		x_pos = (pos[0] + self.offset[0]) // self.tile_size[0]
		y_pos = (self.window_size[1] - pos[1] + self.offset[1]) // self.tile_size[1]

		return x_offset + x_pos, y_offset + y_pos

	def read_world(self, fic):
		self.world.read_world(fic)

	def place(self, pos):
		"""
		Updates the tmpWorld created and reads it to update the world displayed
		:param pos: The coordinates of the tile we click on (x, y)
		:return:
		"""
		tile_pos = self.check_click_pos(pos)
		world = self.tmp_world
		if self.mode == PLACE_MODE:
			if self.type == GROUND_TYPE:
				world[tile_pos[1]][tile_pos[0]] = "g"

			elif self.type == BLOCK_TYPE:
				world[tile_pos[1]][tile_pos[0]] = "b"

			elif self.type == PLAYER_TYPE and tile_pos[1] < self.world_size[1]:
				if self.world.player is not None:
					for line in range(len(world)):
						if "P" in world[line]:
							world[line][world[line].index("P")] = "."
					self.world.player = None

				world[tile_pos[1]][tile_pos[0]] = "P"
				world[tile_pos[1] + 1][tile_pos[0]] = "P"

		if self.mode == REMOVE_MODE:
			if world[tile_pos[1]][tile_pos[0]] == "P":
				if tile_pos[1] > 0:
					if world[tile_pos[1] - 1][tile_pos[0]] == "P":
						world[tile_pos[1] - 1][tile_pos[0]] = "."

				if tile_pos[1] < self.world_size[1] - 1:
					if world[tile_pos[1] + 1][tile_pos[0]] == "P":
						world[tile_pos[1] + 1][tile_pos[0]] = "."

			world[tile_pos[1]][tile_pos[0]] = "."

		self.render_world()
		self.read_world(self.world_file)

	def change_type(self, type):
		self.type = type

	def change_mode(self):
		if self.mode == REMOVE_MODE:
			self.mode = PLACE_MODE
		else:
			self.mode = REMOVE_MODE

	def rename_world_file(self, name):
		os.rename(self.world_file, name)
		self.world_file = name

	def generate_empty_world(self):
		world = []
		for line in range(self.world_size[1]):
			tmp = []
			for col in range(self.world_size[0]):
				tmp += "."
			world.append(tmp)
		return world

	def render_world(self):
		"""
		Reads from a world of this shape :
		[". g g g g . . . . . . . . . . . . . . . . ",
		 ". g g g g . . . . . . . . . . . . . . . . ",
		 ". . . . . . b b b b b . . . . . . . . . . ",
		 ...
		]

		To a format that's easier to generate blocks without having tons of instances :

		type width height x y
		g 4 2 1 0
		b 1 1 6 2
		b 1 1 7 2
		...

		:return:
		"""
		w = self.tmp_world

		flattened_world = []
		flattened_world_x = []

		for line in w:
			obj_type = line[0]
			start_pos = 0
			count = 0
			tmp = []

			for col in range(1, len(line)):
				if obj_type == line[col] and obj_type != "b":
					count += 1
				else:
					if obj_type != ".":
						tmp.append(str(start_pos) + ";" + str(start_pos + count) + ";" + obj_type)
					count = 0
					start_pos = col
					obj_type = line[col]

			flattened_world_x.append(tmp)

		obj_type = None
		start_pos = 0
		count = 0
		tmp = []
		test = True

		while test:
			test = False
			for line in range(len(flattened_world_x)):
				if 0 < len(flattened_world_x[line]):
					if obj_type is None:
						obj_type = flattened_world_x[line][0]
						start_pos = line
						test = True

					if obj_type in flattened_world_x[line] and not obj_type.endswith("b"):
						count += 1
						flattened_world_x[line].remove(obj_type)
					else:
						tmp.append(str(start_pos) + ";" + str(start_pos + count - 1) + ";" + obj_type)
						count = 1
						start_pos = line
						obj_type = flattened_world_x[line][0]
						flattened_world_x[line].remove(obj_type)

			if obj_type is not None:
				tmp.append(str(start_pos) + ";" + str(start_pos + count - 1) + ";" + obj_type)
				flattened_world.append(tmp)
			obj_type = None
			start_pos = 0
			count = 0
			tmp = []

		objs = []

		with open(self.world_file, "w") as out_fic:
			for i in flattened_world:
				for k in i:
					obj = k.split(";")
					if len(obj[4]) > 1:
						props = []
						words = re.split(r"\W+", obj[4][1:])
						for i in range(0, (len(words) - 2) // 2):
							key, value = words[2 * i + 1], words[2 * i + 2]
							props.append((key, value))

						s = (
							obj[4][0]
							+ " "
							+ str(int(obj[3]) - int(obj[2]) + 1)
							+ " "
							+ str(int(obj[1]) - int(obj[0]) + 1)
							+ " "
							+ obj[2]
							+ " "
							+ str(int(obj[0]))
							+ " "
							+ str(props)
							+ "\n"
						)
					else:
						s = (
							obj[4]
							+ " "
							+ str(int(obj[3]) - int(obj[2]) + 1)
							+ " "
							+ str(int(obj[1]) - int(obj[0]) + 1)
							+ " "
							+ obj[2]
							+ " "
							+ str(int(obj[0]))
							+ "\n"
						)
					objs.append(s)

			out_fic.writelines(objs)
