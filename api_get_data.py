import dota2api
from pymongo import MongoClient
import time
import pymongo
import logging


from settings import API_KEY

api = dota2api.Initialise(api_key=API_KEY,language='zh-cn')
db_client = MongoClient()
db = db_client.match_data_details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# def init():
#     global api,db
#     api = dota2api.Initialise(api_key=API_KEY,language='zh-cn')
#     db_client = MongoClient()
#     db = db_client.match_data_details
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_match_data():
    c = 1
    while (c>0):
        start_match_seq=__get_last_seq()
        logging.info("last seq:"+str(start_match_seq))
        c = __get_and_store_match_detail(start_match_seq+1)
        logging.info("this time got:"+str(c))

def __get_and_store_match_detail(start_match_seq):
    counter = 0
    for i in range(1,100):
        try:
            if (start_match_seq == 0):
                hist = api.get_match_history_by_seq_num()
            else:
                hist = api.get_match_history_by_seq_num(start_at_match_seq_num=start_match_seq+1)
            break
        except dota2api.exceptions.APITimeoutError:
            logging.info("timeout")
    for match_item in hist['matches']:
        ret = 0
        if match_item['human_players'] < 10 or match_item['duration'] < 300:
            logging.info('*')
            continue
        for i in range(1,100):
            try:
                # match_detail = api.get_match_details(match_id=match_item['match_id'])
                ret = __save_match_detail_by_id(match_item['match_id'])
                logging.info("got detail:"+str(match_item['match_seq_num']))
                #print("got detail:"+str(match_item['match_seq_num']))
                break
            except dota2api.exceptions.APITimeoutError:
                logging.info("timeout")
        #match_detail = match_item
        # db.match.insert_one(match_detail)


        if (ret == 1):
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

def __save_match_detail_by_id(match_id):
    if db.match.find({"match_id":match_id}).count() == 0:
        logging.info("save:"+str(match_id))
        match_detail = api.get_match_details(match_id=match_id)
        db.match.insert_one(match_detail)
        return 1
    else:
        logging.info("not save:"+str(match_id))
        return 0

def __get_player_data(user_id,start_id):
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
        __save_match_detail_by_id(match_item['match_id'])
        # match_detail = api.get_match_details(match_id=match_item['match_id'])
        # logging.info("got detail:"+str(match_item['match_seq_num']))
    if (min_start_id == start_id):
        min_start_id = 0
    return min_start_id-1

def __get_last_seq():
    return db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"]

def get_player_data(user_id):
    start_id = 0
    while(1):
        start_id = __get_player_data(user_id,start_id)
        if start_id < 0:
            break
