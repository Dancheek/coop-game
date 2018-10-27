from sys import exit
import pygame
from fov import get_fov, line
from time import time as sys_time
import image

BG_COLOR = (37, 37, 37)
EMPTY_COLOR = (50, 50, 50)

HP_COLOR = (243, 16, 76)
MP_COLOR = (15, 121, 222)
AP_COLOR = (243, 205, 48)

FIRE_COLOR = (225, 106, 0)
FREEZE_COLOR = (0, 148, 255)

TILE_WIDTH = 32
SPACE_WIDTH = 8
TILE_SPACE_WIDTH = TILE_WIDTH + SPACE_WIDTH

MAP_WIDTH = 20
MAP_HEIGHT = 17

TURN_TIME = 15

#SCREEN_SIZE = (MAP_WIDTH * TILE_SPACE_WIDTH + SPACE_WIDTH,
#				(MAP_HEIGHT + 2) * TILE_SPACE_WIDTH + SPACE_WIDTH * 3)
SCREEN_SIZE = (800, 800)
TIME_LINE_WIDTH = 800
#TIME_LINE_WIDTH = MAP_WIDTH * TILE_SPACE_WIDTH - SPACE_WIDTH
#TIME_LINE_WIDTH = MAP_WIDTH * TILE_WIDTH - SPACE_WIDTH

STATS_Y_POS = 500
#STATS_Y_POS = MAP_HEIGHT * TILE_SPACE_WIDTH + SPACE_WIDTH * 3
SCREEN_CENTER_X = SCREEN_SIZE[0] // 2
SCREEN_CENTER_Y = SCREEN_SIZE[1] // 2

