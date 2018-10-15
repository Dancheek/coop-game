from sys import exit
import pygame

BG_COLOR = (37, 37, 37)
EMPTY_COLOR = (64, 64, 64)
WALL_COLOR = (100, 100, 100)
HP_COLOR = (80, 231, 22)

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

pygame.font.init()
font = pygame.font.SysFont("consolas", 40)
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
		self.hp = 3
		self.tile_map = [[0 for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]

	def is_wall(self, x, y):
		if (self.tile_map[y][x] == 1):
			return True
		return False

	def draw_block(self, color, x, y):
		screen.fill(color, (SPACE_WIDTH + x * TILE_SPACE_WIDTH,
							SPACE_WIDTH + y * TILE_SPACE_WIDTH,
							TILE_WIDTH, TILE_WIDTH))

	def draw_small_block(self, color, x, y):
		screen.fill(color, (SPACE_WIDTH + x * TILE_SPACE_WIDTH + SPACE_WIDTH,
							SPACE_WIDTH + y * TILE_SPACE_WIDTH + SPACE_WIDTH,
							TILE_WIDTH - SPACE_WIDTH * 2,
							TILE_WIDTH - SPACE_WIDTH * 2))

	def draw_sep_line(self):
		screen.fill(WALL_COLOR, SEP_LINE_RECT)

	def draw_stats(self):
		i = 0
		for player in self.players:
			screen.fill(self.players[player]['color'], (SPACE_WIDTH,
													STATS_Y_POS + TILE_SPACE_WIDTH * i,
													TILE_WIDTH,
													TILE_WIDTH))
			if (player == self.id):
				screen.fill(WALL_COLOR, (0, STATS_Y_POS + TILE_SPACE_WIDTH * i, SPACE_WIDTH, TILE_WIDTH))
			for hp in range(self.players[player]['hp']):
				screen.fill(HP_COLOR, (SPACE_WIDTH + TILE_SPACE_WIDTH * (hp + 1),
										STATS_Y_POS + TILE_SPACE_WIDTH * i,
										TILE_WIDTH,
										TILE_WIDTH))
			i += 1

	def draw_tile_map(self):
		for i in range(MAP_HEIGHT):
			for j in range(MAP_WIDTH):
				if (self.tile_map[i][j] == 0):
					self.draw_block(EMPTY_COLOR, j, i)
				elif (self.tile_map[i][j] == 1):
					self.draw_block(WALL_COLOR, j, i)


	def main(self, players):
		screen.fill(BG_COLOR)
		if self.id is not None:
			if (self.d_x != 0 or self.d_y != 0):
				if (self.x + self.d_x >= 0 and
					self.x + self.d_x < MAP_WIDTH and
					self.y + self.d_y >= 0 and
					self.y + self.d_y < MAP_HEIGHT and
					not self.is_wall(self.x + self.d_x, self.y + self.d_y)):
						self.change_pos(self.d_x, self.d_y)
				self.d_x, self.d_y = 0, 0

			self.draw_tile_map()
			self.draw_sep_line()

			for i in players:
				if (i == self.id):
					#self.draw_block(players[i]['color'], players[i]['x'], players[i]['y'])
					self.draw_block(self.color, self.x, self.y)
				else:
					self.draw_small_block(players[i]['color'], players[i]['x'], players[i]['y'])

			self.draw_stats()
		pygame.display.flip()

	def handle(self):
		for e in pygame.event.get():
			if (e.type == pygame.QUIT):
				exit()
			if (e.type == pygame.KEYDOWN):
				if (e.key == pygame.K_w):
					self.d_x, self.d_y = COORDS[0]
				if (e.key == pygame.K_a):
					self.d_x, self.d_y = COORDS[1]
				if (e.key == pygame.K_s):
					self.d_x, self.d_y = COORDS[2]
				if (e.key == pygame.K_d):
					self.d_x, self.d_y = COORDS[3]


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
