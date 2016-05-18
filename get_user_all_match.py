#!/usr/bin/env python
#coding:utf-8

import pdb

import dota2api2
from pymongo import MongoClient
import time

from api_key import API_KEY
ACCOUNT_ID = 172282397

now_timestamp = int(time.time())
api = dota2api2.Initialise(API_KEY)
db_client = MongoClient()

def get_db_last_timestamp(arg):
    pass

def store_match_detail(maxtime):
    hist = api.get_match_history(account_id=ACCOUNT_ID,date_max=maxtime)
    for match_item in hist['matches']:
        for i in range(1,5):
            try:
                match = api.get_match_details(match_id=match_item['match_id'])
                break
            except dota2api2.exceptions.APITimeoutError:
                print "timeout"
        print match_item['match_id']
        radiant_player = [i for i in match['players'] if i['player_slot'] < 128]
        dire_player = [i for i in match['players'] if i['player_slot'] >= 128]

        radiant_hero = map((lambda x: x['hero_id']) ,radiant_player)
        dire_hero = map((lambda x: x['hero_id']) ,dire_player)

        print radiant_hero
        print dire_hero
