import uvicorn
import os
import configshub
import requests

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from loguru import logger
from json import loads, dumps
from datetime import datetime, timedelta

app = FastAPI()

def is_file(filename: str):
	if len(filename.split(".")) >= 2:
		return True
	else:
		return False

class Api:
	def __init__(self, avg_cpu_usage: list, avg_network_speed: list, avg_ram_usage: list):
		self.avg_cpu_usage = avg_cpu_usage
		self.avg_network_speed = avg_network_speed
		self.avg_ram_usage = avg_ram_usage

		self.router = APIRouter()
		self.router.add_api_route("/api/get_avg_infos", self.get_avg_infos, methods=["GET"])
		self.router.add_api_route("/api/get_socks5_proxy_users", self.get_socks5_proxy_users, methods=["GET"])
		self.router.add_api_route("/api/get_http_proxy_users", self.get_http_proxy_users, methods=["GET"])

		self.router.add_api_route("/api/purchased", self.purchased, methods=["POST"])
		self.router.add_api_route("/api/add_timestamp_end_time", self.get_http_proxy_users, methods=["POST"])

		app.include_router(self.router)

	async def get_avg_infos(self, request: Request):
		api_token = request.headers.get("token")

		if api_token == "python228P!!P":
			avg_cpu = self.avg_cpu_usage[0]
			avg_ram = self.avg_ram_usage[0]
			avg_network = self.avg_network_speed[0]

			return JSONResponse(content={"avg_cpu": avg_cpu, "avg_ram": avg_ram, "avg_network": avg_network})
	
	async def get_socks5_proxy_users(self, request: Request):
		api_token = request.headers.get("token")

		if api_token == "python228P!!P":
			proxy_users = []
			files = [f for f in os.listdir("proxies_config/socks5") if is_file(f)]
			for proxy_user in files:
				with open(f"proxies_config/socks5/{proxy_user}") as file:
					proxy_user_info = loads(file.read())
					proxy_users.append(proxy_user_info)
					
			print("socks5_proxy_users", proxy_users)
			return JSONResponse(content=dumps(proxy_users))

	async def get_http_proxy_users(self, request: Request):
		api_token = request.headers.get("token")

		if api_token == "python228P!!P":
			proxy_users = []
			files = [f for f in os.listdir("http_proxy_server/users") if is_file(f)]
			for proxy_user in files:
				with open(f"http_proxy_server/users/{proxy_user}") as file:
					proxy_user_info = loads(file.read())
					proxy_users.append(proxy_user_info)
					
			print("http_proxy_users", proxy_users)
			return JSONResponse(content=dumps(proxy_users))
	
	async def purchased(request: Request):
		api_token = request.headers.get("token")

		if api_token == "python228P!!P":
			payload = await request.json()

			proxy_type = payload['proxy_type']
			proxy_login = payload['proxy_login']

			new_config_data = payload['new_config_data']

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
			
			return JSONResponse(content={"status": True})
	
	async def add_timestamp_end_time(request: Request):
		api_token = request.headers.get("token")

		if api_token == "python228P!!P":
			payload = await request.json()

			proxy_type = payload['proxy_type']
			proxy_login = payload['proxy_login']
			seconds = payload['add_time']['seconds']

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
			
			return JSONResponse(content={"status": True})
	
	def run(self, host="127.0.0.1", port=1124):
		host = requests.get("https://ipinfo.io/ip").text
		uvicorn.run(app, host=host, port=port)
