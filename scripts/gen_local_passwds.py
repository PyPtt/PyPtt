#!/usr/bin/env python3
"""Generate a `.PASSWDS` for a local bbsdocker/imageptt container with ready-to-use,
already-registered (PERM_POST) accounts, so integration tests can log in without the
interactive `new` registration + SYSOP approval dance.

Usage:
    python scripts/gen_local_passwds.py id1:pw1 [id2:pw2 ...] > .PASSWDS
    docker cp .PASSWDS <container>:/home/bbs/.PASSWDS
    docker exec -u bbs <container> sh -c 'cd /home/bbs && ./bin/uhash_loader'

The container resets on every restart (no volume), so re-run this each time you
spin it up. See CLAUDE.md "Testing against a local pttbbs (Docker)".

Struct layout mirrors ptt/pttbbs `util/pyutil/pttstruct.py` (userec_t, 512 bytes).
"""
import crypt  # ponytail: local-dev only (Py 3.11/3.12); removed in 3.13. On 3.13+ compute
              # the hash in-container (`perl -e 'print crypt("pw","aa")'`) and inline it here.
import struct
import sys

IDLEN, IPV4LEN, PASSLEN, REGLEN = 12, 15, 14, 38
PASSWD_VERSION = 4194
USEREC_SIZE = 512
MAX_USERS = 100  # imageptt .PASSWDS is 100 slots x 512 bytes
USERLEVEL = 0o37  # PERM_BASIC|CHAT|PAGE|POST|LOGINOK -> registered, can post
SALT = "aa"      # traditional DES crypt; Python's crypt matches the container's libc crypt

USEREC_FMT = (
    ("version", "I"), ("userid", "%ds" % (IDLEN+1)), ("realname", "20s"),
    ("nickname", "24s"), ("passwd", "%ds" % PASSLEN), ("pad_1", "B"),
    ("uflag", "I"), ("deprecated_uflag2", "I"), ("userlevel", "I"),
    ("numlogindays", "I"), ("numposts", "I"), ("firstlogin", "I"),
    ("lastlogin", "I"), ("lasthost", "%ds" % (IPV4LEN+1)), ("money", "I"),
    ("_unused", "4s"), ("email", "50s"), ("address", "50s"),
    ("justify", "%ds" % (REGLEN + 1)), ("month", "B"), ("day", "B"),
    ("year", "B"), ("_unused3", "B"), ("pager_ui_type", "B"), ("pager", "B"),
    ("invisible", "B"), ("_unused4", "2s"), ("exmailbox", "I"),
    ("_unused5", "4s"), ("career", "40s"), ("phone", "20s"), ("_unused6", "I"),
    ("chkpad1", "44s"), ("role", "I"), ("lastseen", "I"), ("timesetangel", "I"),
    ("timeplayangel", "I"), ("lastsong", "I"), ("loginview", "I"),
    ("_unused8", "B"), ("pad_2", "B"), ("vl_count", "H"), ("five_win", "H"),
    ("five_lose", "H"), ("five_tie", "H"), ("chc_win", "H"), ("chc_lose", "H"),
    ("chc_tie", "H"), ("mobile", "I"), ("mind", "4s"), ("go_win", "H"),
    ("go_lose", "H"), ("go_tie", "H"), ("dark_win", "H"), ("dark_lose", "H"),
    ("_unused9", "B"), ("signature", "B"), ("_unused19", "B"), ("badpost", "B"),
    ("dark_tie", "H"), ("myangel", "%ds" % (IDLEN + 1)), ("pad_3", "B"),
    ("chess_elo_rating", "H"), ("withme", "I"), ("timeremovebadpost", "I"),
    ("timeviolatelaw", "I"), ("pad_trail", "28s"),
)
FMT = "<" + "".join(v for _, v in USEREC_FMT)
assert struct.calcsize(FMT) == USEREC_SIZE, struct.calcsize(FMT)


def userec(userid: str, password: str, now: int = 1700000000) -> bytes:
    d = {name: (b"" if "s" in f else 0) for name, f in USEREC_FMT}
    d.update(
        version=PASSWD_VERSION,
        userid=userid.encode(),
        realname=userid.encode(),
        nickname=userid.encode(),
        passwd=crypt.crypt(password[:8], SALT).encode(),  # mbbsd truncates to 8 chars
        userlevel=USERLEVEL,
        numlogindays=1,
        firstlogin=now,
        lastlogin=now,
        lasthost=b"127.0.0.1",
        justify=b"pyptt",  # non-empty => registration already approved
        email=b"x@x.x",
    )
    return struct.pack(FMT, *[d[name] for name, _ in USEREC_FMT])


def build(pairs) -> bytes:
    slots = [b"\x00" * USEREC_SIZE] * MAX_USERS
    for i, (uid, pw) in enumerate(pairs):
        assert len(uid) <= IDLEN, "userid %r too long (max %d)" % (uid, IDLEN)
        slots[i] = userec(uid, pw)
    return b"".join(slots)


def _selfcheck():
    blob = build([("pypttbot1", "test1234")])
    assert len(blob) == MAX_USERS * USEREC_SIZE
    rec = struct.unpack_from(FMT, blob, 0)
    fields = dict(zip((n for n, _ in USEREC_FMT), rec))
    assert fields["version"] == PASSWD_VERSION
    assert fields["userid"].rstrip(b"\x00") == b"pypttbot1"
    assert fields["userlevel"] == USERLEVEL
    print("selfcheck OK")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selfcheck"]:
        _selfcheck()
    elif args and all(":" in a for a in args):
        pairs = [a.split(":", 1) for a in args]
        sys.stdout.buffer.write(build(pairs))
    else:
        sys.exit(__doc__)
