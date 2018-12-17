import tile
import api
import loader

class World:
	def __init__(self, world):
		self.players = world['players']
		self.objects_from_dict(world['objects'])
		self.tile_map_from_dict(world['tile_map'])

	# -------- tiles ---------

	def tile_map_from_dict(self, tile_map):
		self.tile_map = tile_map
		self.width = len(self.tile_map[0])
		self.height = len(self.tile_map)
		for y in range(self.height):
			for x in range(self.width):
				self.tile_map[y][x] = api.tile_classes[tile_map[y][x]['id']] (tile_map[y][x])

	def tile_map_to_dict(self):
		return [[tile.to_dict() for tile in row] for row in self.tile_map]

	def get_tile(self, x, y):
		return self.tile_map[y][x]

	def set_tile(self, x, y, tile):
		if (type(tile) == dict):
			self.tile_map[y][x] = api.tile_classes[tile['id']](tile)
		else:
			self.tile_map[y][x] = api.tile_classes[tile](x, y)
		if (api.on_server()):
			api.server.update_tile(x, y)

	def is_outside(self, x, y):
		if (x < 0):					return True
		if (x >= self.width):		return True
		if (y < 0):					return True
		if (y >= self.height):		return True
		return False

	# ------- objects --------

	def objects_from_dict(self, objects):
		self.objects = {}
		for obj in objects:
			self.objects[obj] = api.object_classes[objects[obj]['id']] (objects[obj])

	def objects_to_dict(self):
		return {self.objects[obj].uuid: self.objects[obj].to_dict() for obj in self.objects}

	def get_object(self, uuid):
		return self.objects[uuid]

	def get_object_by_pos(self, x, y):
		for uuid in self.objects:
			obj = self.get_object(uuid)
			if (obj.x == x and obj.y == y):
				return obj
		return None

	def spawn(self, x, y, object_id):
		new_object = api.object_classes[object_id] (x, y)
		self.objects[new_object.uuid] = new_object
		if (api.on_server()):
			api.server.send_objects()
		return new_object.uuid

	def objects_update(self):
		for uuid in self.objects:
			self.get_object(uuid).update()

	def add_player(self, player):
		self.players[player.nickname] = player.to_dict()
		self.objects[player.uuid] = player

	# --------- world ---------

	def to_dict(self):
		for uuid in self.objects:
			obj = self.get_object(uuid)
			if (obj.id == 'default:player'):
				self.players[obj.nickname] = obj.to_dict()

		return {'players': self.players,
				'tile_map': self.tile_map_to_dict(),
				'objects': self.objects_to_dict()}

	def save_as(self, name):
		loader.save_world(self.to_dict(), name)


def load(world_name):
	return World(loader.load_world(world_name))
