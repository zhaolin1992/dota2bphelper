#!/usr/bin/env python
#coding:utf-8

import dota2api2
from pymongo import MongoClient
import time

from api_key import API_KEY
ACCOUNT_ID = 172282397

api = dota2api2.Initialise(API_KEY)

k = 0

hist = api.get_match_history(account_id=ACCOUNT_ID)
for match_item in hist['matches']:
    for i in range(1,5):
        try:
            match = api.get_match_details(match_id=match_item['match_id'])
            break
        except dota2api2.exceptions.APITimeoutError:
            print "timeout"
    print match_item['match_id']
    if (([i for i in match['players'] if i['account_id'] == ACCOUNT_ID][0]['player_slot'] < 5)==match['radiant_win']):
        k += 1
        print 'win'
    else:
        print 'lose'
    #time.sleep(1)

print k
