# TODO make location the PRIMARY KEY for stars table?
# TODO **IF ABOVE** change all stars.id queries to stars.location
# TODO **IF ABOVE** change MAX(stars.id) to COUNT(stars.location)
# TODO change habitable 'True/False' to 'Yes/No' in planets table?
# TODO **IF ABOVE** remove "if eval(habitable):" in system_stats
# TODO use generator (or .fetchone() in loop) in stars_within to save memory?
# TODO explore "with" statement for db/cursor management
# TODO add tests for user input to match parameters
# TODO make sure user cannot create star without a nebula present
# TODO remove perf_counters?

import os
import time
import cluster


if __name__ == "__main__":

	print("Welcome to Star Game!"
		"\nYour nearby star systems are being created ...")

	start = time.perf_counter()
	if os.path.isfile('celestials.db'):
		os.remove('celestials.db')

	star_cluster = cluster.Cluster()
	star_cluster.populate_celestials()
	end = time.perf_counter()
	elapsed = round(end - start, 3)
	star_cluster.print_cluster_stats(elapsed)

	player_location = star_cluster.find_random_location()
	distance_to_origin = star_cluster.distance_to(player_location, '(0, 0, 0)')
	print("You find yourself in the star system at {}.\n"
		"You are {}ly from the center of your star cluster.".format(player_location, distance_to_origin))

	star_cluster.local_scan(player_location)

	# exploding = input("\nExploding which star? [coordinates]\n")
	# star_cluster.explode_star(exploding)

	# star_cluster.local_scan(player_location)

	# creating = input("\nCreate from which nebula? [coordinates]\n")
	# star_cluster.recreate_star(creating)

	# star_cluster.local_scan(player_location)

	# system_in_question = input("\nDetails for which star system?")
	# star_cluster.print_system_stats(system_in_question, player_location)
