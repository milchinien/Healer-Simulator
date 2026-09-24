"""Kleine Pixel-Art-Bibliothek fuer den Healer Simulator.

Alle Grafiken des Spiels werden mit diesen Helfern Pixel fuer Pixel erzeugt.
Koordinaten: (x, y), Ursprung oben links. Farben: '#rrggbb' oder (r, g, b, a).
"""
from __future__ import annotations

import math
import os
import random
from typing import Iterable, Sequence

import numpy as np
from PIL import Image

Color = tuple[int, int, int, int]

# Bayer-Matrix 4x4 fuer geordnetes Dithering
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def c(col) -> Color:
    """Farbe normalisieren."""
    if col is None:
        return (0, 0, 0, 0)
    if isinstance(col, str):
        h = col.lstrip('#')
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    if len(col) == 3:
        return (int(col[0]), int(col[1]), int(col[2]), 255)
    return tuple(int(v) for v in col)  # type: ignore


def mix(a, b, t: float) -> Color:
    a, b = c(a), c(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))  # type: ignore


def shade(col, f: float) -> Color:
    """f<0 dunkler, f>0 heller (Richtung Weiss)."""
    col = c(col)
    if f < 0:
        return mix(col, (0, 0, 0, col[3]), -f)
    return mix(col, (255, 255, 255, col[3]), f)


class Canvas:
    def __init__(self, w: int, h: int, fill=None):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)
        if fill is not None:
            self.a[:, :] = c(fill)

    # ---------------------------------------------------------------- basics
    def inside(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def px(self, x, y, col):
        x, y = int(x), int(y)
        if self.inside(x, y):
            cc = c(col)
            if cc[3] == 255 or cc[3] == 0:
                if cc[3] == 255:
                    self.a[y, x] = cc
            else:
                base = self.a[y, x].astype(float)
                al = cc[3] / 255.0
                out = base.copy()
                out[:3] = base[:3] * (1 - al) + np.array(cc[:3]) * al
                out[3] = max(base[3], cc[3])
                self.a[y, x] = out.astype(np.uint8)

    def get(self, x, y) -> Color:
        x, y = int(x), int(y)
        if not self.inside(x, y):
            return (0, 0, 0, 0)
        return tuple(int(v) for v in self.a[y, x])  # type: ignore

    def clear_px(self, x, y):
        if self.inside(x, y):
            self.a[y, x] = (0, 0, 0, 0)

    def rect(self, x, y, w, h, col):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.px(xx, yy, col)

    def frame(self, x, y, w, h, col):
        self.hline(x, x + w - 1, y, col)
        self.hline(x, x + w - 1, y + h - 1, col)
        self.vline(x, y, y + h - 1, col)
        self.vline(x + w - 1, y, y + h - 1, col)

    def hline(self, x0, x1, y, col):
        for x in range(int(min(x0, x1)), int(max(x0, x1)) + 1):
            self.px(x, y, col)

    def vline(self, x, y0, y1, col):
        for y in range(int(min(y0, y1)), int(max(y0, y1)) + 1):
            self.px(x, y, col)

    def line(self, x0, y0, x1, y1, col):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, col):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if rx > 0 and ry > 0 and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.px(x, y, col)

    def circle(self, cx, cy, r, col):
        self.ellipse(cx, cy, r, r, col)

    def poly(self, pts: Sequence[tuple[float, float]], col):
        """Gefuelltes Polygon (Scanline, even-odd)."""
        ys = [p[1] for p in pts]
        for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
            yc = y + 0.5
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yc < y1) or (y1 <= yc < y0):
                    xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
                    self.px(x, y, col)

    # ------------------------------------------------------------- gradients
    def vgradient(self, x, y, w, h, stops: Sequence, dither=True):
        """Vertikaler Verlauf ueber Farbstufen mit Bayer-Dithering (echte Pixel-Art-Stufen)."""
        stops = [c(s) for s in stops]
        n = len(stops) - 1
        for yy in range(h):
            t = yy / max(1, h - 1) * n
            i = min(int(t), n - 1)
            f = t - i
            for xx in range(w):
                if dither:
                    col = stops[i + 1] if f > BAYER4[(y + yy) % 4, (x + xx) % 4] else stops[i]
                else:
                    col = mix(stops[i], stops[i + 1], f)
                self.px(x + xx, y + yy, col)

    def dither_fill(self, x, y, w, h, col_a, col_b, amount: float, mask=None):
        """Mischt col_b mit Anteil 'amount' (0..1) per Bayer-Dithering in einen Bereich."""
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                if mask is not None and not mask(xx, yy):
                    continue
                self.px(xx, yy, col_b if amount > BAYER4[yy % 4, xx % 4] else col_a)

    # --------------------------------------------------------------- compose
    def paste(self, other: 'Canvas', x, y, flip=False):
        src = other.a[:, ::-1] if flip else other.a
        for yy in range(other.h):
            for xx in range(other.w):
                p = src[yy, xx]
                if p[3] > 0:
                    self.px(x + xx, y + yy, tuple(int(v) for v in p))

    def outline(self, col, diagonal=False):
        """Aussenkontur um alle nicht-transparenten Pixel."""
        alpha = self.a[:, :, 3] > 0
        out = np.zeros_like(alpha)
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonal:
            dirs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in dirs:
            sh = np.zeros_like(alpha)
            ys = slice(max(0, dy), self.h + min(0, dy))
            yd = slice(max(0, -dy), self.h + min(0, -dy))
            xs = slice(max(0, dx), self.w + min(0, dx))
            xd = slice(max(0, -dx), self.w + min(0, -dx))
            sh[yd, xd] = alpha[ys, xs]
            out |= sh
        out &= ~alpha
        self.a[out] = c(col)

    def replace(self, old, new):
        o = np.array(c(old))
        m = np.all(self.a == o, axis=2)
        self.a[m] = c(new)

    def crop(self, x, y, w, h) -> 'Canvas':
        n = Canvas(w, h)
        n.a[:, :] = self.a[y:y + h, x:x + w]
        return n

    def copy(self) -> 'Canvas':
        n = Canvas(self.w, self.h)
        n.a = self.a.copy()
        return n

    def flip_h(self) -> 'Canvas':
        n = self.copy()
        n.a = n.a[:, ::-1].copy()
        return n

    # ------------------------------------------------------------------ io
    def image(self) -> Image.Image:
        return Image.fromarray(self.a, 'RGBA')

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.image().save(path)

    def save_preview(self, path: str, scale=4, bg=(40, 36, 52, 255)):
        img = Image.new('RGBA', (self.w, self.h), bg)
        img.alpha_composite(self.image())
        img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)


