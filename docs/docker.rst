Docker Image
=================

.. image:: https://img.shields.io/docker/v/codingman000/pyptt/latest
   :target: https://hub.docker.com/r/codingman000/pyptt

.. image:: https://img.shields.io/docker/pulls/codingman000/pyptt?color=orange
    :target: https://hub.docker.com/r/codingman000/pyptt

.. image:: https://img.shields.io/docker/image-size/codingman000/pyptt/latest?color=green
    :target: https://hub.docker.com/r/codingman000/pyptt

.. image:: https://img.shields.io/docker/stars/codingman000/pyptt?color=succes
    :target: https://hub.docker.com/r/codingman000/pyptt



| 是的，PyPtt 也支援 Docker Image。
| 只要一行指令就可以啟動一個 PyPtt 的 Docker Image，並且可以在 Docker Image 中使用 PyPtt。
|
| Doc: https://pyptt.cc/docker.html
| Docker hub: https://hub.docker.com/r/codingman000/pyptt
| Github: https://github.com/PyPtt/PyPtt_image

安裝
-----------------

.. code-block:: bash

    docker pull codingman000/pyptt:latest

啟動
-----------------

.. code-block:: bash

    docker run -d -p 8787:8787 codingman000/pyptt:latest

連線
-----------------

物件編碼的方法你可以在這裏了解 程式碼_

.. _程式碼: https://github.com/PyPtt/PyPtt_image/blob/main/src/utils.py#L4

.. code-block:: python

    import PyPtt
    import requests

    from src.utils import object_encode
    from tests import config

    if __name__ == '__main__':
        params = {
            "api": "login",
            "args": object_encode({
                'ptt_id': config.PTT_ID,
                'ptt_pw': config.PTT_PW
            })
        }
        r = requests.get("http://localhost:8787/api", params=params)
        print(r.json())

        params = {
            "api": "get_time",
        }
        r = requests.get("http://localhost:8787/api", params=params)
        print(r.json())

        params = {
            "api": "get_newest_index",
            "args": object_encode({
                'board': 'Gossiping',
                'index_type': PyPtt.NewIndex.BOARD
            })
        }
        r = requests.get("http://localhost:8787/api", params=params)
        print(r.json())

        ##############################

        content = """此內容由 PyPtt image 執行 PO 文

        測試換行 123
        測試換行 456
        測試換行 789
        """

        params = {
            "api": "post",
            "args": object_encode({
                'board': 'Test',
                'title_index': 1,
                'title': 'test',
                'content': content,
            })
        }
        r = requests.get("http://localhost:8787/api", params=params)
        print(r.json())

        ##############################

        params = {
            "api": "logout",
        }
        r = requests.get("http://localhost:8787/api", params=params)
        print(r.json())