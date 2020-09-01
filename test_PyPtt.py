import os
import sys
import json
import traceback
from PyPtt import PTT


def log(msg, mode: str = 'at'):
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
ptt_id = None
ptt_pw = None
ptt2_id = None
ptt2_pw = None
current_py_version = None


def test_init():
    log('init', mode='w')
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

    log('===負向===')
    try:
        log('===語言 99===')
        PTT.API(language=99)
    except ValueError:
        log('通過')
    except:
        log('沒通過')
        sys.exit(-1)
    log('===語言放字串===')
    try:
        PTT.API(language='PTT.i18n.language.ENGLISH')
    except TypeError:
        log('通過')
    except:
        log('沒通過')
        sys.exit(-1)

    def handler(msg):
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(msg + '\n')

    ptt_bot = PTT.API(log_handler=handler)
    ptt_bot.log('Test log')

    global run_ci
    global automation_ci
    global ptt_id
    global ptt_pw
    global ptt2_id
    global ptt2_pw
    global current_py_version

    run_ci = False
    automation_ci = False

    if '-ci' in sys.argv:
        run_ci = True

    if run_ci:

        ptt_id = os.getenv('PTT_ID_0')
        ptt_pw = os.getenv('PTT_PW_0')

        ptt2_id = os.getenv('PTT2_ID_0')
        ptt2_pw = os.getenv('PTT2_PW_0')

        if ptt_id is None or ptt_pw is None:
            log('從環境變數取得帳號密碼失敗')
            ptt_id, ptt_pw = get_password('test_account.txt')
            ptt2_id, ptt2_pw = get_password('test_account_2.txt')
            automation_ci = False
        else:
            automation_ci = True
    else:
        ptt_id, ptt_pw = get_password('test_account.txt')
        ptt2_id, ptt2_pw = get_password('test_account_2.txt')

    current_py_version = os.getenv('PYTHON_VERSION')
    if current_py_version is None:
        current_py_version = sys.version[:3]


