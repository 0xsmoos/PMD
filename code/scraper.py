# -*- coding: utf-8 -*-
# filename          : scraper.py
# description       : Grabs movie links
# author            : LikeToAccess
# email             : liketoaccess@protonmail.com
# date              : 07-15-2021
# version           : v2.0
# usage             : python scraper.py
# notes             :
# license           : MIT
# py version        : 3.8.2 (must run on 3.6 or higher)
#==============================================================================
import time
import os
import crop
import media
from media import log
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:
	def __init__(self):
		options = Options()
		files = os.listdir()
		for file in files:
			if file.endswith("crx"):
				options.add_extension(file)
		# options.add_argument("--headless")
		user_data_dir = os.path.abspath("selenium")
		options.add_argument(f"user-data-dir={user_data_dir}")
		options.add_argument("--disable-gpu")
		options.add_argument("log-level=3")
		self.executable = "chromedriver.exe" if os.name == "nt" else "chromedriver"
		self.driver = webdriver.Chrome(executable_path=os.path.abspath(self.executable), options=options)
		self.first_launch = True
		self.headers = {
			"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}

	def search(self, url):
		self.open_link(url)
		results, descriptions = self.get_results_from_search()
		# print(f"DEBUG: {descriptions[0].text}")
		metadata = {}
		for description in descriptions:
			if description.get_attribute("data-filmname") != description.text: continue
			metadata[description.text] = {
				"data-filmname": description.get_attribute("data-filmname"),
				"data-year":     description.get_attribute("data-year"),
				"data-imdb":     description.get_attribute("data-imdb"),
				"data-duration": description.get_attribute("data-duration"),
				"data-country":  description.get_attribute("data-country"),
				"data-genre":    description.get_attribute("data-genre"),
				"data-descript": description.get_attribute("data-descript"),
			}
		# print(metadata)
		return results, metadata

	def wait_until_element(self, stratagy, locator, timeout=10):
		wait = WebDriverWait(self.driver, timeout)
		element = wait.until(
			EC.presence_of_element_located(
				(
					stratagy, locator
				)
			)
		)
		return element

	def open_link(self, url):
		self.driver.get(url)
		# The following code only runs when the adblock is still initializing from the first launch
		if self.first_launch:
			# Searches for any ads on the site
			element = self.driver.find_elements(
				By.XPATH,
				"//*[@id=\"container-b530c7d909bb9eb21c76642999b355b4\"]/div[2]/div[5]/div/div[3]"
			)
			if element:  # If any ads were found, refresh the page and run the ad check again
				time.sleep(0.5)
				self.driver.refresh()
				self.open_link(url)
			self.first_launch = False

	def current_url(self):
		return self.driver.current_url

	def close(self):
		self.driver.close()

	def get_results_from_search(self):
		elements = self.driver.find_elements_by_class_name("item_hd") + \
				   self.driver.find_elements_by_class_name("item_series")
		description = self.driver.find_elements_by_class_name("_smQamBQsETb")
		return elements, description

	# def maximize(self):
	# 	self.driver.maximize_window()

	def screenshot_captcha(self, captcha_element, filename="captcha.png"):
		self.driver.save_screenshot(filename)
		# self.driver.save_screenshot("full_page.png")
		location = captcha_element.location
		location["y_off"] = 50
		location["x_off"] = 120
		return crop.crop(filename, location, self.executable)

	def check_captcha(self):
		try:
			captcha_image = self.wait_until_element(
				By.XPATH,
				"//*[@id=\"checkcapchamodelyii-captcha-image\"]",
				timeout=1.5
			)
			captcha_input = self.driver.find_element(By.XPATH, "//*[@id=\"checkcapchamodelyii-captcha\"]")
			captcha_submit = self.driver.find_element(By.XPATH, "//*[@id=\"player-captcha\"]/div[3]/div/div")
		except TimeoutException:
			return None, None, None
		if captcha_image:
			print("DEBUG: Captcha!")

		return captcha_image, captcha_input, captcha_submit

	def get_download_link(self, source_url, timeout=10):
		if not source_url.endswith("-online-for-free.html"):
			source_url += "-online-for-free.html"
		self.open_link(source_url)
		captcha_image, captcha_input, captcha_submit = self.check_captcha()
		if captcha_image:
			time.sleep(0.25)
			self.screenshot_captcha(captcha_image)
			log(
				"Captcha! Solve using the command:\n```!solve <captcha_solution>```--file=captcha.png",
				silent=False
			)
			solved_captcha = check_for_captcha_solve()

			if not solved_captcha:
				return False

			captcha_input.send_keys(solved_captcha)
			captcha_submit.click()
			return self.get_download_link(source_url, timeout)

		target_url = self.wait_until_element(By.TAG_NAME, "video", timeout)
		self.driver.execute_script(
			"videos = document.querySelectorAll(\"video\"); for(video of videos) {video.pause()}"
		)
		# print(target_url.get_attribute("src"))
		return target_url

	# '''Demitri's Holy Contribution'''
	# def get_movie(self, name):
	# 	self.driver.get_link_by_partial_text("").click()
	# 	self.driver.find_element_by_tag_name("input").text()

	def download_first_from_search(self, search_query):
		start_time = time.time()
		url = None
		search_results, metadata = self.search(
			"https://gomovies-online.cam/search/" + \
			"-".join(search_query.split())
		)
		print(f"Finished scraping {len(metadata)} results in {round(time.time()-start_time,2)} seconds!")
		if search_results:
			url = self.get_download_link(search_results[0].get_attribute("href") + "-online-for-free.html")
			# print(metadata)
		else:
			print("Error: No search results found!")
		print(f"Finished all scraping in {round(time.time()-start_time,2)} seconds!")
		return url

	def run(self, search_query):
		url = download_first_from_search(search_query)
		return url.get_attribute("src") if url else url


def check_for_captcha_solve(timeout=100):
	if __name__ == "__main__":
			media.write_file("captcha.txt", input("Solve the captcha:\n> "))

	filename = "captcha.txt"
	for half_second in range(timeout*2):
		time.sleep(0.5)
		if os.path.isfile(filename):
			solved_captcha = media.read_file(filename)[0]
			media.remove_file(filename)
			return solved_captcha
	log(f"Captcha was not solved withing {timeout} seconds.\nAborting download.", silent=False)
	return False


if __name__ == "__main__":
	scraper = Scraper()
	while True:
		query = input("Enter a Title to search for:\n> ")
		if query:
			scraper.run(query)
		else:
			break
	scraper.close()

# The criminal I've been chasing is wearing my shoes.
