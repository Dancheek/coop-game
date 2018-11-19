import tile
import api

class World:
	def __init__(self, tile_map):
		self.tile_map = tile_map
		self.map_width = len(tile_map[0])
		self.map_height = len(tile_map)

	def get_tile(self, x, y):
		return self.tile_map[y][x]

	def from_dict(self, d, tiles):
		pass

	def to_dict(self):
		return [[tile.to_dict() for tile in row] for row in self.tile_map]

	def is_outside(self, x, y):
		if (x < 0):					return True
		if (x >= self.map_width):	return True
		if (y < 0):					return True
		if (y >= self.map_height):	return True
		return False

