# -*- coding: utf-8 -*-
import scrapy


class DotabuffSpider(scrapy.Spider):
    name = "dotabuff"
    allowed_domains = ["dotabuff.com"]
    start_urls = ['http://dotabuff.com/']

    def parse(self, response):
        pass
