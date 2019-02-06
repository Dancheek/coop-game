import api

class Storage:
	def __init__(self, size):
		self.size = size
		self._items = [None] * self.size

	def __str__(self):
		return f"<storage, size - {self.size}>"

	def clear(self):
		for i in range(self.size):
			if (self._items[i] != None):
				self._items[i] = None

	def get_item(self, index):
		return self._items[index]

	def set_item(self, index, item):
		self._items[index] = item

	def to_dict(self):
		return {'items': self._items}

	def from_dict(self, d):
		self.size = len(d['items'])
		self._items = d['items']

class Item:
	pass
