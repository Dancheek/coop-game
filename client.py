from PodSixNet.Connection import connection, ConnectionListener
from time import sleep, time as sys_time
from socket import gethostname, gethostbyname
from fov import get_fov

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
		self.game.uuid = None
		self.Connect((host, port))
		self.connection = connection
		self.connection.Send({'action': 'join', 'nickname': game.nickname})

	def loop(self):
		self.Pump()
		self.connection.Pump()

	def change_pos(self, d_x, d_y):
		self.connection.Send({"action": "change_pos", "d_x": d_x, "d_y": d_y})

	def send_message(self, message):
		self.connection.Send({"action": "message", "message": message})

	def end_turn(self):
		self.connection.Send({"action": "end_turn"})

	def set_tile(self, x, y, tile):
		self.connection.Send({"action": "set_tile", 'x': x, 'y': y, 'tile': tile})

	def cast_magic(self, x, y, magic):
		self.connection.Send({"action": "cast_magic", 'x': x, 'y': y, 'magic': magic})

	def interact(self, x, y):
		self.connection.Send({'action': 'interact', 'x': x, 'y': y})

	# ------------ Network callbacks ------------

	#def Network(self, data):
	#	print('network:', data)

	def Network_set_tile(self, data):
		self.game.world.set_tile(data['x'], data['y'], data['tile'])
		self.game.calc_fov()

	def Network_objects(self, data):
		objs = data['objects']
		for obj in objs:
			if (obj in self.game.world.objects):
				self.game.world.get_object(obj).from_dict(objs[obj])
			else:
				self.game.world.objects[obj] = self.game.object_classes[objs[obj]['id']](objs[obj])

	def Network_del_object(self, data):
		del self.game.world.objects[data['object']]

	def Network_self(self, data):
		self.game.uuid = data['uuid']
		self.game.x = data['x']
		self.game.y = data['y']
		self.game.stats = data['stats']
		self.game.calc_fov()

	def Network_message(self, data):
		self.game.add_message(data['message']['text'], data['message']['color'])

	def Network_world(self, data):
		self.game.load_world_from_dict(data['world'])

	def Network_turn_based(self, data):
		self.turn_based = data['turn_based']

	def Network_connected(self, data):
		self.game.on_connect()

	def Network_error(self, data):
		if (self.game.connecting or self.game.connected):
			self.game.connecting = False
			if (type(data['error']) == ConnectionRefusedError):
				self.game.send_message('[{}] {}'.format(data['error'].errno, data['error'].strerror), color=(255, 50, 70))
			else:
				self.game.send_message('[{}] {}'.format(*data['error']), color=(255, 50, 70))
			connection.Close()

	def Network_disconnected(self, data):
		if (self.game.connected):
			self.game.on_disconnect()

