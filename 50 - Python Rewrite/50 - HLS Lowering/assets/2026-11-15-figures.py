"""Generate the figures for the 15 November weekly update (compiler efficiency).

Static SVG on a fixed light card, so they read on a light or a dark page.
Colours (validated together, first three slots of the reference palette):
today's compiler output = blue, the staff's handwritten HLS = orange, the
compiler prototype = aqua. Every line is labelled directly, and every figure
has a table twin on the page.

Numbers: spatial-py, docs/evidence/hardware-performance-planning/vendor-2026-11-15/README.md
(kit simulation, 15 November) and the prover prototype's corpus table.
"""
import math
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

W = 760
SURF, INK, INK2, MUTED, GRID, AXIS = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
BLUE, BLUE_L, ORANGE, AQUA, NEUTRAL = '#2a78d6', '#86b6ef', '#eb6834', '#1baf7a', '#c3c2b7'
FONT = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=12, fill=INK, weight=400, anchor='start', halo=False):
    extra = f' paint-order="stroke" stroke="{SURF}" stroke-width="4" stroke-linejoin="round"' if halo else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def rich(x, y, parts, size=12, anchor='start'):
    spans = ''.join(f'<tspan fill="{fill}" font-weight="{weight}"' + (' dx="6"' if i else '') + f'>{esc(s.strip())}</tspan>'
                    for i, (s, fill, weight) in enumerate(parts))
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'style="font-variant-numeric: tabular-nums">{spans}</text>')


