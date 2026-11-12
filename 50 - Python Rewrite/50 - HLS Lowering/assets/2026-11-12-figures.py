"""Generate the three figures for the first-FPGA-run study page.

Static SVG on a fixed light card, so they read on a light or a dark page.
Colours: Python Spatial = blue, handwritten HLS = orange (validated pair);
shades of blue distinguish kinds of step inside the Python Spatial design.
Every figure has a table twin on the page.
"""
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

W = 760
SURF, INK, INK2, MUTED, GRID, AXIS = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
BLUE, BLUE_L, BLUE_D, ORANGE = '#2a78d6', '#86b6ef', '#104281', '#eb6834'
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
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}">{spans}</text>'


def bar(x0, x1, y, h, fill, title=None, round_end=True):
    r = 4 if round_end and x1 - x0 > 8 else 0
    d = (f'M{x0:.1f},{y:.1f} H{x1 - r:.1f} ' + (f'A{r},{r} 0 0 1 {x1:.1f},{y + r:.1f} ' if r else '') +
         f'V{y + h - r:.1f} ' + (f'A{r},{r} 0 0 1 {x1 - r:.1f},{y + h:.1f} ' if r else '') + f'H{x0:.1f} Z')
    t = f'<title>{esc(title)}</title>' if title else ''
    return f'<path d="{d}" fill="{fill}">{t}</path>'


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


def axis(x0, x1, vmax, ticks, y_top, y_bot, label):
    sx = lambda v: x0 + (x1 - x0) * v / vmax
    out = []
    for t in ticks:
        colour = AXIS if t == 0 else GRID
        out.append(f'<line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="{y_top}" y2="{y_bot}" stroke="{colour}" stroke-width="1"/>')
        out.append(f'<text x="{sx(t):.1f}" y="{y_bot + 16}" font-size="11" fill="{MUTED}" text-anchor="middle" '
                   f'style="font-variant-numeric: tabular-nums">{t}</text>')
    out.append(text(x1, y_bot + 34, label, 11, MUTED, anchor='end'))
    return sx, '\n'.join(out)


def swatch(x, y, fill, label):
    return (f'<rect x="{x}" y="{y - 9}" width="10" height="10" rx="2" fill="{fill}"/>' + text(x + 16, y, label, 11, INK2))


# ---------------------------------------------------------------- figure 1: runs on the chip
def runs():
    x0, x1 = 170, 720
    sx, ax = axis(x0, x1, 400, [0, 100, 200, 300, 400], 72, 232, 'Compute cycles (lower is faster)')
    b = [ax]

    def dots(values, base_y, fill):
        seen = {}
        out = []
        for v in values:
            k = seen.get(v, 0)
            seen[v] = k + 1
            out.append(f'<circle cx="{sx(v):.1f}" cy="{base_y - 9.5 * k:.1f}" r="4" fill="{fill}" stroke="{SURF}" '
                       f'stroke-width="1.5"><title>{v} cycles</title></circle>')
        return '\n'.join(out)

    # handwritten HLS
    b.append(text(24, 112, 'Handwritten HLS', 13, INK, 600))
    b.append(text(24, 128, "course staff's version", 11, INK2))
    b.append(bar(x0, sx(58), 124, 14, ORANGE, 'Handwritten HLS, median 58 cycles'))
    b.append(dots([62, 58, 58, 58, 58, 62], 112, ORANGE))
    b.append(rich(sx(58) + 8, 135.5, [('58', INK, 600), ('  median', INK2, 400)]))
    b.append(text(sx(62) + 12, 99, 'four runs at 58, two at 62', 11, INK2))
    # Python Spatial
    b.append(text(24, 192, 'Python Spatial', 13, INK, 600))
    b.append(text(24, 208, 'compiled by this project', 11, INK2))
    b.append(bar(x0, sx(260), 204, 14, BLUE, 'Python Spatial, median 260 cycles'))
    b.append(dots([349, 354, 256, 260, 260, 260], 192, BLUE))
    b.append(rich(sx(260) + 8, 215.5, [('260', INK, 600), ('median, 4.5 times as many', INK2, 400)]))
    b.append(text(sx(259), 160, 'four runs at 256 to 260', 11, INK2, anchor='middle'))
    b.append(text(sx(351.5), 176, 'first two runs: 349 and 354', 11, INK2, anchor='middle'))
    return frame(280, 'Compute cycles on the FPGA, six runs each',
                 'Lab 1 tiled scale, 32 elements. Each dot is one run after a fresh image load; the bar is the median.',
                 'Handwritten HLS took 58 to 62 cycles (median 58). Python Spatial took 256 to 354 (median 260): '
                 'four runs at 256 to 260 and the first two at 349 and 354.', '\n'.join(b))


