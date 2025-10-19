import re
import sys

from uao import register_uao

from . import log

register_uao()


class Target:
    MainMenu = [
        '離開，再見',
        '人, 我是',
        '[呼叫器]',
    ]

    MainMenu_Exiting = [
        '【主功能表】',
        '您確定要離開',
    ]

    PTT1_QueryPost = [
        '請按任意鍵繼續',
        '文章代碼(AID):',
        ('文章網址:', '本看板目前不提供文章網址')
    ]

    PTT2_QueryPost = [
        '請按任意鍵繼續',
        '文章代碼(AID):'
    ]

    InBoard = [
        '看板資訊/設定',
        '文章選讀',
        '相關主題'
    ]

    InBoardWithCursor = [
        '【',
        '看板資訊/設定',
    ]
    InBoardWithCursorLen = len(InBoardWithCursor)

    # (h)說明 (←/q)離開
    # (y)回應(X%)推文(h)說明(←)離開
    # (y)回應(X/%)推文 (←)離開

    InPost = [
        '瀏覽',
        '頁',
        ')離開'
    ]

    PostEnd = [
        '瀏覽',
        '頁 (100%)',
        ')離開'
    ]

    InWaterBallList = [
        '瀏覽',
        '頁',
        '說明',
    ]

    WaterBallListEnd = [
        '瀏覽',
        '頁 (100%)',
        '說明'
    ]

    PostIP_New = [
        '※ 發信站: 批踢踢實業坊(ptt.cc), 來自:'
    ]

    PostIP_Old = [
        '◆ From:'
    ]

    Edit = [
        '※ 編輯'
    ]

    PostURL = [
        '※ 文章網址'
    ]

    Vote_Type1 = [
        '◆ 投票名稱',
        '◆ 投票中止於',
        '◆ 票選題目描述'
    ]

    Vote_Type2 = [
        '投票名稱',
        '◆ 預知投票紀事',
    ]

    AnyKey = '任意鍵'

    InTalk = [
        '【聊天說話】',
        '線上使用者列表',
        '查詢網友',
        '顯示上幾次熱訊'
    ]

    InUserList = [
        '休閒聊天',
        '聊天/寫信',
        '說明',
    ]

    InMailBox = [
        '【郵件選單】',
        '[~]資源回收筒',
        '鴻雁往返'
    ]

    InMailBoxWithCursor = [
        '【郵件選單】',
        '[~]資源回收筒',
    ]
    InMailBoxWithCursorLen = len(InMailBoxWithCursor)

    InMailMenu = [
        '【電子郵件】',
        '我的信箱',
        '把所有私人資料打包回去',
        '寄信給帳號站長',
    ]

    PostNoContent = [
        '◆ 此文章無內容',
        AnyKey
    ]

    InBoardList = [
        '【看板列表】',
        '選擇看板',
        '只列最愛',
        '已讀/未讀'
    ]

    use_too_many_resources = [
        '程式耗用過多計算資源'
    ]

    Animation = [
        '★ 這份文件是可播放的文字動畫，要開始播放嗎？'
    ]

    CursorToGoodbye = MainMenu.copy()

    content_start = '─── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──'
    content_end_list = [
        '--\n※ 發信站: 批踢踢實業坊',
        '--\n※ 發信站: 批踢踢兔(ptt2.cc)',
        '--\n※ 發信站: 新批踢踢(ptt2.twbbs.org.tw)'
    ]

    OnlineUser = [
        '編號',
        '日 期'
    ]


def show(config, screen_queue, function_name=None):
    if config.log_level != log.DEBUG:
        return

    if isinstance(screen_queue, list):
        for Screen in screen_queue:
            print('-' * 50)
            try:
                print(
                    Screen.encode(
                        sys.stdin.encoding, "replace").decode(
                        sys.stdin.encoding))
            except Exception:
                print(Screen.encode('utf-8', "replace").decode('utf-8'))
    else:
        print('-' * 50)
        try:
            print(screen_queue.encode(
                sys.stdin.encoding, "replace").decode(
                sys.stdin.encoding))
        except Exception:
            print(screen_queue.encode('utf-8', "replace").decode('utf-8'))

        print('len:' + str(len(screen_queue)))
    if function_name is not None:
        print('錯誤在 ' + function_name + ' 函式發生')
    print('-' * 50)


