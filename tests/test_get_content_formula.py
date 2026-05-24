"""
Unit tests for the get_content formula in PyPtt/_api_util.py.

The "dark magical formula" (lines 106-157) assembles a multi-page PTT post by
deciding how many lines at the bottom of each screen page are NEW content.
PTT's status bar encodes the currently visible article-line range as 'a~b'.
The formula tracks changes in a and b between successive pages to extract new
content without duplication or gaps.

How PTT scrolling works (from live observation)
------------------------------------------------
- PTT BBS terminal: 24 display rows = 23 content rows + 1 status bar.
- Normal 'down': b advances by 1 (sometimes 2) per press.
- 'right' (used after the push separator): b can jump by up to 22.
- Stagnation (駐足現象): b does not advance between pages. Happens when
  one article line wraps to 2 display rows in the 80-column terminal —
  the second display row is revealed but it still belongs to the same
  article line, so PTT does not increment b.
- Each page scroll reveals new article lines at the BOTTOM of the screen.
  Lines already seen scroll UP and eventually off the top.

Critical mock contract
----------------------
Since lines[-get_line_b:] must return the NEW content:
  → content lines must be placed at the BOTTOM of the 23-row screen.
  → Empty padding goes at the TOP.

Formula paths
-------------
- first_page: whole screen stored verbatim.
- Type1 (get_line_b > 0): take last get_line_b lines.
  try_line: also prepend lines[-(get_line_b+1)] if it is not already the
  last captured line (bridges gaps at page boundaries).
- Type2 (b stagnant, a advanced): take last (a_temp - prev_a) lines.
  Stores (b+1 → count) in stop_dict for resolution when the next page
  begins at a_temp == b+1.
- Type3 (both stagnant): take the whole screen.
- stop_dict resolution: when a_temp matches a stored key, take that many
  lines instead of the normal Type1 result.
- control_code: no 'a~b' in status bar → take only lines[-1].

Bug fixed in this session
--------------------------
IndexError at lines[-(get_line_b+1)] when get_line_b >= len(lines).
The try_line path is now guarded with `get_line_b + 1 <= len(lines)`.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from PyPtt import _api_util
from PyPtt.screens import Target as ScreenTarget

PTT_SCREEN_ROWS = 23  # content rows per page (24-row terminal minus status bar)


# ── mock helpers ──────────────────────────────────────────────────────────────

def _screen(content_lines: list[str], a: int, b: int, last: bool = False) -> str:
    """
    Build a realistic PTT screen with content at the BOTTOM.

    content_lines: the article lines visible on this page (positions a..b).
    The remaining rows (PTT_SCREEN_ROWS - len(content_lines)) are filled
    with empty strings at the TOP, mimicking the header / older-content rows
    that have scrolled partially off-screen.
    """
    n = len(content_lines)
    pad = max(0, PTT_SCREEN_ROWS - n)
    rows = [''] * pad + content_lines  # content at the BOTTOM
    pct = '100%' if last else ' 50%'
    status = (f'  瀏覽 第 1/3 頁 ({pct})'
              f'  目前顯示: 第 {a:02d}~{b:02d} 行  (h)說明(←)離開 ')
    return '\n'.join(rows + [status])


def _ctrl_screen(content_lines: list[str]) -> str:
    """Control-code screen: no 'a~b' indicator; formula takes lines[-1]."""
    pad = max(0, PTT_SCREEN_ROWS - len(content_lines))
    rows = [''] * pad + content_lines  # last content line ends up at lines[-1]
    return '\n'.join(rows + ['★ 互動動畫播放中'])


def _build_api(page_specs: list[tuple]) -> MagicMock:
    """
    Return a mock api whose connect_core replays page_specs in order.

    page_specs: list of (screen_str, target_index)
      1 → PostEnd (last page, loop exits)
      2 → InPost  (normal page, loop continues)
    """
    api = MagicMock()
    api.Unconfirmed = False
    api.connect_core.send.side_effect = [idx for _, idx in page_specs]
    api.connect_core.get_screen_queue.side_effect = [
        [s] for s, _ in page_specs
    ]
    return api


def _lines(content: str) -> list[str]:
    """Split assembled content on newlines for exact-match counting."""
    return content.split('\n')


# ── single-page posts ─────────────────────────────────────────────────────────

class TestSinglePage:
    def test_all_content_lines_present(self):
        post = ['header', ScreenTarget.content_start, 'body_A', 'body_B']
        api = _build_api([(_screen(post, 1, 4, last=True), 1)])
        content, has_ctrl = _api_util.get_content(api)
        assert has_ctrl is False
        assert content is not None
        for ln in post:
            assert ln in content

    def test_returns_none_for_no_content_post(self):
        api = _build_api([(_screen(['◆ 此文章無內容', '請按任意鍵繼續'], 1, 2), 3)])
        content, _ = _api_util.get_content(api)
        assert content is None


# ── standard overlapping 2-page post ──────────────────────────────────────────

class TestTwoPagePost:
    """Most common PTT pattern: page 2 overlaps with the tail of page 1."""

    def test_all_lines_present(self):
        # 12 lines per page, 3 new lines on page 2
        article = [f'LINE_{i:03d}' for i in range(16)]
        s1 = _screen(article[:12], 1, 12)         # shows lines 0-11
        s2 = _screen(article[4:16], 4, 15, last=True)  # shows lines 4-15 (new: 12-15)
        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)

        result = _lines(content)
        for ln in article:
            assert ln in result, f'{ln!r} missing'

    def test_no_duplicates_in_overlap_zone(self):
        article = [f'DUP_{i:03d}' for i in range(16)]
        s1 = _screen(article[:12], 1, 12)
        s2 = _screen(article[4:16], 4, 15, last=True)
        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)

        result = _lines(content)
        for i in range(4, 12):   # overlap zone
            count = result.count(f'DUP_{i:03d}')
            assert count == 1, f'DUP_{i:03d} appears {count} times'

    def test_non_overlapping_pages_no_crash(self):
        """Non-overlapping pages: no IndexError after the boundary fix."""
        article_p1 = [f'P1_{i:02d}' for i in range(12)]
        article_p2 = [f'P2_{i:02d}' for i in range(12)]
        s1 = _screen(article_p1, 1, 12)
        s2 = _screen(article_p2, 13, 24, last=True)  # get_line_b=12, no overlap
        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)  # must not raise IndexError
        assert content is not None
        result = _lines(content)
        for ln in article_p1 + article_p2:
            assert ln in result


# ── slow 1-line-per-scroll (observed real PTT behaviour) ─────────────────────

class TestSlowScroll:
    """
    Live observation: each 'down' press moves b by exactly 1.
    A 68-line post took 50 iterations.
    """

    @staticmethod
    def _build_specs(article: list[str], display: int = 22) -> list[tuple]:
        """Simulate PTT's 1-line-at-a-time scroll through `article`."""
        n = len(article)
        specs = []
        prev_b = 0

        a, b = 1, min(display, n)
        while True:
            visible = article[a - 1: b]
            is_last = (b >= n)
            specs.append((_screen(visible, a, b, last=is_last), 1 if is_last else 2))
            if is_last:
                break
            a += 1
            b = min(b + 1, n)

        return specs

    def test_all_lines_present(self):
        article = [f'ART_{i:03d}_END' for i in range(30)]
        api = _build_api(self._build_specs(article))
        content, _ = _api_util.get_content(api)
        result = _lines(content)
        for ln in article:
            assert ln in result, f'{ln!r} missing'

    def test_no_duplicates(self):
        article = [f'UNIQ_{i:03d}_END' for i in range(30)]
        api = _build_api(self._build_specs(article))
        content, _ = _api_util.get_content(api)
        result = _lines(content)
        for ln in article:
            count = result.count(ln)
            assert count == 1, f'{ln!r} appears {count} times'

    def test_last_page_multi_line_jump(self):
        """After push separator, 'right' can advance b by many lines at once."""
        article = [f'JMP_{i:02d}' for i in range(20)]
        s1 = _screen(article[:12], 1, 12)
        # b jumps from 12 → 19 (delta=7) — simulates the 'right' page-forward
        s2 = _screen(article[5:20], 6, 19, last=True)
        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)
        result = _lines(content)
        for ln in article:
            assert ln in result, f'{ln!r} missing after multi-line jump'


