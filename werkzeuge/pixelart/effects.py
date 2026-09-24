"""Animierte Effekte: Feuer, Leuchten, Funken, Gluehwuermchen, Lichtsaeule."""
from __future__ import annotations

import math

from pa import Canvas, c, mix, BAYER4, rng
import scenery as S


def fire_sheet(frames=6, w=14, h=20) -> Canvas:
    """Flackerndes Lagerfeuer/Kohlebecken als Spritesheet."""
    sheet = Canvas(w * frames, h)
    cols = ['#fff6c0', '#ffd24a', '#ff9a2a', '#e8521e', '#9a2a18']
    for f in range(frames):
        r = rng(100 + f)
        cv = Canvas(w, h)
        cx = w / 2
        for layer, (col, scale) in enumerate(zip(reversed(cols), [1.0, 0.85, 0.66, 0.45, 0.26])):
            tongues = 3
            for t in range(tongues):
                off = (t - 1) * w * 0.22 * scale + r.uniform(-1.2, 1.2)
                height = h * scale * r.uniform(0.75, 1.0) * (1.0 if t == 1 else 0.75)
                base_w = w * 0.36 * scale
                sway = math.sin((f / frames) * 2 * math.pi + t) * 1.5
                pts = [(cx + off - base_w, h - 1), (cx + off + base_w, h - 1), (cx + off + sway * 0.5, h - 1 - height)]
                cv.poly(pts, col)
        # Funken
        for _ in range(2):
            cv.px(r.randrange(2, w - 2), r.randrange(0, h // 2), '#ffd24a')
        sheet.paste(cv, f * w, 0)
    return sheet


def glow(radius, col) -> Canvas:
    return S.soft_glow_sprite(radius, col)


def light_beam(w=40, h=180) -> Canvas:
    """Senkrechte Lichtsaeule (additiv), oben breit auslaufend."""
    cv = Canvas(w, h)
    for y in range(h):
        t = y / h
        half = 3 + (1 - t) * (w / 2 - 3) * 0.9
        for x in range(w):
            d = abs(x - w / 2) / half
            if d < 1:
                a = (1 - d) ** 1.4 * (0.25 + 0.75 * t) * 0.8
                lvl = math.floor(a * 5) / 5
                if a * 5 - math.floor(a * 5) > BAYER4[y % 4, x % 4]:
                    lvl += 0.2
                if lvl > 0:
                    cc = c('#fff2c0')
                    cv.a[y, x] = (cc[0], cc[1], cc[2], int(min(1.0, lvl) * 200))
    return cv


def particle_dot() -> Canvas:
    cv = Canvas(3, 3)
    cv.px(1, 1, '#ffffff')
    cv.px(0, 1, (255, 255, 255, 120))
    cv.px(2, 1, (255, 255, 255, 120))
    cv.px(1, 0, (255, 255, 255, 120))
    cv.px(1, 2, (255, 255, 255, 120))
    return cv


def sparkle() -> Canvas:
    """Kleiner Stern-Funke (Charakter-Aenderung, Auswahl)."""
    cv = Canvas(7, 7)
    for (x, y, a) in [(3, 0, 120), (3, 1, 200), (3, 2, 255), (3, 3, 255), (3, 4, 255), (3, 5, 200), (3, 6, 120),
                      (0, 3, 120), (1, 3, 200), (2, 3, 255), (4, 3, 255), (5, 3, 200), (6, 3, 120)]:
        cv.px(x, y, (255, 255, 255, a))
    return cv


def soft_shadow(w=40, h=8) -> Canvas:
    """Schatten unter Figuren."""
    cv = Canvas(w, h)
    for y in range(h):
        for x in range(w):
            d = ((x - w / 2 + 0.5) / (w / 2)) ** 2 + ((y - h / 2 + 0.5) / (h / 2)) ** 2
            if d < 1 and (1 - d) > BAYER4[y % 4, x % 4] * 0.8:
                cv.a[y, x] = (8, 5, 12, 150)
    return cv
