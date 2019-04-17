# -*- coding: utf-8 -*-
import re
import scrapy
import time
from ..utils import Browser, eastmoney_token
from selenium import webdriver
from ..items import StockMarketItem
from datetime import datetime, timedelta


class IwencaiSpider(scrapy.Spider):
    name = 'iwencai'
    allowed_domains = ['iwencai.com', "eastmoney.com"]
    start_urls = ['http://www.iwencai.com/']

    def parse(self, response):
        """
	对start_urls中的请求结果进行解析
	这里没有做解析工作，只是访问一次首页后开始请求搜索页面
	"""
	# 基础的搜索链接
	base_search_url = "http://www.iwencai.com/stockpick/search?typed=1&ts=1&f=1&qs=1&tid=stockpick&w="
	# 基础的股票列表链接
	base_list_url = "http://www.iwencai.com/stockpick/cache?token=placeholder&p=%d&perpage=%d"
	# 用于限制每页显示条数
	page_size = 30	
	# 搜索关键词
	keyword = "A股"
	# 组织搜索链接
	search_url = base_search_url + keyword
	# 获取请求搜索链接后的页面内容
	with Browser() as b:
	    b.get(search_url)
	    content = b.content
	# 用于存储搜索结果中的最大条目数
	total = None
	# 尝试从搜索结果中匹配最大条目数
	total_search = re.search(r'"total":(\d+),', content)
	total = total_search and int(total_search.group(1)) or 3601
	# 根据最大条目数 计算出列表页的最大页数
	max_page = total%page_size == 0 and total//page_size or total//page_size + 1
	# 用于测试
	# max_page = 5
	# 组织出每一页的列表页链接，并发送请求
	for page in range(1, max_page + 1):
	    list_url = base_list_url % (page, page_size)
	    yield scrapy.Request(list_url, callback=self.parse_list_url)

    @property
    def get_eastmoney_token(self):
	if not hasattr(self, "eastmoney_token"):
	    self.eastmoney_token = eastmoney_token()
	return self.eastmoney_token


    def parse_list_url(self, response):
	"""
	解析搜索页面获取token，然后访问所有列表页面
	"""
	# 基础的k线图数据api
	base_k_line_api = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?token=%s&rtntype=6&id=%s&type=k&authorityType=fa"
	# 获取东方财富的token
	token = self.get_eastmoney_token
	# 用于匹配产品数据的正则
	products_regexp = re.compile(r'result":(.+)?,"oriIndexID"')
	# 尝试从请求结果中匹配产品数据
	result = products_regexp.search(response.body)
	if not result:
	    print "error, 解析产品列表错误，url:%s" % response.url
	    print response.body[:100]
	    # 省略记录错误日志
	    req = response.request
	    req.dont_filter = True
	    yield req
	    return
	products = eval(result.group(1))
	# 解析产品数据，并请求每个产品的k线图数据api
	for product in products:
	# 用于测试
	# for product in products[:5]:
	    stock_info = {}
	    code, listed_location = product[0].split('.')
	    id = listed_location == "SH" and code + '1' or listed_location == 'SZ' and code + '2' or code
	    stock_info["stock_code"] = code + listed_location
	    stock_info["stock_abbreviation"] = product[1].decode('raw_unicode_escape')
	    stock_info["delist"] = product[2] == "--"
	    stock_info["market_type"] = product[4].decode('raw_unicode_escape')
	    k_line_api = base_k_line_api % (token, id)
	    yield scrapy.Request(url=k_line_api, meta={"stock_info": stock_info}, callback=self.parse_stock_market)

    def parse_stock_market(self, response):
	stock_info = response.meta.get("stock_info")
	data_regexp = re.compile(r'"data":\s?(\[[^\]]+?\]),')
	result = data_regexp.findall(response.body)
	if not result:
	    # 记录日志（简单打印）
	    print "error，解析股票市场数据失败，股票代码：%s" % stock_info["stock_code"]
	    return
	data = eval(result[0])
	start_date = datetime.strptime("2018-1-1", "%Y-%m-%d")
	end_date = datetime.strptime("2019-3-21", "%Y-%m-%d")
	for record in data:
	    record = record.split(',')
	    item = StockMarketItem()
	    item.update(stock_info)
	    item["date"] = record[0]
	    item["open_price"] = float(record[1])
	    item["close_price"] = float(record[2])
	    item["max_price"] = float(record[3])
	    item["min_price"] = float(record[4])
	    # 成交量
	    item["trading_volume"] = int(record[5])
	    # 成交额
	    item["turnover"] = int(record[6])
	    # 振幅
	    item["swing"] = record[7]
	    # 数据全解析 但根据据start_date和end_date控制数据是否要保存  肯根据需求修改
	    if start_date <= datetime.strptime(item["date"], "%Y-%m-%d") <= end_date:
		yield item


