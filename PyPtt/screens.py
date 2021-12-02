import re
import sys

from SingleLog.log import Logger
from uao import register_uao

if __name__ == '__main__':
    import lib_util
else:
    from . import lib_util

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

    QueryPost = [
        '請按任意鍵繼續',
        '───────┘',
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
        '鴻雁往返'
    ]

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


def show(config, screen_queue, function_name=None):
    if config.log_level != Logger.TRACE:
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


displayed = False


def vt100(ori_screen: str, no_color: bool = True) -> str:
    result = ori_screen

    # temp = None
    # for c in result.encode('utf-8'):
    #     if not temp:
    #         temp = f'bytes([{c}'
    #     else:
    #         temp += f', {c}'
    # temp += '])'
    # print(temp)

    if no_color:
        result = re.sub('\x1B\[[\d+;]*m', '', result)

    result = re.sub(r'[\x1B]', '=PTT=', result)

    # global displayed
    # if not displayed:
    #     display = ('★' in result)
    #     if display:
    #         displayed = True
    # else:
    #     display = False
    #
    # if display:
    #     print('=1=' * 10)
    #     print(result)
    #     print('=2=' * 10)

    # result = '\n'.join(
    #     [x.rstrip() for x in result.split('\n')]
    # )

    # 編輯文章時可能會有莫名的清空問題，需再注意
    # if result.endswith('=PTT=[H'):
    #     print('!!!!!!!!=PTT=[H=PTT=[H=PTT=!!!!!!!!!!!!!!!')
    while '=PTT=[H' in result:
        if result.count('=PTT=[H') == 1 and result.endswith('=PTT=[H'):
            break
        result = result[result.find('=PTT=[H') + len('=PTT=[H'):]
    while '=PTT=[2J' in result:
        result = result[result.find('=PTT=[2J') + len('=PTT=[2J'):]

    pattern_result = re.compile('=PTT=\[(\d+);(\d+)H$').search(result)
    last_position = None
    if pattern_result is not None:
        # print(f'Before [{pattern_result.group(0)}]')
        last_position = pattern_result.group(0)

    # 進入 PTT 時，有時候會連分類看版一起傳過來然後再用主功能表畫面直接繪製畫面
    # 沒有[H 或者 [2J 導致後面的繪製行數錯誤

    if '=PTT=[1;3H主功能表' in result:
        result = result[result.find('=PTT=[1;3H主功能表') + len('=PTT=[1;3H主功能表'):]

    # if '=PTT=[1;' in result:
    #     if last_position is None:
    #         result = result[result.rfind('=PTT=[1;'):]
    #     elif not last_position.startswith('=PTT=[1;'):
    #         result = result[result.rfind('=PTT=[1;'):]

    # print('-'*50)
    # print(result)
    result_list = re.findall('=PTT=\[(\d+);(\d+)H', result)
    for (line_count, space_count) in result_list:
        line_count = int(line_count)
        space_count = int(space_count)
        current_line = result[
                       :result.find(
                           f'[{line_count};{space_count}H'
                       )].count('\n') + 1
        # if display:
        #     print(f'>{line_count}={space_count}<')
        #     print(f'>{current_line}<')
        if current_line > line_count:
            # if LastPosition is None:
            #     pass
            # elif LastPosition != f'=PTT=[{line_count};{space_count}H':
            #     print(f'current_line [{current_line}]')
            #     print(f'line_count [{line_count}]')
            #     print('Clear !!!')
            # print(f'!!!!!!!!=PTT=[{line_count};{space_count}H')

            result_lines = result.split('\n')
            target_line = result_lines[line_count - 1]
            if f'=PTT=[{line_count};{space_count}H=PTT=[K' in result:
                # 如果有 K 則把該行座標之後，全部抹除
                target_line = target_line[:space_count - 1]

                # OriginIndex = -1
                origin_line = None
                # for i, line in enumerate(result_lines):
                for line in result_lines:
                    if f'=PTT=[{line_count};{space_count}H=PTT=[K' in line:
                        # OriginIndex = i
                        origin_line = line
                        break

                if origin_line.count('=PTT=') > 2:
                    origin_line = origin_line[
                                  :lib_util.findnth(origin_line, '=PTT=', 3)
                                  ]

                # result_lines[OriginIndex] = result_lines[OriginIndex].replace(
                #     origin_line,
                #     ''
                # )

                origin_line = origin_line[
                              len(f'=PTT=[{line_count};{space_count}H=PTT=[K'):
                              ]

                # log.showValue(
                #     Logger.INFO,
                #     'origin_line',
                #     origin_line
                # )

                new_target_line = f'{target_line}{origin_line}'
                result_lines[line_count - 1] = new_target_line
            result = '\n'.join(result_lines)
        elif current_line == line_count:
            # print(f'!!!!!=PTT=[{line_count};{space_count}H')
            current_space = result[
                            :result.find(
                                f'=PTT=[{line_count};{space_count}H'
                            )]
            current_space = current_space[
                            current_space.rfind('\n') + 1:
                            ]
            # if display:
            #     print(f'>>{current_space}<<')
            #     print(f'ori length>>{len(current_space)}<<')
            #     newversion_length = len(current_space.encode('big5uao', 'ignore'))
            #     print(f'newversion_length >>{newversion_length}<<')

            # current_space = len(current_space.encode('big5', 'replace'))
            current_space = len(current_space)
            # if display:
            #     print(f'!!!!!{current_space}')
            if current_space > space_count:
                # if display:
                #     print('1')
                result = result.replace(
                    f'=PTT=[{line_count};{space_count}H',
                    (line_count - current_line) * '\n' + space_count * ' '
                )
            else:
                # if display:
                #     print('2')
                result = result.replace(
                    f'=PTT=[{line_count};{space_count}H',
                    (line_count - current_line) * '\n' + (space_count - current_space) * ' '
                )
        else:
            result = result.replace(
                f'=PTT=[{line_count};{space_count}H',
                (line_count - current_line) * '\n' + space_count * ' '
            )

        # while '=PTT=[K' in result:
        #     Target = result[result.find('=PTT=[K'):]

        #     print(f'Target[{Target}]')

        #     index1 = Target.find('\n')
        #     index2 = Target.find('=PTT=')
        #     if index2 == 0:
        #         index = index1
        #     else:
        #         index = min(index1, index2)

        #     break
        #     Target = Target[:index]
        #     print('===' * 20)
        #     print(result)
        #     print('-=-' * 20)
        #     print(Target)
        #     print('===' * 20)
        #     result = result.replace(Target, '')

        # print(Target)
        # print('===' * 20)

    if last_position is not None:
        result = result.replace(last_position, '')

    # if display:
    #     print('-Final-' * 10)
    #     print(result)
    #     print('-Final-' * 10)
    return result