# ── stagnation (駐足現象) ──────────────────────────────────────────────────────

class TestStagnation:
    """
    Stagnation: b does not advance between consecutive pages.
    Occurs when an article line wraps to 2 display rows in PTT's 80-column
    terminal — scrolling one display row reveals the second half of the same
    article line, so b stays the same.
    """

    def test_type2_stagnation_then_recovery(self):
        """b stays at 10, a advances → Type2 (take get_line_a lines from bottom)."""
        article = [f'ST2_{i:02d}' for i in range(12)]
        s1 = _screen(article[:10], 1, 10)         # a=1, b=10
        s2 = _screen(article[1:11], 2, 10)         # a=2, b=10 → stagnation
        s3 = _screen(article[2:12], 3, 11, last=True)  # a=3, b=11 → recovery

        api = _build_api([(s1, 2), (s2, 2), (s3, 1)])
        content, _ = _api_util.get_content(api)

        result = _lines(content)
        # All 12 article lines must appear
        for ln in article:
            assert ln in result, f'{ln!r} missing after stagnation/recovery'

    def test_type3_both_stuck(self):
        """Both a and b unchanged → Type3: take all screen lines."""
        article = [f'ST3_{i:02d}' for i in range(20)]
        s1 = _screen(article[:10], 5, 20)
        s2 = _screen(article[:10], 5, 20, last=True)  # a and b both unchanged

        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)
        assert content is not None

    def test_stop_dict_resolution(self):
        """
        Stagnation at b=10 stores stop_dict[11]=2.
        When the next page has a_temp=11, those 2 lines are taken instead of
        the normal Type1 result, capturing the "missed" wrap line.
        """
        article = [f'SD_{i:02d}' for i in range(25)]
        s1 = _screen(article[:10], 1, 10)        # a=1, b=10 (first_page)
        s2 = _screen(article[1:11], 2, 10)        # stagnation: a=2, b=10
        # Resolution: a_temp=11 matches stop_dict key (prev_b+1=11)
        s3 = _screen(article[10:22], 11, 21, last=True)

        api = _build_api([(s1, 2), (s2, 2), (s3, 1)])
        content, _ = _api_util.get_content(api)
        result = _lines(content)
        # Last 2 lines of s3 must be in result (stop_dict resolution takes 2)
        assert 'SD_20' in result
        assert 'SD_21' in result