# ---------------------------------------------------------------- figure 2: timeline of one run
def timeline():
    x0, x1 = 170, 730
    sx, ax = axis(x0, x1, 280, [0, 50, 100, 150, 200, 250], 134, 262, 'Cycles from start to done')
    b = [ax]
    b.append(swatch(170, 84, BLUE, 'Memory transfer: data'))
    b.append(swatch(330, 84, BLUE_L, 'Memory transfer: "initialized" flags only'))
    b.append(swatch(590, 84, BLUE_D, 'Kernel'))

    t = 188 / 6  # one memory transfer, handshakes and waiting (estimate)
    segs = [('src data', t + 5, BLUE, '#ffffff'), ('src flags', t + 5, BLUE_L, INK), ('dst data', t + 4, BLUE, '#ffffff'),
            ('dst flags', t + 5, BLUE_L, INK), ('', 11, BLUE_D, '#ffffff'), ('check', 34, BLUE_D, '#ffffff'),
            ('dst data', t + 4, BLUE, '#ffffff'), ('dst flags', t + 4, BLUE_L, INK)]
    assert abs(sum(s[1] for s in segs) - 260) < 1e-6
    y, h = 142, 24
    pos, edges = 0.0, []
    for i, (name, length, fill, ink) in enumerate(segs):
        a, z = sx(pos) + 1, sx(pos + length) - 1
        last = i == len(segs) - 1
        title = f'{name or "multiply and control"}: about {length:.0f} cycles'
        b.append(bar(a, z, y, h, fill, title, round_end=last))
        if name:
            b.append(text((a + z) / 2, y + 16, name, 11, ink, 500, 'middle'))
        edges.append((pos, pos + length))
        pos += length
    b.append(text(sx(260) + 8, y + 16.5, '260', 12, INK, 600))

    def bracket(a, z, label):
        xa, xz = sx(a) + 1, sx(z) - 1
        return (f'<path d="M{xa:.1f},{y - 5} V{y - 10} H{xz:.1f} V{y - 5}" fill="none" stroke="{MUTED}" stroke-width="1"/>' +
                text((xa + xz) / 2, y - 15, label, 11, INK2, anchor='middle', halo=True))

    b.append(bracket(edges[0][0], edges[3][1], 'Copy in: four transfers, about 144 cycles'))
    b.append(bracket(edges[4][0], edges[5][1], 'Kernel: 45'))
    b.append(bracket(edges[6][0], edges[7][1], 'Copy out: about 71'))
    # callouts under the kernel
    mx = (sx(edges[4][0]) + sx(edges[4][1])) / 2
    cx = (sx(edges[5][0]) + sx(edges[5][1])) / 2
    b.append(f'<path d="M{mx:.1f},{y + h + 2} V{y + h + 14}" stroke="{MUTED}" stroke-width="1"/>')
    b.append(f'<path d="M{cx:.1f},{y + h + 2} V{y + h + 14}" stroke="{MUTED}" stroke-width="1"/>')
    b.append(text(mx + 4, y + h + 27, 'the multiplication: 7 cycles', 11, INK2, anchor='end', halo=True))
    b.append(text(cx - 6, y + h + 27, 'check that every output was written: 34', 11, INK2, halo=True))
    b.append(text(24, 152, 'Python Spatial', 13, INK, 600))
    b.append(text(24, 168, 'six memory transfers', 11, INK2))
    # handwritten
    y2 = 222
    b.append(bar(x0 + 1, sx(58), y2, h, ORANGE, 'Handwritten HLS: 58 cycles'))
    b.append(text((x0 + sx(58)) / 2, y2 + 16, 'one pipeline', 11, '#ffffff', 500, 'middle'))
    b.append(rich(sx(58) + 8, y2 + 16.5, [('58', INK, 600), ('  read, multiply and write overlap', INK2, 400)]))
    b.append(text(24, 232, 'Handwritten HLS', 13, INK, 600))
    b.append(text(24, 248, 'two memory transfers', 11, INK2))
    return frame(308, 'Where the cycles go in one run',
                 'Median run on the FPGA. The split inside Python Spatial is an estimate from the synthesis report and a rough memory model.',
                 'Python Spatial: four copy-in memory transfers (about 144 cycles), the kernel (45 cycles: 7 for the '
                 'multiplication, 34 for the output-completion check), two copy-out transfers (about 71). '
                 'Handwritten HLS: one pipeline of 58 cycles.', '\n'.join(b))


