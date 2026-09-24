"""Bausteine fuer glaubwuerdige Szenen: Haeuser mit Details, perspektivische Fassaden,
Pflaster mit Fluchtpunkt, Laternen, Marktstaende, Baeume usw."""
from __future__ import annotations

import math

import numpy as np

from pa import Canvas, c, mix, shade, BAYER4, rng

INK = '#0e0a14'
LIT = '#ffd46b'
LIT_H = '#fff3c0'


def lerp(a, b, t):
    return a + (b - a) * t


# ------------------------------------------------------------------ Boden
def perspective_cobbles(cv: Canvas, y0, y1, vp, base, light, dark, seed=0, x0=0, x1=None):
    """Kopfsteinpflaster, dessen Reihen nach vorne groesser werden und dessen Fugen zum Fluchtpunkt laufen."""
    x1 = x1 or cv.w
    r = rng(seed)
    cv.rect(x0, y0, x1 - x0, y1 - y0, dark)
    y = y0
    row = 0
    while y < y1:
        t = (y - y0) / max(1, (y1 - y0))
        hgt = 2 + int(t * 7)
        # Steinbreite waechst mit der Naehe
        wbase = 4 + t * 12
        # Versatz so, dass Fugen grob zum Fluchtpunkt zeigen
        x = x0 - r.randrange(0, int(wbase) + 1)
        while x < x1:
            wid = int(wbase * (0.8 + r.random() * 0.5)) + 1
            k = r.random()
            col = base if k > 0.3 else (mix(base, dark, 0.22) if k > 0.12 else mix(base, light, 0.2))
            cv.rect(x + 1, y + 1, wid - 1, hgt - 1, col)
            if hgt > 2:
                cv.hline(x + 2, x + wid - 2, y + 1, mix(col, light, 0.35))
            if hgt > 4:
                cv.hline(x + 2, x + wid - 2, y + hgt - 1, mix(col, dark, 0.25))
            x += wid
        y += hgt
        row += 1


def mosaic_circle(cv: Canvas, cx, cy, rx, ry, ring, ring_d, inlay, inlay_d):
    """Eingelassenes rundes Mosaik im Pflaster mit Sonnenkreuz (Standplatz der Figur)."""
    cv.ellipse(cx, cy, rx + 1, ry + 1, '#1a1420')
    cv.ellipse(cx, cy, rx, ry, ring_d)
    cv.ellipse(cx, cy - 0.5, rx - 1, ry - 1, ring)
    cv.ellipse(cx, cy, rx - 4, ry - 2.5, '#2a2230')
    cv.ellipse(cx, cy, rx - 5, ry - 3, mix(ring_d, '#2a2230', 0.5))
    # Strahlen des Sonnenkreuzes (perspektivisch gestaucht)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        for t in np.linspace(0.18, 0.78 if k % 3 == 0 else 0.55, 18):
            x = cx + math.cos(a) * (rx - 5) * t
            y = cy + math.sin(a) * (ry - 3) * t
            cv.px(x, y, inlay if k % 3 == 0 else inlay_d)
    cv.ellipse(cx, cy, (rx - 5) * 0.18, (ry - 3) * 0.3, inlay)
    for k in range(40):
        a = k / 40 * 2 * math.pi
        cv.px(cx + math.cos(a) * (rx - 2.5), cy + math.sin(a) * (ry - 1.4), inlay_d if k % 2 else inlay)


