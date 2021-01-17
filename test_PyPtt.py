import os
import sys
import json
import traceback
import random
import time
from PyPtt import PTT


def log(msg, mode: str = 'at'):
    if not msg:
        return
    with open('test_result.txt', mode, encoding='utf-8') as f:
        f.write(msg + '\n')


def get_password(password_file):
    try:
        with open(password_file) as AccountFile:
            account = json.load(AccountFile)
            ptt_id = account['ID']
            password = account['Password']
    except FileNotFoundError:
        log(f'Please note PTT ID and Password in {password_file}')
        log('{"ID":"YourID", "Password":"YourPassword"}')
        sys.exit()

    return ptt_id, password


run_ci = None
automation_ci = None
ptt_id_0 = None
ptt_pw_0 = None
ptt2_id_0 = None
ptt2_pw_0 = None
ptt_id_1 = None
ptt_pw_1 = None
ptt2_id_1 = None
ptt2_pw_1 = None
current_py_version = None


def test_init():
    log('init', mode='w')

    log('===負向===')
    try:
        log('===語言 99===')
        PTT.API(language=99)
    except ValueError:
        log('通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False
    log('===語言放字串===')
    try:
        PTT.API(language='PTT.i18n.language.ENGLISH')
    except TypeError:
        log('通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        log('===亂塞 log_level===')
        PTT.API(log_level='log_level')
        log('沒通過')
        assert False
    except TypeError:
        log('通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        log('===亂塞 log_level===')
        PTT.API(log_level=100)
        log('沒通過')
        assert False
    except ValueError:
        log('通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        PTT.API(log_handler='test')
        assert False
    except TypeError:
        log('log_handler 字串測試通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        PTT.API(screen_time_out='test')
        assert False
    except TypeError:
        log('screen_time_out 字串測試通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        PTT.API(screen_long_time_out='test')
        assert False
    except TypeError:
        log('screen_long_time_out 字串測試通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        PTT.API(connect_mode='test')
        assert False
    except TypeError:
        log('host 字串測試通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False


    try:
        PTT.API(connect_mode=PTT.connect_core.connect_mode.TELNET)
        assert False
    except ValueError:
        log('TELNET 測試通過')
    except:
        log('沒通過: 跳出其他例外')
        assert False

    try:
        PTT.API(connect_mode=PTT.connect_core.connect_mode.WEBSOCKET)
        log('WEBSOCKET 測試通過')
    except ValueError:
        assert False
    except:
        log('沒通過: 跳出其他例外')
        assert False

    ################################################

    log('===正向===')
    log('===預設值===')
    PTT.API()
    log('===中文顯示===')
    PTT.API(language=PTT.i18n.language.CHINESE)
    log('===英文顯示===')
    PTT.API(language=PTT.i18n.language.ENGLISH)
    log('===log DEBUG===')
    PTT.API(log_level=PTT.log.level.DEBUG)
    log('===log INFO===')
    PTT.API(log_level=PTT.log.level.INFO)
    log('===log SLIENT===')
    PTT.API(log_level=PTT.log.level.SILENT)
    log('===log SLIENT======')
    PTT.API(host=PTT.data_type.host_type.LOCALHOST)

    ################################################
    def handler(msg):
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

    ptt_bot = PTT.API(log_handler=handler)
    ptt_bot.log('Test log')

    global run_ci
    global automation_ci
    global ptt_id_0
    global ptt_pw_0
    global ptt2_id_0
    global ptt2_pw_0
    global current_py_version

    global ptt_id_1
    global ptt_pw_1

    global ptt2_id_1
    global ptt2_pw_1

    run_ci = False
    automation_ci = False

    if '-ci' in sys.argv:
        run_ci = True

    load_from_file = False
    if run_ci:

        ptt_id_0 = os.getenv('PTT_ID_0')
        ptt_pw_0 = os.getenv('PTT_PW_0')

        ptt_id_1 = os.getenv('PTT_ID_1')
        ptt_pw_1 = os.getenv('PTT_PW_1')

        ptt2_id_0 = os.getenv('PTT2_ID_0')
        ptt2_pw_0 = os.getenv('PTT2_PW_0')

        ptt2_id_1 = os.getenv('PTT2_ID_1')
        ptt2_pw_1 = os.getenv('PTT2_PW_1')

        if ptt_id_0 is None or ptt_pw_0 is None:
            log('從環境變數取得帳號密碼失敗')
            load_from_file = True
            automation_ci = False
        else:
            automation_ci = True
    else:
        load_from_file = True

    if load_from_file:
        ptt_id_0, ptt_pw_0 = get_password('test_account_0.txt')
        ptt_id_1, ptt_pw_1 = get_password('test_account_1.txt')
        ptt2_id_0, ptt2_pw_0 = get_password('test_account_2.txt')
        ptt2_id_1, ptt2_pw_1 = get_password('test_account_3.txt')

    current_py_version = os.getenv('PYTHON_VERSION')
    if current_py_version is None:
        current_py_version = sys.version[:3]


def case(ptt_bot_0, ptt_bot_1):
    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        ptt_bot_0.log('開始測試 PTT1')

        current_id_0 = ptt_id_0
        current_pw_0 = ptt_pw_0
        current_id_1 = ptt_id_1
        current_pw_1 = ptt_pw_1
    else:
        ptt_bot_0.log('開始測試 PTT2')
        current_id_0 = ptt2_id_0
        current_pw_0 = ptt2_pw_0
        current_id_1 = ptt2_id_1
        current_pw_1 = ptt2_pw_1

    try:
        ptt_bot_0.login(current_id_0, current_pw_0[:-1])
        ptt_bot_0.log('登入反向測試失敗')
        assert False
    except PTT.exceptions.WrongIDorPassword:
        ptt_bot_0.log('登入反向測試成功')

    try:
        ptt_bot_0.login(current_id_1, current_pw_1)
        ptt_bot_0.log('id_1 登入測試成功')
        ptt_bot_0.logout()
    except:
        ptt_bot_0.log('id_1 登入測試失敗')
        assert False

    try:
        ptt_bot_0.login(current_id_0, current_pw_0)
        ptt_bot_0.log('id_0 登入測試成功')
    except:
        ptt_bot_0.log('id_0 登入測試失敗')
        assert False

    ################################################

    def show_test_result(board, IndexAID, result):
        if result:
            if isinstance(IndexAID, int):
                ptt_bot_0.log(f'{board} index {IndexAID} 測試通過')
            else:
                ptt_bot_0.log(f'{board} AID {IndexAID} 測試通過')
        else:
            if isinstance(IndexAID, int):
                ptt_bot_0.log(f'{board} index {IndexAID} 測試失敗')
            else:
                ptt_bot_0.log(f'{board} AID {IndexAID} 測試失敗')
                ptt_bot_0.logout()
                sys.exit(1)

    def get_post_test_func(board, index_aid, target_ex, check_format, check_string):

        ptt_bot_0.log(f'開始測試 {board} 板 文章{"編號" if isinstance(index_aid, int) else " aid"} {index_aid}')
        try:
            if isinstance(index_aid, int):
                post_info = ptt_bot_0.get_post(
                    board,
                    post_index=index_aid)
            else:
                post_info = ptt_bot_0.get_post(
                    board,
                    post_aid=index_aid)
        except Exception as e:
            if target_ex is not None and isinstance(e, target_ex):
                show_test_result(board, index_aid, True)
                return
            show_test_result(board, index_aid, False)

            traceback.log_tb(e.__traceback__)
            ptt_bot_0.log(e)
            ptt_bot_0.logout()
            assert False

        if check_string is None and target_ex is None and not check_format:
            ptt_bot_0.log(post_info.content)

        if check_format and not post_info.pass_format_check:
            show_test_result(board, index_aid, True)
            return

        if check_string is not None and check_string not in post_info.content:
            ptt_bot_0.logout()
            assert False

        log(post_info.content)

        ptt_bot_0.log(f'{board} 板 文章{"編號" if isinstance(index_aid, int) else " aid"} {index_aid} 測試通過')

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        test_post_list = [
            ('Python', 1, None, False, '總算可以來想想板的走向了..XD'),
            ('NotExitBoard', 1, PTT.exceptions.NoSuchBoard, False, None),
            ('Python', '1TJH_XY0', None, False, '大家嗨，我是 CodingMan'),
            # 文章格式錯誤
            ('Steam', 4444, None, True, None),
            # 文章格式錯誤
            ('movie', 457, None, True, None),
            ('Gossiping', '1TU65Wi_', None, False, None),
            ('joke', '1Tc6G9eQ', None, False, None),
            # 待證文章
            ('Test', '1U3pLzi0', None, False, None)]
    else:
        test_post_list = [
            # 2001 年的文章
            ('WhoAmI', 1, None, True, None),
            ('CodingMan', 1, None, True, None)]

    for b, i, exception_, check_format, check_string in test_post_list:
        get_post_test_func(b, i, exception_, check_format, check_string)

    ptt_bot_0.log('取得文章基準測試全部通過')

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Wanted',
            'Gossiping',
            'Test',
            'Stock',
            'movie']
    else:
        test_board_list = [
            'WhoAmI',
            'CodingMan',
            'Test']

    for test_board in test_board_list:
        basic_index = 0
        for _ in range(50):
            index = ptt_bot_0.get_newest_index(
                PTT.data_type.index_type.BBS,
                board=test_board)

            if basic_index == 0:
                ptt_bot_0.log(f'{test_board} 最新文章編號 {index}')
                basic_index = index
            elif abs(basic_index - index) > 5:
                ptt_bot_0.log(f'{test_board} 最新文章編號 {index}')
                ptt_bot_0.log(f'basic_index {basic_index}')
                ptt_bot_0.log(f'Index {index}')
                ptt_bot_0.log('取得看板最新文章編號測試失敗')
                ptt_bot_0.logout()

                assert False
    ptt_bot_0.log('取得看板最新文章編號測試全部通過')

    title = 'PyPtt 程式貼文基準測試標題'
    content = f'''
此為 PyPtt v {ptt_bot_0.get_version()} CI 測試流程
詳細請參考 https://github.com/PttCodingMan/PyPtt

此次測試使用 python {current_py_version}
以下為基準測試內文

PyPtt 程式貼文基準測試內文

この日本のベンチマーク
'''
    if automation_ci:
        content = '''
此次測試由 Github Actions 啟動
''' + content
    else:
        content = f'''
此次測試由 {current_id_0} 啟動
''' + content
    content = content.replace('\n', '\r\n')

    basic_board = 'Test'
    # 貼出基準文章
    ptt_bot_0.post(
        basic_board,
        title,
        content,
        1,
        0)

    # 取得 Test 最新文章編號
    index = ptt_bot_0.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=basic_board)

    # 搜尋基準文章
    basic_post_aid = None
    basic_post_index = 0
    for i in range(5):

        post_info = ptt_bot_0.get_post(
            basic_board,
            post_index=index - i)

        if current_id_0 in post_info.author and 'PyPtt 程式貼文基準測試內文' in post_info.content and \
                title in post_info.title:
            ptt_bot_0.log('使用文章編號取得基準文章成功')
            post_info = ptt_bot_0.get_post(
                basic_board,
                post_aid=post_info.aid)
            if current_id_0 in post_info.author and 'PyPtt 程式貼文基準測試內文' in post_info.content and \
                    title in post_info.title:
                ptt_bot_0.log('使用文章代碼取得基準文章成功')
                basic_post_aid = post_info.aid
                basic_post_index = index - i
                break

    if basic_post_aid is None:
        ptt_bot_0.log('取得基準文章失敗')
        ptt_bot_0.logout()
        assert False

    ptt_bot_0.log('取得基準文章成功')
    ptt_bot_0.log('貼文測試全部通過')

    ################################################

    try:
        content1 = '編號推文基準文字123'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.PUSH,
                       content1, post_aid='QQQQQQQ')
        ptt_bot_0.log('推文反向測試失敗')
        ptt_bot_0.logout()
        assert False
    except PTT.exceptions.NoSuchPost:
        ptt_bot_0.log('推文反向測試通過')

    try:
        index = ptt_bot_0.get_newest_index(
            PTT.data_type.index_type.BBS,
            board=basic_board)
        content1 = '編號推文基準文字123'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.PUSH,
                       content1, post_index=index + 100)
        ptt_bot_0.log('推文反向測試失敗')
        ptt_bot_0.logout()
        assert False
    except ValueError:
        ptt_bot_0.log('推文反向測試通過')

    test_push_list = [
        ('編號推文基準文字123', basic_post_index),
        ('代碼推文基準文字123', basic_post_aid),
        ('安安', basic_post_aid),
        ('QQ', basic_post_aid)]

    for push_content, post_index_aid in test_push_list:
        if isinstance(post_index_aid, int):
            ptt_bot_0.push(basic_board, PTT.data_type.push_type.PUSH,
                           push_content, post_index=basic_post_index)
        else:
            ptt_bot_0.push(basic_board, PTT.data_type.push_type.PUSH,
                           push_content, post_aid=basic_post_aid)

    post_info = ptt_bot_0.get_post(
        basic_board,
        post_aid=basic_post_aid)

    push_success_count = 0
    for push in post_info.push_list:

        search_list = [True for content, _ in test_push_list if push.content == content]
        if len(search_list) == 1:
            push_success_count += 1

    if push_success_count != len(test_push_list):
        ptt_bot_0.log('推文基準測試失敗')
        ptt_bot_0.logout()
        assert False

    ptt_bot_0.log('代碼推文基準測試成功')

    content = '===推文基準測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    def show_condition(test_board, search_type, condition):
        if search_type == PTT.data_type.post_search_type.KEYWORD:
            type_str = '關鍵字'
        if search_type == PTT.data_type.post_search_type.AUTHOR:
            type_str = '作者'
        if search_type == PTT.data_type.post_search_type.PUSH:
            type_str = '推文數'
        if search_type == PTT.data_type.post_search_type.MARK:
            type_str = '標記'
        if search_type == PTT.data_type.post_search_type.MONEY:
            type_str = '稿酬'

        ptt_bot_0.log(f'{test_board} 使用 {type_str} 搜尋 {condition}')

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        test_list = [
            ('Python', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
            ('ALLPOST', PTT.data_type.post_search_type.KEYWORD, '(Wanted)'),
            ('Wanted', PTT.data_type.post_search_type.KEYWORD, '(本文已被刪除)'),
            ('ALLPOST', PTT.data_type.post_search_type.KEYWORD, '(Gossiping)'),
            ('Gossiping', PTT.data_type.post_search_type.KEYWORD, '普悠瑪'),
        ]
    else:
        test_list = [
            ('WhoAmI', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
            ('Test', PTT.data_type.post_search_type.KEYWORD, '[公告]'),
        ]

    test_range = 1
    query_mode = False

    for (test_board, search_type, condition) in test_list:
        show_condition(test_board, search_type, condition)
        index = ptt_bot_0.get_newest_index(
            PTT.data_type.index_type.BBS,
            test_board,
            search_type=search_type,
            search_condition=condition)
        ptt_bot_0.log(f'{test_board} 最新文章編號 {index}')

        for i in range(test_range):
            post_info = ptt_bot_0.get_post(
                test_board,
                post_index=index - i,
                search_type=search_type,
                search_condition=condition,
                query=query_mode)

            ptt_bot_0.log(f'列表日期: [{post_info.list_date}]')
            ptt_bot_0.log(f'作者: [{post_info.author}]')
            ptt_bot_0.log(f'標題: [{post_info.title}]')

            if post_info.delete_status == PTT.data_type.post_delete_status.NOT_DELETED:
                if not query_mode:
                    ptt_bot_0.log('內文:')
                    ptt_bot_0.log(post_info.content)
            elif post_info.delete_status == PTT.data_type.post_delete_status.AUTHOR:
                ptt_bot_0.log('文章被作者刪除')
            elif post_info.delete_status == PTT.data_type.post_delete_status.MODERATOR:
                ptt_bot_0.log('文章被版主刪除')
            ptt_bot_0.log('=' * 20)

        content = f'{test_board} 取得文章測試完成'
        ptt_bot_0.push('Test', PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)

    content = '===取得文章測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    def crawl_handler(post):

        def detect_none(Name, Obj, Enable=True):
            if Obj is None and Enable:
                raise ValueError(Name + ' is None')

        if post.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
            if post.delete_status == PTT.data_type.post_delete_status.MODERATOR:
                # print(f'[版主刪除][{post.getAuthor()}]')
                pass
            elif post.delete_status == PTT.data_type.post_delete_status.AUTHOR:
                # print(f'[作者刪除][{post.getAuthor()}]')
                pass
            elif post.delete_status == PTT.data_type.post_delete_status.UNKNOWN:
                # print(f'[不明刪除]')
                pass
            return

        # if post.getTitle().startswith('Fw:') or post.getTitle().startswith('轉'):
        # print(f'[{post.aid}][{post.getAuthor()}][{post.getTitle()}]')
        # print(f'[{post.getContent()}]')

        # print(f'[{post.getAuthor()}][{post.getTitle()}]')

        push_number = post.push_number
        if push_number is not None:
            if push_number == '爆':
                pass
            elif push_number.startswith('X'):
                N = push_number[1:]
            else:
                pass
                # if not push_number.isdigit():
                #     print(f'[{post.aid}][{post.push_number}]')
                #     print(f'[{post.aid}][{post.push_number}]')
                #     print(f'[{post.aid}][{post.push_number}]')
                #     raise ValueError()
            # print(f'[{post.aid}][{post.getPushNumber()}]')

        detect_none('標題', post.title)
        # detect_none('AID', post.aid)
        detect_none('Author', post.author)
        # detect_none('Money', post.getMoney())

        # detect_none('WebUrl', post.web_url)
        # detect_none('ListDate', post.getListDate())

        # if not Query:
        # detect_none('Date', post.getDate())
        # detect_none('Content', post.getContent())
        # detect_none('IP', post.getIP())

        # time.sleep(0.2)

    query_mode = False

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Wanted',
            'joke',
            'Gossiping',
            'C_Chat']
    else:
        test_board_list = [
            'Test']

    # 改成 5 篇，不然 100 篇太耗時間了
    test_range = 5
    for test_board in test_board_list:
        newest_index = ptt_bot_0.get_newest_index(
            PTT.data_type.index_type.BBS,
            board=test_board
        ) - 10000
        # 到很久之前的文章去才不會撞到被刪掉的文章

        error_post_list, del_post_list = ptt_bot_0.crawl_board(
            PTT.data_type.crawl_type.BBS,
            crawl_handler,
            test_board,
            start_index=newest_index - test_range + 1,
            end_index=newest_index,
            query=query_mode)

        start_post = None
        offset = 0
        while True:
            start_post = ptt_bot_0.get_post(
                test_board,
                post_index=newest_index - test_range + 1 - offset)
            offset += 1
            if start_post is None:
                continue
            if start_post.aid is None:
                continue
            break

        end_post = None
        offset = 0
        while True:
            end_post = ptt_bot_0.get_post(
                test_board,
                post_index=newest_index + offset)
            offset += 1
            if end_post is None:
                continue
            if end_post.aid is None:
                continue
            break

        ptt_bot_0.log(test_board)
        ptt_bot_0.log(f'start_post index {newest_index - test_range + 1}')
        ptt_bot_0.log(f'EndPost index {newest_index}')

        error_post_list, del_post_list = ptt_bot_0.crawl_board(
            PTT.data_type.crawl_type.BBS,
            crawl_handler,
            test_board,
            start_aid=start_post.aid,
            end_aid=end_post.aid)
        content = f'{test_board} 爬板測試完成'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)

    content = '===爬板測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    user = ptt_bot_0.get_user(current_id_0)
    if user is None:
        ptt_bot_0.log('取得使用者測試失敗')
        ptt_bot_0.logout()
        assert False

    try:
        user = ptt_bot_0.get_user('sdjfklsdj')
        ptt_bot_0.log('取得使用者反向測試失敗')
        ptt_bot_0.logout()
        assert False
    except PTT.exceptions.NoSuchUser:
        ptt_bot_0.log('取得使用者反向測試通過')

    content = '===取得使用者測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    new_mail1 = ptt_bot_0.has_new_mail()
    ptt_bot_0.log(f'有 {new_mail1} 封新信')
    content = '取得幾封新信測試通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    mail_title = '程式寄信標題'

    try:
        ptt_bot_0.mail(
            'sdjfkdsjfls',
            mail_title,
            '反向測試信件內容',
            0,
            backup=False)

        content = '寄信反向測試失敗'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)
        ptt_bot_0.logout()
        assert False

    except PTT.exceptions.NoSuchUser:
        content = '寄信反向測試成功'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)

    content = '''如有誤寄，對..對不起
PyPtt 程式寄信測試內容
'''
    content = content.replace('\n', '\r\n')
    ptt_bot_0.mail(
        current_id_0,
        mail_title,
        content,
        0,
        backup=False)

    new_mail2 = ptt_bot_0.has_new_mail()
    ptt_bot_0.log(f'有 {new_mail2} 封新信')
    if new_mail2 > new_mail1:
        content = '寄信測試通過'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)
    else:
        ptt_bot_0.logout()
        assert False

    content = '===寄信測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    board_list = ptt_bot_0.get_board_list()
    ptt_bot_0.log(f'總共有 {len(board_list)} 個板名')
    ptt_bot_0.log(f'總共有 {len(set(board_list))} 個不重複板名')

    content = '===取得全站看板清單測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    ptt_time = ptt_bot_0.get_time()

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        content = f'PTT1 主機時間 {ptt_time}'
    else:
        content = f'PTT2 主機時間 {ptt_time}'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    content = '===取得主機時間測試全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    try:
        ptt_bot_0.get_board_info('NotExistBoard')

        ptt_bot_0.log('取得看板資訊反向測試失敗')

        ptt_bot_0.logout()
        assert False
    except PTT.exceptions.NoSuchBoard:
        ptt_bot_0.log('取得看板資訊反向測試成功')
        content = '取得看板資訊反向測試成功'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Wanted',
            'Gossiping',
            'Test',
            'Stock',
            'movie']
    else:
        test_board_list = [
            'WhoAmI',
            'CodingMan',
            'Test']

    for board in test_board_list:
        board_info = ptt_bot_0.get_board_info(board, get_post_kind=True)

        ptt_bot_0.log('發文類別: ', ' '.join(board_info.post_kind))

        ptt_bot_0.log('板名: ', board_info.board)
        ptt_bot_0.log('線上人數: ', board_info.online_user)
        # setting
        ptt_bot_0.log('中文敘述: ', board_info.chinese_des)
        ptt_bot_0.log('板主: ', board_info.moderators)
        ptt_bot_0.log('公開狀態(是否隱形): ', board_info.is_open)
        ptt_bot_0.log('隱板時是否可進入十大排行榜: ', board_info.is_into_top_ten_when_hide)
        ptt_bot_0.log('是否開放非看板會員發文: ', board_info.can_non_board_members_post)
        ptt_bot_0.log('是否開放回應文章: ', board_info.can_reply_post)
        ptt_bot_0.log('是否開放自刪文章: ', board_info.can_self_del_post)
        ptt_bot_0.log('是否開放推薦文章: ', board_info.can_push_post)
        ptt_bot_0.log('是否開放噓文: ', board_info.can_boo_post)
        ptt_bot_0.log('是否可以快速連推文章: ', board_info.can_fast_push)
        ptt_bot_0.log('推文最低間隔時間: ', board_info.min_interval)
        ptt_bot_0.log('推文時是否記錄來源 IP: ', board_info.is_push_record_ip)
        ptt_bot_0.log('推文時是否對齊開頭: ', board_info.is_push_aligned)
        ptt_bot_0.log('板主是否可刪除部份違規文字: ', board_info.can_moderator_del_illegal_content)
        ptt_bot_0.log('轉錄文章是否自動記錄，且是否需要發文權限: ',
                      board_info.is_tran_post_auto_recorded_and_require_post_permissions)
        ptt_bot_0.log('是否為冷靜模式: ', board_info.is_cool_mode)
        ptt_bot_0.log('是否需要滿十八歲才可進入: ', board_info.is_require18)
        ptt_bot_0.log('發文與推文限制登入次數需多少次以上: ', board_info.require_login_time)
        ptt_bot_0.log('發文與推文限制退文篇數多少篇以下: ', board_info.require_illegal_post)
        ptt_bot_0.log('=' * 20)

    content = '===取得看板資訊全部通過'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    favourite_board_list = ptt_bot_0.get_favourite_board()
    for test_board in favourite_board_list:
        if test_board.board is None or test_board.type is None or test_board.title is None:
            ptt_bot_0.log('取得我的最愛測試失敗')
            ptt_bot_0.logout()
            assert False

    content = '===取得我的最愛測試成功'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    user_list = ptt_bot_0.search_user('coding')
    if len(user_list) == 0:
        ptt_bot_0.log('查詢網友測試失敗')
        ptt_bot_0.logout()
        assert False

    content = '===查詢網友測試成功'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    ptt_bot_0.change_pw(current_pw_0)
    ptt_bot_0.change_pw(current_pw_0)

    content = '===變更密碼測試成功'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:

        url_list = [
            'https://www.ptt.cc/bbs/Gossiping/M.1583473330.A.61B.html',
            'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'
        ]

        check_result = True
        for url in url_list:
            board, aid = ptt_bot_0.get_aid_from_url(url)

            if not url.startswith(f'https://www.ptt.cc/bbs/{board}/'):
                check_result = False
                break

            post_info = ptt_bot_0.get_post(board, post_aid=aid, query=True)
            if post_info.aid != aid:
                check_result = False
                break

        if not check_result:
            ptt_bot_0.log('get_aid_from_url 失敗')
            ptt_bot_0.logout()
            assert False
        else:
            content = '=== get_aid_from_url 測試成功'
            ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                           content, post_aid=basic_post_aid)

    ################################################

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        test_board_list = [
            'Wanted',
            'Python',
            'Gossiping'
        ]
    else:
        test_board_list = [
            'CodingMan',
            'WhoamI',
            'WB_Newboard'
        ]

    for board in test_board_list:

        bottom_post_list = ptt_bot_0.get_bottom_post_list(board)

        if len(bottom_post_list) == 0:
            ptt_bot_0.log(f'{board} 板無置底文章')
        else:
            ptt_bot_0.log(f'{board} 共有 {len(bottom_post_list)} 置底文章')
            for post in bottom_post_list:
                ptt_bot_0.log(post.title)

    content = '===取得置底文章測試成功'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    content = '使用文章編號測試回應到板上'

    ptt_bot_0.reply_post(
        PTT.data_type.reply_type.BOARD,
        basic_board,
        content,
        post_index=basic_post_index)

    index = ptt_bot_0.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=basic_board)

    test_pass = False
    for i in range(5):

        post_info = ptt_bot_0.get_post(
            basic_board,
            post_index=index - i)

        if current_id_0 in post_info.author and content in post_info.content:
            test_pass = True
            content = f'{content}成功'
            ptt_bot_0.push(
                basic_board, PTT.data_type.push_type.ARROW,
                content, post_aid=basic_post_aid)
            break
    if not test_pass:
        ptt_bot_0.log(f'{content}失敗')
        ptt_bot_0.logout()
        assert False

    content = '使用 aid 測試回應到板上'

    ptt_bot_0.reply_post(
        PTT.data_type.reply_type.BOARD,
        basic_board,
        content,
        post_aid=basic_post_aid)

    index = ptt_bot_0.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=basic_board)

    test_pass = False
    for i in range(5):

        post_info = ptt_bot_0.get_post(
            basic_board,
            post_index=index - i)

        if current_id_0 in post_info.author and content in post_info.content:
            test_pass = True
            content = f'{content}成功'
            ptt_bot_0.push(
                basic_board, PTT.data_type.push_type.ARROW,
                content, post_aid=basic_post_aid)
            break
    if not test_pass:
        ptt_bot_0.log(f'{content}失敗')
        ptt_bot_0.logout()
        assert False

    content = '===回覆文章測試成功'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    def show_call_status(call_status):
        if call_status == PTT.data_type.call_status.ON:
            ptt_bot_0.log('呼叫器狀態[打開]')
        elif call_status == PTT.data_type.call_status.OFF:
            ptt_bot_0.log('呼叫器狀態[關閉]')
        elif call_status == PTT.data_type.call_status.UNPLUG:
            ptt_bot_0.log('呼叫器狀態[拔掉]')
        elif call_status == PTT.data_type.call_status.WATERPROOF:
            ptt_bot_0.log('呼叫器狀態[防水]')
        elif call_status == PTT.data_type.call_status.FRIEND:
            ptt_bot_0.log('呼叫器狀態[朋友]')
        else:
            ptt_bot_0.log(f'Unknown call_status: {call_status}')

    call_status = ptt_bot_0.get_call_status()
    show_call_status(call_status)

    test_queue = [x for x in range(
        PTT.data_type.call_status.min_value, PTT.data_type.call_status.max_value + 1
    )]
    random.shuffle(test_queue)
    test_queue.remove(call_status)

    test_pass = True
    for i in range(2):
        ptt_bot_0.set_call_status(test_queue[i])
        call_status = ptt_bot_0.get_call_status()
        show_call_status(call_status)

        if call_status != test_queue[i]:
            test_pass = False
            break

    if not test_pass:
        ptt_bot_0.log('設定呼叫器測試失敗')
        ptt_bot_0.logout()
        assert False
    else:
        content = '===設定呼叫器測試通過'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)

    ################################################

    ptt_bot_0.logout()
    ptt_bot_0.login(current_id_0, current_pw_0, kick_other_login=True)
    ptt_bot_1.login(current_id_1, current_pw_1, kick_other_login=True)

    operate_type = PTT.data_type.waterball_operate_type.CLEAR
    ptt_bot_0.get_waterball(operate_type)
    ptt_bot_1.get_waterball(operate_type)

    ptt_bot_0.set_call_status(PTT.data_type.call_status.OFF)
    ptt_bot_1.set_call_status(PTT.data_type.call_status.OFF)

    test_pass = False

    content = '水球測試基準訊息'

    counter = 0
    max_counter = 5
    while True:
        try:
            ptt_bot_1.throw_waterball(current_id_0, content)
            break
        except PTT.exceptions.UserOffline:
            if counter < max_counter:
                counter += 1
                ptt_bot_0.log('等待使用者狀態更新')
                time.sleep(2)
            else:
                raise PTT.exceptions.UserOffline

    waterball_list = ptt_bot_0.get_waterball(operate_type)
    for waterball_info in waterball_list:
        if not waterball_info.type == PTT.data_type.waterball_type.CATCH:
            continue

        receive_target = waterball_info.target
        receive_content = waterball_info.content

        ptt_bot_0.log(f'收到來自 {receive_target} 的水球 [{receive_content}]')

        if content == receive_content:
            test_pass = True
            break

    if not test_pass:
        ptt_bot_0.log('丟水球測試基準測試失敗')
        ptt_bot_0.logout()
        ptt_bot_1.logout()
        assert False

    content = '===水球測試基準測試成功'
    ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                   content, post_aid=basic_post_aid)

    ################################################

    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        content = '===PTT 1 測試全部通過'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)
    else:
        content = '===PTT 2 測試全部通過'
        ptt_bot_0.push(basic_board, PTT.data_type.push_type.ARROW,
                       content, post_aid=basic_post_aid)

    ################################################

    index = ptt_bot_0.get_newest_index(
        PTT.data_type.index_type.MAIL)
    # 往前搜尋 50 封刪除
    for i in range(50):
        current_index = index - i
        if current_index < 1:
            break

        mail_info = ptt_bot_0.get_mail(current_index)
        if mail_title != mail_info.title:
            continue

        ptt_bot_0.del_mail(current_index)
        ptt_bot_0.log(f'第 {current_index} 封測試信刪除成功')

    # mail_title

    ################################################

    index = ptt_bot_0.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=basic_board)
    # 往前搜尋 50 篇刪除
    for i in range(50):
        current_index = index - i
        try:
            ptt_bot_0.del_post(basic_board, post_index=current_index)
            ptt_bot_0.log(f'{basic_board} {current_index} 刪除成功')
        except PTT.exceptions.NoPermission:
            ptt_bot_0.log(f'{basic_board} {current_index} 無刪除權限')
        except PTT.exceptions.DeletedPost:
            ptt_bot_0.log(f'{basic_board} {current_index} 已經被刪除')
        except PTT.exceptions.NoSuchPost:
            ptt_bot_0.log(f'{basic_board} {current_index} 無此文章')

    ################################################

    title = 'PyPtt 程式自動化測試報告'
    content = f'''
此為 PyPtt v {ptt_bot_0.get_version()} CI 測試流程
詳細請參考 https://github.com/PttCodingMan/PyPtt

此次測試使用 python {current_py_version}

結果:
    所有測試皆通過。
'''
    if automation_ci:
        content = '''
此次測試由 Github Actions 啟動
    ''' + content
    else:
        content = f'''
此次測試由 {current_id_0} 啟動
    ''' + content
    content = content.replace('\n', '\r\n')

    ptt_bot_0.post(
        basic_board,
        title,
        content,
        1,
        0)

    ################################################

    ptt_bot_0.logout()


