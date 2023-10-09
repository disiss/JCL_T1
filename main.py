import psutil
import asyncio
import os
import json
import random

import utils
import ws_server
import proxyhub
import configshub

from datetime import datetime

if utils.check_updates():
	utils.install_update()

avg_cpu_usage_list = []
avg_network_speed_list = []
avg_ram_usage_list = []

server = ws_server.BotWebServer(
	avg_cpu_usage=avg_cpu_usage_list,
	avg_network_speed=avg_network_speed_list,
	avg_ram_usage=avg_ram_usage_list
)

async def avg_cpu_usage():
	while True:
		test_list = []
		for i in range(15):
			p_cpu = psutil.cpu_percent(interval=0.5)

			test_list.append(p_cpu)
			await asyncio.sleep(1)

		avg_cpu_usage = int(float(sum(test_list))/len(test_list)) #за 15 сек
		print("avg_cpu_usage: ", avg_cpu_usage, "%")
		
		avg_cpu_usage_list.clear()
		
		avg_cpu_usage_list.append(avg_cpu_usage)

async def avg_network_speed():
	io = psutil.net_io_counters()

	# получим сколько всего байтов отправленно и принято
	bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv

	while True:
		await asyncio.sleep(15)

		# получим снова данные о сети
		io_2 = psutil.net_io_counters()

		# новые значения - старые значения = промежуточные значения
		upload_speed, download_speed = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv

		upload_speed, download_speed = upload_speed/15, download_speed/15

		upload_speed = round(download_speed, 3)
		download_speed = round(upload_speed, 3)

		print(f"Upload: {io_2.bytes_sent}"
			f", Download: {io_2.bytes_recv}"
			f", Upload Speed: {upload_speed}/s"
			f", Download Speed: {download_speed}/s"
		)
		# обновляем  bytes_sent и bytes_recv для следующего цикла
		bytes_sent, bytes_recv = io_2.bytes_sent, io_2.bytes_recv

		avg_network_speed_list.clear()

		avg_network_speed_list.append({
			"upload_speed": upload_speed,
			"download_speed": download_speed
		})

async def avg_ram_usage():
	while True:
		test_list = []
		for i in range(15):
			try:
				ram_info = psutil.virtual_memory()

				test_list.append(ram_info.percent)
			except FileNotFoundError:
				print("Ram info not available on this system")
			
			await asyncio.sleep(1)

		avg_ram_usage = int(float(sum(test_list))/len(test_list)) #за 15 сек
		print("avg_ram_usage: ", avg_ram_usage, "%")
		
		avg_ram_usage_list.clear()
		
		avg_ram_usage_list.append(avg_ram_usage)

def is_file(filename: str):
	if len(filename.split(".")) >= 2:
		return True
	else:
		return False

async def test():
	while True:
		await asyncio.sleep(60)
		
		files = [f for f in os.listdir("proxies_config/socks5") if is_file(f)]
		for filename in files:
			with open(f"proxies_config/socks5/{filename}") as config_file:
				result = json.loads(config_file.read())

				if result['timestamp_end_time'] != None:
					dt_object = datetime.fromtimestamp(result['timestamp_end_time'])
					if datetime.now() >= dt_object:
						print(f"прокси: socks5\\{result['login']} закончился, меняю пароль)")

						new_password = f"Junction{random.randint(1, 100000)}"

						proxy = proxyhub.Socks5(user=result['login'])
						proxy.change_password(password=new_password)
			
						config = configshub.ProxyAuthUsersConfig(f'proxies_config/socks5/{filename}')
						config.update_config(new_info={"busy": False, "password": new_password, "timestamp_end_time": None})

		files = [f for f in os.listdir("http_proxy_server/users") if is_file(f)]
		for filename in files:
			with open(f"http_proxy_server/users/{filename}") as config_file:
				result = json.loads(config_file.read())

				if result['timestamp_end_time'] != None:
					dt_object = datetime.fromtimestamp(result['timestamp_end_time'])
					if datetime.now() >= dt_object:
						print(f"прокси: http\\{result['login']} закончился, меняю пароль)")

						proxy = proxyhub.HTTP(config_filename=f"http_proxy_server/users/{filename}")
						proxy.change_password(password=f"Junction{random.randint(1, 100000)}")

						config = configshub.ProxyAuthUsersConfig(f'http_proxy_server/users/{filename}')
						config.update_config(new_info={"busy": False, "password": new_password, "timestamp_end_time": None})

files = [f for f in os.listdir("proxies_config/socks5") if is_file(f)]
for filename in files:
	with open(f"proxies_config/socks5/{filename}") as config_file:
		result = json.loads(config_file.read())

	print(f"started: {result['host']}-{result['login']}-{result['password']}-{result['danted_config_file']}")
		
	socks5 = proxyhub.Socks5(result['login'])
	socks5.start_proxy()

loop = asyncio.get_event_loop()

loop.create_task(avg_cpu_usage())
loop.create_task(avg_network_speed())
loop.create_task(avg_ram_usage())

loop.run_until_complete(server.run())
loop.run_until_complete(test())