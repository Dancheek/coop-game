
# Module with some const and links to other objects

WHITE = (255, 255, 255)
GREY = (167, 167, 167)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)
RED = (255, 50, 70)

DIRECTIONS = ((0, -1), (-1, 0), (0, 1), (1, 0))


screen = None

game = None
server = None

world = None


send_message = None
send_message_to_all = None

exec_chat_command = None

tile_classes = None
object_classes = None


delta_time = 0


def save_config():
	global config
	config.write(open('config', 'w'))

def on_server():
	global server
	return (server != None)
