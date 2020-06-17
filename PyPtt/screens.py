import re
import sys

try:
    from . import lib_util
    from . import log
except ModuleNotFoundError:
    import lib_util
    import log


class Target(object):
    MainMenu = [
        '離開，再見…',
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

    UseTooManyResources = [
        '程式耗用過多計算資源'
    ]

    Animation = [
        '★ 這份文件是可播放的文字動畫，要開始播放嗎？'
    ]

    CursorToGoodbye = MainMenu.copy()


def show(config, screen_queue, function_name=None):
    if config.log_level != log.level.TRACE:
        return

    if isinstance(screen_queue, list):
        for Screen in screen_queue:
            print('-' * 50)
            try:
                print(Screen.encode(
                    sys.stdin.encoding, "replace").decode(
                    sys.stdin.encoding
                )
                )
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
                #     log.level.INFO,
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
