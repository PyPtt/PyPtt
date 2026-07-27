"""Regression test: `mail(backup=False)` / `reply_post(backup=False)` must
NOT leave a draft behind in the sender's own mailbox.

Bug recap: the '選擇簽名檔' / '請選擇簽名檔' prompt line isn't overwritten by
the following "已順利寄出，是否自存底稿" prompt (they print on different
lines), so on the next screen redraw the signature-file TargetUnit matched a
second time and sent an extra Enter -- which the backup prompt then consumed
as its default [Y]. That silently saved a draft regardless of what `backup=`
was set to. The fix is `max_match=1` on that TargetUnit (`_api_mail.py`,
`_api_reply_post.py`), which caps it to firing once per screen.

Core signal: the sender's own mailbox newest index (`get_newest_index`).
backup=False must leave it unchanged; backup=True must bump it by exactly 1
(the self-saved draft).

This must run against real PTT (PTT1), not the local imageptt container: the
local container doesn't reliably reproduce the signature-file prompt redraw,
so it has no discriminating power there. `ptt_bots[0]` / `ptt_bots[1]` are
NOT usable as sender/recipient here -- PTT1_ID and PTT2_ID are the same
account (CodingMan) on two different hosts (PTT1=批踢踢實業坊,
PTT2=批踢踢兔), not two distinct accounts. Mailing yourself would merge the
"received" signal with the "draft" signal and defeat the mailbox-index
assertion. The sender is `ptt_bots[0]` (CodingMan on PTT1); the recipient is
a second, genuinely distinct PTT1 account (DeepLearning, via the
`deep_learning_bot` fixture below).
"""
import os
import time
import warnings

import pytest

import PyPtt
from PyPtt import MailField, NewIndex, PostField, ReplyTo
from PyPtt import connect_core

MAIL_DELIVERY_WAIT = 3  # > TimedDict(timeout=2) on api._newest_index_data

DEEPLEARNING_ID = os.environ.get('DEEPLEARNING_ID')
DEEPLEARNING_PW = os.environ.get('DEEPLEARNING_PW')


@pytest.fixture(scope='module')
def deep_learning_bot():
    """A second, distinct PTT1 account (DeepLearning) to act as mail
    recipient / reply target author. Skips the whole module when the
    credentials aren't configured rather than failing with a KeyError."""
    if not DEEPLEARNING_ID or not DEEPLEARNING_PW:
        pytest.skip('DEEPLEARNING_ID / DEEPLEARNING_PW not set; skipping '
                    'real-PTT backup-effectiveness test')

    bot = PyPtt.API(host=PyPtt.HOST.PTT1)
    bot.login(ptt_id=DEEPLEARNING_ID, ptt_pw=DEEPLEARNING_PW, kick_other_session=True)
    yield bot
    try:
        bot.logout()
    except Exception:
        pass


def _mailbox_index(bot):
    return bot.get_newest_index(index_type=NewIndex.MAIL)


def _find_and_delete_mail(bot, title_fragment, search_back=5):
    """Best-effort cleanup: find a mail whose title contains
    `title_fragment` near the mailbox's newest entry and delete it. Never
    raises -- this is container hygiene, not part of the assertion."""
    try:
        newest = bot.get_newest_index(index_type=NewIndex.MAIL)
        for i in range(search_back):
            index = newest - i
            if index <= 0:
                continue
            mail_info = bot.get_mail(index)
            if title_fragment in (mail_info[MailField.title] or ''):
                bot.del_mail(index)
                return
    except Exception:
        pass


def test_mail_backup_false_leaves_mailbox_unchanged(ptt_bots, deep_learning_bot):
    bot1 = ptt_bots[0]
    title = f'PyPtt backup=False mail test {int(time.time())}'
    before = _mailbox_index(bot1)
    try:
        bot1.mail(ptt_id=deep_learning_bot.ptt_id, title=title,
                  content='backup=False regression test\n', sign_file=0, backup=False)
        time.sleep(MAIL_DELIVERY_WAIT)
        after = _mailbox_index(bot1)
        assert after == before, (
            f'mail(backup=False) saved a draft anyway: mailbox index {before} -> {after}'
        )
    finally:
        _find_and_delete_mail(bot1, title)
        _find_and_delete_mail(deep_learning_bot, title)