# ---------------------------------------------------------------- figure 3: estimated path
def path():
    x0, x1 = 270, 700
    sx, ax = axis(x0, x1, 280, [0, 50, 100, 150, 200, 250], 100, 262, 'Compute cycles on the FPGA')
    b = [ax]
    b.append(swatch(270, 84, BLUE, 'Measured'))
    b.append(swatch(350, 84, BLUE_L, 'Estimated'))
    b.append(f'<line x1="436" x2="436" y1="74" y2="86" stroke="{ORANGE}" stroke-width="2"/>' +
             text(446, 84, 'Handwritten HLS, measured: 58', 11, INK2))
    rows = [('Today', 260, BLUE, '260', 600),
            ('+ completion check in one step', 225, BLUE_L, 'about 225', 400),
            ('+ no read of dst', 155, BLUE_L, 'about 155', 400),
            ('+ no flag transfers', 85, BLUE_L, 'about 85', 400),
            ('+ read and write inside the tile loop', 65, BLUE_L, 'about 60 to 70', 400)]
    for i, (label, v, fill, tip, weight) in enumerate(rows):
        yc = 120 + 32 * i
        b.append(text(24, yc + 4.5, label, 12.5, INK, 600 if i == 0 else 400))
        b.append(bar(x0, sx(v), yc - 8, 16, fill, f'{label}: {tip} cycles'))
        b.append(text(sx(v) + 8, yc + 4.5, tip, 12, INK, weight, halo=True))
    xt = sx(58)
    b.append(f'<line x1="{xt:.1f}" x2="{xt:.1f}" y1="100" y2="262" stroke="{SURF}" stroke-width="5"/>')
    b.append(f'<line x1="{xt:.1f}" x2="{xt:.1f}" y1="100" y2="262" stroke="{ORANGE}" stroke-width="2">'
             f'<title>Handwritten HLS: 58 cycles (measured)</title></line>')
    return frame(304, "Estimated path to the handwritten design's speed",
                 'Lab 1 tiled scale. Only the first bar is measured; the others come from a rough model and are to be measured.',
                 'Today 260 cycles (measured). Estimated after each change in turn: about 225, about 155, about 85, '
                 'about 60 to 70. Handwritten HLS measured 58.', '\n'.join(b))


for name, fn in [('2026-11-12-f2-runs.svg', runs), ('2026-11-12-f2-timeline.svg', timeline), ('2026-11-12-f2-path.svg', path)]:
    (OUT / name).write_text(fn())
    print('wrote', OUT / name)


# ================================================================ diagrams (same card style)
GOOD = '#0ca30c'
PANEL = '#f1f0eb'
DEFS = (f'<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0.8 L7,4 L0,7.2 Z" fill="{MUTED}"/></marker></defs>')


