#!/usr/bin/env python
#coding:utf-8

import dota2api
from pymongo import MongoClient
import time
import pymongo
import pdb

import sqlalchemy
import psycopg2

# from api_key import API_KEY
# ACCOUNT_ID = 172282397
#
#
# api = dota2api.Initialise(API_KEY)
db_client = MongoClient()
db = db_client.match_data_details

def main():
    match_statics_init()
    #hero_static_init()

def match_statics_init():
    db.all_match_statics.drop()
    db.all_match_statics.insert({"match_code":"All match","count":0})
    db.max_seq_num.drop()
    db.max_seq_num.insert({"value_name":"max_seq_num","value":0})
    db.match.drop()
    db.match_id_pool.drop()

if __name__ == '__main__':
    main()
