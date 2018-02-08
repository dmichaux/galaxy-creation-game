import sqlite3
import random
import math
import sys
from contextlib import closing


class Cluster():
	"""Handles behavior for cluster. Encapsulates database queries and manipulations"""

	def __init__(self, filename):
		"""Open database connection. Create database tables."""
		self.filename = filename
		self.db_conn = sqlite3.connect("save_files/" + filename + ".db")
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("CREATE TABLE IF NOT EXISTS stars "
				"(id INTEGER PRIMARY KEY, age INTEGER, mass INTEGER, location TEXT, nebula TEXT)")
			cursor.execute("CREATE TABLE IF NOT EXISTS planets "
				"(id INTEGER PRIMARY KEY, mass INTEGER, composition TEXT, "
				"distance INTEGER, habitable TEXT, home_star TEXT)")


	def __del__(self):
		"""Close database connection before program finishes."""
		self.db_conn.close()


	def populate_celestials(self):
		"""Populate database with a unique number of stars and planets."""
		star_count = random.randint(2500, 4000)
		map_size = 4000
		star_locations = []
		percent_created = 0
		for i in range(1, star_count):
			age = round(random.uniform(3.0, 13.8), 2)
			mass = round(random.uniform(0.5, 80), 2)
			location, star_locations = self._generate_location(map_size, star_locations)
			if i % (star_count // 20) == 0:
				percent_created += 5
				sys.stdout.write("\r{}% created".format(percent_created))
				sys.stdout.flush()
				if percent_created == 100:
					print()
			with closing(self.db_conn.cursor()) as cursor:
				cursor.execute("INSERT INTO stars (age, mass, location, nebula) "
								"VALUES (?, ?, ?, ?)", (age, mass, location, 'False'))
			local_planet_num = random.randint(0, 9)
			if local_planet_num > 0:
				self._populate_planets(local_planet_num, location)
			self.db_conn.commit()


	def _populate_planets(self, planet_num, home_star_location):
		"""Populate database with planets local to a star."""
		# distance rounded at end because of float addition side-effects
		distance = 0
		for i in range(1, (planet_num + 1)):
			composition = None
			mass = None
			habitable = "False"
			if distance < 3.5:
				distance += random.uniform(0.6, 1.2)
				composition = "rocky"
				mass = round(random.uniform(0.2, 2), 2)
				if 0.9 < distance < 1.8:
					habitable = "True"
			else:
				distance += random.uniform(8, 11)
				composition = "gas/ice"
				mass = round(random.uniform(20, 300), 2)
			with closing(self.db_conn.cursor()) as cursor:
				cursor.execute("INSERT INTO planets (mass, composition, distance, "
								"habitable, home_star) VALUES(?, ?, ?, ?, ?)", (mass, composition, round(distance, 2), habitable, home_star_location))


	def _generate_location(self, map_size, occupied):
		"""Generate a unique 3D location that is not already occupied."""
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


	def print_cluster_stats(self):
		"""Print numbers of stars, total planets, habitable planets."""
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("SELECT MAX(stars.id), MAX(planets.id) FROM stars "
							"INNER JOIN planets ON stars.location = planets.home_star")
			star_num, planet_num = cursor.fetchone()
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("SELECT COUNT(id) FROM planets WHERE habitable = 'True'")
			habitable_num, = cursor.fetchone()
		print(f"\nCluster Stats:\n"
			f"Stars: {star_num}\n"
			f"Planets: {planet_num} [{habitable_num} in the Habitable Zone]")


	def find_random_location(self):
		"""Select a random star's location."""
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("SELECT location FROM stars ORDER BY RANDOM() LIMIT 1")
			random_star_location, = cursor.fetchone()
		return random_star_location


	def distance_to(self, location_1, location_2):
		"""Calculate distance between two locations."""
		loc_1_list = location_1.strip('()').split(', ')
		loc_1_tuple = tuple([int(x) for x in loc_1_list])
		loc_2_list = location_2.strip('()').split(', ')
		loc_2_tuple = tuple([int(x) for x in loc_2_list])
		x1, y1, z1 = loc_1_tuple
		x2, y2, z2 = loc_2_tuple
		distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
		return round(distance, 2)


	def local_scan_for(self, current_location, search_for="all", search_radius=1000):
		"""Query database for stars and/or nebulae within search radius of current location."""
		# In larger query results fetchone() in a loop would save memory. 
		# Here, fetchall() profiles as faster while still using minimal memory.

		def search_for_stars(current_location, search_radius):
			stars_within_range = []
			with closing(self.db_conn.cursor()) as cursor:
				cursor.execute("SELECT location FROM stars WHERE nebula = 'False'")
				stars = cursor.fetchall()
			for location, in stars:
				if self.distance_to(current_location, location) <= search_radius:
					stars_within_range.append(location)
			return stars_within_range

		def search_for_nebulae(current_location, search_radius):
			nebulas_within_range = []
			with closing(self.db_conn.cursor()) as cursor:
				cursor.execute("SELECT location FROM stars WHERE nebula = 'True'")
				nebulas = cursor.fetchall()
			for location, in nebulas:
				if self.distance_to(current_location, location) <= search_radius:
					nebulas_within_range.append(location)
			return nebulas_within_range

		if search_for == "stars":
			return search_for_stars(current_location, search_radius)
		elif search_for == "nebulae":
			return search_for_nebulae(current_location, search_radius)
		elif search_for == "all":
			return search_for_stars(current_location, search_radius), search_for_nebulae(current_location, search_radius), search_radius



	def explode_star(self, coordinates):
		"""Update database to set star values to zero. Delete star's planets."""
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("UPDATE stars "
							"SET age = 0, mass = 0, nebula = 'True' "
							"WHERE location = ?", (coordinates,))
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("DELETE FROM planets WHERE home_star = ?", (coordinates,))
		print("\nStar exploded (orbiting planets too).")
		self.db_conn.commit()


	def recreate_star(self, coordinates):
		"""Update database with new star's mass and planets."""
		mass = round(random.uniform(0.5, 80), 2)
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("UPDATE stars "
							"SET mass = ?, nebula = 'False' "
							"WHERE location = ?", (mass, coordinates))
		local_planet_num = random.randint(0, 9)
		if local_planet_num > 0:
			self._populate_planets(local_planet_num, coordinates)
		print(f"Star created. It has {local_planet_num} planets.")
		self.db_conn.commit()


	def print_system_stats(self, coordinates, player_location):
		"""Find and print information on a star and its planets."""
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("SELECT age, mass FROM stars "
							"WHERE location = ?", (coordinates,))
			star_age, star_mass = cursor.fetchone()
		with closing(self.db_conn.cursor()) as cursor:
			cursor.execute("SELECT COUNT(id) FROM planets "
							"WHERE home_star = ?", (coordinates,))
			planet_num, = cursor.fetchone()
		print(f"\nSelected system details:"
				f"\nStar Age: {star_age} billion years"
				f"\nStar Mass: {star_mass} Solar Masses"
				f"\nOrbiting Planets: {planet_num}")
		# If user searches current location, print more detailed planetary info
		if coordinates == player_location:
			with closing(self.db_conn.cursor()) as cursor:
				cursor.execute("SELECT mass, composition, distance, habitable "
								"FROM planets WHERE home_star = ? "
								"ORDER BY distance", (coordinates,))
				planets_info = cursor.fetchall()
			if len(planets_info) > 0:
				print("\nPlanetary details for system:"
					"\nDistance From Star | Mass | Composition | "
					"Inside Habitable Zone")
				planet_counter = 0
				for planet in planets_info:
					mass, composition, distance, habitable = planet
					if eval(habitable):
						habitable = 'Yes'
					else:
						habitable = 'No'
					planet_counter += 1
					print(f"{planet_counter}: {distance}au | {mass} Earth Masses "
						f"| {composition} | {habitable}")
