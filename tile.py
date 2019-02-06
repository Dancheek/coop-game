import api

class Tile:
	def __init__(self, id, data, meta=None):
		self.id = id
		self.image = data.get('image', self.id)

		self.is_wall = data.get('is_wall', True)
		self.blocks_view = data.get('blocks_view', True)
		if (meta != None):
			self.meta = meta
		else:
			self.meta = data.get('meta', {}).copy()

		self.on_init = data.get('on_init')

		self.on_step = data.get('on_step')

		self.on_try_to_step = data.get('on_try_to_step')

		self.on_interact = data.get('on_interact')

	def from_dict(self, d):
		for i in d['meta']:
			if (i == 'storage'):
				self.meta['storage'].from_dict(d['meta']['storage'])
			else:
				self.meta[i] = d['meta'][i]
		for attr in d:
			if (attr != 'meta'):
				setattr(self, attr, d[attr])

	def to_dict(self):
		d =  {
			'id'	: self.id,
			'meta'	: self.meta.copy()
		}
		if (d['meta'].get('storage') != None):
			d['meta']['storage'] = d['meta']['storage'].to_dict()
		return d