def test_mail_backup_true_saves_draft(ptt_bots, deep_learning_bot):
    bot1 = ptt_bots[0]
    title = f'PyPtt backup=True mail test {int(time.time())}'
    before = _mailbox_index(bot1)
    try:
        bot1.mail(ptt_id=deep_learning_bot.ptt_id, title=title,
                  content='backup=True regression test\n', sign_file=0, backup=True)
        time.sleep(MAIL_DELIVERY_WAIT)
        after = _mailbox_index(bot1)
        assert after == before + 1, (
            f'mail(backup=True) did not save a draft: mailbox index {before} -> {after}'
        )
    finally:
        _find_and_delete_mail(bot1, title)
        _find_and_delete_mail(deep_learning_bot, title)


def _find_and_delete_post(bot, title_fragment, board='Test', search_back=10):
    """Best-effort cleanup: find a post whose title contains
    `title_fragment` near the board's newest entry and delete it. Never
    raises -- this is container hygiene, not part of the assertion."""
    try:
        newest = bot.get_newest_index(index_type=NewIndex.BOARD, board=board)
        for i in range(search_back):
            index = newest - i
            if index <= 0:
                continue
            post = bot.get_post(board=board, index=index, query=True)
            if post and title_fragment in (post.get(PostField.title, '') or ''):
                bot.del_post(board=board, index=index)
                return
    except Exception:
        pass


def _post_reply_target(deep_learning_bot, bot1, board='Test'):
    """DeepLearning posts a fresh article on `board` so bot1 (CodingMan) can
    reply to it as mail. The author must not be bot1 -- replying to your own
    post as mail would land in your own mailbox and be indistinguishable
    from a backup draft. Returns the post's index (as seen by bot1).

    If the freshly posted article can't be located afterwards, the article
    has already gone out for real -- so this makes a best-effort attempt to
    delete it (by title match, scanning the board) before re-raising,
    instead of leaving an orphaned post on real PTT with no cleanup path."""
    # Millisecond resolution folded back into a 10-digit window -- same
    # width as the old int(time.time()) suffix. PTT's query-popup title
    # line truncates past a certain column width (confirmed empirically:
    # a full time.time_ns() suffix got silently cut, breaking the
    # endswith()/in matches below), so this must NOT grow the title.
    suffix = int(time.time() * 1000) % 10_000_000_000
    title = f'PyPtt backup reply target {suffix}'
    deep_learning_bot.post(board=board, title_index=1, title=title,
                           content='reply-target for backup regression test\n', sign_file=0)
    time.sleep(2)

    try:
        newest = bot1.get_newest_index(index_type=NewIndex.BOARD, board=board)
        for i in range(5):
            index = newest - i
            if index <= 0:
                continue
            post = bot1.get_post(board=board, index=index, query=True)
            if post and post.get(PostField.title, '').endswith(title):
                return title, index
        raise AssertionError(f'freshly posted reply target {title!r} not found on {board}')
    except Exception:
        _find_and_delete_post(deep_learning_bot, title, board=board)
        raise


def test_reply_post_backup_false_leaves_mailbox_unchanged(ptt_bots, deep_learning_bot):
    bot1 = ptt_bots[0]
    target_title, index = _post_reply_target(deep_learning_bot, bot1)
    try:
        before = _mailbox_index(bot1)
        bot1.reply_post(reply_to=ReplyTo.MAIL, board='Test',
                        content='backup=False reply regression test\n',
                        index=index, backup=False)
        time.sleep(MAIL_DELIVERY_WAIT)
        after = _mailbox_index(bot1)
        assert after == before, (
            f'reply_post(backup=False) saved a draft anyway: mailbox index {before} -> {after}'
        )
    finally:
        _find_and_delete_mail(bot1, target_title)
        _find_and_delete_mail(deep_learning_bot, target_title)
        try:
            deep_learning_bot.del_post(board='Test', index=index)
        except Exception:
            pass


def test_reply_post_backup_true_saves_draft(ptt_bots, deep_learning_bot):
    bot1 = ptt_bots[0]
    target_title, index = _post_reply_target(deep_learning_bot, bot1)
    try:
        before = _mailbox_index(bot1)
        bot1.reply_post(reply_to=ReplyTo.MAIL, board='Test',
                        content='backup=True reply regression test\n',
                        index=index, backup=True)
        time.sleep(MAIL_DELIVERY_WAIT)
        after = _mailbox_index(bot1)
        assert after == before + 1, (
            f'reply_post(backup=True) did not save a draft: mailbox index {before} -> {after}'
        )
    finally:
        _find_and_delete_mail(bot1, target_title)
        _find_and_delete_mail(deep_learning_bot, target_title)
        try:
            deep_learning_bot.del_post(board='Test', index=index)
        except Exception:
            pass


