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

		with open(self.config_filename) as config_file:
			config_file.write(
				json.dumps(
					old_info.copy().update(new_info)
				)
			)