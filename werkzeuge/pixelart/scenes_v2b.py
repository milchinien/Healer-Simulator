"""Szenen Version 2 (Teil 2): Titel, Rassen-Hintergruende, Ladebildschirm."""
from __future__ import annotations

import math

import props as P
import scenery as S
import world as Wd
from pa import Canvas, mix, shade, BAYER4, rng
from scenes_v2 import W, H, _clouds, _pal_a
from scenes_race import arch_mask, arch_frame, _floor_tiles


def _pal_day_a():
    return {'wall': '#f0e6d0', 'wall_d': '#d0c4a8', 'stone': '#c8c0b4', 'stone_d': '#a09888', 'timber': '#6a4a2e',
            'roof': '#2f5aa8', 'roof_d': '#244480', 'shutter': '#2d5ab0'}


def _pal_day_b():
    return {'wall': '#e8dcc0', 'wall_d': '#c4b494', 'stone': '#c0b8ac', 'stone_d': '#989080', 'timber': '#5a3e26',
            'roof': '#b8452e', 'roof_d': '#8a3222', 'shutter': '#4a7a3a'}


# ============================================================ Titel: naechtliches Tal mit Kapelle und See
def _chapel(bg, chx, base):
    stone, stone_l, stone_d = '#3e3c62', '#56547e', '#2a2848'
    roof_c, roof_l = '#2a2446', '#3a3460'
    lit, lit_h = '#ffd46b', '#fff6d0'
    bg.rect(chx - 30, base - 30, 60, 30, stone)
    bg.rect(chx + 18, base - 30, 12, 30, stone_d)
    for yy in range(base - 28, base, 4):
        for xx in range(chx - 30 + (yy // 4 % 2) * 3, chx + 30, 7):
            bg.px(xx, yy, stone_d)
    bg.hline(chx - 30, chx + 29, base - 30, stone_l)
    bg.poly([(chx - 34, base - 29), (chx + 34, base - 29), (chx + 20, base - 44), (chx - 20, base - 44)], roof_c)
    bg.line(chx - 34, base - 29, chx - 20, base - 44, roof_l)
    bg.hline(chx - 20, chx + 20, base - 44, roof_l)
    lights = []
    for wx in (chx - 24, chx - 12, chx + 8):
        bg.rect(wx, base - 22, 5, 10, stone_d)
        bg.rect(wx + 1, base - 21, 3, 9, lit)
        bg.px(wx + 2, base - 22, lit)
        bg.px(wx + 1, base - 21, lit_h)
        lights.append((wx + 2, base - 17))
    bg.rect(chx - 4, base - 14, 9, 14, stone_d)
    bg.rect(chx - 3, base - 13, 7, 13, '#ffcf6a')
    bg.vline(chx, base - 13, base - 1, '#d09a3a')
    bg.rect(chx - 8, base - 72, 16, 42, stone)
    bg.rect(chx + 3, base - 72, 5, 42, stone_d)
    bg.vline(chx - 8, base - 72, base - 30, stone_l)
    bg.rect(chx - 3, base - 64, 6, 10, stone_d)
    bg.rect(chx - 2, base - 63, 4, 9, lit)
    bg.rect(chx - 2, base - 44, 4, 6, lit)
    bg.poly([(chx - 10, base - 72), (chx + 10, base - 72), (chx, base - 92)], roof_c)
    bg.line(chx - 10, base - 72, chx, base - 92, roof_l)
    bg.vline(chx, base - 101, base - 93, '#f2c14e')
    bg.hline(chx - 3, chx + 3, base - 98, '#f2c14e')
    bg.px(chx, base - 98, '#fff6d0')
    return lights + [(chx, base - 59), (chx, base - 7)]


def title():
    bg = Canvas(W, H)
    sprites, props = {}, []
    S.sky(bg, ['#070616', '#0f0d2a', '#1c1846', '#2e2462', '#4a3474'], 0, 262)
    S.stars(bg, 3, 460, 240)
    S.glow_disc(bg, 560, 74, 16, 44, '#f2f0ff', '#9ea8ff', steps=6)
    for (dx, dy, r_) in [(-5, -4, 3), (6, 6, 2), (0, -8, 1), (7, -3, 1)]:
        bg.circle(560 + dx, 74 + dy, r_, '#d6d8f2')
    S.peaks(bg, [(40, 150, 90), (150, 172, 80), (250, 188, 70), (420, 176, 80), (520, 132, 110), (620, 160, 90)],
            '#211e48', '#3a3676', '#16143a', 300, snow='#aab0e6', snow_dark='#5a5c98', seed=3)
    S.peaks(bg, [(-10, 214, 70), (90, 226, 60), (190, 230, 70), (380, 218, 60), (470, 228, 70), (590, 210, 80)],
            '#171534', '#26235a', '#0f0d26', 300, seed=5)
    # Dorf am Fuss der Berge mit Lichtern
    r = rng(8)
    for k in range(9):
        hx = 40 + k * 17 + r.randint(-3, 3)
        base = 262 + r.randint(-2, 2)
        hw, hh = r.randint(10, 14), r.randint(7, 11)
        bg.rect(hx, base - hh, hw, hh + 6, '#141228')
        bg.poly([(hx - 2, base - hh), (hx + hw + 1, base - hh), (hx + hw / 2, base - hh - 6)], '#100e22')
        if r.random() < 0.7:
            wx, wy = hx + r.randint(2, hw - 3), base - hh + 3
            bg.rect(wx, wy, 2, 2, '#ffcf6a')
            props.append({'type': 'glow', 'tex': 'glow_tiny', 'x': wx + 1, 'y': wy + 1, 'alpha': 0.7, 'flicker': 0.1})
    hill_ys = S.hills(bg, 2, 282, 16, '#0f1826', '#1b2a3a', freq=0.8)
    chx = 320
    base = hill_ys[chx] + 2
    for (x, y) in _chapel(bg, chx, base):
        props.append({'type': 'glow', 'tex': 'glow_small', 'x': x, 'y': y, 'alpha': 0.55, 'flicker': 0.06})
    props.append({'type': 'beam', 'x': chx, 'y': base - 98})
    # See im Tal mit Spiegelungen
    lake_top = 288
    for y in range(lake_top, 322):
        t = (y - lake_top) / 34
        half = 250 - (1 - t) * 30 + math.sin(y * 0.4) * 2
        for x in range(int(320 - half), int(320 + half)):
            col = mix('#1a2046', '#0c1026', t)
            if BAYER4[y % 4, x % 4] < 0.25:
                col = mix(col, '#262c5a', 0.4)
            bg.px(x, y, col)
        bg.px(320 - half, y, '#2a3a4a')
        bg.px(320 + half, y, '#2a3a4a')
    for y in range(lake_top + 2, 320, 2):   # Mondspiegelung
        wdt = 3 + (y - lake_top) // 5
        for x in range(530 - wdt, 530 + wdt):
            if (x + y) % 3 != 0:
                bg.px(x, y, '#9ea8ff' if abs(x - 530) < wdt // 2 else '#5a64a8')
    for y in range(lake_top + 3, 312, 3):   # Kapellenlicht im Wasser
        bg.hline(chx - 3, chx + 3, y, '#b0883a' if y % 2 else '#7a5e2a')
    sprites['title_shimmer'] = P.shimmer_sheet(460, 32, 9, frames=8, col='#cfd6ff', density=0.01)
    props.append({'type': 'anim', 'tex': 'title_shimmer', 'x': 90, 'y': lake_top + 1, 'vframes': 8, 'fps': 5,
                  'additive': True, 'alpha': 0.7})
    # Weg zur Kapelle mit kleinen Laternen
    path = [(60, 360), (120, 332), (210, 318), (250, 300), (300, 290), (316, 276)]
    for a, b in zip(path, path[1:]):
        for k in range(-1, 2):
            bg.line(a[0] + k, a[1], b[0] + k, b[1], '#2a2a3a')
    for (x, y) in path[1:-1]:
        bg.vline(x + 5, y - 6, y, '#1a1822')
        bg.px(x + 5, y - 7, '#ffcf6a')
        props.append({'type': 'glow', 'tex': 'glow_small', 'x': x + 5, 'y': y - 7, 'alpha': 0.8, 'flicker': 0.15})
    # Wald vorne (eigene Ebene ueber allem)
    fg = Canvas(W, H)
    r = rng(12)
    for x in range(-10, W + 10, 8):
        if 150 < x < 490 and r.random() < 0.8:
            continue
        h_ = r.randint(30, 60) if (x < 150 or x > 490) else r.randint(16, 26)
        S.pine(fg, x + r.randint(-3, 3), H - 36 + r.randint(0, 10), h_, '#070b12', '#0b121c', '#132030', trunk='#070b12')
    fg.rect(0, H - 34, W, 34, '#070b12')
    for x in range(0, W, 3):
        fg.vline(x, H - 36 - (x * 7 % 3), H - 34, '#0b121c')
    S.vignette(bg, 0.65)
    cs, cp = _clouds('title', [
        ((10, 80), ('#3e3e7a', '#2a2860', '#1c1a44'), 0.6, 70, 1.0, 44, 90),
        ((40, 150), ('#4a4a86', '#2c2a5e', '#1c1a44'), 0.6, 60, 2.2, 45, 160),
        ((120, 200), ('#5a5a96', '#34326a', '#22204c'), 0.64, 46, 3.6, 46, 210),
    ])
    sprites.update(cs)
    props = cp + props
    props.append({'type': 'particles', 'kind': 'fireflies', 'x': 320, 'y': 300, 'w': 300, 'h': 40})
    props.append({'type': 'particles', 'kind': 'stars_twinkle', 'x': 320, 'y': 100, 'w': 320, 'h': 100})
    return {'layers': {'bg': bg, 'fg': fg}, 'sprites': sprites, 'props': props, 'stand': (320, 290)}


# ============================================================ Mensch: Innenhof der weissen Stadt
def human_city():
    bg = Canvas(W, H)
    sprites, props = {}, []
    S.sky(bg, ['#3a78c8', '#5a98dc', '#8cc0ec', '#c4e2f6'], 0, 230)
    S.peaks(bg, [(90, 150, 110), (250, 170, 90), (420, 140, 120), (580, 160, 100)],
            '#8aa0c4', '#b4c6e2', '#6a80a8', 240, snow='#f4f8ff', snow_dark='#c4d0e6', seed=4)
    wall, wall_l, wall_d = '#d8d4cc', '#f0ece4', '#a8a298'
    bg.rect(0, 150, W, 110, wall)
    for x in range(0, W, 8):
        bg.rect(x, 144, 5, 6, wall)
        bg.px(x, 144, wall_l)
        bg.px(x + 4, 145, wall_d)
    for y in range(154, 260, 6):
        for x in range((y // 6 % 2) * 6, W, 12):
            bg.hline(x, x + 10, y, wall_d)
            bg.px(x, y - 3, wall_d)
    bg.hline(0, W - 1, 150, wall_l)
    bg.hline(0, W - 1, 170, '#bcb6ac')
    gx = 320
    bg.rect(252, 110, 136, 150, wall)
    for x in range(252, 388, 8):
        bg.rect(x, 104, 5, 6, wall)
    bg.hline(252, 387, 110, wall_l)
    for y in range(114, 260, 6):
        for x in range(252 + (y // 6 % 2) * 6, 388, 12):
            bg.hline(x, x + 10, y, wall_d)
    flag, fw = P.flag_sheet(14, 8, '#2d5ab0', '#1f4288', emblem='#f2c14e')
    sprites['human_flag'] = flag
    for tx in (220, 388):
        bg.rect(tx, 96, 32, 164, wall)
        bg.rect(tx + 24, 96, 8, 164, wall_d)
        bg.vline(tx, 96, 259, wall_l)
        bg.poly([(tx - 4, 97), (tx + 36, 97), (tx + 16, 56)], '#2f5aa8')
        bg.poly([(tx + 16, 56), (tx + 36, 97), (tx + 18, 97)], '#244480')
        bg.line(tx - 4, 97, tx + 16, 56, '#5a86d0')
        for yy in range(64, 97, 5):
            bg.hline(int(tx + 16 - (yy - 56) * 0.48), int(tx + 16 + (yy - 56) * 0.48), yy, '#284c94')
        props.append({'type': 'anim', 'tex': 'human_flag', 'x': tx + 15, 'y': 40, 'hframes': 6, 'fps': 8})
        bg.rect(tx + 12, 120, 8, 12, '#3a3040')
        bg.rect(tx + 13, 121, 6, 10, '#9ab8e0')
        bg.rect(tx + 8, 150, 16, 46, '#2d5ab0')
        bg.vline(tx + 23, 150, 195, '#1f4288')
        bg.hline(tx + 8, tx + 23, 150, '#f2c14e')
        bg.poly([(tx + 8, 196), (tx + 24, 196), (tx + 16, 204)], '#2d5ab0')
        for (dx, dy) in [(15, 162), (16, 162), (14, 163), (15, 163), (16, 163), (17, 163), (15, 164), (16, 164),
                         (15, 165), (16, 165), (14, 166), (17, 166), (15, 167), (16, 167)]:
            bg.px(tx + dx, dy, '#f2c14e')
    # Durchblick durch das Tor: Hauptstrasse der Stadt
    arch = arch_mask(gx, 258, 44, 112)
    view = Canvas(W, H)
    S.sky(view, ['#8cc0ec', '#c4e2f6'], 140, 90)
    for (hx, hw, hh, pal, sd) in [(268, 34, 44, _pal_day_a(), 1), (300, 30, 50, _pal_day_b(), 2),
                                  (334, 38, 42, _pal_day_a(), 3)]:
        Wd.townhouse(view, hx, 232, hw, hh, pal, seed=sd, lit_chance=0.0, chimney=False, flowers=True)
    Wd.perspective_cobbles(view, 232, 262, (320, 200), '#b8b2a8', '#dcd6cc', '#8a847c', seed=5)
    for (x, y) in arch:
        p = view.get(x, y)
        if p[3]:
            bg.px(x, y, p)
    for k in range(9):   # hochgezogenes Fallgitter
        bg.vline(gx - 40 + k * 10, 146, 156, '#4a4450')
        bg.px(gx - 40 + k * 10, 157, '#2a2630')
    bg.hline(gx - 42, gx + 42, 150, '#4a4450')
    arch_frame(bg, gx, 258, 44, 112, 6, wall_l, wall_d, accent='#f2c14e')
    Wd.perspective_cobbles(bg, 258, H, (320, 200), '#aca8a2', '#d0ccc6', '#76726c', seed=21)
    for x in range(0, W):   # Blumenbeete an der Mauer
        if 214 < x < 426:
            continue
        bg.rect(x, 256, 1, 4, '#5a4a3a')
        bg.px(x, 255, ['#e04a5a', '#ffd46b', '#5aa048', '#e070b0', '#4a8a3a', '#4a8a3a'][x * 7 % 6])
    for tx_ in (40, 120, 520, 600):
        bg.rect(tx_ - 8, 268, 17, 8, '#b8b2a8')
        bg.frame(tx_ - 8, 268, 17, 8, '#8a847c')
        Wd.round_tree(bg, tx_, 270, 60, '#2e5a2a', '#4a8a3a', '#78b85a', seed=tx_)
    wx, wy = 500, 318   # Brunnen
    bg.ellipse(wx, wy, 20, 6, '#8a847c')
    bg.ellipse(wx, wy - 1, 18, 5, '#c8c4bc')
    bg.ellipse(wx, wy - 1, 15, 3.5, '#4a7ab8')
    bg.rect(wx - 2, wy - 16, 5, 14, '#c8c4bc')
    bg.ellipse(wx, wy - 17, 6, 2, '#b8b2a8')
    sprites['human_fountain'] = P.shimmer_sheet(30, 7, 3, frames=6, col='#ffffff', density=0.05)
    props.append({'type': 'anim', 'tex': 'human_fountain', 'x': wx - 15, 'y': wy - 4, 'vframes': 6, 'fps': 6,
                  'additive': True, 'alpha': 0.8})
    props.append({'type': 'particles', 'kind': 'fountain', 'x': wx, 'y': wy - 18})
    Wd.mosaic_circle(bg, 320, 288, 56, 12, '#c8c4bc', '#8a847c', '#3a6ac8', '#2a4a8a')
    S.vignette(bg, 0.35)
    cs, cp = _clouds('human_city', [
        ((6, 60), ('#ffffff', '#e8eef8', '#c4d4e8'), 0.6, 70, 1.2, 71, 70),
        ((20, 120), ('#ffffff', '#dfeaf6', '#b4c8e0'), 0.57, 64, 2.6, 72, 130),
        ((90, 150), ('#ffffff', '#e6eef8', '#bcd0e4'), 0.63, 46, 4.2, 73, 160),
    ])
    sprites.update(cs)
    props = cp + props
    props.append({'type': 'particles', 'kind': 'birds', 'x': 320, 'y': 60, 'w': 320, 'h': 40})
    props.append({'type': 'particles', 'kind': 'leaves', 'x': 320, 'y': -10, 'w': 340, 'h': 4})
    return {'layers': {'bg': bg}, 'sprites': sprites, 'props': props, 'stand': (320, 288)}


# ============================================================ Zwerg: Schmiedehalle im Berg
def dwarf_hall():
    bg = Canvas(W, H)
    sprites, props = {}, []
    stone, stone_l, stone_d, ink = '#4a4250', '#625868', '#2e2834', '#16121a'
    bg.rect(0, 0, W, H, '#221c28')
    for y in range(0, 262, 12):
        off = (y // 12 % 2) * 20
        for x in range(-off, W, 40):
            bg.rect(x + 1, y + 1, 38, 10, stone)
            bg.hline(x + 1, x + 38, y + 1, stone_l)
            bg.hline(x + 1, x + 38, y + 10, stone_d)
    for k in range(-3, 4):   # Gewoelberippen
        cx = 320 + k * 130
        for a in range(0, 181, 2):
            x = cx + math.cos(math.radians(a)) * 70
            y = 40 - math.sin(math.radians(a)) * 36
            bg.rect(int(x) - 1, int(y), 3, 3, stone_d)
    gx, gy = 320, 262
    for (x, y) in arch_mask(gx, gy, 70, 190):
        t = (y - (gy - 190)) / 190
        col = mix('#3a1a10', '#ff8a2a', max(0.0, t) ** 1.8)
        if BAYER4[y % 4, x % 4] < 0.5:
            col = mix(col, '#1a0c08', 0.2)
        bg.px(x, y, col)
    bg.poly([(gx - 40, gy - 16), (gx + 40, gy - 16), (gx + 26, gy - 110), (gx - 26, gy - 110)], '#2a1410')
    bg.rect(gx - 14, gy - 60, 28, 20, '#ff9a3a')
    bg.rect(gx - 12, gy - 58, 24, 16, '#ffd070')
    bg.hline(gx - 16, gx + 15, gy - 61, '#1a0c08')
    bg.rect(gx - 70, gy - 16, 141, 16, '#ff9a3a')
    for x in range(gx - 70, gx + 71):
        bg.px(x, gy - 16 + (x * 7 % 3), '#ffd070')
    bg.rect(gx - 20, gy - 42, 40, 10, '#1a1014')
    bg.rect(gx - 10, gy - 32, 20, 16, '#1a1014')
    bg.rect(gx - 28, gy - 44, 14, 4, '#1a1014')
    props.append({'type': 'glow', 'tex': 'glow_forge', 'x': gx, 'y': gy - 50, 'alpha': 0.55, 'flicker': 0.1})
    arch_frame(bg, gx, gy, 70, 190, 7, stone_l, stone_d, ink=ink, accent='#ffb04a')
    for px_ in (70, 190, 450, 570):
        bg.rect(px_ - 16, 0, 32, 262, stone)
        bg.rect(px_ + 8, 0, 8, 262, stone_d)
        bg.vline(px_ - 16, 0, 261, stone_l)
        bg.rect(px_ - 20, 236, 40, 26, stone_l)
        bg.rect(px_ - 20, 250, 40, 12, stone_d)
        bg.frame(px_ - 20, 236, 40, 26, ink)
        bg.rect(px_ - 20, 0, 40, 12, stone_l)
        bg.frame(px_ - 20, 0, 40, 12, ink)
        for y in range(40, 230, 44):
            for d in range(6):
                bg.px(px_ - d, y + d, '#ffb04a')
                bg.px(px_ + d, y + d, '#c87a2a')
                bg.px(px_ - d, y + 12 - d, '#ffb04a')
                bg.px(px_ + d, y + 12 - d, '#c87a2a')
            props.append({'type': 'glow', 'tex': 'glow_rune', 'x': px_, 'y': y + 6, 'alpha': 0.5, 'flicker': 0.35,
                          'speed': 0.4})
    for bx in (117, 497):
        bg.rect(bx, 40, 26, 90, '#8a2020')
        bg.vline(bx + 25, 40, 129, '#5a1414')
        bg.hline(bx, bx + 25, 40, '#f2c14e')
        bg.poly([(bx, 130), (bx + 26, 130), (bx + 13, 142)], '#8a2020')
        bg.rect(bx + 8, 70, 10, 8, '#f2c14e')
        bg.rect(bx + 12, 78, 2, 20, '#c99a3a')
    for cx_ in (238, 402):   # Kettenlampen
        for y in range(0, 120, 3):
            bg.px(cx_ + (y // 3) % 2, y, '#5a4a52')
        bg.rect(cx_ - 5, 120, 11, 8, '#2a2228')
        bg.rect(cx_ - 3, 122, 7, 5, '#ffcf6a')
        props.append({'type': 'glow', 'tex': 'glow_small', 'x': cx_, 'y': 124, 'alpha': 0.8, 'flicker': 0.15})
    _floor_tiles(bg, 262, H, '#3a3440', '#4e4656', '#1e1a22')
    for side in (-1, 1):   # Lavarinnen im Boden
        for y in range(266, H):
            t = (y - 262) / 98
            xc = 320 + side * (120 + t * 170)
            for x in range(int(xc - 2 - t * 5), int(xc + 3 + t * 5)):
                bg.px(x, y, '#ff8a2a' if (x + y) % 5 else '#ffd070')
            bg.px(int(xc - 3 - t * 5), y, '#2a1410')
            bg.px(int(xc + 3 + t * 5), y, '#2a1410')
        props.append({'type': 'glow', 'tex': 'glow_lava', 'x': int(320 + side * 210), 'y': 320, 'alpha': 0.45,
                      'flicker': 0.12, 'speed': 0.6})
    for y in range(262, H):
        for x in range(gx - 170, gx + 170):
            d = math.hypot((x - gx) / 170, (y - 262) / 70)
            if d < 1 and (1 - d) * 0.7 > BAYER4[y % 4, x % 4] and bg.inside(x, y):
                bg.a[y, x] = mix(bg.get(x, y), '#ff8a3a', 0.22)
    for y in range(290, H, 4):   # Lore auf Schienen
        bg.hline(0, 90 - (y - 290) // 2, y, '#5a4a3a')
    bg.line(0, 300, 110, 290, '#8a8a92')
    bg.line(0, 312, 120, 302, '#8a8a92')
    bg.rect(40, 276, 34, 18, '#4a3e36')
    bg.frame(40, 276, 34, 18, ink)
    bg.hline(41, 72, 277, '#6a5a4a')
    for k in range(6):
        bg.circle(46 + k * 5, 275, 3, ['#8a7a6a', '#c8a050', '#7a6a5a'][k % 3])
    bg.circle(48, 295, 3, '#2a2228')
    bg.circle(66, 294, 3, '#2a2228')
    Wd.mosaic_circle(bg, 320, 290, 56, 12, '#6a6070', '#3a3440', '#ffb04a', '#c87a2a')
    for (fx, fy) in [(130, 226), (510, 226)]:   # Kohlebecken
        bg.rect(fx - 10, fy, 21, 6, '#2a2228')
        bg.rect(fx - 4, fy + 6, 9, 30, '#2a2228')
        bg.rect(fx - 12, fy + 34, 25, 4, '#2a2228')
        bg.hline(fx - 10, fx + 10, fy, '#5a4a52')
        props.append({'type': 'fire', 'x': fx, 'y': fy})
    S.vignette(bg, 0.65)
    props.append({'type': 'particles', 'kind': 'embers', 'x': 320, 'y': 250, 'w': 70, 'h': 6})
    return {'layers': {'bg': bg}, 'sprites': sprites, 'props': props, 'stand': (320, 290)}


# ============================================================ Orc: Lager in der Steppe
def orc_steppe():
    bg = Canvas(W, H)
    sprites, props = {}, []
    S.sky(bg, ['#2a1030', '#6a1e38', '#b8363a', '#e8683a', '#f8a850', '#ffd88a'], 0, 250)
    S.glow_disc(bg, 470, 200, 24, 64, '#fff0c0', '#ffb060', steps=6)
    # Tafelberge: trapezfoermig, geschichtet, mit verwitterten Kanten (Licht von der Sonne rechts)
    r = rng(17)
    for (mx, mw, mt, far) in [(10, 170, 150, False), (196, 96, 182, True), (372, 70, 194, True), (500, 160, 138, False)]:
        base = 252
        body, lit, dark, strata = ('#6a2a36', '#9a4a44', '#4a1a2a', '#5a2230') if not far else             ('#7a3a44', '#a8584e', '#5a2a38', '#6a3240')
        top_jag = [r.randint(-2, 1) for _ in range(mw + 40)]
        for x in range(mx - 16, mx + mw + 16):
            # Flanken schraeg nach aussen, Kante leicht gezackt
            t_left = (x - (mx - 16)) / 16
            t_right = ((mx + mw + 16) - x) / 16
            edge = min(1.0, t_left, t_right)
            top = mt + top_jag[(x - mx + 16) % len(top_jag)] + (1 - edge) * (base - mt)
            for y in range(int(top), base):
                col = body
                if x > mx + mw - 18:
                    col = lit if BAYER4[y % 4, x % 4] < 0.8 else body
                elif x < mx + 10:
                    col = dark
                if (y - mt) % 11 in (0, 1) and y > top + 2:
                    col = strata if col == body else shade(col, -0.15)
                bg.px(x, y, col)
            bg.px(x, int(top), shade(lit, 0.15) if x > mx + mw * 0.4 else body)
        for _ in range(mw // 10):   # Felsrinnen
            rx = r.randint(mx + 6, mx + mw - 6)
            bg.vline(rx, mt + 4, base - r.randint(4, 30), dark)
    S.hills(bg, 9, 252, 6, '#8a4a2a', '#b06a3a', tex_col='#7a3e22')
    bg.rect(0, 256, W, H - 256, '#a0603a')
    for y in range(256, H):
        for x in range(W):
            if BAYER4[y % 4, x % 4] < (y - 256) / 200:
                bg.px(x, y, '#8a4e2e')
    for (x0, x1) in [(236, 90), (236, 170), (320, 470), (320, 570)]:   # Trampelpfade
        for k in range(-2, 3):
            bg.line(x0, 290 + k, x1, 262 + k // 2, '#b8784a')
    S.grass_tufts(bg, 4, 258, H, 900, ['#c8a050', '#a8803a', '#e0c070'])
    banner, bw = P.flag_sheet(10, 16, '#a82a2a', '#6a1818', emblem='#1a1014')
    sprites['orc_banner'] = banner
    for (tx, ty, tw) in [(70, 258, 64), (160, 252, 42), (478, 254, 48), (568, 264, 74)]:
        bg.poly([(tx - tw / 2, ty), (tx + tw / 2, ty), (tx, ty - tw * 0.8)], '#8a5a3a')
        bg.poly([(tx, ty - tw * 0.8), (tx + tw / 2, ty), (tx + 4, ty)], '#5e3a24')
        bg.poly([(tx - 5, ty), (tx + 5, ty), (tx, ty - tw * 0.35)], '#2a1410')
        for k in (-1, 1):
            bg.line(int(tx), int(ty - tw * 0.8), int(tx + k * 5), int(ty - tw * 0.8 - 8), '#e8dcc0')
        for k in range(3):
            y = int(ty - tw * 0.2 - k * tw * 0.18)
            bg.hline(int(tx - tw * (0.4 - k * 0.1)), int(tx + tw * (0.4 - k * 0.1)), y, '#3e2416')
        for k in range(-2, 3, 2):
            bg.line(int(tx), int(ty - tw * 0.8), int(tx + k * tw * 0.2), ty, '#6e4630')
        props.append({'type': 'anim', 'tex': 'orc_banner', 'x': int(tx + tw * 0.25), 'y': int(ty - tw * 0.95) - 6,
                      'hframes': 6, 'fps': 7})
    tx, ty = 412, 290   # Totempfahl
    bg.rect(tx - 3, ty - 50, 7, 50, '#6a4028')
    bg.vline(tx - 3, ty - 50, ty, '#8a5a38')
    for k, col in enumerate(['#b8352c', '#2a6a8a', '#e8b84a']):
        bg.rect(tx - 5, ty - 44 + k * 12, 11, 4, col)
    bg.circle(tx, ty - 54, 5, '#efe9dc')
    bg.rect(tx - 2, ty - 55, 2, 2, '#1a1014')
    bg.rect(tx + 1, ty - 55, 2, 2, '#1a1014')
    bg.line(tx - 8, ty - 60, tx - 4, ty - 56, '#efe9dc')
    bg.line(tx + 8, ty - 60, tx + 4, ty - 56, '#efe9dc')
    bg.rect(120, 292, 30, 3, '#5a3a24')   # Waffenstaender
    for k in range(3):
        bg.line(124 + k * 10, 294, 128 + k * 10, 270, '#8a8a92')
        bg.rect(126 + k * 10, 266, 3, 5, '#6a6a72')
    Wd.mosaic_circle(bg, 320, 288, 54, 12, '#7a4a38', '#4a2a22', '#ff6a3a', '#b8452e')
    fire = (236, 282)
    bg.ellipse(fire[0], fire[1] + 2, 12, 4, '#3a2418')
    for k in range(5):
        bg.line(fire[0] - 10 + k * 5, fire[1] + 3, fire[0] - 2 + k * 2, fire[1] - 3, '#5a3a24')
    for k in range(8):
        a = k / 8 * 2 * math.pi
        bg.ellipse(fire[0] + math.cos(a) * 13, fire[1] + 2 + math.sin(a) * 4, 2, 1.5, '#6a5a52')
    props.append({'type': 'glow', 'tex': 'pool_fire', 'x': fire[0], 'y': fire[1] + 4, 'alpha': 0.7, 'flicker': 0.15})
    props.append({'type': 'fire', 'x': fire[0], 'y': fire[1]})
    S.vignette(bg, 0.5)
    cs, cp = _clouds('orc_steppe', [
        ((6, 70), ('#b8505a', '#7a2a44', '#4a1a36'), 0.6, 70, 1.2, 88, 80),
        ((20, 140), ('#ffb070', '#c04a4a', '#6a2040'), 0.57, 70, 2.8, 89, 150),
        ((110, 190), ('#ffd090', '#e07050', '#9a3a40'), 0.63, 50, 4.6, 90, 200),
    ])
    sprites.update(cs)
    props = cp + props
    props.append({'type': 'particles', 'kind': 'dust', 'x': -10, 'y': 280, 'w': 4, 'h': 60})
    return {'layers': {'bg': bg}, 'sprites': sprites, 'props': props, 'stand': (320, 288)}


# ============================================================ Gnom: Werkstatt mit Fenster zur Nacht
def gnome_workshop():
    bg = Canvas(W, H)
    sprites, props = {}, []
    plate, plate_l, plate_d = '#3a4a5e', '#4e6278', '#26323f'
    bg.rect(0, 0, W, H, '#1e2632')
    for y in range(0, 262, 26):
        for x in range(0, W, 40):
            bg.rect(x + 1, y + 1, 38, 24, plate)
            bg.hline(x + 1, x + 38, y + 1, plate_l)
            bg.vline(x + 1, y + 1, y + 24, plate_l)
            bg.hline(x + 1, x + 38, y + 24, plate_d)
            for (rx, ry) in [(3, 3), (36, 3), (3, 22), (36, 22)]:
                bg.px(x + rx, y + ry, '#9ab0c8')
    wx, wy, wr = 320, 110, 62   # Rundfenster
    for y in range(wy - wr, wy + wr):
        for x in range(wx - wr, wx + wr):
            if (x - wx) ** 2 + (y - wy) ** 2 <= wr * wr:
                t = (y - (wy - wr)) / (2 * wr)
                col = mix('#141040', '#3a2a70', t)
                if BAYER4[y % 4, x % 4] < t * 0.4:
                    col = mix(col, '#4a3a80', 0.5)
                bg.px(x, y, col)
    r = rng(5)
    for _ in range(60):
        a, d = r.uniform(0, 6.28), r.uniform(0, wr - 3)
        bg.px(wx + math.cos(a) * d, wy + math.sin(a) * d * 0.7 - 10, '#e8e8ff')
    bg.circle(wx + 26, wy - 30, 6, '#f0f0ff')
    bg.circle(wx + 24, wy - 31, 1, '#c8c8e8')
    for (px_, pw, ph) in [(wx - 60, 50, 36), (wx - 20, 70, 50), (wx + 30, 50, 30)]:
        bg.poly([(px_, wy + wr), (px_ + pw / 2, wy + wr - ph), (px_ + pw, wy + wr)], '#221a44')
    for k in range(8):
        bg.px(wx - 40 + k * 11, wy + wr - 8 - (k * 5) % 12, '#ffd46b')
    for k in range(0, 360, 4):
        a = math.radians(k)
        for rr in (wr, wr + 1, wr + 2, wr + 3):
            bg.px(wx + math.cos(a) * rr, wy + math.sin(a) * rr, '#b08a3a' if rr < wr + 2 else '#6a4e1e')
        if k % 20 == 0:
            bg.px(wx + math.cos(a) * (wr + 1.5), wy + math.sin(a) * (wr + 1.5), '#ffe08a')
    bg.vline(wx, wy - wr, wy + wr, '#6a4e1e')
    bg.hline(wx - wr, wx + wr, wy, '#6a4e1e')
    for (y, x0, x1, col) in [(150, 0, 250, '#8a6a3a'), (186, 390, 640, '#8a6a3a'), (190, 0, 200, '#5a7a8a')]:
        bg.rect(x0, y, x1 - x0, 8, col)
        bg.hline(x0, x1 - 1, y + 1, shade(col, 0.3))
        bg.hline(x0, x1 - 1, y + 7, shade(col, -0.4))
        for x in range(x0 + 20, x1, 60):
            bg.rect(x, y - 2, 6, 12, shade(col, -0.2))
            bg.vline(x, y - 2, y + 9, shade(col, 0.3))
    for (x, y0, y1) in [(250, 150, 262), (390, 186, 262), (200, 190, 262)]:
        bg.rect(x, y0, 8, y1 - y0, '#5a7a8a')
        bg.vline(x + 1, y0, y1 - 1, '#8aaaba')
        bg.vline(x + 7, y0, y1 - 1, '#3a4a5a')
    for (vx, vy) in [(96, 150), (560, 186)]:   # Dampfventile
        bg.rect(vx, vy - 6, 6, 6, '#b8352c')
        bg.hline(vx - 2, vx + 7, vy - 7, '#8a2a24')
        props.append({'type': 'particles', 'kind': 'steam', 'x': vx + 3, 'y': vy - 8})
    for (gx_, gy_) in [(254, 130), (394, 170)]:
        bg.circle(gx_, gy_, 8, '#1a1a22')
        bg.circle(gx_, gy_, 7, '#c8b890')
        bg.circle(gx_, gy_, 6, '#f0e8d0')
        bg.line(gx_, gy_, gx_ + 4, gy_ - 3, '#b8352c')
    gears = [('gear_big', 44, 18, '#b08a3a', '#d8b058', '#6a4e1e', 92, 92, 1),
             ('gear_small', 22, 10, '#8a9aac', '#b8c8d8', '#4a5a6a', 150, 50, -1),
             ('gear_right', 52, 22, '#b08a3a', '#d8b058', '#6a4e1e', 560, 110, -1),
             ('gear_copper', 20, 10, '#b8704a', '#e0986a', '#6a3a20', 486, 58, 1)]
    for (name, rr, teeth, col, cl, cd, gx_, gy_, direction) in gears:
        sheet, fw = P.gear_sheet(rr, teeth, col, cl, cd, frames=8)
        sprites[f'gnome_{name}'] = sheet
        props.append({'type': 'anim', 'tex': f'gnome_{name}', 'x': gx_ - fw // 2, 'y': gy_ - fw // 2, 'hframes': 8,
                      'fps': 8 * (0.35 if rr > 30 else 0.7), 'reverse': direction < 0})
    bg.rect(470, 214, 150, 10, '#6a4a2e')   # Werkbank mit mechanischem Huhn
    bg.hline(470, 619, 214, '#8a6a4a')
    bg.rect(478, 224, 6, 38, '#4a321e')
    bg.rect(606, 224, 6, 38, '#4a321e')
    bg.rect(496, 202, 20, 12, '#8a9aac')
    bg.frame(496, 202, 20, 12, '#4a5a6a')
    bg.circle(540, 206, 7, '#c8c2d4')
    bg.rect(546, 198, 4, 4, '#b8352c')
    bg.rect(544, 212, 2, 3, '#8a8a92')
    bg.rect(536, 212, 2, 3, '#8a8a92')
    bg.px(548, 204, '#1a1a22')
    bg.rect(570, 206, 30, 8, '#b08a3a')
    bg.line(604, 206, 612, 196, '#8a8a92')
    bg.rect(20, 170, 130, 6, '#6a4a2e')   # Regal
    bg.rect(20, 222, 130, 6, '#6a4a2e')
    cols = ['#45b3b5', '#d864a8', '#e07c2c', '#8fb0ee']
    for i, x in enumerate(range(26, 146, 14)):
        bg.rect(x, 158, 8, 12, cols[i % 4])
        bg.px(x + 1, 159, '#ffffff')
        bg.rect(x + 2, 210, 6, 12, ['#b08a3a', '#8a9aac', '#45b3b5'][i % 3])
    bg.rect(0, 262, W, H - 262, '#5a3e2a')
    y, step = 262, 3
    while y < H:
        bg.hline(0, W - 1, y, '#3a2618')
        bg.hline(0, W - 1, y + 1, '#7a5a3e')
        y += step
        step = int(step * 1.3) + 1
    for k in range(-14, 15):
        bg.line(320 + k * 16, 262, 320 + k * 60, H, '#4a3220')
    Wd.mosaic_circle(bg, 320, 290, 56, 12, '#6a7e92', '#3a4a5a', '#45e0d0', '#2a8a8a')
    for (lx, ly) in [(200, 30), (440, 30)]:
        bg.vline(lx, 0, ly, '#1a1a22')
        bg.poly([(lx - 7, ly + 6), (lx + 7, ly + 6), (lx, ly)], '#3a4a5a')
        bg.rect(lx - 3, ly + 6, 7, 3, '#fff0b0')
        props.append({'type': 'glow', 'tex': 'glow_lamp', 'x': lx, 'y': ly + 9, 'alpha': 0.55, 'flicker': 0.05})
        props.append({'type': 'glow', 'tex': 'pool_lamp', 'x': lx, 'y': 300, 'alpha': 0.35, 'flicker': 0.05})
    S.vignette(bg, 0.6)
    props.append({'type': 'particles', 'kind': 'motes_teal', 'x': 320, 'y': 200, 'w': 320, 'h': 150})
    return {'layers': {'bg': bg}, 'sprites': sprites, 'props': props, 'stand': (320, 290)}


# ============================================================ Ladebildschirm Gruenhain
def loading_gruenhain():
    bg = Canvas(W, H)
    sprites, props = {}, []
    S.sky(bg, ['#4a8ad8', '#6aa8e8', '#9ccaf2', '#d2ecf8'], 0, 200)
    S.glow_disc(bg, 110, 60, 16, 40, '#fffbe0', '#fff0a0', steps=5)
    S.peaks(bg, [(80, 130, 110), (260, 150, 100), (480, 120, 120), (620, 150, 90)],
            '#7a9ac0', '#a8c0dc', '#5e7aa4', 210, snow='#f4f8ff', snow_dark='#c4d0e6', seed=8)
    S.hills(bg, 3, 200, 12, '#5a9a4a', '#7ab85a', tex_col='#4e8a40')
    for x in range(-10, W + 10, 11):
        S.pine(bg, x, 214 + (x * 7 % 5), 26 + (x * 13 % 12), '#1e4a2e', '#2e6a3e', '#4a8a4e')
    ys = S.hills(bg, 11, 236, 10, '#6ab04a', '#8ed060', tex_col='#5aa040')
    river = []   # Fluss vom Wald ins Tal
    for y in range(226, H):
        t = (y - 226) / (H - 226)
        xc = 420 - t * 260 + math.sin(t * 5) * 30
        river.append((y, xc, 3 + t * 22))
    for k, col in enumerate(['#d8c060', '#8ec050', '#c8a848', '#7ab048']):   # Felder
        y0 = 244 + k * 7
        for x in range(440, 640):
            for y in range(y0 + (x - 440) // 40, y0 + 7 + (x - 440) // 40):
                if y > ys[x] + 3:
                    bg.px(x, y, col if (x + y) % 7 else shade(col, -0.15))
    Wd.townhouse(bg, 470, 246, 44, 26, _pal_day_b(), seed=33, lit_chance=0.0, dormer=False)
    mx, my = 548, 244   # Windmuehle (Fluegel animiert)
    bg.poly([(mx - 10, my), (mx + 10, my), (mx + 6, my - 44), (mx - 6, my - 44)], '#e0d0b0')
    bg.poly([(mx + 2, my), (mx + 10, my), (mx + 6, my - 44), (mx + 2, my - 44)], '#b8a88a')
    bg.poly([(mx - 8, my - 44), (mx + 8, my - 44), (mx, my - 56)], '#8a3a2a')
    bg.rect(mx - 2, my - 10, 4, 10, '#6a4a2e')
    mill, size = P.windmill_sheet(frames=8, length=30)
    sprites['load_windmill'] = mill
    props.append({'type': 'anim', 'tex': 'load_windmill', 'x': mx - size // 2, 'y': my - 42 - size // 2, 'hframes': 8,
                  'fps': 5})
    bg.rect(0, 280, W, H - 280, '#5aa040')
    for y in range(280, H):
        for x in range(W):
            if BAYER4[y % 4, x % 4] < (y - 280) / 160:
                bg.px(x, y, '#4a8a36')
    for y in range(262, H):   # Weg zum Hof (vor dem Fluss gezeichnet)
        half = 6 + (y - 262) * 0.5
        cx = 470 - (y - 262) * 2.2
        for x in range(int(cx - half), int(cx + half)):
            if 0 <= x < W and y > ys[x]:
                bg.px(x, y, '#c8a870' if (x * 3 + y) % 9 else '#a8885a')
    for (y, xc, half) in river:
        for x in range(int(xc - half), int(xc + half)):
            if 0 <= x < W and y > ys[min(W - 1, max(0, x))] - 2:
                col = '#4a8ad8' if (x + y) % 5 else '#6aa8e8'
                if abs(x - (xc - half)) < 1.5 or abs(x - (xc + half)) < 1.5:
                    col = '#3a6a4a'
                bg.px(x, y, col)
    sprites['load_river'] = P.shimmer_sheet(W, H - 226, 14, frames=8, col='#ffffff', density=0.003)
    props.append({'type': 'anim', 'tex': 'load_river', 'x': 0, 'y': 226, 'vframes': 8, 'fps': 5, 'additive': True,
                  'alpha': 0.8})
    by = 300   # Holzbruecke
    bxc = [xc for (y, xc, half) in river if y == by][0]
    bg.rect(int(bxc - 36), by - 3, 72, 7, '#8a6a4a')
    for x in range(int(bxc - 36), int(bxc + 36), 4):
        bg.vline(x, by - 3, by + 3, '#6a4a2e')
    bg.hline(int(bxc - 36), int(bxc + 35), by - 6, '#6a4a2e')
    for x in range(int(bxc - 36), int(bxc + 36), 12):
        bg.vline(x, by - 6, by - 3, '#6a4a2e')
    S.grass_tufts(bg, 7, 270, H, 1400, ['#3a7a2a', '#7ac858', '#9ae070'])
    S.flowers(bg, 9, 276, H, 260, ['#ffffff', '#ffe060', '#ff8ab0', '#b0a0ff'])
    for (sx, sy) in [(380, 290), (402, 296), (420, 286)]:   # Schafe
        bg.ellipse(sx, sy, 5, 3, '#f4f0e6')
        bg.ellipse(sx - 1, sy - 1, 3, 2, '#ffffff')
        bg.rect(sx + 4, sy - 2, 3, 3, '#3a3040')
        for lx in (sx - 3, sx + 2):
            bg.vline(lx, sy + 2, sy + 4, '#3a3040')
    for (tx, h_) in [(24, 96), (86, 70), (604, 100), (150, 54)]:
        Wd.round_tree(bg, tx, 300, h_, '#2e5a2a', '#4a8a3a', '#78b85a', seed=tx)
    S.vignette(bg, 0.35)
    cs, cp = _clouds('loading', [
        ((6, 60), ('#ffffff', '#e8eef8', '#c4d4e8'), 0.6, 70, 1.4, 12, 70),
        ((10, 130), ('#ffffff', '#e6f0fa', '#bcd0e4'), 0.58, 64, 2.8, 13, 140),
        ((90, 150), ('#ffffff', '#eef4fa', '#c8d8e8'), 0.64, 46, 4.4, 14, 160),
    ])
    sprites.update(cs)
    props = cp + props
    props.append({'type': 'particles', 'kind': 'birds', 'x': 320, 'y': 70, 'w': 320, 'h': 40})
    props.append({'type': 'particles', 'kind': 'fireflies_day', 'x': 320, 'y': 310, 'w': 320, 'h': 40})
    return {'layers': {'bg': bg}, 'sprites': sprites, 'props': props, 'stand': (320, 290)}
