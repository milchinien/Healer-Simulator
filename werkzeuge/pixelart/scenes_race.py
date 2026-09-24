"""Rassen-Hintergruende der Charaktererstellung und Ladebildschirm Gruenhain."""
from __future__ import annotations

import math

import scenery as S
from pa import Canvas, mix, shade, BAYER4
from scenes import stone_dais

W, H = S.W, S.H


def _floor_tiles(cv: Canvas, y0, y1, col, light, dark, vp_x=320):
    """Steinfliesen mit Fluchtpunkt-Perspektive."""
    cv.rect(0, y0, W, y1 - y0, col)
    y = y0
    step = 3
    while y < y1:
        cv.hline(0, W - 1, y, dark)
        cv.hline(0, W - 1, y + 1, light)
        y += step
        step = int(step * 1.35) + 1
    for k in range(-14, 15):
        cv.line(vp_x + k * 14, y0, vp_x + k * 70, y1, dark)


def arch_mask(cx, y_base, r, h):
    """Pixel eines Rundbogens (Rechteck mit Halbkreis oben)."""
    pts = set()
    for y in range(y_base - h, y_base + 1):
        for x in range(cx - r, cx + r + 1):
            yy = y - (y_base - h + r)
            if yy >= 0 or (x - cx) ** 2 + yy ** 2 <= r * r:
                pts.add((x, y))
    return pts


