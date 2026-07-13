import time

import PyPtt

try:
    from tests import config
except KeyError:
    import config

import os

# ponytail: PTT_HOST=LOCALHOST points at a local imageptt docker container
# instead of the real PTT1 host; unset keeps the status quo.
_use_localhost = os.environ.get('PTT_HOST') == 'LOCALHOST'


def test_get_waterball():
    ptt1_bot = PyPtt.API(
        host=PyPtt.HOST.LOCALHOST if _use_localhost else PyPtt.HOST.PTT1,
    )
    ptt1_bot.login(ptt_id=config.PTT1_ID, ptt_pw=config.PTT1_PW, kick_other_session=True)

    try:
        print(f'\n請向 {config.PTT1_ID} 丟水球，等待 10 秒...')
        # time.sleep(30)

        waterball_list = ptt1_bot.get_waterball()
        print(f'收到 {len(waterball_list)} 筆水球')

        assert isinstance(waterball_list, list)
        for waterball in waterball_list:
            print(waterball[PyPtt.WaterballField.type],
                  waterball[PyPtt.WaterballField.target],
                  waterball[PyPtt.WaterballField.content],
                  waterball[PyPtt.WaterballField.date])
    finally:
        ptt1_bot.logout()

if __name__ == '__main__':
    test_get_waterball()