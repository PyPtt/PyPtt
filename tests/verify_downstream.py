"""
End-to-end verification that downstream _api_* parsers still work after the
VT100Parser overhaul. Logs into PTT, exercises representative read paths,
and prints what each parser returned.
"""
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import PyPtt


def main() -> int:
    load_dotenv()
    ptt_id = os.environ['PTT1_ID']
    ptt_pw = os.environ['PTT1_PW']

    bot = PyPtt.API(host=PyPtt.HOST.PTT1, log_level=PyPtt.LogLevel.INFO)

    for attempt in range(3):
        try:
            bot.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=True)
            break
        except PyPtt.LoginTooOften:
            time.sleep(10 * (attempt + 1))
    else:
        print('login failed', file=sys.stderr)
        return 1

    try:
        # get_user — verifies _api_get_user parsing of profile screen
        print('\n>>> get_user(CodingMan)')
        user = bot.get_user(user_id=ptt_id)
        for field in (PyPtt.UserField.ptt_id, PyPtt.UserField.money,
                      PyPtt.UserField.login_count, PyPtt.UserField.last_login_date,
                      PyPtt.UserField.last_login_ip):
            print(f'  {field:<22} {user.get(field)!r}')

        # get_board_info — verifies _api_get_board_info regex/positional parsing
        print('\n>>> get_board_info(Python)')
        info = bot.get_board_info(board='Python')
        for field in (PyPtt.BoardField.board, PyPtt.BoardField.mandarin_des,
                      PyPtt.BoardField.open_status, PyPtt.BoardField.can_reply_post,
                      PyPtt.BoardField.is_require18):
            print(f'  {field:<35} {info.get(field)!r}')

        # get_post — exercises _parse_post_content, _parse_ip_location, _parse_comments
        print('\n>>> get_post(Python, newest)')
        newest = bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board='Python')
        post = bot.get_post(board='Python', index=newest)
        for field in (PyPtt.PostField.aid, PyPtt.PostField.author,
                      PyPtt.PostField.title, PyPtt.PostField.date,
                      PyPtt.PostField.ip, PyPtt.PostField.location,
                      PyPtt.PostField.url, PyPtt.PostField.post_status):
            value = post.get(field)
            if isinstance(value, str) and len(value) > 70:
                value = value[:70] + '...'
            print(f'  {field:<22} {value!r}')
        comments = post.get(PyPtt.PostField.comments) or []
        print(f'  comments count          {len(comments)}')
        for c in comments[:3]:
            print(f'    {c.get(PyPtt.CommentField.type)} '
                  f'{c.get(PyPtt.CommentField.author)}: '
                  f'{(c.get(PyPtt.CommentField.content) or "")[:40]}')

    finally:
        try:
            bot.logout()
        except Exception:
            pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