def node(x, y, w, h, lines, style='plain'):
    """lines: list of (text, bold). style: solid (done / generated), outline (under way / to be generated), plain."""
    fill, stroke, sw = {'solid': (BLUE, BLUE, 1), 'outline': (SURF, BLUE, 1.75), 'plain': (SURF, AXIS, 1)}[style]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>']
    lh = 14.5
    y0 = y + h / 2 - lh * (len(lines) - 1) / 2 + 4
    for i, (s, bold) in enumerate(lines):
        if style == 'solid':
            ink = '#ffffff'
        else:
            ink = INK if bold else INK2
        out.append(text(x + w / 2, y0 + lh * i, s, 12 if bold else 11, ink, 600 if bold else 400, 'middle'))
    return '\n'.join(out)


def arrow(x1, y1, x2, y2, both=False):
    start = ' marker-start="url(#ah)"' if both else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="1.25" '
            f'marker-end="url(#ah)"{start}/>')


def key(x, y, style, label):
    fill, stroke, sw = {'solid': (BLUE, BLUE, 1), 'outline': (SURF, BLUE, 1.75), 'plain': (SURF, AXIS, 1)}[style]
    return (f'<rect x="{x}" y="{y - 10}" width="16" height="11" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>' +
            text(x + 23, y, label, 11, INK2))


def check(x, y, label):
    return (f'<path d="M{x},{y - 4} l3.2,3.4 l6,-7.4" fill="none" stroke="{GOOD}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round"/>' + text(x + 14, y, label, 11, INK, 500))


def pieces():
    b = [DEFS]
    b.append(key(24, 84, 'solid', 'Generated by the compiler today'))
    b.append(key(236, 84, 'outline', 'To be generated (decided 12 November)'))
    b.append(key(490, 84, 'plain', 'Fixed, not ours'))
    b.append(f'<rect x="24" y="104" width="176" height="98" rx="8" fill="{PANEL}"/>' + text(36, 123, 'Instance CPU', 11, INK2, 600))
    b.append(f'<rect x="236" y="104" width="500" height="98" rx="8" fill="{PANEL}"/>' + text(248, 123, 'FPGA', 11, INK2, 600))
    b.append(node(40, 134, 144, 54, [('Host program', True), ('sets up, starts, checks', False)], 'outline'))
    b.append(node(252, 134, 120, 54, [('Shell', True), ("AWS's fixed logic", False)], 'plain'))
    b.append(node(404, 134, 150, 54, [('Wrapper', True), ('design_top.sv', False)], 'outline'))
    b.append(node(586, 134, 134, 54, [('Kernel', True), ('the computation', False)], 'solid'))
    b.append(node(404, 232, 150, 42, [('Off-chip memory', True)], 'plain'))
    b.append(arrow(186, 161, 250, 161, both=True))
    b.append(arrow(374, 161, 402, 161, both=True))
    b.append(arrow(556, 161, 584, 161, both=True))
    b.append(arrow(479, 190, 479, 230, both=True))
    return frame(296, 'The four pieces of a design on the F2 instance',
                 'In this experiment the host program was written by hand and the wrapper was the course file with three edits.',
                 'Host program on the instance CPU talks to the AWS shell on the FPGA; the wrapper sits between the shell '
                 'and the kernel and connects the kernel to off-chip memory. Only the kernel is generated today; the '
                 'wrapper and host program are to be generated.', '\n'.join(b))


