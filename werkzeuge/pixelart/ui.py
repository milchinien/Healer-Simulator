"""UI-Grafiken im WoW-inspirierten Pixel-Stil (9-Slice-Texturen).

Jede Textur wird mit ihren 9-Slice-Raendern in SLICES registriert; die Werte
landen in ui_slices.json und werden vom Spiel beim Aufbau des Themes gelesen.
"""
from __future__ import annotations

import numpy as np

from pa import Canvas, c, mix, shade, BAYER4

INK = '#0e0a14'
GOLD_L = '#ffe08a'
GOLD = '#f2c14e'
GOLD_M = '#c99a3a'
GOLD_D = '#8a6424'
GOLD_DD = '#4e3516'
BG_A = '#1d1626'
BG_B = '#150f1c'
BG_C = '#261d31'

SLICES: dict[str, dict] = {}


def reg(name, cv: Canvas, margin, content=None, tile=True):
    SLICES[name] = {
        'margin': margin if isinstance(margin, (list, tuple)) else [margin] * 4,  # l, t, r, b
        'content': content if content is not None else (margin if isinstance(margin, (list, tuple)) else [margin] * 4),
        'tile': tile,
    }
    return cv


def _bg_texture(cv: Canvas, x0, y0, w, h, a=BG_A, b=BG_B, speck=BG_C, seed=1, alpha=255):
    r = np.random.default_rng(seed)
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            t = (y - y0) / max(1, h - 1)
            col = a if t < 0.5 + (BAYER4[y % 4, x % 4] - 0.5) * 0.6 else b
            if r.random() < 0.05:
                col = speck
            cc = c(col)
            cv.px(x, y, (cc[0], cc[1], cc[2], alpha))


def gold_frame(cv: Canvas, x, y, w, h, corners=True):
    """Doppelter Goldrahmen mit Lichtkante oben/links und Nieten in den Ecken."""
    cv.frame(x, y, w, h, INK)
    cv.frame(x + 1, y + 1, w - 2, h - 2, GOLD_D)
    # Lichtkante
    cv.hline(x + 2, x + w - 3, y + 2, GOLD)
    cv.vline(x + 2, y + 2, y + h - 3, GOLD)
    cv.hline(x + 2, x + w - 3, y + h - 3, GOLD_M)
    cv.vline(x + w - 3, y + 2, y + h - 3, GOLD_M)
    cv.px(x + 2, y + 2, GOLD_L)
    cv.frame(x + 3, y + 3, w - 6, h - 6, INK)
    if corners:
        for (cx, cy) in [(x, y), (x + w - 7, y), (x, y + h - 7), (x + w - 7, y + h - 7)]:
            # Eckbeschlag 7x7
            cv.rect(cx + 1, cy + 1, 5, 5, GOLD_M)
            cv.frame(cx, cy, 7, 7, INK)
            cv.px(cx + 3, cy + 3, GOLD_L)
            cv.px(cx + 2, cy + 3, GOLD)
            cv.px(cx + 3, cy + 2, GOLD)
            cv.px(cx + 4, cy + 3, GOLD_D)
            cv.px(cx + 3, cy + 4, GOLD_D)
            cv.px(cx + 1, cy + 1, GOLD)
            cv.px(cx + 5, cy + 5, GOLD_DD)


def panel(alpha=250) -> Canvas:
    cv = Canvas(32, 32)
    _bg_texture(cv, 4, 4, 24, 24, alpha=alpha)
    gold_frame(cv, 0, 0, 32, 32)
    return reg('panel', cv, 8, [9, 9, 9, 9])


def panel_plain(alpha=225) -> Canvas:
    """Schlichter dunkler Kasten mit feinem Rand (fuer Unterbereiche)."""
    cv = Canvas(16, 16)
    _bg_texture(cv, 1, 1, 14, 14, a='#1a1422', b='#140f1a', speck='#231a2c', alpha=alpha, seed=4)
    cv.frame(0, 0, 16, 16, INK)
    cv.hline(1, 14, 1, '#3a2f46')
    cv.hline(1, 14, 14, '#0a070e')
    return reg('panel_plain', cv, 3, [5, 4, 5, 4])


