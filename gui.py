import api
import pygame.locals
from textwrap import wrap
from pygame import Rect, Surface

pygame.font.init()
font = pygame.font.SysFont("consolas", 20)

TILE_WIDTH = 36

def fill_alpha(surface, color, alpha, rect=None): # FIXME
	surface.fill(tuple(255 * (1 - alpha) for i in range(3)), rect, pygame.BLEND_MULT)
	surface.fill(tuple(i * alpha for i in color), rect, pygame.BLEND_ADD)

def split_string(text, max_line_lenght=40):
	text_lines = []
	words = text.split()
	current = 0
	for i in text:
		pass


def draw_text(text='sample text', color=(255, 255, 255), pos=(0, 0), surface=None, align_x='left', align_y='top'):
	if (surface == None):
		surface = api.screen
	text_rect = Rect(0, 0, *font.size(text))

	if (align_x == 'left'):
		text_rect.left = pos[0]
	elif (align_x == 'center'):
		text_rect.centerx = pos[0]
	elif (align_x == 'right'):
		text_rect.right = pos[0]

	if (align_y == 'top'):
		text_rect.top = pos[1]
	elif (align_y == 'center'):
		text_rect.centery = pos[1]
	elif (align_y == 'bottom'):
		text_rect.bottom = pos[1]

	surface.blit(font.render(text, 1, color), text_rect)

