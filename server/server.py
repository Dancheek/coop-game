from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from weakref import WeakKeyDictionary
from time import sleep
from socket import gethostbyname, gethostname
from _thread import start_new_thread
from random import randint, choice
from uuid import uuid4

import loader
import api
import tile
import world

MAP_WIDTH = 20
MAP_HEIGHT = 17
WALLS_COUNT = 60

EMPTY_TILE = 0
WALL_TILE = 1
FIRE_MAGIC = 2
FREEZE_MAGIC = 3

class ServerChannel(Channel): # player representation on server
	def __init__(self, *args, **kwargs):
		Channel.__init__(self, *args, **kwargs)
		self.uuid = str(uuid4())
		self.nickname = "player_" + self.uuid
		self.stats = self._server.player_stats.copy()
		self.stats_max = self._server.player_stats_max.copy()
		self.x = 5
		self.y = 2

	def send_self(self):
		self.Send({"action": "self",
					"uuid": self.uuid,
					"x": self.x,
					"y": self.y,
					"stats": self.stats})

	def set_pos(self, x, y):
		self.x = x
		self.y = y
		self._server.world.objects[self.uuid].x = x
		self._server.world.objects[self.uuid].y = y

	# ------------- Network callbacks ---------------

	def Network_join(self, data):
		self.nickname = data['nickname']
		self._server.add_player(self)

	def Network_change_pos(self, data):
		new_x = self.x + data['d_x']
		new_y = self.y + data['d_y']
		if (self.stats['active']):
			tile_updated = self._server.world.get_tile(new_x, new_y).on_try_to_step(self)
			if (tile_updated):
				self._server.update_tile(new_x, new_y)

			self.set_pos(new_x, new_y)
			self._server.send_objects()
		for mod in self._server.mods:
			if (hasattr(mod, 'server_change_pos')):
				mod.server_change_pos(self, data['d_x'], data['d_y'])
		self.send_self()

	def Network_set_tile(self, data):
		if ((not self._server.turn_based) or (self.turn_based and self.uuid == self._server.active_player)):
			self._server.world.set_tile(data['x'], data['y'], data['tile'])
			self._server.send_to_all(data)

	def Network_cast_magic(self, data):
		target_player = None
		for player in list(self._server.players.keys()):
			if (player.x == data['x'] and player.y == data['y']): target_player = player

		for mod in self._server.mods:
			if (hasattr(mod, 'server_cast_magic')):
				mod.server_cast_magic(self, target_player, data['magic'], data['x'], data['y'])

	def Network_message(self, data):
		if (data['message']['text'][0] == '/'):
			self._server.exec_chat_command(data['message']['text'][1:], self)
		else:
			text = "<{}> ".format(self.nickname) + data['message']['text']
			print(text)
			self._server.send_message_to_all(text)

	def Network_interact(self, data):
		tile_updated = self._server.world.get_tile(data['x'], data['y']).interact(self)
		if (tile_updated):
			self._server.update_tile(data['x'], data['y'])

	# ---------------------------------------------

	def Close(self):
		if (self in self._server.players):
			self._server.del_player(self)
		else:
			del self._server.waiting_for_join[self]


