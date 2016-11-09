import dota2api
from pymongo import MongoClient
import time
import pymongo
import logging


from settings import API_KEY

api = dota2api.Initialise(api_key=API_KEY)
db_client = MongoClient()
db = db_client.match_data_details
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

# def init():
#     global api,db
#     api = dota2api.Initialise(api_key=API_KEY,language='zh-cn')
#     db_client = MongoClient()
#     db = db_client.match_data_details
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pull_player_data(user_id):
    start_id = 0
    while(1):
        start_id = __get_player_data(user_id,start_id)
        add_to_pool()
        if start_id < 0:
            break

def get_match_data():
    c = 1
    while (c>0):
        start_match_seq=get_last_seq()
        logging.info("last seq:"+str(start_match_seq))
        c = get_and_store_match_detail(start_match_seq+1)
        logging.info("this time got:"+str(c))

def match_id_gen():
    start_match_seq=get_last_seq()
    return get_match_id_arr(start_match_seq)

def get_match_id_arr(start_match_seq):
    for i in range(1,10):
        try:
            if start_match_seq == 0:
                hist = api.get_match_history_by_seq_num()
            else:
                hist = api.get_match_history_by_seq_num(start_at_match_seq_num=start_match_seq)
            break
        except dota2api.exceptions.APITimeoutError:
            logging.error("timeout")
    # for match_item in hist['matches']:
    #     yield match_item['match_id']
    return list(map(lambda match_item:match_item['match_id'],hist['matches']))

def get_and_store_match_detail(start_match_seq):
    counter = 0
    for i in range(1,100):
        try:
            if (start_match_seq == 0):
                hist = api.get_match_history_by_seq_num()
            else:
                hist = api.get_match_history_by_seq_num(start_at_match_seq_num=start_match_seq)
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
                ret = save_match_detail_by_id(match_item['match_id'])
                logging.info("got detail:"+str(match_item['match_seq_num']))
                #print("got detail:"+str(match_item['match_seq_num']))
                break
            except dota2api.exceptions.APITimeoutError:
                logging.error("timeout")
        #match_detail = match_item
        # db.match.insert_one(match_detail)

        if (ret == 1):
            import pdb; pdb.set_trace()
            update_max_seq(match_item['match_seq_num'])
            counter += 1
    return counter

def get_last_seq():
    return db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"]

def update_max_seq(seq):
    max_seq_num = max(db.max_seq_num.find({"value_name":"max_seq_num"})[0]["value"],seq)
    db.max_seq_num.update(
        {"value_name":"max_seq_num"},
        {
            "$set":
            {
                "value":max_seq_num
            },
            "$currentDate": {"lastModified": True}
        }
    )

def save_match_detail_by_id(match_id):
    if db.match.find({"match_id":match_id}).count() == 0:
        logging.debug("save:"+str(match_id))
        match_detail = api.get_match_details(match_id=match_id)
        db.match.insert(match_detail)
        return 1
    else:
        logging.warning("not save:"+str(match_id))
        return 0

def add_to_pool(match_id_array):
    db_array = list(map(lambda id:{"match_id":id,"state":"unfetch"},match_id_array))
    db.match_id_pool.insert(db_array)

def find_one_in_pool():
    match_id_info = db.match_id_pool.find_one({"state":"unfetch"})
    if match_id_info:
        return match_id_info["match_id"]
    else:
        return 0

def mark_in_pool(match_id,status):
    status_str = ["fetching","fetched"]
    match_count = db.match_id_pool.find({"match_id":match_id}).count()
    if match_count == 1:
        if db.match_id_pool.find({"match_id":match_id,"state":status_str[status]}).count() == 0:
            db.match_id_pool.update(
                {"match_id":match_id},
                {
                    "$set":
                    {
                        "state":status_str[status]
                    },
                    "$currentDate": {"lastModified": True}
                }
            )
            return 1
        else:
        # db.match_id_pool.remove({"match_id":match_id})
            return 0
    else:
        logging.error("match id num error:"+str(match_id))
        return 0

def pull_player_data(user_id):
    min_match_id = 0
    while (1):
        id_arr = get_player_match_data(user_id,min_match_id)
        if len(id_arr)>0:
            add_to_pool(id_arr)
            min_match_id = min(id_arr) - 1
        else:
            break
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
        save_match_detail_by_id(match_item['match_id'])
        # match_detail = api.get_match_details(match_id=match_item['match_id'])
        # logging.info("got detail:"+str(match_item['match_seq_num']))
    if (min_start_id == start_id):
        min_start_id = 0
    return min_start_id-1

def get_player_match_data(user_id,start_id):
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
    return list(map(lambda match_item:match_item['match_id'],hist['matches']))


# def push_unfetched(match_id):
#     if db.unfetch.find({"match_id":match_id}).count() == 0:
#         db.unfetch.insert({"match_id":match_id})
#         logging.debug("add fetching:"+str(match_id))
#     else:
#         logging.error("match id duplicate:"+str(match_id))
#
# def pull_unfetched(match_id):
#     if db.unfetch.find({"match_id":match_id}).count() > 0:
#         db.unfetch.remove({"match_id":match_id})
#         logging.debug("remove fetching:"+str(match_id))
#     else:
#         logging.error("match id num error:"+str(match_id))
