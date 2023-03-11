import requests
from typing import *


class UpdateCheckResult:
	php_version: str
	base_version: str
	build: int
	is_dev: bool
	channel: str
	git_commit: str  # revision
	mcpe_version: str
	date: int
	details_url: str
	download_url: str
	source_url: str
	build_log_url: str

	def __init__(self,
			php_version: str,
			base_version: str,
			build: int,
			is_dev: bool,
			channel: str,
			git_commit: str,
			mcpe_version: str,
			date: int,
			details_url: str,
			download_url: str,
			source_url: str,
			build_log_url: str):
		self.php_version = php_version
		self.base_version = base_version
		self.build = build
		self.is_dev = is_dev
		self.channel = channel
		self.git_commit = git_commit
		self.mcpe_version = mcpe_version
		self.date = date
		self.details_url = details_url
		self.download_url = download_url
		self.source_url = source_url
		self.build_log_url = build_log_url


def check(endpoint: str) -> UpdateCheckResult:
	res = requests.get(endpoint + "/api")
	result_json = res.json()

	return UpdateCheckResult(
		result_json["php_version"],
		result_json["base_version"],
		result_json["build"],
		result_json["is_dev"],
		result_json["channel"],
		result_json["git_commit"],
		result_json["mcpe_version"],
		result_json["date"],
		result_json["details_url"],
		result_json["download_url"],
		result_json["source_url"],
		result_json["build_log_url"]
	)