def case(ptt_bot):
    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        ptt_bot.log('開始測試 PTT1')
        ptt_bot.login(ptt_id, ptt_pw)
        current_id = ptt_id
    else:
        ptt_bot.log('開始測試 PTT2')
        ptt_bot.login(ptt2_id, ptt2_pw)
        current_id = ptt2_id

    def show_test_result(board, IndexAID, result):
        if result:
            if isinstance(IndexAID, int):
                ptt_bot.log(f'{board} index {IndexAID} 測試通過')
            else:
                ptt_bot.log(f'{board} AID {IndexAID} 測試通過')
        else:
            if isinstance(IndexAID, int):
                ptt_bot.log(f'{board} index {IndexAID} 測試失敗')
            else:
                ptt_bot.log(f'{board} AID {IndexAID} 測試失敗')
                ptt_bot.logout()
                sys.exit(1)

    def get_post_test_func(board, index_aid, target_ex, check_format, check_string):

        ptt_bot.log(f'開始測試 {board} 板 文章{"編號" if isinstance(index_aid, int) else " aid"} {index_aid}')
        try:
            if isinstance(index_aid, int):
                post_info = ptt_bot.get_post(
                    board,
                    post_index=index_aid)
            else:
                post_info = ptt_bot.get_post(
                    board,
                    post_aid=index_aid)
        except Exception as e:
            if target_ex is not None and isinstance(e, target_ex):
                show_test_result(board, index_aid, True)
                return
            show_test_result(board, index_aid, False)

            traceback.ptt_bot.log_tb(e.__traceback__)
            ptt_bot.log(e)
            assert 'test fail'

        if check_string is None and target_ex is None and not check_format:
            ptt_bot.log(post_info.content)

        if check_format and not post_info.pass_format_check:
            show_test_result(board, index_aid, True)
            return

        if check_string is not None and check_string not in post_info.content:
            assert 'check_string not in post_info.content'

        log(post_info.content)

        ptt_bot.log(f'{board} 板 文章{"編號" if isinstance(index_aid, int) else " aid"} {index_aid} 測試通過')

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
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

    ptt_bot.log('取得文章基準測試全部通過')

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
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
            index = ptt_bot.get_newest_index(
                PTT.data_type.index_type.BBS,
                board=test_board)

            if basic_index == 0:
                ptt_bot.log(f'{test_board} 最新文章編號 {index}')
                basic_index = index
            elif abs(basic_index - index) > 5:
                ptt_bot.log(f'{test_board} 最新文章編號 {index}')
                ptt_bot.log(f'basic_index {basic_index}')
                ptt_bot.log(f'Index {index}')
                ptt_bot.log('取得看板最新文章編號測試失敗')
                ptt_bot.logout()

                assert False
    ptt_bot.log('取得看板最新文章編號測試全部通過')

    title = 'PyPtt 程式貼文基準測試標題'
    content = f'''
此為 PyPtt v {ptt_bot.get_version()} CI 測試流程
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
此次測試由 {current_id} 啟動
''' + content
    content = content.replace('\n', '\r\n')

    basic_board = 'Test'
    # 貼出基準文章
    ptt_bot.post(
        basic_board,
        title,
        content,
        1,
        0)

    # 取得 Test 最新文章編號
    index = ptt_bot.get_newest_index(
        PTT.data_type.index_type.BBS,
        board=basic_board)

    # 搜尋基準文章
    basic_post_aid = None
    basic_post_index = 0
    for i in range(5):

        post_info = ptt_bot.get_post(
            basic_board,
            post_index=index - i)

        if current_id in post_info.author and 'PyPtt 程式貼文基準測試內文' in post_info.content and \
                title in post_info.title:
            ptt_bot.log('使用文章編號取得基準文章成功')
            post_info = ptt_bot.get_post(
                basic_board,
                post_aid=post_info.aid)
            if current_id in post_info.author and 'PyPtt 程式貼文基準測試內文' in post_info.content and \
                    title in post_info.title:
                ptt_bot.log('使用文章代碼取得基準文章成功')
                basic_post_aid = post_info.aid
                basic_post_index = index - i
                break

    if basic_post_aid is None:
        ptt_bot.log('取得基準文章失敗')
        ptt_bot.logout()
        assert False

    ptt_bot.log('取得基準文章成功')
    ptt_bot.log('貼文測試全部通過')

    ################################################

    try:
        content1 = '編號推文基準文字123'
        ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                     content1, post_aid='QQQQQQQ')
        ptt_bot.log('推文反向測試失敗')
        ptt_bot.logout()
        assert False
    except PTT.exceptions.NoSuchPost:
        ptt_bot.log('推文反向測試通過')

    try:
        index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            board=basic_board)
        content1 = '編號推文基準文字123'
        ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                     content1, post_index=index + 100)
        ptt_bot.log('推文反向測試失敗')
        ptt_bot.logout()
        assert False
    except ValueError:
        ptt_bot.log('推文反向測試通過')

    test_push_list = [
        ('編號推文基準文字123', basic_post_index),
        ('代碼推文基準文字123', basic_post_aid),
        ('安安', basic_post_aid),
        ('QQ', basic_post_aid)]

    for push_content, post_index_aid in test_push_list:
        if isinstance(post_index_aid, int):
            ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                         push_content, post_index=basic_post_index)
        else:
            ptt_bot.push(basic_board, PTT.data_type.push_type.PUSH,
                         push_content, post_aid=basic_post_aid)

    post_info = ptt_bot.get_post(
        basic_board,
        post_aid=basic_post_aid)

    push_success_count = 0
    for push in post_info.push_list:

        search_list = [True for content, _ in test_push_list if push.content == content]
        if len(search_list) == 1:
            push_success_count += 1

    if push_success_count != len(test_push_list):
        ptt_bot.log('推文基準測試失敗')
        ptt_bot.logout()
        assert False

    ptt_bot.log('代碼推文基準測試成功')

    content = '===推文基準測試全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
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

        ptt_bot.log(f'{test_board} 使用 {type_str} 搜尋 {condition}')

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
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
        index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            test_board,
            search_type=search_type,
            search_condition=condition)
        ptt_bot.log(f'{test_board} 最新文章編號 {index}')

        for i in range(test_range):
            post_info = ptt_bot.get_post(
                test_board,
                post_index=index - i,
                search_type=search_type,
                search_condition=condition,
                query=query_mode)

            ptt_bot.log(f'列表日期: [{post_info.list_date}]')
            ptt_bot.log(f'作者: [{post_info.author}]')
            ptt_bot.log(f'標題: [{post_info.title}]')

            if post_info.delete_status == PTT.data_type.post_delete_status.NOT_DELETED:
                if not query_mode:
                    ptt_bot.log('內文:')
                    ptt_bot.log(post_info.content)
            elif post_info.delete_status == PTT.data_type.post_delete_status.AUTHOR:
                ptt_bot.log('文章被作者刪除')
            elif post_info.delete_status == PTT.data_type.post_delete_status.MODERATOR:
                ptt_bot.log('文章被版主刪除')
            ptt_bot.log('=' * 20)

        content = f'{test_board} 取得文章測試完成'
        ptt_bot.push('Test', PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)

    content = '===取得文章測試全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
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

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
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
        newest_index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            board=test_board
        ) - 10000
        # 到很久之前的文章去才不會撞到被刪掉的文章

        error_post_list, del_post_list = ptt_bot.crawl_board(
            PTT.data_type.crawl_type.BBS,
            crawl_handler,
            test_board,
            start_index=newest_index - test_range + 1,
            end_index=newest_index,
            query=query_mode)

        start_post = None
        offset = 0
        while True:
            start_post = ptt_bot.get_post(
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
            end_post = ptt_bot.get_post(
                test_board,
                post_index=newest_index + offset,
            )
            offset += 1
            if end_post is None:
                continue
            if end_post.aid is None:
                continue
            break

        ptt_bot.log(test_board)
        ptt_bot.log(f'start_post index {newest_index - test_range + 1}')
        ptt_bot.log(f'EndPost index {newest_index}')

        error_post_list, del_post_list = ptt_bot.crawl_board(
            PTT.data_type.crawl_type.BBS,
            crawl_handler,
            test_board,
            start_aid=start_post.aid,
            end_aid=end_post.aid)
        content = f'{test_board} 爬板測試完成'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)

    content = '===爬板測試全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    user = ptt_bot.get_user(current_id)
    if user is None:
        ptt_bot.log('取得使用者測試失敗')
        ptt_bot.logout()
        assert False

    try:
        user = ptt_bot.get_user('sdjfklsdj')
        ptt_bot.log('取得使用者反向測試失敗')
        ptt_bot.logout()
        assert False
    except PTT.exceptions.NoSuchUser:
        ptt_bot.log('取得使用者反向測試通過')

    content = '===取得使用者測試全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    new_mail1 = ptt_bot.has_new_mail()
    ptt_bot.log(f'有 {new_mail1} 封新信')
    content = '取得幾封新信測試通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    try:
        ptt_bot.mail(
            'sdjfkdsjfls',
            '程式寄信標題',
            '反向測試信件內容',
            0)

        content = '寄信反向測試失敗'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)
        ptt_bot.logout()
        assert False

    except PTT.exceptions.NoSuchUser:
        content = '寄信反向測試成功'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)

    content = '''如有誤寄，對..對不起
PyPtt 程式寄信測試內容
'''
    content = content.replace('\n', '\r\n')
    ptt_bot.mail(
        current_id,
        '程式寄信標題',
        content,
        0)

    new_mail2 = ptt_bot.has_new_mail()
    ptt_bot.log(f'有 {new_mail2} 封新信')
    if new_mail2 > new_mail1:
        content = '寄信測試通過'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)
    else:
        ptt_bot.logout()
        assert False

    content = '===寄信測試全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    board_list = ptt_bot.get_board_list()
    ptt_bot.log(f'總共有 {len(board_list)} 個板名')
    ptt_bot.log(f'總共有 {len(set(board_list))} 個不重複板名')

    content = '===取得全站看板清單測試全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    try:
        ptt_bot.get_board_info('NotExistBoard')

        ptt_bot.log('取得看板資訊反向測試失敗')

        ptt_bot.logout()
        assert False
    except PTT.exceptions.NoSuchBoard:
        ptt_bot.log('取得看板資訊反向測試成功')
        content = '取得看板資訊反向測試成功'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
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
        board_info = ptt_bot.get_board_info(board, get_post_kind=True)

        ptt_bot.log('發文類別: ', ' '.join(board_info.post_kind))

        ptt_bot.log('板名: ', board_info.board)
        ptt_bot.log('線上人數: ', board_info.online_user)
        # setting
        ptt_bot.log('中文敘述: ', board_info.chinese_des)
        ptt_bot.log('板主: ', board_info.moderators)
        ptt_bot.log('公開狀態(是否隱形): ', board_info.is_open)
        ptt_bot.log('隱板時是否可進入十大排行榜: ', board_info.is_into_top_ten_when_hide)
        ptt_bot.log('是否開放非看板會員發文: ', board_info.can_non_board_members_post)
        ptt_bot.log('是否開放回應文章: ', board_info.can_reply_post)
        ptt_bot.log('是否開放自刪文章: ', board_info.can_self_del_post)
        ptt_bot.log('是否開放推薦文章: ', board_info.can_push_post)
        ptt_bot.log('是否開放噓文: ', board_info.can_boo_post)
        ptt_bot.log('是否可以快速連推文章: ', board_info.can_fast_push)
        ptt_bot.log('推文最低間隔時間: ', board_info.min_interval)
        ptt_bot.log('推文時是否記錄來源 IP: ', board_info.is_push_record_ip)
        ptt_bot.log('推文時是否對齊開頭: ', board_info.is_push_aligned)
        ptt_bot.log('板主是否可刪除部份違規文字: ', board_info.can_moderator_del_illegal_content)
        ptt_bot.log('轉錄文章是否自動記錄，且是否需要發文權限: ',
                    board_info.is_tran_post_auto_recorded_and_require_post_permissions)
        ptt_bot.log('是否為冷靜模式: ', board_info.is_cool_mode)
        ptt_bot.log('是否需要滿十八歲才可進入: ', board_info.is_require18)
        ptt_bot.log('發文與推文限制登入次數需多少次以上: ', board_info.require_login_time)
        ptt_bot.log('發文與推文限制退文篇數多少篇以下: ', board_info.require_illegal_post)
        ptt_bot.log('=' * 20)

    content = '===取得看板資訊全部通過'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    favourite_board_list = ptt_bot.get_favourite_board()
    for test_board in favourite_board_list:
        if test_board.board is None or test_board.type is None or test_board.title is None:
            ptt_bot.log('取得我的最愛測試失敗')
            ptt_bot.logout()
            assert False

    content = '===取得我的最愛測試成功'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    user_list = ptt_bot.search_user('coding')
    if len(user_list) == 0:
        ptt_bot.log('查詢網友測試失敗')
        ptt_bot.logout()
        assert False
    content = '===查詢網友測試成功'
    ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                 content, post_aid=basic_post_aid)

    ################################################

    if ptt_bot.config.host == PTT.data_type.host_type.PTT1:
        content = '===PTT 1 測試全部通過'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)
    else:
        content = '===PTT 2 測試全部通過'
        ptt_bot.push(basic_board, PTT.data_type.push_type.ARROW,
                     content, post_aid=basic_post_aid)

    ptt_bot.logout()


def run_on_ptt_1():
    ptt_bot = PTT.API(
        host=PTT.data_type.host_type.PTT1,
        log_handler=log)
    case(ptt_bot)


def run_on_ptt_2():
    ptt_bot = PTT.API(
        host=PTT.data_type.host_type.PTT2,
        log_handler=log)
    case(ptt_bot)


def test_PyPtt():
    run_on_ptt_1()
    run_on_ptt_2()


test_init()
test_PyPtt()
