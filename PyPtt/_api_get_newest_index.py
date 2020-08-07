import re
import requests
from bs4 import BeautifulSoup

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
    from . import check_value
    from . import _api_util
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command
    import check_value
    import _api_util


def _get_newest_index(api) -> int:
    last_screen = api.connect_core.get_screen_queue()[-1]
    # print(last_screen)
    last_screen_list = last_screen.split('\n')
    last_screen_list = last_screen_list[3:]
    last_screen_list = '\n'.join([x[:9] for x in last_screen_list])
    # print(last_screen_list)
    all_index = re.findall(r'\d+', last_screen_list)

    if len(all_index) == 0:
        # print(last_screen)
        # raise exceptions.UnknownError(i18n.UnknownError)
        return 0

    all_index = list(map(int, all_index))
    all_index.sort(reverse=True)
    # print(all_index)

    max_check_range = 6
    newest_index = 0
    for IndexTemp in all_index:
        need_continue = True
        if IndexTemp > max_check_range:
            check_range = max_check_range
        else:
            check_range = IndexTemp
        for i in range(1, check_range):
            if str(IndexTemp - i) not in last_screen:
                need_continue = False
                break
        if need_continue:
            log.show_value(
                api.config,
                log.level.DEBUG,
                i18n.FindNewestIndex,
                IndexTemp
            )
            newest_index = IndexTemp
            break

    if newest_index == 0:
        last_screen = api.connect_core.get_screen_queue()[-1]
        print(last_screen)
        raise exceptions.UnknownError(i18n.UnknownError)

    return newest_index


def get_newest_index(
        api,
        index_type: int,
        board: str = None,
        # BBS
        search_type: int = 0,
        search_condition: str = None,
        search_list: list = None) -> int:
    if index_type == data_type.index_type.BBS:

        check_value.check(api.config, str, 'Board', board)

        api._check_board(board)

        check_value.check(
            api.config, int, 'SearchType', search_type,
            value_class=data_type.post_search_type)
        if search_condition is not None:
            check_value.check(
                api.config, str,
                'SearchCondition', search_condition)

        if search_list is not None:
            check_value.check(
                api.config, list,
                'search_list', search_list)
        check_value.check(api.config, int, 'SearchType', search_type)

        cmd_list = []
        cmd_list.append(command.GoMainMenu)
        cmd_list.append('qs')
        cmd_list.append(board)
        cmd_list.append(command.Enter)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.AnyKeyContinue,
                '任意鍵',
                response=' ',
            ),
            connect_core.TargetUnit(
                [
                    '動畫播放中',
                ],
                '互動式動畫播放中',
                response=command.Ctrl_C,
                log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                [
                    '進板成功',
                ],
                screens.Target.InBoard,
                break_detect=True,
                log_level=log.level.DEBUG
            ),
        ]

        index = api.connect_core.send(cmd, target_list)

        cmd_list = []

        normal_newest_index = -1
        if search_condition is not None:

            normal_newest_index = get_newest_index(api, index_type, board=board)

            if search_type == data_type.post_search_type.KEYWORD:
                cmd_list.append('/')
            elif search_type == data_type.post_search_type.AUTHOR:
                cmd_list.append('a')
            elif search_type == data_type.post_search_type.PUSH:
                cmd_list.append('Z')
            elif search_type == data_type.post_search_type.MARK:
                cmd_list.append('G')
            elif search_type == data_type.post_search_type.MONEY:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(command.Enter)

        if search_list is not None:

            if normal_newest_index == -1:
                normal_newest_index = get_newest_index(api, index_type, board=board)

            for search_type_, search_condition_ in search_list:

                if search_type_ == data_type.post_search_type.KEYWORD:
                    cmd_list.append('/')
                elif search_type_ == data_type.post_search_type.AUTHOR:
                    cmd_list.append('a')
                elif search_type_ == data_type.post_search_type.PUSH:
                    cmd_list.append('Z')
                elif search_type_ == data_type.post_search_type.MARK:
                    cmd_list.append('G')
                elif search_type_ == data_type.post_search_type.MONEY:
                    cmd_list.append('A')

                cmd_list.append(search_condition_)
                cmd_list.append(command.Enter)

        cmd_list.append('1')
        cmd_list.append(command.Enter)
        cmd_list.append('$')

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.NoPost,
                '沒有文章...',
                break_detect=True,
                log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                i18n.Success,
                screens.Target.InBoard,
                break_detect=True,
                log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                i18n.Success,
                screens.Target.InBoardWithCursor,
                break_detect=True,
                log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                i18n.NoSuchBoard,
                screens.Target.MainMenu_Exiting,
                exceptions_=exceptions.NoSuchBoard(api.config, board)
            ),
        ]
        index = api.connect_core.send(cmd, target_list)
        if index < 0:
            # OriScreen = api.connect_core.getScreenQueue()[-1]
            # print(OriScreen)
            raise exceptions.NoSuchBoard(api.config, board)

        if index == 0:
            return 0

        newest_index = _get_newest_index(api)

        if normal_newest_index == newest_index:
            raise exceptions.NoSearchResult()

    elif index_type == data_type.index_type.WEB:
        # web
        _NewestIndex = None
        newest_index = 0
        _url = 'https://www.ptt.cc/bbs/'
        url = _url + board
        r = requests.get(url, cookies={'over18': '1'})

        if r.status_code != requests.codes.ok:
            raise exceptions.NoSuchBoard(api.config, board)
        soup = BeautifulSoup(r.text, 'html.parser')

        for index, data in enumerate(soup.select('div.btn-group.btn-group-paging a')):
            text = data.text
            herf = data.get('href')
            if '上頁' in text:
                _NewestIndex = herf.split('index')[1].split('.')[0]
                # print("_NewestIndex: " + _NewestIndex)
                _NewestIndex = int(_NewestIndex)

        if _NewestIndex is None:
            raise exceptions.UnknownError('')
        newest_index = (_NewestIndex) + 1

    elif index_type == data_type.index_type.MAIL:

        cmd_list = []
        cmd_list.append(command.GoMainMenu)
        cmd_list.append(command.Ctrl_Z)
        cmd_list.append('m')
        cmd_list.append(command.Ctrl_F * 50)

        cmd = ''.join(cmd_list)

        target_list = [
            connect_core.TargetUnit(
                i18n.MailBox,
                screens.Target.InMailBox,
                break_detect=True,
                # log_level=log.level.DEBUG
            ),
            connect_core.TargetUnit(
                i18n.NoMail,
                screens.Target.CursorToGoodbye,
                break_detect=True,
                log_level=log.level.DEBUG
            ),
        ]

        def get_index(api):
            current_capacity, _ = _api_util.get_mailbox_capacity(api)
            last_screen = api.connect_core.get_screen_queue()[-1]
            cursor_line = [x for x in last_screen.split('\n') if x.strip().startswith(api.cursor)][0]
            # print(cursor_line)
            list_index = int(re.compile('(\d+)').search(cursor_line).group(0))
            if list_index > current_capacity:
                newest_index = list_index
            else:
                newest_index = current_capacity

            return newest_index

        for _ in range(3):
            index = api.connect_core.send(
                cmd,
                target_list,
            )

            if index == 0:
                newest_index = get_index(api)
                break
            newest_index = 0

    return newest_index
