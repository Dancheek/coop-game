from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from weakref import WeakKeyDictionary
from time import sleep
from socket import gethostbyname, gethostname
from _thread import start_new_thread
from pygame.time import Clock
from random import randint

MAP_WIDTH = 12
MAP_HEIGHT = 10
WALLS_COUNT = 30

class ServerChannel(Channel):
	def __init__(self, *args, **kwargs):
		Channel.__init__(self, *args, **kwargs)
		self.id = str(self._server.NextId())
		self.nickname = None
		self.x = randint(0, MAP_WIDTH - 1)
		self.y = randint(0, MAP_HEIGHT - 1)
		while (self._server.tile_map[self.y][self.x] != 0):
				self.x = randint(0, MAP_WIDTH - 1)
				self.y = randint(0, MAP_HEIGHT - 1)
		self.hp = 3
		self.color = (50, 50, 50)

	def PassOn(self, data):
		"""pass on what we received to all connected clients"""
		data.update({"id": self.id})
		self._server.SendToAll(data)

	# ------------- Client changing ---------------

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

	def Network_set_tile(self, data):
		if (self.id == self._server.active_player):
			self._server.tile_map[data['y']][data['x']] = data['tile']
			self.PassOn(data)

	# ---------------------------------------------

	def Network_end_turn(self, data):
		if (self.id == self._server.active_player):
			self._server.next_turn()

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
			self.next_turn()

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

	def SendPlayers(self):
		self.SendToAll({"action": "players",
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
