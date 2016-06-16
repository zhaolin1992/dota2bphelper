import dota2api

from pandas import DataFrame, Series
import pandas as pd
import numpy as np

import sqlalchemy

from settings import API_KEY
import settings
ACCOUNT_ID = 172282397

mysql_engine = sqlalchemy.create_engine("postgresql://{}@localhost/{}".format(settings.PSQL_USER,settings.PSQL_DB))
#mysql_engine = sqlalchemy.create_engine('mysql+pymysql://root@localhost/bp_helper_db?charset=utf8')
connection = mysql_engine.connect()
api = dota2api.Initialise(API_KEY)

#hero_info
heroes = api.get_heroes(language='zh')["heroes"]
heroes_df = DataFrame(heroes)
heroes_df.to_sql('dota2_hero',mysql_engine,if_exists='replace')
#item_info
items = api.get_game_items(language='zh')["items"]
items_df = DataFrame(items)
items_df.to_sql('dota2_item',mysql_engine,if_exists='replace')
