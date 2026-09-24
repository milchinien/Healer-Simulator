"""Baukasten fuer Pixel-Art-Hintergruende (640x360)."""
from __future__ import annotations

import math

import numpy as np

from pa import Canvas, c, mix, shade, BAYER4, noise2d, rng

W, H = 640, 360
INK = '#0e0a14'


# ------------------------------------------------------------------ Himmel
def sky(cv: Canvas, stops, y0=0, y1=H):
    cv.vgradient(0, y0, cv.w, y1 - y0, stops)


def stars(cv: Canvas, seed, count, y_max, cols=('#fff6d8', '#cfd8ff', '#8a86b8')):
    r = rng(seed)
    for _ in range(count):
        x, y = r.randrange(cv.w), r.randrange(int(y_max))
        col = r.choice(cols)
        cv.px(x, y, col)
        if r.random() < 0.06:  # heller Stern mit Kreuz
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cv.px(x + dx, y + dy, mix(col, '#000000', 0.45))


def glow_disc(cv: Canvas, cx, cy, r_core, r_glow, core, glow, steps=4):
    """Scheibe mit gedithertem Leuchtkranz (Mond, Sonne, Laterne)."""
    for i in range(steps, 0, -1):
        rr = r_core + (r_glow - r_core) * i / steps
        amt = 1 - i / (steps + 1)
        for y in range(int(cy - rr), int(cy + rr) + 1):
            for x in range(int(cx - rr), int(cx + rr) + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= rr * rr and cv.inside(x, y):
                    if amt * 0.9 > BAYER4[y % 4, x % 4]:
                        base = cv.get(x, y)
                        cv.px(x, y, mix(base, glow, 0.18 + 0.1 * amt))
    cv.circle(cx, cy, r_core, core)


def clouds_layer(w, h, seed, y_band, col_light, col_mid, col_dark, density=0.55, scale=46.0, stretch=3.0):
    """Wolkenschicht (eigene Ebene, damit sie im Spiel ziehen kann). Kachelbar in x.
    Das Rauschen wird horizontal gestreckt -> flache, ruhige Wolkenbaender."""
    cv = Canvas(w, h)
    nw = int(w / stretch) + 4
    n0 = noise2d(nw + 32, h, scale / stretch * 1.4, seed, octaves=4)
    # kachelbar machen: Ende in Anfang ueberblenden
    n = n0[:, :nw].copy()
    for i in range(32):
        t = i / 32
        n[:, i] = n0[:, nw + i] * (1 - t) + n0[:, i] * t
    xs = (np.arange(w) / stretch).astype(int) % nw
    xf = (np.arange(w) / stretch) % 1
    n = n[:, xs] * (1 - xf) + n[:, (xs + 1) % nw] * xf
    y0, y1 = y_band
    for y in range(y0, y1):
        band = 1 - abs((y - (y0 + y1) / 2) / ((y1 - y0) / 2)) ** 2.2
        for x in range(w):
            v = n[y, x] * (0.55 + 0.45 * band)
            if v > density:
                above = n[y - 1, x] * (0.55 + 0.45 * band) if y - 1 >= y0 else 0
                above2 = n[y - 3, x] * (0.55 + 0.45 * band) if y - 3 >= y0 else 0
                below = n[y + 2, x] * (0.55 + 0.45 * band) if y + 2 < y1 else 0
                if above < density or (above2 < density and BAYER4[y % 4, x % 4] > 0.35):
                    col = col_light
                elif below < density or (v - density < 0.03 and BAYER4[y % 4, x % 4] > 0.5):
                    col = col_dark
                else:
                    col = col_mid
                cv.px(x, y, col)
    return cv


# ------------------------------------------------------------------ Gelaende
def ridge(w, seed, base, amp, rough=0.55, smooth=1):
    """Bergkamm per Midpoint-Displacement. Liefert y je x."""
    r = rng(seed)
    n = 1
    while n < w:
        n *= 2
    pts = [0.0] * (n + 1)
    pts[0] = r.uniform(-1, 1)
    pts[n] = r.uniform(-1, 1)
    step, scale = n, 1.0
    while step > 1:
        half = step // 2
        for i in range(half, n, step):
            pts[i] = (pts[i - half] + pts[i + half]) / 2 + r.uniform(-1, 1) * scale
        scale *= rough
        step = half
    arr = np.array(pts[:w])
    for _ in range(smooth):
        arr = np.convolve(np.pad(arr, 2, mode='edge'), np.ones(5) / 5, mode='valid')
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-9)   # 0..1
    return (base - arr * amp).astype(int)


