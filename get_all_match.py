#!/usr/bin/env python
#coding:utf-8

import dota2api2
from pymongo import MongoClient
import time
import pymongo
import pdb

from api_key import API_KEY
ACCOUNT_ID = 172282397


api = dota2api2.Initialise(API_KEY)
db_client = MongoClient()
db = db_client.match_data_details

def main():
    start_match_seq=get_last_seq()
    print "last seq:"+str(start_match_seq)
    c = 1
    while (c>0):
        c = store_match(get_last_seq)
        print "this time got:"+str(c)

def get_last_seq():
    return db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"]
def match_statics_init():
    db.all_match_statics.drop()
    db.all_match_statics.insert_one({"match_code":"All match","count":0})
    db.max_seq_num.drop()
    db.max_seq_num.insert_one({"value_name":"max_seq_num","value":0})
def store_match(start_match_seq):
    counter = 0
    for i in range(1,100):
        try:
            if (start_match_seq == 0):
                hist = api.get_match_history_by_seq_num()
            else:
                hist = api.get_match_history_by_seq_num(start_at_match_seq_num=start_match_seq)
            break
        except dota2api2.exceptions.APITimeoutError:
            print "timeout"
    for match_item in hist['matches']:
        db.match.insert_one(match_item)

        #all match
        existing = db.all_match_statics.find({"match_code":"All match"})[0]["count"]
        db.all_match_statics.update_one(
            {"match_code":"All match"},
            {
                "$set":
                {
                    "count":existing+1
                },
                "$currentDate": {"lastModified": True}
            }
        )
        #lobby_type
        lobby_str = "lobby:"+str(match_item['lobby_type'])
        if db.all_match_statics.find({"match_code":lobby_str}).count() > 0:
            db.all_match_statics.update_one(
                {"match_code":lobby_str},
                {
                    "$set":
                    {
                        "count":db.all_match_statics.find({"match_code":lobby_str})[0]["count"]+1
                    },
                    "$currentDate": {"lastModified": True}
                }
            )
        else:
            db.all_match_statics.insert_one({"match_code":lobby_str,"count":1})
        #game mode
        if match_item.has_key('game_mode'):
            mode_str = "mode:"+str(match_item['game_mode'])
            if db.all_match_statics.find({"match_code":mode_str}).count() > 0:
                db.all_match_statics.update_one(
                    {"match_code":mode_str},
                    {
                        "$set":
                        {
                            "count":db.all_match_statics.find({"match_code":mode_str})[0]["count"]+1
                        },
                        "$currentDate": {"lastModified": True}
                    }
                )
            else:
                db.all_match_statics.insert_one({"match_code":mode_str,"count":1})

        db.all_match_statics.update_one(
            {"match_code":"All match"},
            {
                "$set":
                {
                    "count":existing+1
                },
                "$currentDate": {"lastModified": True}
            }
        )

        max_seq_num = max(db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"],match_item["match_seq_num"])
        db.max_seq_num.update_one(
            {"value_name":"max_seq_num"},
            {
                "$set":
                {
                    "value":max_seq_num
                },
                "$currentDate": {"lastModified": True}
            }
        )
        counter += 1
    return counter
if __name__ == '__main__':
    main()
