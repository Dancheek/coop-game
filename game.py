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
import loader
import api
import tile
#import world

BG_COLOR = (37, 37, 37)
EMPTY_COLOR = (50, 50, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 50, 70)

#RED = (234, 22, 55)
#BLUE = (23, 95, 232)
#YELLOW = (241, 219, 23)
#CYAN = (25, 208, 148)
#PINK = (238, 122, 167)
#VIOLET = (165, 53, 147)

HP_COLOR = (243, 16, 76)
MP_COLOR = (15, 121, 222)
AP_COLOR = (243, 205, 48)

FIRE_COLOR = (225, 106, 0)
FREEZE_COLOR = (0, 148, 255)

TILE_WIDTH = 32
SPACE_WIDTH = 8

tile_map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
			[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
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

pygame.display.init()
pygame.display.set_caption("Tile game")

SCREEN_SIZE = (800, 800)
FULL_SCREEN_SIZE = (pygame.display.Info().current_w,
					pygame.display.Info().current_h)

screen_size = SCREEN_SIZE

screen_center_x = screen_size[0] // 2
screen_center_y = screen_size[1] // 2

EMPTY_TILE = 0
WALL_TILE = 1
FIRE_MAGIC = 2
FREEZE_MAGIC = 3
MAGIC_COLORS = {FIRE_MAGIC: FIRE_COLOR,
				FREEZE_MAGIC: FREEZE_COLOR}

pygame.font.init()
font = pygame.font.SysFont("consolas", 20)
COORDS = ((0, -1), (-1, 0), (0, 1), (1, 0))

def fill_alpha(color, alpha, rect=None):
	screen.fill(tuple(255 * (1 - alpha) for i in range(3)), rect, pygame.BLEND_MULT)
	screen.fill(tuple(i * alpha for i in color), rect, pygame.BLEND_ADD)

class Game:
	def __init__(self):
		global screen
		screen = pygame.display.set_mode(screen_size)
		#pygame.mouse.set_cursor((8, 8), (4, 4), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 60, 60, 60, 60, 0, 0))
		self.is_fullscreen = False

		api.screen = screen
		api.game = self
		api.send_message = self.add_message
		api.send_message_to_all = self.add_message

		self.connected = False
		self.connecting = False

		self.nickname = 'player'

		self.d_x = 0
		self.d_y = 0

		self.m_tile_x = 0
		self.m_tile_y = 0

		self.x = 4
		self.y = 4

		self.images = {}

		self.stats = {'active': True}
		self.stats_max = {}

		self.bars = {}
		self.bar_width = 60
		self.bar_height = 16
		self.bar_sep = 28
		self.bar_x_offset = 12
		self.bar_y_offset = 12

		self.tiles = {}

		self.chat_commands = {'c': self.command_connect,
								'q': self.command_leave,
								'exit': self.command_exit,
								'nick': self.command_nickname,
								'help': self.command_help}

		self.magic = FIRE_MAGIC
		self.objects = {}
		self.clock = pygame.time.Clock()
		self.text_input = text_input.TextInput(font)
		self.state = 'normal'

		self.messages = []
		self.messages_on_screen = 20
		self.message_show_from = 0

		self.fov_radius = 12
		self.install_mods()

		self.load_world('default_world')

		self.add_message('press ENTER to open chat', color=YELLOW)
		self.add_message('============= COMMANDS =============')
		self.add_message('/c <ip>          - connect to server', color=(127, 127, 127))
		self.add_message('/q               - abort connection', color=(127, 127, 127))
		self.add_message('/nick <nickname> - change nickname', color=(127, 127, 127))
		self.add_message('====================================')

	def toggle_fullscreen(self):
		global screen
		global screen_size
		global screen_center_x
		global screen_center_y
		if (self.is_fullscreen):
			screen_size = SCREEN_SIZE
			screen_center_x = screen_size[0] // 2
			screen_center_y = screen_size[1] // 2
			screen = pygame.display.set_mode(screen_size)
			self.is_fullscreen = False
		else:
			screen_size = FULL_SCREEN_SIZE
			screen_center_x = screen_size[0] // 2
			screen_center_y = screen_size[1] // 2
			screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
			self.is_fullscreen = True

	def install_mods(self):
		print("loading mods...")
		self.mods = loader.load_mods()
		for mod in self.mods:
			print("{} v.{}: {}".format(mod.name, mod.version, mod.description))
			self.stats.update(mod.stats)
			self.stats_max.update(mod.stats_max)
			self.bars.update(mod.bars)
			self.images.update(mod.images)
			self.tiles.update(mod.tiles)
			self.chat_commands.update(mod.chat_commands)
		for img in self.images:
			self.images[img] = image.from_str(self.images[img])

	def load_tile_map(self, tile_map):
		self.tile_map = tile.from_dict(tile_map, self.tiles)
		self.map_width = len(self.tile_map[0])
		self.map_height = len(self.tile_map)
		self.calc_fov()

	def load_world(self, world_name):
		self.load_tile_map(loader.load_world(world_name))
		#self.world = world.load(name)

	def save_world(self, world_name):
		loader.save_world(tile.to_dict(self.tile_map), world_name)
		#self.world.save(world_name)

	def tile_to_screen(self, tile_x, tile_y, center_x=None, center_y=None):
		if (center_x == None): center_x = self.x
		if (center_y == None): center_y = self.y
		return (screen_center_x - TILE_WIDTH // 2 + (tile_x - center_x) * TILE_WIDTH,
				screen_center_y - TILE_WIDTH // 2 + (tile_y - center_y) * TILE_WIDTH)

	def screen_to_tile(self, screen_x, screen_y, center_x=None, center_y=None):
		if (center_x == None): center_x = self.x
		if (center_y == None): center_y = self.y
		return ((screen_x - screen_center_x + TILE_WIDTH // 2) // TILE_WIDTH + center_x,
				(screen_y - screen_center_y + TILE_WIDTH // 2) // TILE_WIDTH + center_y)

	def is_outside(self, x, y):
		if (x < 0):					return True
		if (x >= self.map_width):	return True
		if (y < 0):					return True
		if (y >= self.map_height):	return True
		return False

	def calc_fov(self):
		self.fov_map = get_fov(self.tile_map, self.x, self.y, self.fov_radius)

	def update_mouse_tile_pos(self):
		self.m_tile_x, self.m_tile_y = self.screen_to_tile(*pygame.mouse.get_pos())

	def add_message(self, text, color=WHITE, player=None):
		self.messages.append({'text': text,
								'color': color,
								'time': sys_time()})

	# ---------- potential network interacting -----------

	def change_pos(self, d_x, d_y):
		if (self.connected):
			self.client.change_pos(d_x, d_y)
		self.x += d_x
		self.y += d_y
		self.calc_fov()
		self.update_mouse_tile_pos()

	def cast_magic(self, x, y, magic):
		if (self.connected):
			self.client.cast_magic(x, y, magic)
		else:
			self.add_message("casted: {}, x: {}, y: {}".format(magic, x, y))
		self.calc_fov()

	def send_message(self, text, color=WHITE):
		if (text[0] == '/'):
			self.exec_chat_command(text[1:])
		else:
			if (self.connected):
				self.client.send_message({'text': text,
										'color': color})
			else:
				self.add_message(text, color=color)

	def exec_chat_command(self, text):
		if (text.split()[0] in self.chat_commands):
			self.chat_commands[text.split()[0]](*text.split())
		else:
			self.add_message('command not found: ' + text.split()[0])


	def interact(self, x, y):
		if (self.connected):
			self.client.interact(x, y)
		else:
			self.tile_map[y][x].interact(self)

	# ----------- screen rendering -----------

	def draw_block(self, color, x, y, y_bounded=True):
		screen.fill(color, (x, y, TILE_WIDTH, TILE_WIDTH))

	def draw_small_block(self, color, x, y):
		screen.fill(color, (x + SPACE_WIDTH,
							y + SPACE_WIDTH,
							TILE_WIDTH - SPACE_WIDTH * 2,
							TILE_WIDTH - SPACE_WIDTH * 2))

	def draw_tile(self, tile_id, x, y):
		screen.blit(self.images[tile_id], self.tile_to_screen(x, y))

	def draw_messages(self, lifetime=5):
		if (lifetime == None):
			for i, message in enumerate(list(reversed(self.messages))[self.message_show_from:]):
				if (i == self.messages_on_screen):
					return
				screen.blit(font.render(message['text'], 1, message['color']), (10, screen_size[1] - 50 - i*20))
		else:
			for i, message in enumerate(reversed(self.messages)):
				if (i == self.messages_on_screen):
					return
				if (sys_time() - message['time'] < lifetime):
					screen.blit(font.render(message['text'], 1, message['color']), (10, screen_size[1] - 50 - i*20))

	def draw_stats(self):
		for bar, stat_name in enumerate(self.bars):
			for i in range(self.bars[stat_name]['max']):
				if (i < self.stats[stat_name]):
					screen.fill(self.bars[stat_name]['color'], (self.bar_x_offset + i * self.bar_width, \
																self.bar_y_offset + self.bar_sep * bar, \
																self.bar_width, self.bar_height))
				else:
					screen.fill(EMPTY_COLOR, (self.bar_x_offset + i * self.bar_width, \
												self.bar_y_offset + self.bar_sep * bar, \
												self.bar_width, self.bar_height))

	def draw_tile_map(self): # TODO rework
		for i in range(self.map_height):
			for j in range(self.map_width):
				if (self.fov_map[i][j]):
					self.draw_tile(self.tile_map[i][j].image, j, i)
		for i in self.objects:
			if (self.fov_map[self.objects[i]['y']][self.objects[i]['x']]):
				if (self.id != i):
					self.draw_tile('default:object', self.objects[i]['x'], self.objects[i]['y'])
		screen.blit(self.images['default:player'], (screen_center_x - TILE_WIDTH // 2, screen_center_y - TILE_WIDTH // 2))

	# --------------- main loop ----------------

	def main(self):
		self.clock.tick(60)
		screen.fill(BG_COLOR)

		if (self.d_x != 0 or self.d_y != 0):
			if (not self.is_outside(self.x + self.d_x, self.y + self.d_y) and self.stats['active']):
				self.tile_map[self.y + self.d_y][self.x + self.d_x].on_try_to_step(self)
				if (not self.tile_map[self.y + self.d_y][self.x + self.d_x].is_wall):
					self.change_pos(self.d_x, self.d_y)
					self.tile_map[self.y][self.x].on_step(self)
			self.d_x, self.d_y = 0, 0

		self.draw_tile_map()
		if (self.state == 'normal'):
			self.draw_tile('default:selection', self.m_tile_x, self.m_tile_y)
		#if (self.m_tile_x != None and self.m_tile_y != None):
		#	for tile in (line(self.x, self.y, self.m_tile_x, self.m_tile_y)):
		#		self.draw_small_block(WHITE, *self.tile_to_screen(*tile))

		self.draw_stats()

		if (self.state == 'text_input'): self.draw_messages(lifetime=None)
		else: self.draw_messages()

		if (self.state == 'text_input'):
			screen.blit(self.text_input.render(), (10, screen_size[1] - 30))
		elif (self.state == 'player_menu'):
			fill_alpha((48, 48, 48), 0.5)
		pygame.display.flip()

	# ------------- events handling -------------

	def handle(self, events):
		keys_pressed = pygame.key.get_pressed()
		self.update_mouse_tile_pos()

		for e in events:
			if (e.type == pygame.QUIT):
				exit()

			if (e.type == pygame.KEYDOWN):
				if (e.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT):
					exit()
				if (e.key == pygame.K_F11):
					self.toggle_fullscreen()

		if (self.state == 'text_input'):
			self.text_input.update(events)
			for e in events:
				if (e.type == pygame.MOUSEBUTTONDOWN):
					if (e.button == 4): # scroll up
						if (len(self.messages) > self.messages_on_screen and \
							self.message_show_from + self.messages_on_screen < len(self.messages)):
								self.message_show_from += 1
					if (e.button == 5): # scroll down
						if (len(self.messages) > self.messages_on_screen and \
							self.message_show_from > 0):
								self.message_show_from -= 1

				if (e.type == pygame.KEYDOWN):
					if (e.key == pygame.K_TAB):
						self.text_input.try_autocomplete(self.chat_commands)
					if (e.key == pygame.K_RETURN):
						text = self.text_input.get_text()
						if (text == ''):
							self.state = 'normal'
						else:
							self.send_message(text)
							self.text_input.clear()

					if (e.key == pygame.K_ESCAPE):
						self.state = 'normal'

		elif (self.state == 'player_menu'):
			for e in events:
				if (e.type == pygame.MOUSEBUTTONDOWN):
					pass
				if (e.type == pygame.KEYDOWN):
					if (e.key == pygame.K_TAB):
						self.state = 'normal'
					if (e.key == pygame.K_ESCAPE):
						self.state = 'normal'

		elif (self.state == 'normal'):
			for e in events:
				if (e.type == pygame.MOUSEBUTTONDOWN):
					if (e.button == 1): # LMB
						if (not self.is_outside(self.m_tile_x, self.m_tile_y) and \
							self.fov_map[self.m_tile_y][self.m_tile_x]):
								self.cast_magic(self.m_tile_x, self.m_tile_y, self.magic)
					if (e.button == 3): # RMB
						if (not self.is_outside(self.m_tile_x, self.m_tile_y)):
							self.interact(self.m_tile_x, self.m_tile_y)
							self.calc_fov()

				if (e.type == pygame.MOUSEMOTION):
					if (e.buttons[0] == 1):
						pass # some drag'n'drop

				if (e.type == pygame.KEYDOWN):
					if (e.key == pygame.K_TAB):
						self.state = 'player_menu'
					if (e.key == pygame.K_RETURN):
						self.state = 'text_input'
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

	# ------------ network --------------

	def connect(self, host, port):
		if (not self.connected):
			self.send_message('!> connecting to {}:{}...'.format(host, port), color=YELLOW)
			self.client = Client(self, host, port)
			self.connecting = True
			#self.send_message('!> connection refused')
			#self.connected = False

	def disconnect(self):
		if (self.connecting):
			self.connecting = False
			self.add_message('!> aborted', color=RED)
		elif (self.connected):
			self.connected = False
			self.client.connection.Close()
			self.load_world('default_world')
			self.objects = {}
			self.x = 4
			self.y = 4
			self.calc_fov()
			self.add_message('!> disconnected from server', color=YELLOW)

	def on_connect(self):
		self.send_message('!> connected', color=YELLOW)
		self.connecting = False
		self.connected = True

	def on_disconnect(self):
		self.connecting = False
		self.connected = False
		self.add_message('!> disconnected', color=YELLOW)

	# ------------- chat commands --------------

	def command_connect(self, *args):
		if (len(args) == 1):
			self.connect(g_localhost, g_port)
		elif (len(args) == 2):
			self.connect(args[1], g_port)
		elif (len(args) == 3):
			if (not args[2].isdigit()):
				self.add_message('port must be a number', color=RED)
			else:
				self.connect(args[1], int(args[2]))
		else:
			self.add_message('Usage: /c <host> <port>', color=YELLOW)

	def command_exit(self, *args):
		exit()

	def command_help(self, *args):
		self.add_message('Available commands:')
		for command in self.chat_commands:
			self.add_message(command)

	def command_leave(self, *args):
		if (self.connecting or self.connected):
			self.disconnect()

	def command_nickname(self, *args):
		if (len(args) == 2):
			self.nickname = args[1]
			self.send_message(f'Your nickname - "{self.nickname}"')
		else:
			self.send_message(f'Your nickname - "{self.nickname}"')
			self.send_message('Usage: /nick <new nickname>', color=YELLOW)


g_localhost = gethostbyname(gethostname())
g_port = 40327
game = Game()
while (True):
	if (game.connecting or game.connected):
		game.client.loop()
	events = pygame.event.get()
	game.handle(events)
	for mod in game.mods:
		if (hasattr(mod, 'main')):
			mod.main(game)
	game.main()

