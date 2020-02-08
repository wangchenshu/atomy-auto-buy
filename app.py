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
# import concurrent.futures
import asyncio

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

def buy_all(driver):
    driver.find_element_by_id("bOrderAll").click()

def input_credit_card_data(driver, credit_month, credit_year, credit_card, check_num):
    # 進行信用卡驗證
    # 輸入卡號
    str_card_no = driver.find_element_by_id('ctl00_ContentPlaceHolder1_strCardNo')
    str_card_no.clear()
    str_card_no.send_keys(credit_card)

    # 輸入有效年月及驗證碼
    month_element = driver.find_element_by_xpath("//select[@name='ctl00$ContentPlaceHolder1$strMM']")
    all_options = month_element.find_elements_by_tag_name("option")
    for option in all_options:
        if credit_month == option.get_attribute("value"):
            option.click()
            break

    year_element = driver.find_element_by_xpath("//select[@name='ctl00$ContentPlaceHolder1$strYY']")
    all_options = year_element.find_elements_by_tag_name("option")
    for option in all_options:
        if credit_year == option.get_attribute("value"):
            option.click()
            break

    element_check_num = driver.find_element_by_id('check_num')
    element_check_num.clear()
    element_check_num.send_keys(check_num)
    driver.execute_script('check_all()')

def input_user_date(driver, cell_phone):
    t_user_name = driver.find_element_by_id('tUserName')
    t_rev_user_name = driver.find_element_by_id('tRevUserName')
    t_cell_phone = driver.find_element_by_id('tCellPhone')
    t_rev_cell_phone = driver.find_element_by_id('tRevCellPhone')
    t_send_name = driver.find_element_by_id('tSendName')

    t_cell_phone.clear()
    t_cell_phone.send_keys(cell_phone)
    
    t_send_name.clear()
    t_send_name.send_keys(t_user_name.text)

    # 點配送到所屬中心, 如果是與訂購人一致, 請選0
    driver.find_element_by_css_selector("input[name='runInfo'][value='4']").click()

    # 輸入收件人姓名及電話
    t_rev_user_name.clear()
    t_rev_user_name.send_keys(t_user_name.text)

    t_rev_cell_phone.clear()
    t_rev_cell_phone.send_keys(cell_phone)

    # 點信用卡, 如果是虛擬帳號, 請選2
    driver.find_element_by_css_selector("input[name='settleGubun'][value='3']").click()

    # 點擊同意
    driver.find_element_by_id('chkAgree').click()

    # 送出訂單
    driver.execute_script('check_submit()')

def excute_new_buy(member):
    username = member[0]
    password = member[1]
    cell_phone = member[2]

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
            if username == item[2]:
                add_to_cart(driver, find_product_url_by_name(item[0]), item[1])
                time.sleep(1)
                result = EC.alert_is_present()(driver)
                if result:
                    driver.switch_to.alert.accept()
                    time.sleep(1)
        except Exception as ex:
            ## pass alert popup ##
            pass

    go_to_cart(driver)
    buy_all(driver)
    input_user_date(driver, cell_phone=cell_phone)

    # 等一下下
    time.sleep(2)
    t_input = input('press any key to exit()')

    # 導向信用卡認證，輸入信用卡資料
    # input_credit_card_data(
    #     driver, 
    #     credit_card=credit_card,
    #     credit_month=credit_month,
    #     credit_year=credit_year,
    #     check_num=check_num
    # )

async def excute_new_buy_async(member):
    res = await loop.run_in_executor(None, excute_new_buy, member)

load_dotenv()
credit_card = os.getenv('CREDIT_CARD')
credit_month = os.getenv('CREDIT_MONTH')
credit_year = os.getenv('CREDIT_YEAR')
check_num = os.getenv('CHECK_NUM')
login_page = 'https://www.atomy.com:449/tw/Home/Account/Login'
cart_page = 'http://www.atomy.com/tw/Home/Product/Cart'
product_list = []
shopping_list = []
member_list = []

product_list = mapping_csv_to_list('result.csv')
shopping_list = mapping_csv_to_list('shopping_list.csv')
member_list = mapping_csv_to_list('member_list.csv')

## headless ##
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# executable_path = '/Users/chenshuwang/bin/chromedriver'
# driver = webdriver.Chrome(executable_path=executable_path,
# chrome_options=chrome_options)

# 同步版本
# all_process=[]
# for member in member_list:
#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         all_process.append(executor.submit(excute_new_buy, member))

# 異步版本
loop = asyncio.get_event_loop()
tasks = []

for member in member_list:
    task = loop.create_task(excute_new_buy_async(member))
    tasks.append(task)
loop.run_until_complete(asyncio.wait(tasks))

