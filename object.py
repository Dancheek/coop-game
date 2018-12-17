from uuid import uuid4
import api

class BaseObject:
	def __init__(self, *args):
		if (len(args) == 1 and type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.x = args[0]
			self.y = args[1]
			self.uuid = str(uuid4())
		self.image = 'default:object'

	def to_dict(self):
		return {'id': self.id,
				'x': self.x,
				'y': self.y,
				'uuid': self.uuid}

	def from_dict(self, d):
		for attr in d:
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

	def get_stat(self, stat_name):
		return self.stats[stat_name]

	def get_rel(self, coords):
		return self.x + coords[0], self.y + coords[1]

	def update(self):
		pass

	def hit(self):
		self.set_stat('health', self.get_stat('health') - 1)


class Player(BaseObject):
	def __init__(self, *args):
		super().__init__(*args)
		self.id = 'default:player'
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.x = args[0]
			self.y = args[1]
			self.nickname = 'player'
			self.stats = {'active': True}
			self.stats_max = {}
			self.inventory = []
			self.in_hand = None
		self.image = 'default:player'

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

