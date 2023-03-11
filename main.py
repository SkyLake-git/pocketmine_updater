import pretty_download
import update_checker
from datetime import datetime
import os
import sys
from packaging.version import parse
import uuid
import shutil
import time
import json
import crayons
from typing import *


def get_version_info(extract_path: str, result_path: str) -> Any:
	op_cmd = f"""php -r \"require_once '{os.path.join(extract_path, 'src/VersionInfo.php')}';require_once '{os.path.join(extract_path, 'src/utils/VersionString.php')}';require_once '{os.path.join(extract_path, 'src/utils/Git.php')}';require_once '{os.path.join(extract_path, 'src/utils/Process.php')}';require_once '{os.path.join(extract_path, 'src/CoreConstants.php')}';use pocketmine\VersionInfo;file_put_contents('{result_path}', json_encode(['base_version' => VersionInfo::BASE_VERSION, 'is_dev' => VersionInfo::IS_DEVELOPMENT_BUILD, 'channel' => VersionInfo::BUILD_CHANNEL, 'build' => VersionInfo::BUILD_NUMBER(), 'git_commit' => VersionInfo::GIT_HASH()]));\""""
	os.system(
		op_cmd
	)

	# バージョン情報の取得
	with open(result_path, 'r', encoding='utf-8') as f:
		result = json.load(f)

	os.unlink(result_path)

	return result


def update_notify(latest: update_checker.UpdateCheckResult, current: Any) -> bool:
	if parse(latest.base_version) > parse(current["base_version"]):
		print(crayons.yellow(f"Your version of PocketMine-MP {current['base_version']} is out of date.", bold=True))
		print(crayons.yellow(
			f"Version {latest.base_version} was released on {datetime.fromtimestamp(latest.date).strftime('%Y-%m-%d %H:%M:%S')}",
			bold=True))

		return True
	return False


def info_display(latest: update_checker.UpdateCheckResult, current: Any) -> None:
	compare_list = {
		# "Git Commit": [latest.git_commit, current["git_commit"]], # Pharからでなく直で読み込んでいるためここらへんのが取得できていない場合がある (というかできない)
		"Version": [latest.base_version, current["base_version"]],
		# "Build": [latest.build, current["build"]]
	}

	info_list = {
		"Details": latest.details_url,
		"Download": latest.download_url,
		"Supported Minecraft Version": latest.mcpe_version,
		"PHP Version": latest.php_version
	}

	print("(latest) - (current)")
	for name, cmps in compare_list.items():
		print(f"{name}: " + crayons.magenta(f"{cmps[0]} - {cmps[1]}"))

	print()

	for name, data in info_list.items():
		print(f"{name}: " + crayons.cyan(data))


def update(phar_path: str, download_url: str) -> None:
	if os.path.exists(phar_path):
		os.unlink(phar_path)

	pretty_download.download(
		pretty_download.DownloadTarget(
			[download_url],
			phar_path
		),
		pretty_download.DownloadSettings(
			256,
			0.0,
			0.1
		),
		formatter=pretty_download.PrefixCreator("PocketMine Phar").create_formatter()
	)

	sys.stdout.write("\rCompleted                            ")


def main():
	phar_provided = False
	folder_provided = False

	if len(sys.argv) < 2:
		return

	phar_path = None
	host_path = None

	phar_path = os.path.realpath(sys.argv[1])
	host_path = os.path.dirname(phar_path)

	if os.path.exists(phar_path) and os.path.isfile(phar_path) and os.path.splitext(os.path.basename(phar_path))[
		1] == ".phar":
		phar_provided = True
	elif os.path.exists(phar_path) and os.path.isdir(phar_path):
		folder_provided = True
	extract_path = os.path.join(os.path.dirname(__file__), str(uuid.uuid4()))
	extract_path_safe = extract_path.replace("\\", "/")
	result_path = os.path.join(extract_path, 'result.txt')
	result_path_safe = result_path.replace("\\", "/")

	if (not phar_provided) and (not folder_provided):
		print("Please provide (folder or phar)")
		return

	latest = update_checker.check("https://update.pmmp.io")

	if (not phar_provided) and folder_provided:
		print(crayons.yellow("Phar path not provided, but folder found.", bold=True))
		info_display(latest, {
			"build": 0,
			"base_version": "0.0.0",
			"channel": "unknown",
			"git_commit": "",
			"is_dev": False
		})

		print()
		print(crayons.cyan("Downloading latest phar to folder", bold=True))

		time.sleep(1)

		update(os.path.join(phar_path, 'PocketMine-MP.phar'), latest.download_url)
		return

	os.makedirs(extract_path, exist_ok=False)

	print("Extracting phar...")
	# Phar を解凍する
	cmd = f"php -r \"$phar = new Phar(\'{phar_path}\');$phar->extractTo(\'{extract_path}\');\"".replace("\\", "/")
	os.system(cmd)

	print("Getting version info...")
	# 解凍したファイルからバージョン情報を抜き取る
	current = get_version_info(extract_path_safe, result_path_safe)

	print("Finalizing...")
	shutil.rmtree(extract_path)

	info_display(latest, current)

	print()

	updated = update_notify(latest, current)

	if updated:
		print(crayons.cyan("Update found. Download starts in 1 second...", bold=True))
		time.sleep(1)
		update(phar_path, latest.download_url)


if __name__ == '__main__':
	main()
