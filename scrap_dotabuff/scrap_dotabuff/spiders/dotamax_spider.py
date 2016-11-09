# -*- coding: utf-8 -*-
import scrapy
from scrap_dotabuff.items import *
import logging
import re
# from db_info import *
class dotamaxSpider(scrapy.Spider):
    name = "dotamax"
    allowed_domains = ["dotamax.com"]
    start_urls = [
        "http://www.dotamax.com/hero/rate",
        ]

    def parse(self, response):
        root_url = "http://dotamax.com"

        if response.status == 200:
            hero_set = response.xpath("//table[@class='sortable table-list']/tbody/tr/@onclick").extract()
            for hero_id_item in hero_set:
                hero_id = re.findall(r"DoNav\('/hero/detail/(.*)'\)",hero_id_item)[0]
                self.logger.info("get hero: %s",hero_id)
                for rela in ['anti','comb']:
                    callback_func = eval('self.parse_hero_'+rela+'_rate')
                    req = scrapy.Request(root_url+"/hero/detail/match_up_"+rela+"/"+hero_id,callback=callback_func)
                    yield req
                # req_anti = None
                # req_comb = None
                # req_anti = scrapy.Request(root_url+"/hero/detail/match_up_anti/"+hero_id,callback=self.parse_hero_anti_rate)
                # req_comb = scrapy.Request(root_url+"hero/detail/match_up_comb/"+hero_id,callback=self.parse_hero_comb_rate)
                # self.logger.info("get %s", hero_id)
                # req_anti.meta['item'] = Item()
                # yield req_comb
                # yield req_comb

    def parse_hero_anti_rate(self, response):
        if response.status == 200:
            data_item = ScrapdotamaxItem()
            hero_node = response.xpath("//span[@class='hero-title']/node()").extract()
            try:
                data_item["hero"] = hero_node[0].strip()
            except Exception:
                self.logger.warning("missing")
                yield None
            data_set = response.xpath("//table[@class='table table-hover table-striped sortable table-list table-thead-left']/tbody//tr")
            rate_item_arr = []
            for hero_data in data_set:
                rate_item = MatchupItem()
                rate_item['op_hero'],rate_item['advantage'],rate_item['win_rate'],rate_item['match_count'] = hero_data.xpath("td/span/node()|td/div/node()").extract()
                rate_item_arr.append(rate_item)
            data_item["matchup"] = rate_item_arr
            data_item["rela"] = "anti"
        yield data_item

    def parse_hero_comb_rate(self, response):
        if response.status == 200:
            data_item = ScrapdotamaxItem()
            hero_node = response.xpath("//span[@class='hero-title']/node()").extract()
            try:
                data_item["hero"] = hero_node[0].strip()
            except Exception:
                self.logger.warning("missing")
                return None
            data_set = response.xpath("//table[@class='table table-hover table-striped sortable table-list table-thead-left']/tbody//tr")
            rate_item_arr = []
            for hero_data in data_set:
                rate_item = MatchupItem()
                rate_item['op_hero'],rate_item['advantage'],rate_item['win_rate'],rate_item['match_count'] = hero_data.xpath("td/span/node()|td/div/node()").extract()
                rate_item_arr.append(rate_item)
            data_item["matchup"] = rate_item_arr
            data_item["rela"] = "comb"
        yield data_item
