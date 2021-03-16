import re

try:
    from . import data_type
    from . import i18n
    from . import connect_core
    from . import log
    from . import screens
    from . import exceptions
    from . import command
    from . import _api_util
except ModuleNotFoundError:
    import data_type
    import i18n
    import connect_core
    import log
    import screens
    import exceptions
    import command
    import _api_util


# 寄信
def mail(
        api,
        ptt_id: str,
        title: str,
        content: str,
        sign_file,
        backup: bool = True) -> None:
    cmd_list = list()
    # 回到主選單
    cmd_list.append(command.GoMainMenu)
    # 私人信件區
    cmd_list.append('M')
    cmd_list.append(command.Enter)
    # 站內寄信
    cmd_list.append('S')
    cmd_list.append(command.Enter)
    # 輸入 id
    cmd_list.append(ptt_id)
    cmd_list.append(command.Enter)

    cmd = ''.join(cmd_list)

    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            [
                i18n.Start,
                i18n.SendMail
            ],
            '主題：',
            break_detect=True),
        connect_core.TargetUnit(
            i18n.NoSuchUser,
            '【電子郵件】',
            exceptions_=exceptions.NoSuchUser(ptt_id))
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )

    cmd_list = list()
    # 輸入標題
    cmd_list.append(title)
    cmd_list.append(command.Enter)
    # 輸入內容
    cmd_list.append(content)
    # 儲存檔案
    cmd_list.append(command.Ctrl_X)

    cmd = ''.join(cmd_list)

    # 根據簽名檔調整顯示訊息
    if sign_file == 0:
        sing_file_selection = i18n.NoSignatureFile
    else:
        sing_file_selection = i18n.Select + ' ' + \
                              str(sign_file) + 'th ' + i18n.SignatureFile
    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '請按任意鍵繼續',
            break_detect_after_send=True,
            response=command.Enter),
        connect_core.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + command.Enter, ),
        connect_core.TargetUnit(
            i18n.SelfSaveDraft if backup else i18n.NotSelfSaveDraft,
            '是否自存底稿',
            response=('y' if backup else 'n') + command.Enter),
        connect_core.TargetUnit(
            sing_file_selection,
            '選擇簽名檔',
            response=str(sign_file) + command.Enter),
        connect_core.TargetUnit(
            sing_file_selection,
            'x=隨機',
            response=str(sign_file) + command.Enter),
    ]

    # 送出訊息
    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_post_timeout)

    log.show_value(
        api.config,
        log.level.INFO,
        i18n.SendMail,
        i18n.Success)


# --
# ※ 發信站: 批踢踢實業坊(ptt.cc)
# ◆ From: 220.142.14.95
content_start = '───────────────────────────────────────'
content_end = '--\n※ 發信站: 批踢踢實業坊(ptt.cc)'
content_ip_old = '◆ From: '

mail_author_pattern = re.compile('作者  (.+)')
mail_title_pattern = re.compile('標題  (.+)')
mail_date_pattern = re.compile('時間  (.+)')
ip_pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')