# ── try_line boundary: IndexError fix ─────────────────────────────────────────

class TestTryLineBoundaryFix:
    """
    Bug fixed: lines[-(get_line_b+1)] raised IndexError when
    get_line_b >= len(lines).  The guard `get_line_b + 1 <= len(lines)` now
    skips the try_line check in that case.

    Reproduction: a page with ALL 23 rows as new content (no overlap),
    so get_line_b == len(lines) == 23 → lines[-24] was IndexError.
    """

    def test_no_crash_when_get_line_b_equals_screen_height(self):
        """get_line_b == PTT_SCREEN_ROWS used to crash; should now be silent."""
        article_p1 = [f'PRE_{i:02d}' for i in range(5)]
        article_p2 = [f'POST_{i:02d}' for i in range(PTT_SCREEN_ROWS)]  # 23 new lines

        s1 = _screen(article_p1, 1, 5)
        # get_line_b = (5 + PTT_SCREEN_ROWS) - 5 = 23 == len(lines)
        s2 = _screen(article_p2, 6, 5 + PTT_SCREEN_ROWS, last=True)

        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)   # must not raise IndexError
        assert content is not None

    def test_content_captured_correctly_at_boundary(self):
        """When try_line is skipped, Type1 still extracts the correct lines."""
        article_p1 = [f'PRE_{i:02d}' for i in range(5)]
        article_p2 = [f'POST_{i:02d}' for i in range(PTT_SCREEN_ROWS)]

        s1 = _screen(article_p1, 1, 5)
        s2 = _screen(article_p2, 6, 5 + PTT_SCREEN_ROWS, last=True)

        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)
        result = _lines(content)

        # All page-2 lines must be in the result
        for ln in article_p2:
            assert ln in result, f'{ln!r} missing when try_line boundary skipped'


# ── control-code pages ────────────────────────────────────────────────────────

