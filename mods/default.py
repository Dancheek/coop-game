from tile import Tile
from object import BaseObject, Player
import api

name		= "default"
version		= '0.0.1'
description	= "Default content of game"

images = {'default:player'			: 'eJxjYCAM/uMAyPLY9KCzkfXhkyfGfFLchw8AAJMQX6E=',
			'default:object'		: 'eJxjYCAM/iMAAxRDOJjyKABJHpsaBhLkCZmP1334AAAQrId5',

			'default:tile'			: 'eJyztrb+b42Ed+7ciYKtaSxPb/vQ5QHBQ5tB',
			'default:wall'			: 'eJxraGj43wDFxcXFcDYIFxUVgcXwYZi6BhzmEKMf2T50c4jRj24OsfaD7AMAKl+ZnQ==',
			'default:floor'			: 'eJwzNTX9bwrFDg4OKBhZDJsaGB9ZDhsbmz50s/Gx8cmjq0G3k5DZANg1a+M=',
			'default:door_closed'	: 'eJxraGj4n+AihxUXFRX9Ly4uBrNLQjRRMEgMJNcA1Y9NHiRHjn5NTYQ8Le0H+Q8Ac+B/Qw==',
			'default:door_opened'	: 'eJxraGj4n+AiB8YODg4ouKio6H9xcTFYriRE87+pqSmKPEiuAaofJA8SA6mBqQPJIeuH6YOpwaUf2Xx0/ejyuOwHYXT7kfWC2CD/AQA5lXoS',

			'default:selection'		: 'eJz7//9/w38gNjAwYEDG/6Hi2OSQ1eCSoxcm5D5cfoCJAwDMKUcd'}

stats = {'health'	: 3,
		'mana'		: 2,
		'action'	: 4,
		'active'	: True}

stats_max = {'health'	: 3,
			'mana'		: 2,
			'action'	: 4}

bars = {'health': {'color'	: (243, 16, 76),
					'max'	: 3},

		'mana'	: {'color'	: (15, 121, 222),
					'max'	: 2},

		'action': {'color'	: (243, 205, 48),
					'max'	: 4}}


def server_main():
	pass

def server_cast_magic(player, target, magic, x, y):
	if (target == None):
		api.server.send_message(f'!!> x: {x}, y: {y}', player=player)
	else:
		api.server.send_message(f'!!> hit {target.nickname} with {magic}', player=player)
		api.server.send_message(f'!!> hitted by {player.nickname} with {magic}', player=target)

def server_on_connect(player):
	api.server.send_message(f'Welcome to the server, {player.nickname}!', player=player, color=api.GREY)

# --------------- tiles ----------------

class TileWall(Tile):
	def __init__(self, *args):
		self.id = 'default:wall'
		super().__init__(*args)


class TileFloor(Tile):
	def __init__(self, *args):
		self.id = 'default:floor'
		super().__init__(*args)
		self.is_wall = False
		self.blocks_view = False


class TileDoor(Tile):
	def __init__(self, *args):
		self.id = 'default:door'
		super().__init__(*args)
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.closed = True

		if (self.closed):
			self.close()
		else:
			self.open()

	def on_try_to_step(self, player):
		if (self.closed):
			return self.interact(player)

	def interact(self, player):
		if (self.closed):
			self.open()
		else:
			self.close()
		return True

	def to_dict(self):
		d = super().to_dict()
		d.update({'closed': self.closed})
		return d

	def open(self):
		self.closed = False
		self.image = 'default:door_opened'
		self.is_wall = False
		self.blocks_view = False

	def close(self):
		self.closed = True
		self.image = 'default:door_closed'
		self.is_wall = True
		self.blocks_view = True


tile_classes = {'default:wall': TileWall,
				'default:floor': TileFloor,
				'default:door': TileDoor}

# --------------- objects ---------------

class Walking(BaseObject):
	def __init__(self, *args):
		self.id = 'custom:walking'
		super().__init__(*args)
		self.image = 'default:object'
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.direction = 0
		self.speed = 4
		self.time_for_move = 1000 / self.speed
		self.time_from_move = 0

	def to_dict(self):
		d = super().to_dict()
		d.update({'direction': self.direction})
		return d

	def update(self):
		if (api.world.get_tile(*self.get_rel(api.DIRECTIONS[self.direction])).is_wall):
			self.direction += 1
			if (self.direction >= len(api.DIRECTIONS)):
				self.direction = 0
		else:
			self.time_from_move += api.delta_time
			if (self.time_from_move >= self.time_for_move):
				self.time_from_move -= self.time_for_move
				self.set_pos(*self.get_rel(api.DIRECTIONS[self.direction]))



object_classes = {'default:object': BaseObject,
					'default:player': Player,
					'custom:walking': Walking}

# --------------- commands ---------------

def command_spawn(*args, player=None):
	if (len(args) != 4):
		api.send_message('Usage: /spawn <x> <y> <object_id>', color=api.RED, player=player)
	else:
		try:
			api.world.spawn(int(args[1]), int(args[2]), args[3])
			api.send_message(f'Object spawned at {args[1]} {args[2]}', player=player)
		except KeyError:
			api.send_message(f'Invalid id - {args[3]}', player=player, color=api.RED)

def command_settile(*args, player=None):
	if (len(args) != 4):
		api.send_message('Usage: /settile <x> <y> <tile_id>', color=api.RED, player=player)
	else:
		api.world.set_tile(int(args[1]), int(args[2]), args[3])
		api.send_message(f'Tile placed at {args[1]} {args[2]}', player=player)

def command_hit(*args, player=None):
	api.send_message_to_all('-1 HP for all objects', color=api.YELLOW)
	for uuid in api.world.objects:
		api.world.objects[uuid].hit()

def command_tp(*args, player=None):
	if (len(args) != 3):
		api.send_message('Usage: /tp <x> <y>', color=api.RED, player=player)
	else:
		player.set_pos(int(args[1]), int(args[2]))

chat_commands = {'spawn': command_spawn,
					'settile': command_settile,
					'hit': command_hit,
					'tp': command_tp}

