# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
from scrapy import signals
from utils import cookies_for_url, Browser


class IwencaiSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IwencaiDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
	self.iwencai_search_url = "http://www.iwencai.com/stockpick/search?typed=1&ts=1&f=1&qs=1&tid=stockpick&w=A%E8%82%A1"
	self.iwencai_cookies = cookies_for_url(self.iwencai_search_url)
	self.iwencai_token = None

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
	if request.url.startswith("http://www.iwencai.com/stockpick/cache?token="):
	    if not self.iwencai_token:
		self.iwencai_token = self.get_iwencai_token
	    url = re.sub(r'token=[^&]+?&', "token=%s&" % self.iwencai_token, request.url)
	    request._set_url(url)
	    request.cookies = self.iwencai_cookies
        return None
    
    @property
    def get_iwencai_token(self):
	token = None
	with Browser() as b:
	    b.get(self.iwencai_search_url)
	    content = b.content
	token_search = re.search(r'token":\s?"([^"]+)"', content)
	if token_search:
	    token = token_search.group(1)
	return token

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
	if request.url.startswith('http://www.iwencai.com/stockpick/cache?token=') and '{"code":130,"error":"token' in response.body:
	    self.iwencai_token = self.get_iwencai_token
	    retryreq = request.copy()    
            retryreq.dont_filter = True
	    return retryreq
        if response.status in [403, 500]:
	    self.iwencai_cookies = cookies_for_url(self.iwencai_search_url)
            retryreq = request.copy()
            retryreq.dont_filter = True
            return retryreq
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

