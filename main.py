# TODO make location the PRIMARY KEY for stars table?
# TODO **IF ABOVE** change all stars.id queries to stars.location
# TODO **IF ABOVE** change MAX(stars.id) to COUNT(stars.location)
# TODO change habitable 'True/False' to 'Yes/No' in planets table?
# TODO **IF ABOVE** remove "if eval(habitable):" in system_stats

# TODO explore "with" statement for db/cursor management
# TODO add tests for user input to match parameters
# TODO make sure user cannot create star without a nebula present

import os
import cluster


def game_start_menu():
	"""Begin navigation for game startup"""
	print("Welcome to Star Game!")
	if os.path.isfile("celestials.db"):
		load_or_new = input("\nA previously created cluster exists. Please select 1 or 2."
							"\n1. Continue with previous cluster\n2. Create new cluster\n")
		if load_or_new == "1":
			star_cluster = cluster.Cluster()
		else:
			os.remove('celestials.db')
			star_cluster = _initialize_cluster()
	else:
		star_cluster = _initialize_cluster()
	return star_cluster


def _initialize_cluster():
	"""Create Cluster object. Populate database."""
	star_cluster = cluster.Cluster()
	print("\nYour star cluster is being created ...")
	star_cluster.populate_celestials()
	return star_cluster


if __name__ == "__main__":

	star_cluster = game_start_menu()
	star_cluster.print_cluster_stats()

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
