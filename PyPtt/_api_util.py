from __future__ import annotations

import re
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Optional

from . import _api_get_board_info
from . import command
from . import connect_core
from . import data_type
from . import exceptions
from . import log
from . import screens


_MAX_GET_CONTENT_HEIGHT = 100  # PTT server hard cap


@contextmanager
def expanded_screen(api):
    """Temporarily resize the PTT terminal to its maximum (100 rows) and restore on exit.

    Wraps any paging loop that calls connect_core.send() in a loop so that more
    content is visible per page and fewer round-trips are needed.  PTT's hard
    cap is 100 rows regardless of what NAWS requests.
    """
    original_height = api.config.screen_height
    if original_height < _MAX_GET_CONTENT_HEIGHT:
        api.connect_core.set_screen_height(_MAX_GET_CONTENT_HEIGHT)
    try:
        yield
    finally:
        if original_height < _MAX_GET_CONTENT_HEIGHT:
            api.connect_core.set_screen_height(original_height)


@dataclass
class PostQueryResult:
    lock_post: bool
    author: str
    title: str
    aid: Optional[str]
    url: Optional[str]
    money: int
    list_date: Optional[str]
    push_number: Optional[str]
    index: int


def get_content(api, post_mode: bool = True):
    api.Unconfirmed = False

    with expanded_screen(api):
        def is_unconfirmed_handler(screen):
            api.Unconfirmed = True

        if post_mode:
            cmd = command.enter * 2
        else:
            cmd = command.enter

        target_list = [
            # 待證實文章
            connect_core.TargetUnit('本篇文章內容經站方授權之板務管理人員判斷有尚待證實之處', response=' ',
                                    handler=is_unconfirmed_handler),
            connect_core.TargetUnit(screens.Target.PostEnd, log_level=log.DEBUG, break_detect=True),
            connect_core.TargetUnit(screens.Target.InPost, log_level=log.DEBUG, break_detect=True),
            connect_core.TargetUnit(screens.Target.PostNoContent, log_level=log.DEBUG, break_detect=True),
            # 動畫文章
            connect_core.TargetUnit(screens.Target.Animation, response='n'),
        ]

        line_from_pattern = re.compile(r'[\d]+~[\d]+')

        has_control_code = False
        control_code_mode = False
        push_start = False
        content_start_exist = False
        content_start_jump = False
        content_start_jump_set = False

        first_page = True
        origin_post = []
        stop_dict = dict()
        new_content_part = ''
        get_line_b = 0
        max_line_b = 0
        stall = 0
        timeouts = 0
        while True:
            index = api.connect_core.send(cmd, target_list)
            if index == 3 or index == 4:
                return None, False
            if index < 0:
                # 逾時只繼續收、不送鍵 (送 Ctrl-L 會多一張重繪，被當成同頁再接一次而重複內容；重開 parser
                # 則只看得到被逾時切斷那張的後半而漏內容)；連續 3 次認不出 (例如被 → 帶離文章) 才中止，
                # 以前會照送 → 在文章與列表間無限繞圈
                timeouts += 1
                if timeouts < 3:
                    cmd = None
                    continue
                if api.connect_core.last_timeout_was_silent:
                    raise exceptions.ConnectionClosed()
                status_line = api.connect_core.get_screen_queue()[-1].split('\n')[-1]
                raise exceptions.UnknownError(f'get_content: unrecognized screen {status_line!r}')
            timeouts = 0

            last_screen = api.connect_core.get_screen_queue()[-1]
            lines = last_screen.split('\n')
            last_line = lines[-1]
            lines.pop()
            last_screen = '\n'.join(lines)

            if screens.Target.content_start in last_screen and not content_start_exist:
                content_start_exist = True

            if content_start_exist:
                if not content_start_jump_set:
                    if screens.Target.content_start not in last_screen:
                        content_start_jump = True
                        content_start_jump_set = True
                else:
                    content_start_jump = False

            pattern_result = line_from_pattern.search(last_line)
            if pattern_result is None:
                control_code_mode = True
                has_control_code = True
            else:
                last_read_line_list = pattern_result.group(0).split('~')
                last_read_line_a_temp = int(last_read_line_list[0])
                last_read_line_b_temp = int(last_read_line_list[1])
                # 行號不再前進 (含倒退) 就中止；上限放寬是因為一行折成多列時 b 會合法地停住幾頁
                if last_read_line_b_temp > max_line_b:
                    max_line_b, stall = last_read_line_b_temp, 0
                else:
                    stall += 1
                    if stall > 20:
                        raise exceptions.UnknownError(f'get_content: stuck at line {last_read_line_b_temp}')
                if control_code_mode:
                    last_read_line_a = last_read_line_a_temp - 1
                    last_read_line_b = last_read_line_b_temp - 1
                control_code_mode = False

            if first_page:
                first_page = False
                origin_post.append(last_screen)
            else:
                # 這裡是根據觀察畫面行數的變化歸納出的神奇公式...
                # 輸出的結果是要判斷出畫面的最後 x 行是新的文章內容
                #
                # 這裡是 PyPtt 最黑暗最墮落的地方，所有你所知的程式碼守則，在這裡都不適用
                # 每除完一次錯誤，我會陷入嚴重的創傷後壓力症候群，而我的腦袋會自動選擇遺忘這裡所有的一切
                # 以確保下一個週一，我可以正常上班
                # but it works!!!

                # print(LastScreen)
                # print(f'last_read_line_a_temp [{last_read_line_a_temp}]')
                # print(f'last_read_line_b_temp [{last_read_line_b_temp}]')
                # print(f'last_read_line_a {last_read_line_a}')
                # print(f'last_read_line_b {last_read_line_b}')
                # print(f'GetLineB {last_read_line_a_temp - last_read_line_a}')
                # print(f'GetLineA {last_read_line_b_temp - last_read_line_b}')
                # print(f'show line {last_read_line_b_temp - last_read_line_a_temp + 1}')
                if not control_code_mode:

                    if last_read_line_a_temp in stop_dict:
                        new_content_part = '\n'.join(
                            lines[-stop_dict[last_read_line_a_temp]:])
                        stop_dict = dict()
                    else:
                        get_line_b = last_read_line_b_temp - last_read_line_b
                        if get_line_b > 0:
                            # print('Type 1')
                            new_content_part = '\n'.join(lines[-get_line_b:])
                            # The doubling and try_line heuristics were tuned for
                            # 24-row screens (max get_line_b ≈ 22). With larger
                            # screen_height the delta can be 50+, causing both
                            # heuristics to look back into the post header rows
                            # (作者/標題/時間) and inject them into the body.
                            # Only apply them when the delta is within the original
                            # 24-row regime.
                            if get_line_b <= 23:
                                if index == 1 and len(new_content_part) == get_line_b - 1:
                                    new_content_part = '\n'.join(lines[-(get_line_b * 2):])
                                elif origin_post and get_line_b + 1 <= len(lines):
                                    last_line_temp = origin_post[-1].strip()
                                    try_line = lines[-(get_line_b + 1)].strip()

                                    if not last_line_temp.endswith(try_line):
                                        new_content_part = try_line + '\n' + new_content_part
                            stop_dict = dict()
                        else:
                            # 駐足現象，LastReadLineB跟上一次相比並沒有改變
                            if (last_read_line_b_temp + 1) not in stop_dict:
                                stop_dict[last_read_line_b_temp + 1] = 1
                            stop_dict[last_read_line_b_temp + 1] += 1

                            get_line_a = last_read_line_a_temp - last_read_line_a

                            if get_line_a > 0:
                                # print(f'Type 2 get_line_a [{get_line_a}]')
                                new_content_part = '\n'.join(lines[-get_line_a:])
                            else:
                                new_content_part = '\n'.join(lines)

                else:
                    new_content_part = lines[-1]

                origin_post.append(new_content_part)

                log.logger.debug('NewContentPart', new_content_part)

            if index == 1:
                if content_start_jump and len(new_content_part) == 0:
                    get_line_b += 1
                    new_content_part = '\n'.join(lines[-get_line_b:])

                    origin_post.pop()
                    origin_post.append(new_content_part)
                break

            if not control_code_mode:
                last_read_line_a = last_read_line_a_temp
                last_read_line_b = last_read_line_b_temp

            for EC in screens.Target.content_end_list:
                if EC in last_screen:
                    push_start = True
                    break

            if push_start:
                cmd = command.right
            else:
                cmd = command.down

    # print(api.Unconfirmed)
    origin_post = '\n'.join(origin_post)
    # OriginPost = [line.strip() for line in OriginPost.split('\n')]
    # OriginPost = '\n'.join(OriginPost)

    log.logger.debug('OriginPost', origin_post)

    return origin_post, has_control_code


