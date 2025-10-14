import re


def test_get_time(ptt_bots):
    """Tests getting the current time from PTT."""
    time_pattern = re.compile(r'^\d{2}:\d{2}$')

    for ptt_bot in ptt_bots:
        # Run a few times to ensure consistency
        for _ in range(3):
            ptt_time = ptt_bot.get_time()
            assert ptt_time is not None, f'get_time returned None for host {ptt_bot.host}'
            assert time_pattern.match(ptt_time), f'Time format "{ptt_time}" is invalid for host {ptt_bot.host}'
