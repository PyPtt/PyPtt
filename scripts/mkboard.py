#!/usr/bin/env python3
"""Create or update a board record in a local imageptt container's `.BRD` file.

Directly patches the raw `boardheader_t` array (see `pttbbs/include/board.h`)
instead of driving the BBS menu UI, so it can run once, non-interactively,
against a freshly-started container. Must run as the `bbs` user inside the
container (root can write the file but the running `mbbsd`/`shmctl` processes
own it as `bbs:bbs`, and `shmctl reloadbcache` requires `-u bbs` shmat access
— see `bootstrap_local_pttbbs.py`).

Usage (inside the container):
    python3 mkboard.py <board_name> [bm_id] [posttype1,posttype2,...]

    board_name   Board id, e.g. "Test".
    bm_id        Moderator's ptt_id. Omit or pass "" for no moderator.
    posttype     Comma-separated "文章種類" category names (up to 8, each at
                 most 2 Big5 characters), e.g. "問題,心得,其他". Omit or pass
                 "" to leave the board without a post-type list.

After running this (and for every board it touches), reload the live board
cache and BM cache as the `bbs` user:
    ./bin/shmctl reloadbcache
    ./bin/shmctl bBMC
"""
import os
import sys

BRD = '/home/bbs/.BRD'
SIZE = 256
IDLEN = 12
BTLEN = 48

# Offsets within a 256-byte boardheader_t record (see pttstruct.py /
# pttbbs/include/board.h). Only the fields this script writes are listed.
OFF_BRD, L_BRD = 0, IDLEN + 1
OFF_TITLE, L_TITLE = OFF_BRD + L_BRD, BTLEN + 1
OFF_BM, L_BM = OFF_TITLE + L_TITLE, IDLEN * 3 + 3
OFF_POSTTYPE, L_POSTTYPE = 172, 33
OFF_POSTTYPE_F = 205


def setfield(hdr: bytearray, off: int, length: int, raw: bytes) -> None:
    raw = raw[:length - 1]  # keep null terminator room
    hdr[off:off + length] = raw + b'\x00' * (length - len(raw))


def encode_posttypes(names) -> bytes:
    """Pack up to 8 category names into the 33-byte `posttype` field.

    Each category occupies a 4-byte, space-padded (not null-padded) Big5
    slot; the list ends at the first all-zero slot, which the trailing
    `bytearray(32)` zero-fill provides for free.
    """
    buf = bytearray(32)
    for i, name in enumerate(names[:8]):
        raw = name.encode('big5')[:4]
        raw = raw + b' ' * (4 - len(raw))
        buf[i * 4:(i + 1) * 4] = raw
    return bytes(buf) + b'\x00'


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    board_name = args[0]
    bm_id = args[1] if len(args) > 1 else ''
    posttype_csv = args[2] if len(args) > 2 else ''
    posttypes = [t for t in posttype_csv.split(',') if t] if posttype_csv else []

    title_b = ('測試 ◎PyPtt ' + board_name).encode('big5')

    data = bytearray(open(BRD, 'rb').read())
    n = len(data) // SIZE

    def brdname(i):
        return data[i * SIZE:i * SIZE + IDLEN + 1].split(b'\x00')[0].decode('latin1')

    existing = [i for i in range(n) if brdname(i).lower() == board_name.lower()]

    # Template: board "Note" (open board, attr=0, level=0); fall back to index 9.
    tmpl_idx = None
    for i in range(n):
        if brdname(i) == 'Note':
            tmpl_idx = i
    if tmpl_idx is None:
        tmpl_idx = 9
    hdr = bytearray(data[tmpl_idx * SIZE:(tmpl_idx + 1) * SIZE])

    setfield(hdr, OFF_BRD, L_BRD, board_name.encode('latin1'))
    setfield(hdr, OFF_TITLE, L_TITLE, title_b)
    setfield(hdr, OFF_BM, L_BM, bm_id.encode('latin1'))
    setfield(hdr, OFF_POSTTYPE, L_POSTTYPE, encode_posttypes(posttypes))
    hdr[OFF_POSTTYPE_F] = 0

    if existing:
        idx = existing[0]
        data[idx * SIZE:(idx + 1) * SIZE] = hdr
        action = 'UPDATED existing board #%d' % (idx + 1)
    else:
        data += hdr
        action = 'APPENDED as board #%d' % (n + 1)

    open(BRD, 'wb').write(data)
    os.chmod(BRD, 0o644)

    # Create board directory boards/<first char>/<name>/
    bdir = '/home/bbs/boards/%s/%s' % (board_name[0], board_name)
    os.makedirs(bdir, exist_ok=True)

    print(action)
    print('board dir:', bdir, 'exists' if os.path.isdir(bdir) else 'MISSING')
    print('BM field set to:', bm_id or '(none)')
    print('posttype set to:', posttypes or '(none)')
    print('.BRD now', len(data) // SIZE, 'boards,', len(data), 'bytes')


if __name__ == '__main__':
    main()