class GameServer(Server):
	channelClass = ServerChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		api.server = self
		api.send_message = self.send_message
		api.send_message_to_all = self.send_message_to_all
		api.exec_chat_command = self.exec_chat_command

		self.players = WeakKeyDictionary()
		self.waiting_for_join = WeakKeyDictionary()

		self.player_stats = {'active': True}
		self.player_stats_max = {}

		self.tile_classes = {}
		self.object_classes = {}

		self.chat_commands = {'help': self.command_help}

		self.players_count = 0

		self.install_mods()

		api.object_classes = self.object_classes
		api.tile_classes = self.tile_classes

		self.load_world('default_world')
		api.world = self.world

		print("Server launched")
		start_new_thread(self.command_input, ())

	def install_mods(self):
		print("loading mods...")
		self.mods = loader.load_mods()
		for mod in self.mods:
			print("{} v.{}: {}".format(mod.name, mod.version, mod.description))
			self.player_stats.update(mod.stats)
			self.player_stats_max.update(mod.stats_max)
			self.tile_classes.update(mod.tile_classes)
			self.object_classes.update(mod.object_classes)
			self.chat_commands.update(mod.chat_commands)

	def load_world(self, name):
		self.world = world.load(name)

	def get_player(self, uuid):
		for player in self.players:
			if (player.uuid == uuid): return player
		return None

	def next_player(self, player):
		players = list(self.players.keys())
		i = players.index(player)
		i += 1
		if (i == self.players_count):
			i = 0
		return players[i]

	def random_player(self):
		return choice(list(self.players.keys()))

	def set_stat(self, player, stat_name, value):
		player.stats[stat_name] = value

	def update_tile(self, x, y):
		self.send_to_all({"action": "set_tile", 'x': x, 'y': y, 'tile': self.world.get_tile(x, y).to_dict()})

	# --------- console interaction -------------

	def print_prompt(self):
		print("[{}] server> ".format(self.players_count), end='')

	def command_input(self):
		while True:
			#self.print_prompt()
			command = input()
			self.exec(command)

	def exec(self, command):
		if (command == ''):
			return
		elif (command == "round"):
			self.start_round()
		else:
			self.send_message_to_all(f"[SERVER] {command}", color=api.ORANGE)

	# -------------------------------------------

	def Connected(self, channel, addr):
		self.waiting_for_join[channel] = True

	def add_player(self, player):
		del self.waiting_for_join[player]
		print(f"[info] channel:  {player.addr}")
		print(f"[info] uuid:     {player.uuid}")
		print(f"[info] nickname: {player.nickname}")
		self.players[player] = True
		self.world.objects[player.uuid] = self.object_classes['default:player']({ \
											"id":		"default:player",
											"nickname": player.nickname,
											"x":		player.x,
											"y":		player.y,
											'uuid':		player.uuid})
		self.players_count += 1
		player.send_self()

		player.Send({"action": "world",
					"world": self.world.to_dict()})

		self.send_objects()

		self.send_message_to_all('{} has joined'.format(player.nickname), color=(255, 255, 0))
		print()

		for mod in self.mods:
			if (hasattr(mod, 'server_on_connect')):
				mod.server_on_connect(player)

	def del_player(self, player):
		print(f"{player.nickname} {player.addr} deleted")
		self.players_count -= 1
		del self.players[player]
		for obj_id in self.world.objects:
			if (obj_id == player.uuid):
				del self.world.objects[obj_id]
				break
		self.send_to_all({'action': 'del_object',
						'object': player.uuid})
		self.send_message_to_all(f'{player.nickname} has leaved', color=(255, 255, 0))

	def send_objects(self):
		self.send_to_all({"action": "objects",
						"objects": self.world.objects_to_dict()})

	def send_players(self):
		for i in self.players:
			i.send_self()

	def send_message(self, text, color=(255, 255, 255), player=None):
		message = {'text': text,
					'color': color}
		player.Send({"action": "message",
					"message": message})

	def send_message_to_all(self, text, color=(255, 255, 255)):
		message = {'text': text,
					'color': color}
		self.send_to_all({"action": "message",
						"message": message})

	def send_to_all(self, data):
		for i in self.players:
			i.Send(data)

	def exec_chat_command(self, text, player):
		print(f'{player.nickname} issued a command \'{text}\'')
		if (text.split()[0] in self.chat_commands):
			self.chat_commands[text.split()[0]](*text.split(), player=player)
		else:
			self.send_message('command not found: ' + text.split()[0], color=api.RED, player=player)
			self.send_message('try /help for command list', color=api.RED, player=player)

	# ---------- chat commands ----------

	def command_help(self, *args, player=None):
		api.send_message('Пока что тут вообще нет команд', color=api.YELLOW, player=player)


host = gethostbyname(gethostname())
port = "40327"#input("port: ")

server = GameServer(localaddr=(host, int(port)))

while (True):
	server.Pump()
	for mod in server.mods:
		if (hasattr(mod, 'server_main')):
			mod.server_main()
	#server.main()
	sleep(0.0001)
