"""Integration test for mail + del_mail.

Round-trip: send a mail to self, locate it in the mailbox, verify its
content, then delete it. Tests both `mail` (untested elsewhere) and
`del_mail` (also untested), and exercises `get_mail` against a freshly
posted item.
"""
import time

import PyPtt
from PyPtt import MailField, NewIndex


def test_mail_send_to_self_then_delete(ptt_bots):
    for ptt_bot in ptt_bots:
        title = f'PyPtt mail test {int(time.time())}'
        content = (
            'PyPtt 自動化測試\n'
            'mail round-trip integration test\n'
            f'host={ptt_bot.host}\n'
        )

        # Mail to self so we don't spam another account.
        ptt_bot.mail(
            ptt_id=ptt_bot.ptt_id,
            title=title,
            content=content,
            sign_file=0,
            backup=True,
        )
        time.sleep(2)  # let PTT deliver the mail

        newest = ptt_bot.get_newest_index(index_type=NewIndex.MAIL)
        assert newest > 0, 'mailbox empty after send'

        # Walk back from the newest mail until we find ours (newest entry
        # is usually it, but PTT sometimes interleaves system mail).
        target_index = None
        for i in range(5):
            mail_info = ptt_bot.get_mail(newest - i)
            if mail_info[MailField.title].endswith(title):
                target_index = newest - i
                break
        assert target_index is not None, f'sent mail {title!r} not found in mailbox'

        # Verify the content survived the round-trip.
        mail_info = ptt_bot.get_mail(target_index)
        assert 'PyPtt 自動化測試' in mail_info[MailField.content]
        assert 'mail round-trip integration test' in mail_info[MailField.content]

        # Clean up — del_mail must succeed (raises on failure).
        # We don't assert on the post-delete newest_index because PyPtt
        # caches that value (`api._newest_index_data`) and the immediate
        # next read can return stale data.
        ptt_bot.del_mail(target_index)
