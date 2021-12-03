import re
import sys

from SingleLog.log import Logger
from uao import register_uao

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


logger = Logger('screen')

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
        while ' \x08' in data:
            data = re.sub(r' \x08', '', data)

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
                # logger.info('xy', xy_part, new_x, new_y)
                self._move(new_x, new_y)

                # print('->', data)
                data = data[len(xy_part):]
                # print('-->', data)

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


if __name__ == '__main__':
    # 看板警察
    screen = b'\x1b[H\x1b[2J\x1b[1;30m\xe3\x80\x90\xe6\x9d\xbf\xe4\xb8\xbb:catcatcatcat\xe3\x80\x91           Python \xe7\xa8\x8b\xe5\xbc\x8f\xe8\xaa\x9e\xe8\xa8\x80                  \xe7\x9c\x8b\xe6\x9d\xbf\xe3\x80\x8aPython\xe3\x80\x8b \r\n[  \x08\x08\xe2\x86\x90\x1b[2;4H]\xe9\x9b\xa2\xe9\x96\x8b [  \x08\x08\xe2\x86\x92\x1b[2;13H]\xe9\x96\xb1\xe8\xae\x80 [Ctrl-P]\xe7\x99\xbc\xe8\xa1\xa8\xe6\x96\x87\xe7\xab\xa0 [d]\xe5\x88\xaa\xe9\x99\xa4 [z]\xe7\xb2\xbe\xe8\x8f\xaf\xe5\x8d\x80 [i]\xe7\x9c\x8b\xe6\x9d\xbf\xe8\xb3\x87\xe8\xa8\x8a/\xe8\xa8\xad\xe5\xae\x9a [h]\xe8\xaa\xaa\xe6\x98\x8e   \r\n\n\x1b[0;1;37m>     1   112/09 ericsk         \x08\x08\xe2\x96\xa1\x1b[4;33H [\xe5\xbf\x83\xe5\xbe\x97] \xe7\xb5\x82\xe6\x96\xbc\xe9\x96\x8b\xe6\x9d\xbf\xe4\xba\x86                              \r\n  \x08\x08\x1b[m\xe2\x94\x8c\x1b[5;3H  \x08\x08\xe2\x94\x80\x1b[5;5H  \x08\x08\xe2\x94\x80\x1b[5;7H  \x08\x08\xe2\x94\x80\x1b[5;9H  \x08\x08\xe2\x94\x80\x1b[5;11H  \x08\x08\xe2\x94\x80\x1b[5;13H  \x08\x08\xe2\x94\x80\x1b[5;15H  \x08\x08\xe2\x94\x80\x1b[5;17H  \x08\x08\xe2\x94\x80\x1b[5;19H  \x08\x08\xe2\x94\x80\x1b[5;21H  \x08\x08\xe2\x94\x80\x1b[5;23H  \x08\x08\xe2\x94\x80\x1b[5;25H  \x08\x08\xe2\x94\x80\x1b[5;27H  \x08\x08\xe2\x94\x80\x1b[5;29H  \x08\x08\xe2\x94\x80\x1b[5;31H  \x08\x08\xe2\x94\x80\x1b[5;33H  \x08\x08\xe2\x94\x80\x1b[5;35H  \x08\x08\xe2\x94\x80\x1b[5;37H  \x08\x08\xe2\x94\x80\x1b[5;39H  \x08\x08\xe2\x94\x80\x1b[5;41H  \x08\x08\xe2\x94\x80\x1b[5;43H  \x08\x08\xe2\x94\x80\x1b[5;45H  \x08\x08\xe2\x94\x80\x1b[5;47H  \x08\x08\xe2\x94\x80\x1b[5;49H  \x08\x08\xe2\x94\x80\x1b[5;51H  \x08\x08\xe2\x94\x80\x1b[5;53H  \x08\x08\xe2\x94\x80\x1b[5;55H  \x08\x08\xe2\x94\x80\x1b[5;57H  \x08\x08\xe2\x94\x80\x1b[5;59H  \x08\x08\xe2\x94\x80\x1b[5;61H  \x08\x08\xe2\x94\x80\x1b[5;63H  \x08\x08\xe2\x94\x80\x1b[5;65H  \x08\x08\xe2\x94\x80\x1b[5;67H  \x08\x08\xe2\x94\x80\x1b[5;69H  \x08\x08\xe2\x94\x80\x1b[5;71H  \x08\x08\xe2\x94\x80\x1b[5;73H  \x08\x08\xe2\x94\x80\x1b[5;75H  \x08\x08\xe2\x94\x80\x1b[5;77H  \x08\x08\xe2\x94\x90\x1b[5;79H\r\n  \x08\x08\xe2\x94\x82\x1b[6;3H \xe6\x96\x87\xe7\xab\xa0\xe4\xbb\xa3\xe7\xa2\xbc(AID): \x1b[1;37m#13cPSYOX \x1b[m(Python) [ptt.cc] [\xe5\xbf\x83\xe5\xbe\x97] \xe7\xb5\x82\xe6\x96\xbc\xe9\x96\x8b\xe6\x9d\xbf\xe4\xba\x86\x1b[6;77H  \x08\x08\xe2\x94\x82\x1b[6;79H\r\n  \x08\x08\xe2\x94\x82\x1b[7;3H \xe6\x96\x87\xe7\xab\xa0\xe7\xb6\xb2\xe5\x9d\x80: \x1b[1;37mhttps://www.ptt.cc/bbs/Python/M.1134139170.A.621.html\x1b[7;77H  \x08\x08\x1b[m\xe2\x94\x82\x1b[7;79H\r\n  \x08\x08\xe2\x94\x82\x1b[8;3H \xe9\x80\x99\xe4\xb8\x80\xe7\xaf\x87\xe6\x96\x87\xe7\xab\xa0\xe5\x80\xbc 2 Ptt\xe5\xb9\xa3\x1b[8;77H  \x08\x08\xe2\x94\x82\x1b[8;79H\r\n  \x08\x08\xe2\x94\x94\x1b[9;3H  \x08\x08\xe2\x94\x80\x1b[9;5H  \x08\x08\xe2\x94\x80\x1b[9;7H  \x08\x08\xe2\x94\x80\x1b[9;9H  \x08\x08\xe2\x94\x80\x1b[9;11H  \x08\x08\xe2\x94\x80\x1b[9;13H  \x08\x08\xe2\x94\x80\x1b[9;15H  \x08\x08\xe2\x94\x80\x1b[9;17H  \x08\x08\xe2\x94\x80\x1b[9;19H  \x08\x08\xe2\x94\x80\x1b[9;21H  \x08\x08\xe2\x94\x80\x1b[9;23H  \x08\x08\xe2\x94\x80\x1b[9;25H  \x08\x08\xe2\x94\x80\x1b[9;27H  \x08\x08\xe2\x94\x80\x1b[9;29H  \x08\x08\xe2\x94\x80\x1b[9;31H  \x08\x08\xe2\x94\x80\x1b[9;33H  \x08\x08\xe2\x94\x80\x1b[9;35H  \x08\x08\xe2\x94\x80\x1b[9;37H  \x08\x08\xe2\x94\x80\x1b[9;39H  \x08\x08\xe2\x94\x80\x1b[9;41H  \x08\x08\xe2\x94\x80\x1b[9;43H  \x08\x08\xe2\x94\x80\x1b[9;45H  \x08\x08\xe2\x94\x80\x1b[9;47H  \x08\x08\xe2\x94\x80\x1b[9;49H  \x08\x08\xe2\x94\x80\x1b[9;51H  \x08\x08\xe2\x94\x80\x1b[9;53H  \x08\x08\xe2\x94\x80\x1b[9;55H  \x08\x08\xe2\x94\x80\x1b[9;57H  \x08\x08\xe2\x94\x80\x1b[9;59H  \x08\x08\xe2\x94\x80\x1b[9;61H  \x08\x08\xe2\x94\x80\x1b[9;63H  \x08\x08\xe2\x94\x80\x1b[9;65H  \x08\x08\xe2\x94\x80\x1b[9;67H  \x08\x08\xe2\x94\x80\x1b[9;69H  \x08\x08\xe2\x94\x80\x1b[9;71H  \x08\x08\xe2\x94\x80\x1b[9;73H  \x08\x08\xe2\x94\x80\x1b[9;75H  \x08\x08\xe2\x94\x80\x1b[9;77H  \x08\x08\xe2\x94\x98\x1b[9;79H\r\n\n\x1b[1;30m      8    12/10 Fenikso        \x08\x08\xe2\x96\xa1\x1b[11;33H \xe8\xb3\x80                                             \r\n      9    12/10 asf423         \x08\x08\xe2\x96\xa1\x1b[12;33H \xe8\xb3\x80\xe9\x96\x8b\xe7\x89\x88                                         \r\n     10    12/10 rofu           \x08\x08\xe2\x96\xa1\x1b[13;33H \xe8\xb3\x80\xe9\x96\x8b\xe7\x89\x88                                         \r\n     11    12/10'
    # screen = screen.decode('utf-8')
    # print(screen)

    p = VT100Parser(screen, 'utf-8')
    print(p.screen)

    print('─────────────────────────────────────'.encode('utf-8'))
