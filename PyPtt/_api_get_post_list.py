from typing import Dict, List

from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import i18n
from . import log
from . import screens


def get_post_list(api, board: str, limit: int = 20, offset: int = 0) -> List[Dict]:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    check_value.check_type(board, str, 'board')
    if limit is not None:
        check_value.check_type(limit, int, 'limit')
    if offset is not None:
        check_value.check_type(offset, int, 'offset')

    max_index = api.get_newest_index(data_type.NewIndex.BOARD, board=board)

    check_value.check_range(limit, min_value=1, max_value=max_index, name='limit')
    check_value.check_range(offset, min_value=0, max_value=max_index - 1, name='offset')

    start_index = max_index - limit - offset + 1
    end_index = start_index + limit - 1

    # the first page shows 10 posts, each next page shows 20 posts
    if limit <= 10:
        max_round = 1
    else:
        # 1 is for the first page, +1 is for rounding up
        # so +2
        max_round = (limit - 10) // 20 + 2

    cmd_list = []

    cmd_list.append(str(max(1, start_index - 100)))
    cmd_list.append(command.enter)
    cmd_list.append(str(start_index))
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True)
    ]

    post_list = []

    for _ in range(max_round):

        index = api.connect_core.send(cmd, target_list)
        cmd = command.page_down
        last_screen = api.connect_core.get_screen_queue()[-1]

        is_parse_area = False

        for line in last_screen.splitlines()[3:-1]:

            if not line.startswith(api.cursor) and not is_parse_area:
                continue
            is_parse_area = True

            if line.strip().startswith(api.cursor):
                # replace the first cursor in the line
                line = line.replace(api.cursor, ' ' * len(api.cursor.encode('big5uao')), 1)

                if api.cursor == data_type.Cursor.NEW:
                    # add one space in the beginning to align the old cursor line
                    line = f' {line}'

            cur_index = int(line[:8].strip())
            status = line[8:10].strip()
            comment = line[10:12].strip()
            list_date = line[12:17].strip()
            author = line[18:31].strip()
            title = line[31:]

            cur_post = {
                data_type.PostField.board: board,
                data_type.PostField.index: cur_index,
                data_type.PostField.list_date: list_date,
                data_type.PostField.author: author,
                data_type.PostField.title: title,
                data_type.PostField.push_number: comment
            }

            post_list.append(cur_post)

            if cur_index >= end_index:
                return post_list

    raise exceptions.UnknownError(i18n.unknown_error)
