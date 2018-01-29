import sqlite3
import random
import os
import time
import math


def print_welcome():
	print("Welcome to Star Game!"
		"\nYour nearby star systems are being created ...")


def populate_celestials():
	"""Populate database with a unique number of stars and planets"""
	star_count = random.randint(2500, 4000)
	map_size = 4000
	star_locations = []
	percent_created = 0
	for i in range(1, star_count):
		age = round(random.uniform(3.0, 13.8), 2)
		mass = round(random.uniform(0.5, 80), 2)
		location, star_locations = generate_location(map_size, star_locations)
		if i % (star_count // 20) == 0:
			percent_created += 5
			print("{}% created".format(percent_created))
		db.execute("INSERT INTO stars (age, mass, location) VALUES (?, ?, ?)", (age, mass, location))
		local_planet_num = random.randint(0, 9)
		if local_planet_num > 0:
			populate_planets(local_planet_num, location)
		db.commit()


def populate_planets(planet_num, home_star_location):
	"""Populate database with planets local to a star"""
	distance = 0
	for i in range(1, (planet_num + 1)):
		composition = None
		mass = None
		habitable = "False"
		if distance < 3.5:
			distance += round(random.uniform(0.6, 1.2), 2)
			composition = "rocky"
			mass = round(random.uniform(0.2, 2), 2)
			if 0.9 < distance < 1.8:
				habitable = "True"
		else:
			distance += round(random.uniform(8, 11), 2)
			composition = "gas/ice"
			mass = round(random.uniform(20, 300), 2)
		db.execute("INSERT INTO planets (mass, composition, distance,"
			" habitable, home_star) VALUES(?, ?, ?, ?, ?)", (mass,
				composition, distance, habitable, home_star_location))


def generate_location(map_size, occupied):
	"""Generate a unique 3D location that is not already occupied"""
	locations = occupied[:]
	coordinates = None
	while True:
		x = random.randint(-map_size, map_size)
		y = random.randint(-map_size, map_size)
		z = random.randint(-map_size, map_size)
		coordinates = (x, y, z)
		if coordinates not in locations:
			locations.append(coordinates)
			break
	return (str(coordinates), locations)


def print_stats(perf_time):
	"""Print numbers of stars, total planets, habitable planets"""
	cursor = db.execute("SELECT MAX(stars.id), MAX(planets.id) FROM stars"
		" INNER JOIN planets ON stars.location = planets.home_star")
	star_number, planet_number = cursor.fetchone()
	print("\nThere are {} stars and {} planets in your area; created in {} seconds.".format(star_number, planet_number, perf_time))
	cursor = db.execute("SELECT COUNT(id) FROM planets"
		" WHERE habitable = 'True'")
	habitable_number, = cursor.fetchone()
	print("Your area includes {} planets in the Habitable Zone!\n".format(habitable_number))


def find_random_location():
	"""Select a random star's location"""
	cursor = db.execute("SELECT MAX(id) FROM stars")
	star_number, = cursor.fetchone()
	random_star_id = random.randint(1, star_number)
	cursor = db.execute("SELECT location FROM stars WHERE id = ?", 
		(random_star_id,))
	random_star_location, = cursor.fetchone()
	return random_star_location


def distance_to(location_1, location_2):
	"""Calculate distance between two locations"""
	loc_1_list = location_1.strip('()').split(', ')
	loc_1_tuple = tuple([int(x) for x in loc_1_list])
	loc_2_list = location_2.strip('()').split(', ')
	loc_2_tuple = tuple([int(x) for x in loc_2_list])
	x1, y1, z1 = loc_1_tuple
	x2, y2, z2 = loc_2_tuple
	distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
	return round(distance, 2)

def stars_within(current_location, search_radius=1000):
	"""Search database for stars within search radius of current location"""
	print("\nConducting omni-directional scan...")
	within_range = []
	cursor = db.execute("SELECT location FROM stars")
	stars = cursor.fetchall()
	for location, in stars:
		if distance_to(current_location, location) <= search_radius:
			within_range.append(location)
	print("\nThe scan of {}ly radius found {} stars.\nLocations: {}".format(search_radius, len(within_range), within_range))
	return (len(within_range), within_range)


if __name__ == "__main__":
	print_welcome()

	start = time.perf_counter()

	if os.path.isfile('celestials.db'):
		os.remove('celestials.db')

	db = sqlite3.connect('celestials.db')
	db.execute('CREATE TABLE stars (id INTEGER PRIMARY KEY, age INTEGER, mass INTEGER, location TEXT)')
	db.execute('CREATE TABLE planets (id INTEGER PRIMARY KEY, mass INTEGER, composition TEXT, distance INTEGER, habitable TEXT, home_star TEXT)')

	populate_celestials()

	end = time.perf_counter()
	elapsed = round(end - start, 3)

	print_stats(elapsed)

	player_location = find_random_location()
	distance_to_origin = distance_to(player_location, '(0, 0, 0)')
	print("You find yourself in the star system at {}.\n"
		"You are {}ly from the center of your star cluster.".format(player_location, distance_to_origin))

	stars_within(str(player_location))

	db.close()