from importlib.util import spec_from_file_location, module_from_spec
from os import listdir
from os.path import splitext, exists, isdir
import pickle
import api

def load_mods(path='mods'):
	mods = []

	if (exists(path) and isdir(path)):
		files = listdir(path)
		for filename in files:
			if (splitext(filename)[1] in ('.py', '.pyc')):
				spec = spec_from_file_location('mod_' + filename.split('.')[0], path + '/' + filename)
				mod = module_from_spec(spec)
				spec.loader.exec_module(mod)
				mods.append(mod)
	return mods

def load_mod(filename):
	spec = spec_from_file_location(filename.split('.')[0], filename)
	mod = module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod

def load_world(name):
	with open(name, 'rb') as file:
		return pickle.load(file)

def save_world(world, name):
	pickle.dump(world, open(name, 'wb'))