def header_plate() -> Canvas:
    """Titelplakette fuer Fensterueberschriften."""
    w, h = 48, 17
    cv = Canvas(w, h)
    cv.rect(2, 2, w - 4, h - 4, '#3b2a18')
    cv.vgradient(3, 3, w - 6, h - 6, ['#6a4a22', '#4a3218', '#2e1f10'])
    cv.frame(0, 0, w, h, INK)
    cv.frame(1, 1, w - 2, h - 2, GOLD_M)
    cv.hline(2, w - 3, 2, GOLD_L)
    cv.hline(2, w - 3, h - 3, GOLD_D)
    cv.vline(1, 2, h - 3, GOLD)
    cv.vline(w - 2, 2, h - 3, GOLD_D)
    return reg('header', cv, [6, 5, 6, 5], [8, 4, 8, 4])


def button(kind='red', state='normal') -> Canvas:
    w, h = 24, 18
    cv = Canvas(w, h)
    if kind == 'red':
        base = {'normal': ['#e0573f', '#b8352c', '#7c1f1e'],
                'hover': ['#f47a52', '#d0463a', '#932826'],
                'pressed': ['#8e2524', '#a8302b', '#b8352c'],
                'disabled': ['#6d5f63', '#564a50', '#3e3439']}[state]
        rim = GOLD if state != 'disabled' else '#8c8088'
        rim_d = GOLD_D if state != 'disabled' else '#5c5058'
    else:  # dunkler Stein/Bronze-Knopf
        base = {'normal': ['#4d3e5c', '#3a2e47', '#241c2e'],
                'hover': ['#62507a', '#4a3b5c', '#2e2439'],
                'pressed': ['#221a2b', '#2e2439', '#3a2e47'],
                'disabled': ['#3a3540', '#2e2a33', '#222026']}[state]
        rim = GOLD_M if state != 'disabled' else '#6a6270'
        rim_d = GOLD_DD if state != 'disabled' else '#3e3944'
    off = 1 if state == 'pressed' else 0
    cv.frame(0, 0, w, h, INK)
    cv.frame(1, 1, w - 2, h - 2, rim_d)
    cv.hline(2, w - 3, 1, rim)
    cv.vline(1, 2, h - 3, rim)
    cv.px(1, 1, rim)
    cv.vgradient(2, 2, w - 4, h - 4, base)
    if state != 'pressed' and state != 'disabled':
        cv.hline(3, w - 4, 2, shade(base[0], 0.25))
    cv.hline(2, w - 3, h - 3, shade(base[2], -0.3))
    return reg(f'btn_{kind}_{state}', cv, [5, 5, 5, 5], [7, 4 + off, 7, 4 - off] if kind == 'dark' else [10, 1 + off, 10, 3 - off])


def list_entry(state='normal') -> Canvas:
    w, h = 20, 20
    cv = Canvas(w, h)
    if state == 'normal':
        cv.rect(0, 0, w, h, (20, 15, 28, 150))
        cv.frame(0, 0, w, h, (70, 56, 84, 160))
    elif state == 'hover':
        cv.rect(0, 0, w, h, (46, 36, 60, 200))
        cv.frame(0, 0, w, h, (140, 110, 70, 220))
    else:  # selected
        cv.vgradient(0, 0, w, h, [(94, 72, 34, 230), (52, 38, 22, 230)])
        cv.frame(0, 0, w, h, INK)
        cv.frame(1, 1, w - 2, h - 2, GOLD)
        cv.hline(2, w - 3, 2, GOLD_L)
    return reg(f'list_{state}', cv, 4, [6, 3, 6, 3])