def get_mailbox_capacity(api) -> tuple[int, int]:
    if api._mail_capacity is not None:
        return api._mail_capacity

    last_screen = api.connect_core.get_screen_queue()[-1]
    capacity_line = last_screen.split('\n')[2]

    log.logger.debug('capacity_line', capacity_line)

    pattern_result = re.compile(r'(\d+)/(\d+)').search(capacity_line)
    if pattern_result is not None:
        current_capacity = int(pattern_result.group(0).split('/')[0])
        max_capacity = int(pattern_result.group(0).split('/')[1])

        log.logger.debug('current_capacity', current_capacity)
        log.logger.debug('max_capacity', max_capacity)

        api._mail_capacity = (current_capacity, max_capacity)
        return current_capacity, max_capacity
    return 0, 0


# >     1   112/09 ericsk       □ [心得] 終於開板了
# ┌── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┐
# │ 文章代碼(AID): #13cPSYOX (Python) [ptt.cc] [心得] 終於開板了  │
# │ 文章網址: https://www.ptt.cc/bbs/Python/M.1134139170.A.621.html      │
# │ 這一篇文章值 2 Ptt幣                                              │
# └── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ─┘

def parse_query_post(api, ori_screen):
    lock_post = False
    try:
        cursor_line = [line for line in ori_screen.split(
            '\n') if line.strip().startswith(api.cursor)][0]
    except Exception as e:
        print(api.cursor)
        print(ori_screen)
        raise e

    post_author = cursor_line
    if '□' in post_author:
        post_author = post_author[:post_author.find('□')].strip()
    elif 'R:' in post_author:
        post_author = post_author[:post_author.find('R:')].strip()
    elif ' 轉 ' in post_author:
        post_author = post_author[:post_author.find('轉')].strip()
    elif ' 鎖 ' in post_author:
        post_author = post_author[:post_author.find('鎖')].strip()
        lock_post = True
    post_author = post_author[post_author.rfind(' '):].strip()

    post_title = cursor_line
    if ' □ ' in post_title:
        post_title = post_title[post_title.find('□') + 1:].strip()
    elif ' R:' in post_title:
        post_title = post_title[post_title.find('R:'):].strip()
    elif ' 轉 ' in post_title:
        post_title = post_title[post_title.find('轉') + 1:].strip()
        post_title = f'Fw: {post_title}'
    elif ' 鎖 ' in post_title:
        post_title = post_title[post_title.find('鎖') + 1:].strip()

    ori_screen_temp = ori_screen[ori_screen.find('┌──'):]
    ori_screen_temp = ori_screen_temp[:ori_screen_temp.find('└──')]

    aid_line = [line for line in ori_screen.split(
        '\n') if line.startswith('│ 文章代碼(AID)')]

    post_aid = None
    if len(aid_line) == 1:
        aid_line = aid_line[0]
        pattern = re.compile(r'#[\w|-]+')
        pattern_result = pattern.search(aid_line)
        post_aid = pattern_result.group(0)[1:]

    pattern = re.compile(r'文章網址: https:[\S]+html')
    pattern_result = pattern.search(ori_screen_temp)

    if pattern_result is None:
        post_web = None
    else:
        post_web = pattern_result.group(0)[6:]

    pattern = re.compile(r'這一篇文章值 [\d]+ Ptt幣')
    pattern_result = pattern.search(ori_screen_temp)
    if pattern_result is None:
        # 特殊文章無價格
        post_money = -1
    else:
        post_money = pattern_result.group(0)[7:]
        post_money = post_money[:post_money.find(' ')]
        post_money = int(post_money)

    pattern = re.compile(r'[\d]+\/[\d]+')
    pattern_result = pattern.search(cursor_line)
    if pattern_result is None:
        list_date = None
    else:
        list_date = pattern_result.group(0)
        list_date = list_date[-5:]
    # print(list_date)

    # >  7485   9 8/09 CodingMan    □ [閒聊] PTT Library 更新
    # > 79189 M 1 9/17 LittleCalf   □ [公告] 禁言退文公告
    # >781508 +爆 9/17 jodojeda     □ [新聞] 國人吃魚少 學者：應把吃魚當成輕鬆愉快
    # >781406 +X1 9/17 kingofage111 R: [申請] ReDmango 請辭Gossiping板主職務

    pattern = re.compile(r'[\d]+')
    pattern_result = pattern.search(cursor_line)
    post_index = 0
    if pattern_result is not None:
        post_index = int(pattern_result.group(0))

    push_number = cursor_line
    push_number = push_number[7:11]
    push_number = push_number.split(' ')
    push_number = list(filter(None, push_number))

    if len(push_number) == 0:
        push_number = None
    else:
        push_number = push_number[-1]
        if push_number.startswith('爆') or push_number.startswith('~爆'):
            push_number = '爆'

        if push_number.startswith('+') or push_number.startswith('~'):
            push_number = push_number[1:]

        if push_number.lower().startswith('m'):
            push_number = push_number[1:]

        if push_number.lower().startswith('!'):
            push_number = push_number[1:]

        if push_number.lower().startswith('s'):
            push_number = push_number[1:]

        if push_number.lower().startswith('='):
            push_number = push_number[1:]

        if len(push_number) == 0:
            push_number = None

    log.logger.debug('PostAuthor', post_author)
    log.logger.debug('PostTitle', post_title)
    log.logger.debug('PostAID', post_aid)
    log.logger.debug('PostWeb', post_web)
    log.logger.debug('PostMoney', post_money)
    log.logger.debug('ListDate', list_date)
    log.logger.debug('PushNumber', push_number)

    return PostQueryResult(
        lock_post=lock_post,
        author=post_author,
        title=post_title,
        aid=post_aid,
        url=post_web,
        money=post_money,
        list_date=list_date,
        push_number=push_number,
        index=post_index,
    )


