from PodSixNet.Connection import connection, ConnectionListener
from time import sleep, time as sys_time
#from game import Game
from socket import gethostname, gethostbyname
from fov import get_fov

#host = input("host IP address (leave blank for localhost): ")
#if host == "localhost" or host == '':
g_host = gethostbyname(gethostname())
g_port = 40327#input("port: ")

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

#print("Select color\nred    - 1\nblue   - 2\nyellow - 3\ncyan   - 4\npink   - 5\nviolet - 6")
#g_color = COLORS[int(input("color: ")) - 1]
#g_color = tuple(int(i) for i in input("color: ").split())
g_color = (255, 0, 255)

class Client(ConnectionListener):
	def __init__(self, game, host, port):
		self.game = game
		self.game.id = None
		self.Connect((host, port))
		connection.Send({"action": "nickname", "nickname": g_nickname})
		#connection.Send({"action": "color", "color": g_color})

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

	def end_turn(self):
		connection.Send({"action": "end_turn"})

	def set_tile(self, x, y, tile):
		connection.Send({"action": "set_tile", 'x': x, 'y': y, 'tile': tile})
		#self.game.tile_map[y][x] = tile

	def cast_magic(self, x, y, magic):
		connection.Send({"action": "cast_magic", 'x': x, 'y': y, 'magic': magic})

	def set_hp(self, hp):
		connection.Send({"action": "set_hp", "hp": hp})

	# ------------ Network callbacks ------------

#	def Network(self.game, data):
#		print('network:', data)

	def Network_initial(self, data):
		self.game.players = data['players']

	def Network_nickname(self, data):
		self.nickname = data["nickname"]

	#def Network_color(self, data):
	#	self.game.players[data["id"]]["color"] = data["color"]

	def Network_change_pos(self, data):
		# delta_time = self.game.clock.tick()
		print(self.game.objects)
		print(self.game.x, self.game.y)
		if (data['id'] == self.game.id):
			self.game.x += data['d_x']
			self.game.y += data['d_y']
		else:
			self.game.objects[data["id"]]["x"] += data["d_x"] # * delta_time
			self.game.objects[data["id"]]["y"] += data["d_y"] # * delta_time

	def Network_set_tile(self, data):
		self.game.tile_map[data['y']][data['x']] = data['tile']
		self.game.calc_fov()

	def Network_set_hp(self, data):
		if (self.game.id == data['id']):
			self.game.hp = data['hp']
		self.game.players[data['id']]['hp'] = data['hp']

	def Network_freeze(self, data):
		self.game.freezed = True

	def Network_unfreeze(self, data):
		self.game.freezed = False

	def Network_get_id(self, data):
		self.game.id = data["id"]

	def Network_active_player(self, data):
		self.game.active_player = data['id']
		if (self.game.active_player == self.game.id):
			self.game.turn_start_time = sys_time()
			self.game.ap = self.game.max_ap
			self.game.mp = self.game.max_mp

	def Network_players(self, data):
		self.game.playersLabel = str(len(data['players'])) + " players"
		mark = []
		self.game.x = data["players"][self.game.id]['x']
		self.game.y = data["players"][self.game.id]['y']
		self.game.calc_fov()
		self.game.hp = data["players"][self.game.id]['hp']
		if (data['force']):
			self.game.players = data['players']
			return
		for i in data['players']:
			if i not in self.game.players:
				self.game.players[i] = {'nickname': data["players"][i]["nickname"],
										"x":		data["players"][i]["x"],
										"y":		data["players"][i]["y"],
										"hp":		data["players"][i]["hp"]}

		for i in self.game.players:
			if i not in data['players'].keys():
				mark.append(i)

		for m in mark:
			del self.game.players[m]

	def Network_objects(self, data):
		self.game.objects = data
		#print(self.game.objects)

	def Network_tile_map(self, data):
		self.game.tile_map = data["tile_map"]
		self.game.map_width = len(data["tile_map"][0])
		self.game.map_height = len(data["tile_map"])
		self.game.calc_fov()

	def Network_turn_based(self, data):
		self.turn_based = data['turn_based']

	def Network_connected(self, data):
		self.game.statusLabel = "connected"

	def Network_error(self, data):
		print(data['error'])
		import traceback
		traceback.print_exc()
		self.game.statusLabel = data['error'][1]
		connection.Close()

	def Network_disconnected(self, data):
		self.game.statusLabel = "disconnected"

	def Launch(self):
		while True:
			self.game.Loop()
			sleep(0.0001)


#c = Client(host, int(port))
#c.Launch()