def draw_rich_text(text, color, pos, surface=None, align_x='left', align_y='top', text_align=None, max_line_lenght=50):
	if (text_align == None):
		text_align = align_x

	if (type(text) == list):
		text_lines = text
	else:
		text_lines = text.split('\n')
		for i, line in enumerate(text_lines):
			if (line == ''):
				text_lines[i] = ['']
			else:
				text_lines[i] = wrap(line, width=max_line_lenght)
		text_lines = [item for sublist in text_lines for item in sublist]

	if (align_y == 'top'):
		for i in range(len(text_lines)):
			draw_text(text_lines[i], color, (pos[0], pos[1] + font.size('')[1] * i), surface, text_align, align_y)

	elif (align_y == 'bottom'):
		for i in range(len(text_lines)):
			draw_text(text_lines[i], color, (pos[0], pos[1] - font.size('')[1] * i), surface, text_align, align_y)

	elif (align_y == 'center'):
		for i in range(len(text_lines)):
			draw_text(text_lines[i], color, (pos[0], pos[1] - (font.size('')[1] * len(text_lines) // 2) + font.size('')[1] * i), surface, text_align, align_y='top')

	return len(text_lines)


def form_element(name, data, root):
	element = None
	if (data['type'] == 'label'):
		element = Label(
			text = data['text'],
			name = name,
			pos = data['pos'],
			size = data['size'],
			align_x = data.get('align_x', 'center'),
			align_y = data.get('align_y', 'center'),
			root = root
		)
	elif (data['type'] == 'button'):
		element = Button(
			text = data.get('text', ''),
			name = name,
			pos = data['pos'],
			size = data['size'],
			root = root,
			on_click = data.get('on_click', None),
			inactive = data.get('inactive', False),
			update = data.get('update', None)
		)
	elif (data['type'] == 'storage_view'):
		element = StorageView(
			name = name,
			pos = data['pos'],
			size = data['size'],
			storage = data['storage'],
			root = root
		)
	return element


class Form:
	def __init__(self, data):
		self.size = data.get('size')
		self.background = data.get('background', (48, 48, 48))

		self.rect = Rect(0, 0, self.size[0]*TILE_WIDTH, self.size[1]*TILE_WIDTH)
		self.rect.center = api.screen.get_rect().center
		self.surface = Surface(self.rect.size)

		elements = data.get('elements', {})
		self.elements = {}
		if (elements != {}):
			for e in elements:
				element = form_element(e, elements[e], root=self)
				if (element != None):
					self.elements[e] = element

		if (data.get('on_open') != None):
			self.on_open = data.get('on_open').__get__(self)

	def reset(self):
		for e in self.elements:
			self.elements[e].reset()

	def get_element(self, name):
		return self.elements[name]

	def draw(self):
		if (self.rect.center != api.screen.get_rect().center):
			self.rect.center = api.screen.get_rect().center
		api.screen.fill((60, 60, 60), (self.rect.x - 5, self.rect.y - 5, self.rect.w + 10, self.rect.h + 10))
		for e in self.elements:
			self.elements[e].draw()

	def handle(self, events):
		for e in self.elements:
			self.elements[e].handle(events)

	def update(self):
		for e in self.elements:
			self.elements[e].update()

	def on_open(self, player):
		pass


class Element:
	def __init__(self, name, pos, size, root):
		self.name = name
		self.pos = pos
		self.size = size
		self.root = root

	def reset(self):
		pass

	def get_pos(self):
		return (
			self.root.rect.x + self.pos[0] * TILE_WIDTH,
			self.root.rect.y + self.pos[1] * TILE_WIDTH
		)

	def get_size(self):
		return (
			self.size[0] * TILE_WIDTH,
			self.size[1] * TILE_WIDTH
		)

	def get_rect(self):
		return Rect(*self.get_pos(), *self.get_size())

	def draw(self):
		pass

	def handle(self, events):
		pass

	def update(self):
		pass


class Label(Element):
	def __init__(self, text='', name='label', pos=(0, 0), size=(1, 1), align_x='center', align_y='center', root=None):
		super().__init__(name, pos, size, root)
		self.text = text
		self.align_x = align_x
		self.align_y = align_y

	def draw(self):
		self_rect = self.get_rect()
		if (self.align_x == 'left'):
			x = self_rect.left
		elif (self.align_x == 'center'):
			x = self_rect.centerx
		elif (self.align_x == 'right'):
			x = self_rect.right

		if (self.align_y == 'top'):
			y = self_rect.top
		elif (self.align_y == 'center'):
			y = self_rect.centery
		elif (self.align_y == 'bottom'):
			y = self_rect.bottom

		draw_text(
			text = self.text,
			pos = (x, y),
			align_x = self.align_x,
			align_y = self.align_y
		)


class Button(Element):
	def __init__(self, text='', name='button', pos=(0, 0), size=(1, 1), root=None, on_click=None, update=None, inactive=False):
		super().__init__(name, pos, size, root)
		self.state_colors = {
			'idle': (70, 70, 70),
			'hover': (100, 100, 100),
			'pressed': (140, 140, 140)
		}
		self.state = 'idle'
		self.text = text
		if (on_click != None):
			self.on_click = on_click.__get__(self)
		if (update != None):
			self.update = update.__get__(self)
		self.inactive = inactive

	def reset(self):
		self.set_state('idle')

	def draw(self):
		if (self.inactive):
			api.screen.fill((50, 50, 50), self.get_rect())
			draw_text(
				text = self.text,
				color = api.GREY,
				pos = self.get_rect().center,
				surface = api.screen,
				align_x = 'center',
				align_y = 'center'
			)
		else:
			api.screen.fill(self.state_colors[self.state], self.get_rect())
			draw_text(
				text = self.text,
				color = api.WHITE,
				pos = self.get_rect().center,
				surface = api.screen,
				align_x = 'center',
				align_y = 'center'
			)

	def handle(self, events):
		if (not self.inactive):
			for e in events:
				if (e.type == pygame.MOUSEMOTION and self.state != 'pressed'):
					if (self.get_rect().collidepoint(e.pos)):
						self.set_state('hover')
					else:
						self.set_state('idle')
				if (e.type == pygame.MOUSEBUTTONDOWN):
					if (self.get_rect().collidepoint(e.pos) and e.button == 1):
						self.set_state('pressed')
				if (e.type == pygame.MOUSEBUTTONUP):
					if (self.state == 'pressed' and e.button == 1):
						if (self.get_rect().collidepoint(e.pos)):
							self.set_state('hover')
							self.on_click()
						else:
							self.set_state('idle')

	def set_state(self, state):
		self.state = state

	def on_click(self):
		print('click')


class StorageView(Element):
	def __init__(self, name='storage', pos=(0, 0), size=(1, 1), storage=None, root=None):
		super().__init__(name, pos, size, root)
		if (storage == 'player'):
			self.storage = api.game.player.meta['storage']
		else:
			self.storage = storage

	def draw(self):
		i = 0
		x, y = self.get_pos()
		while (i < self.storage.size):
			if (self.storage.get_item(i) == None):
				color = (32, 32, 32)
			else:
				color = (128, 128, 128)
			api.screen.fill(color, (
				x + i % self.size[0] * TILE_WIDTH + 2,
				y + i // self.size[0] * TILE_WIDTH + 2,
				TILE_WIDTH - 4,
				TILE_WIDTH - 4
			))
			i += 1

