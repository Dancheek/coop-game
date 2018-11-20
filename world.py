import tile
import api
import loader

class World:
	def __init__(self, tile_map):
		self.width = len(tile_map[0])
		self.height = len(tile_map)
		self.from_dict(tile_map)

	def get_tile(self, x, y):
		return self.tile_map[y][x]

	def set_tile(self, x, y, tile):
		self.tile_map[y][x] = api.tiles[tile['id']](tile)

	def from_dict(self, d):
		self.tile_map = d
		for y in range(self.height):
			for x in range(self.width):
				self.tile_map[y][x] = api.tiles[d[y][x]['id']](d[y][x])

	def to_dict(self):
		return [[tile.to_dict() for tile in row] for row in self.tile_map]

	def save_as(self, name):
		loader.save_world(self.to_dict(), name)

	def is_outside(self, x, y):
		if (x < 0):					return True
		if (x >= self.width):		return True
		if (y < 0):					return True
		if (y >= self.height):		return True
		return False


def load(world_name):
	return World(loader.load_world(world_name))
