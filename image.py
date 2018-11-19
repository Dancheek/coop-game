from pygame.image import fromstring, load
from pygame.transform import scale
from base64 import b64decode
from zlib import decompress

def from_str(string, size=(8, 8)):
	string = decompress(b64decode(string))
	return scale(fromstring(string, size, "RGBA"), (size[0] * 4, size[1] * 4))