def frame(h, title, subtitle, desc, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">{esc(title)}</title>
<desc id="d">{esc(desc)}</desc>
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="8" fill="{SURF}" stroke="rgba(11,11,11,0.10)"/>
{text(24, 34, title, 15, INK, 600)}
{text(24, 54, subtitle, 12, INK2)}
{body}
</svg>
'''


def fmt(v):
    return f'{v:,}'


# ---------------------------------------------------------------- figure 1: cycles against size
def scaling():
    x0, x1, y_top, y_bot = 118, 470, 84, 372
    sizes = [32, 256, 1024]
    lo, hi = math.log10(50), math.log10(5000)
    sx = lambda n: x0 + (x1 - x0) * (math.log2(n) - 5) / 5
    sy = lambda v: y_bot - (y_bot - y_top) * (math.log10(v) - lo) / (hi - lo)
    b = []
    for t in [50, 100, 200, 500, 1000, 2000, 5000]:
        b.append(f'<line x1="56" x2="{x1 + 14}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" stroke="{AXIS if t == 50 else GRID}" stroke-width="1"/>')
        b.append(f'<text x="48" y="{sy(t) + 4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end" '
                 f'style="font-variant-numeric: tabular-nums">{fmt(t)}</text>')
    for n in sizes:
        b.append(f'<text x="{sx(n):.1f}" y="{y_bot + 18}" font-size="11" fill="{MUTED}" text-anchor="middle" '
                 f'style="font-variant-numeric: tabular-nums">{fmt(n)}</text>')
    b.append(text((x0 + x1) / 2, y_bot + 38, 'Elements in the array (16 per tile)', 11, MUTED, anchor='middle'))
    b.append(text(24, 74, 'Compute cycles', 11, MUTED))

    series = [  # name, values, colour, line width, label y offset from the last point
        ("Today's compiler output", [294, 1198, 3910], BLUE, 2, 0),
        ('Prototype 1: check folded into a copy', [260, 692, 1858], AQUA, 2, 0),
        ('Prototype 2: checks proved away', [87, 147, 289], AQUA, 2, 0),
        ("Staff's handwritten HLS", [77, 109, 158], ORANGE, 6, 9),
        ('Prototype 3: one fused loop', [75, 108, 155], AQUA, 2, -9),
    ]
    for name, vals, colour, width, _ in series:
        pts = ' '.join(f'{sx(n):.1f},{sy(v):.1f}' for n, v in zip(sizes, vals))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
                 f'stroke-linecap="round"' + (' stroke-opacity="0.55"' if width > 2 else '') + '/>')
    for name, vals, colour, width, _ in series:
        r = 5.5 if width > 2 else 4
        for n, v in zip(sizes, vals):
            b.append(f'<circle cx="{sx(n):.1f}" cy="{sy(v):.1f}" r="{r}" fill="{colour}" stroke="{SURF}" stroke-width="2">'
                     f'<title>{esc(name)}: {fmt(v)} cycles at {fmt(n)} elements</title></circle>')
    lx = x1 + 26
    for name, vals, colour, width, dy in series:
        y = sy(vals[-1]) + 4 + dy
        b.append(f'<rect x="{lx}" y="{y - 9:.1f}" width="10" height="10" rx="2" fill="{colour}"/>')
        b.append(rich(lx + 16, y, [(fmt(vals[-1]), INK, 600), (name, INK2, 400)], 12))
    # first-point values, so the left end is readable without the table
    b.append(text(sx(32) - 11, sy(294) - 1, '294', 11, INK2, anchor='end', halo=True))
    b.append(text(sx(32) - 11, sy(260) + 11, '260', 11, INK2, anchor='end', halo=True))
    b.append(text(sx(32) - 11, sy(87) - 1, '87', 11, INK2, anchor='end', halo=True))
    b.append(text(sx(32) - 11, sy(75) + 12, '75, 77', 11, INK2, anchor='end', halo=True))
    return frame(424, 'Compute cycles as the array grows',
                 'Lab 1 Part 2 (tiled scale) in the F2 kit simulation, 15 November. Both axes are logarithmic; lower is faster.',
                 "At 32, 256 and 1,024 elements: today's compiler output takes 294, 1,198 and 3,910 cycles; the prototype "
                 'with the completion check folded into the write-back 260, 692 and 1,858; the prototype with checks proved '
                 "and staged copies 87, 147 and 289; the prototype's fused loop 75, 108 and 155; the staff's handwritten HLS "
                 '77, 109 and 158.', '\n'.join(b))


# ---------------------------------------------------------------- figure 2: where today's design spends its time
def breakdown():
    x0, x1, y, h = 24, 736, 96, 30
    parts = [('Final check that every output was written', 2051, BLUE),
             ('Loop over the 64 tiles', 1110, BLUE_L),
             ('Six staged copies', 400, NEUTRAL),
             ('Other', 64, '#e1e0d9')]
    total = sum(p[1] for p in parts)
    assert total == 3625
    b, pos = [], 0
    for i, (name, v, fill) in enumerate(parts):
        a = x0 + (x1 - x0) * pos / total + (1 if i else 0)
        z = x0 + (x1 - x0) * (pos + v) / total - 1
        b.append(f'<rect x="{a:.1f}" y="{y}" width="{z - a:.1f}" height="{h}" rx="3" fill="{fill}">'
                 f'<title>{esc(name)}: about {fmt(v)} cycles</title></rect>')
        if v >= 300:
            b.append(rich(a + 2, y + h + 20, [(fmt(v) if v != 400 else 'about 400', INK, 600)], 12))
            b.append(text(a + 2, y + h + 37, name, 11, INK2))
        pos += v
    b.append(text(x1, y - 10, 'Estimated cycles, 3,625 in all', 11, MUTED, anchor='end'))
    b.append(text(24, y + h + 68, 'The check visits one element every two cycles: 1,024 elements, 2,051 cycles. '
                  'At 32 elements it was 34 of 129.', 11, INK2))
    return frame(214, "Where today's design spends its time at 1,024 elements",
                 "Synthesis estimate for today's compiler output; the kit simulation measured 3,910 cycles.",
                 'Of 3,625 estimated cycles, the final check that every output cell was written takes 2,051, the loop over '
                 'the 64 tiles 1,110, the six staged copies about 400, and the rest 64.', '\n'.join(b))


# ---------------------------------------------------------------- figure 3: checks decided before the run
def census():
    x0, x1, h = 232, 736, 26
    rows = [('All 104 test programs', '1,662 ways a memory access can fail', [1318, 97, 247], 104),
            ('The three Lab 1 programs', '43 ways a memory access can fail', [39, 4, 0], 198)]
    kinds = [('Proved: cannot fail in any run', BLUE), ('Cannot fail once the host confirms the inputs are set', BLUE_L),
             ('Left as a hardware check', NEUTRAL)]
    b = []
    lx = 24
    for (name, fill), w in zip(kinds, [208, 330, 0]):
        b.append(f'<rect x="{lx}" y="71" width="10" height="10" rx="2" fill="{fill}"/>')
        b.append(text(lx + 16, 80, name, 11, INK2))
        lx += w
    for label, sub, vals, y in rows:
        total = sum(vals)
        b.append(text(24, y + 12, label, 13, INK, 600))
        b.append(text(24, y + 28, sub, 11, INK2))
        pos = 0
        for i, (v, (name, fill)) in enumerate(zip(vals, kinds)):
            if not v:
                continue
            a = x0 + (x1 - x0) * pos / total + (1 if pos else 0)
            z = x0 + (x1 - x0) * (pos + v) / total - 1
            b.append(f'<rect x="{a:.1f}" y="{y}" width="{z - a:.1f}" height="{h}" rx="3" fill="{fill}">'
                     f'<title>{esc(name)}: {fmt(v)} of {fmt(total)}</title></rect>')
            pct = f'{100 * v / total:.0f} %'
            anchor, tx = ('start', a + 2) if i < 2 else ('end', z)
            if i == 1 and (z - a) < 60:
                anchor, tx = 'middle', (a + z) / 2
            b.append(rich(tx, y + h + 18, [(fmt(v), INK, 600), (pct, INK2, 400)], 12, anchor))
            pos += v
    b.append(text(232, 198 + 26 + 18 + 22, 'No Lab 1 check is left for the hardware.', 11, INK2))
    return frame(284, 'How many memory checks can be decided before the run',
                 'A throwaway prover over the checked program, 15 November. No wrong proof in 1,120 reference runs.',
                 'Across 104 test programs, 1,318 of 1,662 possible memory failures were proved impossible, 97 are impossible '
                 'when the host confirms the inputs are fully set, and 247 remain as hardware checks. For the three Lab 1 '
                 'programs: 39 of 43 proved, 4 by the host fact, none left.', '\n'.join(b))


for name, fn in [('2026-11-15-scaling.svg', scaling), ('2026-11-15-breakdown.svg', breakdown),
                 ('2026-11-15-census.svg', census)]:
    (OUT / name).write_text(fn())
    print('wrote', OUT / name)
