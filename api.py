from pygame.locals import *
from sys import exit
import pygame.font
import tile
import object
import item

WHITE = (255, 255, 255)
GREY = (167, 167, 167)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)
RED = (255, 50, 70)

DIRECTIONS = ((0, -1), (-1, 0), (0, 1), (1, 0))


screen = None

game = None
server = None

world = None


send_message = None
send_message_to_all = None

exec_chat_command = None

images = {}

tile_classes = {}
object_classes = {'default:player': object.Player}

chat_commands = {}

forms = {}

delta_time = 0


def register_image(name, data):
	if (not on_server()):
		import image
		global images
		images[name] = image.from_str(data)

def register_images(data):
	if (on_server):
		for img in data:
			register_image(img, data[img])


def register_tile(name, data):
	global tile_classes
	class registered_tile(tile.Tile):
		def __init__(self, meta=None):
			super().__init__(name, data, meta)
		def __str__(self):
			return f'<tile, id: {name} at {hex(id(self))}>'
	tile_classes[name] = registered_tile


def register_object(name, data):
	global object_classes
	class registered_object(object.BaseObject):
		def __init__(self, x, y, meta=None, uuid=None):
			super().__init__(x, y, name, data, meta, uuid)
		def __str__(self):
			return f'<object, id: {name}, (x: {x}, y: {y})>'
	object_classes[name] = registered_object


def create_form(data, name=None):
	if (on_server()): return
	import gui
	class registered_form(gui.Form):
		def __init__(self):
			if (name != None):
				self.id = name
			super().__init__(data)
		def __str__(self):
			return f'<form, id: {name}>'
	form = registered_form()
	return form

def register_form(name, data):
	if (on_server()): return
	forms[name] = create_form(data, name=name)

def open_form(form_id, storages={}, player=None):
	if (on_server()):
		player.Send({
			'action': 'open_form',
			'form_id': form_id,
			'storages': storages
		})
	else:
		game.set_form(form_id)
		for e in game.current_form.elements:
			elem_name = game.current_form.get_element(e).name
			if (elem_name in storages):
				game.current_form.get_element(e).storage = get_tile_storage(storages[elem_name])


def register_chat_command(name, data):
	global chat_commands
	chat_commands[name] = data


def create_storage(size):
	return item.Storage(size)

def get_tile_storage(pos):
	return world.get_tile(*pos).meta.get('storage')


def save_config():
	global config
	config.write(open('config', 'w'))


def on_server():
	global server
	return (server != None)
