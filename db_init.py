#!/usr/bin/env python
#coding:utf-8

import dota2api2
from pymongo import MongoClient
import time
import pymongo
import pdb

import sqlalchemy
import psycopg2

from api_key import API_KEY
ACCOUNT_ID = 172282397


api = dota2api2.Initialise(API_KEY)
db_client = MongoClient()
db = db_client.match_data_details

def main():
    match_statics_init()
    #hero_static_init()

def match_statics_init():
    db.all_match_statics.drop()
    db.all_match_statics.insert_one({"match_code":"All match","count":0})
    db.max_seq_num.drop()
    db.max_seq_num.insert_one({"value_name":"max_seq_num","value":0})
    db.match.drop()

if __name__ == '__main__':
    main()
