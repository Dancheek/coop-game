import tile
import api
import loader

class World:
	def __init__(self, tile_map, tiles):
		self.map_width = len(tile_map[0])
		self.map_height = len(tile_map)
		self.from_dict(tile_map, tiles)

	def get_tile(self, x, y):
		return self.tile_map[y][x]

	def from_dict(self, d, tiles):
		for y in range(self.height):
			for x in range(self.width):
				pass
		pass

	def to_dict(self):
		return [[tile.to_dict() for tile in row] for row in self.tile_map]

	def is_outside(self, x, y):
		if (x < 0):					return True
		if (x >= self.map_width):	return True
		if (y < 0):					return True
		if (y >= self.map_height):	return True
		return False


def load(world_name):
	pass