def get_search_condition_cmd(index_type: data_type.NewIndex, search_list: Optional[list] = None):
    cmd_list = []
    if not search_list:
        return cmd_list

    for search_type, search_condition in search_list:

        if search_type == data_type.SearchType.KEYWORD:
            cmd_list.append('/')
        elif search_type == data_type.SearchType.AUTHOR:
            cmd_list.append('a')
        elif search_type == data_type.SearchType.MARK:
            cmd_list.append('G')
        elif index_type == data_type.NewIndex.BOARD:
            if search_type == data_type.SearchType.COMMENT:
                cmd_list.append('Z')
            elif search_type == data_type.SearchType.MONEY:
                cmd_list.append('A')
            else:
                continue
        else:
            continue

        cmd_list.append(search_condition)
        cmd_list.append(command.enter)

    return cmd_list


def check_no_control_chars(value: str, name: str) -> None:
    # 看板設定 / Bakuman 是逐鍵比對的流程：字串裡的 \r 會提早送出輸入列，
    # 後面的字母就落到編輯選單變成熱鍵。比照 _api_post.py 的 display_id 檢查。
    for c in value:
        if ord(c) < 0x20 or ord(c) == 0x7f:
            raise exceptions.ParameterError(f'{name} must not contain control characters (found {c!r})')


