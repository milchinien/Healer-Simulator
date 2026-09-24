"""Spiellogo 'Healer Simulator' in Pixel-Art (Goldschrift mit Kontur und Sonnenkreuz)."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pa import Canvas, mix, BAYER4

INK = (14, 10, 20, 255)
GOLD_STOPS = ['#fff6c8', '#ffe08a', '#f2c14e', '#d8a03a', '#a8742a', '#7a5018']


def _text_mask(text, font_path, size, spacing=0):
    font = ImageFont.truetype(font_path, size)
    # Buchstaben einzeln mit Zusatzabstand setzen
    widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] if ch != ' ' else size // 3 for ch in text]
    total = sum(widths) + spacing * (len(text) - 1) + 8
    img = Image.new('L', (total, size * 2), 0)
    d = ImageDraw.Draw(img)
    d.fontmode = '1'
    x = 4
    for ch, w in zip(text, widths):
        if ch != ' ':
            bb = font.getbbox(ch)
            d.text((x - bb[0], 0), ch, font=font, fill=255)
        x += w + spacing
    a = np.array(img) > 127
    ys, xs = np.where(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def _gold_fill(cv: Canvas, mask, ox, oy, stops):
    h = mask.shape[0]
    cols = [np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)] + [255]) for s in stops]
    n = len(cols) - 1
    for y in range(h):
        t = y / max(1, h - 1) * n
        i = min(int(t), n - 1)
        f = t - i
        for x in range(mask.shape[1]):
            if mask[y, x]:
                col = cols[i + 1] if f > BAYER4[(oy + y) % 4, (ox + x) % 4] else cols[i]
                cv.a[oy + y, ox + x] = col
    # Glanzkante: oberster Pixel jeder Spalte heller
    for x in range(mask.shape[1]):
        for y in range(h):
            if mask[y, x]:
                if y == 0 or not mask[y - 1, x]:
                    cv.a[oy + y, ox + x] = (255, 252, 230, 255)
                if y + 1 >= h or not mask[y + 1, x]:
                    cv.a[oy + y, ox + x] = (90, 58, 18, 255)


def _outline(cv: Canvas, col, n=1):
    for _ in range(n):
        cv.outline(col)


def build(font_path) -> Canvas:
    big = _text_mask('HEALER', font_path, 45, spacing=5)
    small = _text_mask('SIMULATOR', font_path, 27, spacing=3)
    W = max(big.shape[1], small.shape[1]) + 40
    H = big.shape[0] + small.shape[0] + 34
    cv = Canvas(W, H)
    bx = (W - big.shape[1]) // 2
    sx = (W - small.shape[1]) // 2
    by = 6
    sy = by + big.shape[0] + 14
    _gold_fill(cv, big, bx, by, GOLD_STOPS)
    _gold_fill(cv, small, sx, sy, ['#f4f0ff', '#d8d2f2', '#aaa2d6', '#7a70b0'])
    # Konturen: dunkles Gold, dann Tinte
    _outline(cv, (74, 48, 18, 255))
    _outline(cv, INK)
    # Zierlinie mit Sonnenkreuz zwischen den Zeilen
    ly = by + big.shape[0] + 7
    cx = W // 2
    for x in range(12, W - 12):
        if cv.a[ly, x, 3] == 0:
            t = 1 - abs(x - cx) / (W / 2 - 12)
            cv.px(x, ly, mix('#4e3516', '#f2c14e', t))
            if cv.a[ly + 1, x, 3] == 0:
                cv.px(x, ly + 1, (14, 10, 20, 200))
    for (dx, dy, col) in [(0, -3, '#fff6c8'), (0, -2, '#ffe08a'), (0, -1, '#f2c14e'), (0, 1, '#f2c14e'),
                          (0, 2, '#d8a03a'), (0, 3, '#a8742a'), (-3, 0, '#f2c14e'), (-2, 0, '#ffe08a'),
                          (-1, 0, '#ffe08a'), (1, 0, '#f2c14e'), (2, 0, '#d8a03a'), (3, 0, '#a8742a'),
                          (0, 0, '#ffffff'), (-1, -1, '#c99a3a'), (1, -1, '#c99a3a'), (-1, 1, '#c99a3a'),
                          (1, 1, '#c99a3a')]:
        cv.px(cx + dx, ly + dy, col)
    # Schlagschatten
    shadow = Canvas(W + 2, H + 3)
    sh = cv.a[:, :, 3] > 0
    for y, x in zip(*np.where(sh)):
        shadow.px(x + 1, y + 2, (8, 5, 12, 170))
    shadow.paste(cv, 0, 0)
    return shadow
