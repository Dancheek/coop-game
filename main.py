import modloader

data = {}

mods = modloader.load_mods()
for mod in mods:
	data.update(mod.data)

print(data)
