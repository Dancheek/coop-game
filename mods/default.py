import api

name		= "default"
version		= '0.4.1'
description	= "Default content of game"

api.register_images({
	'default:player'		: 'eJxjYCAM/uMAyPLY9KCzkfXhkyfGfFLchw8AAJMQX6E=',
	'default:object'		: 'eJxjYCAM/iMAAxRDOJjyKABJHpsaBhLkCZmP1334AAAQrId5',

	'default:tile'			: 'eJyztrb+b42Ed+7ciYKtaSxPb/vQ5QHBQ5tB',
	'default:wall'			: 'eJxraGj43wDFxcXFcDYIFxUVgcXwYZi6BhzmEKMf2T50c4jRj24OsfaD7AMAKl+ZnQ==',
	'default:floor'			: 'eJwzNTX9bwrFDg4OKBhZDJsaGB9ZDhsbmz50s/Gx8cmjq0G3k5DZANg1a+M=',
	'default:door_closed'	: 'eJxraGj4n+AihxUXFRX9Ly4uBrNLQjRRMEgMJNcA1Y9NHiRHjn5NTYQ8Le0H+Q8Ac+B/Qw==',
	'default:door_opened'	: 'eJxraGj4n+AiB8YODg4ouKio6H9xcTFYriRE87+pqSmKPEiuAaofJA8SA6mBqQPJIeuH6YOpwaUf2Xx0/ejyuOwHYXT7kfWC2CD/AQA5lXoS',
	'default:chest'			: 'eJxLcJH7n0AAl4RoYsXEysOwpqYmGOMyHyZPqvmUyAMANNJ1Yw==',

	'default:selection'		: 'eJz7//9/w38gNjAwYEDG/6Hi2OSQ1eCSoxcm5D5cfoCJAwDMKUcd'})

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

api.register_tile('default:wall', {})


api.register_tile('default:floor', {
	'is_wall': False,
	'blocks_view': False
})


def door_on_init(x, y, tile):
	if (tile.meta['closed']):
		tile.is_wall = True
		tile.blocks_view = True
		tile.image = 'default:door_closed'
	else:
		tile.is_wall = False
		tile.blocks_view = False
		tile.image = 'default:door_opened'

def door_on_interact(x, y, tile, player):
	if (tile.meta['closed']):
		tile.meta['closed'] = False
		tile.is_wall = False
		tile.blocks_view = False
		tile.image = 'default:door_opened'
	else:
		tile.meta['closed'] = True
		tile.is_wall = True
		tile.blocks_view = True
		tile.image = 'default:door_closed'

def door_on_try_to_step(x, y, tile, obj):
	if (tile.meta['closed']):
		door_on_interact(x, y, tile, obj)

api.register_tile('default:door', {
	'is_wall': True,
	'blocks_view': True,
	'image': 'default:door_closed',

	'on_init': door_on_init,
	'on_interact': door_on_interact,
	'on_try_to_step': door_on_try_to_step,

	'meta': {
		'closed': True
	}
})


def chest_on_init(x, y, tile):
	if (tile.meta.get('storage') != None):
		storage = tile.meta['storage']
		tile.meta['storage'] = api.create_storage(27)
		tile.meta['storage'].from_dict(storage)
	else:
		tile.meta['storage'] = api.create_storage(27)

def chest_on_interact(x, y, tile, player):
	api.open_form('default:chest_form', storages={'chest_storage': (x, y)}, player=player)

api.register_tile('default:chest', {
	'is_wall': True,
	'blocks_view': False,

	'on_init': chest_on_init,
	'on_interact': chest_on_interact,
	'on_try_to_step': chest_on_interact
})

# --------------- objects ---------------

api.register_object('default:object', {})


def walking_on_init(obj):
	obj.meta['dir'] = 1

def walking_update(obj, dtime):
	if (api.world.get_tile(*obj.get_rel(api.DIRECTIONS[obj.meta['dir']])).is_wall):
		obj.meta['dir'] += 1
		if (obj.meta['dir'] >= len(api.DIRECTIONS)):
			obj.meta['dir'] = 0
	if (obj.is_moving):
		obj.add_move_progress(obj.speed * dtime)
	else:
		obj.move_to(obj.get_rel(api.DIRECTIONS[obj.meta['dir']]))

