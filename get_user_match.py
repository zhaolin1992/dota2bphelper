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
db = db_client.user_match_data

def main():
    start_match_id=get_id_for_front_timestamp(ACCOUNT_ID)
    print start_match_id
    store_match_detail(start_match_id)



def get_id_for_front_timestamp(account_id):
    result = db.match.find({"account":account_id}).sort("start_time",1)
    if (result.count()==0):
        return 0
    else:
        return result[0]["match_id"]


def store_match_detail(start_match_id):
    for i in range(1,5):
        try:
            if (start_match_id == 0):
                hist = api.get_match_history(account_id=ACCOUNT_ID)
            else:
                hist = api.get_match_history(account_id=ACCOUNT_ID,start_at_match_id=start_match_id)
            break
        except dota2api2.exceptions.APITimeoutError:
            print "timeout"

    for match_item in hist['matches']:
        for i in range(1,5):
            try:
                match = api.get_match_details(match_id=match_item['match_id'])
                break
            except dota2api2.exceptions.APITimeoutError:
                print "timeout"

        play_detail = [i for i in match['players'] if i['account_id'] == ACCOUNT_ID][0]

        radiant_player = [i for i in match['players'] if (i['player_slot'] < 128 and i['account_id'] != ACCOUNT_ID)]
        dire_player = [i for i in match['players'] if (i['player_slot'] >= 128 and i['account_id'] != ACCOUNT_ID)]

        if (play_detail['player_slot'] < 128):
            is_win = match['radiant_win']
            teammate = radiant_player
            opponent = dire_player
        else:
            is_win = not match['radiant_win']
            opponent = radiant_player
            teammate = dire_player

        match_detail = {
            "is_win":is_win,
            "duration":match['duration'],
            "lobby":match['lobby_type'],
            "game_mode":match['game_mode'],
        }

        match_data = {
            "account":ACCOUNT_ID,
            "start_time":match['start_time'],
            "match_id":match['match_id'],
            "match_detail":match_detail,
            "play_detail":play_detail,
            "teammate":teammate,
            "opponent":opponent,
        }
        if (db.match.find({"match_id":match['match_id']}).count() == 0):
            db.match.insert_one(match_data)
            print match['match_id']
if __name__ == '__main__':
    main()
