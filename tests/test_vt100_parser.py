"""
Unit tests for PyPtt.screens.VT100Parser.

Pure byte-stream → 24-line screen parsing — no network required.

Cursor positions are tracked in *terminal cells* (not bytes), with East
Asian Wide / Fullwidth / Ambiguous characters counted as 2 cells — matching
how a PTT-style CJK terminal lays out the screen.

TestRealFixtures at the bottom replays raw byte buffers captured from a
live PTT session (see capture_vt100_fixtures.py) and asserts that
recognizable PTT content appears in the parsed screens.
"""

from pathlib import Path

import pytest

from PyPtt.screens import VT100Parser, _cell_len, _cell_width, _str_pos_at_cells

FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures' / 'vt100'


def load_fixture(name: str) -> tuple[bytes, str]:
    data = (FIXTURE_DIR / f'{name}.bin').read_bytes()
    encoding = (FIXTURE_DIR / f'{name}.encoding').read_text().strip()
    return data, encoding


def parse_fixture(name: str) -> list[str]:
    data, encoding = load_fixture(name)
    return VT100Parser(data, encoding).screen.split('\n')


def parse(data: bytes, encoding: str = 'utf-8') -> list[str]:
    """Run the parser and return the screen split back into 24 lines."""
    return VT100Parser(data, encoding).screen.split('\n')


# ── cell-width helpers ───────────────────────────────────────────────────────

class TestCellWidth:
    """_cell_width / _cell_len underpin every column-position calculation."""

    def test_ascii_is_one_cell(self):
        for ch in 'A1 .!':
            assert _cell_width(ch) == 1

    def test_wide_cjk_is_two_cells(self):
        # 'W' (Wide) ideographs.
        for ch in '中文程式範例你好':
            assert _cell_width(ch) == 2

    def test_fullwidth_is_two_cells(self):
        # 'F' (Fullwidth) — e.g. fullwidth digits, letters, brackets.
        for ch in 'ＡＢＣ１２３＝':
            assert _cell_width(ch) == 2

    def test_ambiguous_is_two_cells_for_ptt(self):
        # PTT renders Ambiguous-width chars as 2 cells; the parser must agree.
        # These are the actual glyphs we encountered in real PTT screens.
        for ch in '※←→◎●★◢◤▆ˇ─':
            assert _cell_width(ch) == 2, f'{ch!r} should be 2 cells'

    def test_cell_len_sums_mixed_string(self):
        # '[軟工] 成為全宇宙のNo.1吧' has the layout PTT actually sends:
        #   '['(1) + '軟'(2) + '工'(2) + ']'(1) + ' '(1)
        # + '成'(2) + '為'(2) + '全'(2) + '宇'(2) + '宙'(2)
        # + 'の'(2) + 'N'(1) + 'o'(1) + '.'(1) + '1'(1) + '吧'(2) = 25
        assert _cell_len('[軟工] 成為全宇宙のNo.1吧') == 25

    def test_cell_len_empty(self):
        assert _cell_len('') == 0


class TestStrPosAtCells:
    """Map a cell offset back to a string index, used by _k and replace_mode."""

    def test_zero_cells_is_position_zero(self):
        assert _str_pos_at_cells('abc', 0) == 0
        assert _str_pos_at_cells('中文', 0) == 0

    def test_negative_clamps_to_zero(self):
        assert _str_pos_at_cells('abc', -5) == 0

    def test_ascii_one_to_one(self):
        assert _str_pos_at_cells('hello', 3) == 3
        assert _str_pos_at_cells('hello', 5) == 5

    def test_beyond_end_returns_len(self):
        # When target exceeds the string's visible width, return len(line)
        # so callers slice up to the end without IndexError.
        assert _str_pos_at_cells('hello', 100) == 5
        assert _str_pos_at_cells('中文', 100) == 2

    def test_wide_char_skipped_when_target_lands_inside(self):
        # '中文' = 4 cells. Asking for cell 1 lands inside '中' (cells 0-1);
        # we round forward so the wide char is treated as fully consumed.
        assert _str_pos_at_cells('中文', 1) == 1

    def test_mixed_line_round_trip(self):
        # 'A中B' = cells [A=0, 中=1-2, B=3], string indices [A=0, 中=1, B=2].
        assert _str_pos_at_cells('A中B', 0) == 0
        assert _str_pos_at_cells('A中B', 1) == 1   # at start of 中
        assert _str_pos_at_cells('A中B', 3) == 2   # after 中, before B
        assert _str_pos_at_cells('A中B', 4) == 3   # after B (end)


