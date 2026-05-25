# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Version

Version is defined in `PyPtt/__init__.py` (`__version__`).

`setup.py` reads `__version__` and appends `.dev{GITHUB_RUN_NUMBER}` when building on a non-master branch. The CI check (`Forget to update the version?`) fails if the built version's prefix matches the latest PyPI release.

Before merging a feature branch, ensure the version is ahead of PyPI:

```bash
# Check PyPI latest
curl -s https://pypi.org/pypi/PyPtt/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
# Check local
grep __version__ PyPtt/__init__.py
# If local == PyPI version, bump the patch in PyPtt/__init__.py
```

## Commands

### Install
```bash
pip install -e ".[dev]"
```

### Lint
```bash
flake8 PyPtt/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 PyPtt/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Run tests
Unit tests (no network required — run these during development):
```bash
python -m pytest tests/test_init.py tests/test_i18n.py tests/test_exceptions.py tests/test_logger.py tests/test_parse_query_post.py tests/test_get_post_parser.py tests/test_vt100_parser.py tests/test_get_post_list_parser.py tests/test_pyte_parity.py
```

`test_pyte_parity.py` cross-checks `VT100Parser` against the `pyte` reference VT100 emulator on captured PTT byte streams (`tests/fixtures/vt100/*.bin`). Skipped if `pyte` isn't installed.

Run a single test:
```bash
python -m pytest tests/test_parse_query_post.py::TestPushNumber::test_explode_plus_prefix
```

Integration tests (require `.env` with `PTT1_ID`, `PTT1_PW`, `PTT2_ID`, `PTT2_PW`, `TEST_USER`; optionally `MOD_BOARD` for moderator-only tests):
```bash
python -m pytest tests/
```

Credentialed integration tests stay local-only — cloud platforms can't reach PTT. CI only runs the no-network unit tests above.

When the full integration suite runs as one long pytest session, mutation-heavy tests (`give_money`, `post`, `reply_post`, `search_user`, `comment`, `mark_post`, `mail_send_and_del`, `set_board_title`, `bucket`, `change_pw`) intermittently fail with `ConnectionClosed`, `NoSuchBoard`, or session-state errors. They pass when run individually or as a small focused group (e.g. `pytest tests/test_set_board_title.py tests/test_bucket.py tests/test_mark_post.py`) — this is PTT session instability and PyPtt's shared session-scoped bot, not a regression signal.

Several moderator-only API tests (`test_mark_post.py`, `test_set_board_title.py`, `test_bucket.py`) need `MOD_BOARD` set to a board the bot moderates (those APIs unconditionally call `check_board(..., check_moderator=True)`). They `pytest.skip` themselves when `MOD_BOARD` is unset. `test_bucket.py::test_bucket_on_moderated_board` additionally mutes `config.TEST_USER`.

`test_fast_post.py` is xfail-strict — `fast_post_step0/1` and `fast_post` call a non-existent `connect_core.API.fast_send` method and will raise `AttributeError`. Drop the xfail once that method is implemented (or the calls are rewired to `send`).

## Architecture

PyPtt is a Python library for automating the PTT BBS (a Telnet/WebSocket bulletin board system popular in Taiwan).

### Main classes

**`PyPtt.API`** (`PyPtt/PTT.py`) — The primary entry point. All ~30 public methods (post, comment, get_post, login, etc.) live here. Not thread-safe.

**`PyPtt.Service`** (`PyPtt/service.py`) — Thread-safe wrapper around `API`. Queues calls from multiple threads and runs a single `API` instance in a dedicated thread. Interface: `service.call('method_name', {args})`.

**`connect_core`** (`PyPtt/connect_core.py`) — Handles WebSocket/Telnet connections and screen parsing. `TargetUnit` defines expected terminal screen patterns and auto-responses. `send()` waits for matching screen patterns before returning.

### API method pattern

Each `_api_*.py` module follows this pattern:
1. Validate parameters via `check_value.check_type()` / `check_value.check_range()`
2. Check preconditions via `_api_util.*` (login state, board exists, etc.)
3. Navigate to the right screen via `_api_util.goto_board()`
4. Send terminal commands using constants from `command.py`
5. Match screen responses using `connect_core.TargetUnit` patterns
6. Parse and return results

### Key modules

- `PyPtt/data_type.py` — Enums (`Language`, `ConnectMode`, `SearchType`, `CommentType`, `HOST`, `PostStatus`, field enums) and `TimedDict` (auto-expiring dict)
- `PyPtt/exceptions.py` — Exception hierarchy (auth, permissions, state, resources, network)
- `PyPtt/i18n.py` + `lang_zh_TW.py` / `lang_en_US.py` — Internationalization; all user-facing strings are in the lang files
- `PyPtt/check_value.py` — Parameter validation utilities used across all `_api_*.py` modules
- `PyPtt/screens.py` — Terminal screen parsing
- `PyPtt/command.py` — Terminal command constants

### `VT100Parser` cursor model

Cursor positions are tracked in **terminal cells**, not encoded bytes:
- Wide ('W'), Fullwidth ('F'), and Ambiguous ('A') chars = 2 cells
- All other chars = 1 cell
- `\x1b[y;xH` column is 1-based on the wire; the parser converts to 0-based

PTT's Ambiguous-width glyphs (`※` `←` `→` `◎` `★` `─` etc.) are rendered as 2 cells by PTT terminals, so the parser must agree. This is what makes column padding line up when PTT positions the cursor past a wide-char run.

PTT emits wide chars via `' ' ' ' '\x08' '\x08' <wide_char>` (two spaces to reserve visual width, then two backspaces to step back, then the wide char), followed by a positioning escape. `VT100Parser` collapses ` \x08` pairs during preprocessing so only the wide char remains in the output string.

The parser returns a **string-position view** — one character per wide glyph, no placeholder cell after — not a cell view. Downstream `_api_*` parsers depend on this convention.

### Downstream parser slicing

A few `_api_*` modules use fixed-column string slices on parsed screens (notably `_api_get_post_list.py` for the listing row layout). These offsets assume a specific leading-space alignment that the cursor-tracking model produces. Changing `VT100Parser`'s output format requires re-verifying these slices — see `tests/test_get_post_list_parser.py` and `tests/test_pyte_parity.py` for regression guards.

### Parser regression tooling

- `tests/capture_vt100_fixtures.py` — monkey-patches `VT100Parser.__init__` to dump raw byte streams from a live PTT session into `tests/fixtures/vt100/*.bin`. Run to regenerate fixtures.
- `tests/compare_parsers.py` — verbose side-by-side diff of `VT100Parser` vs `pyte` for ad-hoc debugging. The pytest version is `tests/test_pyte_parity.py`.
- `tests/verify_downstream.py` — live PTT sanity check that exercises `get_user` / `get_board_info` / `get_post` and prints every parsed field.

### Python version support

Python 3.11+. CI runs against 3.11–3.14 including free-threading variants (`3.13t`, `3.14t`).
