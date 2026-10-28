"""DiscoveryLabNL logo options: Avenir Next outlined to SVG paths (no font needed to view), NL in red."""
import json, math, subprocess, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen

TTC = '/System/Library/Fonts/Avenir Next.ttc'
IDX = {'bold': 0, 'demi': 2, 'medium': 5, 'regular': 7}
FONTS = {k: TTFont(TTC, fontNumber=v) for k, v in IDX.items()}
INK, RED, GREY = '#13263F', '#AE1C28', '#5A6A7E'          # navy ink, Dutch-flag red, slate
INK_D, RED_D, GREY_D = '#FFFFFF', '#F0525A', '#B8C4D2'    # on dark
KERN = {('L', 'a'): -48, ('r', 'y'): -14, ('o', 'v'): -14, ('v', 'e'): -12, ('y', 'L'): -6}
OUT = sys.argv[1]


def shape(weight, text):
    r = subprocess.run(['hb-shape', f'--face-index={IDX[weight]}', '--output-format=json', TTC, text],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def run(weight, text, size, x, y, tracking=0):
    """Outline `text` at baseline (x, y). Returns list of (glyph name, contours) where each contour is
    an SVG path string, plus the advance width in px."""
    gs = FONTS[weight].getGlyphSet()
    s = size / 1000
    out, cx, prev = [], 0, None
    for g in shape(weight, text):
        name = g['g']
        if prev:
            cx += KERN.get((prev, name), 0)
        rec = RecordingPen()
        gs[name].draw(rec)
        contours, cur = [], []
        for op, args in rec.value:
            cur.append((op, args))
            if op in ('closePath', 'endPath'):
                contours.append(cur)
                cur = []
        paths = []
        for c in contours:
            sp = SVGPathPen(gs)
            tp = TransformPen(sp, (s, 0, 0, -s, x + cx * s, y))
            bp = BoundsPen(gs)
            tb = TransformPen(bp, (s, 0, 0, -s, x + cx * s, y))
            for op, args in c:
                getattr(tp, op)(*args)
                getattr(tb, op)(*args)
            paths.append((sp.getCommands(), bp.bounds))
        out.append((name, paths))
        cx += g['ax'] + tracking
        prev = name
    return out, (cx - tracking) * s


def ink_bounds(glyphs):
    bs = [b for _, ps in glyphs for _, b in ps if b]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def svg_paths(glyphs, fill, idot=None):
    """One <path> for the run; with idot, the i's dot (its highest contour) is drawn in that colour."""
    main, extra = [], []
    for name, ps in glyphs:
        if idot and name == 'i' and len(ps) == 2:
            top = min(ps, key=lambda p: p[1][1])  # smallest y = highest on screen
            for p in ps:
                (extra if p is top else main).append(p[0])
        else:
            main += [p[0] for p in ps]
    s = f'<path fill="{fill}" d="{" ".join(main)}"/>'
    if extra:
        s += f'<path fill="{idot}" d="{" ".join(extra)}"/>'
    return s


def wordmark(x, y, size, dark=False, idot=False, tagline=True):
    """DiscoveryLab + NL with the tagline spanning the word's ink width. Returns (svg, bbox)."""
    ink, red, grey = (INK_D, RED_D, GREY_D) if dark else (INK, RED, GREY)
    trk = -8
    a, wa = run('demi', 'DiscoveryLab', size, x, y, trk)
    gap = (KERN[('b', 'N')] if ('b', 'N') in KERN else 0) * size / 1000 + trk * size / 1000
    b, wb = run('bold', 'NL', size, x + wa + gap + 4 * size / 1000, y, trk)
    svg = svg_paths(a, ink, idot=red if idot else None) + svg_paths(b, red)
    x0, y0, x1, y1 = ink_bounds(a + b)
    if tagline:
        text = 'DUTCH MATERIALS DISCOVERY NATIONAL LABORATORY'
        tsize = size * 0.205
        nat, wn = run('medium', text, tsize, 0, 0, 0)
        nb = ink_bounds(nat)
        n_gaps = len(text) - 1
        trk_t = ((x1 - x0) - (nb[2] - nb[0])) / n_gaps / (tsize / 1000)
        yb = ink_bounds(run('demi', 'y', size, 0, 0)[0])[3]  # descender bottom (px below baseline)
        ty = y + yb + size * 0.075 + tsize * 0.708
        t, _ = run('medium', text, tsize, 0, ty, trk_t)
        tb = ink_bounds(t)
        t, _ = run('medium', text, tsize, x0 - (tb[0] - 0), ty, trk_t)
        svg += svg_paths(t, grey)
        y1 = max(y1, ink_bounds(t)[3])
    return svg, (x0, y0, x1, y1)


def mark(kind, cx, cy, M, dark=False):
    ink, red = (INK_D, RED_D) if dark else (INK, RED)
    if kind == 'orbit':
        r, sw = 0.40 * M, 0.072 * M
        sat = math.radians(-40)
        gap = math.radians(30)
        a0, a1 = sat + gap, sat - gap + 2 * math.pi
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        sx, sy = cx + r * math.cos(sat), cy + r * math.sin(sat)
        return (f'<path d="M{p0[0]:.2f},{p0[1]:.2f} A{r:.2f},{r:.2f} 0 1 1 {p1[0]:.2f},{p1[1]:.2f}" fill="none" '
                f'stroke="{ink}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
                f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{0.085 * M:.2f}" fill="{ink}"/>'
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{0.165 * M:.2f}" fill="{red}"/>')
    if kind == 'stack':
        w, h, t, step = 0.92 * M, 0.42 * M, 0.07 * M, 0.20 * M
        tones = [(red, '#8A1520', '#6E1019'), ('#2C4566', '#1E3350', '#13263F'), ('#8796AA', '#6B7B91', '#56667C')] if not dark else \
                [(red, '#C93C44', '#A8323A'), ('#E6ECF3', '#C3CCD8', '#A3AFBF'), ('#6F8099', '#5A6B84', '#4A5A72')]
        out = []
        for i in (2, 1, 0):
            ty = cy - 0.26 * M + i * step
            L, R, T, B = cx - w / 2, cx + w / 2, ty - h / 2, ty + h / 2
            top, left, right = tones[i]
            out.append(f'<path d="M{L:.2f},{ty:.2f} L{cx:.2f},{B:.2f} L{cx:.2f},{B + t:.2f} L{L:.2f},{ty + t:.2f} Z" fill="{left}"/>'
                       f'<path d="M{R:.2f},{ty:.2f} L{cx:.2f},{B:.2f} L{cx:.2f},{B + t:.2f} L{R:.2f},{ty + t:.2f} Z" fill="{right}"/>'
                       f'<path d="M{cx:.2f},{T:.2f} L{R:.2f},{ty:.2f} L{cx:.2f},{B:.2f} L{L:.2f},{ty:.2f} Z" fill="{top}"/>')
        return ''.join(out)
    if kind == 'glass':
        # thin-film stack as translucent plates: each plate is one shape at one opacity, so the plate
        # below shows through the plate above (a film stack seen at an angle)
        w, h, t, step = 0.94 * M, 0.44 * M, 0.06 * M, 0.17 * M
        plates = [(ink, 0.38), (ink, 0.62), (red, 0.88)] if not dark else [('#C3CCD8', 0.35), ('#E6ECF3', 0.6), (red, 0.9)]
        out = []
        for i, (col, op) in enumerate(plates):
            ty = cy + 0.20 * M - i * step
            L, R, T, B = cx - w / 2, cx + w / 2, ty - h / 2, ty + h / 2
            out.append(f'<g opacity="{op}">'
                       f'<path d="M{L:.2f},{ty:.2f} L{cx:.2f},{T:.2f} L{R:.2f},{ty:.2f} L{R:.2f},{ty + t:.2f} L{cx:.2f},{B + t:.2f} L{L:.2f},{ty + t:.2f} Z" fill="{col}"/>'
                       f'<path d="M{L:.2f},{ty:.2f} L{cx:.2f},{B:.2f} L{R:.2f},{ty:.2f}" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="{0.012 * M:.2f}"/>'
                       f'</g>')
        return ''.join(out)
    if kind == 'hub':
        R, sw = 0.40 * M, 0.045 * M
        pts = [(cx + R * math.cos(math.radians(90 + 60 * k)), cy + R * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
        lines = ''.join(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{px:.2f}" y2="{py:.2f}"/>' for px, py in pts)
        ring = 'M' + ' L'.join(f'{px:.2f},{py:.2f}' for px, py in pts) + ' Z'
        dots = ''.join(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{0.085 * M:.2f}" fill="{ink}"/>' for px, py in pts)
        return (f'<g stroke="{ink}" stroke-width="{sw:.2f}" stroke-linecap="round" opacity="0.55">{lines}'
                f'<path d="{ring}" fill="none"/></g>{dots}'
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{0.15 * M:.2f}" fill="{red}"/>')
    return ''


def lockup(kind, x, y, size, dark=False, idot=False, tagline=True):
    """Mark left of the wordmark; the mark spans cap top to tagline bottom."""
    probe, (x0, y0, x1, y1) = wordmark(0, 0, size, dark, idot, tagline)
    if kind == 'none':
        svg, bb = wordmark(x, y, size, dark, idot, tagline)
        return svg, bb
    cap_top = -0.708 * size
    block_bottom = y1 if tagline else 0.0
    M = (block_bottom - cap_top) * (1.18 if tagline else 1.5)
    mid = (cap_top + block_bottom) / 2
    gap = (0.30 if tagline else 0.24) * M
    m = mark(kind, x + M / 2, y + mid, M, dark)
    svg, bb = wordmark(x + M + gap, y, size, dark, idot, tagline)
    return m + svg, (x, y + mid - M / 2, bb[2], max(bb[3], y + mid + M / 2))


if __name__ == '__main__':
    import os
    os.makedirs(OUT, exist_ok=True)
    # Single assets
    for kind in ('orbit', 'stack', 'hub', 'none'):
        for dark in (False, True):
            svg, (x0, y0, x1, y1) = lockup(kind, 0, 0, 100, dark, idot=(kind == 'none'))
            pad = 8
            vb = f'{x0 - pad:.1f} {y0 - pad:.1f} {x1 - x0 + 2 * pad:.1f} {y1 - y0 + 2 * pad:.1f}'
            name = f'DiscoveryLabNL-{kind}{"-dark" if dark else ""}.svg'
            bg = f'<rect x="{x0 - pad:.1f}" y="{y0 - pad:.1f}" width="{x1 - x0 + 2 * pad:.1f}" height="{y1 - y0 + 2 * pad:.1f}" fill="#0E1E33"/>' if dark else ''
            open(f'{OUT}/{name}', 'w').write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{bg}{svg}</svg>')
    # Options sheet
    W, H = 2400, 1700
    parts = [f'<rect width="{W}" height="{H}" fill="#F4F2EE"/>']
    labels = {'orbit': 'A  Orbit: the discovery loop around one result (builds on the discoverylabs.nl icon)',
              'stack': 'B  Stack: thin-film layers, and the three pillars (labs, characterisation, AI)',
              'hub': 'C  Hub: one central lab and its satellite labs, drawn as a lattice',
              'none': 'D  Type only: red dot on the i and red NL'}
    lab_run = lambda txt, x, y: svg_paths(run('medium', txt, 26, x, y)[0], '#3B4656')
    for i, kind in enumerate(('orbit', 'stack', 'hub', 'none')):
        col, row = i % 2, i // 2
        px, py = 60 + col * 1170, 60 + row * 560
        parts.append(f'<rect x="{px}" y="{py}" width="1110" height="500" rx="18" fill="#FFFFFF"/>')
        parts.append(lab_run(labels[kind], px + 40, py + 60))
        svg, bb = lockup(kind, 0, 0, 112, idot=(kind == 'none'))
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        ox, oy = px + (1110 - w) / 2 - bb[0], py + 70 + (430 - h) / 2 - bb[1]
        parts.append(f'<g transform="translate({ox:.1f},{oy:.1f})">{svg}</g>')
    # dark strip with A and C small, plus slide-header size
    py = 60 + 2 * 560
    parts.append(f'<rect x="60" y="{py}" width="2280" height="460" rx="18" fill="#0E1E33"/>')
    for j, kind in enumerate(('orbit', 'stack', 'hub')):
        svg, bb = lockup(kind, 0, 0, 62, dark=True)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        ox, oy = 60 + 40 + j * 760 + (700 - w) / 2 - bb[0], py + 40 + (180 - h) / 2 - bb[1]
        parts.append(f'<g transform="translate({ox:.1f},{oy:.1f})">{svg}</g>')
    # header-size test on white inside the dark strip
    parts.append(f'<rect x="100" y="{py + 250}" width="2200" height="170" rx="10" fill="#FFFFFF"/>')
    for j, kind in enumerate(('orbit', 'stack', 'hub', 'none')):
        svg, bb = lockup(kind, 0, 0, 30, idot=(kind == 'none'))
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        ox, oy = 100 + 30 + j * 545 + (500 - w) / 2 - bb[0], py + 250 + (170 - h) / 2 - bb[1]
        parts.append(f'<g transform="translate({ox:.1f},{oy:.1f})">{svg}</g>')
    open(f'{OUT}/options-sheet.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>')
    print('ok')
