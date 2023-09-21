import os
import random
import json
import requests

host = requests.get("https://ipinfo.io/ip").text
password = "Junction"

def create_user(user, password):
	os.system(f'adduser --gecos "" {user}')
	os.system(password)
	os.system(password)

network_interface = input("pls type network_interface: ")

user = "prox"
for socks_port in [1080, 1101, 1122, 1212]:
	user = user + "y"
	proxy_user = user + str(random.randint(0, 1111))

	create_user(
		user=proxy_user,
		password=password
	)

	config_text = """
# https://www.inet.no/dante/doc/1.4.x/config/ipv6.html
internal.protocol: ipv4
internal: {network_interface} port={port}
external.protocol: ipv4
external: {network_interface}

socksmethod: username

#user.privileged: root
user.notprivileged: {user}

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

""".format(
	network_interface=network_interface,
	port=socks_port,
	user=proxy_user
	)

	with open(f"/etc/danted{proxy_user}.conf", "w+") as config_file:
		config_file.write(config_text)
	
	with open(f"proxies/socks5/{proxy_user}.json", "w+") as config_file:
		config_file.write(json.dumps(
			{
				"host": host,
				"port": socks_port,
				"user": proxy_user,
				"password": password
			}
		))