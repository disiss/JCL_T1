import os
import random
import json
import requests
import subprocess
import time
import sys

def generate_socks5(network_interface, host, ports=[1080, 1101, 1122, 1212]):
	password = "Junction"

	def create_user(user, password):
		os.system(f'adduser --gecos "" --disabled-login {user}')
		time.sleep(2)

		PASSWD_CMD='/usr/bin/passwd'
		cmd = [PASSWD_CMD, user]

		p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
		p.stdin.write(f'{password}'.encode())
		p.stdin.write('\n'.encode())

		p.stdin.write(f'{password}'.encode())
		p.stdin.write('\n'.encode())

		p.stdin.flush()

		p.wait()

	user = "prox"
	for socks_port in ports:
		user = user + "y"
		proxy_login = user + str(random.randint(0, 1111))

		create_user(
			user=proxy_login,
			password=password
		)

		config_text = """
	# https://www.inet.no/dante/doc/1.4.x/config/ipv6.html
	internal.protocol: ipv4
	internal: """+network_interface+""" port="""+str(socks_port)+"""
	external.protocol: ipv4
	external: """+network_interface+"""

	socksmethod: username

	#user.privileged: root
	user.notprivileged: """+proxy_login+"""

	client pass {
		from: 0.0.0.0/0 to: 0.0.0.0/0
		log: error
	}

	client pass {
		from: ::/0 to: ::/0
		log: error
	}

	# deny proxied to loopback
	socks block {
		from: 0.0.0.0/0 to: 127.0.0.0/8
		log: error
	}

	socks block {
		from: ::/0 to: ::1/128
		log: error
	}

	socks pass {
		from: 0.0.0.0/0 to: 0.0.0.0/0
		log: error
	}

	"""

		with open(f"/etc/danted{socks_port}.conf", "w+") as config_file:
			config_file.write(config_text)
		
		with open(f"proxies_config/socks5/{proxy_login}.json", "w+") as config_file:
			config_file.write(json.dumps(
				{	
					"busy": False,
					"host": host,
					"port": socks_port,
					"login": proxy_login,
					"password": password,
					"danted_config_file": f"danted{socks_port}.conf",
					"timestamp_end_time": None
				}
			))

def generate_http(count=4):
	user = "prox"
	password = "Junction"

	for x in count:
		user = user + "y"
		proxy_login = user + str(random.randint(0, 1111))
	
		with open(f"/http_proxy_server/users/{proxy_login}.json") as config_file:
			config_file.write(json.dumps(
				{	
					"busy": False,
					"host": host,
					"port": 1991,
					"login": proxy_login,
					"password": password,
					"timestamp_end_time": None
				}
			))

if __name__ == "__main__":
	host = requests.get("https://ipinfo.io/ip").text

	network_interface = sys.argv[1]
	generating = sys.argv[2]

	if generating == "socks5":
		generate_socks5(network_interface=network_interface, host=host)
	elif generating == "http":
		generate_http()