# --- Regression check: does max_match=1 break ReplyTo.BOARD / BOARD_MAIL? ---
#
# The `max_match=1` cap on the '請選擇簽名檔' TargetUnit
# (`_api_reply_post.py`) is shared by all three ReplyTo branches. It was only
# verified against ReplyTo.MAIL so far. ReplyTo.BOARD and ReplyTo.BOARD_MAIL
# are the branches that actually post to a board -- and posting is the flow
# that shows a REAL '請選擇簽名檔' prompt (unlike plain mail). BOARD_MAIL
# additionally sends mail on top of the board post, so it's the branch most
# likely to hit the prompt twice for genuinely different reasons rather than
# just a leftover-redraw. If max_match=1 swallowed a real second prompt, the
# screen would never see a matching TargetUnit and send() would silently
# time out (it returns -1; reply_post() does not check the return value or
# raise on it) instead of raising cleanly.
#
# These tests assert on real side effects (reply lands on the board, mail is
# delivered) rather than trusting a clean return from reply_post(), and they
# also directly trace how many times '請選擇簽名檔' is seen during send().

REPLY_APPEAR_WAIT = 2  # board listing propagation delay, mirrors _post_reply_target


@pytest.fixture
def sign_file_trace(monkeypatch):
    """Wrap TargetUnit.is_match so every round where the '請選擇簽名檔'
    TargetUnit is evaluated gets recorded: whether the string was actually
    present in that round's screen, and whether is_match returned True for
    it (i.e. wasn't suppressed by max_match=1). Returns the log list."""
    log = []
    original_is_match = connect_core.TargetUnit.is_match

    def traced_is_match(self, screen, cursor):
        matched = original_is_match(self, screen, cursor)
        if self.detect_target == '請選擇簽名檔':
            log.append({
                'present_in_screen': '請選擇簽名檔' in screen,
                'matched': matched,
            })
        return matched

    monkeypatch.setattr(connect_core.TargetUnit, 'is_match', traced_is_match)
    return log


def _find_reply_index(bot, target_title, board='Test', search_back=8):
    """Find the 'R: ...<target_title>' reply authored by `bot` near the top
    of `board`. Returns the index, or None if not found."""
    newest = bot.get_newest_index(index_type=NewIndex.BOARD, board=board)
    for i in range(search_back):
        index = newest - i
        if index <= 0:
            continue
        post = bot.get_post(board=board, index=index, query=True)
        if not post:
            continue
        title = post.get(PostField.title, '') or ''
        if not (title.startswith('R: ') and title.endswith(target_title)):
            continue
        author = (post.get(PostField.author, '') or '').split(' ')[0]
        if author.lower() == bot.ptt_id.lower():
            return index
    return None


def _assert_no_stalled_round(bot, elapsed, label):
    """A genuinely stuck screen round burns a full screen_long_timeout
    (default 10s) of dead time before send() gives up and returns -1. A
    healthy multi-round reply_post() exchange over the real network finishes
    well under that, so total elapsed creeping up to it is the signature of
    exactly the regression this test is hunting for."""
    timeout = bot.config.screen_long_timeout
    assert elapsed < timeout, (
        f'{label} took {elapsed:.1f}s (screen_long_timeout={timeout}s) -- '
        f'looks like a stalled screen round, not normal network latency'
    )


def test_reply_post_board_appears_on_board(ptt_bots, deep_learning_bot, sign_file_trace):
    bot1 = ptt_bots[0]
    target_title, target_index = _post_reply_target(deep_learning_bot, bot1)
    reply_index = None
    try:
        start = time.time()
        bot1.reply_post(reply_to=ReplyTo.BOARD, board='Test',
                        content='ReplyTo.BOARD regression test\n',
                        index=target_index, sign_file=0)
        elapsed = time.time() - start
        _assert_no_stalled_round(bot1, elapsed, 'reply_post(BOARD)')

        time.sleep(REPLY_APPEAR_WAIT)
        reply_index = _find_reply_index(bot1, target_title)
        assert reply_index is not None, (
            f'reply to {target_title!r} not found on Test board -- reply_post(BOARD) '
            f'silently did not complete'
        )
    finally:
        # Cleanup checks below only warn, never assert/raise: if the test
        # body above already failed, a cleanup hiccup here must not
        # overwrite that original failure with a cleanup-only one.
        if reply_index is not None:
            try:
                bot1.del_post(board='Test', index=reply_index)
                post = bot1.get_post(board='Test', index=reply_index, query=True)
                if post and post.get(PostField.post_status) == PyPtt.PostStatus.EXISTS:
                    warnings.warn(f'cleanup failed: reply post at index {reply_index} still EXISTS')
            except Exception as exc:
                warnings.warn(f'cleanup failed for reply post at index {reply_index}: {exc!r}')
        try:
            deep_learning_bot.del_post(board='Test', index=target_index)
            post = deep_learning_bot.get_post(board='Test', index=target_index, query=True)
            if post and post.get(PostField.post_status) == PyPtt.PostStatus.EXISTS:
                warnings.warn(f'cleanup failed: target post at index {target_index} still EXISTS')
        except Exception as exc:
            warnings.warn(f'cleanup failed for target post at index {target_index}: {exc!r}')


