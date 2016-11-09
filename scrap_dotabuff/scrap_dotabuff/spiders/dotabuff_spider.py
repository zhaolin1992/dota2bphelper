import scrapy
from scrap_dotabuff.items import *
import logging
class dotabuffSpider(scrapy.Spider):
    name = "dotabuff"
    allowed_domains = ["dotabuff.com"]
    start_urls = [
        "http://www.dotabuff.com/heroes",
        ]

    def parse(self, response):
        root_url = "http://zh.dotabuff.com"
        if response.status == 200:
            # data_set = response.xpath("//table[@class='sortable']/tbody//tr")#.xpath('//td[@class="cell-xlarge"]').extract()
            hero_set = response.xpath("//div[@class='hero-grid']//a/@href").extract()
            for hero_sub_url in hero_set:
                yield scrapy.Request(root_url+hero_sub_url+"/matchups",callback=self.parse_hero_rate)

    def parse_hero_rate(self, response):
        if response.status == 200:
            data_item = ScrapdotabuffItem()
            data_item["hero"] = response.xpath("//div[@class='header-content-title']/h1/node()")[0].extract()
            data_set = response.xpath("//table[@class='sortable']/tbody//tr")
            rate_item_arr = []
            for hero_data in data_set:
                rate_item = MatchupItem()
                rate_item['op_hero'],rate_item['advantage'],rate_item['win_rate'],rate_item['match_count'] = hero_data.xpath("td/@data-value").extract()
                rate_item_arr.append(rate_item)
            data_item["matchup"] = rate_item_arr
        yield data_item