def fill_below(cv: Canvas, ys, col, x0=0, rim=None, rim2=None, tex=None, seed=0):
    r = np.random.default_rng(seed)
    for x in range(len(ys)):
        top = int(ys[x])
        for y in range(max(0, top), cv.h):
            cc = col
            if tex is not None and r.random() < tex[1]:
                cc = tex[0]
            cv.px(x0 + x, y, cc)
        if rim is not None:
            cv.px(x0 + x, top, rim)
        if rim2 is not None and x > 0 and ys[x - 1] > top:
            cv.px(x0 + x, top + 1, rim2)


def mountains(cv: Canvas, seed, base, amp, col, light, dark, snow=None, rough=0.55, smooth=1, light_from='left'):
    """Bergkette mit Flaechenschattierung: Haenge zum Licht hell, abgewandte dunkel, Schneekappen."""
    ys = ridge(cv.w, seed, base, amp, rough, smooth)
    k = 7
    ys_s = np.convolve(np.pad(ys.astype(float), k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), mode='valid')
    sgn = 1 if light_from == 'right' else -1
    nz = noise2d(cv.w, 1, 6.0, seed + 99, octaves=2)[0]
    snowline = base - amp * 0.55
    for x in range(cv.w):
        top = int(ys[x])
        slope = (ys_s[min(cv.w - 1, x + 1)] - ys_s[max(0, x - 1)]) * sgn
        lit = slope > 0.25
        shadowed = slope < -0.25
        depth = max(8, int((base - top) * 0.9))
        for y in range(max(0, top), cv.h):
            d = y - top
            col_here = col
            fade = d / depth
            if lit and fade < 1 and (fade < 0.55 or BAYER4[y % 4, x % 4] > (fade - 0.55) / 0.45):
                col_here = light
            elif shadowed and fade < 1 and (fade < 0.6 or BAYER4[y % 4, x % 4] > (fade - 0.6) / 0.4):
                col_here = dark
            if snow and top < snowline and y < snowline + nz[x] * 10 - 4:
                col_here = snow if not shadowed else mix(snow, dark, 0.5)
                if lit:
                    col_here = shade(snow, 0.15)
            cv.px(x, y, col_here)
        cv.px(x, top, light if lit else col)
    return ys


def hills(cv: Canvas, seed, base, amp, col, rim, tex_col=None, freq=1.0):
    r = rng(seed)
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    ys = []
    for x in range(cv.w):
        y = base - amp * (0.55 * math.sin(x / 90 * freq + ph[0]) + 0.3 * math.sin(x / 37 * freq + ph[1])
                          + 0.15 * math.sin(x / 13 * freq + ph[2]))
        ys.append(int(y))
    rr = np.random.default_rng(seed)
    for x in range(cv.w):
        for y in range(ys[x], cv.h):
            col_here = col
            if tex_col and rr.random() < 0.08:
                col_here = tex_col
            cv.px(x, y, col_here)
        cv.px(x, ys[x], rim)
    return ys


