import sqlite3
import random
import os
import time


def print_welcome():
	print("Welcome to Star Game!\nYour nearby stars are being created ...")


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
		db.commit()


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
	cursor = db.execute("SELECT MAX(id) FROM stars")
	star_number, = cursor.fetchone()
	print("There are {} stars in your area, created in {} seconds.".format(star_number, perf_time))


if __name__ == "__main__":
	print_welcome()

	start = time.perf_counter()

	if os.path.isfile('celestials.db'):
		os.remove('celestials.db')

	db = sqlite3.connect('celestials.db')
	db.execute('CREATE TABLE stars (id INTEGER PRIMARY KEY, age INTEGER, mass INTEGER, location TEXT)')
	db.execute('CREATE TABLE planets (id INTEGER PRIMARY KEY, mass INTEGER, composition TEXT, distance INTEGER, home_star INTEGER)')

	populate_celestials()

	end = time.perf_counter()
	elapsed = end - start

	print_stats(elapsed)

	db.close()