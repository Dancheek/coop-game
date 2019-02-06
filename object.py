from uuid import uuid4
import api

class BaseObject:
	def __init__(self, x, y, id, data, meta=None, uuid=None):
		self.x = x
		self.y = y
		self.id = id
		self.image = data.get('image', self.id)
		self.stats = data.get('stats', {})
		self.uuid = str(uuid4()) if (uuid == None) else uuid

		self.speed = data.get('speed', 1)
		self.is_moving = False
		self.move_progress = 0
		self.target = (None, None)

		if (meta != None):
			self.meta = meta
		else:
			self.meta = data.get('meta', {})

		self.on_init = data.get('on_init', None)

		self.update = data.get('update', None)

	def to_dict(self):
		d = {
			'id': self.id,
			'x': self.x,
			'y': self.y,
			'uuid': self.uuid,
			'meta': self.meta.copy(),
			'move_progress': self.move_progress
		}
		if (d['meta'].get('storage') != None):
			d['meta']['storage'] = d['meta']['storage'].to_dict()
		return d

	def from_dict(self, d):
		for i in d['meta']:
			if (i == 'storage'):
				self.meta['storage'].from_dict(d['meta']['storage'])
			else:
				self.meta[i] = d['meta'][i]
		for attr in d:
			if (attr != 'meta'):
				setattr(self, attr, d[attr])

	def set_stat(self, stat_name, value):
		self.stats[stat_name] = value
		if (api.on_server()):
			api.server.send_object(self.uuid)

	def set_pos(self, x, y):
		self.x = x
		self.y = y
		if (api.on_server()):
			api.server.send_object(self.uuid)

	def add_move_progress(self, move_progress):
		self.move_progress += move_progress
		if (self.move_progress >= 1000):
			self.set_pos(*self.target)
			self.move_progress -= 1000
			self.is_moving = False

	def move_to(self, pos):
		self.target = pos
		self.is_moving = True

	def get_stat(self, stat_name):
		return self.stats[stat_name]

	def get_rel(self, coords):
		return self.x + coords[0], self.y + coords[1]

	def looking_at(self):
		return self.get_rel(api.DIRECTIONS[self.direction])

	def hit(self):
		self.set_stat('health', self.get_stat('health') - 1)


class Player(BaseObject):
	def __init__(self, x, y, meta=None, uuid=None):
		super().__init__(x, y, 'default:player', {}, meta=meta, uuid=uuid)
		self.nickname = 'player'
		self.stats = {'active': True}
		self.stats_max = {}
		self.meta = {'storage': api.create_storage(36)}
		self.in_hand = None

	def to_dict(self):
		d = super().to_dict()
		d.update({'nickname': self.nickname,
					'stats': self.stats,
					'in_hand': self.in_hand})
		return d

	def set_pos(self, x, y):
		super().set_pos(x, y)
		if (api.on_server()):
			self.send_self()

	def set_stat(self, stat_name, value):
		super().set_stat(stat_name, value)
		if (api.on_server()):
			self.send_self()

