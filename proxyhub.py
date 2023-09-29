import subprocess
import os

import configshub

class Socks5:
	def __init__(self, user: str) -> None:
		self.user = user
	
	def change_password(self, password: str):
		PASSWD_CMD='/usr/bin/passwd'
		cmd = [PASSWD_CMD, self.user]

		p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
		p.stdin.write(f'{password}'.encode())
		p.stdin.write('\n'.encode())

		p.stdin.write(f'{password}'.encode())
		p.stdin.write('\n'.encode())

		p.stdin.flush()

		p.wait()
	
	def start_proxy(self):
		config_file = configshub.ProxyAuthUsersConfig(f"proxies_config/socks5/{self.user}.json")
		config = config_file.get_config_info()

		os.system(f"danted -D -p /root/JCL_T1/proxies_config/socks5/pids/{self.user}.pid -f /etc/{config['danted_config_file']}")

class HTTP:
	def __init__(self, config_filename: str) -> None:
		self.config_filename = config_filename
	
	def change_password(self, password: str):
		config_hub = configshub.ProxyAuthUsersConfig(self.config_filename)
		config_hub.update_config(
			new_info={"password": password}
		)