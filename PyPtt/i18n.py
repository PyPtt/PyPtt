import random

from PyPtt import __version__
from . import data_type

languageList = [
    data_type.Language.MANDARIN,
    data_type.Language.ENGLISH,
]


def specific_load(input_language, lang_list):
    global languageList

    if len(languageList) != len(lang_list):
        raise ValueError('SpecificLoad LangList length error')

    if input_language not in languageList:
        raise ValueError('SpecificLoad unknown language', input_language)
    return lang_list[languageList.index(input_language)]


def replace(string, *args):
    # for i in range(len(args)):
    for i, _ in enumerate(args):
        target = str(args[i])
        string = string.replace('{Target' + str(i) + '}', target)
    return string


mandarin_module: str = ''
english_module: str = ''
init: str = ''
connect_host: str = ''
set_connect_host: str = ''
PTT: str = ''
PTT2: str = ''
localhost: str = ''
must_be_a_string: str = ''
must_be_a_integer: str = ''
must_be_a_boolean: str = ''
must_be: str = ''
unknown: str = ''
must_bigger_than: str = ''
must_small_than: str = ''
must_between: str = ''
connect_core: str = ''
use_too_many_resources: str = ''
prepare_connect_again: str = ''
active: str = ''
connect_mode: str = ''
connect_mode_TELNET: str = ''
connect_mode_WEBSOCKET: str = ''
set_connect_mode: str = ''
fail: str = ''
connect: str = ''
hide_sensitive_info: str = ''
send_msg: str = ''
ptt_msg: str = ''
spend_time: str = ''
kick_other_login: str = ''
not_kick_other_login: str = ''
login_id: str = ''
mail_box: str = ''
login_success: str = ''
go_main_menu: str = ''
wrong_id_pw: str = ''
login_too_often: str = ''
system_busy_try_later: str = ''
del_wrong_pw_record: str = ''
post_not_finish: str = ''
in_login_process_please_wait: str = ''
any_key_continue: str = ''
update_sync_online_user_friend_list: str = ''
error_login_rich_people_go_main_menu: str = ''
skip_registration_form: str = ''
only_secure_connection: str = ''
debug: str = ''
info: str = ''
out_side: str = ''
new_cursor: str = ''
old_cursor: str = ''
logout_success: str = ''
logout: str = ''
complete: str = ''
query_ptt_time_success: str = ''
has_new_mail_goto_main_menu: str = ''
mail_box_full: str = ''
use_mailbox_api_will_logout_after_execution: str = ''
unregistered_user_cant_use_all_api: str = ''
picks_in_register: str = ''
reading_board_info: str = ''
no_permission: str = ''
no_post: str = ''
set_contact_mail_first: str = ''
no_such_board: str = ''
no_mail: str = ''
find_newest_index: str = ''
catch_post: str = ''
catch_post_success: str = ''
query_post_success: str = ''
success: str = ''
post_deleted: str = ''
board: str = ''
substandard_post: str = ''
author: str = ''
title: str = ''
date: str = ''
content: str = ''
comment_id: str = ''
comment_date: str = ''
comment: str = ''
comment_content: str = ''
unconfirmed_post: str = ''
browse_post: str = ''
done: str = ''
browse_post_done: str = ''
post_no_content: str = ''
animation_post: str = ''
login_fail: str = ''
no_fast_comment: str = ''
no_such_user: str = ''
user_offline: str = ''
no_money: str = ''
money_too_few: str = ''
connection_closed: str = ''
unregistered_user_cant_use_this_api: str = ''
multi_thread_operate: str = ''
error_pw: str = ''
ptt2_not_support: str = ''
no_comment: str = ''
no_response: str = ''
need_moderator_permission: str = ''
connect_fail: str = ''
no_such_post: str = ''
screen_no_match_target: str = ''
can_not_use_search_post_code_f: str = ''
user_has_previously_been_banned: str = ''
no_search_result: str = ''
timeout: str = ''
deleted_post: str = ''
has_post_permission: str = ''
save_file: str = ''
select_signature: str = ''
not_record_ip: str = ''
record_ip: str = ''
push_aligned: str = ''
not_push_aligned: str = ''
has_comment_permission: str = ''
only_arrow: str = ''
error_parameter: str = ''
wait_for_no_fast_comment: str = ''
require_login: str = ''
reading: str = ''
quit_user_profile: str = ''
read_complete: str = ''
get_user: str = ''
get_user_success: str = ''
get_user_fail: str = ''
water_ball: str = ''
set_call_status: str = ''
throw_waterball: str = ''
throw_waterball_success: str = ''
no_waterball: str = ''
browse_waterball: str = ''
browse_waterball_done: str = ''
get_call_status: str = ''
get_call_status_success: str = ''
set_call_status_success: str = ''
transaction_cancelled: str = ''
transaction: str = ''
transaction_success: str = ''
constant_red_bag: str = ''
verify_id: str = ''
anonymous_transaction: str = ''
input_money: str = ''
input_id: str = ''
authentication_has_not_expired: str = ''
trading_in_progress: str = ''
send_mail: str = ''
no_signature_file: str = ''
select_sign_file: str = ''
not_self_save_draft: str = ''
self_save_draft: str = ''
board_list: str = ''
reply_board: str = ''
reply_mail: str = ''
reply_board_mail: str = ''
forced_write: str = ''
edit_post: str = ''
use_the_original_title: str = ''
quote_original: str = ''
respond_success: str = ''
get_favourite_board_list: str = ''
confirm: str = ''
input_origin_password: str = ''
input_new_password: str = ''
check_new_password: str = ''
catch_bottom_post_success: str = ''
confirm_delete: str = ''
delete_success: str = ''
bucket_fail: str = ''
bucket_success: str = ''
input_bucket_days_reason: str = ''
new_settings_have_been_saved: str = ''
no_changes: str = ''
restore_connection: str = ''
new_version: str = ''
development_version: str = ''
current_version: str = ''
latest_version: str = ''
del_all_mark_post: str = ''
mark_success: str = ''
set_up_lang_module: str = ''
welcome: str = ''
goodbye: str = ''
update_remote_version: str = ''
retry: str = ''
change_pw: str = ''
post: str = ''
red_bag_no_edition: str = ''
edit_red_bag: str = ''
delete_post: str = ''
search_user: str = ''
get_mail: str = ''
no_such_mail: str = ''
reset_your_contact_email: str = ''

