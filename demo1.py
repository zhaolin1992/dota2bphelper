#!/usr/bin/env python

# -*- coding: utf-8 -*-

import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import pymongo
import psycopg2


define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
        (r"/", MainHandler),
        # (r"/hero", HeroHandler),
        ]
        settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        )

        psql_conn = psycopg2.connect("host='localhost' dbname=dota2bphelper user=dam0n")
        psql_cursor = psql_conn.cursor()

        mongo_db_client = pymongo.MongoClient()
        mongo_db = mongo_db_client.match_statics

        self.db = mongo_db
        self.psql = psql_cursor
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        psql_cursor = self.application.psql
        psql_cursor.execute("SELECT * FROM dota2_hero;")
        hero_records = psql_cursor.fetchall()

        mongo_db = self.application.db
        print '.'
        heroes_match_info = []
        for record in hero_records:
            hero_match = mongo_db.match_record.find({"hero_id":int(record[1])})
            hero_win_match = mongo_db.match_record.find({"$and":[{"hero_id":int(record[1])},{"win":True}]})
            hero_info = dict()
            hero_info['name'] = record[2]
            hero_info['total_match'] = hero_match.count()
            hero_info['win_match'] = hero_win_match.count()
            hero_info['image_url'] = record[6]
            heroes_match_info.append(hero_info)
        self.render("index.html",
        page_title="hero win rate",
        info=heroes_match_info,
        )

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
