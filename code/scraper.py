# -*- coding: utf-8 -*-
# filename          : scraper.py
# description       : Grabs movie links
# author            : LikeToAccess
# email             : liketoaccess@protonmail.com
# date              : 05-27-2021
# version           : v1.0
# usage             : python scraper.py
# notes             :
# license           : MIT
# py version        : 3.8.2 (must run on 3.6 or higher)
#==============================================================================
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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
		options.add_argument("--disable-gpu")
		# options.binary_location = r"C:\\Program Files (x86)\\AVG\\Browser\\Application\\AVGBrowser.exe"
		options.add_argument("log-level=3")
		executable = "chromedriver.exe" if os.name == "nt" else "chromedriver"
		self.driver = webdriver.Chrome(executable_path=os.path.abspath(executable), options=options)
		# self.driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
		# time.sleep(2)
		# self.driver.execute_script("window.open(\"\");")
		# self.driver.close()
		self.headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
		self.first_launch = True
		self.start_time = time.time()

	def search(self, link):
		self.open_link(link)
		results = self.get_results_from_search()
		# self.close()
		return results

	# def refresh(self):
	# 	self.driver.refresh()

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


	def open_link(self, link):
		self.driver.get(link)
		if self.first_launch:
			# self.wait_until_element(By.XPATH, "/html/body")
			element = self.driver.find_elements(By.XPATH, "//*[@id=\"container-b530c7d909bb9eb21c76642999b355b4\"]/div[2]/div[5]/div/div[3]")
			if element:
				# print(element)
				time.sleep(1)
				self.driver.refresh()
				self.open_link(link)
			self.first_launch = False
			# print("TEST")

		'''
		<div class="container-e9f98936bb33e6212d822ba738daa9a7__report-final">Ad was closed</div>
		'''

	def current_url(self):
		return self.driver.current_url

	def close(self):
		self.driver.close()

	def get_results_from_search(self):
		elements = self.driver.find_elements_by_class_name("item_hd") + \
				   self.driver.find_elements_by_class_name("item_series")
		return elements

	def maximize(self):
		self.driver.maximize_window()

	def get_download_link(self, source_link, timeout=10):
		self.open_link(source_link)
		target_link = self.wait_until_element(By.TAG_NAME, "video", timeout)
		print(target_link.get_attribute("src"))
		return target_link

'''
<video class="jw-video jw-reset" disableremoteplayback="" webkit-playsinline="" playsinline="" preload="auto" src="https://stream-2-1-ip4.loadshare.org/slice/5/VideoID-lpblIaAB/qFWIAA/ZBeL1r/MboyAT/ZJqtJS/360?name=the-lego-star-wars-holiday-special_360&amp;token=ip=67.220.18.185~st=1626163022~exp=1626177422~acl=/*~hmac=ffbbe3557b8fba7c8735fc3c0a0b869a881660768acbf245825fffd3fae27e72"></video>
'''

	# def get_movie(self, name):
	# 	self.driver.get_link_by_partial_text("").click()
	# 	self.driver.find_element_by_tag_name("input").text()

if __name__ == "__main__":
	scraper = Scraper()
	search = True
	while search != "":
		search = "-".join(input("Enter a Title to search for:\n> ").split())
		search_results = scraper.search(f"https://gomovies-online.cam/search/{search}")
		try:
			search_results[0].click()
			scraper.get_download_link(scraper.current_url() + "-online-for-free.html")
		except IndexError:
			print("Error: No search results found!")
	scraper.close()

	# search_arg = "-".join(sys.argv[1:])
	# search_results = scraper.search(f"https://gomovies-online.cam/search/{search_arg}")
	# for result in search_results: print(result.text)
