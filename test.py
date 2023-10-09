import psutil
import requests

host = requests.get("https://ipecho.net/plain", verify=False).text
print(host)

addrs = psutil.net_if_addrs()
# print(addrs)

for addr_name, addr in addrs.items():
	for addr in addr:
		if addr.address == host:
			print("network_inerface is", addr_name)