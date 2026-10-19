import re

from . import _api_util
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import log
from . import screens
from .data_type import FavouriteBoardField

# '    83)  MCP_Test     測試 ◎…'、'     2 ˇAllTogether  聯誼 ◎…'：編號、[)]、[ˇ]、板名、類別、◎標題
_ROW = re.compile(r'\s*\d+\)?\s+ˇ?\s*(\S+)\s+(\S+)\s*(.*)')


def get_favourite_board(api) -> list:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    cmd_list = [command.go_main_menu, 'F', command.enter, '0']
    cmd = ''.join(cmd_list)

    target_list = [
        # 舊版頁尾有「選擇看板」，新版沒有；標頭與頁尾的「已讀/未讀」新舊都有
        connect_core.TargetUnit(['【看板列表】', '已讀/未讀'], break_detect=True)
    ]

    log.logger.info(i18n.get_favourite_board_list)

    board_list = []
    favourite_board_list = []
    # NOTE: expanded_screen intentionally not used — same risk as get_board_list.
    while True:

        api.connect_core.send(
            cmd,
            target_list)

        ori_screen = api.connect_core.get_screen_queue()[-1]
        screen_buf = [x for x in ori_screen.split('\n')[3:-1] if x.strip()]

        for line in screen_buf:
            if '------------' in line:
                continue
            if line.startswith(api.cursor):
                line = ' ' * screens._cell_len(api.cursor) + line[len(api.cursor):]
            # 板名、類別依欄位內容切；標題與人氣欄之間沒有分隔，只能在第 64 格 (人氣欄起點) 切掉
            m = _ROW.match(line[:screens._str_pos_at_cells(line, 64)])
            if m is None:
                continue
            board, board_type = m.group(1), m.group(2)
            # remove ◎
            board_title = m.group(3)[1:].strip()

            if board in board_list:
                log.logger.info(i18n.get_favourite_board_list, '...', i18n.success)
                return favourite_board_list
            board_list.append(board)

            favourite_board_list.append({
                FavouriteBoardField.board: board,
                FavouriteBoardField.type: board_type,
                FavouriteBoardField.title: board_title})

        if len(screen_buf) < 20:
            break

        cmd = command.ctrl_f

    log.logger.info(i18n.get_favourite_board_list, '...', i18n.success)
    return favourite_board_list
