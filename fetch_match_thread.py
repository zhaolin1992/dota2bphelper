from api_get_data import *
import time

from tornado import httpclient, gen, ioloop, queues

concurrency = 10

@gen.coroutine
def fetch_match():
    start_match_seq=get_last_seq()
    logging.info("last seq:"+str(start_match_seq))
    match_arr = get_match_id_arr(start_match_seq)
    add_to_pool(match_arr)
    max_id = max(match_arr)
    update_max_seq(max_id)

@gen.coroutine
def handle_match_detail():
    while(1):
        match_id = find_one_in_pool()
        if match_id>0:
            mark_in_pool(match_id,0)
            if save_match_detail_by_id(match_id):
                mark_in_pool(match_id,1)

@gen.coroutine
def fetch_detail():
    # fetch_match()
    for _ in range(concurrency):
        handle_match_detail()

if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(fetch_detail)