# ------------------------------------------------------------------ Haeuser
def townhouse(cv: Canvas, x, y_base, w, h, pal, seed=0, roof_h=None, sign=None, lit_chance=0.75,
              chimney=True, dormer=True, flowers=True):
    """Fachwerkhaus mit Steinsockel, vorkragendem Obergeschoss, Fensterlaeden, Blumenkaesten.
    Liefert eine Liste von Lichtpunkten (Fenster/Tuer) und Schornsteinpositionen."""
    r = rng(seed)
    lights, chimneys = [], []
    wall, wall_d, stone, stone_d, timber = pal['wall'], pal['wall_d'], pal['stone'], pal['stone_d'], pal['timber']
    roof, roof_d, roof_l = pal['roof'], pal['roof_d'], pal.get('roof_l', shade(pal['roof'], 0.2))
    base_h = max(8, int(h * 0.38))
    # Sockel aus Stein
    cv.rect(x, y_base - base_h, w, base_h, stone)
    for yy in range(y_base - base_h + 2, y_base, 4):
        off = (yy // 4 % 2) * 4
        for xx in range(x + off, x + w, 8):
            cv.vline(xx, yy, yy + 3, stone_d)
        cv.hline(x, x + w - 1, yy + 3, stone_d)
    cv.rect(x + w - 3, y_base - base_h, 3, base_h, stone_d)
    # Obergeschoss (1 px vorkragend)
    up_top = y_base - h
    cv.rect(x - 1, up_top, w + 2, h - base_h, wall)
    cv.rect(x + w - 3, up_top, 4, h - base_h, wall_d)
    cv.hline(x - 1, x + w, y_base - base_h, timber)
    cv.hline(x - 1, x + w, y_base - base_h - 1, timber)
    cv.hline(x - 1, x + w, up_top, timber)
    cv.vline(x - 1, up_top, y_base - base_h, timber)
    cv.vline(x + w, up_top, y_base - base_h, timber)
    n_bays = max(1, w // 13)
    bay_w = w / n_bays
    for k in range(1, n_bays):
        bx = int(x + k * bay_w)
        cv.vline(bx, up_top, y_base - base_h, timber)
    for k in range(n_bays):   # Andreaskreuze unter den Fenstern
        bx0 = int(x + k * bay_w)
        bx1 = int(x + (k + 1) * bay_w)
        yb = y_base - base_h - 1
        ym = yb - 5
        cv.line(bx0 + 1, yb, bx0 + (bx1 - bx0) // 2, ym, timber)
        cv.line(bx1 - 1, yb, bx0 + (bx1 - bx0) // 2, ym, timber)
    # Fenster oben
    for k in range(n_bays):
        wx = int(x + k * bay_w + bay_w / 2 - 3)
        wy = up_top + 3
        wh = max(5, (h - base_h) - 13)
        wh = min(wh, 9)
        on = r.random() < lit_chance
        cv.rect(wx - 2, wy, 2, wh, pal.get('shutter', '#5a3a3a'))
        cv.rect(wx + 6, wy, 2, wh, pal.get('shutter', '#5a3a3a'))
        cv.rect(wx - 1, wy - 1, 8, wh + 2, timber)
        cv.rect(wx, wy, 6, wh, LIT if on else '#2a2440')
        if on:
            cv.hline(wx, wx + 5, wy, LIT_H)
            lights.append((wx + 3, wy + wh // 2))
        cv.vline(wx + 3, wy, wy + wh - 1, timber)
        cv.hline(wx, wx + 5, wy + wh // 2, timber)
        if flowers:
            by = wy + wh + 1
            cv.rect(wx - 1, by, 8, 2, '#6a4028')
            for fx in range(wx - 1, wx + 7):
                cv.px(fx, by - 1, r.choice(['#e04a5a', '#ffd46b', '#5aa048', '#e070b0', '#4a8a3a']))
    # Erdgeschoss: Tuer mit Rundbogen + Fenster
    dx = x + (w // 2 - 4 if w < 40 else w // 3 - 4)
    cv.rect(dx - 1, y_base - 13, 10, 13, stone_d)
    cv.rect(dx, y_base - 12, 8, 12, '#4a2e1e')
    cv.hline(dx + 1, dx + 6, y_base - 13, '#4a2e1e')
    cv.vline(dx + 4, y_base - 12, y_base - 1, '#3a2216')
    cv.px(dx + 6, y_base - 6, '#f2c14e')
    lights.append(('door', dx + 4, y_base - 14))
    if w >= 40:
        gx = x + int(w * 0.66)
        on = r.random() < lit_chance
        cv.rect(gx - 1, y_base - base_h + 2, 12, 8, timber)
        cv.rect(gx, y_base - base_h + 3, 10, 6, LIT if on else '#2a2440')
        if on:
            cv.hline(gx, gx + 9, y_base - base_h + 3, LIT_H)
            lights.append((gx + 5, y_base - base_h + 6))
        cv.vline(gx + 5, y_base - base_h + 3, y_base - base_h + 8, timber)
    # Schild (z. B. Gasthaus)
    if sign:
        sx = dx + 10
        sy = y_base - base_h - 4
        cv.hline(sx, sx + 6, sy, '#241c28')
        cv.rect(sx + 2, sy + 1, 7, 6, '#6a4a2e')
        cv.frame(sx + 2, sy + 1, 7, 6, '#3a2616')
        for (px_, py_) in sign:
            cv.px(sx + 3 + px_, sy + 2 + py_, '#f2c14e')
    # Dach
    roof_h = roof_h or int(w * 0.6)
    top = up_top
    cv.poly([(x - 4, top + 1), (x + w + 3, top + 1), (x + w / 2, top - roof_h)], roof)
    cv.poly([(x + w / 2, top - roof_h), (x + w + 3, top + 1), (x + w / 2 + 2, top + 1)], roof_d)
    for yy in range(int(top - roof_h + 3), top + 1, 3):
        for xx in range(x - 4, x + w + 4):
            p = cv.get(xx, yy)
            if p[3] > 0 and tuple(p[:3]) in (c(roof)[:3], c(roof_d)[:3]) and (xx + (yy // 3) * 2) % 4 != 0:
                cv.px(xx, yy, shade(p, -0.22))
    cv.line(x - 4, top + 1, int(x + w / 2), int(top - roof_h), roof_l)
    cv.hline(x - 4, x + w + 3, top + 1, shade(roof_d, -0.3))
    # Gaube
    if dormer and roof_h > 14:
        gx = int(x + w / 2 - 4)
        gy = int(top - roof_h * 0.45)
        cv.rect(gx, gy, 8, 7, wall)
        cv.frame(gx, gy, 8, 7, timber)
        on = r.random() < lit_chance * 0.7
        cv.rect(gx + 2, gy + 2, 4, 4, LIT if on else '#2a2440')
        if on:
            lights.append((gx + 4, gy + 4))
        cv.poly([(gx - 2, gy + 1), (gx + 9, gy + 1), (gx + 4, gy - 4)], roof_d)
    if chimney:
        chx = int(x + w * 0.72)
        cy_ = int(top - roof_h * 0.55)
        cv.rect(chx, cy_ - 8, 5, 12, pal.get('chimney', '#6b5a58'))
        cv.rect(chx - 1, cy_ - 9, 7, 2, shade(pal.get('chimney', '#6b5a58'), -0.3))
        chimneys.append((chx + 2, cy_ - 10))
    return lights, chimneys


def side_facade(cv: Canvas, x_near, x_far, g_near, g_far, h_near, h_far, pal, windows=(), door_t=None,
                seed=0, roof_near=16, roof_far=10, bays=6):
    """Perspektivische Seitenfassade (Hausfront, die zum Fluchtpunkt hin kleiner wird):
    Steinsockel, zwei Fachwerk-Geschosse mit Fenstern, Traufe. windows: Liste (t, lit) fuer das
    erste Obergeschoss; das zweite Geschoss bekommt versetzte Fenster. Liefert Lichtpunkte."""
    r = rng(seed)
    lights = []
    step = 1 if x_far > x_near else -1
    xs = list(range(x_near, x_far + step, step))
    n = len(xs)
    wall, wall_d, stone, stone_d, timber = pal['wall'], pal['wall_d'], pal['stone'], pal['stone_d'], pal['timber']

    def geo(t):
        g = lerp(g_near, g_far, t)
        hh = lerp(h_near, h_far, t)
        return g, hh

    for i, x in enumerate(xs):
        t = i / max(1, n - 1)
        g, hh = geo(t)
        top = g - hh
        f1 = g - hh * 0.36
        f2 = g - hh * 0.68
        for y in range(int(top), int(g)):
            if y >= f1:
                col = stone
                rows = max(1.5, hh * 0.36 / 5)
                if int((y - f1) / rows) != int((y - f1 + 1) / rows):
                    col = stone_d
                elif int((t * bays * 3 + (int((y - f1) / rows) % 2) * 0.5)) != int(((t + 1 / max(1, n - 1)) * bays * 3 + (int((y - f1) / rows) % 2) * 0.5)):
                    col = stone_d
            else:
                col = wall
                if y < f2 and (y - top) < hh * 0.04:
                    col = wall_d
            cv.px(x, y, col)
        for yb in (f1, f1 - 1, f2, top):
            cv.px(x, int(yb), timber)
        # Staender an den Achsgrenzen
        if int(t * bays) != int((t + 1 / max(1, n - 1)) * bays):
            cv.vline(x, int(top), int(f1), timber)
        # Traufe / Dachkante
        rh = lerp(roof_near, roof_far, t)
        for y in range(int(top - rh), int(top) + 1):
            k = (y - (top - rh)) / max(1, rh)
            col = pal['roof'] if k < 0.7 else pal['roof_d']
            if int(y) % 3 == 0 and k < 0.7 and (x // 2) % 2 == 0:
                col = shade(pal['roof'], -0.2)
            cv.px(x, y, col)
        cv.px(x, int(top - rh), pal.get('roof_l', shade(pal['roof'], 0.25)))
        cv.px(x, int(top) + 1, shade(timber, -0.3))

    def window(tw, frac_lo, frac_hi, lit_on, width=7):
        i0 = int(tw * (n - 1))
        x = xs[i0]
        g, hh = geo(tw)
        scale = hh / h_near
        ww = max(2, int(width * scale))
        wy0 = int(g - hh * frac_hi)
        wy1 = int(g - hh * frac_lo)
        wh = max(3, wy1 - wy0)
        x0 = x if step > 0 else x - ww
        cv.rect(x0 - 1, wy0 - 1, ww + 2, wh + 2, timber)
        cv.rect(x0, wy0, ww, wh, LIT if lit_on else '#2a2440')
        if lit_on:
            cv.hline(x0, x0 + ww - 1, wy0, LIT_H)
            lights.append((x0 + ww // 2, wy0 + wh // 2, scale))
        cv.vline(x0 + ww // 2, wy0, wy0 + wh - 1, timber)
        if wh > 5:
            cv.hline(x0, x0 + ww - 1, wy0 + wh // 2, timber)
        # Blumenkasten
        if scale > 0.55:
            cv.rect(x0 - 1, wy0 + wh + 1, ww + 2, max(1, int(2 * scale)), '#6a4028')
            for fx in range(x0 - 1, x0 + ww + 1):
                cv.px(fx, wy0 + wh, r.choice(['#e04a5a', '#ffd46b', '#5aa048', '#e070b0']))

    for (tw, lit_on) in windows:
        window(tw, 0.42, 0.62, lit_on)
    for k in range(bays):
        tw = (k + 0.5) / bays
        window(tw, 0.74, 0.9, r.random() < 0.55, width=6)
    # Erdgeschoss: Tuer + Schaufenster
    if door_t is not None:
        i0 = int(door_t * (n - 1))
        x = xs[i0]
        g, hh = geo(door_t)
        scale = hh / h_near
        dw = max(3, int(10 * scale))
        dh = max(5, int(hh * 0.3))
        x0 = x if step > 0 else x - dw
        cv.rect(x0 - 1, int(g) - dh - 1, dw + 2, dh + 1, stone_d)
        cv.rect(x0, int(g) - dh, dw, dh, '#4a2e1e')
        cv.vline(x0 + dw // 2, int(g) - dh, int(g) - 1, '#3a2216')
        lights.append(('door', x0 + dw // 2, int(g) - dh - 3, scale))
    for tw in ((door_t or 0.5) + 0.22, (door_t or 0.5) - 0.24):
        if 0.05 < tw < 0.95:
            window(tw, 0.08, 0.26, r.random() < 0.6, width=12)
    return lights


# ------------------------------------------------------------------ Strassenmoebel
def street_lamp(cv: Canvas, x, y_base, h=52, ornate=True):
    """Gusseiserne Strassenlaterne mit Glaskasten. Liefert die Flammenposition (Mitte)."""
    iron, iron_l, iron_d = '#2a2230', '#4e4458', '#161218'
    # Sockel
    cv.rect(x - 4, y_base - 4, 9, 4, iron)
    cv.hline(x - 4, x + 4, y_base - 4, iron_l)
    cv.rect(x - 3, y_base - 7, 7, 3, iron)
    # Mast mit Verzierung
    cv.rect(x - 1, y_base - h, 3, h - 6, iron)
    cv.vline(x - 1, y_base - h, y_base - 7, iron_l)
    for yy in (y_base - 18, y_base - h + 10):
        cv.rect(x - 2, yy, 5, 2, iron)
        cv.hline(x - 2, x + 2, yy, iron_l)
    # Laternenkopf
    top = y_base - h - 12
    cv.poly([(x - 5, top + 3), (x + 5, top + 3), (x, top - 2)], iron)
    cv.px(x, top - 3, iron_l)
    cv.rect(x - 4, top + 3, 9, 9, iron)
    cv.rect(x - 3, top + 4, 7, 7, '#ffcf6a')
    cv.vline(x, top + 4, top + 10, iron_d)
    cv.hline(x - 3, x + 3, top + 4, '#fff0b0')
    cv.rect(x - 5, top + 12, 11, 2, iron)
    cv.hline(x - 5, x + 5, top + 12, iron_l)
    if ornate:
        cv.px(x - 5, top + 2, iron_l)
        cv.px(x + 5, top + 2, iron_l)
    return (x, top + 7)


def wall_lamp(cv: Canvas, x, y):
    iron = '#2a2230'
    cv.hline(x - 3, x, y - 4, iron)
    cv.rect(x - 1, y - 3, 5, 6, iron)
    cv.rect(x, y - 2, 3, 4, '#ffcf6a')
    cv.px(x, y - 2, '#fff0b0')
    return (x + 1, y)


def market_stall(cv: Canvas, x, y_base, w=64, seed=0):
    """Geschlossener Marktstand mit gestreiftem Sonnendach, Kisten und Faessern."""
    r = rng(seed)
    wood, wood_d = '#7a5236', '#4e321e'
    # Pfosten
    for px_ in (x + 2, x + w - 4):
        cv.rect(px_, y_base - 34, 3, 34, wood_d)
        cv.vline(px_, y_base - 34, y_base - 1, wood)
    # Theke
    cv.rect(x, y_base - 14, w, 14, wood)
    for yy in range(y_base - 13, y_base, 3):
        cv.hline(x, x + w - 1, yy, wood_d)
    cv.hline(x - 1, x + w, y_base - 15, '#9a6a44')
    # Ware (abgedeckt)
    cv.rect(x + 6, y_base - 20, w - 12, 5, '#6a5a48')
    for k in range(6):
        cv.circle(x + 10 + k * 8, y_base - 20, 3, r.choice(['#b8452e', '#d8a03a', '#5a9a3a', '#c8603a']))
    # Sonnendach gestreift
    top = y_base - 40
    for i in range(w + 8):
        col = '#c8483f' if (i // 6) % 2 == 0 else '#f0e6cc'
        drop = int(2 * math.sin(i / 6 * math.pi) ** 2)
        cv.vline(x - 4 + i, top, top + 6 + drop, col)
        cv.px(x - 4 + i, top + 7 + drop, shade(col, -0.35))
    cv.hline(x - 4, x + w + 3, top - 1, '#3a2220')
    # Kisten und Fass daneben
    cv.rect(x + w + 4, y_base - 10, 10, 10, wood)
    cv.frame(x + w + 4, y_base - 10, 10, 10, wood_d)
    cv.line(x + w + 4, y_base - 10, x + w + 13, y_base - 1, wood_d)
    cv.rect(x + w + 6, y_base - 18, 8, 8, '#8a6040')
    cv.frame(x + w + 6, y_base - 18, 8, 8, wood_d)
    barrel(cv, x - 10, y_base)


def barrel(cv: Canvas, x, y_base):
    cv.ellipse(x + 4, y_base - 6, 4, 6, '#6a4028')
    cv.rect(x + 1, y_base - 11, 7, 10, '#7a4e30')
    for yy in (y_base - 10, y_base - 3):
        cv.hline(x + 1, x + 7, yy, '#3a3040')
    cv.vline(x + 2, y_base - 11, y_base - 2, '#9a6a44')
    cv.ellipse(x + 4, y_base - 11, 3, 1, '#4a2e1e')


def bunting(cv: Canvas, x0, y0, x1, y1, sag=6, seed=0):
    """Wimpelkette zwischen zwei Punkten."""
    r = rng(seed)
    cols = ['#c8483f', '#f2c14e', '#4f76c4', '#5aa048', '#f0e6cc']
    n = int(abs(x1 - x0))
    prev = None
    for i in range(n + 1):
        t = i / max(1, n)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + sag * math.sin(t * math.pi)
        cv.px(x, y, '#2a2230')
        if i % 7 == 3:
            col = cols[(i // 7) % len(cols)]
            cv.poly([(x - 2, y + 1), (x + 3, y + 1), (x + 0.5, y + 6)], col)


def round_tree(cv: Canvas, x, y_base, h, dark, mid, light, trunk='#4a2f1e', seed=0):
    r = rng(seed)
    th = h // 3
    cv.rect(x - 1, y_base - th, 3, th, trunk)
    cv.px(x + 1, y_base - th, shade(trunk, -0.3))
    cr = h * 0.36
    cy = y_base - th - cr * 0.8
    blobs = [(x + r.uniform(-cr * 0.6, cr * 0.6), cy + r.uniform(-cr * 0.4, cr * 0.4), cr * r.uniform(0.55, 0.8))
             for _ in range(7)]
    for bx, by, br in blobs:
        cv.circle(bx, by, br + 1, dark)
    for bx, by, br in blobs:
        cv.circle(bx - 0.6, by - 0.6, br, mid)
    for bx, by, br in blobs:
        cv.circle(bx - br * 0.35, by - br * 0.4, br * 0.45, light)
    for _ in range(int(h * 1.5)):   # Blattstruktur
        bx, by, br = r.choice(blobs)
        a = r.uniform(0, 6.28)
        cv.px(bx + math.cos(a) * br * 0.8, by + math.sin(a) * br * 0.8, dark)


def castle(cv: Canvas, x, y_base, col, col_l, lit, seed=3):
    """Burg auf einem Huegel: Mauer, Tuerme, Bergfried, beleuchtete Fenster. Liefert Lichtpunkte."""
    r = rng(seed)
    lights = []
    cv.rect(x, y_base - 22, 130, 22, col)
    for k in range(0, 130, 6):
        cv.rect(x + k, y_base - 25, 3, 3, col)
    towers = [(x - 8, 46, 14), (x + 28, 70, 18), (x + 62, 88, 16), (x + 98, 58, 14), (x + 124, 42, 14)]
    for (tx, th, tw) in towers:
        cv.rect(tx, y_base - th, tw, th, col)
        cv.vline(tx, y_base - th, y_base, col_l)
        cv.poly([(tx - 2, y_base - th), (tx + tw + 1, y_base - th), (tx + tw / 2, y_base - th - tw * 0.95)], shade(col, -0.25))
        cv.line(tx - 2, y_base - th, int(tx + tw / 2), int(y_base - th - tw * 0.95), col_l)
        for k in range(3):
            wy = y_base - th + 8 + k * 13
            if wy < y_base - 6 and r.random() < 0.75:
                cv.rect(tx + tw // 2 - 1, wy, 2, 3, lit)
                lights.append((tx + tw // 2, wy + 1))
        px_ = int(tx + tw / 2)
        top = int(y_base - th - tw * 0.95)
        cv.vline(px_, top - 7, top, '#2a2230')
        cv.poly([(px_ + 1, top - 7), (px_ + 7, top - 5), (px_ + 1, top - 3)], '#b8352c')
    cv.rect(x + 56, y_base - 12, 10, 12, '#16121c')
    cv.rect(x + 57, y_base - 11, 8, 11, lit)
    lights.append((x + 61, y_base - 6))
    for k in range(10):
        if r.random() < 0.5:
            cv.rect(x + 6 + k * 12, y_base - 14, 2, 3, lit)
    return lights
