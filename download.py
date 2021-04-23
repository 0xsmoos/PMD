from time import time
import os
import requests as req
import config as cfg
import stream
import media


headers = {"user-agent": cfg.user_agent}
quality = cfg.video_quality
media_files = media.Media("MOVIES")
home = os.getcwd()
req.adapters.HTTPAdapter(max_retries=2)


def url_format(url, target_res):
	for current_res in quality:
		url = url.replace(f"/{current_res}?name=",f"/{quality[int(target_res)]}?name=")
		url = url.replace(f"_{current_res}&token=ip=",f"_{quality[int(target_res)]}&token=ip=")
	return url

def test_link(url, start_time=0, resolution=0, error=False):
	if ((time() - start_time) < 10) or error:
		if int(resolution) >= len(quality)-1:
			print("FAILED (cannot lower quality)\nFailed download, link is invalid.")
			cfg.reset_attempts()
			return False
		cfg.increment_attempts()
		print("FAILED (lowering quality)")
		download(url)
		return False
	print("FAILED (retrying)")
	download(url)
	return False

def size(filename):
	file_size = os.stat(filename).st_size
	return file_size

def download(url):
	resolution = cfg.read_attempts()
	url = url_format(url, resolution)
	try: filename = media_files.rename(url.split("?name=")[1].split("&token=ip=")[0]+".mp4")
	except IndexError: filename = False
	try: request = req.get(url, headers=headers, stream=True, timeout=(30,cfg.timeout))
	except (req.exceptions.ConnectionError, req.exceptions.InvalidURL, req.exceptions.ReadTimeout):
		print("DEBUG: error")
		filename = False
	if not filename:
		print(f"FAILED (download timed out {cfg.timeout}s)\nFailed download, link is invalid.")
		return False
	print(f"Atempting download in {quality[int(resolution)]}p...", end=" ", flush=True)
	start_time = time()
	# print(f"DEBUG: {request.headers}")
	# print(f"DEBUG: {request}, {filename}, {media_files.path}, {url}")
	absolute_path = f"{media_files.path}/{filename}"
	try: stream.download_file(request, absolute_path)
	except req.exceptions.ConnectionError:
		download(url)
		return False
	except req.exceptions.HTTPError as error:
		return test_link(url, error=error)
	file_size = size(absolute_path)
	if file_size == 0:
		return test_link(url, start_time, resolution)
	with open(absolute_path, "r") as file:
		try:
			for count, line in enumerate(file):
				if count > 20:
					break
				if "403 Forbidden" in line:
					return test_link(url, start_time, resolution)
		except UnicodeDecodeError:
			pass
	cfg.reset_attempts()
	print("SUCCESS")
	print(f"Finished download in {quality[int(resolution)]}p.")
	return absolute_path
