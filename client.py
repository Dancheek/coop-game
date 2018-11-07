from PodSixNet.Connection import connection, ConnectionListener
from time import sleep, time as sys_time
#from game import Game
from socket import gethostname, gethostbyname
from fov import get_fov

#g_nickname = input("nickname: ")
#if g_nickname == '':
g_nickname = 'anon'

RED = (234, 22, 55)
BLUE = (23, 95, 232)
YELLOW = (241, 219, 23)
CYAN = (25, 208, 148)
PINK = (238, 122, 167)
VIOLET = (165, 53, 147)
COLORS = (RED, BLUE, YELLOW, CYAN, PINK, VIOLET)

class Client(ConnectionListener):
	def __init__(self, game, host, port):
		self.game = game
		self.game.id = None
		self.Connect((host, port))
		connection.Send({"action": "nickname", "nickname": g_nickname})

		self.game.players = {}
		self.turn_based = False
		#Game.__init__(self.game)

	def Loop(self):
		self.Pump()
		connection.Pump()
		#self.game.handle()
		#self.game.main()

	def change_pos(self, d_x, d_y):
		connection.Send({"action": "change_pos", "d_x": d_x, "d_y": d_y})

	def send_message(self, message):
		connection.Send({"action": "message", "message": message})

	def end_turn(self):
		connection.Send({"action": "end_turn"})

	def set_tile(self, x, y, tile):
		connection.Send({"action": "set_tile", 'x': x, 'y': y, 'tile': tile})
		#self.game.tile_map[y][x] = tile

	def cast_magic(self, x, y, magic):
		connection.Send({"action": "cast_magic", 'x': x, 'y': y, 'magic': magic})

	# ------------ Network callbacks ------------

#	def Network(self.game, data):
#		print('network:', data)

	def Network_initial(self, data):
		self.game.players = data['players']

	def Network_nickname(self, data):
		self.nickname = data["nickname"]

	#def Network_color(self, data):
	#	self.game.players[data["id"]]["color"] = data["color"]

	def Network_set_tile(self, data):
		self.game.tile_map[data['y']][data['x']] = data['tile']
		self.game.calc_fov()

	def Network_set_hp(self, data):
		if (self.game.id == data['id']):
			self.game.hp = data['hp']
		self.game.players[data['id']]['hp'] = data['hp']

	def Network_get_id(self, data):
		self.game.id = data["id"]

	def Network_active_player(self, data):
		self.game.active_player = data['id']
		if (self.game.active_player == self.game.id):
			self.game.turn_start_time = sys_time()
			self.game.stats['mana'] = self.game.stats_max['mana']
			self.game.stats['action'] = self.game.stats_max['action']

	def Network_objects(self, data):
		self.game.objects = data['objects']
		#print(self.game.objects)

	def Network_self(self, data):
		self.game.x = data['x']
		self.game.y = data['y']
		self.game.stats = data['stats']
		self.game.calc_fov()

	def Network_message(self, data):
		self.game.messages.append(data['message'])

	def Network_tile_map(self, data):
		self.game.tile_map = data["tile_map"]
		self.game.map_width = len(data["tile_map"][0])
		self.game.map_height = len(data["tile_map"])
		self.game.calc_fov()

	def Network_turn_based(self, data):
		self.turn_based = data['turn_based']

	def Network_connected(self, data):
		print('connected')
		self.game.on_connect()

	def Network_error(self, data):
		print(data['error'])
		self.game.connecting = False
		self.game.send_message('!> ' + str(data['error']))
		connection.Close()

	def Network_disconnected(self, data):
		self.game.connected = False

	def Launch(self):
		while True:
			self.game.Loop()
			sleep(0.0001)


#c = Client(host, int(port))
#c.Launch()
