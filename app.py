#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

import os
import sys
import csv
import time

def add_to_cart(driver, url, num):
    driver.get(url)
    qty = driver.find_element_by_id('tQty')
    qty.clear()
    qty.send_keys(num)
    driver.find_element_by_id("bAddCart").click()

def go_to_cart(driver):
    driver.get(cart_page)

def find_product_url_by_name(name):
    return list(filter(lambda x: name in x, product_list))[0][3]

def mapping_csv_to_list(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        new_list = list(reader)
    return new_list

load_dotenv()

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
login_page = 'https://www.atomy.com:449/tw/Home/Account/Login'
cart_page = 'http://www.atomy.com/tw/Home/Product/Cart'
product_list = []
shopping_list = []

product_list = mapping_csv_to_list('result.csv')
shopping_list = mapping_csv_to_list('shopping_list.csv')

## headless ##
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# executable_path = '/Users/chenshuwang/bin/chromedriver'
# driver = webdriver.Chrome(executable_path=executable_path,
# chrome_options=chrome_options)

driver = webdriver.Chrome()
driver.get(login_page)

## input login user name ##
loginusr = driver.find_element_by_id("userId")
loginusr.send_keys(username)

## input login password ##
loginpwd = driver.find_element_by_id("userPw")
loginpwd.send_keys(password)

## login ##
driver.execute_script('return login()')

## check shopping list and add to cart ##
for item in shopping_list:
    try:
        add_to_cart(driver, find_product_url_by_name(item[0]), item[1])
        result = EC.alert_is_present()(driver)
        if result:
            driver.switch_to.alert.accept()
    except Exception:
        ## pass alert popup ##
        pass
    time.sleep(1)

go_to_cart(driver)