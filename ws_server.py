import websockets
import asyncio
import requests
import random
import os

from json import loads, load, dumps
from datetime import datetime, timedelta

import configshub

def is_file(filename: str):
	if len(filename.split(".")) >= 2:
		return True
	else:
		return False

class BotWebServer:
	def __init__(self, avg_cpu_usage: list, avg_network_speed: list, avg_ram_usage: list):
		self.CONNECTIONS = {}
		self.avg_cpu_usage = avg_cpu_usage
		self.avg_network_speed = avg_network_speed
		self.avg_ram_usage = avg_ram_usage

	async def ws_listner(self, websocket, path):
		while True:
			try:
				data = await websocket.recv()
				response = loads(data)

				print("new connect")
				print(response['command'])

				if response['command'] == "get_avg_infos":
					avg_cpu = self.avg_cpu_usage[0]
					avg_ram = self.avg_ram_usage[0]
					avg_network = self.avg_network_speed[0]
					await websocket.send(dumps({"avg_cpu": avg_cpu, "avg_ram": avg_ram, "avg_network": avg_network}))
				
				elif response['command'] == "get_socks5_proxy_users":
					proxy_users = []
					files = [f for f in os.listdir("proxies_config/socks5") if is_file(f)]
					for proxy_user in files:
						with open(f"proxies_config/socks5/{proxy_user}") as file:
							proxy_user_info = loads(file.read())
							proxy_users.append(proxy_user_info)
					
					print("socks5_proxy_users", proxy_users)
					await websocket.send(dumps(proxy_users))
				
				elif response['command'] == "get_http_proxy_users":
					proxy_users = []
					files = [f for f in os.listdir("http_proxy_server/users") if is_file(f)]
					for proxy_user in files:
						with open(f"http_proxy_server/users/{proxy_user}") as file:
							proxy_user_info = loads(file.read())
							proxy_users.append(proxy_user_info)
					
					print("http_proxy_users", proxy_users)
					await websocket.send(dumps(proxy_users))

				
				elif response['command'] == "purchased":
					try:
						proxy_type = response['proxy_type']
						proxy_login = response['proxy_login']

						new_config_data = response['new_config_data']

						if proxy_type == "socks5":
							config = configshub.ProxyAuthUsersConfig(f"proxies_config/socks5/{proxy_login}.json")
							config.update_config(
								new_info=new_config_data
							)
						elif proxy_type == "http":
							config = configshub.ProxyAuthUsersConfig(f"http_proxy_server/users/{proxy_login}.json")
							config.update_config(
								new_info=new_config_data
							)
					except Exception as err:
						error_id = random.uniform(0.00001, 1.0)
						with open("soft_logs\\error.txt", "a+") as file:
							file.write(error_id+" | "+err)
						
				elif response['command'] == "add_timestamp_end_time":
					proxy_type = response['proxy_type']
					proxy_login = response['proxy_login']
					seconds = response['add_time']['seconds']

					if proxy_type == "socks5":
						config = configshub.ProxyAuthUsersConfig(f"proxies_config/socks5/{proxy_login}.json")
						old_config_info = config.get_config_info()

						new_end_time = datetime.fromtimestamp(old_config_info['timestamp_end_time'])+timedelta(seconds=seconds)
						
						new_config_info = old_config_info.copy()
						new_config_info.update({'timestamp_end_time': new_end_time.timestamp()})

						config.update_config(
							new_info=new_config_info
						)

					elif proxy_type == "http":
						config = configshub.ProxyAuthUsersConfig(f"http_proxy_server/users/{proxy_login}.json")
						old_config_info = config.get_config_info()

						new_end_time = datetime.fromtimestamp(old_config_info['timestamp_end_time'])+timedelta(seconds=seconds)
						
						new_config_info = old_config_info.copy()
						new_config_info.update({'timestamp_end_time': new_end_time.timestamp()})

						config.update_config(
							new_info=new_config_info
						)

			except websockets.exceptions.ConnectionClosed:
				for acc, conn in self.CONNECTIONS.items():
					if conn == websocket:
						self.accounts_online.remove(acc)
						print("removed acc", acc, "from accounts_online!")
				
				break

	async def run(self, host="192.168.0.191", port=1124):
		loop = asyncio.get_running_loop()
		asyncio.set_event_loop(loop)

		host = requests.get("https://ipinfo.io/ip").text

		self.ws_server = await websockets.serve(self.ws_listner, host, port, ping_interval=5, ping_timeout=40)
		await self.ws_server.start_serving()