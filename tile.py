import api

class Tile:
	def __init__(self, *args):
		if (len(args) == 1 and type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.id = args[0]
			self.x = args[1]
			self.y = args[2]
		self.image = self.id
		self.is_wall = True
		self.blocks_view = True

	def on_step(self, player):
		pass

	def on_try_to_step(self, player):
		pass

	def interact(self, player):
		pass

	def from_dict(self, d):
		self.id = d['id']
		self.x = d['x']
		self.y = d['y']

	def to_dict(self):
		return {'id'	: self.id,
				'x'		: self.x,
				'y'		: self.y}

def from_dict(tile_map, tiles):
	return [[tiles[tile['id']](tile) for tile in row] for row in tile_map]

def to_dict(tile_map):
	return [[tile.to_dict() for tile in row] for row in tile_map]
