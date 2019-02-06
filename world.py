import tile
import api
import loader
import numpy

class World:
	def __init__(self, world):
		self.spawn_point = world['spawn_point']
		self.players = world['players']
		self.objects_from_dict(world['objects'])
		self.tile_map_from_dict(world['tile_map'])

	# -------- tiles ---------

	def tile_map_from_dict(self, tile_map):
		self.tile_map = numpy.empty(numpy.shape(tile_map), dtype=tile.Tile)
		self.height, self.width = self.tile_map.shape

		for y in range(self.height):
			for x in range(self.width):
				self.set_tile(x, y, tile_map[y][x]['id'], meta=tile_map[y][x]['meta'])

	def tile_map_to_dict(self):
		return [[tile.to_dict() for tile in row] for row in self.tile_map]

	def get_tile(self, x, y):
		return self.tile_map[y][x]

	def set_tile(self, x, y, id, meta=None):
		self.tile_map[y][x] = api.tile_classes[id](
			meta=meta)
		if (self.tile_map[y][x].on_init != None):
			self.tile_map[y][x].on_init(x, y, self.tile_map[y][x])
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
			self.spawn(
				objects[obj]['x'],
				objects[obj]['y'],
				objects[obj]['id'],
				meta=objects[obj]['meta'],
				uuid=obj)

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

	def spawn(self, x, y, object_id, meta=None, uuid=None):
		new_object = api.object_classes[object_id] (x, y, meta=meta, uuid=uuid)
		self.objects[new_object.uuid] = new_object
		if (new_object.on_init != None):
			new_object.on_init(new_object)
		if (api.on_server()):
			api.server.send_objects()
		return new_object.uuid

	def objects_update(self):
		for uuid in self.objects:
			if (self.get_object(uuid).update != None):
				self.get_object(uuid).update(self.get_object(uuid), api.delta_time)

	def add_player(self, player):
		self.players[player.nickname] = player.to_dict()
		self.objects[player.uuid] = player
		player.x = self.spawn_point[0]
		player.y = self.spawn_point[1]

	# --------- world ---------

	def to_dict(self):
		return {'spawn_point': self.spawn_point,
				'players': self.players,
				'tile_map': self.tile_map_to_dict(),
				'objects': self.objects_to_dict()}

	def save_as(self, name):
		world_dict = self.to_dict()

		for uuid in world_dict['objects']:
			obj = self.get_object(uuid)
			if (obj.id == 'default:player'):
				world_dict['players'][obj.nickname] = obj.to_dict()

		world_dict['objects'] = {uuid: world_dict['objects'][uuid] for uuid in world_dict['objects'] if world_dict['objects'][uuid]['id'] != 'default:player'}
		loader.save_world(world_dict, name)


def load(world_name):
	return World(loader.load_world(world_name))
