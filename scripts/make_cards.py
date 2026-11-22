import sys, os
OUT = sys.argv[1]

C = dict(bg='#1e1e2e', bar='#181825', surface='#313244', ov='#6c7086', text='#cdd6f4', sub='#a6adc8',
         blue='#89b4fa', mauve='#cba6f7', pink='#f5c2e7', green='#a6e3a1', yellow='#f9e2af',
         red='#f38ba8', teal='#94e2d5', lav='#b4befe', peach='#fab387')
FONT = "font-family=\"'JetBrains Mono','Cascadia Code',Consolas,Menlo,'DejaVu Sans Mono',monospace\""

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def T(x, y, t, col, size=20, weight=400, anchor='start', extra=''):
    return f'<text x="{x}" y="{y}" fill="{col}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(t)}</text>'

STYLE = '''<style>
.seg{opacity:0;animation:on .25s ease-out forwards}
@keyframes on{to{opacity:1}}
.eyes{transform-box:fill-box;transform-origin:center;animation:blink 5s infinite}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.12)}}
.cur{animation:cur 1s steps(1) infinite}
@keyframes cur{50%{opacity:0}}
.fade{opacity:0;animation:on .4s ease-out forwards}
@media (prefers-reduced-motion:reduce){.seg,.fade{animation:none;opacity:1}.eyes,.cur{animation:none}}
</style>'''

def lerp(a, b, t):
    a = [int(a[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x+(y-x)*t):02x}' for x, y in zip(a, b))

HALF = [
".oo........",
".oio.......",
".oiio......",
".oiiooooooo",
".o.........",
".o.........",
".o...ee....",
".o..eeee...",
".o..eeee...",
".o...ee....",
".o........n",
".o.......m.",
".o........m",
"..o........",
"...oooooooo",
]
CAT = [h + h[::-1] for h in HALF]

def cat(x, y, p):
    out, eyes = [], []
    n = len(CAT)
    for r, row in enumerate(CAT):
        oc = lerp(C['mauve'], C['blue'], r/(n-1))
        for c, ch in enumerate(row):
            col = {'o': oc, 'i': '#8c6fc9', 'e': C['pink'], 'n': C['pink'], 'm': C['lav']}.get(ch)
            if not col:
                continue
            rect = f'<rect x="{x+c*p}" y="{y+r*p}" width="{p}" height="{p}" fill="{col}"/>'
            (eyes if ch == 'e' else out).append(rect)
    # nose underside
    out.append(f'<rect x="{x+10*p}" y="{y+10*p+p//2}" width="{2*p}" height="{p//2}" fill="{C["blue"]}"/>')
    # whiskers
    W = len(CAT[0])
    for k, ry in enumerate([10.3, 11.6]):
        out.append(f'<rect x="{x-2*p}" y="{y+ry*p}" width="{4*p}" height="3" fill="{C["lav"]}"/>')
        out.append(f'<rect x="{x+(W-2)*p}" y="{y+ry*p}" width="{4*p}" height="3" fill="{C["lav"]}"/>')
    return ''.join(out) + f'<g class="eyes">{"".join(eyes)}</g>'

def icon(x, y, col, kind):
    # tiny 12px glyphs drawn with rects; y is text baseline
    t = y - 14
    if kind == 0:   return f'<rect x="{x}" y="{t}" width="12" height="12" rx="2" fill="none" stroke="{col}" stroke-width="2"/>'
    if kind == 1:   return f'<rect x="{x+1}" y="{t+1}" width="10" height="10" fill="{col}" transform="rotate(45 {x+6} {t+6})"/>'
    if kind == 2:   return f'<circle cx="{x+6}" cy="{t+6}" r="6" fill="{col}"/>'
    return f'<rect x="{x}" y="{t+2}" width="12" height="8" rx="1" fill="{col}"/>'

def box(x, y, w, h, title, tcol, ticon):
    tw = 16 + len(title)*12 + 24
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{C["ov"]}" stroke-width="2"/>'
            f'<rect x="{x+18}" y="{y-12}" width="{tw}" height="24" fill="{C["bg"]}"/>'
            + icon(x+26, y+7, tcol, ticon) + T(x+46, y+7, title, tcol))

