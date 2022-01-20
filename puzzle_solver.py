import os
import sys
import time
import math
import cv2 as cv
import numpy as np
import urllib.request
from time import sleep
from pprint import pprint
from collections import Counter
from matplotlib import pyplot as plt

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium_move_cursor.MouseActions import move_to_element_chrome

class TikTok():
	def __init__(self,profile):
		self.options = uc.ChromeOptions()
		prof_id = profile
		path = f'temp/profile{prof_id}'
		self.options.add_argument(f'--user-data-dir={os.path.abspath(path)}')
		self.options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
		self.options.add_argument("--window-size=1920,1080")
		self.options.add_argument("--disable-popup-blocking")
		self.options.page_load_strategy = 'eager'
		self.options.add_argument('--disable-gpu')

	def start_chrome(self):
		self.driver = uc.Chrome(options=self.options)
		self.driver.maximize_window()
		self.driver.implicitly_wait(5)

	def login(self,username,password):
		self.start_chrome()

		self.driver.get('https://www.tiktok.com/login/phone-or-email/email')

		try:
			self.driver.find_element(By.NAME,'email').send_keys(username)
			self.driver.find_element(By.NAME,'password').send_keys(password)
			self.driver.find_element(By.CSS_SELECTOR,'button[type="submit"]').click()
		except:
			pass

		try:
			self.driver.find_element(By.ID,"captcha-verify-image")
			while 1:
				ans = self.solve_captcha()
				if ans['success']:
					break
				sleep(4)
		except Exception as e:
			pass

	def solve_captcha(self):
		captcha = self.driver.find_element(By.ID,"login_slide")
		print('wait img loader...')
		while 1:
			try:    
				img = self.driver.find_element(By.ID,"captcha-verify-image")
				if img.get_attribute('src'):
					sleep(1)
					img.screenshot('foo.png')
					break
			except Exception as e:
				print('wait img loader.....')
				try:
					self.driver.find_element(By.XPATH,"//div[contains(text(), 'Authorize')]")
					return {'success':1}
				except Exception as e:
					raise e

		img = cv.imread('foo.png')
		gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
		corners = cv.goodFeaturesToTrack(gray,15,0.05,1)
		corners = np.int0(corners)

		x_Array = []
		for i in corners:
			x,y = i.ravel()
			cv.circle(img,(x,y),3,255,-1)
			if x > 70:
				x_Array.append(x)

		x_Array.sort()
		print(x_Array)      

		slider = self.driver.find_element(By.CLASS_NAME,"captcha_verify_slide--slidebar")
		source = self.driver.find_element(By.CLASS_NAME,"secsdk-captcha-drag-icon")
		source_location = source.location
		source_size = source.size

		array = [170, 345, 400, 400, 345] 
		unic = Counter(x_Array) # проверка числа на уникальность, для устранения "гуляюших координат"
		for x in x_Array:
			if unic[x] > 1:
				x_offset = x-8
				break

		y_offset = 0
		action = ActionChains(self.driver)
		try:
			steps_count = 5
			step = (x_offset)/steps_count
			act_1 = action.click_and_hold(source)
			for x in range(0,steps_count):
				act_1.move_by_offset(step, y_offset)
			act_1.release().perform()

			msg = self.driver.find_element(By.CLASS_NAME,'msg').find_element(By.TAG_NAME,'div').text
			while msg == '':
				msg = self.driver.find_element(By.CLASS_NAME,'msg').find_element(By.TAG_NAME,'div').text
			print(msg)

			if 'Верификация пройдена' in msg or 'complete' in msg:
				return {'success':1}
			else:
				return {'success':0}

		except Exception as e:
			print(e)

	def close_browser(self):
		self.driver.quit()


if __name__ == '__main__':
	try:
		email = 'pupkin@gmail.com'
		password = '@password'

		t = TikTok('new1')
		t.login(email, password)
		sleep(10)

	except Exception as e:
		raise e
	finally:
		try:
			t.close_browser()
		except:
			pass
	

