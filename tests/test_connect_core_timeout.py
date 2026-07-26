"""No-network regression tests for the half-dead-connection heuristic in
connect_core.API._async_send: a round that receives zero bytes before its
screen_timeout elapses is treated as a dead connection (ConnectionClosed),
while a round that receives at least one byte but never matches a target
keeps the pre-existing timeout-returns--1 behavior."""

import asyncio

import pytest

from PyPtt import config, connect_core, exceptions


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


def test_total_silence_raises_connection_closed():
    api = _make_api(chunks=[])
    target = connect_core.TargetUnit('NEVER_MATCHES_ANYTHING')

    with pytest.raises(exceptions.ConnectionClosed):
        api.send('cmd', [target], screen_timeout=0.1)


def test_bytes_received_without_match_still_returns_minus_one():
    api = _make_api(chunks=[b'some screen noise that matches nothing'])
    target = connect_core.TargetUnit('NEVER_MATCHES_ANYTHING')

    result = api.send('cmd', [target], screen_timeout=0.1)

    assert result == -1


def test_mid_send_disconnect_after_a_matched_round_still_returns_minus_one():
    """received_any_byte is tracked per-send, not per-round, on purpose: a
    multi-round send() (e.g. del_post's confirm -> bad-post-menu -> InBoard
    chain) that matches a target in round 1 and then goes fully silent in a
    later round must still return -1, not raise ConnectionClosed.

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
