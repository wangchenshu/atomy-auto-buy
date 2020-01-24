#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

from bs4 import BeautifulSoup

import os
import sys
import csv
import time
import re
import requests

def strip_name(name):
    name = name.strip(' ')
    name = name.strip('(↓)')
    name = name.strip('☎')
    name = name.strip('銷售代表')
    name = name.strip('經銷商')
    name = name.strip('/TL')
    return name

def find_all_member(s, member_num):
    r = s.post('http://www.atomy.com/tw/Home/MyAtomy/GroupTree?Slevel=100&vrate=100&VcustNo='+member_num+'&VbuCustName=0&VgjisaCode=0&VgmemberAuth=0&VglevelCnt=0&Vglevel=1&VgregDate=0&VgcustDate=1&VgstopDate=0&VgtotSale=0&VgcumSale=0&VgcurSale=0&VgbuName=0&SDate=2020-01-28&EDate=2020-01-28&glevel=1&gcust_date=1')
    soup = BeautifulSoup(r.text, 'html.parser')
    member_names = []
    member_ids = []

    table_tags = soup.find_all('table')
    for table_tag in table_tags:
        span_tags = table_tag.find_all('span')
        if (len(span_tags) > 4):
            member_ids.append(span_tags[0].text)
            name = strip_name(span_tags[2].text)
            member_names.append(span_tags[0].text + '-' + name.strip('銷售代表'))

    print(member_num + ' 的下線 (只能顯示到 100 代)')
    print(member_names)
    print('共計: ', len(member_names), '人')
    return member_names, member_ids

def find_id_by_name(member_names, name):
    return member_names.index(name.strip('\n'))

def exit(driver):
    print('bye')
    driver.execute_script('logoutForm.submit();')
    driver.close()
    sys.exit(1)

def menu():
    print('--------------------')
    print('選單:')
    print('0. 查我的資料')
    print('1. 輸入會員ID 查下線會員')
    print('q. 輸入q 離開')
    print('--------------------')

def start_login_atomy(username, password):
    ## headless ##
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # executable_path = '/Users/chenshuwang/bin/chromedriver'
    # driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)

    opts = Options()
    opts.headless = True
    driver = webdriver.Chrome(options=opts)
    # driver = webdriver.Chrome()

    print('程式啟動...')

    driver.get(login_page)

    ## input login user name ##
    loginusr = driver.find_element_by_id("userId")
    loginusr.send_keys(username)

    ## input login password ##
    loginpwd = driver.find_element_by_id("userPw")
    loginpwd.send_keys(password)

    ## login ##
    driver.execute_script('return login()')
    print('登入成功!')

    ## go to member tree page ##
    # driver.get(member_tree_page)

    # ## search ##
    # driver.execute_script('srchDisplay()')
    # print('please wait few seconds...')

    # time.sleep(3)
    # dLine = driver.find_element_by_id('dLine')
    # html = dLine.get_attribute('innerHTML')

    ## set cookies ##
    selenium_cookies = driver.get_cookies()
    s = requests.session()
    for i in selenium_cookies:
        requests.utils.add_dict_to_cookiejar(s.cookies, {i['name']: i['value']})
    
    return driver, s

load_dotenv()

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
login_page = 'https://www.atomy.com:449/tw/Home/Account/Login'
member_tree_page = 'http://www.atomy.com/tw/Home/MyAtomy/GroupTree'

all_member_names = []
all_member_ids = []
member_names = []
member_ids = []

driver, s = start_login_atomy(username, password)

## see my members ##
member_names, member_ids = find_all_member(s, username)
print('以上為我的下線 (只能顯示到 100 代)')

i_op = ''

while i_op != 'q':
    menu()
    i_op = input('請輸入 :\n')

    if i_op == '0':
        member_names, member_ids = find_all_member(s, username)
    elif i_op == '1':
        i_id = input('請輸入 ID :\n')
        find_all_member(s, i_id)
    elif i_op == 'q':
        exit(driver)
