"""No-network regression tests for connect_core.API._async_send's timeout
handling: a round that receives zero bytes before its screen_timeout elapses
no longer raises ConnectionClosed (that heuristic was falsified -- pttbbs
silently drops invalid keys without redrawing, producing zero-byte timeouts
on connections that are still alive). Instead, send() always returns -1 on
timeout and records whether the timeout was totally silent on
`last_timeout_was_silent`, leaving the death-vs-alive judgment call to the
caller (see PyPtt/_api_get_user.py)."""

import asyncio

from PyPtt import config, connect_core


class FakeCore:
    """Stands in for the websockets connection. Replays `chunks` one at a
    time; once exhausted (or if empty from the start), recv() hangs forever
    so the caller's asyncio.timeout is what ends the round."""

    def __init__(self, chunks=()):
        self._chunks = list(chunks)

    async def send(self, _data):
        pass

    async def recv(self):
        if self._chunks:
            return self._chunks.pop(0)
        await asyncio.sleep(3600)


class FakeApi:
    def __init__(self):
        self.config = config.Config()
        self.config.screen_timeout = 0.1
        self.cursor = None


def _make_api(chunks=()):
    core_api = connect_core.API(FakeApi())
    core_api._core = FakeCore(chunks)
    return core_api


def test_total_silence_returns_minus_one_and_flags_silent():
    """Zero bytes for the whole send() no longer raises ConnectionClosed --
    it returns -1 like any other timeout, and sets last_timeout_was_silent
    so the caller can decide what a fully-silent timeout means for it."""
    api = _make_api(chunks=[])
    target = connect_core.TargetUnit('NEVER_MATCHES_ANYTHING')

    result = api.send('cmd', [target], screen_timeout=0.1)

    assert result == -1
    assert api.last_timeout_was_silent is True


def test_bytes_received_without_match_still_returns_minus_one():
    """At least one byte arrived but nothing matched: still a plain -1
    timeout, and last_timeout_was_silent must be False (the connection was
    demonstrably talking)."""
    api = _make_api(chunks=[b'some screen noise that matches nothing'])
    target = connect_core.TargetUnit('NEVER_MATCHES_ANYTHING')

    result = api.send('cmd', [target], screen_timeout=0.1)

    assert result == -1
    assert api.last_timeout_was_silent is False


def test_mid_send_disconnect_after_a_matched_round_still_returns_minus_one():
    """received_any_byte is tracked per-send, not per-round, on purpose: a
    multi-round send() (e.g. del_post's confirm -> bad-post-menu -> InBoard
    chain) that matches a target in round 1 and then goes fully silent in a
    later round must still return -1 with last_timeout_was_silent False, not
    True.

    This is what keeps _api_del_post.py:351's `timed_out = result == -1`
    reachable, letting it report "delete succeeded, but PTT never returned
    to the board screen" on an already-irreversible operation instead of
    the caller seeing a bare ConnectionClosed with no idea whether the
    delete went through. If received_any_byte is ever moved back to being
    reset every round, this test goes red.
    """
    non_break_target = connect_core.TargetUnit('CONFIRM_PROMPT', response='y')
    api = _make_api(chunks=[b'CONFIRM_PROMPT'])

    result = api.send('cmd', [non_break_target], screen_timeout=0.1)

    assert result == -1
    assert api.last_timeout_was_silent is False


def test_flag_resets_on_next_send():
    """last_timeout_was_silent must not leak from a previous call() into the
    next one: a silent-timeout send() followed by a normal, successfully
    matched send() must leave the flag False. Guards against a caller
    reading a stale True from an earlier, unrelated timeout."""
    api = _make_api(chunks=[])
    target = connect_core.TargetUnit('NEVER_MATCHES_ANYTHING')

    result = api.send('cmd', [target], screen_timeout=0.1)

    assert result == -1
    assert api.last_timeout_was_silent is True

    api._core = FakeCore(chunks=[b'HELLO'])
    match_target = connect_core.TargetUnit('HELLO', break_detect=True)

    result = api.send('cmd2', [match_target], screen_timeout=0.1)

    assert result != -1
    assert api.last_timeout_was_silent is False
