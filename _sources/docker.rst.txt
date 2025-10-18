Docker Image
=================

| 是的，PyPtt 也支援 Docker Image。
| 只要一行指令就可以啟動一個 PyPtt 的 Docker Image，並且可以在 Docker Image 中使用 PyPtt。
|
| Doc: https://pyptt.cc/docker.html
| GHCR: https://github.com/PyPtt/PyPtt/pkgs/container/pyptt
| Code: https://github.com/PyPtt/PyPtt/blob/master/PyPtt/api_server.py

安裝
-----------------

.. code-block:: bash

    docker pull ghcr.io/pyptt/pyptt:latest

啟動
-----------------

.. code-block:: bash

    docker run -d -p 8787:8787 ghcr.io/pyptt/pyptt:latest

如果你想要也可以直接啟動 api_server.py:

.. code-block:: bash

    pip install .[api]
    uvicorn PyPtt.api_server:app --host 0.0.0.0 --port 8787

連線
-----------------

.. code-block:: python

    import PyPtt
    import requests

    from tests import config

    if __name__ == '__main__':
        payload = {
            "api": "login",
            "args": {
                'ptt_id': config.PTT1_ID,
                'ptt_pw': config.PTT1_PW
            }
        }
        r = requests.post("http://localhost:8787/api", json=payload)
        print(r.json())

        payload = {
            "api": "get_time",
        }
        r = requests.post("http://localhost:8787/api", json=payload)
        print(r.json())

        payload = {
            "api": "get_newest_index",
            "args": {
                'board': 'Gossiping',
                'index_type': PyPtt.NewIndex.BOARD
            }
        }
        r = requests.post("http://localhost:8787/api", json=payload)
        print(r.json())

        ##############################

        content = '''此內容由 PyPtt image 執行 PO 文

        測試換行 123
        測試換行 456
        測試換行 789
        '''

        payload = {
            "api": "post",
            "args": {
                'board': 'Test',
                'title_index': 1,
                'title': 'test',
                'content': content,
            }
        }
        r = requests.post("http://localhost:8787/api", json=payload)
        print(r.json())

        ##############################

        payload = {
            "api": "logout",
        }
        r = requests.post("http://localhost:8787/api", json=payload)
        print(r.json())
