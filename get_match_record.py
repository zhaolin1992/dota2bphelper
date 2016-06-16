import dota2api
from pymongo import MongoClient
import time
import pymongo
from pandas import DataFrame, Series
import pandas as pd
import numpy as np

import sys

import json
from bson import BSON
from bson import json_util

db_client = MongoClient()
db = db_client.match_data_details

statics_db = db_client.match_statics

import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    if len(sys.argv)>1 and sys.argv[1] == "init":
        hero_static_init()
    else:
        max_seq = get_last_seq()
        logging.info(max_seq)
        record_match_data(max_seq)
def get_last_seq():
    return statics_db.max_solved_seq_num.find({"value_name":"max_solved_seq_num"})[0]["value"]

def record_match_data(min_seq):
    matches = db.match.find({"match_seq_num": { '$gt': min_seq } })
    # import pdb; pdb.set_trace()
    for match in matches:
        if match["human_players"] == 10 and match["duration"] > 1200:

            data_frame = DataFrame(match["players"])
            radiant_heroes = data_frame[data_frame['player_slot']<128]['hero_id'].tolist()
            dire_heroes = data_frame[data_frame['player_slot']>=128]['hero_id'].tolist()
            for index, row in data_frame.iterrows():
                if (row["player_slot"] < 128):
                    radiant_heroes.remove(row["hero_id"])
                    teammate = radiant_heroes
                    opponent = dire_heroes
                    is_win = bool(match["radiant_win"])
                else:
                    dire_heroes.remove(row["hero_id"])
                    teammate = dire_heroes
                    opponent = radiant_heroes
                    is_win = not bool(match["radiant_win"])
                record_json = json.loads(row.to_json())
                record_json['win'] = is_win
                record_json['match_id'] = match['match_id']
                record_json['match_seq'] = match['match_seq_num']
                record_json['teammate'] = teammate
                record_json['opponent'] = opponent

                item = []

                for x in range(0,6):
                    if record_json["item_{}".format(x)]>0:
                        if "item_{}" in record_json:
                            item.append(record_json["item_{}".format(x)])
                            del record_json["item_{}".format(x)]
                        if "item_{}_name" in record_json:
                            del record_json["item_{}_name".format(x)]

                record_json['item'] = item

                count = statics_db.match_record.find({'$and':[{'hero_id':row['hero_id']},{'match_id':match['match_id']}]}).count()
                if count == 0:
                    statics_db.match_record.insert_one(record_json)
            max_solved_seq_num = max(statics_db.max_solved_seq_num.find({"value_name":"max_solved_seq_num"})[0]["value"],match["match_seq_num"])
            statics_db.max_solved_seq_num.update_one(
                {"value_name":"max_solved_seq_num"},
                {
                    "$set":
                    {
                        "value":max_solved_seq_num
                    },
                    "$currentDate": {"lastModified": True}
                }
            )
            logging.info("match handle:"+str(max_solved_seq_num))
def hero_static_init():
    statics_db.max_solved_seq_num.drop()
    statics_db.max_solved_seq_num.insert_one({"value_name":"max_solved_seq_num","value":0})
    statics_db.match_record.drop()

    conn = psycopg2.connect("host='localhost' dbname={} user={}".format(settings.PSQL_DB,settings.PSQL_USER))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM dota2_hero;")
    # records = cursor.fetchall()
    # for r in records:
    #         r[0]
    conn.close()


if __name__ == '__main__':
    main()
