from uuid import uuid4

class Object:
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
		self.id = d['id']
		self.x = d['x']
		self.y = d['y']
		self.uuid = d['uuid']

class Player(Object):
	def __init__(self, *args):
		super().__init__(*args)
		if (type(args[0]) == dict):
			self.from_dict(args[0])
		else:
			self.nickname = 'player'
			self.stats = {'active': True}
			self.max_stats = {}
			self.inventory = []

	def to_dict():
		d = super().to_dict()
		d.update({'nickname': self.nickname})
		return d

	def from_dict(self, d):
		super().from_dict(d)
		self.nickname = d['nickname']
