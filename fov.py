_octants = (( 1,  0,  0,  1),
			( 0,  1,  1,  0),
			( 0, -1,  1,  0),
			(-1,  0,  0,  1),
			(-1,  0,  0, -1),
			( 0, -1, -1,  0),
			( 0,  1, -1,  0),
			( 1,  0,  0, -1))


def get_fov(tile_map, cx, cy, r, blocking_tiles = [1]):
	height = len(tile_map)
	width = len(tile_map[0])

	fov = [[False] * width for i in range(height)]

	# Visit the center, ignoring whether it is a wall.
	fov[cy][cx] = True

	# Maintain a stack of pending beams. Store each beam as a tuple:
	#
	#	(min_x, min_y, max_y, min_dy, min_dx, max_dy, max_dx)
	#
	#	min_x		   - The first column to scan.
	#	min_y, max_y   - The first and last rows to scan.
	#	min_dy, min_dx - The start slope of the beam.
	#	max_dy, max_dx - The end slope of the beam.
	#
	# We track min_y and max_y to avoid scanning all the way from top to bottom
	# for each column. Another alternative is to calculate min_y and max_y from
	# the slopes.

	stack = []

	# Scan all octants.
	for xx, xy, yx, yy in _octants:

		# Push the root beam for this octant onto the stack.
		stack.append((1, 0, 1, 0, 1, 1, 1))

		while stack:
			# Pop the next beam from the stack.
			min_x, min_y, max_y, min_dy, min_dx, max_dy, max_dx = stack.pop()
			for x in range(min_x, r + 1):
				min_cell_dx, max_cell_dx = 2 * x + 1, 2 * x - 1

				# Skip any cells that are completely below or above the beam,
				# or completely outside its radius.
				while (2 * min_y + 1) * min_dx <= min_dy * max_cell_dx:
					min_y += 1
				while (2 * max_y - 1) * max_dx >= max_dy * min_cell_dx:
					max_y -= 1
				while (2 * x - 1) ** 2 + (2 * max_y - 1) ** 2 >= (2 * r) ** 2:
					max_y -= 1

				# Scan the column from base to top.
				any_walls = False
				all_walls = True
				old_wall = False
				for y in range(min_y, max_y + 1):

					# Transform to global coordinates and visit the cell.

					_x = cx + x * xx + y * xy
					_y = cy + x * yx + y * yy

					if (_x < 0 or width <= _x or
						_y < 0 or height <= _y):
							wall = True
					else:
						fov[_y][_x] = True
						if (tile_map[_y][_x] in blocking_tiles): wall = True
						else: wall = False
					#wall = visit(cx + x * xx + y * xy, cy + x * yx + y * yy)

					if wall:
						if not any_walls:

							# We have found the first wall in the column. Save
							# the old beam.
							any_walls = True
							old_max_y = max_y
							old_max_dy, old_max_dx = max_dy, max_dx

						if not old_wall:

							# Initially assume that the new wall spans the rest
							# of the column.
							old_wall = True
							max_y = y
							max_dy, max_dx = 2 * y - 1, min_cell_dx

						# The second to last cell in the column may block the
						# last cell.
						if (y == old_max_y - 1 and (2 * y + 1) * old_max_dx 
							> old_max_dy * max_cell_dx):
							 break

					else:
						if old_wall:

							# We have finished scanning a wall.
							old_wall = False
							if not all_walls and x < r:

								# The wall divides the column into two gaps.
								# Push a child beam for the lower gap onto the
								# stack.
								stack.append((x + 1, min_y, max_y, min_dy,
											 min_dx, max_dy, max_dx))

							# Initially assume that the new gap spans the rest
							# of the column.
							min_y, max_y = y, old_max_y
							min_dy, min_dx = 2 * (y - 1) + 1, max_cell_dx
							max_dy, max_dx = old_max_dy, old_max_dx

						all_walls = False
				if all_walls:
					break

				# Increment max_y for the next column.
				max_y += 1
	return fov

#def old_fov(tile_map, player_x, player_y, fov_radius, blocking_tiles = [1], start_angle = 0, end_angle = 360):
#	height = len(tile_map)
#	width = len(tile_map[0])
#
#	fov = [[0] * width for i in range(height)]
#
#	for i in range(start_angle, end_angle + 1):
#		x = player_x
#		y = player_y
#
#		ax = sintable[i]
#		ay = costable[i]
#
#		for j in range(fov_radius):
#			x += ax
#			y += ay
#
#			if (x < 0 or y < 0 or x + 1 >= width or y + 1 >= height):
#				break
#			fov[int(round(y))][int(round(x))] = 1
#			if (tile_map[int(round(y))][int(round(x))] in blocking_tiles):
#				break
#	if (player_x >= 0 and player_y >= 0): fov[player_y][player_x] = 1
#	return fov

def line(x1, y1, x2, y2):
	points = []
	issteep = abs(y2-y1) > abs(x2-x1)
	if issteep:
		x1, y1 = y1, x1
		x2, y2 = y2, x2
	rev = False
	if x1 > x2:
		x1, x2 = x2, x1
		y1, y2 = y2, y1
		rev = True
	deltax = x2 - x1
	deltay = abs(y2-y1)
	error = int(deltax / 2)
	y = y1
	ystep = None
	if y1 < y2:
		ystep = 1
	else:
		ystep = -1
	for x in range(x1, x2 + 1):
		if issteep:
			points.append((y, x))
		else:
			points.append((x, y))
		error -= deltay
		if error < 0:
			y += ystep
			error += deltax
	# Reverse the list if the coordinates were reversed
	if rev:
		points.reverse()
	return points