def last_screen(api) -> str:
    screen_queue = api.connect_core.get_screen_queue()
    return screen_queue[-1] if screen_queue else ''


def is_article_list(api, screen: str) -> bool:
    # 看板設定畫面會顯示板主可自訂的中文敘述，可能剛好含 InBoard 的子字串
    # (例如「[i]看板設定文章列表(b)進板」)；先用固定位置的頁首/頁尾排除設定畫面。
    if screens.in_board_setting(screen):
        return False
    return connect_core.TargetUnit(screens.Target.InBoard).is_match(screen, api.cursor)


def close_session(api) -> None:
    # 確認不了已回到文章列表時，任何後續按鍵 (例如 go_main_menu 開頭的 Space)
    # 都可能落在看板設定的熱鍵上，所以直接斷線並標成未登入。
    if log.logger is not None:
        log.logger.info('board setting: cannot confirm the article list, closing connection')
    try:
        api.connect_core.close()
    except Exception:
        pass
    api._is_login = False


def leave_board_setting(api, stale: bool = False) -> bool:
    """從看板設定 / Bakuman 一次一鍵退回文章列表；回到文章列表才回傳 True。

    每一步依目前畫面選鍵 (screens.board_setting_exit_key)，只會送 ←、Ctrl-C、
    Bakuman「[Q]結束?」的 Enter，以及 Ctrl-L 重繪。stale=True (上一鍵完全沒收到
    回應) 時最後一張畫面可能已過期，先送 Ctrl-L 重繪，不照舊畫面重送。
    退不回文章列表 (或送鍵時出錯) 就斷線並回傳 False。"""
    if not api._is_login:
        return False

    wait_list = [
        screens.Target.InBoard,
        '任意鍵',
        screens.Target.Bakuman[1],
        [['看板設定(編輯)', '(^P)開啟編輯', '(←)離開']],
        screens.Target.BoardSettingOldPrompt,
        '請輸入',
        '確認以上資料全部正確嗎',
    ]
    refreshed_unknown = False
    left_unknown = False
    timeouts = 0
    try:
        for _ in range(15):
            if stale:
                key = command.refresh
            else:
                screen = last_screen(api)
                if is_article_list(api, screen):
                    return True
                key = screens.board_setting_exit_key(screen)
                if key is None:
                    if not refreshed_unknown:
                        refreshed_unknown = True
                        key = command.refresh
                    elif not left_unknown:
                        left_unknown = True
                        key = command.left
                    else:
                        break
            target_list = [connect_core.TargetUnit(t, log_level=log.DEBUG, break_detect=True) for t in wait_list]
            if api.connect_core.send(key, target_list, screen_timeout=api.config.screen_timeout) < 0:
                timeouts += 1
                if timeouts > 3:
                    break
                stale = getattr(api.connect_core, 'last_timeout_was_silent', False)
            else:
                stale = False
    except Exception:
        pass
    except BaseException:
        # KeyboardInterrupt / SystemExit：不再送鍵，直接斷線
        close_session(api)
        raise

    close_session(api)
    return False


