#!/usr/bin/env python3
"""Regenerate docs/_static/star_history.svg from GitHub stargazer data.

We self-host this chart instead of embedding star-history.com's live SVG,
whose endpoint reliably times out for this repo (HTTP 500). Run whenever you
want the README chart refreshed:

    python3 scripts/gen_star_history.py          # fetch via gh, write SVG
    python3 scripts/gen_star_history.py in.txt out.svg   # from a saved file

Needs the `gh` CLI authenticated (for the fetch mode). ponytail: hand-rolled
SVG, no charting lib — a few hundred points is trivial.
"""
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = "PyPtt/PyPtt"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "_static", "star_history.svg")

W, H = 800, 520
L, R, T, B = 66, 32, 52, 54          # margins
PW, PH = W - L - R, H - T - B        # plot area
LINE = "#e91e63"


def fetch_stamps():
    """All `starred_at` timestamps, ascending, via the gh CLI."""
    out = subprocess.check_output([
        "gh", "api", f"repos/{REPO}/stargazers",
        "-H", "Accept: application/vnd.github.star+json",
        "--paginate", "--jq", ".[].starred_at",
    ], text=True)
    return [l.strip() for l in out.splitlines() if l.strip()]


def epoch(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc).timestamp()


def render(stamps):
    stamps = sorted(epoch(t) for t in stamps)
    n = len(stamps)
    pts = [(t, i + 1) for i, t in enumerate(stamps)]           # cumulative

    tmin = stamps[0]
    tmax = datetime.now(timezone.utc).timestamp()              # extend to today
    ymax = ((n // 200) + 1) * 200                              # nice round top

    def px(t): return L + (t - tmin) / (tmax - tmin) * PW
    def py(c): return T + PH - (c / ymax) * PH

    y0 = datetime.fromtimestamp(tmin, timezone.utc).year + 1
    y1 = datetime.fromtimestamp(tmax, timezone.utc).year
    xticks = [(px(datetime(y, 1, 1, tzinfo=timezone.utc).timestamp()), str(y))
              for y in range(y0, y1 + 1)]
    yticks = list(range(0, ymax + 1, 200))

    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" font-family="-apple-system,BlinkMacSystemFont,'
      f'Segoe UI,Helvetica,Arial,sans-serif">')
    a(f'<defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{LINE}" stop-opacity="0.18"/>'
      f'<stop offset="1" stop-color="{LINE}" stop-opacity="0"/>'
      f'</linearGradient></defs>')
    a(f'<rect x="0" y="0" width="{W}" height="{H}" rx="8" fill="#ffffff"/>')
    for yt in yticks:
        y = py(yt)
        a(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" '
          f'stroke="#eaeef2" stroke-width="1"/>')
        a(f'<text x="{L-10}" y="{y+4:.1f}" text-anchor="end" font-size="12" '
          f'fill="#57606a">{yt}</text>')
    for x, lbl in xticks:
        a(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{T+PH}" '
          f'stroke="#f2f4f6" stroke-width="1"/>')
        a(f'<text x="{x:.1f}" y="{T+PH+22}" text-anchor="middle" font-size="12" '
          f'fill="#57606a">{lbl}</text>')
    a(f'<line x1="{L}" y1="{T+PH}" x2="{W-R}" y2="{T+PH}" stroke="#d0d7de"/>')
    a(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+PH}" stroke="#d0d7de"/>')
    poly = " ".join(f"{px(t):.1f},{py(c):.1f}" for t, c in pts)
    fx, lx = px(pts[0][0]), px(pts[-1][0])
    a(f'<path d="M{fx:.1f},{T+PH} L{poly.replace(" ", " L")} L{lx:.1f},{T+PH} Z" '
      f'fill="url(#fill)"/>')
    a(f'<polyline points="{poly}" fill="none" stroke="{LINE}" '
      f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    a(f'<text x="{L-56}" y="30" font-size="17" font-weight="700" '
      f'fill="#1f2328">Star History</text>')
    a(f'<circle cx="{W-R-118}" cy="26" r="5" fill="{LINE}"/>')
    a(f'<text x="{W-R-106}" y="30" font-size="13" fill="#1f2328">{REPO}</text>')
    a('</svg>')
    svg = "\n".join(s)

    # sanity: curve ends at the star count, stays inside the viewport
    assert pts[-1][1] == n
    assert L <= px(pts[-1][0]) <= W - R and T <= py(n) <= T + PH
    return svg, n


def main(argv):
    if len(argv) >= 2:
        with open(argv[0]) as f:
            stamps = [l.strip() for l in f if l.strip()]
        dst = argv[1]
    else:
        stamps = fetch_stamps()
        dst = OUT
    svg, n = render(stamps)
    with open(dst, "w") as f:
        f.write(svg)
    print(f"wrote {dst}: {n} stars, {len(svg)} bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
