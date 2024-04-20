import datetime
import json

class ProxyAuthUsersConfig:
	def __init__(self, config_filename: str):
		"""config_filename for example: proxies_config/socks5/config_file.json"""
		self.config_filename = config_filename
	
	def get_config_info(self) -> dict:
		with open(self.config_filename) as config_file:
			config_info = config_file.read()
		
		return json.loads(config_info)

	def update_config(self, new_info: dict, old_info=None):
		if old_info == None:
			old_info = self.get_config_info()
		
		curr_info = old_info.copy()
		curr_info.update(new_info)

		with open(self.config_filename, "w") as config_file:
			config_file.write(
				json.dumps(
					curr_info
				)
			)