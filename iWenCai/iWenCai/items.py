# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StockMarketItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #info = ["stock_code", "stock_abbreviation", "cur_price", "price_limit", "market_category", "market_value"]

    id = scrapy.Field()
    stock_code = scrapy.Field()
    stock_abbreviation = scrapy.Field()
    market_type = scrapy.Field()
    # 停牌
    delist = scrapy.Field()
    date = scrapy.Field()
    open_price = scrapy.Field()
    close_price = scrapy.Field()
    max_price = scrapy.Field()
    min_price = scrapy.Field()
    trading_volume = scrapy.Field()
    turnover = scrapy.Field()
    swing = scrapy.Field()
    date_stamp = scrapy.Field()