def single_case(ptt_bot_0, ptt_bot_1):
    if ptt_bot_0.config.host == PTT.data_type.host_type.PTT1:
        ptt_bot_0.log('開始測試 PTT1')

        current_id_0 = ptt_id_0
        current_pw_0 = ptt_pw_0
        current_id_1 = ptt_id_1
        current_pw_1 = ptt_pw_1
    else:
        ptt_bot_0.log('開始測試 PTT2')
        current_id_0 = ptt2_id_0
        current_pw_0 = ptt2_pw_0
        current_id_1 = ptt2_id_1
        current_pw_1 = ptt2_pw_1

    try:
        ptt_bot_0.login(current_id_0, current_pw_0)
        ptt_bot_0.log('id_0 登入測試成功')
    except:
        ptt_bot_0.log('id_0 登入測試失敗')
        assert False
    pass

    #####################
    #####################

    ptt_bot_0.logout()


def run_on_ptt_1():
    ptt_bot_0 = PTT.API(
        host=PTT.data_type.host_type.PTT1,
        log_handler=log)

    ptt_bot_1 = PTT.API(
        host=PTT.data_type.host_type.PTT1,
        log_handler=log)
    case(ptt_bot_0, ptt_bot_1)
    # single_case(ptt_bot_0, ptt_bot_1)


def run_on_ptt_2():
    ptt_bot_0 = PTT.API(
        host=PTT.data_type.host_type.PTT2,
        log_handler=log)
    ptt_bot_1 = PTT.API(
        host=PTT.data_type.host_type.PTT2,
        log_handler=log)
    case(ptt_bot_0, ptt_bot_1)
    # single_case(ptt_bot_0, ptt_bot_1)


def test_PyPtt():
    run_on_ptt_1()
    run_on_ptt_2()


if __name__ == '__main__':
    test_init()
    test_PyPtt()
