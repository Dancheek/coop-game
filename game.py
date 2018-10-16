from sys import exit
import pygame
from fov import get_fov

BG_COLOR = (37, 37, 37)
EMPTY_COLOR = (64, 64, 64)
WALL_COLOR = (100, 100, 100)
HP_COLOR = (80, 231, 22)
FIRE_COLOR = (225, 106, 0)
FREEZE_COLOR = (0, 148, 255)

TILE_WIDTH = 32
SPACE_WIDTH = 8
TILE_SPACE_WIDTH = TILE_WIDTH + SPACE_WIDTH

MAP_WIDTH = 12
MAP_HEIGHT = 10

SCREEN_SIZE = (MAP_WIDTH * TILE_SPACE_WIDTH + SPACE_WIDTH,
				(MAP_HEIGHT + 2) * TILE_SPACE_WIDTH + SPACE_WIDTH * 3)
SEP_LINE_RECT = (SPACE_WIDTH,
					MAP_HEIGHT * TILE_SPACE_WIDTH + SPACE_WIDTH,
					MAP_WIDTH * TILE_SPACE_WIDTH - SPACE_WIDTH,
					SPACE_WIDTH)
STATS_Y_POS = MAP_HEIGHT * TILE_SPACE_WIDTH + SPACE_WIDTH * 3

FIRE_MAGIC = 2
FREEZE_MAGIC = 3
MAGIC_COLORS = {FIRE_MAGIC: FIRE_COLOR,
				FREEZE_MAGIC: FREEZE_COLOR}

pygame.font.init()
font = pygame.font.SysFont("consolas", 20)
COORDS = ((0, -1), (-1, 0), (0, 1), (1, 0))
LINE_HEIGTH = 16


