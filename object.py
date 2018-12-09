from uuid import uuid4

class BaseObject:
	def __init__(self, *args):
		if (len(args) == 1 and type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.id = args[0]
			self.x = args[1]
			self.y = args[2]
			self.uuid = str(uuid4())
		self.image = self.id

	def to_dict(self):
		return {'id': self.id,
				'x': self.x,
				'y': self.y,
				'uuid': self.uuid}

	def from_dict(self, d):
		for attr in d:
			setattr(self, attr, d[attr])


class Player(BaseObject):
	def __init__(self, *args):
		super().__init__(*args)
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.nickname = 'player'
			self.stats = {'active': True}
			self.stats_max = {}
			self.inventory = []
		self.image = 'default:player'

	def to_dict(self):
		d = super().to_dict()
		d.update({'nickname': self.nickname,
					'stats': self.stats})
		return d

