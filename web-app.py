import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import psycopg2
import psycopg2.extras
import pymongo
import settings
from sqlalchemy import *
from sqlalchemy.orm import *
import json

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
        (r"/", MainHandler),
        (r"/hero_rate", HeroHandler)
        ]

        settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

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


        # self.render("index.html",hero_rate=all_result)
        conn.close()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
