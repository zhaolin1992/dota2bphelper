# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MatchupItem(scrapy.Item):
    # define the fields for your item here like:
    op_hero = scrapy.Field()
    advantage = scrapy.Field()
    win_rate = scrapy.Field()
    match_count = scrapy.Field()
    pass

class ScrapdotabuffItem(scrapy.Item):
    hero = scrapy.Field()
    matchup = scrapy.Field()
    pass

class ScrapdotamaxItem(scrapy.Item):
    hero = scrapy.Field()
    matchup = scrapy.Field()
    rela = scrapy.Field()
    pass