# ── basics ────────────────────────────────────────────────────────────────────

class TestBasics:
    def test_empty_input_gives_24_blank_lines(self):
        lines = parse(b'')
        assert len(lines) == 24
        assert all(line == '' for line in lines)

    def test_plain_ascii_lands_on_first_line(self):
        lines = parse(b'hello world')
        assert lines[0] == 'hello world'
        assert all(line == '' for line in lines[1:])

    def test_screen_is_always_24_rows(self):
        # Even very small input yields exactly 24 rows.
        assert len(parse(b'x')) == 24
        # Writing past the visible region (clamped) still yields 24.
        assert len(parse(b'\x1b[100;1HX')) == 24


# ── escape-sequence handling ──────────────────────────────────────────────────

class TestColorCodes:
    def test_color_sgr_is_stripped(self):
        # \x1b[1;37;44m … \x1b[0m → only the payload remains.
        assert parse(b'\x1b[1;37;44mHELLO\x1b[0m')[0] == 'HELLO'

    def test_multiple_sgr_runs(self):
        data = b'\x1b[33mA\x1b[0;1;37;44mB\x1b[mC'
        assert parse(data)[0] == 'ABC'


class TestClearScreen:
    def test_2J_drops_data_written_before_it(self):
        assert parse(b'BEFORE\x1b[2JAFTER')[0] == 'AFTER'

    def test_only_last_2J_counts(self):
        # The parser uses rfind('=ESC=[2J'), so only the final clear wins.
        assert parse(b'A\x1b[2JB\x1b[2JC')[0] == 'C'

    def test_no_2J_keeps_everything(self):
        assert parse(b'A\x1b[KB')[0] == 'AB'


class TestCursorHome:
    def test_H_resets_cursor_to_origin(self):
        # After 'first' is written, \x1b[H sends cursor home; 'second' then
        # overwrites starting at column 0. 'first' (len 5) is fully replaced
        # because 'second' (len 6) is longer.
        assert parse(b'first\x1b[Hsecond')[0] == 'second'

    def test_H_does_not_clear_other_rows(self):
        # Row 3 stays intact; row 0 is independently written after \x1b[H.
        lines = parse(b'\x1b[3;1HFIRST\x1b[Hsecond')
        assert lines[0] == 'second'
        assert lines[2] == 'FIRST'


class TestAbsolutePositioning:
    def test_y_x_H_places_cursor_at_row_and_column(self):
        # \x1b[5;3H → row 5 (index 4), column 3 (0-based 2) → 2 spaces of pad.
        assert parse(b'\x1b[5;3HHi')[4] == '  Hi'

    def test_y_x_s_is_equivalent_to_H(self):
        # The 's' (save cursor) form is parsed the same way as 'H'.
        assert parse(b'\x1b[5;3sHi')[4] == parse(b'\x1b[5;3HHi')[4]

    def test_column_1_lands_at_origin(self):
        # x=1 (1-based) → column 0 → content starts at the beginning of the row.
        assert parse(b'\x1b[2;1HA')[1] == 'A'

    def test_y_beyond_screen_is_clamped_to_last_row(self):
        # y=100 → clamped to row index 23 (the last row).
        assert parse(b'\x1b[100;1HX')[23] == 'X'


