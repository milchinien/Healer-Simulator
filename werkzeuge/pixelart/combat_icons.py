"""Icons fuer den Kampf-Hauptbildschirm: Zauber, Auren, Rollen, Mikromenue,
NPC-Portraets, Wellenpunkte, Aktionsleisten-Plaetze und Einheitenrahmen.

Alle Grafiken werden Pixel fuer Pixel erzeugt und nach
assets/gfx/combat/<name>.png geschrieben.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pa import Canvas, c, from_grid, mix, shade

# ------------------------------------------------------------------ Farben
INK = '#0e0a14'
OUT = '#120e18'
GOLD_L = '#ffe08a'
GOLD = '#f2c14e'
GOLD_M = '#c99a3a'
GOLD_D = '#8a6424'
GOLD_DD = '#4e3516'
HI_GOLD = '#ffd46b'
CREAM = '#f4e9cf'
DARK = '#1d1626'
DARKER = '#0e0a14'
SKIN = '#e0a47e'
SKIN_S = '#b8795a'
SKIN_D = '#8a5040'


# ------------------------------------------------------------------ Helfer
def _grid(rows, legend, w=None):
    return from_grid(rows, legend, w)


def _outlined(rows, legend, col=OUT, pad=1, size=None, diagonal=False):
    """Raster zeichnen, auf Zielgroesse setzen und aussen konturieren."""
    shape = _grid(rows, legend)
    w, h = size if size else (shape.w + 2 * pad, shape.h + 2 * pad)
    cv = Canvas(w, h)
    cv.paste(shape, pad, pad)
    cv.outline(col, diagonal=diagonal)
    return cv


def _layer(cv: Canvas, part: Canvas, x=0, y=0, col=OUT):
    """Teil mit eigener Kontur auf die Leinwand setzen (Ebenen trennen sich sauber)."""
    tmp = Canvas(part.w + 2, part.h + 2)
    tmp.paste(part, 1, 1)
    tmp.outline(col)
    cv.paste(tmp, x - 1, y - 1)


def _field(cv: Canvas, fn, bands, x0=0, y0=0, x1=None, y1=None):
    """Intensitaetsfeld in harte Farbstufen zerlegen (saubere Pixel-Art-Glut)."""
    x1 = cv.w if x1 is None else x1
    y1 = cv.h if y1 is None else y1
    for y in range(y0, y1):
        for x in range(x0, x1):
            v = fn(x + 0.5, y + 0.5)
            for thr, col in bands:
                if v >= thr:
                    cv.px(x, y, col)
                    break


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy), t


def _poly_dist(px, py, pts):
    best = 1e9
    for i in range(len(pts) - 1):
        d, _ = _seg_dist(px, py, *pts[i], *pts[i + 1])
        best = min(best, d)
    return best


def _radial_bg(cv: Canvas, cx, cy, stops, radius, x0=1, y0=1, x1=None, y1=None):
    """Radialer Hintergrund in festen Farbstufen (innen -> aussen)."""
    x1 = cv.w - 1 if x1 is None else x1
    y1 = cv.h - 1 if y1 is None else y1
    n = len(stops) - 1
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / radius
            i = min(n, int(d * n + 0.5))
            cv.px(x, y, stops[i])


def _spell_frame(cv: Canvas, base):
    """1px dunkler Rand und dezente Fase (Licht oben links) fuer Zaubersymbole."""
    w, h = cv.w, cv.h
    for x in range(1, w - 1):
        cv.px(x, 1, (255, 255, 255, 46))
        cv.px(x, h - 2, (0, 0, 0, 80))
    for y in range(2, h - 2):
        cv.px(1, y, (255, 255, 255, 30))
        cv.px(w - 2, y, (0, 0, 0, 64))
    cv.frame(0, 0, w, h, INK)


def _ellipse_mask(w, h, cx, cy, rx, ry):
    ys, xs = np.mgrid[0:h, 0:w]
    return (((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2) <= 1.0


def _poly_mask(w, h, pts):
    cv = Canvas(w, h)
    cv.poly(pts, (255, 255, 255, 255))
    return cv.a[:, :, 3] > 0


def _shade_mask(cv: Canvas, m, cols, cx, cy, rx, ry, bias=0.0, hi=0.45, lo=-0.4):
    """Maske mit 3 Stufen (hell, mittel, dunkel) nach Licht von oben links fuellen."""
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        nx = (x + 0.5 - cx) / rx
        ny = (y + 0.5 - cy) / ry
        light = -(0.55 * nx + 0.75 * ny) + bias
        col = cols[0] if light > hi else (cols[2] if light < lo else cols[1])
        cv.px(x, y, col)


# =================================================================== Zauber
def spell_lesser_heal():
    cv = Canvas(18, 18)
    _radial_bg(cv, 9, 7.5, ['#c9d27a', '#9ab85a', '#6f9a48', '#4a7a3c', '#2e5a34', '#1c3a2a'], 10.5)
    # sanfter Lichtschein
    _field(cv, lambda x, y: 1 - math.hypot(x - 9, y - 7.5) / 6.5,
           [(0.55, (255, 246, 196, 150)), (0.25, (255, 232, 150, 80)), (0.0, (255, 220, 120, 34))], 1, 1, 17, 17)
    # Lichtkugel mit Kreuz
    _field(cv, lambda x, y: 1 - math.hypot(x - 9, y - 7.5) / 3.6,
           [(0.45, '#fffbe6'), (0.2, '#ffe890'), (0.0, '#f2c14e')], 1, 1, 17, 17)
    for y in range(3, 12):
        cv.px(8, y, '#ffffff')
        cv.px(9, y, '#fff6d0')
    for x in range(5, 13):
        cv.px(x, 6, '#ffffff')
        cv.px(x, 7, '#fff6d0')
    for (x, y) in [(8, 2), (9, 2), (4, 6), (4, 7), (13, 6), (13, 7), (8, 12), (9, 12)]:
        cv.px(x, y, (255, 240, 170, 150))
    # Funken
    for (x, y) in [(4, 3), (14, 3), (3, 10), (14, 10)]:
        cv.px(x, y, '#fff3b0')
    # offene Hand von der Seite, Handflaeche nach oben, Daumen links
    hand = _grid([
        '.kk.............',
        'kssk............',
        'ksSk.........kk.',
        'ksSSk..kkkkkkssk',
        'kssSSkkssssssSSk',
        'GksssssssSSSSSdk',
        'WGkSssSSSdddddk.',
        'WWGkkSSddkkkkk..',
        'WWWGGkkkk.......',
    ], {'k': '#4a2818', 's': '#f8d8b4', 'S': '#e0a47e', 'd': '#b8795a', 'W': '#f6f2e8', 'G': '#f2c14e'})
    cv.paste(hand, 1, 8)
    _spell_frame(cv, '#6f9a48')
    return cv


def spell_smite():
    cv = Canvas(18, 18)
    _radial_bg(cv, 9, 12, ['#f0a040', '#d0702a', '#a8481e', '#7a2c16', '#4e1a12', '#2e0e0c'], 12)
    bolt = [(13.5, 0.5), (9.2, 6.2), (12.2, 7.4), (8.6, 14.0)]
    bolt2 = [(9.2, 6.2), (6.2, 8.2)]

    def f(x, y):
        return max(1.9 - _poly_dist(x, y, bolt), 1.1 - _poly_dist(x, y, bolt2))
    _field(cv, f, [(1.35, '#ffffff'), (0.9, '#fff3a0'), (0.35, '#ffc23a'), (-0.4, (255, 150, 40, 170))], 1, 1, 17, 17)

    # Einschlag unten
    def burst(x, y):
        dx, dy = x - 8.8, y - 14.6
        r = math.hypot(dx, dy * 1.6)
        ray = max(0, 1 - abs(dy) / 0.8) * max(0, 1 - abs(dx) / 7.5)
        return max(1 - r / 4.2, ray * 0.9)
    _field(cv, burst, [(0.7, '#ffffff'), (0.45, '#fff3a0'), (0.25, '#ffc23a'), (0.08, (255, 140, 40, 160))], 1, 1, 17, 17)
    # Splitter
    for (x, y) in [(3, 11), (14, 11), (4, 9), (15, 13), (2, 14)]:
        cv.px(x, y, '#ffd46b')
    _spell_frame(cv, '#a8481e')
    return cv


def spell_renew():
    cv = Canvas(18, 18)
    _radial_bg(cv, 9, 9, ['#8aba5a', '#5c9a4a', '#3a7a44', '#265a3c', '#173e30', '#0e2622'], 11)
    # Spirale aus Licht: Punkte der Kurve vorberechnen
    cx, cy = 9.0, 9.0
    pts = []
    n = 240
    tmax = 3.0 * math.pi
    for i in range(n + 1):
        t = i / n * tmax
        r = 0.9 + 0.62 * t
        a = t + 2.2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.95, i / n))

    def f(x, y):
        best, bt = 1e9, 0
        for (px, py, tt) in pts:
            d = (x - px) ** 2 + (y - py) ** 2
            if d < best:
                best, bt = d, tt
        width = 0.55 + 0.75 * bt
        return (width - math.sqrt(best), bt)

    cols_in = ['#ffffff', '#fff3b0', '#ffe07a']
    cols_out = ['#e8f59a', '#b8e070', '#7ec85a']
    for y in range(1, 17):
        for x in range(1, 17):
            v, t = f(x + 0.5, y + 0.5)
            if v > -0.55:
                if v > 0.35:
                    col = mix(cols_in[0], cols_out[0], t)
                elif v > 0:
                    col = mix(cols_in[1], cols_out[1], t)
                else:
                    col = mix(cols_in[2], cols_out[2], t)
                    col = (col[0], col[1], col[2], 150)
                cv.px(x, y, col)
    # Kern
    cv.px(9, 9, '#ffffff')
    cv.px(8, 9, '#fffbe0')
    # Blaetter an der Spirale
    leaf = _grid([
        '..gG',
        '.gGL',
        'gGLg',
        'dg..',
    ], {'g': '#5aa83a', 'G': '#8ed85a', 'L': '#c8f08a', 'd': '#2e6a2a'})
    cv.paste(leaf, 12, 1)
    leaf2 = _grid([
        '..dg',
        'gGLg',
        'GLg.',
        'Gg..',
    ], {'g': '#5aa83a', 'G': '#8ed85a', 'L': '#c8f08a', 'd': '#2e6a2a'}).flip_h()
    cv.paste(leaf2, 1, 12)
    for (x, y) in [(3, 4), (15, 13), (14, 8)]:
        cv.px(x, y, '#fff3b0')
    _spell_frame(cv, '#3a7a44')
    return cv


def spell_sw_pain():
    cv = Canvas(18, 18)
    _radial_bg(cv, 9, 8, ['#7a3aa0', '#5a2482', '#3e1660', '#280c42', '#16062a', '#0c0418'], 11)
    # dunkle Ranken aus den Ecken
    tend = []
    for (sx, sy, ex, ey, ph) in [(1, 16, 6, 10, 0.0), (16, 16, 12, 10, 1.2), (1, 2, 5, 6, 2.0), (16, 3, 13, 6, 0.6)]:
        seg = []
        for i in range(21):
            t = i / 20
            x = sx + (ex - sx) * t + math.sin(t * 5 + ph) * 1.3
            y = sy + (ey - sy) * t + math.cos(t * 4 + ph) * 0.8
            seg.append((x, y))
        tend.append(seg)

    def f(x, y):
        return max(1.15 - _poly_dist(x, y, s) for s in tend)
    _field(cv, f, [(0.55, '#08020e'), (0.1, '#1c0a2a'), (-0.35, (170, 90, 230, 110))], 1, 1, 17, 17)
    # Schaedel
    skull = _grid([
        '...kkkkkk...',
        '..kLLLLLLk..',
        '.kLLLLLLLbk.',
        'kLLLLLLLLbbk',
        'kLkkkLLkkkbk',
        'kLkekLLkekbk',
        'kLkkkbbkkkdk',
        '.kbbbkkbbdk.',
        '..kbbbbbdk..',
        '..kbkbkbkk..',
        '...kkkkkk...',
    ], {'k': '#0a0212', 'L': '#c8b4e4', 'b': '#8a70b0', 'd': '#54407a', 'e': '#ff7df0'})
    cv.paste(skull, 3, 4)
    # Augenglut
    for (x, y) in [(5, 8), (10, 8)]:
        cv.px(x, y, (255, 120, 240, 150))
    _spell_frame(cv, '#3e1660')
    return cv


def spell_flash_heal():
    cv = Canvas(18, 18)
    _radial_bg(cv, 9, 9, ['#fff0b0', '#ffd46b', '#f2a93a', '#d0782a', '#9a4a1c', '#5a2a12'], 11.5)
    cx, cy = 9.0, 9.0

    def star(x, y):
        dx, dy = x - cx, y - cy
        r = math.hypot(dx, dy) + 1e-6
        a = math.atan2(dy, dx)
        R = 2.4 + 6.6 * abs(math.cos(2 * a)) ** 14 + 3.6 * abs(math.sin(2 * a)) ** 14
        return R / r
    _field(cv, star, [(2.6, '#ffffff'), (1.6, '#fffbe0'), (1.05, '#fff09a'), (0.8, (255, 230, 140, 150))], 1, 1, 17, 17)
    # Tempo-Funken
    for (x, y) in [(3, 5), (14, 12), (13, 4), (4, 13)]:
        cv.px(x, y, '#ffffff')
    _spell_frame(cv, '#f2a93a')
    return cv


# ==================================================================== Auren
def _aura(bg_top, bg_bot, rows, legend):
    cv = Canvas(9, 9)
    cv.vgradient(1, 1, 7, 7, [bg_top, bg_bot], dither=False)
    cv.paste(_grid(rows, legend), 1, 1)
    cv.hline(1, 7, 1, (255, 255, 255, 40))
    cv.frame(0, 0, 9, 9, INK)
    return cv


def aura_renew():
    return _aura('#4a8a4a', '#1a4a32', [
        '..YYY..',
        '.Y...Yy',
        'Y...yYy',
        'Y.LG...',
        'Y.Gg..y',
        '.y...y.',
        '..yyy..',
    ], {'y': '#ffe07a', 'Y': '#fff3b0', 'g': '#4aa83a', 'G': '#8ed85a', 'L': '#d8f8a0'})


def aura_sw_pain():
    return _aura('#6a2a8a', '#1c0a2e', [
        '.LLLLL.',
        'LLLLLLb',
        'LkkLkkb',
        'LkeLkeb',
        'bbbkbbd',
        '.bdbdd.',
        '.d.d.d.',
    ], {'L': '#d8c4f0', 'b': '#9a7ac0', 'd': '#5a4480', 'k': '#0a0212', 'e': '#ff7df0'})


def aura_revive_weakness():
    return _aura('#46424f', '#1a1820', [
        '.......',
        '.HH.hh.',
        'HWHHhhh',
        'HHHkhhs',
        '.HHHks.',
        '..Hks..',
        '...s...',
    ], {'H': '#d4d8e4', 'W': '#ffffff', 'h': '#a4a8b8', 's': '#747888', 'k': '#141218'})


def aura_shield_wall():
    return _aura('#2a5ab0', '#0e1c48', [
        'WSSSSSs',
        'WSSGSSs',
        'SSGGGSs',
        'SSSGSSs',
        '.SSGSs.',
        '..SSs..',
        '...s...',
    ], {'W': '#e8f2ff', 'S': '#a8c4ec', 's': '#5a78b0', 'G': '#f2c14e'})


def aura_enrage():
    return _aura('#a8201c', '#3a0808', [
        '...y..y',
        '..yY..y',
        '.yYYy.y',
        'yYWWYyy',
        'yYWWWYy',
        'yYWWWYy',
        '.yYYYy.',
    ], {'y': '#ff7a2a', 'Y': '#ffc846', 'W': '#fff6c0'})


def aura_weakened():
    return _aura('#5a5664', '#24222c', [
        '...g...',
        '...h...',
        'gGGGGGg',
        '..sSd..',
        '..sSd..',
        '..sSd..',
        '...S...',
    ], {'h': '#6a4a30', 'g': '#8a8494', 'G': '#c8c2d4', 's': '#b0acb8', 'S': '#e4e0ea', 'd': '#7a7684'})


# ==================================================================== Rollen
def role_tank():
    return _grid([
        'kkkkkkk',
        'kWSSSsk',
        'kSSGSsk',
        'kSGGGsk',
        '.kSGsk.',
        '..ksk..',
        '...k...',
    ], {'k': OUT, 'W': '#d8e8ff', 'S': '#6a9ae0', 's': '#3a5aa0', 'G': '#f2c14e'})


def role_dps():
    return _grid([
        '....kkk',
        '...kWWk',
        'kk.kWsk',
        'kGkWsk.',
        '.kGsk..',
        'kbkGk..',
        'kkk.k..',
    ], {'k': OUT, 'W': '#f4f4fa', 's': '#9a9aac', 'G': '#f2c14e', 'b': '#8a5a36'})


def role_heal():
    return _grid([
        '.kkkkk.',
        'kgGWGgk',
        'kGGWGdk',
        'kWWWWWk',
        'kGGWGdk',
        'kgdWddk',
        '.kkkkk.',
    ], {'k': OUT, 'W': '#ffffff', 'G': '#5ad04a', 'g': '#8aea6a', 'd': '#2e8a2e'})


# =============================================================== Mikromenue
def micro_character():
    cv = Canvas(14, 14)
    body = _grid([
        '..yyYYYyy...',
        '.yYYYYyyyo..',
        'yYYyyyyyyoo.',
        'yYyyyyyyyooo',
        'yyyyyyyyyooo',
    ], {'Y': GOLD_L, 'y': GOLD, 'o': GOLD_M})
    head = _grid([
        '..hhhh..',
        '.hHHhhh.',
        'hHhhhhhh',
        'hhsssshh',
        'hssessSh',
        '.sssssS.',
        '..sSSS..',
    ], {'h': '#8a5a2e', 'H': '#b07a40', 's': SKIN, 'S': SKIN_S, 'e': '#2a1e3a'})
    _layer(cv, body, 1, 8)
    _layer(cv, head, 3, 1)
    return cv


def micro_spellbook():
    return _outlined([
        'sLLLLLLLLb..',
        'GBBBBBBBBbC.',
        'sBBBBYBBBbCc',
        'sBBBBYBBBbCc',
        'sBBYYWYYBbCc',
        'sBBBYYYBBbCc',
        'sBBBYBYBBbCc',
        'GBBBBBBBBbCc',
        'sBBBBBBBBbCc',
        'sbbbbbbbbbCc',
        '.ccccccccccc',
    ], {'s': '#3a1e4a', 'L': '#9a5ac8', 'B': '#6a3a9a', 'b': '#432470', 'G': GOLD, 'Y': GOLD, 'W': '#fff6d0',
        'C': CREAM, 'c': '#b8a888'}, size=(14, 14), pad=1)


def micro_talents():
    cv = Canvas(14, 14)
    crown = _grid([
        '....gGGg....',
        '..ggGLLGgg..',
        '.gGGLGGGggd.',
        '.gGGGgGgggd.',
        'gGGgggggggdd',
        'gGggggggdgdd',
        '.gggdggdddd.',
        '..dd.dd.dd..',
    ], {'g': '#5aa83a', 'G': '#8ed85a', 'L': '#c8f08a', 'd': '#2e6a2a'})
    trunk = _grid([
        '..Tt..',
        '..Tt..',
        '.TTtt.',
        'Tt..tt',
    ], {'T': '#b07a40', 't': '#6a4424'})
    _layer(cv, trunk, 4, 9)
    _layer(cv, crown, 1, 1)
    # Goldene Talentpunkte
    for (x, y) in [(4, 4), (9, 3), (7, 6)]:
        cv.px(x, y, GOLD_L)
    return cv


def micro_bags():
    # Lederbeutel mit Zugband und goldener Schnalle
    return _outlined([
        '..t.....t...',
        '..ttYYYtt...',
        '....yYy.....',
        '...tLLLt....',
        '..TLLLLLlt..',
        '.TLLLLLLLlt.',
        'TLLLLLLLLllt',
        'TLLGGGGLLllt',
        'TLLGgYGLlllt',
        'TLLGGGGLlllt',
        '.tLLlllllll.',
        '..tttttttt..',
    ], {'t': '#5e3a1e', 'T': '#d8a060', 'L': '#b07a44', 'l': '#8a5a30', 'Y': GOLD_L, 'y': GOLD_M,
        'G': '#6e4424', 'g': GOLD}, size=(14, 14), pad=1)


def micro_group():
    cv = Canvas(14, 14)

    def fig(shoulder, sh_d, hair, big=False):
        if big:
            return _grid([
                '.hhhh.',
                'hHhhhh',
                'hsssss',
                'hsesse',
                '.ssSS.',
                'AAAAAa',
                'AAAAaa',
                'AAAaaa',
            ], {'h': hair, 'H': shade(hair, 0.3), 's': SKIN, 'S': SKIN_S, 'e': '#2a1e3a', 'A': shoulder, 'a': sh_d})
        return _grid([
            '.hhh.',
            'hHhhh',
            'hssss',
            '.sSS.',
            'AAAAa',
            'AAAaa',
            'AAaaa',
        ], {'h': hair, 'H': shade(hair, 0.3), 's': SKIN, 'S': SKIN_S, 'A': shoulder, 'a': sh_d})
    _layer(cv, fig('#5a8ae0', '#2e4e9a', '#3a2a1e'), 1, 2)
    _layer(cv, fig('#e05a4a', '#9a2e2a', '#c8a050'), 8, 2)
    _layer(cv, fig('#6ad04a', '#2e8a2e', '#8a5a2e', big=True), 4, 5)
    return cv


def micro_cards():
    cv = Canvas(14, 14)
    px, py = 7.0, 14.5  # Drehpunkt unter der Mitte

    def card(angle, back=True):
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)

        def rot(x, y):
            return (px + x * ca - y * sa, py + x * sa + y * ca)
        part = Canvas(14, 14)
        outer = [rot(-2.6, -2.5), rot(2.6, -2.5), rot(2.6, -12.3), rot(-2.6, -12.3)]
        inner = [rot(-1.6, -3.5), rot(1.6, -3.5), rot(1.6, -11.3), rot(-1.6, -11.3)]
        part.poly(outer, GOLD_M)
        part.poly(inner, '#8a2e2a' if back else CREAM)
        if back:
            cx, cy = rot(0, -7.4)
            part.px(int(cx), int(cy), GOLD_L)
        return part

    for ang in (-30, 30):
        p = card(ang)
        p.outline(OUT)
        cv.paste(p, 0, 0)
    front = card(0, back=False)
    # Symbol der Vorderseite: rotes Kreuz
    for (x, y) in [(7, 4), (6, 5), (7, 5), (8, 5), (7, 6), (7, 7)]:
        front.px(x, y, '#c8403a')
    front.px(7, 4, '#f06a5a')
    front.vline(8, 9, 10, '#c8b89a')
    front.outline(OUT)
    cv.paste(front, 0, 0)
    return cv


def micro_map():
    return _outlined([
        'RRr......RRr',
        'RPPpppppppRr',
        'rPPPppPpppRr',
        'RPpPPPpPppRr',
        'rPppPxpPpXRr',
        'RPpPpPppXpRr',
        'rPPpPPPpppRr',
        'RPpppPpPppRr',
        'rPPpPPPpppRr',
        'RRr......RRr',
    ], {'R': '#d8c4a0', 'r': '#9a8060', 'P': '#f0e0b8', 'p': '#d8c498', 'x': '#c8403a', 'X': '#e0402f'},
        size=(14, 14), pad=1)


def micro_raids():
    cv = Canvas(14, 14)
    crown = _grid([
        'G..G..G.',
        'GY.GY.GY',
        'GYYGYYGY',
        'gggrgggg',
    ], {'G': GOLD_L, 'Y': GOLD, 'g': GOLD_M, 'r': '#e0402f'})
    skull = _grid([
        '..wwwwww..',
        '.wwwwwwwws',
        'wwwwwwwwws',
        'wkkkwwkkks',
        'wkrkwwkrks',
        'wkkkwkkkks',
        '.wwwkkwws.',
        '..wswswk..',
    ], {'w': '#efe9dc', 's': '#b3aa9c', 'k': INK, 'r': '#e0402f'})
    _layer(cv, skull, 2, 5)
    _layer(cv, crown, 3, 1)
    return cv


def micro_options():
    cv = Canvas(14, 14)
    cx, cy = 7.0, 7.0

    def gear(x, y):
        dx, dy = x - cx, y - cy
        r = math.hypot(dx, dy)
        a = math.atan2(dy, dx)
        tooth = 1 if math.cos(8 * a) > 0.1 else 0
        R = 4.3 + 1.6 * tooth
        if r > R or r < 1.6:
            return -1
        return 1 - (0.55 * dx + 0.75 * dy) / 6.0
    _field(cv, gear, [(1.35, '#eeeaf6'), (0.95, '#c8c2d4'), (0.0, '#8a8498')], 1, 1, 13, 13)
    # Nabe
    for (x, y) in [(5, 6), (6, 5), (7, 5), (8, 6)]:
        cv.px(x, y, '#6a6478')
    cv.outline(OUT)
    return cv


def micro_meter():
    return _outlined([
        '.........Gg.',
        '.........Gg.',
        '......Yy.Gg.',
        '......Yy.Gg.',
        '...Rr.Yy.Gg.',
        '...Rr.Yy.Gg.',
        'Bb.Rr.Yy.Gg.',
        'Bb.Rr.Yy.Gg.',
        'Bb.Rr.Yy.Gg.',
        'aaaaaaaaaaaa',
    ], {'B': '#7aa8f0', 'b': '#3a5aa0', 'R': '#f06a4a', 'r': '#a82e2a', 'Y': GOLD_L, 'y': GOLD_M,
        'G': '#8aea6a', 'g': '#2e8a2e', 'a': '#c8c2d4'}, size=(14, 14), pad=1)


# ============================================================ NPC-Portraets
PW = PH = 30


def _portrait_bg(top, bot):
    cv = Canvas(PW, PH)
    cv.vgradient(1, 1, PW - 2, PH - 2, [top, bot])
    return cv


def _finish_portrait(cv: Canvas, fig: Canvas):
    fig.outline(OUT)
    cv.paste(fig, 0, 0)
    # Lichtkante und Rahmen
    cv.hline(1, PW - 2, 1, (255, 255, 255, 40))
    cv.frame(0, 0, PW, PH, INK)
    return cv


def _eye(fig: Canvas, x, y, iris):
    fig.px(x, y, iris)
    fig.px(x + 1, y, '#ffffff')
    fig.px(x, y - 1, OUT)
    fig.px(x + 1, y - 1, OUT)


def npc_trainer():
    cv = _portrait_bg('#5a86d8', '#1c2a5a')
    # Lichtschein hinter dem Kopf
    _field(cv, lambda x, y: 1 - math.hypot(x - 16, y - 12) / 11,
           [(0.5, (255, 240, 190, 70)), (0.2, (255, 240, 190, 36))], 1, 1, 29, 29)
    fig = Canvas(PW, PH)
    W3 = ('#f6f2e8', '#d8d0c0', '#a8998a')
    # Robe / Schultern
    robe = _poly_mask(PW, PH, [(2, 30), (4, 23), (9, 20), (22, 20), (27, 23), (29, 30)])
    _shade_mask(fig, robe, ('#f0e2b8', '#d4bc88', '#9a8058'), 15, 22, 13, 8)
    # Kapuze
    hood = _ellipse_mask(PW, PH, 14.5, 12.5, 9.3, 9.5) | _poly_mask(PW, PH, [(6, 16), (22, 16), (23, 23), (6, 23)])
    _shade_mask(fig, hood, W3, 13, 11, 9, 10, bias=0.1)
    # Gesichtsoeffnung
    face = _ellipse_mask(PW, PH, 18.6, 13.8, 5.6, 6.2) & ~_poly_mask(PW, PH, [(0, 0), (30, 0), (30, 8), (0, 8)])
    trim = (_ellipse_mask(PW, PH, 18.6, 13.8, 6.8, 7.4) & hood) & ~face
    ys, xs = np.nonzero(trim)
    for y, x in zip(ys, xs):
        fig.px(x, y, '#f5c95a' if (x + 0.5 - 18.6) * 0.55 + (y + 0.5 - 13.8) * 0.75 < 0 else '#b8862e')
    # Stola in Gold auf der Robe
    for y in range(21, 30):
        fig.px(9, y, '#f5c95a')
        fig.px(10, y, '#b8862e')
    _shade_mask(fig, face, (SKIN, SKIN, SKIN_S), 18, 12, 6, 6, bias=0.3)
    # Augenbrauen weiss und buschig
    for (x, y) in [(15, 11), (16, 11), (17, 11), (19, 11), (20, 11), (21, 11), (22, 11)]:
        fig.px(x, y, '#f4f0ea')
    fig.px(15, 12, '#c8c0b8')
    fig.px(22, 12, '#c8c0b8')
    # Augen (alt, etwas schmal)
    for (x, iris) in [(16, '#3a5a9a'), (20, '#3a5a9a')]:
        fig.px(x, 13, iris)
        fig.px(x + 1, 13, '#ffffff')
        fig.px(x, 12, SKIN_S)
        fig.px(x + 1, 12, SKIN_S)
    # Falten
    fig.px(22, 14, SKIN_S)
    # Nase
    fig.px(23, 14, SKIN)
    fig.px(23, 15, SKIN_S)
    fig.px(24, 15, SKIN_S)
    # Bart
    beard = _poly_mask(PW, PH, [(13.5, 15.5), (24.5, 15.5), (24, 20), (21, 25), (19, 27.5), (16, 24), (13, 19)])
    # weiche Kante trennt den Bart von Kapuze und Robe
    ring = np.zeros_like(beard)
    ring[1:, :] |= beard[:-1, :]
    ring[:, 1:] |= beard[:, :-1]
    ring[:, :-1] |= beard[:, 1:]
    ring &= ~beard
    ring[:17, :] = False
    for y, x in zip(*np.nonzero(ring)):
        fig.px(x, y, '#6e6660')
    _shade_mask(fig, beard, ('#ffffff', '#ece6de', '#b8b0a8'), 18, 18, 6, 6, bias=0.2)
    # Straehnen
    for (x, y) in [(16, 19), (17, 21), (20, 20), (19, 23), (22, 18)]:
        fig.px(x, y, '#c8c0b8')
    # Schnurrbart
    for x in range(17, 25):
        fig.px(x, 16, '#ffffff' if x < 21 else '#e8e2da')
    fig.px(20, 17, '#8a5040')
    fig.px(21, 17, '#8a5040')
    _finish_portrait(cv, fig)
    return cv


def npc_blacksmith():
    cv = _portrait_bg('#e88a3a', '#3a1410')
    # Esse-Funken
    for (x, y) in [(4, 5), (25, 4), (27, 9), (3, 12), (7, 3)]:
        cv.px(x, y, '#ffd46b')
    fig = Canvas(PW, PH)
    # Hammer ueber der linken (hinteren) Schulter
    handle = _poly_mask(PW, PH, [(6, 6), (8, 5.5), (11, 22), (9, 22.5)])
    _shade_mask(fig, handle, ('#b07a40', '#8a5a30', '#5e3a1e'), 8, 12, 2, 6)
    head_h = _poly_mask(PW, PH, [(1.5, 3), (11, 1.5), (12, 7), (2.5, 8.5)])
    _shade_mask(fig, head_h, ('#d8d4e0', '#9a96a8', '#5e5a6c'), 6, 5, 5, 3)
    fig.outline(OUT)
    # Schultern: dunkles Hemd, kraeftig, darauf Lederschuerze
    body = _poly_mask(PW, PH, [(1, 30), (2, 24), (7, 19.5), (23, 19.5), (28, 24), (29, 30)])
    _shade_mask(fig, body, ('#5a4a5e', '#3e3044', '#2a2030'), 15, 22, 14, 8)
    apron = _poly_mask(PW, PH, [(9, 30), (10, 21), (21, 21), (23, 30)])
    _shade_mask(fig, apron, ('#b07a44', '#8a5a30', '#5e3a1e'), 16, 25, 7, 6)
    # Schuerzen-Riemen
    for (x, y) in [(9, 20), (10, 21), (21, 21), (22, 20)]:
        fig.px(x, y, '#5e3a1e')
    # Kopf (breit, kahl mit Stirnband)
    head = _ellipse_mask(PW, PH, 16.5, 12.5, 7.2, 6.8)
    _shade_mask(fig, head, (SKIN, SKIN, SKIN_S), 15.5, 11, 7, 7, bias=0.2)
    # Glanz auf der Glatze
    fig.px(13, 7, '#f4c8a4')
    fig.px(14, 7, '#f4c8a4')
    fig.px(12, 8, '#f4c8a4')
    # Stirnband rot
    for x in range(9, 24):
        yy = 9 if x > 13 else 10
        if head[yy, x]:
            fig.px(x, yy, '#c8403a' if x < 20 else '#8a2e2a')
    # Ohr
    fig.px(11, 13, SKIN_S)
    fig.px(11, 14, SKIN_S)
    fig.px(12, 13, '#8a5040')
    # Augenbrauen buschig, rot
    for (x, y) in [(15, 11), (16, 11), (19, 11), (20, 11), (21, 11)]:
        fig.px(x, y, '#8a3a1e')
    _eye(fig, 16, 13, '#3a5a9a')
    _eye(fig, 20, 13, '#3a5a9a')
    # Nase, knollig
    for (x, y) in [(22, 14), (23, 14), (23, 15), (22, 15)]:
        fig.px(x, y, SKIN if y == 14 else SKIN_S)
    # Russ
    for (x, y) in [(14, 12), (13, 15), (19, 10), (18, 15)]:
        fig.px(x, y, (40, 30, 34, 150))
    # Grosser roter Bart mit Zoepfen
    beard = _poly_mask(PW, PH, [(12, 14.5), (23.5, 15), (24.5, 19), (22, 24), (19, 25.5), (15, 24), (12, 19)])
    _shade_mask(fig, beard, ('#e0783a', '#b8502a', '#7a301c'), 18, 18, 6, 6, bias=0.1)
    for (x, y) in [(15, 18), (16, 20), (19, 19), (20, 22), (22, 18)]:
        fig.px(x, y, '#7a301c')
    # Zopf mit Goldring
    for y in range(25, 29):
        fig.px(18, y, '#b8502a')
        fig.px(19, y, '#7a301c')
    fig.px(18, 26, GOLD)
    fig.px(19, 26, GOLD_M)
    # Mund im Bart
    fig.px(20, 17, '#5a1e14')
    fig.px(21, 17, '#5a1e14')
    _finish_portrait(cv, fig)
    return cv


def npc_weaponmaster():
    cv = _portrait_bg('#9a3a3a', '#281016')
    fig = Canvas(PW, PH)
    # Schwertgriff hinter der Schulter (Ruecken links)
    grip = _poly_mask(PW, PH, [(5, 5), (7, 4), (9, 12), (7, 12.5)])
    _shade_mask(fig, grip, ('#8a5a36', '#6a4424', '#4a2e18'), 7, 8, 2, 4)
    pommel = _ellipse_mask(PW, PH, 5.8, 4.2, 1.7, 1.7)
    _shade_mask(fig, pommel, (GOLD_L, GOLD, GOLD_M), 5.8, 4.2, 1.5, 1.5)
    guard = _poly_mask(PW, PH, [(3, 13), (12, 10.5), (12.5, 12.5), (3.5, 15)])
    _shade_mask(fig, guard, (GOLD_L, GOLD, GOLD_D), 8, 12, 4, 2)
    fig.outline(OUT)
    # Lederruestung
    body = _poly_mask(PW, PH, [(1, 30), (2, 24), (7, 20), (23, 20), (28, 24), (29, 30)])
    _shade_mask(fig, body, ('#9a6a3e', '#744a2a', '#4e301c'), 15, 22, 14, 8)
    # Schulterstueck
    pad = _ellipse_mask(PW, PH, 6.5, 23.5, 5.5, 4)
    _shade_mask(fig, pad, ('#b88a52', '#8a5e34', '#5a3a1e'), 6.5, 23, 5, 4)
    # Nieten
    for (x, y) in [(4, 22), (7, 21), (9, 23)]:
        fig.px(x, y, '#d8d4e0')
    # Riemen quer ueber die Brust
    for i in range(10):
        x, y = 8 + i * 2, 29 - i
        fig.px(x, y, '#3a2414')
        fig.px(x + 1, y, '#3a2414')
    fig.px(16, 25, GOLD)
    # Hals
    for y in range(18, 21):
        for x in range(14, 20):
            fig.px(x, y, SKIN_S)
    # Kopf
    head = _ellipse_mask(PW, PH, 16.5, 11.5, 6.4, 6.6)
    _shade_mask(fig, head, (SKIN, SKIN, SKIN_S), 15.5, 10, 6, 7, bias=0.2)
    # Kurzes dunkles Haar
    hair = (_ellipse_mask(PW, PH, 15.5, 9.0, 7.0, 5.0) & ~_poly_mask(PW, PH, [(17, 9.5), (30, 7), (30, 30), (14, 30)]))
    hair |= _ellipse_mask(PW, PH, 11.5, 11.5, 2.2, 4.2)
    _shade_mask(fig, hair, ('#5a4032', '#3a2a22', '#241a16'), 14, 8, 7, 5, bias=0.1)
    # Ohr
    fig.px(12, 12, SKIN)
    fig.px(12, 13, SKIN_S)
    fig.px(13, 12, SKIN_S)
    # Brauen, ernst
    for (x, y) in [(15, 10), (16, 10), (19, 10), (20, 10), (21, 10)]:
        fig.px(x, y, '#241a16')
    _eye(fig, 16, 12, '#4a6a3a')
    _eye(fig, 20, 12, '#4a6a3a')
    # Narbe quer ueber das rechte Auge
    for (x, y) in [(23, 8), (22, 9), (22, 10), (22, 11), (21, 13), (21, 14), (20, 15)]:
        fig.px(x, y, '#9a3a3a')
    for (x, y) in [(23, 9), (23, 10), (22, 14)]:
        fig.px(x, y, '#f4c8b0')
    # Nase
    fig.px(22, 13, SKIN)
    fig.px(22, 14, SKIN_S)
    # Stoppeln / Kinn
    for y in range(16, 19):
        for x in range(13, 24):
            if head[y, x] and (x + y) % 2 == 0:
                fig.px(x, y, '#c8906e' if fig.get(x, y)[:3] == c(SKIN)[:3] else '#9a6450')
    fig.px(19, 15, '#8a5040')
    fig.px(20, 15, '#8a5040')
    _finish_portrait(cv, fig)
    return cv


# ================================================================= Sonstiges
def lock():
    return _grid([
        '..kkk..',
        '.kgggk.',
        '.kg.gk.',
        'kkkkkkk',
        'kYYYYgk',
        'kYGkYgk',
        'kYYkYgk',
        'kggggdk',
        'kkkkkkk',
    ], {'k': OUT, 'g': GOLD_M, 'Y': GOLD, 'G': GOLD_L, 'd': GOLD_D})


DOT = [
    '...#####...',
    '.#########.',
    '.#########.',
    '###########',
    '###########',
    '###########',
    '###########',
    '###########',
    '.#########.',
    '.#########.',
    '...#####...',
]


def _erode(m):
    e = m.copy()
    e[1:, :] &= m[:-1, :]
    e[:-1, :] &= m[1:, :]
    e[:, 1:] &= m[:, :-1]
    e[:, :-1] &= m[:, 1:]
    e[0, :] = e[-1, :] = False
    e[:, 0] = e[:, -1] = False
    return e


def _dot(fill, ring=None, shine=False):
    """Runder 11x11-Punkt: Kontur, optional Ring, Kern ueber Funktion fill(x, y)."""
    cv = Canvas(11, 11)
    m = np.array([[ch == '#' for ch in row] for row in DOT])
    e1 = _erode(m)
    e2 = _erode(e1)
    for y in range(11):
        for x in range(11):
            if not m[y, x]:
                continue
            if not e1[y, x]:
                cv.px(x, y, OUT)
            elif ring and not e2[y, x]:
                cv.px(x, y, ring[0] if (x + 0.5 - 5.5) * 0.55 + (y + 0.5 - 5.5) * 0.75 < 0.3 else ring[1])
            else:
                cv.px(x, y, fill(x, y))
    if shine:
        cv.px(3, 3, '#fffbe6')
        cv.px(4, 3, '#fff3b0')
        cv.px(3, 4, '#fff3b0')
    return cv


def _gold_ball(x, y):
    light = -(0.55 * (x + 0.5 - 5.5) + 0.75 * (y + 0.5 - 5.5)) / 4.2
    if light > 0.35:
        return GOLD_L
    if light < -0.45:
        return GOLD_M
    return GOLD


def _dark_hole(x, y):
    # vertiefte Mulde: oben Schatten, unten leichter Widerschein
    return '#08060c' if y < 4 else ('#221a2c' if y > 6 else '#120e18')


def _locked(x, y):
    return '#1a1422' if y < 4 else ('#2e2539' if y > 6 else '#241c2e')


def wave_locked():
    return _dot(_locked, ring=('#4a3e56', '#2e2539'))


def wave_open():
    return _dot(_dark_hole, ring=(GOLD_L, GOLD_M))


def wave_done():
    return _dot(_gold_ball, shine=True)


BOSS_SKULL = [
    '.###.',
    '#####',
    '#.#.#',
    '.###.',
    '.#.#.',
]


def _boss(cv: Canvas, col, hole=None):
    for y, row in enumerate(BOSS_SKULL):
        for x, ch in enumerate(row):
            if ch == '#':
                cv.px(3 + x, 3 + y, col)
            elif hole is not None and 1 <= y <= 3 and 0 < x < 4:
                cv.px(3 + x, 3 + y, hole)
    return cv


def wave_boss_locked():
    cv = wave_locked()
    return _boss(cv, '#5e5668')


def wave_boss_open():
    cv = _dot(_dark_hole, ring=('#ff6a4a', '#b02a24'))
    return _boss(cv, '#efe9dc', '#0a070e')


def wave_boss_done():
    cv = _dot(_gold_ball)
    _boss(cv, '#3a1a10')
    return cv


def wave_current():
    cv = Canvas(15, 15)
    cx = cy = 7.5
    for y in range(15):
        for x in range(15):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if 5.6 < d <= 6.6:
                cv.px(x, y, '#fff3b0' if (x + y) < 14 else HI_GOLD)
            elif 6.6 < d <= 7.5:
                cv.px(x, y, (255, 212, 107, 130))
            elif 5.0 < d <= 5.6:
                cv.px(x, y, (255, 230, 150, 90))
    return cv


# ------------------------------------------------------- Symbole 13x13
def icon_dummy():
    cv = Canvas(13, 13)
    # Pfahl und Querholz
    for y in range(3, 12):
        cv.px(6, y, '#8a5a30')
        cv.px(7, y, '#5e3a1e')
    for x in range(1, 12):
        cv.px(x, 6, '#a0703f')
        cv.px(x, 7, '#6e4424')
    cv.px(5, 11, '#8a5a30')
    cv.px(8, 11, '#5e3a1e')
    # Strohbuendel an den Armen
    for (x, y) in [(1, 5), (1, 8), (11, 5), (11, 8), (0, 6), (12, 7)]:
        cv.px(x, y, '#e8c860')
    # Koerper-Sack mit Zielscheibe
    body = _grid([
        '.sSSSs.',
        'sSSSSSs',
        'SSRWRSs',
        'SRWRWRs',
        'SSRWRSs',
        'sSSSSss',
        '.sssss.',
    ], {'s': '#b8a070', 'S': '#d8c490', 'R': '#d0403a', 'W': '#f4e9cf'})
    cv.paste(body, 3, 4)
    # Kopf-Sack
    head = _grid([
        '.hhh.',
        'hHHhh',
        'hHhhd',
        '.hdd.',
    ], {'h': '#c8b080', 'H': '#e8d4a0', 'd': '#9a8458'})
    cv.paste(head, 4, 0)
    cv.px(5, 2, '#5e3a1e')
    cv.px(7, 2, '#5e3a1e')
    cv.outline(OUT)
    return cv


def icon_swords():
    cv = Canvas(13, 13)
    o = 1
    for i in range(7):
        # Schwert 1: Klinge von oben links, Schwert 2 gespiegelt
        cv.px(o + i + 1, o + i, '#9a9aac')
        cv.px(o + 9 - i, o + i, '#9a9aac')
    for i in range(7):
        cv.px(o + i, o + i, '#f4f4fa')
        cv.px(o + 10 - i, o + i, '#f4f4fa')
    cv.px(o + 5, o + 5, '#ffffff')
    # Parierstangen (quer zur Klinge)
    for (x, y) in [(8, 6), (7, 7), (6, 8)]:
        cv.px(o + x, o + y, GOLD)
        cv.px(o + 10 - x, o + y, GOLD)
    cv.px(o + 8, o + 6, GOLD_L)
    cv.px(o + 2, o + 6, GOLD_L)
    # Griffe und Knauf
    for (x, y) in [(8, 8), (9, 9)]:
        cv.px(o + x, o + y, '#8a5a36')
        cv.px(o + 10 - x, o + y, '#6a4424')
    cv.px(o + 10, o + 10, GOLD_M)
    cv.px(o + 0, o + 10, GOLD_M)
    cv.outline(OUT)
    return cv


def icon_auto():
    return _outlined([
        'Yy...Yy....',
        'YYy..YYy...',
        '.YYy..YYy..',
        '..YYy..YYy.',
        '...YYo..YYo',
        '..YYo..YYo.',
        '.YYo..YYo..',
        'YYo..YYo...',
        'Yo...Yo....',
    ], {'Y': GOLD_L, 'y': GOLD, 'o': GOLD_M}, size=(13, 13), pad=1)


def icon_repeat():
    cv = Canvas(13, 13)
    cx, cy = 6.0, 6.8

    def ring(x, y):
        d = math.hypot(x - cx, y - cy)
        a = math.degrees(math.atan2(y - cy, x - cx))
        if 2.2 <= d <= 4.4 and not (-82 <= a <= -8):
            return 1 - (0.55 * (x - cx) + 0.75 * (y - cy)) / 4.4
        return -1
    _field(cv, ring, [(1.3, GOLD_L), (0.75, GOLD), (0.0, GOLD_M)], 1, 1, 12, 12)
    # Pfeilspitze am Ende oben, zeigt im Uhrzeigersinn nach rechts
    cv.poly([(6.0, 0.6), (10.6, 3.4), (6.0, 6.2)], GOLD)
    cv.px(6, 1, GOLD_L)
    cv.px(6, 2, GOLD_L)
    cv.px(7, 2, GOLD_L)
    cv.outline(OUT)
    return cv


def icon_map():
    return _outlined([
        'PPPpQQQqPPP',
        'PGGpQBBqPPP',
        'PGGpQBQqPxP',
        'PPGpQQQqxPP',
        'PPPpQQxqPPp',
        'PPPxQQQqPGG',
        'PPxpQQQqPGG',
        'PxPpQBBqPPP',
        'XpPpQQQqPPP',
        'pppqqqqqppp',
    ], {'P': '#f0e0b8', 'p': '#c8b490', 'Q': '#e0d0a8', 'q': '#a89470', 'G': '#7ab85a', 'B': '#6a9ad8',
        'x': '#c8403a', 'X': '#e0402f'}, size=(13, 13), pad=1)


def icon_raid():
    return _outlined([
        'S.S.....S.S',
        'SSS.S.S.SSS',
        'SLSSSSSSSLs',
        'SLSSSSSSsLs',
        'SLSSdddSsLs',
        'SLSdIIIdsLs',
        'SLSdIgIdsLs',
        'SLSdIIIdsLs',
        'SLSdIgIdsLs',
        'sssdIIIdsss',
    ], {'S': '#b8b0c0', 's': '#7a7288', 'L': '#d8d2e0', 'd': '#3a2a1e', 'I': '#6e5a4a', 'g': GOLD_M},
        size=(13, 13), pad=1)


def icon_skull_red():
    return _outlined([
        '..rrrrrr...',
        '.rRRRrrrr..',
        'rRRrrrrrrd.',
        'rkkkrrkkkd.',
        'rkWkrrkWkd.',
        'rkkkrkkkkd.',
        '.rrrkkrrd..',
        '..rdrdrd...',
        '..kdkdkd...',
    ], {'r': '#d8403a', 'R': '#f07a5a', 'd': '#8a2020', 'k': '#2a0a0a', 'W': '#ffd46b'},
        size=(13, 13), pad=1)


# --------------------------------------------------- Aktionsleisten-Platz
def _slot(edge_tl, edge_br, corner, inner=None):
    cv = Canvas(22, 22)
    cv.frame(0, 0, 22, 22, INK)
    cv.hline(1, 20, 1, edge_tl)
    cv.vline(1, 1, 20, edge_tl)
    cv.hline(1, 20, 20, edge_br)
    cv.vline(20, 1, 20, edge_br)
    for (x, y) in [(1, 1), (20, 1), (1, 20), (20, 20)]:
        cv.px(x, y, corner)
    if inner:
        inner(cv)
    return cv


def _slot_inner_empty(cv: Canvas):
    cv.rect(2, 2, 18, 18, '#0c0911')
    # Innenschatten oben links (vertieft)
    cv.hline(2, 19, 2, '#050307')
    cv.vline(2, 2, 19, '#050307')
    cv.hline(3, 19, 3, '#08060c')
    # Rautenmuster, sehr dezent
    for y in range(4, 19):
        for x in range(4, 19):
            if (x + y) % 4 == 0 and (x - y) % 8 == 0:
                cv.px(x, y, '#1a1422')
            elif (x + y) % 8 == 0 and (x - y) % 4 == 0:
                cv.px(x, y, '#151019')
    # kleines Kreuzsiegel in der Mitte
    for (x, y) in [(10, 9), (11, 9), (10, 12), (11, 12), (9, 10), (9, 11), (12, 10), (12, 11)]:
        cv.px(x, y, '#231a2c')
    cv.hline(3, 19, 19, '#1a1422')


def slot():
    return _slot(GOLD_DD, GOLD_M, GOLD_D)


def slot_hover():
    return _slot(GOLD_M, GOLD_L, GOLD)


def slot_pressed():
    return _slot('#fff3b0', '#ffffff', GOLD_L)


def slot_empty():
    return _slot(GOLD_DD, GOLD_M, GOLD_D, _slot_inner_empty)


# ------------------------------------------------------- Einheitenrahmen
def _unitframe(edge_hi, edge_lo, inner_hi, inner_lo):
    """16x16, 9-Slice mit 3px Raendern: Kontur, Kante, Innenkante; Mitte flach."""
    cv = Canvas(16, 16)
    cv.rect(1, 1, 14, 14, '#16111d')
    cv.rect(3, 3, 10, 10, '#1a1422')
    # Kontur mit abgerundeten Ecken
    cv.frame(0, 0, 16, 16, OUT)
    for (x, y) in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        cv.clear_px(x, y)
    # Kante (Licht oben/links heller)
    cv.hline(1, 14, 1, edge_hi)
    cv.vline(1, 1, 14, edge_hi)
    cv.hline(1, 14, 14, edge_lo)
    cv.vline(14, 2, 14, edge_lo)
    for (x, y) in [(1, 1), (14, 1), (1, 14), (14, 14)]:
        cv.px(x, y, OUT)
    # Innenkante
    cv.hline(2, 13, 2, inner_hi)
    cv.vline(2, 2, 13, inner_hi)
    cv.hline(2, 13, 13, inner_lo)
    cv.vline(13, 3, 13, inner_lo)
    return cv


def unitframe():
    return _unitframe(GOLD_D, GOLD_DD, '#0a070e', '#231a2c')


def unitframe_target():
    return _unitframe('#fff6d6', GOLD_L, GOLD_M, GOLD_D)


def unitframe_aggro():
    return _unitframe('#ff6a4a', '#d0302a', '#8a1c1a', '#5a1212')


# ================================================================== Aufbau
ICONS = [
    # Zauber 18x18
    ('spell_lesser_heal', spell_lesser_heal),
    ('spell_smite', spell_smite),
    ('spell_renew', spell_renew),
    ('spell_sw_pain', spell_sw_pain),
    ('spell_flash_heal', spell_flash_heal),
    # Auren 9x9
    ('aura_renew', aura_renew),
    ('aura_sw_pain', aura_sw_pain),
    ('aura_revive_weakness', aura_revive_weakness),
    ('aura_shield_wall', aura_shield_wall),
    ('aura_enrage', aura_enrage),
    ('aura_weakened', aura_weakened),
    # Rollen 7x7
    ('role_tank', role_tank),
    ('role_dps', role_dps),
    ('role_heal', role_heal),
    # Mikromenue 14x14
    ('micro_character', micro_character),
    ('micro_spellbook', micro_spellbook),
    ('micro_talents', micro_talents),
    ('micro_bags', micro_bags),
    ('micro_group', micro_group),
    ('micro_cards', micro_cards),
    ('micro_map', micro_map),
    ('micro_raids', micro_raids),
    ('micro_options', micro_options),
    ('micro_meter', micro_meter),
    # NPC-Portraets 30x30
    ('npc_trainer', npc_trainer),
    ('npc_blacksmith', npc_blacksmith),
    ('npc_weaponmaster', npc_weaponmaster),
    # Sonstiges
    ('lock', lock),
    ('wave_locked', wave_locked),
    ('wave_open', wave_open),
    ('wave_done', wave_done),
    ('wave_boss_locked', wave_boss_locked),
    ('wave_boss_open', wave_boss_open),
    ('wave_boss_done', wave_boss_done),
    ('wave_current', wave_current),
    ('icon_dummy', icon_dummy),
    ('icon_swords', icon_swords),
    ('icon_auto', icon_auto),
    ('icon_repeat', icon_repeat),
    ('icon_map', icon_map),
    ('icon_raid', icon_raid),
    ('icon_skull_red', icon_skull_red),
    ('slot', slot),
    ('slot_hover', slot_hover),
    ('slot_pressed', slot_pressed),
    ('slot_empty', slot_empty),
    ('unitframe', unitframe),
    ('unitframe_target', unitframe_target),
    ('unitframe_aggro', unitframe_aggro),
]

# 9-Slice-Raender (links, oben, rechts, unten)
SLICES = {
    'unitframe': [3, 3, 3, 3],
    'unitframe_target': [3, 3, 3, 3],
    'unitframe_aggro': [3, 3, 3, 3],
    'slot': [2, 2, 2, 2],
    'slot_hover': [2, 2, 2, 2],
    'slot_pressed': [2, 2, 2, 2],
    'slot_empty': [2, 2, 2, 2],
}


def build(root):
    out = os.path.join(root, 'assets', 'gfx', 'combat')
    made = {}
    for name, fn in ICONS:
        cv = fn()
        cv.save(os.path.join(out, name + '.png'))
        made[name] = cv
    return made


def nine_slice(cv: Canvas, w, h, m):
    """Textur per 9-Slice auf w x h strecken (nur fuer die Vorschau)."""
    l, t, r, b = m
    out = Canvas(w, h)
    sx = [0, l, cv.w - r, cv.w]
    sy = [0, t, cv.h - b, cv.h]
    dx = [0, l, w - r, w]
    dy = [0, t, h - b, h]
    for j in range(3):
        for i in range(3):
            for y in range(dy[j], dy[j + 1]):
                for x in range(dx[i], dx[i + 1]):
                    fx = sx[i] + (x - dx[i]) % max(1, sx[i + 1] - sx[i])
                    fy = sy[j] + (y - dy[j]) % max(1, sy[j + 1] - sy[j])
                    out.a[y, x] = cv.a[fy, fx]
    return out


def _demo(made: dict) -> Canvas:
    """Anwendungsbeispiel: Einheitenrahmen, Aktionsleiste, Wellenleiste."""
    d = Canvas(300, 64)
    # Einheitenrahmen, 9-Slice gestreckt
    for k, nm in enumerate(['unitframe', 'unitframe_target', 'unitframe_aggro']):
        fr = nine_slice(made[nm], 56, 22, SLICES[nm])
        d.paste(fr, 2 + k * 60, 2)
        d.paste(made[['role_tank', 'role_heal', 'role_dps'][k]], 6 + k * 60, 6)
    d.paste(made['aura_shield_wall'], 46, 13)
    d.paste(made['aura_renew'], 106, 13)
    d.paste(made['aura_sw_pain'], 156, 13)
    d.paste(made['aura_renew'], 146, 13)
    # Aktionsleiste
    x = 2
    for nm, st in [('spell_lesser_heal', 'slot'), ('spell_flash_heal', 'slot_hover'), ('spell_renew', 'slot'),
                   ('spell_smite', 'slot_pressed'), ('spell_sw_pain', 'slot'), (None, 'slot_empty')]:
        d.paste(made[st], x, 30)
        if nm:
            d.paste(made[nm], x + 2, 32)
        x += 23
    d.paste(made['lock'], x - 23 + 7, 30 + 6)
    # Wellenleiste
    x = 150
    seq = ['wave_done', 'wave_done', 'wave_done', 'wave_boss_done', 'wave_open', 'wave_open',
           'wave_boss_open', 'wave_locked', 'wave_locked', 'wave_boss_locked']
    for k, nm in enumerate(seq):
        d.paste(made[nm], x + k * 14, 36)
    d.paste(made['wave_current'], x + 4 * 14 - 2, 34)
    return d


def preview(made: dict, path: str, scale=4):
    """Uebersicht: alle Icons beschriftet im Raster (x4, daneben 1x), auf dunklem Grund."""
    font = ImageFont.load_default()
    cols = 7
    cell_w = 150
    groups = [
        ('Zauber 18x18', [n for n in made if n.startswith('spell_')]),
        ('Auren 9x9 / Rollen 7x7 / Schloss', [n for n in made if n.startswith(('aura_', 'role_'))] + ['lock']),
        ('Mikromenue 14x14', [n for n in made if n.startswith('micro_')]),
        ('NPC-Portraets 30x30', [n for n in made if n.startswith('npc_')]),
        ('Wellen 11x11 / 15x15', [n for n in made if n.startswith('wave_')]),
        ('Symbole 13x13', [n for n in made if n.startswith('icon_')]),
        ('Plaetze 22x22 / Einheitenrahmen 16x16', [n for n in made if n.startswith(('slot', 'unitframe'))]),
    ]
    rows = []
    for title, names in groups:
        for i in range(0, len(names), cols):
            chunk = names[i:i + cols]
            hh = max(made[n].h for n in chunk) * scale + 30
            rows.append((title if i == 0 else None, chunk, hh))
    demo = _demo(made)
    total_h = sum(hh + (18 if t else 0) for t, _, hh in rows) + demo.h * 3 + 40
    img = Image.new('RGBA', (cols * cell_w + 16, total_h), c(DARK))
    dr = ImageDraw.Draw(img)
    y = 6
    for title, chunk, hh in rows:
        if title:
            dr.text((8, y), title, fill=c(HI_GOLD), font=font)
            y += 18
        for k, n in enumerate(chunk):
            cv = made[n]
            gx = 8 + k * cell_w
            big = cv.image().resize((cv.w * scale, cv.h * scale), Image.NEAREST)
            img.alpha_composite(big, (gx, y))
            img.alpha_composite(cv.image(), (gx + cv.w * scale + 6, y))
            dr.text((gx, y + cv.h * scale + 4), f'{n} {cv.w}x{cv.h}', fill=c(CREAM), font=font)
        y += hh
    dr.text((8, y), 'Beispiel (x3): Einheitenrahmen, Aktionsleiste, Wellenleiste', fill=c(HI_GOLD), font=font)
    y += 18
    img.alpha_composite(demo.image().resize((demo.w * 3, demo.h * 3), Image.NEAREST), (8, y))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', 'healer-simulator')
    made = build(root)
    preview(made, os.path.join(here, '..', '..', 'output', 'kampf', 'icons_preview.png'))
    print(f'{len(made)} Icons geschrieben nach {os.path.normpath(os.path.join(root, "assets", "gfx", "combat"))}')
