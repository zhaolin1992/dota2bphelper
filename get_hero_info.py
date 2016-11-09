import dota2api

from pymongo import MongoClient


from settings import API_KEY
import settings
ACCOUNT_ID = 172282397

# mysql_engine = sqlalchemy.create_engine("postgresql://{}@localhost/{}".format(settings.PSQL_USER,settings.PSQL_DB))
# #mysql_engine = sqlalchemy.create_engine('mysql+pymysql://root@localhost/bp_helper_db?charset=utf8')
# connection = mysql_engine.connect()
cn_api = dota2api.Initialise(API_KEY,language='zh-cn')
api = dota2api.Initialise(API_KEY)
db_client = MongoClient()
db = db_client.heroes

#hero_info
db.hero_info.drop()
cn_heroes = cn_api.get_heroes()["heroes"]
heroes = api.get_heroes()["heroes"]
for hero in heroes:
    for cn_hero in cn_heroes:
        if hero['id'] == cn_hero['id']:
            hero['cn_name'] = cn_hero['localized_name']
            continue
db.hero_info.insert(heroes)
