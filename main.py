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
import json
import re
import signal
import sys
import cluster


def game_start_menu():
	"""Begin navigation for game startup"""
	print("Welcome to Star Game!")
	player_location = None # changed if loading from file
	if os.path.isdir("save_files") and os.listdir("save_files"): # if saved files exist
		files = os.listdir('save_files')
		new_or_load = input("\n1. Create a new cluster\n2. Warp back to a previous cluster\n")
		while new_or_load not in ["1", "2"]: #user did not enter "1" or "2"
			new_or_load = input('Invalid selection. Please enter "1" or "2":\n') 
		if new_or_load == "1": # new game
			filename = _get_valid_filename(files)
			star_cluster = _initialize_cluster(filename)
		else: # load game
			print("Choose a cluster to warp to:")
			for file in files:
				if file.endswith(".txt"):
					print(os.path.splitext(file)[0])
			filename = input()
			while not _test_filename_existence(filename, files): # must choose a valid save file
				filename = input("That cluster does not exist. Choose again:\n")
			save_data = {}
			with open("save_files/" + filename + ".txt", "r") as json_file:
				save_data = json.load(json_file)
			player_location = save_data["location"]
			star_cluster = cluster.Cluster(filename)
	else: # No previous games exists. Start new game.
		if not os.path.isdir("save_files"):
			os.mkdir("save_files")
		filename = _get_valid_filename()
		star_cluster = _initialize_cluster(filename)
	return star_cluster, player_location


def _test_filename_existence(filename, files):
	exists = False
	for file in files:
		if (filename + ".txt") == file:
			exists = True
	return exists


def _get_valid_filename(files=None):
	"""Get filename that is 1 to 10 chars, alphanumeric-only, and not already in use"""
	filename = input("What would you like to name your new cluster?\n"
					"[10 characters max, alphanumeric only]\n")
	while True:
		valid = False # set to fail break condition
		exists = True # set to fail break condition
		if re.match("^[^\W_]{1,10}$", filename): # regex for 1 to 10 alphanumeric-only chars
			valid = True
		if files: # previous save files exist. Test filename for duplication
			exists = _test_filename_existence(filename, files)
		else: # files=None so no previous save files exist
			exists = False
		if not valid:
			filename = input("Invalid name. Please try another name:\n")
		if exists:
			filename = input("Name already in use. Choose again:\n")
		if valid and not exists: # filename must match regex and must not already exist
			break
	return filename


def _initialize_cluster(filename):
	"""Create Cluster object. Populate database."""
	star_cluster = cluster.Cluster(filename)
	print("\nYour star cluster is being created ...")
	star_cluster.populate_celestials()
	return star_cluster


def main_operations_menu():
	action = input("Select an action:\n"
					"\t1. Omni-Directional Scan: search the area for stars and nebulae\n"
					"\t2. Focal Scan: search a star system for details\n"
						"\t\t [planetary details are available if scanning current system]\n"
					"\t3. Fire Weapons: obliterate a star system\n"
					"\t4. Utilize God-Like Powers: create a star system from a nebula\n"
					"\t5. Warp: move to another star system\n"
					"\t6. Exit game\n")
	return action


def save_game(player_location, filename):
	"""Serialize and save game data to file"""
	save_data = {"location": player_location}
	with open("save_files/" + filename + ".txt", "w") as outfile:
		json.dump(save_data, outfile)
	print("\nYour cluster and player data has been saved.")


if __name__ == "__main__":

	# ==== Handles Exiting By Ctrl-C ====
	def exit_gracefully(signal, frame):
		"""Attempt to save game data before exit, if user presses Ctrl-C"""
		try: # exiting with game data
			save_game(player_location, star_cluster.filename)
		except NameError: # exiting before game data established
			pass
		finally:
			print("\nExiting program.")
			sys.exit(0)
	signal.signal(signal.SIGINT, exit_gracefully)

	# ==== Begin Game ====
	star_cluster, player_location = game_start_menu()
	star_cluster.print_cluster_stats()

	if not player_location:
		player_location = star_cluster.find_random_location()
	distance_to_origin = star_cluster.distance_to(player_location, '(0, 0, 0)')
	print("You find yourself in the star system at {}.\n"
		"You are {}ly from the center of your star cluster.".format(player_location, distance_to_origin))

	# main game loop
	while True:
		print("Current System:", player_location)
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
			save_game(player_location, star_cluster.filename)
			break


	print("\nThank you - come again!")
