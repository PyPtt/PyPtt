from . import _api_util
from . import check_value
from . import command
from . import connect_core
from . import exceptions
from . import i18n
from . import lib_util


def search_user(api, ptt_id: str, min_page: int, max_page: int) -> list:
    _api_util.one_thread(api)

    if not api._is_login:
        raise exceptions.RequireLogin(i18n.require_login)

    if not api.is_registered_user:
        raise exceptions.UnregisteredUser(lib_util.get_current_func_name())

    check_value.check_type(ptt_id, str, 'ptt_id')
    if min_page is not None:
        check_value.check_index('min_page', min_page)
    if max_page is not None:
        check_value.check_index('max_page', max_page)
    if min_page is not None and max_page is not None:
        check_value.check_index_range('min_page', min_page, 'max_page', max_page)

    cmd_list = []
    cmd_list.append(command.go_main_menu)
    cmd_list.append('T')
    cmd_list.append(command.enter)
    cmd_list.append('Q')
    cmd_list.append(command.enter)
    cmd_list.append(ptt_id)
    cmd = ''.join(cmd_list)

    if min_page is not None:
        template = min_page
    else:
        template = 1

    appendstr = ' ' * template
    cmdtemp = cmd + appendstr

    target_list = [
        connect_core.TargetUnit('任意鍵', break_detect=True)]

    resultlist = []

    api.logger.info(i18n.search_user)

    while True:

        api.connect_core.send(
            cmdtemp,
            target_list)
        ori_screen = api.connect_core.get_screen_queue()[-1]
        # print(OriScreen)
        # print(len(OriScreen.split('\n')))

        if len(ori_screen.split('\n')) == 2:
            result_id = ori_screen.split('\n')[1]
            result_id = result_id[result_id.find(' ') + 1:].strip()
            # print(result_id)

            resultlist.append(result_id)
            break
        else:

            ori_screen = ori_screen.split('\n')[3:-1]
            ori_screen = '\n'.join(ori_screen)

            templist = ori_screen.replace('\n', ' ')

            while '  ' in templist:
                templist = templist.replace('  ', ' ')

            templist = templist.split(' ')
            resultlist.extend(templist)

            # print(templist)
            # print(len(templist))

            if len(templist) != 100 and len(templist) != 120:
                break

            template += 1
            if max_page is not None:
                if template > max_page:
                    break

            cmdtemp = ' '

    api.connect_core.send(
        command.enter,
        [
            # 《ＩＤ暱稱》
            connect_core.TargetUnit('《ＩＤ暱稱》', response=command.enter),
            connect_core.TargetUnit('查詢網友', break_detect=True)
        ]
    )
    api.logger.info(i18n.success)

    return list(filter(None, resultlist))