xy_pattern_h = re.compile(r'^=ESC=\[[\d]+;[\d]+H')
xy_pattern_s = re.compile(r'^=ESC=\[[\d]+;[\d]+s')


class VT100Parser:
    def _h(self):
        self._cursor_x = 0
        self._cursor_y = 0

    def _2j(self):
        self.screen = [''] * 24
        self.screen_length = dict()

    def _move(self, x, y):
        self._cursor_x = x
        self._cursor_y = y

    def _newline(self):
        self._cursor_x = 0
        self._cursor_y += 1

    def _k(self):
        if self._cursor_x == 0:
            # nothing happen but cause error
            return
        self.screen[self._cursor_y] = self.screen[self._cursor_y][:self._cursor_x]

    def __init__(self, bytes_data, encoding):
        # self._data = data
        # https://www.csie.ntu.edu.tw/~r88009/Java/html/Network/vt100.htm

        self._cursor_x = 0
        self._cursor_y = 0
        self.screen = [''] * 24
        self.screen_length = dict()

        data = bytes_data.decode(encoding, errors='replace')

        # remove color
        data = re.sub(r'\x1B\[[\d+;]*m', '', data)
        data = re.sub(r'[\x1B]', '=ESC=', data)
        data = re.sub(r'[\r]', '', data)
        while ' \x08' in data:
            data = re.sub(r' \x08', '', data)

        if '=ESC=[2J' in data:
            data = data[data.rfind('=ESC=[2J') + len('=ESC=[2J'):]

        count = 0
        while data:
            count += 1
            while True:
                if not data.startswith('=ESC='):
                    break
                if data.startswith('=ESC=[H'):
                    data = data[len('=ESC=[H'):]
                    self._h()
                    continue
                elif data.startswith('=ESC=[K'):
                    data = data[len('=ESC=[K'):]
                    self._k()
                    continue
                elif data.startswith('=ESC=[s'):
                    data = data[len('=ESC=[s'):]
                    continue
                break

            xy_result = None
            xy_result_h = xy_pattern_h.search(data)
            if not xy_result_h:
                xy_result_s = xy_pattern_s.search(data)
                if xy_result_s:
                    xy_result = xy_result_s
            else:
                xy_result = xy_result_h

            if xy_result:
                xy_part = xy_result.group(0)

                new_y = int(xy_part[6:xy_part.find(';')]) - 1
                new_x = int(xy_part[xy_part.find(';') + 1: -1])
                # log.py.info('xy', xy_part, new_x, new_y)
                self._move(new_x, new_y)

                data = data[len(xy_part):]

            else:
                if data.startswith('\n'):
                    data = data[1:]
                    self._newline()
                    continue

                # print(f'-{data[:1]}-{len(data[:1].encode("big5-uao", "replace"))}')

                if self._cursor_y not in self.screen_length:
                    self.screen_length[self._cursor_y] = len(self.screen[self._cursor_y].encode(encoding, 'replace'))

                current_line_length = self.screen_length[self._cursor_y]
                replace_mode = False
                if current_line_length < self._cursor_x:
                    append_space = ' ' * (self._cursor_x - current_line_length)
                    self.screen[self._cursor_y] += append_space
                elif current_line_length > self._cursor_x:
                    replace_mode = True

                next_newline = data.find('\n')
                next_newline = 1920 if next_newline < 0 else next_newline

                next_esc = data.find('=ESC=')
                next_esc = 1920 if next_esc < 0 else next_esc
                if next_esc == 0:
                    break

                current_index = min(next_newline, next_esc)

                current_data = data[:current_index]
                current_data_length = len(current_data.encode(encoding, 'replace'))
                # print('=', current_data, '=', current_data_length)
                if replace_mode:
                    current_line = self.screen[self._cursor_y][:self._cursor_x]
                    current_line += current_data
                    current_line += self.screen[self._cursor_y][self._cursor_x + len(current_data):]

                    self.screen[self._cursor_y] = current_line
                else:
                    self.screen[self._cursor_y] += current_data
                    self._cursor_x += current_data_length
                    self.screen_length[self._cursor_y] = self._cursor_x

                data = data[current_index:]

                # print('\n'.join(self.screen))
        # print('\n'.join(self._screen))
        # print('=' * 20)
        # print(data)

        # print('Spend', count, 'cycle')
        self.screen = '\n'.join(self.screen)

