import requests

def check_updates():
	with open("version.txt") as file:
		currently_version = file.read()

	response = requests.get()