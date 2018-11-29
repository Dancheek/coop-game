from tile import Tile
from object import Object
import api

name		= "default"
version		= '0.0.1'
description	= "Default content of game"

images = {'default:player'			: 'eJxjYCAM/uMAyPLY9KCzkfXhkyfGfFLchw8AAJMQX6E=',
			'default:wall'			: 'eJxraGj43wDFxcXFcDYIFxUVgcXwYZi6BhzmEKMf2T50c4jRj24OsfaD7AMAKl+ZnQ==',
			'default:floor'			: 'eJwzNTX9bwrFDg4OKBhZDJsaGB9ZDhsbmz50s/Gx8cmjq0G3k5DZANg1a+M=',
			'default:door_closed'	: 'eJxraGj4n+AihxUXFRX9Ly4uBrNLQjRRMEgMJNcA1Y9NHiRHjn5NTYQ8Le0H+Q8Ac+B/Qw==',
			'default:door_opened'	: 'eJxraGj4n+AiB8YODg4ouKio6H9xcTFYriRE87+pqSmKPEiuAaofJA8SA6mBqQPJIeuH6YOpwaUf2Xx0/ejyuOwHYXT7kfWC2CD/AQA5lXoS',
			'default:object'		: 'eJxjYCAM/iMAAxRDOJjyKABJHpsaBhLkCZmP1334AAAQrId5',
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
	api.server.send_message('#> Hi there', player=player, color=(255, 255, 0))

# --------------- tiles ----------------

class TileFloor(Tile):
	def __init__(self, *args):
		super().__init__(*args)
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		self.is_wall = False
		self.blocks_view = False


class TileDoor(Tile):
	def __init__(self, *args):
		super().__init__(*args)
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.closed = True
			self.image = 'default:door_closed'

	def on_try_to_step(self, player):
		if (self.closed):
			return self.interact(player)

	def interact(self, player):
		if (self.closed):
			self.closed = False
			self.image = 'default:door_opened'
			self.is_wall = False
			self.blocks_view = False
		else:
			self.closed = True
			self.image = 'default:door_closed'
			self.is_wall = True
			self.blocks_view = True
		return True

	def to_dict(self):
		d = super().to_dict()
		d.update({'image': self.image,
					'closed': self.closed})
		return d

	def from_dict(self, d):
		super().from_dict(d)
		self.image = d['image']
		self.closed = d['closed']
		self.is_wall = self.closed
		self.blocks_view = self.closed


tile_classes = {'default:wall': Tile,
				'default:floor': TileFloor,
				'default:door': TileDoor}

# --------------- objects ---------------

class ObjectPlayer(Object):
	def __init__(self, *args):
		super().__init__(*args)
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		self.image = 'default:player'

object_classes = {'default:object': Object,
					'default:player': ObjectPlayer}

# --------------- commands ---------------

def command_spawn(*args, player=None):
	if (len(args) != 4):
		api.send_message('Usage: /spawn <x> <y> <object_id>', color=api.RED, player=player)
	else:
		api.world.spawn(int(args[1]), int(args[2]), args[3])
		api.send_message(f'Object spawned at {args[1]} {args[2]}', player=player)

def command_settile(*args, player=None):
	if (len(args) != 4):
		api.send_message('Usage: /settile <x> <y> <tile_id>', color=api.RED, player=player)
	else:
		api.world.set_tile(int(args[1]), int(args[2]), args[3])
		api.send_message(f'Tile placed at {args[1]} {args[2]}', player=player)

chat_commands = {'spawn': command_spawn,
				 'settile': command_settile}