class TestEraseToEndOfLine:
    def test_K_truncates_from_cursor_to_end_of_line(self):
        # 'helloworld' → move to col 6 (0-based 5) → \x1b[K keeps 'hello'.
        assert parse(b'helloworld\x1b[1;6H\x1b[K')[0] == 'hello'

    def test_K_at_column_zero_erases_whole_row(self):
        # 'preset' → \x1b[H (cursor home to col 0) → \x1b[K clears the row
        # → write 'abc' starting at col 0 → row is 'abc'.
        assert parse(b'preset\x1b[H\x1b[Kabc')[0] == 'abc'

    def test_K_at_column_zero_clears_screen_length(self):
        # After K erases at col 0, subsequent writes don't need padding —
        # the row length is zero, so 'abc' appends cleanly with no leading gap.
        assert parse(b'preset\x1b[1;1H\x1b[Kabc')[0] == 'abc'


class TestBackspaceCollapse:
    def test_space_backspace_pair_is_removed(self):
        # PTT often emits ' \x08' to "erase forward"; the parser collapses it.
        assert parse(b'abc \x08def')[0] == 'abcdef'

    def test_multiple_space_backspace_pairs(self):
        # Each ' \x08' pair eats one character of preceding whitespace.
        assert parse(b'a    \x08\x08\x08\x08b')[0] == 'ab'


class TestNewlines:
    def test_lf_advances_to_next_row(self):
        lines = parse(b'line1\nline2')
        assert lines[0] == 'line1'
        assert lines[1] == 'line2'

    def test_cr_is_stripped(self):
        # Bare \r is unconditionally removed; CRLF becomes LF.
        assert parse(b'a\rb')[0] == 'ab'
        lines = parse(b'line1\r\nline2')
        assert lines[0] == 'line1'
        assert lines[1] == 'line2'

    def test_newline_resets_column_to_zero(self):
        # After \x1b[5;3H 'Hi', the LF should reset cursor_x to 0 → 'Next'
        # lands at column 0 on row 5 (index 5) with no leading padding.
        lines = parse(b'\x1b[5;3HHi\nNext')
        assert lines[4] == '  Hi'
        assert lines[5] == 'Next'


# ── encoding & wide characters ────────────────────────────────────────────────

class TestEncoding:
    def test_utf8_chinese_round_trip(self):
        assert parse('中文'.encode('utf-8'))[0] == '中文'

    def test_big5_uao_decoding(self):
        # The big5-uao codec is registered by uao.register_uao() on import.
        assert parse('中文'.encode('big5'), encoding='big5-uao')[0] == '中文'

    def test_invalid_bytes_replaced_not_raised(self):
        # errors='replace' is used during decode; bad bytes do not raise.
        lines = parse(b'A\xffB')
        # The replacement char is encoding-dependent; just assert no crash
        # and that the surrounding ASCII survives.
        assert lines[0].startswith('A')
        assert lines[0].endswith('B')


# ── replace-mode (cursor lands inside existing text) ──────────────────────────

class TestReplaceMode:
    def test_writing_inside_existing_line_overwrites_in_place(self):
        # 'helloworld' → cursor to col 1 (0-based) via \x1b[1;2H → 'X' overlays
        # the second character: 'h' + 'X' + 'lloworld'.
        assert parse(b'helloworld\x1b[1;2HX')[0] == 'hXlloworld'

    def test_replace_preserves_trailing_text(self):
        # 'XY' at col 1 overlays two chars, keeps the rest.
        assert parse(b'helloworld\x1b[1;2HXY')[0] == 'hXYloworld'

    def test_replace_advances_cursor_for_subsequent_writes(self):
        # After overwriting 'X' at col 1, the next write should continue from
        # col 2, not stay at col 1 — verifies the replace-mode cursor advance.
        assert parse(b'helloworld\x1b[1;2HXY')[0] == 'hXYloworld'

    def test_wide_chars_count_as_two_cells(self):
        # ※ is East Asian Ambiguous → treated as 2 cells. After writing ※,
        # positioning to col 3 (0-based 2) requires no padding.
        assert parse(b'\x1b[1;1H\xe2\x80\xbb\x1b[1;3H!')[0] == '※!'


# ── wide-char field alignment (the actual bug we hit on real PTT data) ────────

