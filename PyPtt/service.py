import threading
import time
import uuid

from SingleLog import Logger

import PyPtt


class Service:

    def __init__(self, pyptt_init_config: dict = {}):
        self._log = Logger('Service')
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
        call = {
            'api': api,
            'id': self._get_call_id(),
            'args': args
        }
        self._call_queue.append(call)

        while call['id'] not in self._call_result:
            time.sleep(0.1)

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

        self._log.stage('done')