def arch_frame(cv: Canvas, cx, y_base, r, h, size, col, col_d, ink=None, accent=None, every=15):
    """Bogenrahmen aus Steinquadern."""
    for k in range(0, 181, 5):
        a = math.radians(180 - k)
        x = cx + math.cos(a) * (r + size)
        y = y_base - h + r - math.sin(a) * (r + size)
        s = size
        cv.rect(int(x) - s // 2, int(y) - s // 2, s, s, col)
        cv.frame(int(x) - s // 2, int(y) - s // 2, s, s, ink or col_d)
        if accent and k % every == 0:
            cv.px(int(x), int(y), accent)
    for side in (-1, 1):
        x = cx + side * (r + size)
        top = y_base - h + r
        cv.rect(int(x) - size // 2, top, size, h - r, col)
        cv.frame(int(x) - size // 2, top, size, h - r, ink or col_d)


# ============================================================ Mensch: Stadt
def human_city():
    bg = Canvas(W, H)
    S.sky(bg, ['#3a78c8', '#5a98dc', '#8cc0ec', '#c4e2f6'], 0, 230)
    clouds = S.clouds_layer(W, 160, 71, (20, 150), '#ffffff', '#dfeaf6', '#b4c8e0', density=0.57, scale=64)
    S.peaks(bg, [(90, 150, 110), (250, 170, 90), (420, 140, 120), (580, 160, 100)],
            '#8aa0c4', '#b4c6e2', '#6a80a8', 240, snow='#f4f8ff', snow_dark='#c4d0e6', seed=4)
    wall, wall_l, wall_d = '#d8d4cc', '#f0ece4', '#a8a298'
    # Stadtmauer mit Zinnen
    bg.rect(0, 150, W, 110, wall)
    for x in range(0, W, 8):
        bg.rect(x, 144, 5, 6, wall)
        bg.px(x, 144, wall_l)
    for y in range(154, 260, 6):
        for x in range((y // 6 % 2) * 6, W, 12):
            bg.hline(x, x + 10, y, wall_d)
            bg.px(x, y - 3, wall_d)
    bg.hline(0, W - 1, 150, wall_l)
    # Torhaus
    gx = 320
    bg.rect(252, 110, 136, 150, wall)
    bg.hline(252, 387, 110, wall_l)
    for x in range(252, 388, 8):
        bg.rect(x, 104, 5, 6, wall)
    for y in range(114, 260, 6):
        for x in range(252 + (y // 6 % 2) * 6, 388, 12):
            bg.hline(x, x + 10, y, wall_d)
    # Tuerme links/rechts vom Tor mit blauen Daechern und Bannern
    for tx in (220, 388):
        bg.rect(tx, 96, 32, 164, wall)
        bg.rect(tx + 24, 96, 8, 164, wall_d)
        bg.vline(tx, 96, 259, wall_l)
        bg.poly([(tx - 4, 97), (tx + 36, 97), (tx + 16, 56)], '#2f5aa8')
        bg.poly([(tx + 16, 56), (tx + 36, 97), (tx + 18, 97)], '#244480')
        bg.line(tx - 4, 97, tx + 16, 56, '#5a86d0')
        bg.vline(tx + 16, 44, 56, '#3a3040')
        bg.poly([(tx + 17, 44), (tx + 26, 47), (tx + 17, 50)], '#f2c14e')
        bg.rect(tx + 12, 120, 8, 12, '#3a3040')
        bg.rect(tx + 13, 121, 6, 10, '#ffd46b')
        bg.rect(tx + 8, 150, 16, 46, '#2d5ab0')
        bg.vline(tx + 23, 150, 195, '#1f4288')
        bg.hline(tx + 8, tx + 23, 150, '#f2c14e')
        bg.poly([(tx + 8, 196), (tx + 24, 196), (tx + 16, 204)], '#2d5ab0')
        for (dx, dy) in [(15, 162), (16, 162), (14, 163), (15, 163), (16, 163), (17, 163), (15, 164), (16, 164),
                         (15, 165), (16, 165), (14, 166), (17, 166), (15, 167), (16, 167)]:
            bg.px(tx + dx, dy, '#f2c14e')
    # Torbogen mit Blick auf eine helle Strasse
    arch = arch_mask(gx, 258, 44, 112)
    for (x, y) in arch:
        t = (y - 146) / 112
        col = mix('#1e2638', '#6a7a98', max(0.0, t) ** 1.5)
        if BAYER4[y % 4, x % 4] < 0.3:
            col = mix(col, '#1e2638', 0.3)
        bg.px(x, y, col)
    arch_frame(bg, gx, 258, 44, 112, 6, wall_l, wall_d, accent='#f2c14e')
    # Hof
    S.cobblestones(bg, 258, H, '#a8a4a0', '#d0ccc6', '#6e6a68', seed=21)
    for tx_ in (40, 120, 520, 600):
        S.round_tree(bg, tx_, 262, 58, '#2e5a2a', '#4a8a3a', '#78b85a', seed=tx_)
    stone_dais(bg, 320, 286, 60, 13, '#c8c4c0', '#8a8680', '#3a6ac8')
    S.vignette(bg, 0.4)
    return {'bg': bg, 'clouds': clouds}, {'stand': (320, 286), 'lights': [], 'fires': []}


# ============================================================ Zwerg: Bergfestung
def dwarf_hall():
    bg = Canvas(W, H)
    stone, stone_l, stone_d, ink = '#4a4250', '#625868', '#2e2834', '#16121a'
    bg.rect(0, 0, W, H, '#221c28')
    for y in range(0, 262, 12):
        off = (y // 12 % 2) * 20
        for x in range(-off, W, 40):
            bg.rect(x + 1, y + 1, 38, 10, stone)
            bg.hline(x + 1, x + 38, y + 1, stone_l)
            bg.hline(x + 1, x + 38, y + 10, stone_d)
    # Grosses Tor mit Schmiedeglut
    gx, gy = 320, 262
    for (x, y) in arch_mask(gx, gy, 70, 190):
        t = (y - (gy - 190)) / 190
        col = mix('#3a1a10', '#ff8a2a', max(0.0, t) ** 1.8)
        if BAYER4[y % 4, x % 4] < 0.5:
            col = mix(col, '#1a0c08', 0.2)
        bg.px(x, y, col)
    bg.rect(gx - 70, gy - 16, 141, 16, '#ff9a3a')
    for x in range(gx - 70, gx + 71):
        bg.px(x, gy - 16 + (x * 7 % 3), '#ffd070')
    # Amboss-Silhouette
    bg.rect(gx - 20, gy - 42, 40, 10, '#1a1014')
    bg.rect(gx - 10, gy - 32, 20, 16, '#1a1014')
    bg.rect(gx - 28, gy - 44, 14, 4, '#1a1014')
    arch_frame(bg, gx, gy, 70, 190, 7, stone_l, stone_d, ink=ink, accent='#ffb04a')
    # Saeulen mit Rautengravur
    for px_ in (70, 190, 450, 570):
        bg.rect(px_ - 16, 0, 32, 262, stone)
        bg.rect(px_ + 8, 0, 8, 262, stone_d)
        bg.vline(px_ - 16, 0, 261, stone_l)
        bg.rect(px_ - 20, 236, 40, 26, stone_l)
        bg.rect(px_ - 20, 250, 40, 12, stone_d)
        bg.frame(px_ - 20, 236, 40, 26, ink)
        for y in range(30, 230, 40):
            for d in range(6):
                bg.px(px_ - d, y + d, '#8a7a4a')
                bg.px(px_ + d, y + d, '#6a5a38')
                bg.px(px_ - d, y + 12 - d, '#8a7a4a')
                bg.px(px_ + d, y + 12 - d, '#6a5a38')
    # Banner rot/gold mit Hammer
    for bx in (117, 497):
        bg.rect(bx, 40, 26, 90, '#8a2020')
        bg.vline(bx + 25, 40, 129, '#5a1414')
        bg.hline(bx, bx + 25, 40, '#f2c14e')
        bg.poly([(bx, 130), (bx + 26, 130), (bx + 13, 142)], '#8a2020')
        bg.rect(bx + 8, 70, 10, 8, '#f2c14e')
        bg.rect(bx + 12, 78, 2, 20, '#c99a3a')
    _floor_tiles(bg, 262, H, '#3a3440', '#4e4656', '#1e1a22')
    for y in range(262, H):
        for x in range(gx - 170, gx + 170):
            d = math.hypot((x - gx) / 170, (y - 262) / 70)
            if d < 1 and (1 - d) * 0.7 > BAYER4[y % 4, x % 4] and bg.inside(x, y):
                bg.a[y, x] = mix(bg.get(x, y), '#ff8a3a', 0.25)
    stone_dais(bg, 320, 290, 60, 13, '#6a6070', '#3a3440', '#ffb04a')
    fires = []
    for (fx, fy) in [(130, 226), (510, 226)]:   # Kohlebecken
        bg.rect(fx - 10, fy, 21, 6, '#2a2228')
        bg.rect(fx - 4, fy + 6, 9, 30, '#2a2228')
        bg.rect(fx - 12, fy + 34, 25, 4, '#2a2228')
        bg.hline(fx - 10, fx + 10, fy, '#5a4a52')
        fires.append((fx, fy))
    S.vignette(bg, 0.7)
    return {'bg': bg}, {'stand': (320, 290), 'fires': fires, 'lights': [(gx, gy - 30)]}


# ============================================================ Orc: Steppe
def orc_steppe():
    bg = Canvas(W, H)
    S.sky(bg, ['#2a1030', '#6a1e38', '#b8363a', '#e8683a', '#f8a850', '#ffd88a'], 0, 250)
    S.glow_disc(bg, 470, 196, 22, 60, '#fff0c0', '#ffb060', steps=6)
    clouds = S.clouds_layer(W, 170, 88, (10, 160), '#ffb070', '#c04a4a', '#6a2040', density=0.57, scale=70)
    for (mx, mw, mt) in [(30, 150, 150), (200, 90, 178), (380, 60, 190), (520, 150, 140)]:   # Tafelberge
        bg.rect(mx, mt, mw, 250 - mt, '#5a2030')
        bg.rect(mx + mw - 12, mt, 12, 250 - mt, '#3e1624')
        bg.hline(mx, mx + mw - 1, mt, '#8a3a3a')
        bg.hline(mx, mx + mw - 1, mt + 1, '#6e2a34')
        for y in range(mt + 6, 250, 9):
            bg.hline(mx + 2, mx + mw - 3, y, '#4a1a2a')
        bg.poly([(mx - 10, 250), (mx, mt + 10), (mx + 8, 250)], '#4a1a2a')
    S.hills(bg, 9, 252, 6, '#8a4a2a', '#b06a3a', tex_col='#7a3e22')
    bg.rect(0, 256, W, H - 256, '#a0603a')
    for y in range(256, H):
        for x in range(W):
            if BAYER4[y % 4, x % 4] < (y - 256) / 200:
                bg.px(x, y, '#8a4e2e')
    S.grass_tufts(bg, 4, 258, H, 900, ['#c8a050', '#a8803a', '#e0c070'])
    for (tx, ty, tw) in [(70, 258, 60), (160, 252, 40), (476, 254, 46), (566, 262, 70)]:   # Zelte
        bg.poly([(tx - tw / 2, ty), (tx + tw / 2, ty), (tx, ty - tw * 0.8)], '#8a5a3a')
        bg.poly([(tx, ty - tw * 0.8), (tx + tw / 2, ty), (tx + 4, ty)], '#5e3a24')
        bg.poly([(tx - 5, ty), (tx + 5, ty), (tx, ty - tw * 0.35)], '#2a1410')
        for k in (-1, 1):
            bg.line(int(tx), int(ty - tw * 0.8), int(tx + k * 5), int(ty - tw * 0.8 - 8), '#e8dcc0')
        for k in range(3):
            y = int(ty - tw * 0.2 - k * tw * 0.18)
            bg.hline(int(tx - tw * (0.4 - k * 0.1)), int(tx + tw * (0.4 - k * 0.1)), y, '#3e2416')
    stone_dais(bg, 320, 288, 58, 13, '#7a4a38', '#4a2a22', '#ff6a3a')
    fire = (236, 282)
    bg.ellipse(fire[0], fire[1] + 2, 12, 4, '#3a2418')
    for k in range(5):
        bg.line(fire[0] - 10 + k * 5, fire[1] + 3, fire[0] - 2 + k * 2, fire[1] - 3, '#5a3a24')
    S.vignette(bg, 0.55)
    return {'bg': bg, 'clouds': clouds}, {'stand': (320, 288), 'fires': [fire], 'lights': []}


# ============================================================ Gnom: Werkstatt
def _gear(cv, cx, cy, r, col, col_l, col_d, teeth):
    for k in range(teeth):
        a = k / teeth * 2 * math.pi
        tx, ty = cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3)
        cv.rect(int(tx) - 3, int(ty) - 3, 6, 6, col_d)
        cv.rect(int(tx) - 2, int(ty) - 2, 4, 4, col)
    cv.circle(cx, cy, r + 1, col_d)
    cv.circle(cx, cy, r, col)
    cv.circle(cx - 1, cy - 1, r * 0.8, col_l)
    cv.circle(cx, cy, r * 0.7, col)
    cv.circle(cx, cy, r * 0.3, col_d)
    cv.circle(cx, cy, r * 0.15, '#1a1a22')


def gnome_workshop():
    bg = Canvas(W, H)
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
    _gear(bg, 90, 90, 44, '#b08a3a', '#d8b058', '#6a4e1e', 18)
    _gear(bg, 170, 40, 24, '#8a9aac', '#b8c8d8', '#4a5a6a', 12)
    _gear(bg, 560, 110, 52, '#b08a3a', '#d8b058', '#6a4e1e', 22)
    _gear(bg, 470, 44, 20, '#b8704a', '#e0986a', '#6a3a20', 10)
    for (y, x0, x1, col) in [(150, 0, 250, '#8a6a3a'), (186, 390, 640, '#8a6a3a'), (60, 250, 420, '#5a7a8a')]:
        bg.rect(x0, y, x1 - x0, 8, col)
        bg.hline(x0, x1 - 1, y + 1, shade(col, 0.3))
        bg.hline(x0, x1 - 1, y + 7, shade(col, -0.4))
        for x in range(x0 + 20, x1, 60):
            bg.rect(x, y - 2, 6, 12, shade(col, -0.2))
            bg.vline(x, y - 2, y + 9, shade(col, 0.3))
    for (x, y0, y1) in [(250, 60, 262), (420, 60, 186)]:
        bg.rect(x, y0, 8, y1 - y0, '#5a7a8a')
        bg.vline(x + 1, y0, y1 - 1, '#8aaaba')
        bg.vline(x + 7, y0, y1 - 1, '#3a4a5a')
    for (gx_, gy_) in [(254, 120), (424, 120)]:   # Druckanzeigen
        bg.circle(gx_, gy_, 8, '#1a1a22')
        bg.circle(gx_, gy_, 7, '#c8b890')
        bg.circle(gx_, gy_, 6, '#f0e8d0')
        bg.line(gx_, gy_, gx_ + 4, gy_ - 3, '#b8352c')
    bg.rect(470, 214, 150, 10, '#6a4a2e')   # Werkbank
    bg.hline(470, 619, 214, '#8a6a4a')
    bg.rect(478, 224, 6, 38, '#4a321e')
    bg.rect(606, 224, 6, 38, '#4a321e')
    bg.rect(500, 200, 20, 14, '#8a9aac')
    bg.rect(540, 196, 12, 18, '#b8352c')
    bg.rect(570, 204, 30, 10, '#b08a3a')
    bg.rect(20, 170, 130, 6, '#6a4a2e')   # Regal
    bg.rect(20, 210, 130, 6, '#6a4a2e')
    cols = ['#45b3b5', '#d864a8', '#e07c2c', '#8fb0ee']
    for i, x in enumerate(range(26, 146, 14)):
        bg.rect(x, 158, 8, 12, cols[i % 4])
        bg.px(x + 1, 159, '#ffffff')
        bg.rect(x + 2, 198, 6, 12, ['#b08a3a', '#8a9aac', '#45b3b5'][i % 3])
    bg.rect(0, 262, W, H - 262, '#5a3e2a')   # Dielen
    y, step = 262, 3
    while y < H:
        bg.hline(0, W - 1, y, '#3a2618')
        bg.hline(0, W - 1, y + 1, '#7a5a3e')
        y += step
        step = int(step * 1.3) + 1
    for k in range(-14, 15):
        bg.line(320 + k * 16, 262, 320 + k * 60, H, '#4a3220')
    stone_dais(bg, 320, 290, 58, 13, '#6a7e92', '#3a4a5a', '#45e0d0')
    lamps = [(200, 30), (320, 16), (440, 30)]
    for (lx, ly) in lamps:
        bg.vline(lx, 0, ly, '#1a1a22')
        bg.poly([(lx - 7, ly + 6), (lx + 7, ly + 6), (lx, ly)], '#3a4a5a')
        bg.rect(lx - 3, ly + 6, 7, 3, '#fff0b0')
    S.vignette(bg, 0.6)
    return {'bg': bg}, {'stand': (320, 290), 'lights': [(lx, ly + 8) for (lx, ly) in lamps], 'fires': []}


# ============================================================ Ladebildschirm Gruenhain
def loading_gruenhain():
    bg = Canvas(W, H)
    S.sky(bg, ['#4a8ad8', '#6aa8e8', '#9ccaf2', '#d2ecf8'], 0, 200)
    S.glow_disc(bg, 110, 60, 16, 40, '#fffbe0', '#fff0a0', steps=5)
    clouds = S.clouds_layer(W, 150, 12, (10, 140), '#ffffff', '#e6f0fa', '#bcd0e4', density=0.58, scale=64)
    S.peaks(bg, [(80, 130, 110), (260, 150, 100), (480, 120, 120), (620, 150, 90)],
            '#7a9ac0', '#a8c0dc', '#5e7aa4', 210, snow='#f4f8ff', snow_dark='#c4d0e6', seed=8)
    S.hills(bg, 3, 200, 12, '#5a9a4a', '#7ab85a', tex_col='#4e8a40')
    for x in range(-10, W + 10, 11):
        S.pine(bg, x, 214 + (x * 7 % 5), 26 + (x * 13 % 12), '#1e4a2e', '#2e6a3e', '#4a8a4e')
    ys = S.hills(bg, 11, 236, 10, '#6ab04a', '#8ed060', tex_col='#5aa040')
    for k, col in enumerate(['#d8c060', '#8ec050', '#c8a848', '#7ab048']):   # Felder
        y0 = 244 + k * 7
        for x in range(360, 640):
            for y in range(y0 + (x - 360) // 40, y0 + 7 + (x - 360) // 40):
                if y > ys[x] + 3:
                    bg.px(x, y, col if (x + y) % 7 else shade(col, -0.15))
    S.house(bg, 440, 246, 46, 26, '#e8dcc0', '#c4b494', '#6a4a2e', '#b8452e', '#8a3222', seed=33)
    mx, my = 520, 244   # Windmuehle
    bg.poly([(mx - 10, my), (mx + 10, my), (mx + 6, my - 44), (mx - 6, my - 44)], '#e0d0b0')
    bg.poly([(mx + 2, my), (mx + 10, my), (mx + 6, my - 44), (mx + 2, my - 44)], '#b8a88a')
    bg.poly([(mx - 8, my - 44), (mx + 8, my - 44), (mx, my - 56)], '#8a3a2a')
    hub = (mx, my - 42)
    for a in (0.4, 0.4 + math.pi / 2, 0.4 + math.pi, 0.4 + 3 * math.pi / 2):
        ex, ey = hub[0] + math.cos(a) * 30, hub[1] + math.sin(a) * 30
        bg.line(hub[0], hub[1], int(ex), int(ey), '#5a3a24')
        px_, py_ = -math.sin(a) * 5, math.cos(a) * 5
        bg.poly([(hub[0] + math.cos(a) * 8, hub[1] + math.sin(a) * 8), (ex, ey), (ex + px_, ey + py_),
                 (hub[0] + math.cos(a) * 8 + px_, hub[1] + math.sin(a) * 8 + py_)], '#f0e6d0')
    bg.circle(hub[0], hub[1], 2, '#3a2418')
    bg.rect(0, 280, W, H - 280, '#5aa040')
    for y in range(280, H):
        for x in range(W):
            if BAYER4[y % 4, x % 4] < (y - 280) / 160:
                bg.px(x, y, '#4a8a36')
    for y in range(262, H):   # Weg
        half = 8 + (y - 262) * 0.9
        cx = 250 + (y - 262) * 0.6
        for x in range(int(cx - half), int(cx + half)):
            if 0 <= x < W and y > ys[x]:
                bg.px(x, y, '#c8a870' if (x * 3 + y) % 9 else '#a8885a')
    S.grass_tufts(bg, 7, 270, H, 1400, ['#3a7a2a', '#7ac858', '#9ae070'])
    S.flowers(bg, 9, 276, H, 260, ['#ffffff', '#ffe060', '#ff8ab0', '#b0a0ff'])
    for (tx, h_) in [(24, 96), (86, 70), (604, 100), (150, 54)]:
        S.round_tree(bg, tx, 300, h_, '#2e5a2a', '#4a8a3a', '#78b85a', seed=tx)
    for x in range(300, 431, 12):   # Zaun
        bg.rect(x, 268, 2, 12, '#8a6a4a')
        bg.px(x, 268, '#b08a64')
    bg.hline(300, 430, 271, '#8a6a4a')
    bg.hline(300, 430, 276, '#8a6a4a')
    S.vignette(bg, 0.35)
    return {'bg': bg, 'clouds': clouds}, {'lights': [], 'mill_hub': hub}
