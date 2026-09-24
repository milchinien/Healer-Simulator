"""Alle Hintergrund-Szenen. Jede Szene liefert Ebenen + Metadaten (Lichtpunkte usw.)."""
from __future__ import annotations

import math

import numpy as np

import scenery as S
from pa import Canvas, c, mix, shade, BAYER4, rng

W, H = S.W, S.H


def castle_silhouette(cv: Canvas, x, y_base, col, lit='#ffcf6a', seed=3):
    r = rng(seed)
    # Mauer
    cv.rect(x, y_base - 22, 120, 22, col)
    for k in range(0, 120, 6):
        cv.rect(x + k, y_base - 25, 3, 3, col)
    towers = [(x - 6, 44, 14), (x + 30, 60, 16), (x + 70, 52, 12), (x + 112, 40, 14)]
    for (tx, th, tw) in towers:
        cv.rect(tx, y_base - th, tw, th, col)
        cv.poly([(tx - 2, y_base - th), (tx + tw + 1, y_base - th), (tx + tw / 2, y_base - th - tw * 0.9)], shade(col, -0.2))
        for k in range(2):
            wy = y_base - th + 8 + k * 12
            if r.random() < 0.8:
                cv.rect(tx + tw // 2 - 1, wy, 2, 3, lit)
        # Wimpel
        px_ = int(tx + tw / 2)
        top = int(y_base - th - tw * 0.9)
        cv.vline(px_, top - 7, top, '#2a2230')
        cv.poly([(px_ + 1, top - 7), (px_ + 7, top - 5), (px_ + 1, top - 3)], '#b8352c')
    for k in range(10):
        if r.random() < 0.5:
            cv.rect(x + 6 + k * 11, y_base - 14, 2, 3, lit)


def stone_dais(cv: Canvas, cx, cy, rx, ry, top, side, rune):
    cv.ellipse(cx, cy + 4, rx + 1, ry + 1, '#0e0a14')
    cv.ellipse(cx, cy + 3, rx, ry, side)
    cv.ellipse(cx, cy, rx, ry, top)
    cv.ellipse(cx, cy - 1, rx - 3, ry - 2, shade(top, 0.08))
    # Runenring
    for k in range(48):
        a = k / 48 * 2 * math.pi
        x = cx + math.cos(a) * (rx - 5)
        y = cy + math.sin(a) * (ry - 3)
        if k % 3 != 0:
            cv.px(x, y, rune)
    cv.ellipse(cx, cy, rx * 0.45, ry * 0.45, shade(top, -0.06))


# ============================================================ Charakterauswahl
def distant_town(cv: Canvas, y_base, col, col_roof, lit, seed=0, x0=0, x1=W):
    """Silhouetten entfernter Daecher mit vereinzelten Lichtern."""
    r = rng(seed)
    x = x0
    while x < x1:
        w_ = r.randint(12, 26)
        h_ = r.randint(10, 24)
        cv.rect(x, y_base - h_, w_, h_ + 40, col)
        cv.poly([(x - 2, y_base - h_), (x + w_ + 1, y_base - h_), (x + w_ / 2, y_base - h_ - w_ * 0.45)], col_roof)
        for _ in range(r.randint(0, 3)):
            wx = x + r.randint(2, max(3, w_ - 4))
            wy = y_base - h_ + r.randint(3, max(4, h_ - 4))
            cv.rect(wx, wy, 2, 2, lit)
        if r.random() < 0.3:
            S.round_tree(cv, x + w_ + 2, y_base + 2, r.randint(16, 24), '#1c1530', '#261d3c', '#322650', seed=x)
        x += w_ + r.randint(-2, 3)


def charselect():
    bg = Canvas(W, H)
    S.sky(bg, ['#141132', '#2b2152', '#5a3466', '#a5506a', '#e98a5c', '#f7c07a'], 0, 205)
    S.stars(bg, 11, 110, 80)
    S.glow_disc(bg, 520, 58, 9, 26, '#fff1d0', '#ffd49a')
    bg.circle(516, 55, 2, '#f4dcb8')
    bg.circle(523, 62, 1, '#f0d4ae')
    S.mountains(bg, 21, 212, 52, '#3d2d5c', '#56407a', '#2e2248')
    castle_silhouette(bg, 250, 200, '#2c2046')
    S.hills(bg, 5, 212, 8, '#261c3c', '#35284f')
    distant_town(bg, 238, '#2a2042', '#221a38', '#e8a860', seed=4)
    distant_town(bg, 252, '#342848', '#2a1f3c', '#ffc070', seed=8)
    # Haeuserreihen (Abendlicht: kuehle Waende, warme Fenster)
    wall, wall_d, timber = '#6e5e74', '#54465c', '#261a26'
    wall2, wall2_d = '#7a6a6e', '#5c4e56'
    roof, roof_d = '#5a2634', '#3e1824'
    roof2, roof2_d = '#3e3252', '#2a2238'
    S.house(bg, -10, 266, 58, 56, wall, wall_d, timber, roof, roof_d, seed=1)
    S.house(bg, 52, 262, 44, 62, wall2, wall2_d, timber, roof2, roof2_d, seed=2)
    S.house(bg, 100, 258, 36, 40, wall, wall_d, timber, roof, roof_d, seed=3, chimney=False)
    S.house(bg, 318, 258, 40, 42, wall2, wall2_d, timber, roof, roof_d, seed=4)
    S.house(bg, 362, 262, 56, 58, wall, wall_d, timber, roof2, roof2_d, seed=5)
    S.house(bg, 424, 266, 62, 64, wall2, wall2_d, timber, roof, roof_d, seed=6)
    S.house(bg, 490, 266, 70, 52, wall, wall_d, timber, roof2, roof2_d, seed=7)
    S.house(bg, 566, 266, 80, 66, wall2, wall2_d, timber, roof, roof_d, seed=8)
    # Platz
    S.cobblestones(bg, 266, H, '#4a3e54', '#6a5a72', '#1e1626', seed=9)
    # Lichtschein der Laternen auf dem Pflaster
    for (lx, ly) in [(118, 304), (360, 304)]:
        for y in range(266, H):
            for x in range(lx - 80, lx + 80):
                d = math.hypot((x - lx) / 80, (y - ly) / 44)
                if d < 1 and (1 - d) * 0.6 > BAYER4[y % 4, x % 4] and bg.inside(x, y):
                    bg.a[y, x] = mix(bg.get(x, y), '#e0a060', 0.3)
    stone_dais(bg, 226, 294, 58, 13, '#6e6278', '#3a3046', '#ffd46b')
    lights = []
    lights.append(S.lantern_post(bg, 110, 304))
    lights.append(S.lantern_post(bg, 352, 304))
    S.vignette(bg, 0.6)
    clouds = S.clouds_layer(W, 140, 31, (18, 125), '#f7b08a', '#b8667a', '#6a3f66', density=0.56, scale=60)
    return {'bg': bg, 'clouds': clouds}, {'lights': lights, 'stand': (226, 294)}


# ============================================================ Titelbildschirm
def title():
    bg = Canvas(W, H)
    S.sky(bg, ['#070616', '#0f0d2a', '#1c1846', '#2e2462', '#4a3474'], 0, 250)
    S.stars(bg, 3, 420, 230)
    S.glow_disc(bg, 470, 70, 16, 44, '#f2f0ff', '#9ea8ff', steps=6)
    bg.circle(465, 66, 3, '#d6d8f2')
    bg.circle(476, 76, 2, '#dcdef4')
    bg.circle(470, 60, 1, '#dcdef4')
    S.peaks(bg, [(40, 150, 90), (150, 172, 80), (250, 188, 70), (420, 176, 80), (520, 132, 110),
                 (620, 160, 90)], '#211e48', '#3a3676', '#16143a', 300, snow='#aab0e6', snow_dark='#5a5c98', seed=3)
    S.peaks(bg, [(-10, 210, 70), (90, 222, 60), (190, 228, 70), (380, 214, 60), (470, 226, 70), (590, 206, 80)],
            '#171534', '#26235a', '#0f0d26', 300, seed=5)
    # Kapelle auf dem Huegel mit Lichtsaeule
    hill_ys = S.hills(bg, 2, 286, 18, '#0f1826', '#1b2a3a', freq=0.8)
    chx = 320
    base = hill_ys[chx] + 2
    stone, stone_l, stone_d = '#3e3c62', '#56547e', '#2a2848'
    roof_c, roof_l = '#2a2446', '#3a3460'
    lit, lit_h = '#ffd46b', '#fff6d0'
    # Kirchenschiff
    bg.rect(chx - 30, base - 30, 60, 30, stone)
    bg.rect(chx + 18, base - 30, 12, 30, stone_d)
    for yy in range(base - 28, base, 4):            # Steinfugen
        for xx in range(chx - 30 + (yy // 4 % 2) * 3, chx + 30, 7):
            bg.px(xx, yy, stone_d)
    bg.hline(chx - 30, chx + 29, base - 30, stone_l)
    bg.poly([(chx - 34, base - 29), (chx + 34, base - 29), (chx + 20, base - 44), (chx - 20, base - 44)], roof_c)
    bg.line(chx - 34, base - 29, chx - 20, base - 44, roof_l)
    bg.hline(chx - 20, chx + 20, base - 44, roof_l)
    # Spitzbogenfenster
    for wx in (chx - 24, chx - 12, chx + 8):
        bg.rect(wx, base - 22, 5, 10, stone_d)
        bg.rect(wx + 1, base - 21, 3, 9, lit)
        bg.px(wx + 2, base - 22, lit)
        bg.px(wx + 1, base - 21, lit_h)
    # Tor
    bg.rect(chx - 4, base - 14, 9, 14, stone_d)
    bg.rect(chx - 3, base - 13, 7, 13, '#ffcf6a')
    bg.px(chx, base - 14, '#ffcf6a')
    bg.vline(chx, base - 13, base - 1, '#d09a3a')
    # Turm
    bg.rect(chx - 8, base - 72, 16, 42, stone)
    bg.rect(chx + 3, base - 72, 5, 42, stone_d)
    bg.vline(chx - 8, base - 72, base - 30, stone_l)
    bg.rect(chx - 3, base - 64, 6, 10, stone_d)
    bg.rect(chx - 2, base - 63, 4, 9, lit)
    bg.px(chx - 2, base - 63, lit_h)
    bg.rect(chx - 2, base - 44, 4, 6, lit)
    bg.poly([(chx - 10, base - 72), (chx + 10, base - 72), (chx, base - 92)], roof_c)
    bg.line(chx - 10, base - 72, chx, base - 92, roof_l)
    # Symbol oben (Sonnenkreuz)
    bg.vline(chx, base - 101, base - 93, '#f2c14e')
    bg.hline(chx - 3, chx + 3, base - 98, '#f2c14e')
    bg.px(chx, base - 98, '#fff6d0')
    # Waldsilhouetten vorne
    fg = Canvas(W, H)
    r = rng(12)
    for x in range(-10, W + 10, 9):
        h_ = r.randint(26, 52)
        S.pine(fg, x + r.randint(-3, 3), H - 38 + r.randint(0, 10), h_, '#070b12', '#0b121c', '#132030',
               trunk='#070b12')
    fg.rect(0, H - 34, W, 34, '#070b12')
    S.vignette(bg, 0.7)
    clouds = S.clouds_layer(W, 200, 44, (30, 190), '#4a4a86', '#2c2a5e', '#1c1a44', density=0.6, scale=60)
    return {'bg': bg, 'fg': fg, 'clouds': clouds}, {'lights': [(chx, base - 60), (chx, base - 8)], 'beam': (chx, base - 98)}
