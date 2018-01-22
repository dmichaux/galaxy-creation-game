import sqlite3
import random
import os


def get_game_menu_input():
	print("Welcome to Star Game!")
	size = input("Please select the size by entering a number:\n1. Cluster (small)\n2. Galaxy (large, !!much longer load time!!)\n")
	return size

def populate_celestials(size):
	"""Populate database with a unique number of stars and planets"""
	star_count = None
	if size == "1":
		star_count = random.randint(15000, 20000)
	else:
		star_count = random.randint(100000000000, 150000000000)


if __name__ == "__main__":
	size = get_game_menu_input()

	if os.path.isfile('celestials.db'):
		os.remove('celestials.db')

	db = sqlite3.connect('celestials.db')
	db.execute('CREATE TABLE stars (id INTEGER PRIMARY KEY, age INTEGER, mass INTEGER, luminosity INTEGER, location TEXT)')
	db.execute('CREATE TABLE planets (id INTEGER PRIMARY KEY, mass INTEGER, composition TEXT, distance INTEGER, home_star INTEGER)')

	populate_celestials(size)
