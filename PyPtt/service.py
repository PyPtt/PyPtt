import time
import uuid

from SingleLog.log import Logger

import PyPtt


class PyPttService:

    def __init__(self, ):
        self._log = Logger('Service')
        self._api = PyPtt.API()
        self._call_queue = []
        self._call_result = {}
        self._close = False

    def _run(self):

        while not self._close:
            if len(self._call_queue) == 0:
                time.sleep(0.1)
                continue

            call = self._call_queue.pop(0)

            func = getattr(self._api, call['api'])

            result = func(**call['args'])

            self._call_result[call['id']] = result

    def call(self, api: str, args: dict = None):
        call = {
            'api': api,
            'id': uuid.uuid4().hex,
            'args': args
        }
        self._call_queue.append(call)

        while call['id'] not in self._call_result:
            time.sleep(0.1)

        result = self._call_result[call['id']]
        del self._call_result[call['id']]

        return result

    def close(self):
        self._close = True


if __name__ == '__main__':
    print(uuid.uuid4().hex)
