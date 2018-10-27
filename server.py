from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from weakref import WeakKeyDictionary
from time import sleep
from socket import gethostbyname, gethostname
from _thread import start_new_thread
from random import randint

MAP_WIDTH = 20
MAP_HEIGHT = 17
WALLS_COUNT = 60

EMPTY_TILE = 0
WALL_TILE = 1
FIRE_MAGIC = 2
FREEZE_MAGIC = 3

class ServerChannel(Channel):
	def __init__(self, *args, **kwargs):
		Channel.__init__(self, *args, **kwargs)
		self.id = str(self._server.NextId())
		self.nickname = None
		self.x = -1
		self.y = -1
		self.hp = 3
		self.freezed = False
		self.color = (50, 50, 50)

	def PassOn(self, data):
		"""pass on what we received to all connected clients"""
		data.update({"id": self.id})
		self._server.SendToAll(data)

	# ------------- Network callbacks ---------------

	def Network_nickname(self, data):
		self.nickname = data['nickname']
		print("{} has joined".format(self.nickname))
		self.PassOn(data)

	def Network_color(self, data):
		self.color = data['color']
		self.PassOn(data)

	def Network_change_pos(self, data):
		if (self.id == self._server.active_player):
			self.x += data['d_x']
			self.y += data['d_y']
			self.PassOn(data)

	def Network_set_hp(self, data):
		self._server.set_hp(self, data['hp'])

	def Network_set_tile(self, data):
		if (self.id == self._server.active_player):
			self._server.tile_map[data['y']][data['x']] = data['tile']
			self._server.SendToAll(data)

	def Network_cast_magic(self, data):
		target_player = None
		for player in list(self._server.players.keys()):
			if (player.x == data['x'] and player.y == data['y']): target_player = player
		if (target_player != None):
			if (data['magic'] == FIRE_MAGIC):
				if (target_player.freezed):
					self._server.unfreeze_player(target_player)
				else:
					self._server.hit_player(target_player)
			elif (data['magic'] == FREEZE_MAGIC):
				self._server.freeze_player(target_player)
		else:
			tile = self._server.tile_map[data['y']][data['x']]

			if (tile == EMPTY_TILE):
				self._server.set_tile(data['x'], data['y'], data['magic'])

			elif (data['magic'] == FIRE_MAGIC and tile == FREEZE_MAGIC):
				self._server.set_tile(data['x'], data['y'], EMPTY_TILE)

			elif (data['magic'] == FREEZE_MAGIC and tile == FIRE_MAGIC):
				self._server.set_tile(data['x'], data['y'], EMPTY_TILE)

	def Network_end_turn(self, data):
		if (self.id == self._server.active_player):
			self._server.next_turn()

	# ---------------------------------------------

	def Close(self):
		self._server.DelPlayer(self)