EMPTY_TILE = 0
WALL_TILE = 1
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

		self.ap = 0
		self.max_ap = 3

		self.hp = 3
		self.max_hp = 3

		self.mp = 2
		self.max_mp = 2
		self.magic = FIRE_MAGIC

		self.freezed = False
		self.active_player = -1
		self.clock = pygame.time.Clock()

		self.tile_map = [[0 for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]
		self.fov_map = [[0] * MAP_WIDTH for i in range(MAP_HEIGHT)]
		self.fov_radius = 7

	def tile_to_screen(self, tile_x, tile_y, center_x=None, center_y=None):
		if (center_x == None): center_x = self.x
		if (center_y == None): center_y = self.y
		return (SCREEN_CENTER_X - TILE_WIDTH // 2 + (tile_x - center_x) * TILE_WIDTH,
				SCREEN_CENTER_Y - TILE_WIDTH // 2 + (tile_y - center_y) * TILE_WIDTH)

	def screen_to_tile(self, screen_x, screen_y, center_x=None, center_y=None):
		if (center_x == None): center_x = self.x
		if (center_y == None): center_y = self.y
		return ((screen_x - SCREEN_CENTER_X + TILE_WIDTH // 2) // TILE_WIDTH + center_x,
				(screen_y - SCREEN_CENTER_Y + TILE_WIDTH // 2) // TILE_WIDTH + center_y)

	def get_time_from_turn_start(self):
		return sys_time() - self.turn_start_time

	def is_wall(self, x, y):
		if (self.tile_map[y][x] == WALL_TILE or self.tile_map[y][x] == FREEZE_MAGIC):
			return True
		return False

	def draw_block(self, color, x, y, y_bounded=True):
		#x *= TILE_WIDTH
		#if (y_bounded):
		#	y = y * TILE_WIDTH
		screen.fill(color, (x, y, TILE_WIDTH, TILE_WIDTH))

	def draw_small_block(self, color, x, y):
		#x *= TILE_WIDTH
		#if (y_bounded):
		#	y *= TILE_WIDTH
		screen.fill(color, (x + SPACE_WIDTH,
							y + SPACE_WIDTH,
							TILE_WIDTH - SPACE_WIDTH * 2,
							TILE_WIDTH - SPACE_WIDTH * 2))

	def draw_time_line(self):
		if (self.id == self.active_player):
			color = self.color
			width = TIME_LINE_WIDTH * (TURN_TIME - self.get_time_from_turn_start()) / TURN_TIME
			screen.fill(EMPTY_COLOR, (0, 0, TIME_LINE_WIDTH, SPACE_WIDTH))
		else:
			color = EMPTY_COLOR
			width = TIME_LINE_WIDTH
		screen.fill(color, (0, 0, width, SPACE_WIDTH))

	def draw_stats(self):
		bar_width = 60
		bar_height = 15
		bar_sep = 25
		for i in range(self.max_hp):
			if (i < self.hp): screen.fill(HP_COLOR, (10 + i * bar_width, SCREEN_SIZE[1] - bar_sep*3, bar_width, bar_height))
			else: screen.fill(EMPTY_COLOR, (10 + i * bar_width, SCREEN_SIZE[1] - bar_sep*3, bar_width, bar_height))

		for i in range(self.max_mp):
			if (i < self.mp): screen.fill(MP_COLOR, (10 + i * bar_width, SCREEN_SIZE[1] - bar_sep*2, bar_width, bar_height))
			else: screen.fill(EMPTY_COLOR, (10 + i * bar_width, SCREEN_SIZE[1] - bar_sep*2, bar_width, bar_height))

		for i in range(self.max_ap):
			if (i < self.ap): screen.fill(AP_COLOR, (10 + i * bar_width, SCREEN_SIZE[1] - bar_sep, bar_width, bar_height))
			else: screen.fill(EMPTY_COLOR, (10 + i * bar_width, SCREEN_SIZE[1] - bar_sep, bar_width, bar_height))

	def draw_tile_map(self):
		for i in range(MAP_HEIGHT):
			for j in range(MAP_WIDTH):
				if (self.fov_map[i][j]):
					if (self.tile_map[i][j] == EMPTY_TILE):
						screen.blit(image.floor, self.tile_to_screen(j, i))
					elif (self.tile_map[i][j] == WALL_TILE):
						screen.blit(image.wall, self.tile_to_screen(j, i))
					elif (self.tile_map[i][j] == FIRE_MAGIC):
						screen.fill(FIRE_COLOR, (*self.tile_to_screen(j, i), TILE_WIDTH, TILE_WIDTH))
					elif (self.tile_map[i][j] == FREEZE_MAGIC):
						screen.fill(FREEZE_COLOR, (*self.tile_to_screen(j, i), TILE_WIDTH, TILE_WIDTH))
		for i in self.players:
			if (self.fov_map[self.players[i]['y']][self.players[i]['x']]):
				if (self.id != i):
					screen.blit(image.player, self.tile_to_screen(self.players[i]['x'], self.players[i]['y']))
#				if (i == self.active_player):
#					self.draw_block(self.players[i]['color'], self.players[i]['x'], self.players[i]['y'])
#				else:
#					self.draw_small_block(self.players[i]['color'], self.players[i]['x'], self.players[i]['y'])
		screen.blit(image.player, (SCREEN_CENTER_X - TILE_WIDTH // 2, SCREEN_CENTER_Y - TILE_WIDTH // 2))

	def calc_fov(self):
		self.fov_map = get_fov(self.tile_map, self.x, self.y, self.fov_radius, (WALL_TILE, FREEZE_MAGIC))

	def main(self):
		self.clock.tick(60)
		screen.fill(BG_COLOR)

		if (self.d_x != 0 or self.d_y != 0):
			if (self.x + self.d_x >= 0 and
				self.x + self.d_x < MAP_WIDTH and
				self.y + self.d_y >= 0 and
				self.y + self.d_y < MAP_HEIGHT and
				not self.is_wall(self.x + self.d_x, self.y + self.d_y) and
				self.id == self.active_player and
				self.ap > 0 and
				not self.freezed):
					self.change_pos(self.d_x, self.d_y)
					self.ap -= 1
					self.calc_fov()
					if (self.tile_map[self.y][self.x] == FIRE_MAGIC):
						self.hp -= 1
						self.set_hp(self.hp)
						self.set_tile(self.x, self.y, EMPTY_TILE)
			self.d_x, self.d_y = 0, 0

		self.draw_tile_map()
#		if (self.m_tile_x != None and self.m_tile_y != None):
#			for tile in (line(self.x, self.y, self.m_tile_x, self.m_tile_y)):
#				self.draw_small_block((255, 255, 255), *self.tile_to_screen(*tile))
		self.draw_time_line()

		if (self.id == self.active_player):
			if (self.ap == 0 and self.mp == 0):
				self.end_turn()
			if (self.get_time_from_turn_start() > TURN_TIME):
				self.end_turn()
		self.draw_stats()
		screen.blit(font.render(str(round(self.clock.get_fps())), 1, (255, 255, 255)), (SCREEN_SIZE[0] - 22, SCREEN_SIZE[1] - 20))
		pygame.display.flip()

	def handle(self):
		m_x, m_y = pygame.mouse.get_pos()
		self.m_tile_x, self.m_tile_y = self.screen_to_tile(m_x, m_y)
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
						self.mp > 0):
							self.cast_magic(self.m_tile_x, self.m_tile_y, self.magic)

			if (e.type == pygame.KEYDOWN):
				if (e.key == pygame.K_SPACE):
					self.end_turn()
				if (e.key == pygame.K_LCTRL):
					self.hp -= 1
					self.set_hp(self.hp)
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

if (__name__ == "__main__"):
	print(123)


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
