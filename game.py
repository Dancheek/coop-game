print('game initialising...')
from sys import exit
from time import time as sys_time
from PodSixNet.Connection import connection
from socket import gethostname, gethostbyname
import pygame

from client import Client
from fov import get_fov, line
import image
import text_input
import modloader

BG_COLOR = (37, 37, 37)
EMPTY_COLOR = (50, 50, 50)

HP_COLOR = (243, 16, 76)
MP_COLOR = (15, 121, 222)
AP_COLOR = (243, 205, 48)

FIRE_COLOR = (225, 106, 0)
FREEZE_COLOR = (0, 148, 255)

TILE_WIDTH = 32
SPACE_WIDTH = 8

tile_map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 3, 3, 3, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 3, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
			[1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
			[1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

TURN_TIME = 15

SCREEN_SIZE = (800, 800)
TIME_LINE_WIDTH = 800

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
		screen = pygame.display.set_mode(SCREEN_SIZE)#, pygame.FULLSCREEN)
		pygame.display.set_caption("Tile game")
		self.connected = False
		self.connecting = False

		self.color = (255, 255, 255)
		self.nickname = ''

		self.d_x = 0
		self.d_y = 0

		self.x = 4
		self.y = 4

		self.m_tile_x = None
		self.m_tile_y = None

		self.stats = {}
		self.stats_max = {}
		self.bars = {}

		self.magic = FIRE_MAGIC
		self.id = 1
		self.active_player = 1
		self.turn_start_time = sys_time()
		self.players = {}
		self.objects = {}
		self.clock = pygame.time.Clock()
		self.text_input = text_input.TextInput(font)
		self.text_input_active = False
		self.messages = []

		self.tile_map = tile_map#[[0 for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]
		self.map_width = len(self.tile_map[0])
		self.map_height = len(self.tile_map)
		self.fov_map = [[0] * self.map_width for i in range(self.map_height)]
		self.fov_radius = 12
		self.calc_fov()

		self.install_mods()

	def install_mods(self):
		print("loading mods...")
		self.mods = modloader.load_mods()
		for mod in self.mods:
			print("{} v.{}: {}".format(mod.name, mod.version, mod.description))
			self.stats.update(mod.stats)
			self.stats_max.update(mod.stats_max)
			self.bars.update(mod.bars)

	def change_pos(self, d_x, d_y):
		if (self.connected):
			self.client.change_pos(d_x, d_y)
		self.x += d_x
		self.y += d_y

	def cast_magic(self, x, y, magic):
		if (self.connected):
			self.client.cast_magic(x, y, magic)
		else:
			self.tile_map[y][x] = magic

	def end_turn(self):
		if (self.connected):
			self.client.end_turn()
		else:
			self.mp = self.max_mp
			self.ap = self.max_ap
			self.turn_start_time = sys_time()

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
		if (x < 0):					return True
		if (x >= self.map_width):	return True
		if (y < 0):					return True
		if (y >= self.map_height):	return True

		if (self.tile_map[y][x] == WALL_TILE or self.tile_map[y][x] == FREEZE_MAGIC):
			return True
		return False

	def send_message(self, message):
		if (message[0] == '/'):
			if (message.split()[0] == '/c'):
				if (len(message.split()) == 1):
					self.connect(g_localhost, g_port)
				else:
					self.connect(message.split()[1], g_port)
			elif (message.split()[0] == '/q'):
				pass
			elif (message.split()[0] == '/nickname'):
				pass
		else:
			if (self.connected):
				self.client.send_message(message)
			else:
				self.messages.append(message)

	def draw_block(self, color, x, y, y_bounded=True):
		screen.fill(color, (x, y, TILE_WIDTH, TILE_WIDTH))

	def draw_small_block(self, color, x, y):
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

	def draw_messages(self):
		for i, message in enumerate(reversed(self.messages)):
			if (i == 8): return
			screen.blit(font.render(message, 1, (255, 255, 255)), (10, SCREEN_SIZE[1] - 50 - i*20))

	def draw_stats(self):
		bar_width = 60
		bar_height = 16
		bar_sep = 28
		x = y = 12
		for bar, stat_name in enumerate(self.bars):
			for i in range(self.bars[stat_name]['max']):
				if (i < self.stats[stat_name]):
					screen.fill(self.bars[stat_name]['color'], (x + i * bar_width, y + bar_sep * bar, \
																bar_width, bar_height))
				else:
					screen.fill(EMPTY_COLOR, (x + i * bar_width, y + bar_sep * bar, \
																bar_width, bar_height))

	def draw_tile_map(self):
		for i in range(self.map_height):
			for j in range(self.map_width):
				if (self.fov_map[i][j]):
					if (self.tile_map[i][j] == EMPTY_TILE):
						screen.blit(image.floor, self.tile_to_screen(j, i))
					elif (self.tile_map[i][j] == WALL_TILE):
						screen.blit(image.wall, self.tile_to_screen(j, i))
					elif (self.tile_map[i][j] == FIRE_MAGIC):
						screen.fill(FIRE_COLOR, (*self.tile_to_screen(j, i), TILE_WIDTH, TILE_WIDTH))
					elif (self.tile_map[i][j] == FREEZE_MAGIC):
						screen.fill(FREEZE_COLOR, (*self.tile_to_screen(j, i), TILE_WIDTH, TILE_WIDTH))
		for i in self.objects:
			if (self.fov_map[self.objects[i]['y']][self.objects[i]['x']]):
				if (self.id != i):
					screen.blit(image.object, self.tile_to_screen(self.objects[i]['x'], self.objects[i]['y']))
		screen.blit(image.player, (SCREEN_CENTER_X - TILE_WIDTH // 2, SCREEN_CENTER_Y - TILE_WIDTH // 2))

	def calc_fov(self):
		self.fov_map = get_fov(self.tile_map, self.x, self.y, self.fov_radius, (WALL_TILE, FREEZE_MAGIC))

	def main(self):
		self.clock.tick(60)
		screen.fill(BG_COLOR)

		#print(self.id, self.active_player)
		if (self.d_x != 0 or self.d_y != 0):
			if (not self.is_wall(self.x + self.d_x, self.y + self.d_y)):
				if (self.connected):
					if (self.client.turn_based):
						if (self.id == self.active_player):
							self.change_pos(self.d_x, self.d_y)
							self.calc_fov()
					else:
						self.change_pos(self.d_x, self.d_y)
						self.calc_fov()
				else:
					self.change_pos(self.d_x, self.d_y)
					self.calc_fov()
			self.d_x, self.d_y = 0, 0

		self.draw_tile_map()
		#if (self.m_tile_x != None and self.m_tile_y != None):
		#	for tile in (line(self.x, self.y, self.m_tile_x, self.m_tile_y)):
		#		self.draw_small_block((255, 255, 255), *self.tile_to_screen(*tile))
		if (self.connected and self.client.turn_based):
			self.draw_time_line()
			if (self.id == self.active_player):
				if (self.stats['mana'] == 0 and self.stats['action'] == 0):
					self.end_turn()
				if (self.get_time_from_turn_start() > TURN_TIME):
					self.end_turn()
		self.draw_stats()
		#screen.blit(font.render(str(round(self.clock.get_fps())), 1, (255, 255, 255)), (SCREEN_SIZE[0] - 22, SCREEN_SIZE[1] - 20))
		if (self.text_input_active):
			screen.blit(self.text_input.render(), (10, SCREEN_SIZE[1] - 30))
		self.draw_messages()
		pygame.display.flip()

	def handle(self):
		keys_pressed = pygame.key.get_pressed()
		m_x, m_y = pygame.mouse.get_pos()
		self.m_tile_x, self.m_tile_y = self.screen_to_tile(m_x, m_y)
		if (self.m_tile_x < 0 or self.m_tile_x >= self.map_width):
			self.m_tile_x = None
		if (self.m_tile_y < 0 or self.m_tile_y >= self.map_height):
			self.m_tile_y = None

		events = pygame.event.get()
		for e in events:
			if (e.type == pygame.QUIT):
				exit()

			if (e.type == pygame.KEYDOWN and e.key == pygame.K_F4):
				if (keys_pressed[pygame.K_LALT]): exit()

		if (self.text_input_active):
			output = self.text_input.update(events)
			if (output != None):
				if (output == 0):
					self.text_input_active = False
				else:
					self.send_message(output)
		else:
			for e in events:
				if (e.type == pygame.MOUSEBUTTONDOWN):
					if (e.button == 1):
						if (self.m_tile_x != None and self.m_tile_y != None and \
							self.fov_map[self.m_tile_y][self.m_tile_x]):
								self.cast_magic(self.m_tile_x, self.m_tile_y, self.magic)

				if (e.type == pygame.KEYDOWN):
					if (e.key == pygame.K_SPACE):
						self.end_turn()
					if (e.key == pygame.K_TAB):
						self.connect(g_host, g_port)
					if (e.key == pygame.K_RETURN):
						self.text_input_active = True
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

	def connect(self, host, port):
		if (not self.connected):
			self.send_message('!> connecting...')
			self.client = Client(self, host, port)
			self.connecting = True
			#self.send_message('!> connection refused')
			#self.connected = False

	def on_connect(self):
		self.send_message('!> connected')
		self.connected = True


if (__name__ == "__main__"):
	g_localhost = gethostbyname(gethostname())
	g_port = 40327
	game = Game()
	while (True):
		if (game.connecting or game.connected):
			game.client.Loop()
		game.handle()
		game.main()