class TestWideCharFieldAlignment:
    """When PTT writes a wide-char run and then jumps the cursor forward to a
    later column, the parser must pad with (target_col - current_cells) spaces
    — counting cells, not encoded bytes. This was the headline bug fixed by
    the cursor-tracking overhaul; pin it down so future regressions surface
    in unit tests rather than only via fixture diffs."""

    def test_wide_chars_advance_cursor_in_cells_not_bytes(self):
        # Layout: 30 cells of header, then '[軟工]' (5 cells) + ' ' + 25 cells
        # of '成為全宇宙のNo.1吧' content, then jump to col 65 → 9 spaces of
        # padding before '24'. This is the exact byte pattern PTT sends for
        # board-listing rows with CJK titles.
        body = '[軟工] 成為全宇宙のNo.1吧'
        data = (
            b'\x1b[5;31H' + body.encode('utf-8')
            + b'\x1b[5;65H24'
        )
        line = parse(data)[4]
        # cols 0-29 padded, body at 30-54 (25 cells), 9 spaces, '24' at 64-65
        assert line.endswith('吧         24'), f'got {line!r}'

    def test_back_to_back_wide_chars_keep_cell_alignment(self):
        # Two wide chars then a positioning jump that lands at exactly the
        # cells-consumed boundary → no padding needed, no replace mode.
        # '※' (2 cells) at col 0 → cursor at col 2 → jump to col 3 → ' xx'.
        data = b'\x1b[1;1H\xe2\x80\xbb\x1b[1;3H xx'
        assert parse(data)[0] == '※ xx'

    def test_space_backspace_collapse_with_wide_char(self):
        # PTT's actual byte pattern for emitting a wide char in a column slot:
        # send two spaces (the visual width), two backspaces (to step back),
        # then the wide char itself. The parser must collapse the ' \x08' pairs
        # and place the wide char at column 0.
        # Equivalent to writing '◎' at column 0 of an empty line.
        data = b'  \x08\x08\xe2\x97\x8e tail'
        assert parse(data)[0] == '◎ tail'

    def test_ptt_post_meta_line_layout(self):
        # Exact byte pattern observed for the '※ 發信站' line of a post:
        # position to row 10 col 1, ' \x08\x08' (space pad + backspace)
        # collapses to empty, write '※' (2 cells) → cursor at col 2,
        # re-position to row 10 col 3 → cursor at cell 2 (matches), no pad,
        # write ' 發信站: x'. Expected: '※ 發信站: x' (single space).
        data = (
            b'\x1b[10;1H  \x08\x08\xe2\x80\xbb'      # row 10 col 1, then ※
            b'\x1b[10;3H \xe7\x99\xbc\xe4\xbf\xa1\xe7\xab\x99: x'  # row 10 col 3
        )
        assert parse(data)[9] == '※ 發信站: x'

    def test_box_drawing_horizontal_treated_as_two_cells(self):
        # '─' (U+2500) is Ambiguous-width — PTT uses long runs of it as
        # post-content separators. With cell tracking, three positioned
        # writes pack into a tight string (no gap-fill spaces between).
        # Mirrors the screens.Target.content_start update.
        data = (
            b'\x1b[1;1H\xe2\x94\x80'   # ─ at col 1 → cursor at cell 2
            + b'\x1b[1;3H\xe2\x94\x80'  # ─ at col 3 → cursor at cell 4
            + b'\x1b[1;5H\xe2\x94\x80'  # ─ at col 5 → cursor at cell 6
        )
        assert parse(data)[0] == '───'


# ── real PTT byte streams ─────────────────────────────────────────────────────

FIXTURE_NAMES = [
    'main_menu',
    'board_info_python',
    'post_full',
    'post_listing',
    'user_profile',
    'favourite_boards',
]


