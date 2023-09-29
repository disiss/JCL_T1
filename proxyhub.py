import subprocess
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

class HTTP:
	def __init__(self, config_filename: str) -> None:
		self.config_filename = config_filename
	
	def change_password(self, password: str):
		config_hub = configshub.ProxyAuthUsersConfig(self.config_filename)
		config_hub.update_config(
			new_info={"password": password}
		)