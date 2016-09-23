from api_get_data import *
import time

from tornado import httpclient, gen, ioloop, queues

concurrency = 10

@gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched = set(), set()
    last_seq = 0

    @gen.coroutine
    def fetch_match_data():
        match_seq = yield q.get()
        try:
            if match_seq in fetching:
                return

            # print('fetching %s' % current_url)
            fetching.add(match_seq)
            save_match_detail_by_id(match_seq)
            # urls = yield get_links_from_url(current_url)
            fetched.add(match_seq)

            # for new_url in urls:
            #     # Only follow links beneath the base URL
            #     if new_url.startswith(base_url):
            #         yield q.put(new_url)

        finally:
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            yield fetch_match_data()

    start_match_seq=get_last_seq()
    logging.info("last seq:"+str(start_match_seq))
    match_gen = get_match_id_arr(start_match_seq)

    for match in match_gen:
        if match > last_seq:
            last_seq = match
        q.put(match)

    # Start workers, then wait for the work queue to be empty.
    for _ in range(concurrency):
        worker()
    # assert fetching == fetched
    # print('Done in %d seconds, fetched %s URLs.' % (
    #     time.time() - start, len(fetched)))
    if fetching == fetched:
        print('Done in %d seconds, fetched %s matches.' % (
             time.time() - start, len(fetched)))
        update_max_seq(last_seq)



if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
