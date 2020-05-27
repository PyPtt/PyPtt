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


def mail(
        api,
        ptt_id: str,
        title: str,
        content: str,
        sign_file) -> None:
    # log.showValue(
    #     api.config,
    #     log.level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    CmdList = []
    CmdList.append(command.GoMainMenu)
    CmdList.append('M')
    CmdList.append(command.Enter)
    CmdList.append('S')
    CmdList.append(command.Enter)
    CmdList.append(ptt_id)
    CmdList.append(command.Enter)

    Cmd = ''.join(CmdList)

    TargetList = [
        connect_core.TargetUnit(
            [
                i18n.Start,
                i18n.SendMail
            ],
            '主題：',
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.NoSuchUser,
            '【電子郵件】',
            exceptions_=exceptions.NoSuchUser(ptt_id)
        ),
    ]

    api.connect_core.send(
        Cmd,
        TargetList,
        screen_timeout=api.config.screen_long_timeout
    )

    CmdList = []
    CmdList.append(title)
    CmdList.append(command.Enter)
    CmdList.append(content)
    CmdList.append(command.Ctrl_X)

    Cmd = ''.join(CmdList)

    if sign_file == 0:
        SingFileSelection = i18n.NoSignatureFile
    else:
        SingFileSelection = i18n.Select + ' ' + \
                            str(sign_file) + 'th ' + i18n.SignatureFile

    TargetList = [
        connect_core.TargetUnit(
            i18n.AnyKeyContinue,
            '任意鍵',
            break_detect=True
        ),
        connect_core.TargetUnit(
            i18n.SaveFile,
            '確定要儲存檔案嗎',
            response='s' + command.Enter,
            # Refresh=False,
        ),
        connect_core.TargetUnit(
            i18n.SelfSaveDraft,
            '是否自存底稿',
            response='y' + command.Enter
        ),
        connect_core.TargetUnit(
            SingFileSelection,
            '選擇簽名檔',
            response=str(sign_file) + command.Enter
        ),
        connect_core.TargetUnit(
            SingFileSelection,
            'x=隨機',
            response=str(sign_file) + command.Enter
        ),
    ]

    api.connect_core.send(
        Cmd,
        TargetList,
        screen_timeout=api.config.screen_post_timeout
    )

    log.show_value(
        api.config,
        log.level.INFO,
        i18n.SendMail,
        i18n.Success
    )


def get_mail(api, index) -> data_type.MailInfo:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append(command.Ctrl_Z)
    cmd_list.append('m')
    cmd_list.append(str(index))
    cmd_list.append(command.Enter)
    # cmd_list.append(command.Enter)
    cmd = ''.join(cmd_list)

    fast_target = ''
    for i in range(0, 5):
        space = ' ' * i
        fast_target = f'{api.cursor}{space}{index}'

        if api.cursor == data_type.Cursor.NEW:
            if len(fast_target) == 6:
                break
        else:
            if len(fast_target) == 5:
                break

    target_list = [
        connect_core.TargetUnit(
            i18n.MailBox,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=log.level.DEBUG
        ),
        connect_core.TargetUnit(
            i18n.MailBox,
            fast_target,
            break_detect=True,
            log_level=log.level.DEBUG
        )
    ]

    api.connect_core.send(
        cmd,
        target_list,
    )
    # last_screen = api.connect_core.get_screen_queue()[-1]
    # print(last_screen)

    origin_mail, _ = _api_util.get_content(api, post_mode=False)
    # print(origin_mail)

    mail_author_pattern = re.compile('作者  (.+)')
    pattern_result = mail_author_pattern.search(origin_mail)
    mail_author = pattern_result.group(0)[2:].strip()
    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Author,
        mail_author
    )

    mail_title_pattern = re.compile('標題  (.+)')
    pattern_result = mail_title_pattern.search(origin_mail)
    mail_title = pattern_result.group(0)[2:].strip()
    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Title,
        mail_title
    )

    mail_date_pattern = re.compile('時間  (.+)')
    pattern_result = mail_date_pattern.search(origin_mail)
    mail_date = pattern_result.group(0)[2:].strip()
    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Date,
        mail_date
    )

    content_start = '───────────────────────────────────────'
    content_end = '--\n※ 發信站: 批踢踢實業坊(ptt.cc)'

    mail_content = origin_mail[
                   origin_mail.find(content_start) +
                   len(content_start) + 1:
                   ]

    red_envelope = False
    if content_end not in origin_mail and 'Ptt幣的大紅包喔' in origin_mail:
        mail_content = mail_content.strip()
        red_envelope = True
    else:

        mail_content = mail_content[
                       :mail_content.rfind(content_end) + 3
                       ]

    log.show_value(
        api.config,
        log.level.DEBUG,
        i18n.Content,
        mail_content
    )

    if red_envelope:
        mail_ip = None
        mail_location = None
    else:
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 111.242.182.114
        # ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: 59.104.127.126 (臺灣)

        ip_line = origin_mail.split('\n')
        ip_line = [x for x in ip_line if x.startswith(content_end[3:])][0]
        # print(ip_line)

        pattern = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
        result = pattern.search(ip_line)
        mail_ip = result.group(0)
        log.show_value(
            api.config,
            log.level.DEBUG,
            [
                i18n.MailBox,
                'IP',
            ],
            mail_ip
        )

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
                mail_location
            )

    mail_result = data_type.MailInfo(
        origin_mail=origin_mail,
        author=mail_author,
        title=mail_title,
        date=mail_date,
        content=mail_content,
        ip=mail_ip,
        location=mail_location,
        red_envelope=red_envelope)

    return mail_result


def del_mail(api, index) -> None:
    cmd_list = []
    cmd_list.append(command.GoMainMenu)
    cmd_list.append(command.Ctrl_Z)
    cmd_list.append('m')
    if index > 20:
        # speed up
        cmd_list.append(str(1))
        cmd_list.append(command.Enter)
    cmd_list.append(str(index))
    cmd_list.append(command.Enter)
    cmd_list.append('dy')
    cmd_list.append(command.Enter)

    # cmd_list.append(command.Enter)
    cmd = ''.join(cmd_list)

    target_list = [
        connect_core.TargetUnit(
            i18n.MailBox,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=log.level.DEBUG
        )
    ]

    api.connect_core.send(
        cmd,
        target_list,
    )

    api.connect_core.get_screen_queue()[-1]
