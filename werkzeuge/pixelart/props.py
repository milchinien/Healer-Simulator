"""Animierte Szenen-Elemente als Spritesheets (Frames nebeneinander bzw. untereinander).

Jede Funktion liefert (Canvas, Metadaten). Die Metadaten landen in scenes.json und
beschreiben, wie das Spiel das Element abspielt (Framegroesse, Frames, fps).
"""
from __future__ import annotations

import math

import numpy as np

from pa import Canvas, c, mix, shade, BAYER4, noise2d, rng

INK = '#0e0a14'


# ------------------------------------------------------------------ Wolken
def cloud_frames(w, h, seed, band, col_light, col_mid, col_dark, density=0.56, scale=60.0, stretch=3.0, frames=12):
    """Wolkenband, das sich ueber `frames` Frames langsam verformt (Schleife) und in x kachelbar ist.
    Rueckgabe: Canvas mit den Frames untereinander (w x h*frames)."""
    nw = int(w / stretch) + 4

    def tile_noise(s):
        n0 = noise2d(nw + 32, h, scale / stretch * 1.4, s, octaves=4)
        n = n0[:, :nw].copy()
        for i in range(32):
            t = i / 32
            n[:, i] = n0[:, nw + i] * (1 - t) + n0[:, i] * t
        return n
    na, nb = tile_noise(seed), tile_noise(seed + 1000)
    xs = (np.arange(w) / stretch).astype(int) % nw
    xf = (np.arange(w) / stretch) % 1
    sheet = Canvas(w, h * frames)
    y0, y1 = band
    for f in range(frames):
        t = f / frames
        wa = math.cos(math.pi * t) ** 2
        # Mischung zweier Rauschfelder; Varianz wieder herstellen, damit Wolken in jedem Frame gleich dicht sind
        n_small = ((na - 0.5) * wa + (nb - 0.5) * (1 - wa)) / math.sqrt(wa * wa + (1 - wa) ** 2) + 0.5
        n = n_small[:, xs] * (1 - xf) + n_small[:, (xs + 1) % nw] * xf
        off = f * h
        for y in range(y0, y1):
            band_f = 1 - abs((y - (y0 + y1) / 2) / ((y1 - y0) / 2)) ** 2.2
            k = 0.55 + 0.45 * band_f
            row = n[y] * k
            up1 = n[y - 1] * k if y - 1 >= y0 else np.zeros(w)
            up3 = n[y - 3] * k if y - 3 >= y0 else np.zeros(w)
            dn2 = n[y + 2] * k if y + 2 < y1 else np.zeros(w)
            for x in range(w):
                v = row[x]
                if v <= density:
                    continue
                if up1[x] < density or (up3[x] < density and BAYER4[y % 4, x % 4] > 0.35):
                    col = col_light
                elif dn2[x] < density or (v - density < 0.03 and BAYER4[y % 4, x % 4] > 0.5):
                    col = col_dark
                else:
                    col = col_mid
                sheet.px(x, off + y, col)
    return sheet


# ------------------------------------------------------------------ Licht
def glow(radius, col, strength=0.85, steps=5) -> Canvas:
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
                    cv.a[y, x] = (cc[0], cc[1], cc[2], int(255 * lvl * strength))
    return cv


def light_pool(rx, ry, col, strength=0.55) -> Canvas:
    """Elliptischer Lichtschein auf dem Boden (additiv im Spiel)."""
    cv = Canvas(rx * 2 + 1, ry * 2 + 1)
    cc = c(col)
    for y in range(cv.h):
        for x in range(cv.w):
            d = math.hypot((x - rx) / rx, (y - ry) / ry)
            if d <= 1:
                a = (1 - d) ** 1.3
                lvl = math.floor(a * 4) / 4
                if a * 4 - math.floor(a * 4) > BAYER4[y % 4, x % 4]:
                    lvl = min(1.0, lvl + 0.25)
                if lvl > 0:
                    cv.a[y, x] = (cc[0], cc[1], cc[2], int(255 * lvl * strength))
    return cv