def from_grid(rows: Iterable[str], legend: dict, w=None) -> Canvas:
    """ASCII-Raster in Canvas umwandeln. '.' und ' ' = transparent."""
    rows = list(rows)
    width = w or max(len(r) for r in rows)
    cv = Canvas(width, len(rows))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in '. ':
                continue
            if ch not in legend:
                raise KeyError(f'Unbekanntes Zeichen {ch!r} in Zeile {y}: {row!r}')
            cv.px(x, y, legend[ch])
    return cv


def rng(seed: int) -> random.Random:
    return random.Random(seed)


def noise2d(w: int, h: int, scale: float, seed: int, octaves=3) -> np.ndarray:
    """Einfaches Value-Noise (0..1) fuer Wolken, Felsen, Gras."""
    r = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        s = scale / (2 ** o)
        gw, gh = int(w / s) + 3, int(h / s) + 3
        grid = r.random((gh, gw))
        ys = np.arange(h) / s
        xs = np.arange(w) / s
        y0 = ys.astype(int)
        x0 = xs.astype(int)
        fy = ys - y0
        fx = xs - x0
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        a = grid[y0][:, x0]
        b = grid[y0][:, x0 + 1]
        cc = grid[y0 + 1][:, x0]
        d = grid[y0 + 1][:, x0 + 1]
        top = a + (b - a) * fx[None, :]
        bot = cc + (d - cc) * fx[None, :]
        out += amp * (top + (bot - top) * fy[:, None])
        total += amp
        amp *= 0.5
    return out / total
