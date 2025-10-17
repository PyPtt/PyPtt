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
