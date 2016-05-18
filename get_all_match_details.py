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
    c = 1
    while (c>0):
        start_match_seq=get_last_seq()
        print "last seq:"+str(start_match_seq)
        c = store_match(start_match_seq)
        print "this time got:"+str(c)


def get_last_seq():
    return db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"]

def store_match(start_match_seq):
    counter = 0
    for i in range(1,100):
        try:
            if (start_match_seq == 0):
                hist = api.get_match_history_by_seq_num()
            else:
                hist = api.get_match_history_by_seq_num(start_at_match_seq_num=start_match_seq+1)
            break
        except dota2api2.exceptions.APITimeoutError:
            print "timeout"
    for match_item in hist['matches']:
        if match_item['human_players'] < 10 or match_item['duration'] < 1200:
            print '*'
            continue
        for i in range(1,100):
            try:
                match_detail = api.get_match_details(match_id=match_item['match_id'])
                print "got detail:"+str(match_item['match_seq_num'])
                break
            except dota2api2.exceptions.APITimeoutError:
                print "timeout"
        #match_detail = match_item
        db.match.insert_one(match_detail)

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
        lobby_str = "lobby:"+str(match_detail['lobby_type'])
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
        if match_detail.has_key('game_mode'):
            mode_str = "mode:"+str(match_detail['game_mode'])
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
        #import pdb; pdb.set_trace()
        max_seq_num = max(db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"],match_detail["match_seq_num"])
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