def run_in_board_setting(api, flow):
    """執行看板設定流程 flow()；任何例外 (含 UseTooManyResources、逾時) 都先退回
    文章列表再往外丟。退不回來就斷線並改丟 ConnectionClosed。"""
    try:
        return flow()
    except Exception as e:
        stale = getattr(api.connect_core, 'last_timeout_was_silent', False)
        if not leave_board_setting(api, stale=stale):
            raise exceptions.ConnectionClosed() from e
        raise
    except BaseException:
        # KeyboardInterrupt / SystemExit：畫面狀態不明，不送任何鍵，直接斷線
        close_session(api)
        raise


def search_key(search_list: Optional[list]) -> tuple:
    # 搜尋條件的比對鍵；空 tuple 表示一般文章列表
    return tuple((search_type, search_condition) for search_type, search_condition in (search_list or []))


def board_list_kind(api, screen: str, board: str, require_name: bool = True) -> Optional[str]:
    """目前畫面是 board 的哪一種列表：'plain' 一般文章列表、'search' 搜尋結果，其他回傳 None。

    一般列表標頭是「看板《Python》」；搜尋結果是「系列《Python》」。
    標頭擠不下時 (例如板主名單長又有「你有新信件」) PTT 會整段省略「看板《X》」，
    這時改看頁尾 (PTT1 新版：一般列表「文章列表」、搜尋結果「系列文章」)；
    但看不到看板名稱，require_name=True 時回傳 None，只有呼叫端確定還在這個看板裡才放寬。"""
    if screens.in_board_setting(screen):
        return None
    lines = screen.split('\n')
    match = re.search(r'(看板|系列)《([^》]+)》', lines[0])
    if match is not None:
        if match.group(2).lower() != board.lower():
            return None
        kind = 'plain' if match.group(1) == '看板' else 'search'
    else:
        if require_name:
            return None
        footer = next((line.strip() for line in reversed(lines) if line.strip()), '')
        if footer.startswith('文章列表'):
            kind = 'plain'
        elif footer.startswith('系列文章'):
            kind = 'search'
        else:
            return None
    if kind == 'plain' and is_article_list(api, screen):
        return 'plain'
    if kind == 'search' and connect_core.TargetUnit(screens.Target.InSearchList).is_match(screen, api.cursor):
        return 'search'
    return None


