from . import _api_util
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import log
from . import screens


def get_post_index(api, board: str, aid: str) -> int:
    _api_util.goto_board(api, board)

    cmd_list = []
    cmd_list.append('#')
    cmd_list.append(aid)
    cmd_list.append(command.enter)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('找不到這個文章代碼', log_level=log.DEBUG,
                                exceptions_=exceptions.NoSuchPost(board, aid)),
        # 此狀態下無法使用搜尋文章代碼(AID)功能
        connect_core.TargetUnit('此狀態下無法使用搜尋文章代碼(AID)功能',
                                exceptions_=exceptions.CanNotUseSearchPostCode()),
        connect_core.TargetUnit('沒有文章...', exceptions_=exceptions.NoSuchPost(board, aid)),
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.InBoardWithCursor, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.MainMenu_Exiting, exceptions_=exceptions.NoSuchBoard(api.config, board))
    ]

    index = api.connect_core.send(
        cmd,
        target_list
    )
    ori_screen = api.connect_core.get_screen_queue()[-1]
    if index < 0:
        # print(OriScreen)
        raise exceptions.NoSuchBoard(api.config, board)

    # if index == 5:
    #     print(OriScreen)
    #     raise exceptions.NoSuchBoard(api.config, board)

    # print(index)
    # print(OriScreen)
    screen_list = ori_screen.split('\n')

    line = [x for x in screen_list if x.startswith(api.cursor)]
    line = line[0]
    last_line = screen_list[screen_list.index(line) - 1]
    # print(LastLine)
    # print(line)

    if '編號' in last_line and '人氣:' in last_line:
        index = line[1:].strip()
        index_fix = False
    else:
        index = last_line.strip()
        index_fix = True
    while '  ' in index:
        index = index.replace('  ', ' ')
    index_list = index.split(' ')
    index = index_list[0]
    if index == '★':
        return 0
    index = int(index)
    if index_fix:
        index += 1
    # print(Index)
    return index