def input_field(state='normal') -> Canvas:
    w, h = 16, 16
    cv = Canvas(w, h)
    cv.rect(1, 1, w - 2, h - 2, '#0c0911')
    cv.frame(0, 0, w, h, GOLD_D if state == 'normal' else GOLD)
    cv.hline(1, w - 2, 1, '#050307')
    cv.vline(1, 1, h - 2, '#050307')
    cv.hline(1, w - 2, h - 2, '#221a2c')
    return reg(f'input_{state}', cv, 3, [5, 4, 5, 4])


def tile(state='normal') -> Canvas:
    """Quadratische Auswahl-Kachel (Rassen, Geschlecht, Modus)."""
    w, h = 16, 16
    cv = Canvas(w, h)
    if state == 'normal':
        cv.rect(1, 1, w - 2, h - 2, (24, 18, 32, 230))
        cv.frame(0, 0, w, h, INK)
        cv.frame(1, 1, w - 2, h - 2, '#5a4a38')
    elif state == 'hover':
        cv.rect(1, 1, w - 2, h - 2, (44, 34, 56, 240))
        cv.frame(0, 0, w, h, INK)
        cv.frame(1, 1, w - 2, h - 2, GOLD_M)
    else:
        cv.vgradient(1, 1, w - 2, h - 2, [(90, 70, 30, 255), (40, 30, 18, 255)])
        cv.frame(0, 0, w, h, INK)
        cv.frame(1, 1, w - 2, h - 2, GOLD_L)
        cv.frame(2, 2, w - 4, h - 4, GOLD_M)
    return reg(f'tile_{state}', cv, 4, [4, 4, 4, 4])


def slider_parts():
    track = Canvas(12, 6)
    track.rect(0, 0, 12, 6, INK)
    track.rect(1, 1, 10, 4, '#0a070e')
    track.hline(1, 10, 4, '#2a2133')
    reg('slider_track', track, [3, 2, 3, 2], [0, 0, 0, 0])
    fill = Canvas(12, 6)
    fill.rect(0, 0, 12, 6, INK)
    fill.vgradient(1, 1, 10, 4, [GOLD_L, GOLD, GOLD_D])
    reg('slider_fill', fill, [3, 2, 3, 2], [0, 0, 0, 0])
    knobs = {}
    for st, cols in {'normal': (GOLD, GOLD_D), 'hover': (GOLD_L, GOLD_M)}.items():
        k = Canvas(7, 11)
        k.rect(1, 1, 5, 9, cols[0])
        k.frame(0, 0, 7, 11, INK)
        k.vline(5, 1, 9, cols[1])
        k.hline(1, 5, 9, cols[1])
        k.px(3, 3, GOLD_DD)
        k.px(3, 5, GOLD_DD)
        k.px(3, 7, GOLD_DD)
        knobs[st] = k
    return track, fill, knobs


def checkbox():
    out = {}
    for st in ['off', 'on', 'off_hover', 'on_hover']:
        cv = Canvas(11, 11)
        cv.rect(1, 1, 9, 9, '#0c0911')
        cv.frame(0, 0, 11, 11, GOLD_M if 'hover' in st else GOLD_D)
        if st.startswith('on'):
            for (x, y) in [(2, 5), (3, 6), (4, 7), (5, 6), (6, 5), (7, 4), (8, 3), (3, 5), (4, 6), (5, 5), (6, 4), (7, 3)]:
                cv.px(x, y, GOLD_L if (x + y) % 2 else GOLD)
        out[st] = cv
    return out


def scrollbar():
    tr = Canvas(6, 12)
    tr.rect(0, 0, 6, 12, (10, 7, 14, 200))
    tr.vline(0, 0, 11, INK)
    reg('scroll_track', tr, [2, 3, 2, 3], [0, 0, 0, 0])
    gr = Canvas(6, 12)
    gr.rect(0, 0, 6, 12, INK)
    gr.rect(1, 1, 4, 10, GOLD_D)
    gr.vline(1, 1, 10, GOLD_M)
    reg('scroll_grabber', gr, [2, 3, 2, 3], [0, 0, 0, 0])
    return tr, gr


