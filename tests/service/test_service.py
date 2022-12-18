import threading

from SingleLog import Logger

import PyPtt
from PyPtt import Service
from tests import config


def api_test(thread_id, service):
    logger = Logger(f'api_test_{thread_id}')

    result = service.call('get_time')
    logger.info('get_time', result)

    result = service.call('get_aid_from_url', {'url': 'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'})
    logger.info('get_aid_from_url', result)

    result = service.call('get_newest_index', {'index_type': PyPtt.NewIndex.BOARD, 'board': 'Python'})
    logger.info('get_newest_index', result)


def test():

    pyptt_init_config = {
        # 'language': PyPtt.Language.ENGLISH,
    }

    service = Service(pyptt_init_config)

    try:

        service.call('login', {'ptt_id': config.PTT1_ID, 'ptt_pw': config.PTT1_PW})

        pool = []
        for i in range(10):
            t = threading.Thread(target=api_test, args=(i, service))
            t.start()
            pool.append(t)

        for t in pool:
            t.join()

        service.call('logout')
    finally:
        service.close()


if __name__ == '__main__':
    test()
    # pass