def forget_current_board(api) -> None:
    # 送出 goto_board 以外的搜尋指令後，畫面上的搜尋結果跟記錄對不起來；
    # 下一次 goto_board 一定要走完整路徑重新進板
    api._current_board = None
    api._current_search = ()


def _list_targets() -> list:
    return [
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.InSearchList, log_level=log.DEBUG, break_detect=True),
    ]


def _stay_in_board(api, board: str, want: tuple) -> Optional[str]:
    """上一個 API 停在同一個看板時，不回主選單、不重新進板，只用 ← 退回需要的列表。

    回傳 'search' 表示已經在 want 這組條件的搜尋結果裡；'plain' 表示在一般文章列表
    (呼叫端視需要再搜尋)；None 表示判斷不了，交給完整路徑 (go_main_menu 從任何畫面都能回主選單)。
    每一步都以畫面確認：標頭的看板名稱、一般列表或搜尋結果。"""
    if getattr(api, '_current_board', None) != board.lower():
        return None

    # 最多: 提示框 → 文章內文 → 搜尋結果 → 一般列表
    for _ in range(4):
        screen = last_screen(api)
        kind = board_list_kind(api, screen, board)
        if kind == 'plain':
            return 'plain'
        if kind == 'search' and want and api._current_search == want:
            return 'search'

        if kind is None and '任意鍵' in screen.rstrip().rsplit('\n', 1)[-1]:
            # 「請按任意鍵繼續」(查詢文章資訊 Q、發文/回文完成)；完整路徑也是先按空白鍵關掉提示框
            key = command.space
        elif kind is None and connect_core.TargetUnit(screens.Target.InPost).is_match(screen, api.cursor):
            # 文章內文 ← 回到點進來的列表
            key = command.left
        elif kind == 'search':
            # 搜尋結果 ← 直接回到一般列表 (多層搜尋也是一次)
            key = command.left
        else:
            return None

        target_list = _list_targets() + [
            connect_core.TargetUnit(screens.Target.InPost, log_level=log.DEBUG, break_detect=True),
        ]
        index = api.connect_core.send(key, target_list)
        if index < 0:
            if api.connect_core.last_timeout_was_silent:
                raise exceptions.ConnectionClosed()
            return None
        if kind == 'search':
            api._current_search = ()

    return None


def _search_in_board(api, board: str, search_list: list, want: tuple) -> None:
    # 從一般文章列表送出搜尋條件；搜不到時 PTT 跳出「找不到符合條件的文章」並留在一般列表
    cmd = ''.join(get_search_condition_cmd(data_type.NewIndex.BOARD, search_list))
    target_list = [
        connect_core.TargetUnit(screens.Target.NoSearchResult, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.InSearchList, log_level=log.DEBUG, break_detect=True),
    ]
    index = api.connect_core.send(cmd, target_list)
    # 搜尋是從已確認的一般列表送出的，標頭省略看板名稱時也認得是同一個看板
    if index == 1 and board_list_kind(api, last_screen(api), board, require_name=False) == 'search':
        api._current_search = want
        return

    if index == 0:
        # 關掉提示框；回到一般列表就留在板內，下一次不用重新進板
        index = api.connect_core.send(command.space, _list_targets())
        if index == 0 and board_list_kind(api, last_screen(api), board, require_name=False) == 'plain':
            api._current_search = ()
            raise exceptions.NoSearchResult()

        # 提示框之後畫面不明；下一次 goto_board 走完整路徑
        forget_current_board(api)
        if index < 0 and api.connect_core.last_timeout_was_silent:
            raise exceptions.ConnectionClosed()
        raise exceptions.NoSearchResult()

    # 搜尋後認不得畫面 (跟改版前一樣：完全沒回應是斷線，其他當成進不了看板)
    forget_current_board(api)
    if index < 0 and api.connect_core.last_timeout_was_silent:
        raise exceptions.ConnectionClosed()
    raise exceptions.NoSuchBoard(api.config, board)


