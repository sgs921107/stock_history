# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import json
import logging
from hashlib import md5


class BasePipeline(object):
    """
    基础管道
    用于完善字段
    """

    def open_spider(self, spider):
	self.md5 = md5()

    def process_item(self, item, spider):
	self.md5.update(item["stock_code"] + item["date"])
	item["id"] = self.md5.hexdigest()
	item["date_stamp"] = int(time.mktime(time.strptime(item["date"], "%Y-%m-%d")))
	return item


class IWenCaiProductsPipeline(object):

    def open_spider(self, spider): 
	logging.warning("start spider".center(140, "="))
	self.start_time = time.time()
	self.data_file = open("./data/products.json", "w")

    def process_item(self, item, spider):
	data = json.dumps(dict(item), ensure_ascii=False).encode("utf-8")
	self.data_file.write(data)
	self.data_file.write("\r\n")
        return item

    def close_spider(self, spider):
	self.data_file.close()
	end_time = time.time()
	run_time = (end_time - self.start_time) / 60
	logging.warning("run time: %.2fMinute".center(100, "-") % run_time)
	logging.warning("end spider".center(140, "="))
