import requests
import subprocess
import os
import sys

def check_updates():
	with open("version.txt") as file:
		currently_version = file.read()

	response = requests.get("https://raw.githubusercontent.com/disiss/JCL_T1/main/version.txt")
	latest_version = response.text

	if currently_version != latest_version:
		print("Нашел обновление...")
		return True
	else:
		return False

def install_update():
	with open("JCL_updater.sh") as file:
		updater_code = file.read()

	print("Now working directory: {0}".format(os.getcwd()))

	os.chdir('/')
	print("Now working directory:: {0}".format(os.getcwd()))

	print("creating updater.sh")
	with open("JCL_updater.sh", "w+") as file:
		file.write(updater_code)
	
	subprocess.Popen(['bash', 'updater.sh'])
	raise Exception("Downloading new version...")

def start_all_proxies():
	pass