def goto_board(api, board: str, refresh: bool = False, end: bool = False,
               search_list: Optional[list] = None) -> None:
    """進到 board 的文章列表；給 search_list 時進到該條件的搜尋結果 (搜不到丟 NoSearchResult)。
    refresh=True 保證最後一個畫面是剛重畫的一般列表 (不跟 search_list 一起用)。

    上一個 API 已經停在同一個看板時不重新進板 (見 _stay_in_board)。"""
    want = search_key(search_list)
    state = _stay_in_board(api, board, want)
    if state == 'plain' and refresh:
        # 呼叫端要讀最新畫面 (get_board_info 的人氣)：不重新進板，重畫一次
        index = api.connect_core.send(command.refresh, _list_targets(), refresh=False)
        if index < 0 and api.connect_core.last_timeout_was_silent:
            raise exceptions.ConnectionClosed()
        if index != 0 or board_list_kind(api, last_screen(api), board) != 'plain':
            state = None
    if state is not None:
        if want and state == 'plain':
            _search_in_board(api, board, search_list, want)
        if end:
            _goto_board_end(api)
        return

    forget_current_board(api)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('qs')
    cmd_list.append(board)
    cmd_list.append(command.enter)
    cmd_list.append(command.ctrl_c * 5)

    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit('任意鍵', log_level=log.DEBUG, response=command.space * 5),
        connect_core.TargetUnit('互動式動畫播放中', log_level=log.DEBUG, response=command.ctrl_c * 5),
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.InBoardWithCursor, log_level=log.DEBUG, break_detect=True),
        connect_core.TargetUnit(screens.Target.MainMenu_Exiting, log_level=log.DEBUG, break_detect=True),
    ]

    if refresh:
        current_refresh = True
    else:
        if board.lower() in api._goto_board_list:
            current_refresh = True
        else:
            current_refresh = False
    api._goto_board_list.add(board.lower())

    # 這裡可能因為發現第一次進入看板會有進版畫面，一般來說都可以在 target_list 找到對應的標的
    # 但某些看板會卡在進版動畫中，但沒有顯示任意鍵繼續或互動是動畫，所以當 index == -1 (表示找不到標的 timeout 了)
    # 可以嘗試修改 cmd_list
    index = api.connect_core.send(cmd, target_list, refresh=current_refresh)
    if index == -1 and api.connect_core.last_timeout_was_silent:
        raise exceptions.ConnectionClosed()

    # index == 4 表示偵測到 MainMenu_Exiting，代表導航到看板失敗
    # 可能是暫時性的問題（閒置太久、連線狀態改變等），重試一次
    if index == 4:
        log.logger.debug('goto_board', board, 'failed, retrying')
        index = api.connect_core.send(cmd, target_list, refresh=True)
        if index == -1 and api.connect_core.last_timeout_was_silent:
            raise exceptions.ConnectionClosed()
        if index == 4:
            raise exceptions.NoSuchBoard(api.config, board)

    if index in (2, 3):
        api._current_board = board.lower()
        api._current_search = ()
        if want:
            _search_in_board(api, board, search_list, want)

    if end:
        _goto_board_end(api)


def _goto_board_end(api) -> None:
    cmd_list = []
    cmd_list.append('1')
    cmd_list.append(command.enter)
    cmd_list.append('$')
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(screens.Target.InBoard, log_level=log.DEBUG, break_detect=True),
    ]

    api.connect_core.send(cmd, target_list)


def one_thread(api):
    current_thread_id = threading.get_ident()
    if current_thread_id != api._thread_id:
        raise exceptions.MultiThreadOperated()


def check_user_exist(api, ptt_id: str) -> None:
    if ptt_id.lower() not in api._exist_user_list:
        api.get_user(ptt_id)


def check_board(api, board: str, check_moderator: bool = False) -> Dict:
    if board.lower() not in api._exist_board_list:
        board_info = _api_get_board_info.get_board_info(api, board, get_post_kind=False, call_by_others=False)
        api._exist_board_list.add(board.lower())
        api._board_info_list[board.lower()] = board_info

        moderators = board_info[data_type.BoardField.moderators]
        moderators = [x.lower() for x in moderators]
        api._moderators[board.lower()] = moderators
        api._board_info_list[board.lower()] = board_info

    if check_moderator:
        if api.ptt_id.lower() not in api._moderators[board.lower()]:
            raise exceptions.NeedModeratorPermission(board)

    return api._board_info_list[board.lower()]
