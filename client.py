from PodSixNet.Connection import connection, ConnectionListener
from time import sleep, time
from game import Game
from pygame.time import Clock
from socket import gethostname, gethostbyname

host = input("host IP address (leave blank for localhost): ")
if host == "localhost" or host == '':
	host = gethostbyname(gethostname())
port = "40327"#input("port: ")

#g_nickname = input("nickname: ")
#if g_nickname == '':
g_nickname = 'anon'

RED = (234, 22, 55)
BLUE = (23, 95, 232)
YELLOW = (241, 219, 23)
CYAN = (25, 208, 148)
PINK = (238, 122, 167)
COLORS = (RED, BLUE, YELLOW, CYAN, PINK)

print("Select color\nred    - 1\nblue   - 2\nyellow - 3\ncyan   - 4\npink   - 5")
g_color = COLORS[int(input("color: ")) - 1]
#g_color = tuple(int(i) for i in input("color: ").split())
# g_color = (255, 0, 255)

class Client(ConnectionListener, Game):
	def __init__(self, host, port):
		self.id = None
		self.Connect((host, port))
		connection.Send({"action": "nickname", "nickname": g_nickname})
		connection.Send({"action": "color", "color": g_color})

		self.players = {}
		self.clock = Clock()
		self.color = g_color
		Game.__init__(self)

	def Loop(self):
		self.Pump()
		connection.Pump()
		self.handle()
		self.main(self.players)

	def change_pos(self, d_x, d_y):
		connection.Send({"action": "change_pos", "d_x": d_x, "d_y": d_y})
		self.x += d_x
		self.y += d_y
		# print("change_pos", x, y)

	def end_turn(self):
		connection.Send({"action": "end_turn"})

	def set_tile(self, x, y, tile):
		connection.Send({"action": "set_tile", 'x': x, 'y': y, 'tile': tile})
		self.tile_map[y][x] = tile

	# ------------ Network callbacks ------------

#	def Network(self, data):
#		print('network:', data)

	def Network_initial(self, data):
		self.players = data['players']

	def Network_nickname(self, data):
		self.players[data["id"]]["nickname"] = data["nickname"]

	def Network_color(self, data):
		self.players[data["id"]]["color"] = data["color"]

	def Network_change_pos(self, data):
		# delta_time = self.clock.tick()
		self.players[data["id"]]["x"] += data["d_x"] # * delta_time
		self.players[data["id"]]["y"] += data["d_y"] # * delta_time

	def Network_set_tile(self, data):
		self.tile_map[data['y']][data['x']] = data['tile']

	def Network_get_id(self, data):
		self.id = data["id"]

	def Network_active_player(self, data):
		self.active_player = data['id']
		print(self.active_player, self.id)
		if (self.active_player == self.id):
			self.made_step = False
			self.magic_casted = False

	def Network_players(self, data):
		# print(data)
		self.playersLabel = str(len(data['players'])) + " players"
		mark = []
		self.x = data["players"][self.id]['x']
		self.y = data["players"][self.id]['y']
		self.hp = data["players"][self.id]['hp']

		for i in data['players']:
			if i not in self.players:
				self.players[i] = {'color':		data['players'][i]["color"],
									'nickname':	data["players"][i]["nickname"],
									"x":		data["players"][i]["x"],
									"y":		data["players"][i]["y"],
									"hp":		data["players"][i]["hp"]}

		for i in self.players:
			if i not in data['players'].keys():
				mark.append(i)

		for m in mark:
			del self.players[m]

	def Network_tile_map(self, data):
		self.tile_map = data["tile_map"]

	def Network_connected(self, data):
		self.statusLabel = "connected"

	def Network_error(self, data):
		print(data['error'])
		#import traceback
		#traceback.print_exc()
		#self.statusLabel = data['error'][1]
		connection.Close()

	def Network_disconnected(self, data):
		self.statusLabel = "disconnected"

	def Launch(self):
		while True:
			self.Loop()
			sleep(0.0001)


c = Client(host, int(port))
c.Launch()