def tooltip() -> Canvas:
    cv = Canvas(12, 12)
    cv.rect(1, 1, 10, 10, (12, 9, 18, 245))
    cv.frame(0, 0, 12, 12, '#6e6a80')
    cv.hline(1, 10, 1, '#262033')
    return reg('tooltip', cv, 3, [5, 4, 5, 4])


def tab(state='normal') -> Canvas:
    w, h = 16, 14
    cv = Canvas(w, h)
    top = {'normal': ['#3a2e47', '#231b2c'], 'hover': ['#4d3e5c', '#2e2439'], 'selected': ['#6a4a22', '#3a2a16']}[state]
    cv.vgradient(1, 1, w - 2, h - 1, top)
    cv.hline(1, w - 2, 0, INK)
    cv.vline(0, 1, h - 1, INK)
    cv.vline(w - 1, 1, h - 1, INK)
    cv.hline(2, w - 3, 1, GOLD_L if state == 'selected' else GOLD_D)
    cv.vline(1, 1, h - 1, GOLD_M if state == 'selected' else GOLD_DD)
    cv.vline(w - 2, 1, h - 1, GOLD_D if state == 'selected' else GOLD_DD)
    if state != 'selected':
        cv.hline(0, w - 1, h - 1, GOLD_D)
    return reg(f'tab_{state}', cv, [4, 4, 4, 2], [6, 3, 6, 2])


def arrow_button(direction='left', state='normal') -> Canvas:
    cv = Canvas(11, 11)
    fill = {'normal': GOLD_M, 'hover': GOLD_L, 'pressed': GOLD_D, 'disabled': '#5c5058'}[state]
    cv.rect(1, 1, 9, 9, {'normal': '#2a2133', 'hover': '#3d3049', 'pressed': '#140f1a', 'disabled': '#1c1822'}[state])
    cv.frame(0, 0, 11, 11, INK)
    cv.frame(1, 1, 9, 9, GOLD_D if state != 'disabled' else '#3e3944')
    pts = [(3, 5), (4, 4), (4, 5), (4, 6), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7)]
    if direction == 'right':
        pts = [(10 - x, y) for x, y in pts]
    oy = 1 if state == 'pressed' else 0
    for (x, y) in pts:
        cv.px(x, y + oy, fill)
    return cv


def progress_bar():
    bg = Canvas(16, 10)
    bg.rect(0, 0, 16, 10, INK)
    bg.rect(1, 1, 14, 8, '#0a070e')
    bg.frame(1, 1, 14, 8, GOLD_D)
    bg.hline(2, 13, 2, '#050307')
    reg('progress_bg', bg, [3, 3, 3, 3], [0, 0, 0, 0])
    fg = Canvas(16, 10)
    fg.vgradient(0, 0, 16, 10, ['#fff3b0', '#f2c14e', '#b07f2c', '#7a5418'])
    fg.hline(0, 15, 1, '#fff8d6')
    reg('progress_fill', fg, [2, 2, 2, 2], [0, 0, 0, 0])
    return bg, fg


def separator() -> Canvas:
    cv = Canvas(32, 5)
    for x in range(32):
        t = 1 - abs(x - 15.5) / 16
        cv.px(x, 2, mix(GOLD_DD, GOLD, t))
    cv.px(15, 1, GOLD_M)
    cv.px(16, 1, GOLD_M)
    cv.px(15, 3, GOLD_M)
    cv.px(16, 3, GOLD_M)
    for (x, y) in [(15, 0), (16, 0), (14, 2), (17, 2), (15, 4), (16, 4)]:
        cv.px(x, y, GOLD)
    cv.px(15, 2, GOLD_L)
    cv.px(16, 2, GOLD_L)
    return reg('separator', cv, [6, 0, 6, 0], [0, 0, 0, 0], tile=False)


def swatch_frame(selected=False) -> Canvas:
    cv = Canvas(9, 9)
    cv.frame(0, 0, 9, 9, GOLD_L if selected else INK)
    cv.frame(1, 1, 7, 7, GOLD_M if selected else '#3e3346')
    return cv
