"""Vendored Big5-UAO codec.

Vendored (unmodified) from PttCodingMan/pyUAO, a fork of eight04/pyUAO,
to drop the external `uao` PyPI dependency (unmaintained upstream) and
pick up this fork's correctness fixes and incremental/stream codec
support. Vendoring is for dependency control, not performance: PyPtt is
I/O bound, so codec speed is not the point here.

Source:  https://github.com/PttCodingMan/pyUAO
Commit:  9d9a8bf59dbe60800d214b66ce972bc2ddf8da89 (v0.3.0)
License: MIT (c) 2018 eight -- see LICENSE in this directory.
"""

from codecs import (
    Codec,
    CodecInfo,
    IncrementalDecoder,
    IncrementalEncoder,
    StreamReader,
    StreamWriter,
    lookup_error,
    register,
)

from .b2u import b2u_table
from .u2b import u2b_table

__version__ = "0.3.0"

# ASCII is not part of the generated table; fill it in once at import time so
# the hot loops below never have to special-case it or mutate the tables.
for _i in range(0x80):
    u2b_table.setdefault(chr(_i), bytes((_i,)))
del _i

# UAO maps the lone byte 0xFF to U+F8F8. The generated u2b table stores that
# mapping as a zero-padded pair (b"\x00\xff"), which is not a valid Big5 byte
# sequence, and the generated b2u table omits it entirely. 0xFF is never a
# lead byte (b2u lead bytes are 0x81-0xFE), so a single-byte entry is safe.
u2b_table["\uf8f8"] = b"\xff"
b2u_table.setdefault(0xFF, "\uf8f8")

_u2b_get = u2b_table.get
_b2u_get = b2u_table.get


def _encode(input, errors):
    """Encode a str, returning a list of bytes chunks."""
    try:
        # fast path: every character is in the table
        return [u2b_table[c] for c in input]
    except KeyError:
        pass
    out = []
    append = out.append
    error_handler = None
    i = 0
    n = len(input)
    while i < n:
        b = _u2b_get(input[i])
        if b is not None:
            append(b)
            i += 1
            continue
        if error_handler is None:
            error_handler = lookup_error(errors)
        replacement, i = error_handler(UnicodeEncodeError(
            "big5-uao", input, i, i + 1, "illegal multibyte sequence"))
        if i < 0:
            i += n
        if isinstance(replacement, str):
            out += _encode(replacement, "strict")
        else:
            append(replacement)
    return out


def _decode(input, errors, final):
    """Decode bytes, returning (list of str chunks, bytes consumed).

    With final=False, a trailing lead byte is left unconsumed so the
    incremental decoder can buffer it until more data arrives.
    """
    out = []
    append = out.append
    error_handler = None
    i = 0
    n = len(input)
    while i < n:
        c = input[i]
        if c < 0x80:
            append(chr(c))
            i += 1
            continue
        if i + 1 < n:
            u = _b2u_get(c * 0x100 + input[i + 1])
            if u is not None:
                append(u)
                i += 2
                continue
            u = _b2u_get(c)
            if u is not None:
                append(u)
                i += 1
                continue
            reason = "illegal multibyte sequence"
            end = i + 1
        else:
            # single-byte mappings (0xFF) never start a pair, so they can
            # be emitted even when more data may follow
            u = _b2u_get(c)
            if u is not None:
                append(u)
                i += 1
                continue
            if not final:
                break
            reason = "incomplete multibyte sequence"
            end = n
        if error_handler is None:
            error_handler = lookup_error(errors)
        replacement, i = error_handler(UnicodeDecodeError(
            "big5-uao", input, i, end, reason))
        if i < 0:
            i += n
        append(replacement)
    return out, i


class Big5UAOCodec(Codec):
    def encode(self, input, errors="strict"):
        """Encode str to bytes with the u2b table."""
        return b"".join(_encode(input, errors)), len(input)

    def decode(self, input, errors="strict"):
        """Decode bytes to str with the b2u table."""
        input = bytes(input)
        out, consumed = _decode(input, errors, True)
        return "".join(out), consumed


class Big5UAOIncrementalEncoder(IncrementalEncoder):
    def encode(self, input, final=False):
        return b"".join(_encode(input, self.errors))


class Big5UAOIncrementalDecoder(IncrementalDecoder):
    def __init__(self, errors="strict"):
        IncrementalDecoder.__init__(self, errors)
        self.buffer = b""

    def decode(self, input, final=False):
        data = self.buffer + bytes(input)
        out, consumed = _decode(data, self.errors, final)
        self.buffer = data[consumed:]
        return "".join(out)

    def reset(self):
        self.buffer = b""

    def getstate(self):
        return self.buffer, 0

    def setstate(self, state):
        self.buffer = state[0]


class Big5UAOStreamWriter(Big5UAOCodec, StreamWriter):
    pass


class Big5UAOStreamReader(Big5UAOCodec, StreamReader):
    def decode(self, input, errors="strict"):
        # Never treat the chunk as final: StreamReader keeps unconsumed
        # bytes in its buffer, so a split multibyte sequence is completed
        # by the next read instead of raising.
        input = bytes(input)
        out, consumed = _decode(input, errors, False)
        return "".join(out), consumed


_codec_info = None

def _lookup(name):
    if name in ("big5-uao", "big5uao", "big5_uao"):
        global _codec_info
        if _codec_info is None:
            codec = Big5UAOCodec()
            _codec_info = CodecInfo(
                name="big5-uao",
                encode=codec.encode,
                decode=codec.decode,
                incrementalencoder=Big5UAOIncrementalEncoder,
                incrementaldecoder=Big5UAOIncrementalDecoder,
                streamreader=Big5UAOStreamReader,
                streamwriter=Big5UAOStreamWriter,
            )
        return _codec_info
    return None

REGISTERED = False
def register_uao():
    global REGISTERED
    if REGISTERED:
        return
    REGISTERED = True
    register(_lookup)
