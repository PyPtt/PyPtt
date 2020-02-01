import re
try:
    from . import i18n
    from . import ConnectCore
    from . import log
    from . import screens
    from . import Command
except ModuleNotFoundError:
    import i18n
    import ConnectCore
    import log
    import screens
    import Command


def has_new_mail(api) -> int:

    # log.showValue(
    #     api.config,
    #     log.Level.INFO,
    #     [
    #         i18n.PTT,
    #         i18n.Msg
    #     ],
    #     i18n.MarkPost
    # )

    cmd_list = []
    cmd_list.append(Command.GoMainMenu)
    cmd_list.append('M')
    cmd_list.append(Command.Enter)
    cmd_list.append('R')
    cmd_list.append(Command.Enter)
    cmd_list.append('1')
    cmd_list.append(Command.Enter)
    cmd_list.append('$')
    cmd = ''.join(cmd_list)

    target_list = [
        ConnectCore.TargetUnit(
            i18n.MailBox,
            screens.Target.InMailBox,
            break_detect=True,
            log_level=log.Level.DEBUG
        )
    ]

    api.connect_core.send(
        cmd,
        target_list,
        screen_timeout=api.config.screen_long_timeout
    )

    ori_screen = api.connect_core.get_screen_queue()[-1]

    pattern = re.findall('[\s]+[\d]+ (\+)[\s]+', ori_screen)
    return len(pattern)
