import re
import requests
from bs4 import BeautifulSoup
try:
    from . import DataType
    from . import i18n
    from . import ConnectCore
    from . import Log
    from . import Screens
    from . import Exceptions
    from . import Command
    from . import CheckValue
except ModuleNotFoundError:
    import DataType
    import i18n
    import ConnectCore
    import Log
    import Screens
    import Exceptions
    import Command
    import CheckValue


def get_newest_index(
        api,
        index_type: int,
        board: str = None,
        # BBS
        search_type: int = 0,
        search_condition: str = None) -> int:

    if index_type == DataType.IndexType.BBS:

        api._check_board(board)

        CheckValue.check(
            api.Config, int, 'SearchType', search_type,
            value_class=DataType.PostSearchType)
        if search_condition is not None:
            CheckValue.check(
                api.Config, str,
                'SearchCondition', search_condition)
        CheckValue.check(api.Config, int, 'SearchType', search_type)

        cmd_list = []
        cmd_list.append(Command.GoMainMenu)
        cmd_list.append('qs')
        cmd_list.append(board)
        cmd_list.append(Command.Enter)
        cmd_list.append(Command.Ctrl_C * 2)
        cmd_list.append(Command.Space)

        if search_condition is not None:
            if search_type == DataType.PostSearchType.Keyword:
                cmd_list.append('/')
            elif search_type == DataType.PostSearchType.Author:
                cmd_list.append('a')
            elif search_type == DataType.PostSearchType.Push:
                cmd_list.append('Z')
            elif search_type == DataType.PostSearchType.Mark:
                cmd_list.append('G')
            elif search_type == DataType.PostSearchType.Money:
                cmd_list.append('A')

            cmd_list.append(search_condition)
            cmd_list.append(Command.Enter)

        cmd_list.append('1')
        cmd_list.append(Command.Enter)
        cmd_list.append('$')

        cmd = ''.join(cmd_list)

        target_list = [
            ConnectCore.TargetUnit(
                i18n.NoPost,
                '沒有文章...',
                break_detect=True,
                log_level=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Success,
                Screens.Target.InBoard,
                break_detect=True,
                log_level=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.Success,
                Screens.Target.InBoardWithCursor,
                break_detect=True,
                log_level=Log.Level.DEBUG
            ),
            ConnectCore.TargetUnit(
                i18n.NoSuchBoard,
                Screens.Target.MainMenu_Exiting,
                exceptions=Exceptions.NoSuchBoard(api.Config, board)
            ),
        ]
        index = api._ConnectCore.send(cmd, target_list)
        if index < 0:
            # OriScreen = api._ConnectCore.getScreenQueue()[-1]
            # print(OriScreen)
            raise Exceptions.NoSuchBoard(api.Config, board)

        if index == 0:
            return 0

        last_screen = api._ConnectCore.get_screen_queue()[-1]
        all_index = re.findall(r'\d+ ', last_screen)

        if len(all_index) == 0:
            print(last_screen)
            raise Exceptions.UnknownError(i18n.UnknownError)

        all_index = list(map(int, all_index))
        all_index.sort(reverse=True)

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
                Log.show_value(
                    api.Config,
                    Log.Level.DEBUG,
                    i18n.FindNewestIndex,
                    IndexTemp
                )
                newest_index = IndexTemp
                break

        if newest_index == 0:
            Screens.show(api.Config, api._ConnectCore.get_screen_queue())
            raise Exceptions.UnknownError(i18n.UnknownError)

    elif DataType.IndexType.Web:
        # web
        _NewestIndex = None
        newest_index = 0
        _url = 'https://www.ptt.cc/bbs/'
        url = _url + board
        r = requests.get(url, cookies={'over18': '1'})

        if r.status_code != requests.codes.ok:
            raise Exceptions.NoSuchBoard(api.Config, board)
        soup = BeautifulSoup(r.text, 'html.parser')

        for index, data in enumerate(soup.select('div.btn-group.btn-group-paging a')):
            text = data.text
            herf = data.get('href')
            if '上頁' in text:
                _NewestIndex = herf.split('index')[1].split('.')[0]
                # print("_NewestIndex: " + _NewestIndex)
                _NewestIndex = int(_NewestIndex)

        if _NewestIndex is None:
            raise Exceptions.UnknownError('')
        newest_index = (_NewestIndex) + 1
    return newest_index