class TestControlCode:
    """
    Control-code pages (ANSI animation, special frames) have no 'a~b' in the
    status bar.  Formula response: set has_control_code=True, capture lines[-1].
    """

    def test_sets_has_control_code_flag(self):
        s1 = _screen([f'CTRL_{i}' for i in range(10)], 1, 4)
        s2 = _ctrl_screen(['anim_frame', 'CTRL_CAPTURED'])
        s3 = _screen([f'CTRL_{i}' for i in range(10)], 2, 5, last=True)

        api = _build_api([(s1, 2), (s2, 2), (s3, 1)])
        _, has_ctrl = _api_util.get_content(api)
        assert has_ctrl is True

    def test_captures_last_line_of_ctrl_screen(self):
        """The last content row of the control-code screen is captured."""
        s1 = _screen([f'X_{i}' for i in range(10)], 1, 4)
        # Build ctrl screen manually: 22 empty rows + CTRL_LAST + status
        ctrl_rows = [''] * 22 + ['CTRL_LAST']
        s2 = '\n'.join(ctrl_rows + ['★ 互動動畫播放中'])
        s3 = _screen([f'X_{i}' for i in range(10)], 2, 5, last=True)

        api = _build_api([(s1, 2), (s2, 2), (s3, 1)])
        content, _ = _api_util.get_content(api)
        assert 'CTRL_LAST' in content

    def test_transition_after_ctrl_takes_one_new_line(self):
        """
        After a control-code page, the formula uses prev (a-1, b-1) as a proxy
        for the previous page's counters: get_line_b = b_temp - (b_temp-1) = 1.
        Only 1 new line is extracted from the page that follows.
        """
        article = [f'POST_CTRL_{i:02d}' for i in range(20)]
        s1 = _screen(article[:5], 1, 5)
        s2 = _ctrl_screen(['animation'])
        s3 = _screen(article[1:10], 2, 9, last=True)

        api = _build_api([(s1, 2), (s2, 2), (s3, 1)])
        content, _ = _api_util.get_content(api)
        # The last line of s3 should be present
        assert 'POST_CTRL_09' in content


# ── doubling heuristic ────────────────────────────────────────────────────────

class TestDoublingHeuristic:
    """
    On the last page, if all get_line_b new lines are empty strings, the
    formula doubles the count: lines[-(get_line_b*2):] instead of lines[-get_line_b:].

    Condition: index==1 AND len('\n'.join(lines[-k:])) == k-1,
    which holds exactly when all k lines are '' (empty).
    """

    def test_no_doubling_for_non_empty_content(self):
        article = [f'DBL_{i:02d}' for i in range(15)]
        s1 = _screen(article[:12], 1, 12)
        s2 = _screen(article[9:15], 10, 15, last=True)  # get_line_b=3, non-empty
        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)
        assert content is not None
        result = _lines(content)
        for ln in article:
            assert ln in result

    def test_doubling_captures_extra_line(self):
        """
        get_line_b=2, both new lines empty → doubling → lines[-4:] taken.
        The non-empty lines[-3] and lines[-4] (delta and gamma) get included.
        """
        # Screen 2: 19 empty + ['gamma', 'delta', '', ''] (23 rows total)
        # lines[-1]='' lines[-2]='' → get_line_b=2 new lines are all empty
        # → doubling → lines[-4:] = ['delta', '', ''] ... actually:
        p2_content = ['alpha', 'beta', 'gamma', 'delta'] + ['', '']  # 6 content rows
        s1 = _screen(['alpha', 'beta', 'gamma'], 1, 3)
        # get_line_b = 5-3 = 2; lines[-2:] = ['',''] (empty) → doubling
        s2 = _screen(p2_content, 3, 5, last=True)

        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)
        # doubling path takes lines[-4:] which includes 'delta'
        assert 'delta' in content


# ── content_start_jump correction ─────────────────────────────────────────────

class TestContentStartJump:
    """
    Edge case: the '──────' separator appears on page 1 but not page 2, AND
    the formula produces new_content_part=='' on the last page.
    get_content then grabs one extra line as a correction.
    """

    def test_no_crash_on_separator_boundary(self):
        sep = ScreenTarget.content_start
        p1 = [sep, 'body_A', 'body_B']
        s1 = _screen(p1, 1, 3)
        p2 = ['body_B', 'body_C']
        s2 = _screen(p2, 2, 3, last=True)

        api = _build_api([(s1, 2), (s2, 1)])
        content, _ = _api_util.get_content(api)
        assert content is not None
