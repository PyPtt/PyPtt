import json
import sys


def get_password(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['id']
            password = account['pw']
    except FileNotFoundError:
        print(f'Please write PTT ID and Password in {password_file}')
        print('{"id":"your ptt id", "pw":"your ptt pw"}')
        sys.exit()

    return ptt_id, password
