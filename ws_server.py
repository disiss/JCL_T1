import websockets
import asyncio
import requests
from json import loads, load, dumps
import re

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