def chrome(W, H, tab):
    return (f'<rect width="{W}" height="{H}" rx="14" fill="{C["bg"]}"/>'
            f'<path d="M0 14a14 14 0 0 1 14-14h{W-28}a14 14 0 0 1 14 14v30H0z" fill="{C["bar"]}"/>'
            f'<path d="M14 44V18a8 8 0 0 1 8-8h300a8 8 0 0 1 8 8v26z" fill="{C["bg"]}"/>'
            + icon(30, 34, C['blue'], 3)
            + T(52, 33, tab, C['text'], 16)
            + T(300, 33, '×', C['sub'], 20, anchor='middle')
            + T(360, 33, '+', C['sub'], 20, anchor='middle')
            + T(392, 32, '⌄', C['sub'], 16, anchor='middle')
            + f'<circle cx="{W-90}" cy="22" r="6" fill="{C["yellow"]}"/><circle cx="{W-66}" cy="22" r="6" fill="{C["green"]}"/><circle cx="{W-42}" cy="22" r="6" fill="{C["red"]}"/>')

def prompt(x, y, cmd, cursor=False):
    cur = f'<tspan class="cur" fill="{C["pink"]}">█</tspan>' if cursor else ''
    return (f'<text x="{x}" y="{y}" font-size="20" xml:space="preserve">'
            f'<tspan fill="{C["blue"]}">PS </tspan><tspan fill="{C["mauve"]}">C:\\Users\\alisa</tspan>'
            f'<tspan fill="{C["sub"]}">&gt; </tspan><tspan fill="{C["text"]}">{esc(cmd)}</tspan>{cur}</text>')

PROFILE = [
    ('NAME',   'Alisa', C['blue'], 0),
    ('ROLE',   'Frontend Engineer + UI/UX Designer', C['blue'], 1),
    ('STUDY',  'BSSE @ IIUI, Islamabad', C['blue'], 0),
    ('SHELL',  'React + Tailwind, with a Figma file open', C['blue'], 3),
    ('UPTIME', 'powered by infinite cups of chai', C['blue'], 2),
]

# edit these freely — (label, skill, percent)
SKILLS = [
    ('DESIGN', 'Figma / UI/UX', 90),
    ('FRONT',  'React',         85),
    ('FRONT',  'Next.js',       80),
    ('STYLE',  'Tailwind CSS',  90),
    ('LANG',   'JavaScript',    80),
    ('LANG',   'TypeScript',    65),
    ('BACK',   'Supabase',      70),
    ('BACK',   'Firebase',      60),
    ('SHIP',   'Git + Vercel',  75),
    ('GROWTH', 'Distribution',  85),
]

def pct_col(p):
    return C['green'] if p >= 85 else C['teal'] if p >= 75 else C['yellow'] if p >= 60 else C['peach']