# ------------------------------------------------------------------ Pflanzen
def pine(cv: Canvas, x, y_base, h, dark, mid, light, trunk='#3a2418'):
    w = max(3, int(h * 0.42))
    cv.rect(x - 1, y_base - max(2, h // 6), 2, max(2, h // 6), trunk)
    layers = max(3, h // 6)
    for i in range(layers):
        ly = y_base - max(2, h // 6) - i * (h * 0.8 / layers)
        lw = w * (1 - i / (layers + 0.6))
        lh = h * 0.8 / layers + 3
        pts = [(x - lw, ly), (x + lw, ly), (x, ly - lh)]
        cv.poly(pts, mid)
        # Schattenseite rechts
        cv.poly([(x, ly - lh), (x + lw, ly), (x + lw * 0.2, ly)], dark)
        cv.line(int(x - lw), int(ly), int(x), int(ly - lh), light)


def round_tree(cv: Canvas, x, y_base, h, dark, mid, light, trunk='#4a2f1e', seed=0):
    r = rng(seed)
    th = h // 3
    cv.rect(x - 1, y_base - th, 3, th, trunk)
    cv.px(x + 1, y_base - th, shade(trunk, -0.3))
    cr = h * 0.36
    cy = y_base - th - cr * 0.8
    blobs = [(x + r.uniform(-cr * 0.6, cr * 0.6), cy + r.uniform(-cr * 0.4, cr * 0.4), cr * r.uniform(0.55, 0.8))
             for _ in range(6)]
    for bx, by, br in blobs:
        cv.circle(bx, by, br + 1, dark)
    for bx, by, br in blobs:
        cv.circle(bx - 0.6, by - 0.6, br, mid)
    for bx, by, br in blobs:
        cv.circle(bx - br * 0.35, by - br * 0.4, br * 0.45, light)


def grass_tufts(cv: Canvas, seed, y0, y1, count, cols):
    r = rng(seed)
    for _ in range(count):
        x, y = r.randrange(cv.w), r.randrange(y0, y1)
        col = r.choice(cols)
        hgt = r.randint(1, 3)
        cv.vline(x, y - hgt, y, col)
        if r.random() < 0.5:
            cv.px(x - 1, y - 1, col)
        if r.random() < 0.5:
            cv.px(x + 1, y - hgt + 1, col)


def flowers(cv: Canvas, seed, y0, y1, count, cols):
    r = rng(seed)
    for _ in range(count):
        x, y = r.randrange(cv.w), r.randrange(y0, y1)
        cv.px(x, y, r.choice(cols))


# ------------------------------------------------------------------ Bauten
def house(cv: Canvas, x, y_base, w, h, wall, wall_d, timber, roof, roof_d, window_lit=True, seed=0,
          roof_h=None, door=True, chimney=True):
    r = rng(seed)
    roof_h = roof_h or int(w * 0.55)
    # Wand
    cv.rect(x, y_base - h, w, h, wall)
    cv.rect(x + w - 3, y_base - h, 3, h, wall_d)
    # Fachwerk
    cv.hline(x, x + w - 1, y_base - h, timber)
    cv.hline(x, x + w - 1, y_base - h // 2, timber)
    cv.vline(x, y_base - h, y_base, timber)
    cv.vline(x + w - 1, y_base - h, y_base, timber)
    for k in range(1, max(2, w // 12)):
        xx = x + k * w // max(2, w // 12)
        cv.vline(xx, y_base - h, y_base, timber)
        cv.line(xx - 5, y_base - h // 2, xx, y_base - h + 1, timber)
    # Fenster
    lit = '#ffd46b'
    for k in range(max(1, w // 14)):
        wx = x + 4 + k * 14
        if wx + 5 > x + w - 3:
            break
        wy = y_base - h + 4
        on = window_lit and r.random() < 0.8
        cv.rect(wx - 1, wy - 1, 7, 8, timber)
        cv.rect(wx, wy, 5, 6, lit if on else '#2a2440')
        if on:
            cv.px(wx, wy, '#fff3c0')
            cv.vline(wx + 2, wy, wy + 5, timber)
            cv.hline(wx, wx + 4, wy + 3, timber)
    # Tuer
    if door:
        dx = x + w // 2 - 3
        cv.rect(dx - 1, y_base - 12, 8, 12, timber)
        cv.rect(dx, y_base - 11, 6, 11, '#5a3a24')
        cv.px(dx + 4, y_base - 6, '#f2c14e')
    # Dach
    top = y_base - h
    pts = [(x - 4, top + 1), (x + w + 3, top + 1), (x + w // 2, top - roof_h)]
    cv.poly(pts, roof)
    cv.poly([(x + w // 2, top - roof_h), (x + w + 3, top + 1), (x + w // 2 + 2, top + 1)], roof_d)
    for yy in range(top - roof_h + 3, top + 1, 3):   # Ziegelreihen
        for xx in range(x - 4, x + w + 4):
            if cv.get(xx, yy)[3] > 0 and cv.get(xx, yy)[:3] in (c(roof)[:3], c(roof_d)[:3]):
                if (xx + yy) % 5 == 0:
                    cv.px(xx, yy, shade(roof, -0.25))
    cv.line(x - 4, top + 1, x + w // 2, top - roof_h, shade(roof, 0.2))
    if chimney:
        chx = x + int(w * 0.7)
        cv.rect(chx, top - roof_h // 2 - 6, 5, 10, '#6b5a58')
        cv.rect(chx - 1, top - roof_h // 2 - 7, 7, 2, '#4a3c3c')


def cobblestones(cv: Canvas, y0, y1, base, light, dark, seed=0, perspective=True):
    """Kopfsteinpflaster mit Perspektive (hinten kleine, vorne grosse Steine), unregelmaessig."""
    r = rng(seed)
    cv.rect(0, y0, cv.w, y1 - y0, dark)
    y = y0
    while y < y1:
        t = (y - y0) / max(1, (y1 - y0))
        hgt = 2 + int(t * 6) if perspective else 5
        x = -r.randrange(0, 10)
        while x < cv.w:
            wid = int(hgt * (1.6 + r.random() * 1.2)) + 1
            k = r.random()
            col = base if k > 0.3 else (mix(base, dark, 0.35) if k > 0.1 else mix(base, light, 0.4))
            cv.rect(x + 1, y + 1, wid - 1, hgt - 1, col)
            cv.hline(x + 2, x + wid - 2, y + 1, mix(col, light, 0.6))
            if hgt > 3:
                cv.px(x + 1, y + hgt - 1, mix(col, dark, 0.5))
            x += wid
        y += hgt


def lantern_post(cv: Canvas, x, y_base, h=46):
    iron = '#241c28'
    iron_l = '#4a3f52'
    cv.rect(x - 1, y_base - h, 3, h, iron)
    cv.vline(x - 1, y_base - h, y_base, iron_l)
    cv.rect(x - 3, y_base - 3, 7, 3, iron)
    # Arm und Laterne
    cv.hline(x - 1, x + 7, y_base - h + 2, iron)
    cv.rect(x + 5, y_base - h + 3, 5, 7, iron)
    cv.rect(x + 6, y_base - h + 4, 3, 5, '#ffd46b')
    cv.px(x + 6, y_base - h + 4, '#fff6d0')
    cv.hline(x + 4, x + 10, y_base - h + 3, iron_l)
    return (x + 7, y_base - h + 6)   # Lichtmittelpunkt


def soft_glow_sprite(radius, col, steps=5) -> Canvas:
    """Gedithertes Leuchten als eigene Textur (wird im Spiel additiv geblendet und flackert)."""
    size = radius * 2 + 1
    cv = Canvas(size, size)
    cc = c(col)
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - radius, y - radius) / radius
            if d <= 1:
                a = (1 - d) ** 1.6
                lvl = math.floor(a * steps) / steps
                if a * steps - math.floor(a * steps) > BAYER4[y % 4, x % 4]:
                    lvl = min(1.0, lvl + 1 / steps)
                if lvl > 0:
                    cv.a[y, x] = (cc[0], cc[1], cc[2], int(255 * lvl * 0.85))
    return cv


def vignette(cv: Canvas, strength=0.55, col='#07050b'):
    """Dunkelt die Bildraender per Dithering ab."""
    for y in range(cv.h):
        for x in range(cv.w):
            dx = (x - cv.w / 2) / (cv.w / 2)
            dy = (y - cv.h / 2) / (cv.h / 2)
            d = (dx * dx * 0.7 + dy * dy) ** 0.5
            t = max(0.0, d - 0.72) / 0.5 * strength
            if t > BAYER4[y % 4, x % 4]:
                base = cv.get(x, y)
                cv.a[y, x] = mix(base, col, 0.45)


def shadow_ellipse(cv: Canvas, cx, cy, rx, ry, col='#0a0710', amount=0.5):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and cv.inside(x, y):
                if amount > BAYER4[y % 4, x % 4] * 0.9:
                    cv.a[y, x] = mix(cv.get(x, y), col, 0.55)


def peaks(cv: Canvas, specs, col, light, dark, base_y, snow=None, snow_dark=None, light_from='right', seed=0):
    """Klassische Pixel-Berge aus Dreiecksgipfeln.
    specs: Liste (apex_x, apex_y, halbe_breite). Jeder Gipfel hat eine beleuchtete und eine
    Schattenflanke (geteilt entlang eines schraegen Grats) und optional eine gezackte Schneekappe."""
    r = rng(seed)
    for (ax, ay, hw) in specs:
        # gezackte Flanken: pro Zeile kleine Zufallsabweichung
        jag_l, jag_r = {}, {}
        for y in range(int(ay), base_y + 1):
            jag_l[y] = r.choice([0, 0, 1, -1, 1])
            jag_r[y] = r.choice([0, 0, 1, -1, -1])
        ridge_end = ax + (hw * 0.25 if light_from == 'right' else -hw * 0.25)
        snow_depth = (base_y - ay) * 0.28
        for y in range(int(ay), base_y + 1):
            t = (y - ay) / max(1, base_y - ay)
            xl = int(ax - hw * t) + jag_l[y]
            xr = int(ax + hw * t) + jag_r[y]
            xridge = ax + (ridge_end - ax) * t
            for x in range(xl, xr + 1):
                right_side = x > xridge
                lit = right_side if light_from == 'right' else not right_side
                cc = light if lit else dark
                # Flaechenmitte weicher: Grundfarbe mit Dithering zur Flanke
                dist = abs(x - xridge) / max(1, hw * t)
                if dist > 0.55 and BAYER4[y % 4, x % 4] < (dist - 0.55) * 1.6:
                    cc = col
                if snow and y - ay < snow_depth + (r.random() * 3 if (x + y) % 3 == 0 else 0):
                    cc = snow if lit else (snow_dark or mix(snow, dark, 0.45))
                cv.px(x, y, cc)
            # Grat-Linie hell
            cv.px(int(xridge), y, light if y - ay > snow_depth else snow or light)