goodbye_en = [
    'goodbye',
    'bye',
    'see you',
    'catch you later',
    'I hate to run, but…',
    'Until we meet again, I will wait.',
]
goodbye_mandarin = [
    '再見',
    '掰',
    '待會見',
    '祝平安',
    '謝謝你，我很開心',
    '等你回來',
]


def load(lang):
    if not isinstance(lang, data_type.Language):
        raise ValueError('Unknown language', lang)

    global reset_your_contact_email
    reset_your_contact_email = specific_load(lang, [
        '請重新設定您的聯絡信箱',
        'Please reset your contact email'
    ])

    global no_such_mail
    no_such_mail = specific_load(lang, [
        '無此信件',
        'No such mail',
    ])

    global get_mail
    get_mail = specific_load(lang, [
        '取得信件',
        'Get mail',
    ])

    global search_user
    search_user = specific_load(lang, [
        '搜尋使用者',
        'Search user',
    ])

    global delete_post
    delete_post = specific_load(lang, [
        '刪除文章',
        'Delete post',
    ])

    global red_bag_no_edition
    red_bag_no_edition = specific_load(lang, [
        '不修改紅包袋',
        'Not editing the red bag',
    ])

    global edit_red_bag
    edit_red_bag = specific_load(lang, [
        '修改紅包袋',
        'Edits the red bag',
    ])

    global post
    post = specific_load(lang, [
        '發佈文章',
        'post article',
    ])

    global change_pw
    change_pw = specific_load(lang, [
        '變更密碼',
        'change password',
    ])

    global retry
    retry = specific_load(lang, [
        '重試',
        'retry',
    ])

    global update_remote_version
    update_remote_version = specific_load(lang, [
        '確認最新版本',
        'fetching latest version',
    ])

    global goodbye
    goodbye = specific_load(lang, [
        random.choice(goodbye_mandarin),
        random.choice(goodbye_en),
    ])

    global must_be
    must_be = specific_load(lang, [
        '必須為',
        'must be',
    ])

    global welcome
    welcome = specific_load(lang, [
        f'PyPtt v {__version__} 由 CodingMan 開發',
        f'PyPtt v {__version__} developed by CodingMan',
    ])

    global set_up_lang_module
    set_up_lang_module = specific_load(lang, [
        '設定語言模組',
        'set up language module',
    ])

    global mark_success
    mark_success = specific_load(lang, [
        '刪除所有標記文章',
        'Del All Mark PostField',
    ])

    global del_all_mark_post
    del_all_mark_post = specific_load(lang, [
        '刪除所有標記文章',
        'Del All Mark PostField',
    ])

    global current_version
    current_version = specific_load(lang, [
        '目前版本',
        'Current version',
    ])

    global latest_version
    latest_version = specific_load(lang, [
        '正在執行最新版本',
        'Running the latest version',
    ])

    global development_version
    development_version = specific_load(lang, [
        '正在執行開發版本',
        'Running development version',
    ])

    global new_version
    new_version = specific_load(lang, [
        '有新版本',
        'There is a new version',
    ])

    global restore_connection
    restore_connection = specific_load(lang, [
        '恢復連線',
        'restore Connection',
    ])

    global no_changes
    no_changes = specific_load(lang, [
        '未改變任何設定',
        'no changes have been made to any settings',
    ])

    global new_settings_have_been_saved
    new_settings_have_been_saved = specific_load(lang, [
        '已儲存新設定',
        'new settings have been saved',
    ])

    global input_bucket_days_reason
    input_bucket_days_reason = specific_load(lang, [
        '輸入水桶天數與理由',
        'input bucket days and reason',
    ])

    global bucket_success
    bucket_success = specific_load(lang, [
        '水桶成功',
        'bucket success',
    ])

    global bucket_fail
    bucket_fail = specific_load(lang, [
        '水桶失敗',
        'bucket fail',
    ])

    global confirm_delete
    confirm_delete = specific_load(lang, [
        '確定刪除',
        'confirm delete',
    ])

    global delete_success
    delete_success = specific_load(lang, [
        '刪除成功',
        'delete Success',
    ])

    global catch_bottom_post_success
    catch_bottom_post_success = specific_load(lang, [
        '取得置底文章成功',
        'catch bottom post success',
    ])

    global catch_post_success
    catch_post_success = specific_load(lang, [
        '取得文章成功',
        'get post success',
    ])

    global query_post_success
    query_post_success = specific_load(lang, [
        '查詢文章成功',
        'query post success',
    ])

    global input_origin_password
    input_origin_password = specific_load(lang, [
        '輸入原密碼',
        'input Origin Password',
    ])

    global input_new_password
    input_new_password = specific_load(lang, [
        '設定新密碼',
        'input new password',
    ])

    global check_new_password
    check_new_password = specific_load(lang, [
        '檢查新密碼',
        'check new password',
    ])

    global confirm
    confirm = specific_load(lang, [
        '確認',
        'confirm',
    ])

    global get_favourite_board_list
    get_favourite_board_list = specific_load(lang, [
        '取得我的最愛',
        'Query favourite board list',
    ])

    global respond_success
    respond_success = specific_load(lang, [
        '回應成功',
        'respond success',
    ])

    global use_the_original_title
    use_the_original_title = specific_load(lang, [
        '採用原標題',
        'use the original title',
    ])

    global quote_original
    quote_original = specific_load(lang, [
        '引用原文',
        'quote original',
    ])

    global edit_post
    edit_post = specific_load(lang, [
        '編輯文章',
        'edit post',
    ])

    global forced_write
    forced_write = specific_load(lang, [
        '強制寫入',
        'Forced Write',
    ])

    global reply_board
    reply_board = specific_load(lang, [
        '回應至看板',
        'respond to the BoardField',
    ])

    global reply_mail
    reply_mail = specific_load(lang, [
        '回應至作者信箱',
        'respond to the mailbox of author',
    ])

    global reply_board_mail
    reply_board_mail = specific_load(lang, [
        '回應至看板與作者信箱',
        'respond to the board and the mailbox of author',
    ])

    global board_list
    board_list = specific_load(lang, [
        '看板列表',
        'board list',
    ])

    global self_save_draft
    self_save_draft = specific_load(lang, [
        '自存底稿',
        'self-save draft',
    ])

    global not_self_save_draft
    not_self_save_draft = specific_load(lang, [
        '放棄自存底稿',
        'not self-save draft',
    ])

    global select_sign_file
    select_sign_file = specific_load(lang, [
        '選擇第 {Target0} 簽名檔',
        'select {Target0}th signature file',
    ])

    global no_signature_file
    no_signature_file = specific_load(lang, [
        '不加簽名檔',
        'no Signature File',
    ])

    global send_mail
    send_mail = specific_load(lang, [
        '寄信',
        'send mail',
    ])

    global trading_in_progress
    trading_in_progress = specific_load(lang, [
        '交易正在進行中',
        'trading is in progress',
    ])

    global authentication_has_not_expired
    authentication_has_not_expired = specific_load(lang, [
        '認證尚未過期',
        'authentication has not expired',
    ])

    global input_id
    input_id = specific_load(lang, [
        '輸入帳號',
        'input ID',
    ])

    global input_money
    input_money = specific_load(lang, [
        '輸入金額',
        'input money',
    ])

    global anonymous_transaction
    anonymous_transaction = specific_load(lang, [
        '不使用匿名交易',
        'transaction without anomalous',
    ])

    global verify_id
    verify_id = specific_load(lang, [
        '確認身分',
        'verify ID',
    ])

    global constant_red_bag
    constant_red_bag = specific_load(lang, [
        '不修改紅包袋',
        'constant the red bag',
    ])

    global transaction_success
    transaction_success = specific_load(lang, [
        '交易成功',
        'transaction success',
    ])

    global transaction
    transaction = specific_load(lang, [
        '交易',
        'transaction',
    ])

    global transaction_cancelled
    transaction_cancelled = specific_load(lang, [
        '交易取消!',
        'the transaction is cancelled!',
    ])

    global set_call_status_success
    set_call_status_success = specific_load(lang, [
        '設定呼叫器狀態成功',
        'set BBCall status success',
    ])

    global get_call_status
    get_call_status = specific_load(lang, [
        '取得呼叫器狀態',
        'get BBCall status',
    ])

    global get_call_status_success
    get_call_status_success = specific_load(lang, [
        '取得呼叫器狀態成功',
        'get BBCall status success',
    ])

    global browse_waterball
    browse_waterball = specific_load(lang, [
        '瀏覽水球紀錄',
        'browse waterball',
    ])

    global browse_waterball_done
    browse_waterball_done = specific_load(lang, [
        '瀏覽水球紀錄完成',
        'browse waterball complete',
    ])

    global no_waterball
    no_waterball = specific_load(lang, [
        '無訊息記錄',
        'no waterball',
    ])

    global throw_waterball_success
    throw_waterball_success = specific_load(lang, [
        '丟水球成功',
        'throw waterball success',
    ])

    global throw_waterball
    throw_waterball = specific_load(lang, [
        '丟 {Target0} 水球',
        'throw {Target0} waterball',
    ])

    global set_call_status
    set_call_status = specific_load(lang, [
        '設定呼叫器狀態',
        'set call status',
    ])

    global water_ball
    water_ball = specific_load(lang, [
        '水球',
        'water Ball',
    ])

    global get_user
    get_user = specific_load(lang, [
        '取得使用者',
        'get user',
    ])

    global get_user_success
    get_user_success = specific_load(lang, [
        '取得使用者成功',
        'get user success',
    ])

    global get_user_fail
    get_user_fail = specific_load(lang, [
        '取得使用者失敗',
        'get user fail',
    ])

    global read_complete
    read_complete = specific_load(lang, [
        f'讀取完成',
        f'read complete',
    ])

    global quit_user_profile
    quit_user_profile = specific_load(lang, [
        f'退出使用者檔案',
        f'Quit UserField Profile',
    ])

    global reading
    reading = specific_load(lang, [
        '讀取中',
        'reading',
    ])

    global require_login
    require_login = specific_load(lang, [
        '請先登入',
        'please login first',
    ])

    global error_parameter
    error_parameter = specific_load(lang, [
        '參數錯誤',
        'wrong parameter',
    ])

    global only_arrow
    only_arrow = specific_load(lang, [
        '使用加註方式',
        'Arrow Only in Push',
    ])

    global has_comment_permission
    has_comment_permission = specific_load(lang, [
        '確認擁有推文權限',
        'user has permission to comment',
    ])

    global push_aligned
    push_aligned = specific_load(lang, [
        '推文對齊',
        'Push aligned',
    ])

    global not_push_aligned
    not_push_aligned = specific_load(lang, [
        '無推文對齊',
        'No push aligned',
    ])

    global not_record_ip
    not_record_ip = specific_load(lang, [
        '不紀錄 IP',
        'not record IP',
    ])

    global record_ip
    record_ip = specific_load(lang, [
        '紀錄 IP',
        'Record ip',
    ])

    global select_signature
    select_signature = specific_load(lang, [
        '選擇簽名檔',
        'Select Signature',
    ])

    global save_file
    save_file = specific_load(lang, [
        '儲存檔案',
        'Save File',
    ])

    global has_post_permission
    has_post_permission = specific_load(lang, [
        '確認擁有貼文權限',
        'have permission to post',
    ])

    global deleted_post
    deleted_post = specific_load(lang, [
        '已刪除文章',
        'Deleted PostField',
    ])

    global timeout
    timeout = specific_load(lang, [
        '等待過久',
        'timeout',
    ])

    global no_search_result
    no_search_result = specific_load(lang, [
        '沒有搜尋結果',
        'No Search Result',
    ])

    global user_has_previously_been_banned
    user_has_previously_been_banned = specific_load(lang, [
        '使用者之前已被禁言',
        'user has previously been banned',
    ])

    global can_not_use_search_post_code_f
    can_not_use_search_post_code_f = specific_load(lang, [
        '此狀態下無法使用搜尋文章代碼(AID)功能',
        'This status can not use the search PostField code function',
    ])

    global screen_no_match_target
    screen_no_match_target = specific_load(lang, [
        '畫面無法辨識',
        'this screen is not recognized',
    ])

    global no_such_post
    no_such_post = specific_load(lang, [
        '{Target0} 板找不到這個文章代碼 {Target1}',
        'in {Target0}, the post code is not EXISTS {Target1}',
    ])

    global connect_fail
    connect_fail = specific_load(lang, [
        '連線失敗',
        'connect fail',
    ])

    global need_moderator_permission
    need_moderator_permission = specific_load(lang, [
        '需要板主權限',
        'need moderator permission',
    ])

    global no_response
    no_response = specific_load(lang, [
        '很抱歉, 此文章已結案並標記, 不得回應',
        'this post has been closed and marked, no response',
    ])

    global no_comment
    no_comment = specific_load(lang, [
        '禁止推薦',
        'no comment',
    ])

    global error_pw
    error_pw = specific_load(lang, [
        '密碼不正確',
        'wrong password',
    ])

    global multi_thread_operate
    multi_thread_operate = specific_load(lang, [
        '請勿使用多線程同時操作一個 PyPtt 物件',
        'do not use a multi-thread to operate a PyPtt object',
    ])

    global unregistered_user_cant_use_this_api
    unregistered_user_cant_use_this_api = specific_load(lang, [
        '未註冊使用者，無法使用此功能',
        'unregistered UserField Can\'t Use This API',
    ])

    global connection_closed
    connection_closed = specific_load(lang, [
        '連線已經被關閉',
        'connection Closed',
    ])

    global money_too_few
    money_too_few = specific_load(lang, [
        '金額過少，交易取消!',
        'the amount is too small, the transaction is cancelled!',
    ])

    global no_money
    no_money = specific_load(lang, [
        'PTT 幣不足',
        'not enough PTT coins',
    ])

    global user_offline
    user_offline = specific_load(lang, [
        '使用者離線',
        'user offline',
    ])

    global no_such_user
    no_such_user = specific_load(lang, [
        '無該使用者',
        'no such user',
    ])

    global no_fast_comment
    no_fast_comment = specific_load(lang, [
        '禁止快速連續推文',
        'no fast comment',
    ])

    global wait_for_no_fast_comment
    wait_for_no_fast_comment = specific_load(lang, [
        f'因{no_fast_comment}，所以等待五秒',
        f'because {no_fast_comment}, wait 5 sec',
    ])

    global login_fail
    login_fail = specific_load(lang, [
        '登入失敗',
        'login fail'
    ])

    global animation_post
    animation_post = specific_load(lang, [
        '動畫文章',
        'Animation PostField',
    ])

    global post_no_content
    post_no_content = specific_load(lang, [
        '此文章無內容',
        'post has no content',
    ])

    global done
    done = specific_load(lang, [
        '完成',
        'done',
    ])

    global browse_post
    browse_post = specific_load(lang, [
        '瀏覽文章',
        'browse post',
    ])

    global browse_post_done
    browse_post_done = specific_load(lang, [
        f'{browse_post}{done}',
        f'{browse_post} {done}',
    ])

    global unconfirmed_post
    unconfirmed_post = specific_load(lang, [
        '待證實文章',
        'PostField To Be Confirmed',
    ])

    global comment
    comment = specific_load(lang, [
        '推文',
        'comment',
    ])

    global comment_date
    comment_date = specific_load(lang, [
        '推文日期',
        'comment date',
    ])

    global comment_id
    comment_id = specific_load(lang, [
        '推文帳號',
        'comment id',
    ])

    global content
    content = specific_load(lang, [
        '內文',
        'content',
    ])

    global comment_content
    comment_content = specific_load(lang, [
        f'{comment}{content}',
        f'{comment} {content}',
    ])

    global date
    date = specific_load(lang, [
        '日期',
        'date',
    ])

    global title
    title = specific_load(lang, [
        '標題',
        'title',
    ])

    global author
    author = specific_load(lang, [
        '作者',
        'author',
    ])

    global substandard_post
    substandard_post = specific_load(lang, [
        '不合規範文章',
        'substandard post',
    ])

    global board
    board = specific_load(lang, [
        '看板',
        'board',
    ])

    global post_deleted
    post_deleted = specific_load(lang, [
        '文章已經被刪除',
        'post has been deleted',
    ])

    global success
    success = specific_load(lang, [
        '成功',
        'success',
    ])

    global catch_post
    catch_post = specific_load(lang, [
        '取得文章',
        'catch post',
    ])

    global find_newest_index
    find_newest_index = specific_load(lang, [
        '找到最新編號',
        'find newest index',
    ])

    global no_mail
    no_mail = specific_load(lang, [
        f'沒有信件',
        f'you have no mail',
    ])

    global no_such_board
    no_such_board = specific_load(lang, [
        '無該看板',
        'no such board',
    ])

    global no_post
    no_post = specific_load(lang, [
        '沒有文章',
        'no post',
    ])

    global set_contact_mail_first
    set_contact_mail_first = specific_load(lang, [
        '請先設定聯絡信箱後才能修改密碼',
        'password can only be changed after setting the contact mailbox',
    ])

    global no_permission
    no_permission = specific_load(lang, [
        '使用者沒有權限',
        'user Has No Permission',
    ])

    global reading_board_info
    reading_board_info = specific_load(lang, [
        '讀取看板資訊',
        'reading board Info',
    ])

    global picks_in_register
    picks_in_register = specific_load(lang, [
        '註冊申請單處理順位',
        'registration application processing order',
    ])

    global unregistered_user_cant_use_all_api
    unregistered_user_cant_use_all_api = specific_load(lang, [
        '未註冊使用者，將無法使用全部功能',
        'unregistered UserField Can\'t Use All API',
    ])

    global use_mailbox_api_will_logout_after_execution
    use_mailbox_api_will_logout_after_execution = specific_load(lang, [
        f'如果使用信箱相關功能，將執行後自動登出',
        f'if you use mailbox related functions, you will be logged out automatically after execution',
    ])

    global mail_box_full
    mail_box_full = specific_load(lang, [
        '郵件已滿',
        'mail box is full',
    ])

    global has_new_mail_goto_main_menu
    has_new_mail_goto_main_menu = specific_load(lang, [
        '有新信，回到主選單',
        'new mail! Back to main menu',
    ])

    global query_ptt_time_success
    query_ptt_time_success = specific_load(lang, [
        '取得批踢踢時間成功',
        'query ptt time success',
    ])

    global complete
    complete = specific_load(lang, [
        '完成',
        'complete',
    ])

    global logout
    logout = specific_load(lang, [
        '登出',
        'logout',
    ])

    global logout_success
    logout_success = specific_load(lang, [
        '登出成功',
        'logout success',
    ])

    global new_cursor
    new_cursor = specific_load(lang, [
        '新式游標',
        'new cursor',
    ])

    global old_cursor
    old_cursor = specific_load(lang, [
        '舊式游標',
        'old cursor',
    ])

    global debug
    debug = specific_load(lang, [
        '除錯',
        'dbug',
    ])

    global info
    info = specific_load(lang, [
        '資訊',
        'info',
    ])

    global out_side
    out_side = specific_load(lang, [
        '外部',
        'out',
    ])

    global only_secure_connection
    only_secure_connection = specific_load(lang, [
        '跳過填寫註冊單',
        'skip registration form',
    ])

    global skip_registration_form
    skip_registration_form = specific_load(lang, [
        '跳過填寫註冊單',
        'skip registration form',
    ])

    global error_login_rich_people_go_main_menu
    error_login_rich_people_go_main_menu = specific_load(lang, [
        '錯誤登入到大富翁排行榜，回到主選單',
        'error login rich people, go main menu',
    ])

    global update_sync_online_user_friend_list
    update_sync_online_user_friend_list = specific_load(lang, [
        '正在更新與同步線上使用者及好友名單',
        'update sync online user friend list',
    ])

    global any_key_continue
    any_key_continue = specific_load(lang, [
        '任意鍵繼續',
        'any key to continue',
    ])

    global in_login_process_please_wait
    in_login_process_please_wait = specific_load(lang, [
        '登入中，請稍候',
        'in login process, please wait',
    ])

    global post_not_finish
    post_not_finish = specific_load(lang, [
        '文章尚未完成',
        'post is not finish',
    ])

    global del_wrong_pw_record
    del_wrong_pw_record = specific_load(lang, [
        '刪除錯誤密碼嘗試紀錄',
        'delete error password record',
    ])

    global system_busy_try_later
    system_busy_try_later = specific_load(lang, [
        '系統繁忙，請稍後再試',
        'system busy, try later',
    ])

    global login_too_often
    login_too_often = specific_load(lang, [
        '登入太頻繁',
        'login too often',
    ])

    global wrong_id_pw
    wrong_id_pw = specific_load(lang, [
        '帳號密碼錯誤',
        'wrong id or pw',
    ])

    global go_main_menu
    go_main_menu = specific_load(lang, [
        '回到主選單',
        'go to main menu',
    ])

    global login_success
    login_success = specific_load(lang, [
        '登入成功',
        'login success',
    ])

    global mail_box
    mail_box = specific_load(lang, [
        '郵件信箱',
        'mail box',
    ])

    global login_id
    login_id = specific_load(lang, [
        '登入帳號',
        'login id',
    ])

    global not_kick_other_login
    not_kick_other_login = specific_load(lang, [
        '不剔除其他登入',
        'not kick other login',
    ])

    global kick_other_login
    kick_other_login = specific_load(lang, [
        '強制執行剔除其他登入',
        'kick other login',
    ])

    global spend_time
    spend_time = specific_load(lang, [
        '花費時間',
        'spend time',
    ])

    global ptt_msg
    ptt_msg = specific_load(lang, [
        '批踢踢訊息',
        'ptt msg',
    ])

    global send_msg
    send_msg = specific_load(lang, [
        '送出訊息',
        'send msg',
    ])

    global hide_sensitive_info
    hide_sensitive_info = specific_load(lang, [
        '隱藏敏感資訊',
        'hide sensitive info'])

    global connect
    connect = specific_load(lang, [
        '連線',
        'connect'])

    global fail
    fail = specific_load(lang, [
        '失敗',
        'fail'])

    global connect_mode_WEBSOCKET
    connect_mode_WEBSOCKET = specific_load(lang, [
        'WebSocket',
        'WebSocket'])

    global connect_mode_TELNET
    connect_mode_TELNET = specific_load(lang, [
        'Telnet',
        'Telnet'])

    global connect_mode
    connect_mode = specific_load(lang, [
        '連線模式',
        'the connect mode'])

    global set_connect_mode
    set_connect_mode = specific_load(lang, [
        '設定連線模式',
        'set up the connect mode'])

    global active
    active = specific_load(lang, [
        '啟動',
        'active'])

    global prepare_connect_again
    prepare_connect_again = specific_load(lang, [
        '準備再次連線',
        'prepare connect again'])

    global use_too_many_resources
    use_too_many_resources = specific_load(lang, [
        '耗用過多資源',
        'use too many resources'])

    global connect_core
    connect_core = specific_load(lang, [
        '連線核心',
        'connect core'])

    global must_small_than
    must_small_than = specific_load(lang, [
        '必須小於',
        'must smaller than'])

    global must_between
    must_between = specific_load(lang, [
        '必須介於',
        'must between'])

    global must_bigger_than
    must_bigger_than = specific_load(lang, [
        '必須大於',
        'must bigger than'])

    global unknown
    unknown = specific_load(lang, [
        '不明的',
        'unknown'])

    global must_be_a_boolean
    must_be_a_boolean = specific_load(lang, [
        '必須為布林值',
        'must be a boolean'])

    global must_be_a_integer
    must_be_a_integer = specific_load(lang, [
        '必須為數字',
        'must be a integer'])

    global must_be_a_string
    must_be_a_string = specific_load(lang, [
        '必須為字串',
        'must be a string'])

    global mandarin_module
    mandarin_module = specific_load(lang, [
        '繁體中文',
        'mandarin'])

    global english_module
    english_module = specific_load(lang, [
        '英文',
        'english'])

    global init
    init = specific_load(lang, [
        '初始化',
        'init'])

    global connect_host
    connect_host = specific_load(lang, [
        '連線主機',
        'the connect host'])

    global set_connect_host
    set_connect_host = specific_load(lang, [
        '設定連線主機',
        'set up the connect host'])

    global PTT
    PTT = specific_load(lang, [
        '批踢踢',
        'PTT'])

    global PTT2
    PTT2 = specific_load(lang, [
        '批踢踢兔',
        'PTT2'])

    global localhost
    localhost = specific_load(lang, [
        '本機',
        'localhost'])

    global ptt2_not_support
    ptt2_not_support = specific_load(lang, [
        f'{PTT2}不支援此功能',
        f'{PTT2} not support this api',
    ])

    ##############################################

    # No changes have been made to any settings

    # Quote original

    # global List
    # List = []

    # for k, v in globals().items():
    #     # System Var
    #     if k.startswith('_'):
    #         continue

    #     print(f'k {k}')
    #     print(f'v {v}')
    #     if isinstance(k, str) and isinstance(v, str):
    #         List.append(k)


def _createlist():
    i18nStrList = []

    for k, v in globals().items():
        # System Var
        if k.startswith('_'):
            continue
        if isinstance(k, str) and isinstance(v, str):
            i18nStrList.append(k)

    with open('i18n.txt', 'w') as F:
        F.write('\n'.join(i18nStrList))