def flow():
    b = [DEFS]
    b.append(text(24, 86, 'Compiler, on any machine', 11, INK2, 600))
    for i, label in enumerate(['Python Spatial source', 'Compiler and checker', 'Generated C++']):
        x = 24 + i * 174
        b.append(node(x, 96, 150, 42, [(label, True)], 'solid' if i == 2 else 'plain'))
        if i:
            b.append(arrow(x - 22, 117, x - 2, 117))
    b.append(f'<path d="M447,140 V160 H90 V178" fill="none" stroke="{MUTED}" stroke-width="1.25" marker-end="url(#ah)"/>')
    b.append(text(736, 170, "The class's make flow, on the F2 instance", 11, INK2, 600, 'end'))
    steps = [('gen_rtl', 'C++ to Verilog', 'passed'), ('hw_sim', 'shell simulation', 'passed'),
             ('fpga_build', 'place and route', 'timing met'), ('AWS image', 'registration', 'loadable'),
             ('Run on the chip', 'six fresh loads', 'passed 6 of 6')]
    for i, (name, what, result) in enumerate(steps):
        x = 24 + i * 145
        b.append(f'<rect x="{x}" y="180" width="132" height="70" rx="6" fill="{SURF}" stroke="{AXIS}"/>')
        b.append(text(x + 12, 199, name, 12, INK, 600))
        b.append(text(x + 12, 215, what, 11, INK2))
        b.append(check(x + 12, 238, result))
        if i:
            b.append(arrow(x - 12, 215, x - 1, 215))
    return frame(270, 'From Python Spatial source to a run on the FPGA',
                 'Every step passed for Lab 1 tiled scale, with the generated C++ unchanged throughout.',
                 'Python Spatial source goes through the compiler and checker to generated C++, then through the '
                 "class's make flow: gen_rtl passed, hw_sim passed, fpga_build met timing, the AWS image became "
                 'loadable, and the run on the chip passed six times out of six.', '\n'.join(b))


def plan():
    b = [DEFS]
    b.append(key(24, 84, 'solid', 'Done'))
    b.append(key(96, 84, 'outline', 'Under way'))
    b.append(key(196, 84, 'plain', 'Planned'))
    b.append(text(24, 114, 'Lab features', 11, INK2, 600))
    lab = [([('Lab 1: DRAM', True), ('and SRAM', True), ('runs on the FPGA', False)], 'solid'),
           ([('FIFO', True), ('design reviewed', False)], 'outline'),
           ([('Reg', True)], 'plain'),
           ([('Reduce', True), ('and Fold', True)], 'plain'),
           ([('Lab 2 and Lab 3', True), ('features', False)], 'plain')]
    for i, (lines, style) in enumerate(lab):
        x = 24 + i * 116
        b.append(node(x, 122, 104, 56, lines, style))
        if i:
            b.append(arrow(x - 11, 150, x - 1, 150))
    b.append(text(24, 206, 'Hardware, in parallel', 11, INK2, 600))
    b.append(node(24, 214, 236, 50, [('Single-exit loops', True), ('written and reviewed; hardware run next', False)], 'outline'))
    b.append(arrow(262, 239, 278, 239))
    b.append(node(280, 214, 312, 50, [('Interface redesign', True), ('less memory traffic; generated wrapper and host', False)], 'plain'))
    b.append(f'<rect x="624" y="122" width="112" height="142" rx="6" fill="{PANEL}" stroke="{INK2}" stroke-width="1.25"/>')
    for i, (s, bold) in enumerate([('April 2027', True), ('students and', False), ('TAs use', False), ('Python Spatial', False)]):
        b.append(text(680, 174 + 16 * i, s, 13 if bold else 11.5, INK if bold else INK2, 600 if bold else 400, 'middle'))
    b.append(arrow(594, 150, 622, 150))
    b.append(arrow(594, 239, 622, 239))
    return frame(284, 'The plan to April 2027',
                 'Lab features come first; hardware work runs beside them.',
                 'Lab features in order: Lab 1 DRAM and SRAM (runs on the FPGA), FIFO (design reviewed), Reg, Reduce '
                 'and Fold, then Lab 2 and Lab 3 features. Hardware in parallel: single-exit loops, then an interface '
                 'redesign with less memory traffic and a generated wrapper and host program. Target: April 2027.', '\n'.join(b))


for name, fn in [('2026-11-12-f2-pieces.svg', pieces), ('2026-11-12-f2-flow.svg', flow), ('2026-11-12-plan.svg', plan)]:
    (OUT / name).write_text(fn())
    print('wrote', OUT / name)
