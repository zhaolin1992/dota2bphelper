import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import psycopg2
import psycopg2.extras
import settings
from sqlalchemy import *
from sqlalchemy.orm import *
import json

from pymongo import MongoClient

db_client = MongoClient()
hero_db = db_client.heroes

def get_hero_id(hero_str):
    res = hero_db.hero_info.find({"$or":[{"cn_name":hero_str},{"localized_name":hero_str}]})
    if (res.count() == 0):
        return None
    else:
        return res[0]["id"]

def get_hero_vs(hero_a_id,hero_b_id):
    comb_max_res = hero_db.max_hero_rate.find({"hero":hero_a_id,"rela":"comb"})[0]["matchup"]
    anti_buff_res = hero_db.buff_hero_rate.find({"hero":hero_a_id})[0]["matchup"]
    anti_max_res = hero_db.max_hero_rate.find({"hero":hero_a_id,"rela":"anti"})[0]["matchup"]

    comb_res = dict()
    anti_res = dict()

    for comb_max_item in comb_max_res:
        if hero_b_id == get_hero_id(comb_max_item["op_hero"]):
            comb_rate = float(comb_max_item["win_rate"].strip('%'))
            comb_ad = float(comb_max_item["advantage"].strip('%'))
            comb_res = {"comb_rate":comb_rate,"comb_ad":comb_ad,"comb_match":int(comb_max_item["match_count"])}

    for anti_buff_item in anti_buff_res:
        if hero_b_id == get_hero_id(anti_buff_item["op_hero"]):
            anti_ad = float(anti_buff_item["advantage"])
            anti_rate = float(anti_buff_item["win_rate"])
            anti_match = int(anti_buff_item["match_count"])
            anti_res = {"buff_anti_ad":anti_ad,"anti_rate":anti_rate,"buff_anti_match":anti_match}

    for anti_max_item in anti_max_res:
        if hero_b_id == get_hero_id(anti_max_item["op_hero"]):
            anti_ad=float(anti_max_item["advantage"].strip('%'))
            anti_rate=float(anti_max_item["win_rate"].strip('%'))
            anti_match=int(anti_max_item["match_count"])
            anti_res["anti_rate"] = round((anti_rate+anti_res["anti_rate"])/2,6)
            anti_res["max_anti_ad"] = anti_ad

    return {"comb":comb_res,"anti":anti_res}

def get_comb_hero_rate(hero_id):
    comb_max_res = hero_db.max_hero_rate.find({"hero":hero_id,"rela":"comb"})[0]["matchup"]

    rate_res = []
    for max_comb in comb_max_res:
        item_id = get_hero_id(max_comb["op_hero"])
        if (item_id != None):
            comb_rate = float(max_comb["win_rate"].strip('%'))
            comb_ad = float(max_comb["advantage"].strip('%'))
            rate_res.append({"hero_id":item_id,"comb_rate":comb_rate,"comb_ad":comb_ad,"comb_match":int(max_comb["match_count"])})
    rate_sorted_res = sorted(rate_res,key = lambda x:x["comb_rate"],reverse=True)[0:9]
    ad_sorted_res = sorted(rate_res,key = lambda x:x["comb_ad"],reverse=True)[0:9]
    return [rate_sorted_res,ad_sorted_res]

def get_all_hero_score(hero_id):
    return

def get_anti_hero_rate(hero_id):
    anti_buff_res = hero_db.buff_hero_rate.find({"hero":hero_id})[0]["matchup"]
    anti_max_res = hero_db.max_hero_rate.find({"hero":hero_id,"rela":"anti"})[0]["matchup"]

    rate_dict = dict()
    rate_res = []

    for buff_anti in anti_buff_res:
        item_id = get_hero_id(buff_anti["op_hero"])
        anti_ad=float(buff_anti["advantage"])
        anti_rate=float(buff_anti["win_rate"])
        anti_match=int(buff_anti["match_count"])
        rate_dict[item_id] = {"buff_anti_ad":anti_ad,"anti_rate":anti_rate,"buff_anti_match":anti_match}

    for max_anti in anti_max_res:
        item_id = get_hero_id(max_anti["op_hero"])
        anti_ad=float(max_anti["advantage"].strip('%'))
        anti_rate=float(max_anti["win_rate"].strip('%'))
        anti_match=int(max_anti["match_count"])
        rate_dict[item_id]["anti_rate"] = round((anti_rate+rate_dict[item_id]["anti_rate"])/2,6)
        rate_dict[item_id]["max_anti_ad"] = anti_ad
        rate_dict[item_id]["max_anti_match"] = anti_match

    for anti_item in rate_dict:
        rate_dict[anti_item]["hero_id"]=anti_item
        rate_res.append(rate_dict[anti_item])
        # rate_res.append()

    # max_rate_sorted_res = sorted(rate_res,key = lambda x:x["max_anti_rate"],reverse=True)[0:9]
    max_ad_sorted_res = sorted(rate_res,key = lambda x:x["max_anti_ad"],reverse=True)[0:9]
    rate_sorted_res = sorted(rate_res,key = lambda x:x["anti_rate"],reverse=True)[0:9]
    buff_ad_sorted_res = sorted(rate_res,key = lambda x:x["buff_anti_ad"],reverse=True)[0:9]
    return [max_ad_sorted_res,buff_ad_sorted_res,rate_sorted_res]



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
        (r"/hero_rate", HeroRateHandler),
        (r"/hero_vs", HeroSuggestHandler)
        ]

        settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class HeroRateHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            hero_id = int(self.get_argument('hero', True))
            comb_rate_arr = get_comb_hero_rate(hero_id)
            anti_rate_arr = get_anti_hero_rate(hero_id)
            self.write({"comb_rate":comb_rate_arr[0],"comb_ad":comb_rate_arr[1],"anti_max_ad":anti_rate_arr[0],"anti_buff_ad":anti_rate_arr[1],"anti_rate":anti_rate_arr[2]})
            # if (res.count() == 1):
            #     self.write(json.dumps(res1[0]["matchup"]))
        except AssertionError:
            self.write("no params")

class HeroSuggestHandler(tornado.web.RequestHandler):
    def get(self):
        hero_a_id = int(self.get_argument('hero_a', True))
        hero_b_id = int(self.get_argument('hero_b', True))
        self.write(get_hero_vs(hero_a_id,hero_b_id))

class HeroHandler(tornado.web.RequestHandler):
    def get(self):
        conn = psycopg2.connect("host='localhost' dbname={} user={}".format(settings.PSQL_DB,settings.PSQL_USER))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT localized_name as name,url_small_portrait as image_url,total_match,win_match\
        FROM dota2_hero,win_rate\
        WHERE dota2_hero.id = win_rate.hero_id \
        ;")
        all_result = cursor.fetchall()
        self.write(json.dumps(all_result).encode('utf8'))

        conn.close()




if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