xy_pattern_h = re.compile('^=ESC=\[[\d]+;[\d]+H')
xy_pattern_s = re.compile('^=ESC=\[[\d]+;[\d]+s')


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
        data = re.sub('\x1B\[[\d+;]*m', '', data)
        data = re.sub(r'[\x1B]', '=ESC=', data)
        data = re.sub(r'[\r]', '', data)

        # print('---' * 8)
        # print(encoding)
        # print(bytes_data)
        # print(data)
        # print('---' * 8)

        if '=ESC=[2J' in data:
            data = data[data.rfind('=ESC=[2J') + len('=ESC=[2J'):]

        count = 0
        while data:
            count += 1
            while True:
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
                # print('!=', xy_part)

                new_y = int(xy_part[6:xy_part.find(';')]) - 1
                new_x = int(xy_part[xy_part.find(';') + 1: -1])
                # print(new_x, new_y)
                self._move(new_x, new_y)

                data = data[len(xy_part):]

            else:
                if data[:1] == '\n':
                    data = data[1:]
                    self._newline()
                    continue
                # print(f'-{data[:1]}-{len(data[:1].encode("big5-uao", "replace"))}')

                if self._cursor_y not in self.screen_length:
                    self.screen_length[self._cursor_y] = len(self.screen[self._cursor_y].encode('big5-uao', 'replace'))

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
                current_data_length = len(current_data.encode('big5-uao', 'replace'))

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


