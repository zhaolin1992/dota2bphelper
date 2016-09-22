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

from settings import API_KEY

api = dota2api.Initialise(API_KEY)
db_client = MongoClient()
db = db_client.match_data_details

statics_db = db_client.match_statics

import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    get_player_data(sys.argv[1])

def get_player_data(user_id):
    start_id = 0
    while(1):
        start_id = _get_player_data(user_id,start_id)
        if start_id < 0:
            break


def _get_player_data(user_id,start_id):
    min_start_id = 0xFFFFFFFF
    for i in range(1,100):
        try:
            if (start_id == 0):
                min_start_id = 0xFFFFFFFF
                hist = api.get_match_history(account_id=user_id)
            else:
                min_start_id = start_id
                hist = api.get_match_history(account_id=user_id,start_at_match_id=start_id)
            break
        except dota2api.exceptions.APITimeoutError:
            logging.info("timeout")
    for match_item in hist['matches']:
        if (match_item['match_id'] < min_start_id):
            min_start_id = match_item['match_id']
        # print match_item['match_id']
        save_match_by_id(match_item['match_id'])
        # match_detail = api.get_match_details(match_id=match_item['match_id'])
        # logging.info("got detail:"+str(match_item['match_seq_num']))
    if (min_start_id == start_id):
        min_start_id = 0
    return min_start_id-1

def save_match_by_id(match_id):
    if db.match.find({"match_id":match_id}).count() == 0:
        logging.info("save:"+str(match_id))
        match_detail = api.get_match_details(match_id=match_id)
        db.match.insert_one(match_detail)
    else:
        logging.info("not save:"+str(match_id))

if __name__ == '__main__':
    main()