class TestRealFixtures:
    """Replay captured PTT byte buffers through VT100Parser.

    Fixtures are produced by tests/capture_vt100_fixtures.py against a live
    PTT account. The assertions below pin down stable structural content
    (labels, separators, banner text) rather than volatile bits such as
    timestamps, post counts, or user activity numbers.
    """

    @pytest.mark.parametrize('name', FIXTURE_NAMES)
    def test_parses_to_24_rows(self, name):
        # Every captured buffer must decode to exactly 24 rows joined by \n.
        data, encoding = load_fixture(name)
        screen = VT100Parser(data, encoding).screen
        assert isinstance(screen, str)
        assert screen.count('\n') == 23

    def test_main_menu_contains_menu_options_and_banner(self):
        lines = parse_fixture('main_menu')
        text = '\n'.join(lines)
        # The header and footer banners of the PTT main menu.
        assert '【主功能表】' in lines[0]
        assert '批踢踢實業坊' in lines[0]
        # All ten lettered menu options should appear, each on its own row.
        for option in ('(A)nnounce', '(F)avorite', '(C)lass', '(M)ail',
                       '(T)alk', '(U)ser', '(X)yz', '(P)lay',
                       '(N)amelist', '(G)oodbye'):
            assert option in text, f'missing menu option {option!r}'
        # Status bar at the bottom: online count + identity + pager state.
        assert ', 我是CodingMan' in lines[23]
        assert '[呼叫器]' in lines[23]

    def test_board_info_python_layout(self):
        lines = parse_fixture('board_info_python')
        text = '\n'.join(lines)
        # Header carries the board name.
        assert 'Python 程式語言' in lines[0]
        assert '看板《Python》' in lines[0]
        # Action hints row.
        assert '[i]看板資訊/設定' in lines[1]
        # Settings panel — column letters are positionally significant.
        assert '《Python》看板設定' in lines[3]
        assert 'b - 中文敘述' in text
        assert 'h - 公開狀態' in text
        assert '允許 未滿十八歲進入' in text

    def test_post_full_shows_metadata_and_comments(self):
        lines = parse_fixture('post_full')
        text = '\n'.join(lines)
        # Origin and URL metadata follow the '--' content separator.
        assert any(line.startswith('--') for line in lines)
        assert '※ 發信站: 批踢踢實業坊(ptt.cc)' in text
        assert '※ 文章網址: https://www.ptt.cc/bbs/Python/' in text
        # Each push/arrow comment starts with one of these glyphs.
        comment_lines = [
            line for line in lines
            if line.startswith('推 ') or line.startswith('→ ') or line.startswith('噓 ')
        ]
        assert len(comment_lines) >= 1, 'expected at least one comment in fixture'
        # Status bar at the bottom of a fully-read post.
        assert '(100%)' in lines[23]
        assert '(y)回應' in lines[23]
        assert '離開' in lines[23]

    def test_post_listing_has_table_header_and_rows(self):
        lines = parse_fixture('post_listing')
        text = '\n'.join(lines)
        assert '看板《Python》' in lines[0]
        # Column header row.
        assert '編號' in lines[2] and '日 期' in lines[2] and '作  者' in lines[2]
        # Body rows start with an index number (right-aligned, leading spaces).
        body_rows = [line for line in lines[3:20] if line.strip()]
        assert len(body_rows) >= 3
        for line in body_rows:
            # First non-space token of a body row should be an integer index.
            first_token = line.split()[0]
            assert first_token.isdigit(), f'expected index, got {first_token!r}'

    def test_user_profile_field_labels(self):
        lines = parse_fixture('user_profile')
        text = '\n'.join(lines)
        assert '【 查詢網友 】' in lines[0]
        # Profile uses fullwidth bracket labels.
        for label in ('《ＩＤ暱稱》', '《經濟狀況》', '《登入次數》',
                      '《有效文章》', '《上次上站》', '《 五子棋 》'):
            assert label in text, f'missing label {label!r}'
        # The queried ID must show up adjacent to the ID label.
        assert 'CodingMan' in lines[1]

    def test_favourite_boards_table(self):
        lines = parse_fixture('favourite_boards')
        text = '\n'.join(lines)
        assert '【看板列表】' in lines[0]
        assert '批踢踢實業坊' in lines[0]
        # Table header columns.
        assert '編號' in lines[2] and '看  板' in lines[2] and '類別' in lines[2]
        # Footer action hints.
        assert '增加看板' in lines[23]