if __name__ == '__main__':
    # 看板警察
    screen = b'\r\n      \xa2\xf6        \xa2\xf7\xa3P\xa2\xf6 E c \xa2\xfci                  \x1b[37;40m \xa2f   \xa2g\xa2d \x1b[m\r\n        \xa3R\xa3@  \xa2\xd1               \xa3P g  ..        \x1b[30;47m\xa2k\x1b[33m/\x1b[37;40m\xa2k\x1b[m   \x1b[33;47m \\ \x1b[37;40m\xa2k\x1b[m\r\n      \x1b[47m                               \x1b[m          \x1b[37;43m\xa2p\x1b[47m \x1b[;35m\xa2f\x1b[1m\xa2e\xa2f\x1b[;33;47m \xa2j\x1b[m\r\n     \x1b[30;47m    \xa2z\xa2f \xa2d\xa2e  \xa2f\xa2{ \xa2e\xa2{          \x1b[m      \x1b[1;35m\xa2\xa8\x1b[47m\xa2g\x1b[45m\xa1\xbd\xa2i\xa2i\xa2i\x1b[;37;45m\xa2\xab \x1b[35;40m\xa2\xa9\x1b[m\r\n     \x1b[30;47m     \xa2m\xa2}  \xa2m   \xa2m  \xa2f\xa2t  \xa1\xe3\xa1\xaf    \x1b[m\xa2\xa9    \x1b[1;35;45m\xa1\xbd\xa2i\xa2i\xa2i\xa2i\xa2i\xa2i\xa2l\x1b[m\r\n       \x1b[47m                              \x1b[m\xa2\xab    \x1b[1;35m\xa2y\xa2i\x1b[45m\xa1\xbd\xa2i\xa2i\xa2i\xa2i\xa2i\xa2o\x1b[;35m\xa2k\x1b[m\xa2e\r\n         \x1b[1;30m[ptt2.twbbs.org / ptt2.cc]\x1b[m          \x1b[1;35m\xa2i\x1b[40m\xa2\xab\x1b[;37;40m\xa2f\x1b[1;35;47m    \x1b[;37;40m\xa2g\x1b[1;35m\xa2\xaa\x1b[45m\xa2m\x1b[m \x1b[47m    \x1b[m\r\n                ..illust by senkousha        \x1b[1;35m\xa2\xaa\x1b[;30;47m\xa2m\xa1\xac\x1b[31m\xa1\xbb\x1b[30m  \xa1\xab \x1b[40m \x1b[;35m\xa2\xab\x1b[47m      \x1b[m\r\n                                             \xa1\xb4  \x1b[30;47m\xa2f\xa2f\xa2f\xa2f\x1b[m  \xa1\xb4 \x1b[30;47m\xa2g\xa2h\x1b[m\r\n\x00\xff\xfd\x18\xff\xfa\x18\x01\xff\xf0\xff\xfd\x1f\xff\xfb\x01\xff\xfb\x03\xff\xfb\x00\xff\xfd\x00\x1b[H\x1b[2J\x1b[m\x1b[1;33m   \xa1O  \x1b[m     \x1b[47m \x1b[m \x1b[47m \x1b[1;30m       \x1b[;30;47m\xa2\x1b[40me\x1b[m \xa2\x1b[47m\xa8\x1b[1;30;40m\xa2\x1b[m\xa8\x1b[47m\xa2\x1b[m\xab\x1b[30m\xa2\x1b[m\xa8\x1b[1;30;47m  \x1b[37m\xa3\xbb\x1b[30m  \x1b[m\xa2o\x1b[47m \x1b[30;40m\xa2\xab\x1b[m /   \x1b[33m/\x1b[m  \x1b[33m\xa2\xa8\x1b[m  \x1b[33m/ \xa2\xa8\x1b[30m\xa2\x1b[33mo\x1b[m    \x1b[33m\xa2\x1b[30m\xa9\x1b[33m\xa2\xa9\x1b[30m \x1b[1;33m\xa1\xf9\x1b[30m \x1b[m   \xa2B\r\n\x1b[1;33m \xa1\xb4\x1b[m     \x1b[33m.\x1b[m   \x1b[33;47m  \x1b[30m\xa2j\x1b[37m \x1b[1;33m \x1b[30m   \x1b[m \x1b[1m\xa2\x1b[mf\xa2\xab\xa2\xa9 \x1b[47m \x1b[m \x1b[1;30m \x1b[47m  \x1b[37m\xa1\xb4\x1b[30m  \x1b[;37;47m \x1b[33m \x1b[40m \x1b[m\xa2o /    \x1b[33m\xa2k\x1b[30m\xa2\x1b[43mc\xa2\x1b[40md\x1b[43m\xa2\x1b[33;40mc\x1b[30;43m /\x1b[33m\xa2\x1b[40ml\xa2\x1b[37;43ml\x1b[33;40m\xa2\x1b[30;43mc\xa2d\x1b[40m\xa2\x1b[43mc_\xa2\x1b[31m\xaa\x1b[40m\xa2\x1b[1m\xab\x1b[;33;40m \x1b[m   \\\r\n     \x1b[1;33m\xa3\xbb\x1b[m    \x1b[30;47m\xa2o\x1b[33m  \x1b[37m \x1b[1;30m    \x1b[40m \x1b[m   \xa2d\x1b[1;47m\xa2\x1b[;37;47mf\x1b[m\xa2\xab\x1b[1;30m \x1b[;30;47m\xa2\x1b[37m\xab\x1b[1;30m     \x1b[m\xa2p\x1b[47m \x1b[m\xa2n/    \x1b[33m\xa2j\xa2\x1b[30;43mc\xa2e\x1b[40m\xa2\x1b[43md\xa3\xbf\xa2j\xa2k\xa3\xbd\xa2c\xa2\x1b[40md\x1b[43m\xa2\x1b[33mb\x1b[37m \x1b[30m\xa1\x1b[40m\xb6\x1b[m \xa2\xad   \\\r\n         \x1b[1;33m.\x1b[m   \x1b[33;47m   \x1b[1m   \x1b[;33;47m \x1b[m \x1b[30;47m\xa2d\xa2e\xa2h\x1b[m\xa2\xaa\xa2\xa9\x1b[30m\xa2\x1b[47mf\xa2\x1b[37md\x1b[1;33m  \x1b[;33;47m   \x1b[30m \x1b[m\xa2l      \x1b[30;43m/\x1b[m\xa2\x1b[30m\xa8\x1b[1;33m\xa2\x1b[;30;40md\x1b[1;33m  \x1b[;30;43m\xa3\x1b[33m\xb0\x1b[37m  \x1b[30m\xa2j\x1b[33m\xa1\x1b[30m\xd4\x1b[m\xa2\x1b[30m\xa8\x1b[1;33m\xa2\x1b[;30;40md\x1b[m \x1b[30m\xa1\x1b[43m\xbf \x1b[m    \xa2\xad\r\n \x1b[33m\xa1D\x1b[m         \x1b[30;47m\xa2p \x1b[33m \x1b[1;37m\xa1\xb4\x1b[;33;47m   \x1b[m\xa2f\xa2g\x1b[47m  \x1b[30m\xa2\xaa\x1b[m\xa2\xaa\x1b[1;30m\xa2\x1b[;30;40m\xab\x1b[47m\xa2\x1b[37m\xab\x1b[33m    \x1b[37m\xa2c\x1b[m   \x1b[30m\xa1\x1b[43m\xbf\x1b[33m\xa1\x1b[40m\xb6\x1b[m \x1b[43m \x1b[47m\xa2\x1b[1;33m\xaa\x1b[;33;40m\xa1\x1b[1m`\x1b[37m"\xa2\x1b[;33;43m\xa8\x1b[37m       \x1b[47m\xa2\x1b[1;33m\xaa\x1b[;33;40m\xa1\x1b[1m`\x1b[37m"\xa2\x1b[;33;43m\xa8\x1b[30m \x1b[m \x1b[33m\xa1\x1b[43m\xb6\x1b[30m\xa1\x1b[40m\xbf\x1b[m \xa2B\r\n\x1b[1;33m\xa3\xbb\x1b[m   \x1b[1;33m.\x1b[m \x1b[1;33m\xa1\x1b[;33;40mL\x1b[m   \x1b[1;33m\xa1D\x1b[m\xa2\xaa\x1b[33;47m \x1b[1;30m\xa3_lzcat\x1b[;30;47m \x1b[1;33m \x1b[;33;47m   \x1b[30m\xa2\xaa\xa2\xab\x1b[33m  \x1b[1;37m\xa3\xbb\x1b[;33;47m  \x1b[m\xa2\xab |\x1b[33m \x1b[m \x1b[30;43m\\\xa1^\x1b[33;40m \x1b[30;43m\xa2k\x1b[33;40m\xa2h\xa2f\xa2\x1b[43mg\x1b[37m     \xa2\x1b[33m\xa8\xa2\x1b[40mh\xa2f\xa2g\x1b[37;43m  \x1b[m \x1b[30;43m\xa3\xa2/\x1b[m   \\\r\n\x1b[1;30m\xa2b\xa2c\xa2b\xa1\xc4\x1b[m      \x1b[1;33m.\x1b[m  \xa2\xaa\x1b[33;47m \x1b[30m\xa2\xac\xa2\xaa\xa1\xc3\xa2\xab\xa2\xad\x1b[33m     \x1b[1;37m\xa2d\x1b[40m\xa2\xab\x1b[m  \xa1W\x1b[33m \x1b[m \x1b[1;33m\xa2\x1b[;33;40m\xaa\x1b[31;43m+\x1b[m \x1b[30;43m\xa2n\x1b[31m\'"\x1b[30m               \x1b[31m"\'\x1b[33m \x1b[40m\xa2j\x1b[31;43m+\x1b[30;47m\xa2\x1b[43m\xa8\x1b[m\r\n        \xa1\xc3\x1b[30;47m\xa2h\xa2f\x1b[1;40m\xa2d\xa2b\xa1\xc4\x1b[;30;47m\xa2e\xa2d\xa2\x1b[35mb\xa2\x1b[30md\xa2d\xa2e\xa2g\x1b[1;33;40m  \x1b[m    \x1b[1;33m\xa1\xb4\x1b[;33;40m \x1b[m \x1b[33m \x1b[m  / \x1b[30m \xa1\x1b[43m\xb6      \x1b[37m \x1b[33m\xa3\x1b[30m\xbf    \x1b[37m    \x1b[33m\xa1\x1b[40m\xbf\x1b[m |\r\n\x1b[35m  \x1b[1;33m \x1b[m                 \xa1\xc3\xa1\xc3\x1b[30m \x1b[45m \x1b[41m \x1b[40m\xab\x1b[m        \x1b[1;33m \x1b[m  \x1b[1m\xa2\xa8\xa2\x1b[me\xa2c\xa2A  | \x1b[30m\xa1\x1b[43m\xb6     \x1b[33m\xa2\x1b[30mc\xa2\x1b[31md\xa1\x1b[33m\xc5\x1b[30m    \x1b[33m\xa1\x1b[40m\xbf\x1b[m  |\r\n\x1b[35m  \x1b[m  \x1b[1;33m\xa1\xb4\x1b[m             \x1b[30m\xa2\x1b[33m\xa8\xa2\xa9\x1b[m \x1b[34;45m \x1b[33m\xa2\x1b[41m\xa8\x1b[37;43m \x1b[33;40m \x1b[m\xa1\xc5\xa2\x1b[1;30mb\xa2c\x1b[m  \xa2\xac\x1b[1;33m \x1b[;30;47m\xa2g\xa2e\x1b[m    \x1b[31m \x1b[m/\x1b[31m \x1b[30m  \x1b[33m\xa2\xaa\x1b[30;43m   \x1b[33m\xa2\x1b[40mg\x1b[41m\xa2f\xa2\x1b[43mh\x1b[30m   \xa2\xa8\x1b[m \x1b[31m  \x1b[m\xa1\xfd    \x1b[1;33m\xa1\xb4\x1b[m\r\n\x1b[35m  \x1b[m                 \x1b[30m \x1b[33m\xa2\xaa\x1b[37;43m \x1b[33;45m\xa2\x1b[31;41m\xa9\x1b[30;43m   \x1b[47m\xa2f\x1b[m     \xa1\xc3      \xa2\xac \xa2b\x1b[1;33m \x1b[m|     \x1b[30m\xa2\x1b[43mf\x1b[33m\xa2\x1b[30mc    \xa2b\xa2\x1b[40md\x1b[33m\xa1U\x1b[m  \x1b[31m \x1b[m \\\r\n\x1b[1;35mP\x1b[m               \x1b[30m  \xa2\x1b[33m\xaa\x1b[30;43m\xa1\xc3\xa2\x1b[35;45m\xaa\x1b[31;41m \x1b[30;43m  \x1b[40m  \x1b[1;33m\xa3\xbb\x1b[m          \xa2\xa8\x1b[47m\xa2\x1b[30me\xa2f\x1b[m \xa1U      \x1b[30;43m\xa2l\x1b[33;40m\xa2\xa9\x1b[30;43m\xa2g\x1b[m     \x1b[33m\xa1U\x1b[m     \xa2B  \x1b[1;33m\xa3\xbb\x1b[m\r\n\x1b[1;35mt\x1b[m \x1b[35m  \x1b[m           \x1b[1;30m\xa2b\x1b[;30;40m\xa2\x1b[33m\xa8\x1b[30;43m   \x1b[31;45m \x1b[30;41m\xa2\x1b[33m\xa8\x1b[30;43m \x1b[33;40m\xa2k\x1b[m           \xa2\xac       /    \x1b[35m\xa2\x1b[m\xa8\xa2\x1b[30;43m\xab \x1b[33m  \x1b[40m\xa2h\xa2f\xa2d \xa1\xb6\x1b[37;47m \x1b[m\xa2\x1b[1;30m\xa9\x1b[m   \xa1Y\r\n\x1b[1;35mt\x1b[;35;40m \x1b[m      \x1b[1;33m\xa3\xbb\x1b[m   \xa2\xac \x1b[30m   \x1b[33m\xa2h\x1b[45m\xa2\x1b[35;41m\xab\x1b[30;40m \x1b[43m \x1b[33;40m\xa2n\x1b[m         \xa2\xac \x1b[31m\xa2b\xa2d\xa2f\xa2g\xa2d\x1b[m \x1b[1m\xa2\x1b[m\xa8\x1b[47m   \x1b[m\xa2\xa9\x1b[30;43m\xa2\x1b[33mg\x1b[30m  \x1b[37m  \xa2\x1b[33m\xa8\x1b[30m\xa2b\x1b[1;37m\xa2\x1b[;37;43m\xa8\x1b[35;47m.\xa1O\x1b[1;30;40m\xa2\xa9\x1b[m \xa1Y\r\n\x1b[1;35m2\x1b[m  \x1b[35m \x1b[1;30m\xa2b\xa2c\xa2\x1b[me\x1b[30;47m\xa2g\xa2\x1b[40mh\x1b[m   \x1b[1m\xa2\xa8\x1b[;33;43m\xa2\x1b[31;40mh\x1b[33;41m\xa2\x1b[30m\xa8\x1b[33;43m \x1b[40m\xa2o\x1b[m\xa2\xa9      \xa4\x1b[30mH\x1b[m  \x1b[1;33;41m\xa1\xb4\x1b[;37;41m  \x1b[1;31m \xa2j\x1b[;37;41m   \x1b[31;47m\xa2\xab\x1b[35m\xa2\x1b[1;33m\xa9\x1b[35;45m\xa2\x1b[47m\xa8\x1b[;37;47m  \xa1\x1b[m\xb6 \x1b[30;43m\xa2\xa9  \x1b[33m\xa1\x1b[30m\xc3\x1b[37m \x1b[33;47m\xa2\x1b[37m\xab \xa2\x1b[1;35m\xa9\x1b[;35;47m \x1b[1m\xa2\xa8\x1b[30m \x1b[40m\xa2\x1b[;35;40m\xa9\x1b[m\r\n\x1b[1;35m.\x1b[m  \x1b[35m  \x1b[m           \xa2\x1b[32;47m\xa8\x1b[37m \x1b[30;43m  \xa2\xab \x1b[33m\xa2\x1b[30;40mg\x1b[37;45m\xa1\x1b[47m\xb6 \x1b[m   \xa1\xd4 \x1b[30;41m\xa2\xab\x1b[1;31m\xa2d\xa2e\xa2\xab\x1b[37m\xa2b\xa2\x1b[;37;41md\x1b[1;30;47m\xa2\xad\x1b[35m\xa2\x1b[;35;47m\xaa\x1b[43m\xa2\xa9\x1b[47m\xa2\xab\xa3\xbb\x1b[37m\xa1\x1b[45m\xb6\x1b[30m\xa2\xaa\x1b[m \x1b[30;43m\xa2\xa9\x1b[33;47m\xa2\xab  \x1b[37m \x1b[35m\xa2\xa8\x1b[1;33;45m\xa2\x1b[;33;45m\xab\x1b[1;35;47m\xa2\x1b[;32;47m\xab\x1b[1;30m\xa2\xac\x1b[40m\xa2g\x1b[m\r\n\x1b[1;35mc\x1b[m  \x1b[35m  \x1b[m         \x1b[30;47m\xa2o\x1b[33m \x1b[35m\xa3\xbb\x1b[32;45m \x1b[33;43m    \x1b[45m\xa2\x1b[30mo\x1b[37;47m \xa1\x1b[m\xbf    \x1b[30;41m\xa2\xab\x1b[1;31m \xa2o\x1b[;37;41m   \x1b[1m\xa2\xa8\x1b[;37;47m\xa2\xab    \x1b[1;30m\xa2\x1b[;30;45m\xad\x1b[1;35;47m\xa2\x1b[;37;47m\xab\x1b[35m\xa1O\x1b[32m\xa2\x1b[37m\xaa \x1b[30m \x1b[35m\xa2\xaa\xa2\x1b[1m\xab\xa2\xa8\x1b[;37;47m  \x1b[35m\xa1O\x1b[37m \xa2\x1b[45m\xa8\x1b[47m \x1b[30m\xa2\x1b[1m\xac \x1b[;35;47m\xa3\xbb\x1b[1;30m\xa2\xaa\x1b[m\r\n\x1b[1;35mc\x1b[33m  \x1b[;35;40m \x1b[1;33m\xa1\xb4 \x1b[m     \x1b[30m\xa1\x1b[47m\xbf\x1b[1;33;45m\xa2\x1b[35;47m\xa8\x1b[;35;47m\xa2\x1b[37m\xa8\x1b[45m\xa2\x1b[35m\xab\x1b[43m\xa2k\x1b[37m \x1b[30m\xa2\xa8\x1b[37;45m \x1b[47m\xa1\x1b[m\xbf  \x1b[30;41m\xa2\xab\x1b[37m   \x1b[1;31m\xa1\x1b[;31;41m\xb6\x1b[37m \x1b[31m\xa2\x1b[1;37md\x1b[47m\xa2\x1b[;37;47mn \xa2\x1b[42m\xaa\x1b[1;35;45m\xa2\x1b[47m\xa8\x1b[;35;47m\xa3\xbb\x1b[37m  \x1b[30m\\\x1b[37m  \x1b[35m.\xa2\x1b[37m\xa8 \x1b[30m   \x1b[1m\xa2\x1b[;30;45m\xad\x1b[1;35m\xa2\x1b[33;43m\xaa\x1b[;35;45m\xa2\x1b[47m\xa9\x1b[37m \x1b[35m\xa3\xbb\x1b[37m \x1b[30m\xa2A\x1b[37m   \x1b[35m\xa2\xa9\x1b[37m\xa2 \x1b[m\r\n\xa1@\xa5\xd8\xabe\xa6\xb3\xa1\x1b[31mi\x1b[1m605\x1b[;31m\xa1j\x1b[m\xa6\xec\xb3X\xab\xc8\xa6b \x1b[1;33m\xa7\xe5\xbd\xf0\xbd\xf0\xa8\xdf \x1b[m\xc5\xe9\xc5\xe7\xaeL\xa9]\xaa\xba\xad\xb7\xaa\xf6\xa1@\xa1@\x1b[;41;33;1mCOVID-19\xb8\xea\xb0T\xbd\xd0\xa6\xdc EOC \xac\xdd\xaaO\x1b[m\r\n\r\n\r\n\r\n\x1b[s\x1b[23;1s \x1b[m\x1b[;1;31m\xa1\xb8\x1b[;33;1m\xa7\xe5\xbd\xf0\xbd\xf0\xa8\xdf\xa1D\xa9x\xa4\xe8\xaf\xbb\xb5\xb7\xb1M\xad\xb6\xa6\xa8\xa5\xdf\x1b[;31;1m\xa1\xb8\x1b[m  \x1b[;44;1m f\x1b[;36m https://www.facebook.com/Ptt2TW/ \x1b[m\x1b[s\r\n\x1b[s\x1b[24;1s \x1b[m\x1b[;1;34m\xab\xd8\xbd\xd0\xb1K\xa4\xc1\xc3\xf6\xaa` Ptt2 Facebook \xaf\xbb\xb5\xb7\xb9\xce\xa9M\xa5\xbb\xaf\xb8 SYSOP \xaaO\xc4\xc0\xa5X\xaa\xba\xb0T\xae\xa7\xa4\xce\xa4\xbd\xa7i\xa1C \x1b[;31;1;5mHOT! \x1b[m\x1b[s\x1b[21;1H\x1b[K\x1b[m\xbd\xd0\xbf\xe9\xa4J\xa5N\xb8\xb9\xa1A\xa9\xce\xa5H guest \xb0\xd1\xc6[\xa1A\xa9\xce\xa5H new \xb5\xf9\xa5U: \x1b[7m              \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08CoidngMan,\x1b[m\x1b[22;1H\x1b[K\x1b[m\xbd\xd0\xbf\xe9\xa4J\xb1z\xaa\xba\xb1K\xbdX: \x1b[22;1H\x1b[K\x1b[m\xe6\xad\xa3\xe5\x9c\xa8\xe6\xaa\xa2\xe6\x9f\xa5\xe5\xb8\xb3\xe8\x99\x9f\xe8\x88\x87\xe5\xaf\x86\xe7\xa2\xbc...\x07\x1b[22;1H\x1b[K\x1b[m\xb1K\xbdX\xa4\xa3\xb9\xef\xb3\xe1\xa1I\xbd\xd0\xc0\xcb\xacd\xb1b\xb8\xb9\xa4\xce\xb1K\xbdX\xa4j\xa4p\xbcg\xa6\xb3\xb5L\xbf\xe9\xa4J\xbf\xf9\xbb~\xa1C\x1b[21;1H\x1b[K\x1b[m\xbd\xd0\xbf\xe9\xa4J\xa5N\xb8\xb9\xa1A\xa9\xce\xa5H guest \xb0\xd1\xc6[\xa1A\xa9\xce\xa5H new \xb5\xf9\xa5U: \x1b[7m              \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x07'
    # screen = screen.decode('utf-8')
    # print(screen)

    p = VT100Parser(screen, 'big5uao')
    print(p.screen)