def _reply_post_board_mail(ptt_bots, deep_learning_bot, sign_file_trace, backup):
    bot1 = ptt_bots[0]
    target_title, target_index = _post_reply_target(deep_learning_bot, bot1)
    reply_index = None
    try:
        codingman_before = _mailbox_index(bot1)
        deeplearning_before = _mailbox_index(deep_learning_bot)

        start = time.time()
        bot1.reply_post(reply_to=ReplyTo.BOARD_MAIL, board='Test',
                        content=f'ReplyTo.BOARD_MAIL backup={backup} regression test\n',
                        index=target_index, sign_file=0, backup=backup)
        elapsed = time.time() - start
        _assert_no_stalled_round(bot1, elapsed, f'reply_post(BOARD_MAIL, backup={backup})')

        appearances = sum(1 for e in sign_file_trace if e['present_in_screen'])
        matches = sum(1 for e in sign_file_trace if e['matched'])
        print(f'[sign_file_trace backup={backup}] '
              f'請選擇簽名檔 appeared in {appearances} round(s), matched {matches} of them: '
              f'{sign_file_trace}')

        time.sleep(REPLY_APPEAR_WAIT)
        reply_index = _find_reply_index(bot1, target_title)
        assert reply_index is not None, (
            f'reply to {target_title!r} not found on Test board -- '
            f'reply_post(BOARD_MAIL, backup={backup}) silently did not complete'
        )

        time.sleep(MAIL_DELIVERY_WAIT)
        deeplearning_after = _mailbox_index(deep_learning_bot)
        assert deeplearning_after == deeplearning_before + 1, (
            f'DeepLearning did not receive the BOARD_MAIL reply: mailbox index '
            f'{deeplearning_before} -> {deeplearning_after}'
        )

        # NOTE (discovered while writing this test, not a max_match=1 effect):
        # unlike ReplyTo.MAIL, pttbbs never shows '已順利寄出，是否自存底稿'
        # for ReplyTo.BOARD_MAIL at all (confirmed by tracing every matched
        # TargetUnit for this call: '▲ 回應至' -> '採用原標題[Y/n]?' ->
        # '請問要引用原文嗎' -> '編輯文章' -> '確定要儲存檔案嗎' ->
        # '任意鍵繼續', with neither '請選擇簽名檔' nor the backup prompt
        # ever appearing). So `backup=` has no observable effect on
        # BOARD_MAIL's own mailbox -- it stays unchanged either way. This
        # contradicts the docstring's "僅在回覆類型含站內信時有作用" implying
        # BOARD_MAIL should behave like MAIL here; flagging as a separate,
        # pre-existing discrepancy rather than silently asserting the
        # (unverified) assumption.
        codingman_after = _mailbox_index(bot1)
        assert codingman_after == codingman_before, (
            f'reply_post(BOARD_MAIL, backup={backup}) changed the mailbox index '
            f'{codingman_before} -> {codingman_after} -- if this now fires with '
            f'backup=True, the no-backup-prompt assumption above no longer holds '
            f'and this assertion needs revisiting'
        )
    finally:
        if reply_index is not None:
            try:
                bot1.del_post(board='Test', index=reply_index)
            except Exception:
                pass
        try:
            deep_learning_bot.del_post(board='Test', index=target_index)
        except Exception:
            pass
        _find_and_delete_mail(deep_learning_bot, target_title)
        _find_and_delete_mail(bot1, target_title)


def test_reply_post_board_mail_backup_false(ptt_bots, deep_learning_bot, sign_file_trace):
    _reply_post_board_mail(ptt_bots, deep_learning_bot, sign_file_trace, backup=False)


def test_reply_post_board_mail_backup_true(ptt_bots, deep_learning_bot, sign_file_trace):
    _reply_post_board_mail(ptt_bots, deep_learning_bot, sign_file_trace, backup=True)
