import numpy as np
import pygame

CAMERA_TRIGGER = pygame.USEREVENT


class Camera:
	def __init__(self, size, tile_size, game_scale):
		self.size = np.array(size)
		self.tile_size = tile_size
		self.scale = game_scale
		self.width = size[0]
		self.height = size[1]
		self.xmin = int((8 * self.tile_size[0]) / self.scale)
		self.xmax = int((self.xmin + 20 * self.tile_size[0]) / self.scale)
		self.ymin = int((4 * self.tile_size[1]) / self.scale)
		self.ymax = int((self.ymin + 20 * self.tile_size[1]) / self.scale)
		self.pos = np.array(
			(
				(self.xmax - self.xmin) // 2 + self.xmin,
				(self.ymin - self.ymax) // 2 - self.ymin,
			)
		)
		self.triggerBounds = (
			(self.xmin, self.ymin),
			(self.xmax - self.xmin, self.ymax - self.ymin),
		)

		self.initialValues = (8, 28, 4, 24, tuple(self.pos), self.triggerBounds)

	def set_pos(self, pos):
		self.pos = np.array(pos)

	def draw(self, screen):
		pygame.draw.ellipse(
			screen,
			(0, 0, 0),
			pygame.Rect(np.array(self.triggerBounds[0]) - 3, (6, 6)),
			0,
		)
		pygame.draw.rect(screen, (200, 50, 50), pygame.Rect(self.triggerBounds), 2)

	def reset(self):
		self.xmin = int(self.initialValues[0] * self.tile_size[0] / self.scale)
		self.xmax = int(self.initialValues[1] * self.tile_size[0] / self.scale)
		self.ymin = int(self.initialValues[2] * self.tile_size[1] / self.scale)
		self.ymax = int(self.initialValues[3] * self.tile_size[1] / self.scale)
		self.pos = self.initialValues[4]
		self.triggerBounds = self.initialValues[5]

	def resize(self, size, case_size):
		self.width = size[0]
		self.height = size[1]
		self.xmin = self.xmin * case_size[0] // self.tile_size[0]
		self.xmax = self.xmax * case_size[0] // self.tile_size[0]
		self.ymin = self.ymin * case_size[1] // self.tile_size[1]
		self.ymax = self.ymax * case_size[1] // self.tile_size[1]
		self.pos = np.array(
			(
				(self.xmax - self.xmin) // 2 + self.xmin,
				(self.ymax - self.ymin) // 2 + self.ymin,
			)
		)
		self.triggerBounds = (
			(self.xmin, self.ymin),
			(self.xmax - self.xmin, self.ymax - self.ymin),
		)

		e = np.array(self.initialValues[4]) * size // self.size * np.array((1, -1))
		f = (
			(self.initialValues[0] * case_size[0], self.initialValues[2] * case_size[1]),
			(
				self.initialValues[1] * case_size[0] - self.initialValues[0] * case_size[0],
				self.initialValues[3] * case_size[1] - self.initialValues[2] * case_size[1],
			),
		)
		self.initialValues = (8, 28, 4, 24, e, f)
		self.size = np.array(size)
		self.tile_size = case_size

	def check_player_pos(self, player):
		dx, dy = 0, 0
		trigger = False
		tile_size = self.tile_size
		tmp_speed = np.int32(np.round(player.speed))
		if (self.initialValues[0] * tile_size[0]) < player.pos[0] + tmp_speed[0] < self.xmin:
			dx += player.pos[0] + tmp_speed[0] - self.xmin
			trigger = pygame.USEREVENT
		elif player.pos[0] + tmp_speed[0] + (player.width * tile_size[0]) > self.xmax:
			trigger = pygame.USEREVENT
			dx += player.pos[0] + tmp_speed[0] + (player.width * tile_size[0]) - self.xmax

		if (self.initialValues[2] * tile_size[1]) < player.pos[1] + tmp_speed[1] < self.ymin:
			dy += player.pos[1] + tmp_speed[1] - self.ymin
			trigger = pygame.USEREVENT
		elif player.pos[1] + tmp_speed[1] + (player.height * tile_size[1]) > self.ymax:
			dy += (player.pos[1] + tmp_speed[1] + player.height * tile_size[1]) - self.ymax
			trigger = pygame.USEREVENT

		if trigger:
			pygame.event.post(pygame.event.Event(trigger, {"dx": int(dx), "dy": int(dy)}))

	def move(self, dx, dy):
		self.xmin += dx
		self.xmax += dx
		self.ymin += dy
		self.ymax += dy
		self.pos += (dx, dy)
