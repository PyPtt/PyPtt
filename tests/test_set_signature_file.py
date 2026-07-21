"""Integration test for set_signature_file (the PTT "名片檔"/plan).

Self-restoring round-trip: capture the account's current signature file via
`get_user`, overwrite it with an identifiable marker, verify the marker shows
up on a fresh `get_user` read, then set it back to the original content so
the test doesn't leave a permanent change on the account.
"""
import time

from PyPtt import UserField


def test_set_signature_file_round_trip(ptt_bots):
    for ptt_bot in ptt_bots:
        original = ptt_bot.get_user(ptt_bot.ptt_id)[UserField.signature_file]

        marker = f'PyPtt set_signature_file test {int(time.time())}'
        try:
            ptt_bot.set_signature_file(marker)
            time.sleep(1)

            updated = ptt_bot.get_user(ptt_bot.ptt_id)[UserField.signature_file]
            assert marker in updated.strip()
        finally:
            # Restore -- must always run, even if the assertion above fails.
            ptt_bot.set_signature_file(original)
            time.sleep(1)

            restored = ptt_bot.get_user(ptt_bot.ptt_id)[UserField.signature_file]
            # Tolerate trailing whitespace/blank-line drift from the
            # editor round-trip; compare on stripped content.
            assert restored.strip() == original.strip()