api.register_object('test:walking', {
	'image': 'default:object',
	'speed': 4,

	'on_init': walking_on_init,
	'update': walking_update
})

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


def command_tp(*args, player=None):
	if (len(args) != 3):
		api.send_message('Usage: /tp <x> <y>', color=api.RED, player=player)
	else:
		player.set_pos(int(args[1]), int(args[2]))


def command_world_spawnpoint(*args, player=None):
	if (len(args) == 1):
		api.world.spawn_point = (player.x, player.y)
		api.send_message(f'World\'s spawn point has been set at ({player.x}, {player.y})', color=api.WHITE, player=player)
	elif (len(args) == 3):
		api.world.spawn_point = (int(args[1]), int(args[2]))
		api.send_message(f'World\'s spawn point has been set at ({args[1]}, {args[2]})', color=api.WHITE, player=player)
	else:
		api.send_message('Usage: /world_spawnpoint - set world spawnpoint to player position', color=api.RED, player=player)
		api.send_message('/world_spawnpoint <x> <y> - set world spawnpoint to (x, y)', color=api.RED, player=player)


api.register_chat_command('spawn', command_spawn)
api.register_chat_command('settile', command_settile)
api.register_chat_command('tp', command_tp)
api.register_chat_command('world_spawnpoint', command_world_spawnpoint)

# ---------------- forms --------------

api.register_form('default:player_menu_form', {
	'size': (9, 5),
	'elements': {
		'title': {
			'type': 'label',
			'text': 'Inventory',
			'pos': (0, 0),
			'size': (9, 1),
			'align_x': 'left'
		},
		'player_inventory': {
			'type': 'storage_view',
			'pos': (0, 1),
			'size': (9, 4),
			'storage': 'player'
		}
	}
})


api.register_form('default:chest_form', {
	'size': (9, 9),
	'elements': {
		'chest_title': {
			'type': 'label',
			'text': 'Chest',
			'pos': (0, 0),
			'size': (9, 1),
			'align_x': 'left'
		},
		'chest_storage': {
			'type': 'storage_view',
			'pos': (0, 1),
			'size': (9, 3),
			'storage': None
		},
		'player_inventory_title': {
			'type': 'label',
			'text': 'Inventory',
			'pos': (0, 4),
			'size': (9, 1),
			'align_x': 'left'
		},
		'player_inventory': {
			'type': 'storage_view',
			'pos': (0, 5),
			'size': (9, 4),
			'storage': 'player'
		}
	}
})


def continue_button_on_click(btn):
	api.game.set_form(None)

def exit_button_on_click(btn):
	api.exit()

def disconnect_button_on_click(btn):
	if (api.game.connected):
		api.game.disconnect()

def disconnect_button_update(btn):
	if (btn.inactive and api.game.connected):
		btn.inactive = False
	elif (not btn.inactive and not api.game.connected):
		btn.inactive = True

api.register_form('default:escape_menu', {
	'size': (10, 8.5),
	'background': (32, 32, 32),
	'elements': {
		'pause_label': {
			'type': 'label',
			'text': 'Pause',
			'pos': (0, 0),
			'size': (10, 1)
		},
		'continue_button': {
			'type': 'button',
			'text': 'continue',
			'pos': (0, 1),
			'size': (10, 1.5),
			'on_click': continue_button_on_click
		},
		'settings_button': {
			'type': 'button',
			'text': 'settings',
			'pos': (0, 3),
			'size': (10, 1.5),
			'inactive': True
		},
		'disconnect_button': {
			'type': 'button',
			'text': 'disconnect',
			'pos': (0, 5),
			'size': (10, 1.5),
			'on_click': disconnect_button_on_click,
			'inactive': True,
			'update': disconnect_button_update
		},
		'exit_button': {
			'type': 'button',
			'text': 'exit',
			'pos': (0, 7),
			'size': (10, 1.5),
			'on_click': exit_button_on_click
		}
	}
})
