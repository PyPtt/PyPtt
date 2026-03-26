# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
python -m pytest tests/test_init.py tests/test_i18n.py tests/test_exceptions.py tests/test_logger.py tests/test_parse_query_post.py tests/test_get_post_parser.py
```

Run a single test:
```bash
python -m pytest tests/test_parse_query_post.py::TestPushNumber::test_explode_plus_prefix
```

Integration tests (require `.env` with `PTT1_ID`, `PTT1_PW`, `PTT2_ID`, `PTT2_PW`):
```bash
python -m pytest tests/
```

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

### Python version support

Python 3.11+. CI runs against 3.11–3.14 including free-threading variants (`3.13t`, `3.14t`).