def lantern_flame(frames=6) -> Canvas:
    """Kleine Flamme (5x6) fuer Laternen, flackernd."""
    shapes = [
        ['..y..', '.yoy.', '.oWo.', 'yoWoy', '.ooo.', '..o..'],
        ['.y...', '.yo..', '.oWo.', '.oWoy', '.ooo.', '..o..'],
        ['...y.', '..oy.', '.oWo.', 'yoWo.', '.ooo.', '..o..'],
        ['..y..', '..o..', '.oWo.', '.oWo.', '.ooo.', '..o..'],
        ['.....', '..y..', '.yWy.', '.oWoy', '.ooo.', '..o..'],
        ['..y..', '.yo..', '.oWy.', 'yoWo.', '.ooo.', '..o..'],
    ]
    sheet = Canvas(5 * frames, 6)
    leg = {'y': '#ffe38a', 'o': '#ffa83a', 'W': '#fffbe0'}
    for f in range(frames):
        for y, row in enumerate(shapes[f % len(shapes)]):
            for x, ch in enumerate(row):
                if ch in leg:
                    sheet.px(f * 5 + x, y, leg[ch])
    return sheet


def fire(frames=8, w=16, h=22) -> Canvas:
    """Lagerfeuer/Kohlebecken, weich flackernd (Flammenzungen wandern)."""
    sheet = Canvas(w * frames, h)
    cols = ['#9a2a18', '#e8521e', '#ff9a2a', '#ffd24a', '#fff6c0']
    for f in range(frames):
        cv = Canvas(w, h)
        ph = f / frames * 2 * math.pi
        for li, col in enumerate(cols):
            scale = 1.0 - li * 0.18
            for t in range(3):
                off = (t - 1) * w * 0.2 * scale + math.sin(ph + t * 2.1 + li) * 1.2
                height = h * scale * (0.85 + 0.15 * math.sin(ph * (1 + t * 0.5) + t)) * (1.0 if t == 1 else 0.72)
                base_w = w * 0.34 * scale
                sway = math.sin(ph + t * 1.7) * 1.8 * scale
                cv.poly([(w / 2 + off - base_w, h - 1), (w / 2 + off + base_w, h - 1), (w / 2 + off + sway, h - 1 - height)], col)
        r = rng(f + 7)
        for _ in range(2):
            cv.px(r.randrange(3, w - 3), r.randrange(0, h // 2), '#ffd24a')
        sheet.paste(cv, f * w, 0)
    return sheet


# ------------------------------------------------------------------ Drehende Teile
def gear_frame(r, teeth, angle, col, col_l, col_d) -> Canvas:
    size = int(r * 2 + 10)
    cx = cy = size / 2
    cv = Canvas(size, size)
    for k in range(teeth):
        a = angle + k / teeth * 2 * math.pi
        pts = []
        for da, rr in ((-0.16, r - 0.5), (-0.1, r + 3.2), (0.1, r + 3.2), (0.16, r - 0.5)):
            pts.append((cx + math.cos(a + da * 6.28 / teeth * 2.4) * rr, cy + math.sin(a + da * 6.28 / teeth * 2.4) * rr))
        cv.poly(pts, col_d)
    cv.circle(cx, cy, r + 0.6, col_d)
    cv.circle(cx, cy, r - 0.4, col)
    # Speichen
    for k in range(4):
        a = angle + k * math.pi / 2
        for t in np.linspace(r * 0.3, r * 0.75, 12):
            cv.px(cx + math.cos(a) * t, cy + math.sin(a) * t, col_d)
            cv.px(cx + math.cos(a + 0.12) * t, cy + math.sin(a + 0.12) * t, col_d)
    cv.circle(cx, cy, r * 0.28, col_l)
    cv.circle(cx, cy, r * 0.12, '#1a1a22')
    # Licht oben links
    for y in range(size):
        for x in range(size):
            p = cv.get(x, y)
            if p[3] and tuple(p[:3]) == c(col)[:3]:
                if (x - cx) + (y - cy) < -r * 0.9:
                    cv.px(x, y, col_l)
    cv.outline(INK)
    return cv


def gear_sheet(r, teeth, col, col_l, col_d, frames=8):
    first = gear_frame(r, teeth, 0, col, col_l, col_d)
    sheet = Canvas(first.w * frames, first.h)
    for f in range(frames):
        a = f / frames * (2 * math.pi / teeth)
        sheet.paste(gear_frame(r, teeth, a, col, col_l, col_d), f * first.w, 0)
    return sheet, first.w


def windmill_sheet(frames=8, length=30):
    size = length * 2 + 8
    sheet = Canvas(size * frames, size)
    for f in range(frames):
        cv = Canvas(size, size)
        cx = cy = size / 2
        base = f / frames * (math.pi / 2)
        for k in range(4):
            a = base + k * math.pi / 2
            ex, ey = cx + math.cos(a) * length, cy + math.sin(a) * length
            cv.line(cx, cy, ex, ey, '#5a3a24')
            px_, py_ = -math.sin(a) * 5, math.cos(a) * 5
            cv.poly([(cx + math.cos(a) * 8, cy + math.sin(a) * 8), (ex, ey), (ex + px_, ey + py_),
                     (cx + math.cos(a) * 8 + px_, cy + math.sin(a) * 8 + py_)], '#f0e6d0')
            for t in (0.45, 0.7):   # Querstreben
                sx, sy = cx + math.cos(a) * length * t, cy + math.sin(a) * length * t
                cv.line(sx, sy, sx + px_, sy + py_, '#b8a88a')
        cv.circle(cx, cy, 2, '#3a2418')
        sheet.paste(cv, f * size, 0)
    return sheet, size


def flag_sheet(w, h, col, col_d, emblem=None, frames=6, pole=True):
    """Wehende Fahne an einer Stange (links)."""
    fw = w + 4
    fh = h + 6
    sheet = Canvas(fw * frames, fh)
    for f in range(frames):
        cv = Canvas(fw, fh)
        for x in range(w):
            t = x / max(1, w - 1)
            dy = math.sin(f / frames * 2 * math.pi - x * 0.55) * 1.6 * t
            shade_ = math.cos(f / frames * 2 * math.pi - x * 0.55)
            for y in range(h):
                yy = int(round(2 + y + dy))
                col_here = col if shade_ > -0.2 else col_d
                if y == 0:
                    col_here = shade(col_here, 0.2)
                cv.px(2 + x, yy, col_here)
        if emblem:
            ex, ey = 2 + w // 2 - 1, 2 + h // 2 - 1
            for (dx, dy) in [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (2, 1), (0, -1), (1, 2)]:
                cv.px(ex + dx, ey + dy + int(round(math.sin(f / frames * 2 * math.pi - (ex - 2) * 0.55) * 0.8)), emblem)
        cv.outline(INK)
        if pole:
            cv.vline(1, 0, fh - 1, '#3a3040')
            cv.px(1, 0, '#f2c14e')
        sheet.paste(cv, f * fw, 0)
    return sheet, fw


def shimmer_sheet(w, h, seed, frames=8, col='#ffffff', density=0.012):
    """Glitzernde Lichtreflexe auf Wasser (additiv)."""
    sheet = Canvas(w, h * frames)
    r = rng(seed)
    dashes = [(r.randrange(w), r.randrange(h), r.randint(1, 4), r.uniform(0, 1)) for _ in range(int(w * h * density))]
    for f in range(frames):
        for (x, y, ln, ph) in dashes:
            v = math.sin((f / frames + ph) * 2 * math.pi)
            if v > 0.2:
                a = int(120 + 120 * v)
                for k in range(ln):
                    sheet.px(x + k, f * h + y, (*c(col)[:3], a))
    return sheet


def rune_glow(w, h, col) -> Canvas:
    return glow(max(w, h) // 2, col, 0.6)
