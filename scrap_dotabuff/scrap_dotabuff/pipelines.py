# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrap_dotabuff.items import *
import json
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy import signals
from pydispatch import dispatcher

_encoder = ScrapyJSONEncoder()
db_client = MongoClient()
db = db_client.heroes

def get_hero_id(hero_str):
    res = db.hero_info.find({"$or":[{"cn_name":hero_str},{"localized_name":hero_str}]})
    if (res.count() == 0):
        return None
    else:
        return res[0]["id"]


class ScrapdotabuffPipeline(object):
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
    def process_item(self, item, spider):
        # import pdb; pdb.set_trace()
        # print(item["hero"])
        item["hero"] = get_hero_id(item["hero"])
        if spider.name == "dotabuff":
            db.buff_hero_rate.insert(json.loads(_encoder.encode(item)))
        elif spider.name == "dotamax":
            db.max_hero_rate.insert(json.loads(_encoder.encode(item)))
        return item
    def spider_opened(self, spider):
        if spider.name == "dotabuff":
            db.buff_hero_rate.drop()
        elif spider.name == "dotamax":
            db.max_hero_rate.drop()
