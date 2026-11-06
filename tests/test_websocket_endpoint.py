"""No-network regression test for the WebSocket endpoint connect_core dials.

On 2026-11-06 PTT1's gateway started answering wss://ws.ptt.cc/bbs/ (with a
trailing slash) with HTTP 404, so login died with ConnectError before reaching
any screen. term.ptt.cc connects to wss://ws.ptt.cc/bbs, which still works.
"""
import pytest

from PyPtt import config, connect_core, data_type


class FakeApi:
    def __init__(self, host, port=23):
        self.config = config.Config()
        self.config.host = host
        self.config.port = port


def _endpoint(host, port=23):
    return connect_core.API(FakeApi(host, port))._websocket_endpoint()


@pytest.mark.parametrize('host, url, origin', [
    (data_type.HOST.PTT1, 'wss://ws.ptt.cc/bbs', 'https://term.ptt.cc'),
    (data_type.HOST.PTT2, 'wss://ws.ptt2.cc/bbs', 'https://term.ptt2.cc'),
    (data_type.HOST.LOCALHOST, 'ws://localhost:48763/bbs', 'http://localhost'),
])
def test_known_hosts(host, url, origin):
    assert _endpoint(host) == (url, origin)


@pytest.mark.parametrize('host', [data_type.HOST.PTT1, data_type.HOST.PTT2, data_type.HOST.LOCALHOST])
def test_no_trailing_slash(host):
    url, _ = _endpoint(host)
    assert not url.endswith('/')


def test_localhost_custom_port():
    assert _endpoint(data_type.HOST.LOCALHOST, port=12345)[0] == 'ws://localhost:12345/bbs'
