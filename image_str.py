from pygame.image import tostring, load
from sys import argv
#import image

#screen = pygame.display.set_mode((300, 300))

img = load(argv[1])
img_str = tostring(img, "RGBA")
print("{} = scale(fromstring({}, (8, 8), \"RGBA\"), (32, 32))".format(argv[1].split('.')[0], img_str))
"""
def main():
	screen.fill((37, 37, 37))
	screen.blit(img, (0, 0))
	pygame.display.flip()

def handle():
	for e in pygame.event.get():
		if (e.type == pygame.QUIT):
			exit()

while True:
	handle()
	main()"""