def fetch():
    W = 1200
    H = 140 + 30 + len(PROFILE)*32 + 44 + 30 + len(SKILLS)*32 + 44 + 90
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>', STYLE, chrome(W, H, 'alisa — PowerShell')]
    s.append(prompt(40, 90, 'fastfetch --skills'))
    s.append(f'<g shape-rendering="crispEdges">{cat(80, 300, 14)}</g>')
    bx, bw = 440, 720
    # profile box
    y0 = 140
    rows = len(PROFILE)
    s.append(box(bx, y0, bw, 30 + rows*32, 'Profile', C['blue'], 2))
    for i, (k, v, col, ic) in enumerate(PROFILE):
        y = y0 + 44 + i*32
        s.append(f'<g class="fade" style="animation-delay:{.1+i*.08:.2f}s">' + icon(bx+22, y, C['blue'], ic) + T(bx+46, y, k, C['blue'], weight=700) + T(bx+170, y, v, C['text']) + '</g>')
    # skills box
    y1 = y0 + 30 + rows*32 + 44
    s.append(box(bx, y1, bw, 30 + len(SKILLS)*32, 'Skills', C['mauve'], 1))
    seg_w, seg_g, nseg = 10, 2, 20
    barx = bx + 370
    for i, (lab, sk, p) in enumerate(SKILLS):
        y = y1 + 44 + i*32
        base = .6 + i*.12
        s.append(f'<g class="fade" style="animation-delay:{base:.2f}s">' + icon(bx+22, y, C['mauve'], i % 4) + T(bx+46, y, lab, C['mauve'], weight=700) + T(bx+170, y, sk, C['text']) + '</g>')
        fill = round(p/100*nseg)
        segs = []
        for j in range(nseg):
            xx = barx + j*(seg_w+seg_g)
            if j < fill:
                segs.append(f'<rect class="seg" style="animation-delay:{base+.15+j*.035:.3f}s" x="{xx}" y="{y-15}" width="{seg_w}" height="14" fill="{C["green"]}"/>')
            else:
                segs.append(f'<rect x="{xx}" y="{y-15}" width="{seg_w}" height="14" fill="{C["surface"]}"/>')
        s.append(f'<g shape-rendering="crispEdges">{"".join(segs)}</g>')
        s.append(f'<g class="fade" style="animation-delay:{base+.15+fill*.035:.2f}s">' + T(bx + bw - 22, y, f'{p}%', pct_col(p), anchor='end') + '</g>')
    # colour dots
    yd = y1 + 30 + len(SKILLS)*32 + 44
    for i, col in enumerate([C['ov'], C['blue'], C['teal'], C['pink'], C['green'], C['yellow'], C['mauve'], C['red']]):
        s.append(f'<circle cx="{bx+20+i*30}" cy="{yd}" r="7" fill="{col}"/>')
    s.append(prompt(40, H-34, '', cursor=True))
    s.append('</svg>')
    return ''.join(s)

PROJECTS = [
    ('d----', 'live',     C['green'],  'chaii/',              'pixel-art chai stall hangout app (PWA)'),
    ('d----', 'building', C['yellow'], 'reminder-assistant/', 'WhatsApp + PWA + Google Tasks check-ins'),
    ('d----', 'wip',      C['peach'],  'portfolio/',          'minecraft title-screen portfolio'),
    ('d-r--', 'archived', C['ov'],     'coldbeak/',           'AI cold email SaaS, co-founded'),
]

def projects():
    W, H = 1200, 380
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {FONT}>', STYLE, chrome(W, H, 'alisa — projects')]
    s.append(prompt(40, 90, 'ls ~/projects'))
    s.append(T(76, 140, 'Directory: C:\\Users\\alisa\\projects', C['sub']))
    cols = [40, 150, 290, 560]
    for x, h in zip(cols, ['Mode', 'Status', 'Name', 'About']):
        s.append(T(x, 188, h, C['teal'], weight=700))
        s.append(T(x, 212, '-'*len(h), C['teal']))
    for i, (m, st, sc, n, d) in enumerate(PROJECTS):
        y = 246 + i*30
        s.append(f'<g class="fade" style="animation-delay:{.2+i*.15:.2f}s">' + T(cols[0], y, m, C['sub']) + T(cols[1], y, st, sc, weight=700) + T(cols[2], y, n, C['blue'], weight=700) + T(cols[3], y, d, C['text']) + '</g>')
    s.append(prompt(40, H-24, '', cursor=True))
    s.append('</svg>')
    return ''.join(s)

open(os.path.join(OUT, 'fetch.svg'), 'w').write(fetch())
open(os.path.join(OUT, 'projects.svg'), 'w').write(projects())
print('ok')