def get_mail(
        api,
        index,
        search_type: int = 0,
        search_condition: str = None,
        search_list: list = None) -> data_type.MailInfo:
    cmd_list = list()
    # 回到主選單
    cmd_list.append(command.GoMainMenu)
    # 進入信箱
    cmd_list.append(command.Ctrl_Z)
    cmd_list.append('m')

    # 處理條件整理出指令
    _cmd_list, normal_newest_index = _api_util.get_search_condition_cmd(
        api,
        data_type.index_type.MAIL,
        search_type,
        search_condition,
        search_list,
        None)
    cmd_list.extend(_cmd_list)

    # 前進至目標信件位置
    cmd_list.append(str(index))
    cmd_list.append(command.Enter)
    cmd = ''.join(cmd_list)

    # 有時候會沒有最底下一列，只好偵測游標是否出現
    if api.cursor == data_type.Cursor.NEW:
        space_length = 6 - len(api.cursor) - len(str(index))
    else:
        space_length = 5 - len(api.cursor) - len(str(index))
    fast_target = f"{api.cursor}{' ' * space_length}{index}"

    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.MailBox,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=log.level.DEBUG),
        connect_core.TargetUnit(
            i18n.MailBox,
            fast_target,
            break_detect=True,
            log_level=log.level.DEBUG)
    ]

    # 送出訊息
    api.connect_core.send(
        cmd,
        target_list)

    # 取得信件全文
    origin_mail, _ = _api_util.get_content(api, post_mode=False)

    # 使用表示式分析信件作者
    pattern_result = mail_author_pattern.search(origin_mail)
    if pattern_result is None:
        mail_author = None
    else:
        mail_author = pattern_result.group(0)[2:].strip()

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Author,
        mail_author)

    # 使用表示式分析信件標題
    pattern_result = mail_title_pattern.search(origin_mail)
    if pattern_result is None:
        mail_title = None
    else:
        mail_title = pattern_result.group(0)[2:].strip()

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Title,
        mail_title)

    # 使用表示式分析信件日期
    pattern_result = mail_date_pattern.search(origin_mail)
    if pattern_result is None:
        mail_date = None
    else:
        mail_date = pattern_result.group(0)[2:].strip()
    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Date,
        mail_date)

    # 從全文拿掉信件開頭作為信件內文
    mail_content = origin_mail[
                   origin_mail.find(content_start) +
                   len(content_start) + 1:]

    # 紅包偵測
    red_envelope = False
    if content_end not in origin_mail and 'Ptt幣的大紅包喔' in origin_mail:
        mail_content = mail_content.strip()
        red_envelope = True
    else:

        mail_content = mail_content[
                       :mail_content.rfind(content_end) + 3]

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Content,
        mail_content)

    if red_envelope:
        mail_ip = None
        mail_location = None
    else:
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 111.242.182.114
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 59.104.127.126 (臺灣)

        # 非紅包開始解析 ip 與 地區

        ip_line_list = origin_mail.split('\n')
        ip_line = [x for x in ip_line_list if x.startswith(content_end[3:])]

        if len(ip_line) == 0:
            # 沒 ip 就沒地區
            mail_ip = None
            mail_location = None
        else:
            ip_line = ip_line[0]

            result = ip_pattern.search(ip_line)
            if result is None:
                ip_line = [x for x in ip_line_list if x.startswith(content_ip_old)]

                if len(ip_line) == 0:
                    mail_ip = None
                else:
                    ip_line = ip_line[0]
                    result = ip_pattern.search(ip_line)
                    mail_ip = result.group(0)
            else:
                mail_ip = result.group(0)

            log.show_value(
                api.config,
                log.level.DEBUG,
                [
                    i18n.MailBox,
                    'IP',
                ],
                mail_ip)

            location = ip_line[ip_line.find(mail_ip) + len(mail_ip):].strip()
            if len(location) == 0:
                mail_location = None
            else:
                # print(location)
                mail_location = location[1:-1]

                log.show_value(
                    api.config,
                    log.level.DEBUG,
                    [
                        i18n.MailBox,
                        'location',
                    ],
                    mail_location)

    mail_result = data_type.MailInfo(
        origin_mail=origin_mail,
        author=mail_author,
        title=mail_title,
        date=mail_date,
        content=mail_content,
        ip=mail_ip,
        location=mail_location,
        is_red_envelope=red_envelope)

    return mail_result


def del_mail(api, index) -> None:
    cmd_list = list()
    # 進入主選單
    cmd_list.append(command.GoMainMenu)
    # 進入信箱
    cmd_list.append(command.Ctrl_Z)
    cmd_list.append('m')
    if index > 20:
        # speed up
        cmd_list.append(str(1))
        cmd_list.append(command.Enter)

    # 前進到目標信件位置
    cmd_list.append(str(index))
    cmd_list.append(command.Enter)
    # 刪除
    cmd_list.append('dy')
    cmd_list.append(command.Enter)
    cmd = ''.join(cmd_list)

    # 定義如何根據情況回覆訊息
    target_list = [
        connect_core.TargetUnit(
            i18n.MailBox,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=log.level.DEBUG)
    ]

    # 送出
    api.connect_core.send(
        cmd,
        target_list)
