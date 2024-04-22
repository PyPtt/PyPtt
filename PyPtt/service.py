import queue
import threading
import time
from queue import Queue
from threading import Condition
from typing import Optional

from . import PTT
from . import check_value
from . import log


class Service:

    def __init__(self, pyptt_init_config: Optional[dict] = None):

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
        if pyptt_init_config is None:
            pyptt_init_config = {}

        log_level = pyptt_init_config.get('log_level', log.INFO)
        self.logger = log.init(log_level, 'service')

        self.logger.info('init')

        self._api = None
        self._api_init_config = pyptt_init_config

        self._call_queue = Queue()
        self._call_result = {}
        self._call_result_cv = Condition()

        self._id_pool = {}

        self._close = False

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        while self._api is None:
            time.sleep(0.01)

    def _run(self):
        if self._api is not None:
            self._api.logout()
            self._api = None

        self._api = PTT.API(**self._api_init_config)

        self.logger.info('start')

        while not self._close:
            try:
                call = self._call_queue.get(timeout=0.05)
            except queue.Empty:
                continue

            func = getattr(self._api, call['api'])

            api_result = None
            api_exception = None
            try:
                api_result = func(**call['args'])
            except Exception as e:
                api_exception = e

            with self._call_result_cv:
                self._call_result[call['id']] = {
                    'result': api_result,
                    'exception': api_exception
                }
                self._call_result_cv.notify()

    def _get_call_id(self):

        call_id = f'{threading.get_ident()}_{int(time.time() * 1000000)}'
        self._id_pool[call_id] = True

        return call_id

    def call(self, api: str, args: Optional[dict] = None):
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
        self._call_queue.put(call)

        with self._call_result_cv:
            while call['id'] not in self._call_result:
                self._call_result_cv.wait()

            call_result = self._call_result[call['id']]
            del self._call_result[call['id']]

        del self._id_pool[call['id']]

        if call_result['exception'] is not None:
            raise call_result['exception']

        return call_result['result']

    def close(self):
        self.logger.info('close')
        self._close = True
        self._thread.join()

        self.logger.info('done')