class GameServer(Server):
	channelClass = ServerChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		self.id = 0
		self.players = WeakKeyDictionary()
		self.players_count = 0
		self.generate_tile_map()
		self.active_player_num = None
		self.active_player = None
		print("Server launched")
		start_new_thread(self.CommandInput, ())

	def get_player(self, id):
		for player in list(self.players.keys()):
			if (player.id == id): return player
		return None

	def hit_player(self, player):
		self.set_hp(player, player.hp - 1)

	def freeze_player(self, player):
		player.freezed = True
		player.Send({"action": "freeze"})

	def unfreeze_player(self, player):
		player.freezed = False
		player.Send({"action": "unfreeze"})

	def set_hp(self, player, hp):
		player.hp = hp
		self.SendToAll({"action": "set_hp", 'id': player.id, 'hp': player.hp})
		if (hp == 0): self.start_round()

	def set_tile(self, x, y, tile):
		self.tile_map[y][x] = tile
		self.SendToAll({"action": "set_tile", 'x': x, 'y': y, 'tile': tile})

	def generate_tile_map(self):
		correct = False
		while (not correct):
			self.tile_map = [[0 for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]
			x = randint(0, MAP_WIDTH - 1)
			y = randint(0, MAP_HEIGHT - 1)
			for i in range(WALLS_COUNT):
				while (self.tile_map[y][x] != 0):
					x = randint(0, MAP_WIDTH - 1)
					y = randint(0, MAP_HEIGHT - 1)
				self.tile_map[y][x] = 1

			while (self.tile_map[y][x] != 0):
				x = randint(0, MAP_WIDTH - 1)
				y = randint(0, MAP_HEIGHT - 1)
			correct = self.map_check([i[:] for i in self.tile_map], x, y)

	def map_check(self, tile_map, x, y):
		if (x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT):
			return
		if (tile_map[y][x] == 1 or tile_map[y][x] == 2):
			return
		tile_map[y][x] = 2
		for coord in ((0, -1), (-1, 0), (0, 1), (1, 0)):
			self.map_check(tile_map, x + coord[0], y + coord[1])
		for i in range(MAP_HEIGHT):
			for j in range(MAP_WIDTH):
				if (tile_map[i][j] == 0):
					return False
		return True

	def print_prompt(self):
		print("[{}] server> ".format(self.players_count), end='')

	def CommandInput(self):
		while True:
			# self.print_prompt()
			command = input()
			self.Exec(command)

	def Exec(self, command):
		if command == '':
			return
		if command == 'exit':
			exit()
		print("command: {}".format(command))

	def NextId(self):
		self.id += 1
		return self.id

	def Connected(self, channel, addr):
		self.AddPlayer(channel)
		if (self.players_count == 2):
			self.start_round()#self.next_turn()

	def next_turn(self):
		if (self.active_player_num == None):
			self.active_player_num = randint(0, 1)
		else:
			self.active_player_num += 1
			if (self.active_player_num == self.players_count):
				self.active_player_num = 0
		self.active_player = list(self.players.keys())[self.active_player_num].id
		self.SendToAll({'action': 'active_player',
							'id': self.active_player})

	def start_round(self):
		self.generate_tile_map()
		for player in self.players:
			x = randint(0, MAP_WIDTH - 1)
			y = randint(0, MAP_HEIGHT - 1)
			while (self.tile_map[y][x] != 0):
				x = randint(0, MAP_WIDTH - 1)
				y = randint(0, MAP_HEIGHT - 1)
			player.x = x
			player.y = y
			player.hp = 3
			if (player.freezed): self.unfreeze_player(player)
			player.Send({"action": "tile_map",
						"tile_map": self.tile_map})
		self.SendPlayers(force = True)
		self.active_player_num = None
		self.next_turn()

	def AddPlayer(self, player):
		print("{} {} connected".format(player.nickname, str(player.addr)))
		self.players[player] = True # {player_obj: True}
		self.players_count += 1
		player.Send({"action": "initial",
					"players": dict([(p.id, {"color":	p.color,
											"nickname":	p.nickname,
											"x":		p.x,
											"y":		p.y,
											"hp":		p.hp}) for p in self.players])})

		player.Send({"action": "get_id", "id": str(self.id)})
		self.SendPlayers()

		player.Send({"action": "tile_map",
					"tile_map": self.tile_map})

	def DelPlayer(self, player):
		print("{} {} deleted".format(player.nickname, str(player.addr)))
		self.players_count -= 1
		del self.players[player]
		self.SendPlayers()

	def SendPlayers(self, force = False):
		self.SendToAll({"action": "players",
						"force": force,
						"players": dict([(p.id, {"color":	p.color,
												"nickname": p.nickname,
												"x":		p.x,
												"y":		p.y,
												"hp":		p.hp}) for p in self.players])})

	def SendToAll(self, data):
		for i in self.players:
			i.Send(data)

	def Launch(self):
		while True:
			self.Pump()
			sleep(0.0001)


host = gethostbyname(gethostname())
port = "40327"#input("port: ")

s = GameServer(localaddr=(host, int(port)))
s.Launch()
