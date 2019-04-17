#!/usr/bin/env python
# -*- coding=utf8 -*-
import re
import requests
from selenium import webdriver
from settings import CHROME_DRIVER_PATH
import time


def cookies_str2dict(cookies_str):
    """
    将字符串的cookies转换为字典
    cookies_str: 字符串形式的cookies
    return cookies_dict:字典形式的cookies
    """
    cookies_list = cookies_str.split(";")
    cookies_dict = {}
    for cookie in cookies_list:
	k, v = cookie.split("=")
	cookies_dict.setdefault(k.strip(), v)
    return cookies_dict


def eastmoney_token():
    url = "http://quote.eastmoney.com/concept/SZ300743.html"
    headers = {
	    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
	    }
    resp = requests.get(url, headers=headers)
    token_regex = re.compile(r'token=([^"]+?)"')
    result = token_regex.findall(resp.content)
    if not result:
	return None
    token = result[0]
    return token


class Browser(object):

    def __init__(self):
	option = webdriver.ChromeOptions()
	option.add_argument('headless')
	self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=option)

    def __enter__(self):
	return self

    def quit(self):
	self.driver.quit()

    def close(self):
	self.driver.close()

    def __exit__(self, exc_type, exc_value, traceback):
	if exc_type:
	    print exc_type
	    print exc_value
	    print traceback
	self.quit()

    def get(self, url):
	self.driver.get(url)

    def cookies(self):
	driver_cookies = self.driver.get_cookies()
	cookies = {}
	for cookie in driver_cookies:
	    cookies[cookie["name"]] = cookie["value"]
	return cookies

    @property
    def content(self):
	return self.driver.page_source


def cookies_for_url(url):
    with Browser() as b:
	b.get(url)
	return b.cookies()


if __name__ == '__main__':
    """
    cookies_str = "ods=d63cc1ce4c6d370f9981fac0057d0fa309664378e93f905b8ec5b54faee8ee9770bedf89dd21d81d248f0077d47fc4672b487244df1b785d6e4e5a9e8a760bea; remember=72WjLha%2Fi1sCy94%2FWIOixbL0hArZUHmXW4%2BFutJr8Po%3D; sa_vst=-98614089.d20c89f6-6d71-4580-af76-067ff005588e.1553825492.1553826175.1553826240.1; sa_ref=-98614089.1553826240.1.1.utmcsr%3D(none)%7Cutmccn%3Dundefined%7Cutmcmd%3Ddirect%7Cutmctr%3D(none)%7Cutmcct%3D%2522(none)%2522; ODS_token=; SERVERID=6f95987c69571e21e20dc5e19db54d4d|1553827711|1553825388"
    cookies_dict = cookies_str2dict(cookies_str)
    print cookies_dict
    token = eastmoney_token()
    print token
    """
    url = "http://www.iwencai.com/stockpick/search?typed=1&ts=1&f=1&qs=1&tid=stockpick&w=A%E8%82%A1"
    cookies = cookies_for_url(url)
    print cookies



#########################################################################
# File Name: utils.py
# Author: sgs
# mail: sgs921107@163.com
# Created Time: Wed 27 Mar 2019 01:16:46 PM CST
#########################################################################
