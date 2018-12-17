import pyperclip
from sys import exit

import pygame.font
pygame.font.init()

class TextInput:
	def __init__(self,	font,
						init_str = '',
						color = (255, 255, 255),
						cursor_color = (255, 255, 255),
						on_enter_press = None):
		self.font = font

		self.color = color
		self.cursor_color = cursor_color

		self.text = init_str
		self.surface = pygame.Surface((0, 0))
		self.cursor_pos = len(init_str)
		self.clock = pygame.time.Clock()

		self.repeat_event = None
		self.repeat_time = 0

		self.history = []
		self.history_selected = 0

	def update(self, events):
		for e in events:
			if (e.type == pygame.KEYDOWN):
				if (self.repeat_event == None):
					self.repeat_event = e
				elif (e != self.repeat_event):
					self.repeat_event = e
					self.repeat_time = 0

				if (e.key == pygame.K_BACKSPACE):
					if (self.cursor_pos > 0):
						self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
						self.cursor_pos -= 1

				elif (e.key == pygame.K_DELETE):
					if (self.cursor_pos < len(self.text)):
						self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]

				elif (e.key == pygame.K_LEFT):
					self.cursor_pos = max(self.cursor_pos - 1, 0)

				elif (e.key == pygame.K_RIGHT):
					self.cursor_pos = min(len(self.text), self.cursor_pos + 1)

				elif (e.key == pygame.K_UP):
					self.history_selected = max(self.history_selected - 1, 0)
					if (self.history_selected < len(self.history)):
						self.text = self.history[self.history_selected]
						self.cursor_pos = len(self.text)

				elif (e.key == pygame.K_DOWN):
					self.history_selected = min(self.history_selected + 1, len(self.history))
					if (self.history_selected < len(self.history)):
						self.text = self.history[self.history_selected]
						self.cursor_pos = len(self.text)
					elif (self.history_selected == len(self.history)):
						self.text = ''
						self.cursor_pos = 0

				elif (e.key == pygame.K_ESCAPE):
					self.clear()
					self.history_selected = len(self.history)

				elif (e.key == pygame.K_RETURN):
					if (self.text == ''):
						self.clear()
						return
					if (len(self.history) == 0 or len(self.history) > 0 and self.history[-1] != self.text):
						self.history.append(self.text)
						self.history_selected = len(self.history)

				elif (e.key == pygame.K_TAB):
					pass

				elif (e.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL):
					self.text = self.text[:self.cursor_pos] + pyperclip.paste() + self.text[self.cursor_pos:]
					self.cursor_pos += len(pyperclip.paste())

				elif (not pygame.key.get_mods() & pygame.KMOD_CTRL):
					self.text = self.text[:self.cursor_pos] + e.unicode + self.text[self.cursor_pos:]
					self.cursor_pos += len(e.unicode)

			elif (e.type == pygame.KEYUP):
				self.repeat_event = None
				self.repeat_time = 0
		if (self.repeat_event != None):
			self.repeat_time += self.clock.get_time()
			if (self.repeat_time > 300):
				self.repeat_time -= 40
				pygame.event.post(self.repeat_event)
		self.clock.tick()

	def render(self):
		self.cursor_x = self.font.size(self.text[:self.cursor_pos])[0]
		if (self.cursor_pos == len(self.text)):
			self.surface = self.font.render(self.text + ' ', 1, self.color)
			self.surface.blit(self.font.render(' ', 1, (37, 37, 37), self.color), (self.cursor_x, 0))
		else:
			self.surface = self.font.render(self.text, 1, self.color)
			self.surface.blit(self.font.render(self.text[self.cursor_pos], 1, (37, 37, 37), self.color), (self.cursor_x, 0))
		return self.surface

	def get_text(self):
		return self.text

	def try_autocomplete(self, variants):
		for variant in variants:
			if (variant.startswith(self.text[1:])):
				self.text = '/' + variant + ' '
				self.cursor_pos = len(variant) + 2

	def clear(self):
		self.text = ''
		self.cursor_pos = 0
		self.repeat_event = None
		self.repeat_time = 0

if (__name__ == "__main__"):
	screen = pygame.display.set_mode((1000, 50))

	text_input = TextInput(pygame.font.SysFont('consolas', 20))
	clock = pygame.time.Clock()

	while True:
		screen.fill((37, 37, 37))
		screen.blit(text_input.render(), (10, 10))
		pygame.display.flip()
		clock.tick(60)
		events = pygame.event.get()
		output = text_input.update(events)
		if (output != None):
			if (output == 0):
				exit()
			else:
				print(output)
		for e in events:
			if (e.type == pygame.QUIT):
				exit()
