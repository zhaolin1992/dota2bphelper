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
    get_player_data(sys.argv[1],sys.argv[2])


def get_player_data(user_id,start_id):
    for i in range(1,100):
        try:
            if (start_id == 0):
                hist = api.get_match_history(account_id=user_id)
            else:
                hist = api.get_match_history(account_id=user_id,start_at_match_id=start_id)
            break
        except dota2api.exceptions.APITimeoutError:
            logging.info("timeout")
    for match_item in hist['matches']:
        print match_item['match_id']

if __name__ == '__main__':
    main()
