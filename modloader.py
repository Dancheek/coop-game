from importlib.util import spec_from_file_location, module_from_spec
from os import listdir
from os.path import splitext

def load_mods(path='mods'):
	mods = []

	files = listdir(path)
	for filename in files:
		if (splitext(filename)[1] in ('.py', '.pyc')):
			spec = spec_from_file_location(filename, path + '/' + filename)
			mod = module_from_spec(spec)
			spec.loader.exec_module(mod)
			mods.append(mod)
	return mods

