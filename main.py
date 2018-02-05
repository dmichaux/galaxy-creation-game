# TODO make location the PRIMARY KEY for stars table?
# TODO **IF ABOVE** change all stars.id queries to stars.location
# TODO **IF ABOVE** change MAX(stars.id) to COUNT(stars.location)

# TODO change habitable 'True/False' to 'Yes/No' in planets table?
# TODO **IF ABOVE** remove "if eval(habitable):" in system_stats

# TODO explore "with" statement for db/cursor management
# TODO add tests for user input to match parameters
# TODO make sure user cannot create star without a nebula present
# TODO add sleep() time for better flow

import os
import cluster


def game_start_menu():
	"""Begin navigation for game startup"""
	print("Welcome to Star Game!")
	if os.path.isdir("save_files") and os.listdir("save_files"): # if saved files exist
		files = os.listdir('save_files')
		new_or_load = input("\n1. Create a new cluster\n2. Warp back to a previous cluster\n")
		if new_or_load == "1": # new game
			filename = input("What would you like to name your new cluster?\n")
			already_exists = _test_filename(filename, files)
			while already_exists: # must choose a unique name
				filename = input("Name already in use. Choose again:\n")
				already_exists = _test_filename(filename, files)
			star_cluster = _initialize_cluster(filename)
		else: # load game
			print("Choose a cluster to warp to:")
			for file in files:
				if file.endswith(".txt"):
					print(file.strip(".tx"))
			filename = input()
			valid = _test_filename(filename, files)
			while not valid: # must choose a valid save file
				filename = input("That cluster does not exist. Choose again:\n")
				valid = _test_filename(filename, files)
			star_cluster = cluster.Cluster(filename)
	else: # No previous games exits. Start new game.
		if not os.path.isdir("save_files"):
			os.mkdir("save_files")
		filename = input("What would you like to name your new cluster?\n")
		star_cluster = _initialize_cluster(filename)
	return star_cluster


def _test_filename(filename, files):
	exists = False
	for file in files:
		if filename in file:
			exists = True
	return exists


def _initialize_cluster(filename):
	"""Create Cluster object. Populate database."""
	star_cluster = cluster.Cluster(filename)
	print("\nYour star cluster is being created ...")
	star_cluster.populate_celestials()
	return star_cluster


def main_operations_menu():
	action = input("\nSelect an action:\n"
					"\t1. Omni-Directional Scan: search the area for stars and nebulae\n"
					"\t2. Focal Scan: search a star system for details\n"
						"\t\t [planetary details are available if scanning current system]\n"
					"\t3. Fire Weapons: obliterate a star system\n"
					"\t4. Utilize God-Like Powers: create a star system from a nebula\n"
					"\t5. Warp: move to another star system\n"
					"\t6. Exit game\n")
	return action


if __name__ == "__main__":

	star_cluster = game_start_menu()
	star_cluster.print_cluster_stats()

	player_location = star_cluster.find_random_location()
	distance_to_origin = star_cluster.distance_to(player_location, '(0, 0, 0)')
	print("You find yourself in the star system at {}.\n"
		"You are {}ly from the center of your star cluster.".format(player_location, distance_to_origin))

	# main game loop
	while True:
		action = main_operations_menu()
		if action == "1":
			star_cluster.local_scan(player_location)
		elif action == "2":
			coordinates = input("\nProvide coordinates for Focal Scan:\n")
			star_cluster.print_system_stats(coordinates, player_location)
		elif action == "3":
			coordinates = input("\nProvide coordinates to attack:\n")
			star_cluster.explode_star(coordinates)
		elif action == "4":
			coordinates = input("\nProvide coordinates of a nebula:\n")
			star_cluster.recreate_star(coordinates)
		elif action == "5":
			coordinates = input("\nProvide coordinates for warp drive:\n")
			player_location = coordinates
		else:
			break

	print("\nThank you - come again!")
