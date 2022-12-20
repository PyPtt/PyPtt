import threading
import time
import uuid

from SingleLog import DefaultLogger

import PyPtt
from PyPtt import check_value


class Service:

    def __init__(self, pyptt_init_config: dict = {}):

        """

        這是一個可以在多執行緒中使用的 PyPtt API 服務。

        | 請注意：這僅僅只是 Thread Safe 的實作，對效能並不會有實質上的幫助。
        | 如果你需要更好的效能，請在每一個線程都使用一個 PyPtt.API 本身。

        Args:
            pyptt_init_config (dict): PyPtt 初始化設定，請參考 :ref:`初始化設定 <api-init>`。

        Returns:
            None

        範例::

            from PyPtt import Service

            def api_test(thread_id, service):

                result = service.call('get_time')
                print(f'thread id {thread_id}', 'get_time', result)

                result = service.call('get_aid_from_url', {'url': 'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'})
                print(f'thread id {thread_id}', 'get_aid_from_url', result)

                result = service.call('get_newest_index', {'index_type': PyPtt.NewIndex.BOARD, 'board': 'Python'})
                print(f'thread id {thread_id}', 'get_newest_index', result)

            if __name__ == '__main__':
                pyptt_init_config = {
                    # 'language': PyPtt.Language.ENGLISH,
                }

                service = Service(pyptt_init_config)

                try:
                    service.call('login', {'ptt_id': 'YOUR_PTT_ID', 'ptt_pw': 'YOUR_PTT_PW'})

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
        """

        self._log = DefaultLogger('Service')
        self._log.info('init')

        self._api = None
        self._api_init_config = pyptt_init_config

        self._call_queue = []
        self._call_result = {}

        self._id_pool = set()
        self._id_pool_lock = threading.Lock()

        self._close = False

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        while self._api is None:
            time.sleep(0.01)

    def _run(self):

        if self._api is not None:
            self._api.logout()
            self._api = None

        self._api = PyPtt.API(**self._api_init_config)

        self._log.info('start')

        while not self._close:
            if len(self._call_queue) == 0:
                time.sleep(0.05)
                continue

            call = self._call_queue.pop(0)

            func = getattr(self._api, call['api'])

            api_result = None
            api_exception = None
            try:
                api_result = func(**call['args'])
            except Exception as e:
                api_exception = e

            self._call_result[call['id']] = {
                'result': api_result,
                'exception': api_exception
            }

    def _get_call_id(self):
        while True:
            call_id = uuid.uuid4().hex

            with self._id_pool_lock:
                if call_id not in self._id_pool:
                    self._id_pool.add(call_id)
                    return call_id

    def call(self, api: str, args: dict = {}):

        if args is None:
            args = {}

        check_value.check_type(api, str, 'api')
        check_value.check_type(args, dict, 'args')

        if api not in dir(self._api):
            raise ValueError(f'api {api} not found')

        call = {
            'api': api,
            'id': self._get_call_id(),
            'args': args
        }
        self._call_queue.append(call)

        while call['id'] not in self._call_result:
            time.sleep(0.01)

        call_result = self._call_result[call['id']]
        del self._call_result[call['id']]

        with self._id_pool_lock:
            self._id_pool.remove(call['id'])

        if call_result['exception'] is not None:
            raise call_result['exception']

        return call_result['result']

    def close(self):
        self._log.info('close')
        self._close = True
        self._thread.join()

        self._log.info('done')
