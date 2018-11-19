from tile import Tile
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

def server_cast_magic(root, target, magic, x, y):
	if (target == None):
		api.server.send_message(f'!!> x: {x}, y: {y}', player=root)
	else:
		api.server.send_message(f'!!> hit {target.nickname} with {magic}', player=root)
		api.server.send_message(f'!!> hitted by {root.nickname} with {magic}', player=target)

def server_on_connect(root):
	api.server.send_message('#> Hi there', player=root, color=(255, 255, 0))


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


tiles = {'default:wall': Tile,
		'default:floor': TileFloor,
		'default:door': TileDoor}

def command_load_world(*args):
	if (len(args) != 2):
		api.send_message('Usage: /load_world <world name>', color=api.RED)
	else:
		api.game.load_world(args[1])
		api.send_message(f'World "{args[1]}" loaded', color=api.YELLOW)

def command_save_world(*args):
	if (len(args) != 2):
		api.send_message('Usage: /save_world <world name>', color=api.RED)
	else:
		api.game.save_world(args[1])
		api.send_message(f'World saved as "{args[1]}"', color=api.YELLOW)

chat_commands = {'load_world': command_load_world,
				 'save_world': command_save_world}

