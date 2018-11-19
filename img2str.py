#!/usr/bin/env python3
from pygame.image import tostring, load
import pygame.locals
from sys import argv, stderr
from base64 import b64encode
from zlib import compress

def to_str(name):
	img = load(name)
	img_str = b64encode(compress(tostring(img, "RGBA")))
	return img_str.decode()

if (__name__ == '__main__'):
	if (len(argv) == 1):
		print('Usage: img2str <image>')
	else:
		try:
			print(to_str(argv[1]))
		except pygame.error as error:
			print("img2str:", error, file=stderr)