class Game:
	def __init__(self):
		self.playersLabel = "0 players"
		self.statusLabel = "connecting"
		global screen
		screen = pygame.display.set_mode(SCREEN_SIZE)
		pygame.display.set_caption("Tile game")
		self.d_x = 0
		self.d_y = 0
		self.x = -1
		self.y = -1
		self.m_tile_x = None
		self.m_tile_y = None
		self.made_step = True
		self.magic_casted = True
		self.hp = 3
		self.active_player = -1
		self.magic = FIRE_MAGIC
		self.clock = pygame.time.Clock()
		self.tile_map = [[0 for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]
		self.fov_map = [[1] * MAP_WIDTH for i in range(MAP_HEIGHT)]
		self.fov_radius = 20

	def is_wall(self, x, y):
		if (self.tile_map[y][x] == 1):
			return True
		return False

	def draw_block(self, color, x, y, y_bounded=True):
		x = SPACE_WIDTH + x * TILE_SPACE_WIDTH
		if (y_bounded):
			y = SPACE_WIDTH + y * TILE_SPACE_WIDTH
		screen.fill(color, (x, y, TILE_WIDTH, TILE_WIDTH))

	def draw_small_block(self, color, x, y, y_bounded=True):
		x = SPACE_WIDTH + x * TILE_SPACE_WIDTH
		if (y_bounded):
			y = SPACE_WIDTH + y * TILE_SPACE_WIDTH
		screen.fill(color, (x + SPACE_WIDTH,
							y + SPACE_WIDTH,
							TILE_WIDTH - SPACE_WIDTH * 2,
							TILE_WIDTH - SPACE_WIDTH * 2))

	def draw_sep_line(self):
		screen.fill(self.color, SEP_LINE_RECT)

	def draw_stats(self):
		y = 0
		for player in self.players:
			self.draw_block(self.players[player]['color'], 0, STATS_Y_POS + TILE_SPACE_WIDTH * y, y_bounded = False)
			for hp in range(self.players[player]['hp']):
				self.draw_block(HP_COLOR, hp + 1, STATS_Y_POS + TILE_SPACE_WIDTH * y, y_bounded = False)
			y += 1
		if (self.magic_casted):
			self.draw_small_block(MAGIC_COLORS[self.magic],
									MAP_WIDTH - 1,
									SCREEN_SIZE[1] - TILE_SPACE_WIDTH,
									y_bounded = False)
		else:
			self.draw_block(MAGIC_COLORS[self.magic],
							MAP_WIDTH - 1,
							SCREEN_SIZE[1] - TILE_SPACE_WIDTH,
							y_bounded = False)
		if (self.made_step):
			self.draw_small_block(WALL_COLOR,
									MAP_WIDTH - 2,
									SCREEN_SIZE[1] - TILE_SPACE_WIDTH,
									y_bounded = False)
		else:
			self.draw_block(WALL_COLOR,
							MAP_WIDTH - 2,
							SCREEN_SIZE[1] - TILE_SPACE_WIDTH,
							y_bounded = False)

	def draw_tile_map(self):
		for i in range(MAP_HEIGHT):
			for j in range(MAP_WIDTH):
				if (self.fov_map[i][j]):
					if (self.tile_map[i][j] == 0):
						self.draw_block(EMPTY_COLOR, j, i)
					elif (self.tile_map[i][j] == 1):
						self.draw_block(WALL_COLOR, j, i)
					elif (self.tile_map[i][j] == FIRE_MAGIC):
						self.draw_block(FIRE_COLOR, j, i)
					elif (self.tile_map[i][j] == FREEZE_MAGIC):
						self.draw_block(FREEZE_COLOR, j, i)
		for i in self.players:
			if (self.fov_map[self.players[i]['y']][self.players[i]['x']]):
				if (i == self.active_player):
					self.draw_block(self.players[i]['color'], self.players[i]['x'], self.players[i]['y'])
				else:
					self.draw_small_block(self.players[i]['color'], self.players[i]['x'], self.players[i]['y'])


	def main(self, players):
		self.clock.tick(60)
		screen.fill(BG_COLOR)
		if self.id is not None:
			if (self.d_x != 0 or self.d_y != 0):
				if (self.x + self.d_x >= 0 and
					self.x + self.d_x < MAP_WIDTH and
					self.y + self.d_y >= 0 and
					self.y + self.d_y < MAP_HEIGHT and
					not self.is_wall(self.x + self.d_x, self.y + self.d_y) and
					self.id == self.active_player and
					not self.made_step):
						self.change_pos(self.d_x, self.d_y)
						self.made_step = True
						self.fov_map = get_fov(self.tile_map, self.x, self.y, self.fov_radius)
				self.d_x, self.d_y = 0, 0

			self.draw_tile_map()
			self.draw_sep_line()

			if (self.made_step and self.magic_casted and self.id == self.active_player):
				self.end_turn()

			self.draw_stats()
			#screen.blit(font.render(str(round(self.clock.get_fps())), 1, (255, 255, 255)), (0, 0))
		pygame.display.flip()

	def handle(self):
		m_x, m_y = pygame.mouse.get_pos()
		self.m_tile_x = m_x // TILE_SPACE_WIDTH
		self.m_tile_y = m_y // TILE_SPACE_WIDTH
		if (self.m_tile_x < 0 or self.m_tile_x >= MAP_WIDTH):
			self.m_tile_x = None
		if (self.m_tile_y < 0 or self.m_tile_y >= MAP_HEIGHT):
			self.m_tile_y = None

		for e in pygame.event.get():
			if (e.type == pygame.QUIT):
				exit()

			if (e.type == pygame.MOUSEBUTTONDOWN):
				if (e.button == 1):
					if (self.m_tile_x != None and self.m_tile_y != None and
						self.fov_map[self.m_tile_y][self.m_tile_x] and
						self.id == self.active_player and
						not self.magic_casted):
							self.set_tile(self.m_tile_x, self.m_tile_y, self.magic)
							self.magic_casted = True

			if (e.type == pygame.KEYDOWN):
				if (e.key == pygame.K_w):
					self.d_x, self.d_y = COORDS[0]
				if (e.key == pygame.K_a):
					self.d_x, self.d_y = COORDS[1]
				if (e.key == pygame.K_s):
					self.d_x, self.d_y = COORDS[2]
				if (e.key == pygame.K_d):
					self.d_x, self.d_y = COORDS[3]
				if (e.key == pygame.K_1):
					self.magic = FIRE_MAGIC
				if (e.key == pygame.K_2):
					self.magic = FREEZE_MAGIC


class Hub:
	def __init__(self):
		global screen
		screen = pygame.display.set_mode(SCREEN_SIZE)
		pygame.display.set_caption("Tile game")
		self.ip = ''

	def main(self):
		screen.fill(BG_COLOR)
		pygame.display.flip()

	def handle(self):
		for e in pygame.event.get():
			if (e.type == pygame.KEYDOWN):
				if (e.key == K_RETURN):
					pass
