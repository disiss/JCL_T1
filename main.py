import psutil
import asyncio

import ws_server

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

async def test():
	while True:
		await asyncio.sleep(15)
		print("its ok")

loop = asyncio.get_event_loop()

loop.create_task(avg_cpu_usage())
loop.create_task(avg_network_speed())
loop.create_task(avg_ram_usage())

loop.run_until_complete(server.run())
loop.run_until_complete(test())