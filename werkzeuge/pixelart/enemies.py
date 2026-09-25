"""Gegner-Sprites fuer den Kampf (Gruenhain).

Alle Gegner schauen nach LINKS (3/4-Ansicht), Licht von oben links, Chibi-Proportionen
wie die Spielerfiguren (rig3). Jede Figur wird aus Teilen (Masken) aufgebaut, die erst
beim Rendern schattiert werden - so bleiben Licht und Kontur auch in gedrehten Posen
(Tot-Frame) stimmig.

build(root) schreibt:
  assets/gfx/enemies/<id>.png   ein Sheet pro Gegner, eine Zeile, Frames gleich gross
  data/enemies_gfx.json         Framegroesse und Animationen je Gegner
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

from pa import Canvas, c, mix, shade

OUTLINE = '#120e18'


# ================================================================ Grundgeruest
class Spr:
    """Figur aus Teilen. Teile werden in Zeichenreihenfolge gesammelt und beim Rendern schattiert."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        ys, xs = np.mgrid[0:h, 0:w]
        self.X = xs + 0.5
        self.Y = ys + 0.5
        self.layers = []

    # ------------------------------------------------------------ Masken
    def E(self, cx, cy, rx, ry):
        return ((self.X - cx) / rx) ** 2 + ((self.Y - cy) / ry) ** 2 <= 1.0

    def R(self, x0, y0, x1, y1):
        m = np.zeros((self.h, self.w), bool)
        m[max(0, int(y0)):max(0, int(y1) + 1), max(0, int(x0)):max(0, int(x1) + 1)] = True
        return m

    def P(self, pts):
        cv = Canvas(self.w, self.h)
        cv.poly(pts, (255, 255, 255, 255))
        return cv.a[:, :, 3] > 0

    def C(self, x0, y0, x1, y1, r0, r1=None):
        """Kapsel (Glied) von (x0,y0) nach (x1,y1), Radius r0 -> r1."""
        r1 = r0 if r1 is None else r1
        dx, dy = x1 - x0, y1 - y0
        ll = dx * dx + dy * dy
        if ll == 0:
            t = np.zeros_like(self.X)
        else:
            t = np.clip(((self.X - x0) * dx + (self.Y - y0) * dy) / ll, 0, 1)
        px, py = x0 + t * dx, y0 + t * dy
        r = r0 + (r1 - r0) * t
        return (self.X - px) ** 2 + (self.Y - py) ** 2 <= r * r

    def pts(self, pts):
        m = np.zeros((self.h, self.w), bool)
        for (x, y) in pts:
            x, y = int(x), int(y)
            if 0 <= x < self.w and 0 <= y < self.h:
                m[y, x] = True
        return m

    # ------------------------------------------------------------ Teile
    def part(self, mask, ramp, sep=False, bias=0.0, rim=True, light=None, lv=None):
        """Schattiertes Teil. ramp: dunkel -> hell (3 oder 4 Stufen)."""
        self.layers.append(dict(kind='shade', m=mask.copy(), ramp=[c(x) for x in ramp], sep=sep,
                                bias=bias, rim=rim, light=light, lv=lv))

    def flat(self, mask, col, sep=False):
        self.layers.append(dict(kind='flat', m=mask.copy(), col=c(col), sep=sep))

    def tint(self, mask, ramp, shift=0):
        """Faerbt vorhandene Pixel um, die Lichtstufe des Untergrunds bleibt erhalten."""
        self.layers.append(dict(kind='tint', m=mask.copy(), ramp=[c(x) for x in ramp], shift=shift))

    def dots(self, pts, col):
        self.flat(self.pts(pts), col)

    def grid(self, rows, x0, y0, legend, sep=False, dx_rows=None):
        """Handgezeichnetes Raster. legend: Zeichen -> Farbe oder (Rampe, Stufe)."""
        masks = {}
        for yy, row in enumerate(rows):
            ox = dx_rows(yy) if dx_rows else 0
            for xx, ch in enumerate(row):
                if ch in '. ':
                    continue
                X, Y = int(x0) + xx + ox, int(y0) + yy
                if 0 <= X < self.w and 0 <= Y < self.h:
                    masks.setdefault(ch, np.zeros((self.h, self.w), bool))[Y, X] = True
        if sep and masks:
            full = np.zeros((self.h, self.w), bool)
            for m in masks.values():
                full |= m
            self.layers.append(dict(kind='sep', m=full))
        for ch, m in masks.items():
            v = legend[ch]
            if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], (list, tuple)):
                ramp, lv = v
                self.layers.append(dict(kind='flat', m=m, col=c(ramp[lv]), sep=False, lvl=lv,
                                        gramp=[c(x) for x in ramp]))
            else:
                self.layers.append(dict(kind='flat', m=m, col=c(v), sep=False, lvl=1))

    def cut(self, mask):
        """Loescht bereits gezeichnete Pixel (z. B. offenes Maul)."""
        self.layers.append(dict(kind='cut', m=mask.copy()))

    # ------------------------------------------------------------ Rendern
    @staticmethod
    def _levels(m, n, bias, rim, light):
        """Cel-Shading: Hauptflaeche hell, Schattenseite unten rechts, Lichtkante oben links."""
        ys, xs = np.where(m)
        if len(xs) == 0:
            return np.zeros(m.shape, int)
        if light is None:
            cx = (xs.min() + xs.max() + 1) / 2
            cy = (ys.min() + ys.max() + 1) / 2
            rx = max(1.0, (xs.max() - xs.min() + 1) / 2)
            ry = max(1.0, (ys.max() - ys.min() + 1) / 2)
        else:
            cx, cy, rx, ry = light
        h, w = m.shape
        yy, xx = np.mgrid[0:h, 0:w]
        nx = (xx + 0.5 - cx) / rx
        ny = (yy + 0.5 - cy) / ry
        L = -(0.6 * nx + 0.8 * ny) + bias

        def nb(dx, dy):
            o = np.zeros_like(m)
            ys_ = slice(max(0, dy), h + min(0, dy))
            yd = slice(max(0, -dy), h + min(0, -dy))
            xs_ = slice(max(0, dx), w + min(0, dx))
            xd = slice(max(0, -dx), w + min(0, -dx))
            o[yd, xd] = m[ys_, xs_]
            return o
        top_open = ~nb(0, -1)
        left_open = ~nb(-1, 0)
        bot_open = ~nb(0, 1)
        right_open = ~nb(1, 0)
        top = 3 if n >= 4 else 2
        lv = np.full(m.shape, top - 1, int)          # Hauptflaeche
        lv[L < -0.38] = top - 2                        # Schattenseite
        if rim:
            lv[(top_open | (left_open & (L > 0.3))) & (L > -0.1)] = top    # Lichtkante
            lv[bot_open | (right_open & (L < -0.1))] = max(0, top - 3) if n >= 4 else 0
        return lv

    def render(self, rot=0, flash=0.0, flipv=False) -> Canvas:
        """rot: Vierteldrehungen (np.rot90), flipv: auf den Ruecken drehen. Licht wird danach neu berechnet."""
        layers = self.layers
        if rot or flipv:
            rl = []
            for L in layers:
                L = dict(L)
                f = (lambda a: np.rot90(a, rot)) if rot else (lambda a: a[::-1].copy())
                L['m'] = f(L['m'])
                L['light'] = None
                if L.get('lv') is not None:
                    L['lv'] = f(L['lv'])
                if L.get('gramp') is not None:
                    # Rasterfarben: Lichtstufen an die neue Lage anpassen
                    n = len(L['gramp'])
                    remap = {0: 3, 1: 2, 2: 2, 3: 1} if n >= 4 else {0: 2, 1: 1, 2: 0}
                    if flipv or abs(rot) == 2:
                        L['lvl'] = remap[L['lvl']]
                        L['col'] = L['gramp'][min(L['lvl'], n - 1)]
                rl.append(L)
            layers = rl
        h, w = layers[0]['m'].shape
        img = np.zeros((h, w, 4), np.uint8)
        lvl = np.full((h, w), 1, int)
        for L in layers:
            m = L['m']
            if L['kind'] == 'cut':
                img[m] = 0
                continue
            if L['kind'] == 'tint':
                sel = m & (img[:, :, 3] > 0)
                r = L['ramp']
                for i in range(4):
                    k = min(max(i + L['shift'], 0), len(r) - 1)
                    img[sel & (lvl == i)] = r[k]
                continue
            if L.get('sep') or L['kind'] == 'sep':
                painted = img[:, :, 3] > 0
                d = m.copy()
                d[1:, :] |= m[:-1, :]
                d[:-1, :] |= m[1:, :]
                d[:, 1:] |= m[:, :-1]
                d[:, :-1] |= m[:, 1:]
                ring = d & ~m & painted
                for y, x in zip(*np.where(ring)):
                    img[y, x] = mix(tuple(int(v) for v in img[y, x]), OUTLINE, 0.62)
                lvl[ring] = 0
                if L['kind'] == 'sep':
                    continue
            if L['kind'] == 'flat':
                img[m] = L['col']
                lvl[m] = L.get('lvl', 1)
            else:
                r = L['ramp']
                lv = L['lv'] if L.get('lv') is not None else self._levels(m, len(r), L['bias'], L['rim'], L['light'])
                if len(r) == 3:
                    lv3 = np.clip(lv, 0, 2)
                    for i in range(3):
                        img[m & (lv3 == i)] = r[i]
                else:
                    for i in range(4):
                        img[m & (lv == i)] = r[i]
                lvl[m] = lv[m]
        cv = Canvas(w, h)
        cv.a = img
        if flash > 0:
            a = cv.a.astype(float)
            sel = a[:, :, 3] > 0
            a[sel, 0] = a[sel, 0] + (255 - a[sel, 0]) * flash
            a[sel, 1] = a[sel, 1] + (244 - a[sel, 1]) * flash
            a[sel, 2] = a[sel, 2] + (236 - a[sel, 2]) * flash
            cv.a = a.astype(np.uint8)
        cv.outline(mix(OUTLINE, '#7a2a3a', flash * 0.8) if flash else OUTLINE)
        return cv


def shift(cv: Canvas, dx, dy) -> Canvas:
    out = Canvas(cv.w, cv.h)
    out.paste(cv, dx, dy)
    return out


def place_bottom(cv: Canvas, w, h, dx=0) -> Canvas:
    """Schneidet die Figur zu und setzt sie unten mittig in einen w x h Frame."""
    ys, xs = np.where(cv.a[:, :, 3] > 0)
    fig = cv.crop(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    out = Canvas(w, h)
    out.paste(fig, (w - fig.w) // 2 + dx, h - fig.h)
    return out


def lerp(a, b, t):
    return a + (b - a) * t


# ================================================================ Paletten
# alle Rampen dunkel -> hell; Schatten kuehler/violetter, Licht waermer
P = {
    'eye_dark': '#1a1224',
    'white': '#fffaf0',
    'tongue': ['#8a2a3e', '#d0505a', '#f08878'],
    'mouth': '#3a1222',
    'teeth': '#f4efe2',
    # Woelfe
    'wolfy': ['#3e3a56', '#686a80', '#9699aa', '#c6c8ca'],
    'wolfy_belly': ['#7a7488', '#b8b2b6', '#e2dcd2', '#f4efe4'],
    'wolfg': ['#27243a', '#403e55', '#5f6074', '#868aa0'],
    'wolfg_mane': ['#1c1828', '#312e44', '#4a4a60', '#6c6e84'],
    'wolfg_belly': ['#4e4a5e', '#7e7a88', '#a8a4aa', '#c8c2c0'],
    # Schweine
    'piglet': ['#40242e', '#6e4232', '#9e6844', '#c68e5a'],
    'piglet_stripe': ['#8a6a38', '#c8a050', '#ecc86a', '#f8e08a'],
    'snout': ['#8a4a50', '#c47a70', '#e8a490'],
    'boar': ['#1e1626', '#3a2a30', '#5c4238', '#84624a'],
    'boar_bristle': ['#160f1c', '#30242c', '#54423e', '#86705c'],
    'tusk': ['#9a9088', '#dcd4c6', '#fffaee'],
    'hoof': ['#1a1418', '#34282c', '#4e3e3c'],
    # Kobolde
    'kobold': ['#343226', '#595b30', '#808641', '#a8ad5a'],
    'kobold_ear': ['#5a3a3a', '#9a6a5a', '#c89080'],
    'rag': ['#2e2226', '#523a30', '#7a5840', '#9c7a54'],
    'rag_red': ['#2a1620', '#582630', '#843c34', '#a85c40'],
    'wax': ['#8e7c66', '#c8b894', '#e8dab6', '#fff6e0'],
    'flame': ['#c8401a', '#f08a2a', '#ffd25a', '#fffbe0'],
    'rust': ['#3e2220', '#7a3e26', '#b0662e', '#d8944e'],
    'wood': ['#3a2420', '#624030', '#8a6040', '#b08858'],
    'iron': ['#2c2a3a', '#4e4e62', '#7a7c90', '#a8aabc'],
    # Diebe
    'hood': ['#2a1c24', '#4a3028', '#6e4a34', '#94704a'],
    'scarf': ['#3a1624', '#6a2230', '#98363a', '#c05a48'],
    'skin_h': ['#7a4a3a', '#c98a64', '#e8b08a'],
    'cloth_g': ['#1e1e2a', '#34343f', '#4e4e5a', '#6a6a74'],
    'boot': ['#1a1418', '#302428', '#4a3834'],
    'hat_red': ['#3a0e20', '#7a1a2a', '#b82e34', '#e05a48'],
    'feather': ['#8a7a6a', '#d8ccb8', '#f8f2e4', '#ffffff'],
    'plume': ['#7a4a10', '#c88a1a', '#f0c040', '#fbe890'],
    'coat': ['#1a2230', '#27384a', '#385468', '#50707e'],
    'steel': ['#3a3a50', '#7a7e96', '#c4c8d8', '#ffffff'],
    'gold': ['#6a4418', '#b8862e', '#f2c14e', '#ffe08a'],
    # Stroh / Puppe
    'straw': ['#6a4a1c', '#a8802e', '#d8b44e', '#f4dc86'],
    'burlap': ['#4e3a2c', '#806246', '#aa8a62', '#cfb186'],
    'target_r': ['#6a1420', '#a82430', '#d8423e'],
    'target_w': ['#b8b0a8', '#e8e2d8', '#fffaf2'],
    'rope': ['#5a4428', '#8a6e44', '#b89a64'],
}
EYE_GLOW = {'young': '#f4ecb0', 'grey': '#f0b030'}


# ================================================================ Vierbeiner: Woelfe
# Kopfraster nach links. 1-4 Fell dunkel->hell, v/w/W Bauchfell, p/P Ohrinnen, e Auge, g Augenlicht,
# n Nase, k Linie, a-d Nackenzotteln. WOLF_JAW: (erste Zeile, letzte Spalte) des Unterkiefers.
WOLF_HEAD_YOUNG = [
    "......2......4....",
    "......21....433...",
    "......2p1..43P32..",
    ".....32pp343PP32..",
    ".....433333333321.",
    ".....4333333333321",
    ".....4333333333321",
    ".44444333ee3333221",
    "n43333333eg3333221",
    "n3333333333w333221",
    ".wwwwwwww3www33221",
    "..kkkkwwwwwwwww21.",
    "......vvwwwwwwv1..",
    "........vwwv.wv...",
]
WOLF_HEAD_GREY = [
    ".......2........4........",
    ".......21......433.......",
    ".......2p1....43P32..d...",
    "......32pp1..43PP32.dc...",
    "......433331433PP32dcb.d.",
    "......4333333333332cbbdc.",
    ".....43333333333333bbbcb.",
    ".....433333311133332bbba.",
    ".444444333331ee33332bbba.",
    "n4333333333333eg33221bbd.",
    "n33333333333333w33221bcb.",
    "n3333333333333ww33221bba.",
    ".wwwwwwwwww3wwww3321bba..",
    "..kkkkkwwwwwwwwwww321ba..",
    ".....vvvvwwwwwwwwwv21a...",
    ".......vvwwvwwv.wwv1a....",
    "........v..v..v..v.......",
]
WOLF_JAW = {False: (11, 9), True: (13, 11)}


def _wolf_legend(big):
    fur = P['wolfg'] if big else P['wolfy']
    bel = P['wolfg_belly'] if big else P['wolfy_belly']
    return {'1': (fur, 0), '2': (fur, 1), '3': (fur, 2), '4': (fur, 3),
            'v': (bel, 1), 'w': (bel, 2), 'W': (bel, 3),
            'p': P['kobold_ear'][0], 'P': P['kobold_ear'][1],
            'a': (P['wolfg_mane'], 0), 'b': (P['wolfg_mane'], 1), 'c': (P['wolfg_mane'], 2), 'd': (P['wolfg_mane'], 3),
            'e': P['eye_dark'], 'g': EYE_GLOW['grey' if big else 'young'], 'n': P['eye_dark'], 'k': OUTLINE}


def _eye_variant(rows, mode):
    """Augen im Raster umbauen: open / angry / shut / x."""
    rows = [list(r) for r in rows]
    pos = [(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch in 'eg']
    if not pos or mode == 'open':
        return [''.join(r) for r in rows]
    x0 = min(p[0] for p in pos)
    y0 = min(p[1] for p in pos)

    def put(x, y, ch):
        if 0 <= y < len(rows) and 0 <= x < len(rows[y]) and rows[y][x] != '.':
            rows[y][x] = ch
    if mode in ('shut', 'x'):
        for (x, y) in pos:
            rows[y][x] = '3'
    if mode == 'shut':
        put(x0 - 1, y0, 'e')
        put(x0, y0 + 1, 'e')
        put(x0 + 1, y0 + 1, 'e')
    elif mode == 'x':
        for (dx, dy) in [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)]:
            put(x0 + dx + 1, y0 + dy, 'e')
    elif mode == 'angry':
        for (dx, dy) in [(-1, -1), (0, -1), (1, -1)]:
            put(x0 + dx, y0 + dy, '1')
    return [''.join(r) for r in rows]


def wolf_head(s: Spr, x0, y0, big, mouth=0, eyes='open', ear=0, snarl=False):
    rows = _eye_variant(WOLF_HEAD_GREY if big else WOLF_HEAD_YOUNG, eyes)
    fur = P['wolfg'] if big else P['wolfy']
    leg = _wolf_legend(big)
    jy, jx = WOLF_JAW[big]

    def ear_dx(yy):
        return (1 if ear > 0 else -1 if ear < 0 else 0) if yy < 3 else 0
    if mouth <= 0:
        s.grid(rows, x0, y0, leg, sep=True, dx_rows=ear_dx)
        if snarl:
            # gefletschte Zaehne auf der Maullinie, geruempfte Nase
            s.dots([(x0 + 2, y0 + jy), (x0 + 4, y0 + jy)], P['teeth'])
            s.dots([(x0 + 3, y0 + jy)], P['mouth'])
            s.dots([(x0 + 3, y0 + jy - 3), (x0 + 5, y0 + jy - 3)], fur[1])
        return
    upper = [r if y < jy else ''.join('.' if x <= jx else ch for x, ch in enumerate(r)) for y, r in enumerate(rows)]
    lower = [('.' * len(r)) if y < jy else ''.join(ch if x <= jx else '.' for x, ch in enumerate(r))
             for y, r in enumerate(rows)]
    s.grid(upper, x0, y0, leg, sep=True, dx_rows=ear_dx)
    # Rachen zwischen Ober- und Unterkiefer
    mo = int(mouth)
    s.flat(s.R(x0 + 1, y0 + jy, x0 + jx, y0 + jy + mo - 1), P['mouth'])
    s.flat(s.R(x0 + 4, y0 + jy + mo - 1, x0 + jx - 1, y0 + jy + mo - 1), P['tongue'][1])
    s.grid(lower, x0 + 1, y0 + mo, leg)
    s.dots([(x0 + 1, y0 + jy), (x0 + 4, y0 + jy)], P['teeth'])
    s.dots([(x0 + 3, y0 + jy + mo - 1)], P['teeth'])


def wolf(pose: dict, big=False) -> Spr:
    """Wolf nach links. big=False: junger Waldwolf 32x24, big=True: Grauwolf 36x28."""
    W, H = (36, 28) if big else (32, 24)
    s = Spr(W, H)
    fur = P['wolfg'] if big else P['wolfy']
    belly = P['wolfg_belly'] if big else P['wolfy_belly']
    far = [mix(x, '#2a2040', 0.35) for x in fur]
    k = 1.2 if big else 1.0
    gy = H - 2                          # Unterkante der Pfoten (Kontur liegt darunter)
    bx, by = pose.get('bx', 0), pose.get('by', 0)
    br = pose.get('breath', 0)

    body_cx = (22.0 if big else 19.5) + bx
    body_cy = gy - (11.0 if big else 9.0) + by
    brx, bry = (8.8 if big else 7.0), (5.2 if big else 3.8) + br * 0.4
    fl_x = body_cx - brx * 0.62
    bl_x = body_cx + brx * 0.55
    hip_y = body_cy + bry * 0.2
    legs = pose.get('legs') or {}
    feet = {
        'ff': legs.get('ff', (fl_x + 2.2, gy)),
        'bf': legs.get('bf', (bl_x + 2.2, gy)),
        'fn': legs.get('fn', (fl_x - 0.4, gy)),
        'bn': legs.get('bn', (bl_x - 0.2, gy)),
    }
    lw = 1.05 if big else 0.8

    def leg(hip, foot, ramp, back, sep=False):
        (x0, y0), (x1, y1) = hip, foot
        if back:
            # Hinterlauf: kraeftiger Oberschenkel, Sprunggelenk nach hinten geknickt
            kx, ky = x1 + 1.4 * k, lerp(y0, y1, 0.62)
            m = s.E(x0, y0 + 0.5, 2.6 * k, 3.0 * k)
            m |= s.C(x0 + 0.5, y0 + 1, kx, ky, 1.5 * k, lw) | s.C(kx, ky, x1, y1 - 0.4, lw)
        else:
            m = s.C(x0, y0, x1, y1 - 0.4, 1.4 * k, lw)
        m |= s.R(x1 - 1.6, y1 - 0.6, x1 + 0.4, y1 - 0.6) | s.R(x1 - 1.0, y1 - 1.4, x1 + 0.4, y1 - 1.4)   # Pfote
        s.part(m, ramp, sep=sep, light=(x0 - 1, (y0 + y1) / 2 - 2, 3, (y1 - y0) / 2 + 2))

    # Schwanz: buschig, hinter dem Koerper
    ta = math.radians(pose.get('tail', 40))
    tx0, ty0 = body_cx + brx * 0.75, body_cy - bry * 0.35
    tl = (5.6 if big else 7.0) * k
    tx1, ty1 = tx0 + math.cos(ta) * tl, ty0 - math.sin(ta) * tl
    txm, tym = tx0 + math.cos(ta + 0.45) * tl * 0.5, ty0 - math.sin(ta + 0.45) * tl * 0.5
    tail = s.C(tx0, ty0, txm, tym, 1.4 * k, 2.3 * k) | s.C(txm, tym, tx1, ty1, 2.3 * k, 0.8)
    s.part(tail, fur, light=(txm - 1, tym - 1, 3 * k, 4 * k))
    s.tint(s.E(tx1, ty1, 1.8 * k, 1.8 * k) & tail, belly)

    # ferne Beine
    leg((fl_x + 1.8, hip_y), feet['ff'], far, False)
    leg((bl_x + 1.6, hip_y - 0.5), feet['bf'], far, True)

    # Rumpf
    body = s.E(body_cx, body_cy, brx, bry)
    body |= s.E(body_cx - brx * 0.5, body_cy + 0.5, bry * 1.05, bry * 1.1)   # Brust
    s.part(body, fur, light=(body_cx - 2, body_cy - 1, brx, bry * 1.2))
    s.tint(s.E(body_cx - brx * 0.35, body_cy + bry * 1.0, brx * 0.75, bry * 0.42) & body, belly)
    if pose.get('hackles') and not big:
        # struppiges Nackenfell: Buckel an den Schultern mit nach hinten gestraeubten Zotteln
        up = 1.0 + (0.6 if pose.get('hackles') else 0)
        mr = (5.6 if big else 3.6)
        mcx = body_cx - brx * (0.25 if big else 0.35)
        mcy = body_cy - bry * 0.35
        mane = s.E(mcx, mcy, mr * 1.05, mr * 0.95)
        tufts = np.zeros_like(mane)
        for i, ang in enumerate([150, 118, 88, 60, 34] if big else [120, 85, 50]):
            a = math.radians(ang)
            bx_, by_ = mcx + math.cos(a) * mr * 0.8, mcy - math.sin(a) * mr * 0.8
            tl = (2.8 if i % 2 == 0 else 2.0) * up
            tx_, ty_ = bx_ + math.cos(a - 0.7) * tl, by_ - math.sin(a - 0.7) * tl
            tufts |= s.P([(bx_ - math.sin(a) * 1.6, by_ - math.cos(a) * 1.6), (tx_, ty_),
                          (bx_ + math.sin(a) * 1.6, by_ + math.cos(a) * 1.6)])
        mane |= tufts
        s.part(mane, P['wolfg_mane'] if big else fur, light=(mcx - 1, mcy - 1, mr + 1.5, mr + 1.5), bias=0.1)

    # nahe Beine
    leg((fl_x, hip_y + 0.5), feet['fn'], fur, False, sep=True)
    leg((bl_x, hip_y), feet['bn'], fur, True)

    # Kopf
    hx0 = 1 + pose.get('hx', 0)
    hy0 = (gy - 25 if big else gy - 21) + pose.get('hy', 0)
    wolf_head(s, hx0, hy0, big, pose.get('mouth', 0), pose.get('eyes', 'open'), pose.get('ear', 0),
              pose.get('snarl', False))
    return s


def _wolf_frames(big):
    W, H = (36, 28) if big else (32, 24)
    g = H - 2
    bcx = 22.0 if big else 19.5
    brx = 8.8 if big else 7.0
    fl = bcx - brx * 0.62
    bl = bcx + brx * 0.55
    fr = []
    # idle: Atmen, Schwanz wedelt, Ohr zuckt
    for (b, t, e) in [(0, 38, 0), (1, 46, 0), (1, 52, 1), (0, 44, 0)]:
        fr.append(wolf(dict(breath=b, tail=t, ear=e, by=-0.5 * b), big).render())
    # attack: Ducken, Sprung, Biss, zurueck
    a = [
        dict(bx=1.5, by=1.2, hx=2, hy=2, tail=34, eyes='angry', snarl=True,
             legs={'fn': (fl - 1.0, g), 'ff': (fl + 1.0, g), 'bn': (bl + 0.5, g), 'bf': (bl + 2.5, g)}),
        dict(bx=-1, by=-2, hx=0, hy=-1, tail=15, mouth=3, eyes='angry',
             legs={'fn': (fl - 4.5, g - 4), 'ff': (fl - 3, g - 3), 'bn': (bl + 3.5, g - 1), 'bf': (bl + 5, g - 1.5)}),
        dict(bx=-1, by=0, hx=0, hy=1, tail=32, eyes='angry', snarl=True,
             legs={'fn': (fl - 3, g), 'ff': (fl - 1.5, g), 'bn': (bl + 1.5, g), 'bf': (bl + 3.5, g)}),
        dict(bx=0, by=0, hx=0, hy=0, tail=36),
    ]
    for p, dx in zip(a, [0, 0, 0, 0]):
        fr.append(shift(wolf(p, big).render(), dx, 0))
    # cast: Knurren und Scharren
    for i in range(2):
        p = dict(bx=0.5, by=0.8, hx=1, hy=2, tail=34 + 6 * i, eyes='angry', snarl=True, hackles=True, ear=-1,
                 legs={'fn': (fl - 0.5 + (1.8 if i else -0.8), g - (1.6 if i else 0))})
        fr.append(wolf(p, big).render())
    # hit
    fr.append(shift(wolf(dict(hx=1, hy=0, tail=62, eyes='shut', ear=1, mouth=1, bx=0.5), big).render(flash=0.55), 1, 0))
    fr.append(shift(wolf(dict(hx=1, hy=0, tail=50, eyes='shut'), big).render(), 1, 0))
    # tot
    fr.append(wolf_dead(big))
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 5, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 10, 'loop': False},
        'cast': {'start': 8, 'count': 2, 'fps': 6, 'loop': True},
        'hit': {'start': 10, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 12, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


def wolf_dead(big) -> Canvas:
    """Wolf liegt auf der Seite: Bauch zum Betrachter, Beine schlaff, Augen als X."""
    W, H = (36, 28) if big else (32, 24)
    s = Spr(W, H)
    k = 1.2 if big else 1.0
    fur = P['wolfg'] if big else P['wolfy']
    belly = P['wolfg_belly'] if big else P['wolfy_belly']
    far = [mix(x, '#2a2040', 0.35) for x in fur]
    g = H - 2
    cx, cy = W * 0.62, g - 3.2 * k
    # Schwanz flach nach rechts
    s.part(s.C(cx + 6 * k, cy + 0.5, cx + 10.0 * k, g - 0.8, 1.8 * k, 1.0), fur)
    # ferne Beine
    s.part(s.C(cx - 3.5 * k, cy + 1.5, cx - 7.5 * k, g - 0.3, 0.9 * k) | s.C(cx + 4 * k, cy + 1, cx + 1 * k, g - 0.3, 1.0 * k), far)
    body = s.E(cx, cy, 7.4 * k, 3.4 * k)
    s.part(body, fur, light=(cx - 1, cy - 1, 7.4 * k, 3.6 * k), sep=True)
    s.tint(s.E(cx - 0.5, cy + 2.6 * k, 6.5 * k, 1.6 * k) & body, belly)
    if big:
        s.part(s.E(cx - 4.5 * k, cy - 0.2, 3.4 * k, 3.2 * k), P['wolfg_mane'])
    s.part(s.C(cx - 2.5 * k, cy + 2, cx - 6 * k, g - 0.3, 0.9 * k) | s.C(cx + 5 * k, cy + 1.6, cx + 3 * k, g - 0.3, 1.0 * k),
           fur, sep=True)
    # Kopf liegt am Boden (Raster, ganz unten)
    rows = _eye_variant(WOLF_HEAD_GREY if big else WOLF_HEAD_YOUNG, 'x')
    hx0 = max(1, int(cx - 7.4 * k - len(rows[0]) + 7 * k))
    hy0 = int(g + 1 - len(rows)) + 2
    s.grid(rows[:-2], hx0, hy0, _wolf_legend(big), sep=True)
    tx, ty = hx0 + 3, hy0 + WOLF_JAW[big][0]
    s.dots([(tx, ty), (tx + 1, ty), (tx + 1, ty + 1)], P['tongue'][1])
    return s.render()


# ================================================================ Borstenkeiler (Elite)
def boar(pose: dict) -> Spr:
    """Borstenkeiler nach links, Frame 44x32: wuchtiger Buckel, Borstenkamm, weisse Hauer."""
    W, H = 44, 32
    s = Spr(W, H)
    fur = P['boar']
    far = [mix(x, '#1a1028', 0.4) for x in fur]
    gy = H - 2
    bx, by = pose.get('bx', 0), pose.get('by', 0)
    hx, hy = pose.get('hx', 0), pose.get('hy', 0)
    br = pose.get('breath', 0)
    tilt = pose.get('tilt', 0)          # + = Schnauze hoch (Hauer-Hieb), - = gesenkt
    dead = pose.get('dead', False)

    # Rumpf-Anker: Schulterbuckel + Hinterteil
    sx_, sy_ = 22.5 + bx, 17.0 + by - br * 0.5
    rx_, ry_ = 32.5 + bx, 19.5 + by
    legs = pose.get('legs') or {}
    feet = {'ff': legs.get('ff', (19.5, gy)), 'bf': legs.get('bf', (38.0, gy)),
            'fn': legs.get('fn', (14.5, gy)), 'bn': legs.get('bn', (33.0, gy))}
    hips = {'ff': (19.5 + bx, 22 + by), 'bf': (37.0 + bx, 22 + by), 'fn': (15.5 + bx, 23 + by), 'bn': (32.5 + bx, 23 + by)}

    def leg(key, ramp, sep=False):
        (x0, y0), (x1, y1) = hips[key], feet[key]
        if dead:
            return
        m = s.C(x0, y0, x1, y1 - 2.0, 2.6, 1.7)
        s.part(m, ramp, sep=sep, light=(x0 - 1.5, (y0 + y1) / 2 - 3, 3, 6))
        hoof = s.R(x1 - 1.6, y1 - 2.0, x1 + 1.2, y1 - 0.4)
        hoof &= ~s.pts([(x1 - 0.3, y1 - 0.6)])       # gespaltener Huf
        s.part(hoof, P['hoof'], light=(x1 - 1, y1 - 2, 2, 2))

    # Schwanz mit Quaste
    wag = pose.get('tail', 0)
    tx, ty = rx_ + 7.4, ry_ - 3.5
    s.part(s.C(tx - 1, ty, tx + 1.8, ty + 3.4 + wag, 0.8) | s.E(tx + 2.0, ty + 4.6 + wag, 1.2, 1.6), P['boar_bristle'])

    leg('ff', far)
    leg('bf', far)

    body = s.E(sx_, sy_, 10.5, 9.0 + br * 0.3) | s.E(rx_, ry_, 8.6, 7.4)
    if dead:
        body = s.E(sx_ + 1, gy - 6.0, 11.0, 6.2) | s.E(rx_, gy - 5.5, 8.6, 5.6)
    s.part(body, fur, light=(sx_ - 2, sy_ - 5, 16, 11), bias=0.25)
    # heller Bauch
    s.tint(s.E(sx_ + 4, (sy_ + 8.5) if not dead else gy - 1.5, 11, 2.2) & body, fur, shift=1)

    # Borstenkamm vom Nacken bis zur Kruppe
    up = 1.0 + pose.get('crest', 0)
    crest = np.zeros_like(body)
    base = [(13.0, 12.5), (15.5, 9.5), (18.5, 8.2), (21.5, 7.8), (24.5, 8.2), (27.5, 9.4), (30.5, 11.0), (33.5, 12.6),
            (36.0, 14.2)]
    for i, (x, y) in enumerate(base):
        x += bx
        y += by if not dead else (gy - 12 - 8.0 + (y - 8) * 0.4)
        ln = (4.4 if i % 2 == 0 else 3.2) * up * (1.0 - 0.06 * abs(i - 3))
        crest |= s.P([(x - 1.9, y + 2.5), (x + 1.6, y - ln), (x + 2.0, y + 2.5)])
    crest &= ~(body & ~s.E(sx_, sy_ - 3, 9.5, 5) & ~s.E(rx_, ry_ - 3, 7, 3.5)) if not dead else ~s.R(0, gy - 6, W, H)
    s.part(crest, P['boar_bristle'], light=(24 + bx, 7 + by, 12, 4), bias=0.1)

    leg('fn', fur, sep=True)
    leg('bn', fur, sep=True)

    # Kopf
    hcx, hcy = 13.0 + hx, 17.0 + hy
    if dead:
        hcx, hcy = 11.0, gy - 6.5
    ta = math.radians(tilt)
    ca, sa = math.cos(ta), math.sin(ta)

    def rot(px, py):
        """Punkt relativ zum Kopfmittelpunkt drehen (Neigung)."""
        return hcx + px * ca + py * sa * 0.9, hcy - px * sa * 0.9 + py * ca
    snx, sny = rot(-9.2, 4.2)
    sr = 2.6
    head = s.E(hcx, hcy, 7.4, 6.8)
    head |= s.P([rot(-2, -6.2), rot(-9.4, 1.4), rot(-9.4, 6.8), rot(1, 6.6)])
    # fernes Ohr
    ear_t = pose.get('ear', 0)
    e0 = rot(2.0, -5.0)
    s.part(s.P([(e0[0] - 3.5, e0[1] + 1.5), (e0[0] - 2.4 - ear_t, e0[1] - 5.6), (e0[0] + 0.2, e0[1] + 0.5)]), far)
    s.part(head, fur, sep=True, light=(hcx - 3, hcy - 3, 8, 7), bias=0.3)
    s.tint(head & s.E(*rot(0.5, 6.4), 5.0, 1.0), fur, shift=-1)         # Kieferschatten
    # Stirnborsten
    fr_ = s.P([rot(-1, -6.4), rot(1.5, -9.0), rot(3.5, -5.8)]) | s.P([rot(2, -6.0), rot(5.0, -8.2), rot(6.0, -4.0)])
    s.part(fr_, P['boar_bristle'], bias=0.3)
    # Schnauzenscheibe
    snout_r = [mix(x, '#40303a', 0.12) for x in P['snout']]
    s.part(s.E(snx + 0.9, sny, 2.0, sr + 0.3), snout_r, sep=True, light=(snx, sny - 1, 2.0, sr))
    s.dots([(snx, sny - 1), (snx, sny + 1)], mix(snout_r[0], OUTLINE, 0.55))
    # Maul
    m0, m1 = rot(-7.8, 6.4), rot(-2.4, 6.0)
    if pose.get('mouth', 0) > 0 or dead:
        s.flat(s.P([m0, (m1[0], m1[1] - 0.5), (m1[0] - 0.5, m1[1] + 1.6), (m0[0] + 1.5, m0[1] + 2.2)]), P['mouth'])
        if dead:
            s.flat(s.pts([(m0[0] + 1.5, m0[1] + 1.5), (m0[0] + 2.5, m0[1] + 1.5)]), P['tongue'][1])
    else:
        s.flat(s.C(m0[0], m0[1], m1[0], m1[1], 0.35), mix(fur[0], OUTLINE, 0.5))
    # Hauer: aus dem Mundwinkel nach oben gebogen
    t0 = rot(-4.8, 6.4)
    t1 = rot(-6.2, 2.8)
    t2 = rot(-7.6, 1.0)
    tusk = s.C(t0[0], t0[1], t1[0], t1[1], 1.35, 0.95) | s.C(t1[0], t1[1], t2[0], t2[1], 0.95, 0.45)
    s.part(tusk, P['tusk'], sep=True, light=(t1[0] - 1, t1[1], 2, 3), bias=0.5)
    # Auge
    ex, ey = [int(v) for v in rot(-3.2, -1.6)]
    eyes = pose.get('eyes', 'open')
    brow = mix(fur[0], OUTLINE, 0.4)
    if eyes == 'x' or dead:
        s.dots([(ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)], P['eye_dark'])
    elif eyes == 'shut':
        s.dots([(ex - 1, ey), (ex, ey + 1), (ex + 1, ey + 1), (ex + 2, ey)], P['eye_dark'])
    else:
        s.dots([(ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)], P['eye_dark'])
        s.dots([(ex, ey)], '#ff6a3a')
        s.dots([(ex - 1, ey - 2), (ex, ey - 1), (ex + 1, ey - 1), (ex + 2, ey - 1), (ex + 2, ey - 2)], brow)
    # nahes Ohr
    e1 = rot(4.0, -4.6)
    ear = s.P([(e1[0] - 1.8, e1[1] + 1.4), (e1[0] + 0.6 - ear_t, e1[1] - 6.4), (e1[0] + 3.4, e1[1] + 1.2)])
    s.part(ear, fur, sep=True, bias=0.3)
    s.tint(ear & s.P([(e1[0] - 0.4, e1[1] + 1), (e1[0] + 0.6 - ear_t, e1[1] - 4.2), (e1[0] + 2.0, e1[1] + 1)]),
           [mix(x, '#2a1a20', 0.45) for x in P['kobold_ear']], shift=-1)
    # Schnaubwolken
    for (px_, py_, r_) in pose.get('puffs', []):
        s.part(s.E(px_, py_, r_, r_ * 0.8), ['#9a96a4', '#cfccd4', '#f0eef2'], bias=0.3)
    # Blitzen der Hauer (Angriffsvorbereitung)
    for (px_, py_) in pose.get('glint', []):
        s.dots([(px_, py_)], '#ffffff')
        s.dots([(px_ - 1, py_), (px_ + 1, py_), (px_, py_ - 1), (px_, py_ + 1)], '#fff2c0')
    return s


def _boar_frames():
    W, H = 44, 32
    g = H - 2
    fr = []
    for (b, t, e) in [(0, 0, 0), (1, 0, 0), (1, 1, 1), (0, 1, 0)]:
        fr.append(boar(dict(breath=b, tail=t, ear=e, hy=0.6 * b)).render())
    # attack: zuruecksetzen, Sturmangriff, Hauer-Hieb nach oben, zurueck
    a = [
        dict(bx=0, hx=2, hy=2, tilt=-10, crest=0.25, ear=-1,
             legs={'fn': (15.5, g), 'bn': (34, g), 'bf': (39, g)}),
        dict(bx=-1, by=0, hx=0, hy=2, tilt=-14, crest=0.3, ear=-1,
             legs={'fn': (10.5, g), 'ff': (16.5, g - 1), 'bn': (36, g), 'bf': (40, g - 1)}),
        dict(bx=-1, by=-1, hx=-1, hy=-1, tilt=20, mouth=1, crest=0.35,
             legs={'fn': (12.5, g), 'ff': (18.5, g), 'bn': (34, g)}),
        dict(hy=0.5, tilt=0),
    ]
    for p, dx in zip(a, [0, 0, -1, 0]):
        fr.append(shift(boar(p).render(), dx, 0))
    # cast: Scharren + Schnauben (Sturmangriff wird vorbereitet)
    for i in range(2):
        p = dict(hx=1, hy=2, tilt=-8, crest=0.35 + 0.15 * i, ear=-1,
                 puffs=[(3.5 - i, 25.5 - i * 1.5, 1.6 + i * 0.5)],
                 legs={'fn': ((12.5, g) if i == 0 else (17.5, g - 2))})
        fr.append(boar(p).render())
    fr.append(boar(dict(hx=2, hy=-1, tilt=10, eyes='shut', ear=1, mouth=1)).render(flash=0.55))
    fr.append(boar(dict(hx=1.5, tilt=4, eyes='shut')).render())
    fr.append(boar(dict(dead=True, tilt=-6)).render())
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 5, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 10, 'loop': False},
        'cast': {'start': 8, 'count': 2, 'fps': 6, 'loop': True},
        'hit': {'start': 10, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 12, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


# ================================================================ Frischling (Raster)
# 1-4 Fell, y/Y Streifen, Q/S/s Schnauzenscheibe, n Nasenloch, e/g Auge, p Ohrinnen, h/H Huf,
# f/F ferne Beine, k Maullinie, t Schwaenzchen
PIGLET = [
    "......43..............",
    ".....4p32...34444443..",
    "....444333.344YYYY4432",
    "...4333333344333333332",
    "..4333333333yyyyyyy32t",
    ".433eg3333333333333321",
    "QS33ee333333YYYYYY3321",
    "Sn333333323333333333t2",
    "Sn2333332232yyyyyy2221",
    ".sk2223332222222222221",
    "..11122221222222222211",
    "....1222.1222.122221..",
    "....3f2...1ff.132.1f..",
    "....hHh...hhh.hHh.hh..",
]
PIG_LEGS = [(3, 8), (9, 12), (13, 17), (18, 21)]      # Spaltenbereiche: vorne nah, vorne fern, hinten nah, hinten fern


def _pig_legend():
    fur = P['piglet']
    far = [mix(x, '#1a1028', 0.35) for x in fur]
    return {'1': (fur, 0), '2': (fur, 1), '3': (fur, 2), '4': (fur, 3),
            'y': (P['piglet_stripe'], 1), 'Y': (P['piglet_stripe'], 2),
            's': P['snout'][0], 'S': P['snout'][1], 'Q': P['snout'][2], 'n': '#3a1a24',
            'e': P['eye_dark'], 'g': '#fffaf0', 'h': P['hoof'][1], 'H': P['hoof'][2],
            'p': P['kobold_ear'][1], 'k': OUTLINE, 't': (fur, 2), 'f': far[1], 'F': far[0],
            'm': P['mouth'], 'r': P['tongue'][1]}


def piglet(pose: dict) -> Spr:
    W, H = 24, 18
    s = Spr(W, H)
    rows = _eye_variant(PIGLET, pose.get('eyes', 'open'))
    if pose.get('mouth'):
        rows = [list(r) for r in rows]
        rows[9][1:5] = list('mmrm')
        rows[10][2:4] = list('11')
        rows = [''.join(r) for r in rows]
    leg = _pig_legend()
    x0, y0 = 1 + pose.get('dx', 0), H - 1 - len(PIGLET)
    hx, hy = pose.get('head', (0, 0))
    bx, by = pose.get('body', (0, 0))
    legs = pose.get('legs', [(0, 0)] * 4)
    ear = pose.get('ear', 0)
    tail = pose.get('tail', 0)

    def sub(cond):
        return [''.join(ch if cond(x, y) else '.' for x, ch in enumerate(r)) for y, r in enumerate(rows)]
    # Beine zuerst (ferne vor nahen), dann Rumpf, dann Kopf
    for i in (1, 3, 0, 2):
        a, b = PIG_LEGS[i]
        dx, dy = legs[i]
        s.grid(sub(lambda x, y, a=a, b=b: y >= 11 and a <= x <= b), x0 + dx, y0 + dy, leg, sep=i in (0, 2))
    s.grid(sub(lambda x, y: y < 11 and x >= 9 and not (x >= 20 and 4 <= y <= 5)), x0 + bx, y0 + by, leg)
    s.grid(sub(lambda x, y: y < 11 and x >= 20 and 4 <= y <= 5), x0 + bx, y0 + by - tail, leg)
    s.grid(sub(lambda x, y: y < 11 and x < 9 and not (y < 2)), x0 + hx, y0 + hy, leg, sep=pose.get('hsep', False))
    s.grid(sub(lambda x, y: y < 2 and x < 9), x0 + hx + ear, y0 + hy + abs(ear), leg)
    for (px_, py_, r_) in pose.get('puffs', []):
        s.part(s.E(px_, py_, r_, r_ * 0.8), ['#9a96a4', '#cfccd4', '#f0eef2'], bias=0.3)
    if pose.get('dead'):
        s.flat(s.pts([(x0 + 3, y0 + 12)]), P['tongue'][1])
    return s


def _piglet_frames():
    W, H = 24, 18
    fr = []
    idle = [dict(), dict(head=(0, 1), tail=1), dict(head=(0, 1), tail=1, ear=1), dict(head=(0, 0), tail=0)]
    for p in idle:
        fr.append(piglet(p).render())
    L0 = [(0, 0)] * 4
    atk = [
        dict(dx=0, head=(0, 1), legs=[(1, 0), (1, 0), (0, 0), (0, 0)], eyes='angry'),
        dict(dx=0, head=(0, 1), body=(0, 0), legs=[(-2, -1), (-1, 0), (1, 0), (2, -1)], eyes='angry'),
        dict(dx=0, head=(0, -1), legs=[(-1, 0), (0, 0), (0, 0), (1, 0)], mouth=True),
        dict(dx=0, legs=L0),
    ]
    for p in atk:
        fr.append(piglet(p).render())
    for i in range(2):
        fr.append(piglet(dict(head=(0, 1), eyes='angry', legs=[(1 + i, -i), (0, 0), (0, 0), (0, 0)],
                              puffs=[(2.5 - i * 0.5, 10.5 - i * 1.5, 1.0 + 0.3 * i)])).render())
    fr.append(piglet(dict(head=(0, -1), eyes='shut', mouth=True, ear=1, legs=[(1, 0), (1, 0), (0, 0), (0, 0)])).render(flash=0.55))
    fr.append(piglet(dict(head=(0, 0), eyes='shut')).render())
    # tot: plumpst flach auf den Bauch, Beinchen seitlich weg, Augen als X, Zunge heraus
    fr.append(piglet(dict(eyes='x', dead=True, mouth=True, body=(0, 2), head=(0, 2),
                          legs=[(-2, 1), (-1, 1), (1, 1), (2, 1)])).render())
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 5, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 10, 'loop': False},
        'cast': {'start': 8, 'count': 2, 'fps': 6, 'loop': True},
        'hit': {'start': 10, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 12, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


# ================================================================ Humanoide: gemeinsame Teile
# Gesicht nach links (3/4), Licht oben links. O Kontur, 1-3 Haut dunkel->hell.
FACE_ROUND = [
    "......OOOOOO.....",
    "....OO3333222OO..",
    "...O33332222222O.",
    "..O3332222222222O",
    "..O3322222222222O",
    ".O33222222222222O",
    ".O32222222222221O",
    "O222222222222221O",
    "1222222222222221O",
    ".O122222222222110",
    "..O11222222211O..",
    "...OO11111111O...",
    ".....OOOOOOOO....",
]
FACE_EYES = ((4, 6), (9, 6))      # nahes Auge (2x2, Glanz), fernes Auge (2x2, schmaler)

FLAMES = [   # Flammen-Frames: 0 rot, 1 orange, 2 gelb, 3 weiss
    ["..0..", ".010.", ".121.", "01210", ".121.", "..1.."],
    ["...0.", "..01.", ".121.", "01321", ".121.", "..1.."],
    [".0...", ".10..", ".121.", "01231", ".121.", "..1.."],
    ["..0..", "..1..", ".121.", "01321", ".121.", "..1.."],
]
FLAMES_SMALL = [
    [".0.", "010", "121", ".1."],
    ["..0", ".01", "121", ".1."],
    ["0..", "10.", "121", ".1."],
    [".0.", ".1.", "131", ".1."],
]
FLAME_BIG = [
    ["...0...", "..010..", "..121..", ".01210.", "0123210", "0123321", ".12321.", "..121..", "...1..."],
    ["..0....", "..01...", "..121..", ".01221.", "0123210", "0123321", ".12321.", "..121..", "...1..."],
    ["....0..", "...10..", "..121..", ".12210.", "0123210", "1233210", ".12321.", "..121..", "...1..."],
    ["...0...", "..101..", "..121..", ".01210.", "0123310", "0123321", ".12321.", "..121..", "...1..."],
]


def flame(s: Spr, cx, bottom, frame, big=False):
    """Flamme mit Unterkante bei 'bottom', mittig bei cx."""
    g = (FLAME_BIG if big == True else FLAMES_SMALL if big == 'small' else FLAMES)[frame % 4]
    leg = {str(i): P['flame'][i] for i in range(4)}
    s.grid(g, int(cx) - len(g[0]) // 2, int(bottom) - len(g) + 1, leg)


def candle(s: Spr, x, y, w, h, fr, big_flame=False, drips=((0, 2), (3, 1)), lit=True):
    """Kerze mit Oberkante y, links x. Tropfnasen (Spalte, Laenge)."""
    m = s.R(x, y, x + w - 1, y + h - 1)
    s.part(m, P['wax'], light=(x + 0.5, y + h / 2 - 1, w / 2 + 0.5, h / 2 + 1), rim=True, bias=0.0)
    # Wachstropfen an der Seite und geschmolzener Rand
    for (dx, ln) in drips:
        s.flat(s.R(x + dx, y, x + dx, y + ln), P['wax'][3] if dx < w / 2 else P['wax'][2])
    s.flat(s.R(x, y, x + w - 1, y), P['wax'][3])
    s.flat(s.pts([(x + w // 2, y - 1)]), '#3a2a2a')               # Docht
    if lit:
        flame(s, x + w // 2, y - 1, fr, big_flame)


def glow(s: Spr, pts, strength=1):
    """Leuchtende Funken: weisser Kern, gelber Kranz."""
    for (x, y) in pts:
        s.dots([(x, y)], P['flame'][3])
        if strength > 1:
            s.dots([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], P['flame'][2])


def arm(s: Spr, shoulder, hand, sleeve, skin, width=2, hand_size=2):
    """Arm als Linie (2 Pixel breit) mit Hand."""
    (sx, sy), (hx, hy) = shoulder, hand
    steps = max(abs(hx - sx), abs(hy - sy), 1)
    m = np.zeros((s.h, s.w), bool)
    for i in range(int(round(steps))):
        t = i / steps
        m |= s.pts([(round(sx + (hx - sx) * t), round(sy + (hy - sy) * t))])
    if width > 1:
        m2 = m.copy()
        m2[:, 1:] |= m[:, :-1]
        m = m2
    s.part(m, sleeve, rim=False, bias=0.2)
    hm = s.R(hx, hy, hx + hand_size - 1, hy + hand_size - 1)
    s.part(hm, skin, rim=False, light=(hx, hy, hand_size, hand_size), bias=0.4)


def face(s: Spr, x0, y0, skin, eyes='open', iris='#f0c030', grid=FACE_ROUND, eye_pos=FACE_EYES, brow=False):
    leg = {'O': OUTLINE, '0': OUTLINE, '1': (skin, len(skin) - 3), '2': (skin, len(skin) - 2),
           '3': (skin, len(skin) - 1)}
    s.grid(grid, x0, y0, leg)
    (nx, ny), (fx, fy) = eye_pos
    nx, ny, fx, fy = x0 + nx, y0 + ny, x0 + fx, y0 + fy
    d = P['eye_dark']
    if eyes == 'x':
        for (ex, ey) in ((nx, ny), (fx, fy)):
            s.dots([(ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)], d)
    elif eyes == 'shut':
        s.dots([(nx - 1, ny + 1), (nx, ny + 1), (nx + 1, ny), (fx, fy + 1), (fx + 1, fy + 1)], d)
    else:
        s.dots([(nx, ny), (nx + 1, ny), (fx, fy), (fx + 1, fy)], d)
        s.dots([(nx + 1, ny + 1), (fx, fy + 1), (fx + 1, fy + 1)], iris)
        s.dots([(nx, ny + 1)], '#ffffff')
        if eyes == 'angry' or brow:
            b = skin[0]
            s.dots([(nx - 1, ny - 1), (nx, ny - 1), (nx + 1, ny - 1), (fx, fy - 1), (fx + 1, fy - 2)], b)


class Weapon:
    """Waffe in lokalen Koordinaten: u entlang des Griffs (vom Griffpunkt), v quer dazu."""

    def __init__(self):
        self.parts = []     # (Punkte-Polygon oder Kapsel, Rampe, sep)

    def poly(self, pts, ramp, sep=True):
        self.parts.append(('poly', pts, ramp, sep))
        return self

    def stick(self, u0, u1, r, ramp, sep=True):
        self.parts.append(('stick', (u0, u1, r), ramp, sep))
        return self

    def draw(self, s: Spr, gx, gy, ang_deg):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), -math.sin(a)
        vx, vy = -uy, ux

        def T(u, v):
            return gx + u * ux + v * vx, gy + u * uy + v * vy
        for kind, data, ramp, sep in self.parts:
            if kind == 'poly':
                m = s.P([T(u, v) for (u, v) in data])
            else:
                u0, u1, r = data
                (x0, y0), (x1, y1) = T(u0, 0), T(u1, 0)
                m = s.C(x0, y0, x1, y1, r)
            s.part(m, ramp, sep=sep, bias=0.2)
        return T


# ================================================================ Kobolde
KOBOLD_BODY = [
    "..AAAAAa..",
    ".AAAAAAad.",
    ".AAAAAAad.",
    ".RRRRRRrr.",
    ".AAAAAaad.",
    ".A.AAa.ad.",
]
KOBOLD_LEGS = [
    "..32..32..",
    "..21..21..",
    ".221.2211.",
]


def _kobold_body(s, x0, y0, legs_dx=(0, 0), rag=None):
    rag = rag or P['rag']
    leg = {'A': (rag, 2), 'a': (rag, 1), 'd': (rag, 0), 'R': (P['rope'], 2), 'r': (P['rope'], 1)}
    kl = {'1': (P['kobold'], 0), '2': (P['kobold'], 1), '3': (P['kobold'], 2)}
    near = [r[:5] for r in KOBOLD_LEGS]
    far = [('.' * 5) + r[5:] for r in KOBOLD_LEGS]
    s.grid(far, x0 + legs_dx[1], y0 + len(KOBOLD_BODY), kl)
    s.grid(near, x0 + legs_dx[0], y0 + len(KOBOLD_BODY), kl)
    s.grid(KOBOLD_BODY, x0, y0, leg)


def kobold_ears(s, x0, y0, twitch=0):
    """Grosse Fledermausohren: fernes Ohr vorne links (klein), nahes hinten rechts (gross)."""
    sk, inner = P['kobold'], P['kobold_ear']
    far = s.P([(x0 + 3, y0 + 5), (x0 - 1 - twitch, y0 + 1 + twitch), (x0 + 3, y0 + 8)])
    s.part(far, [mix(x, '#1a1028', 0.3) for x in sk])
    near = s.P([(x0 + 14, y0 + 4), (x0 + 20.6 + twitch * 0.5, y0 + 0.5 + twitch), (x0 + 18.5, y0 + 5.5), (x0 + 15, y0 + 9)])
    s.part(near, sk, bias=0.3)
    s.tint(near & s.P([(x0 + 15.5, y0 + 5), (x0 + 19.4 + twitch * 0.5, y0 + 2 + twitch), (x0 + 16, y0 + 8)]), inner, shift=-1)


def kobold_face_extras(s, x0, y0, mouth='grin'):
    """Spitze Nase und breites Grinsen mit Zahn."""
    sk = P['kobold']
    s.dots([(x0 - 1, y0 + 8), (x0, y0 + 8)], sk[2])
    s.dots([(x0 - 1, y0 + 9)], sk[1])
    if mouth == 'grin':
        s.dots([(x0 + 2, y0 + 10), (x0 + 3, y0 + 10), (x0 + 4, y0 + 10), (x0 + 5, y0 + 10), (x0 + 6, y0 + 9)], P['mouth'])
        s.dots([(x0 + 4, y0 + 10)], P['teeth'])
    elif mouth == 'open':
        s.flat(s.R(x0 + 2, y0 + 9, x0 + 6, y0 + 10), P['mouth'])
        s.dots([(x0 + 3, y0 + 9), (x0 + 5, y0 + 9)], P['teeth'])
        s.dots([(x0 + 3, y0 + 10), (x0 + 4, y0 + 10)], P['tongue'][1])
    elif mouth == 'ouch':
        s.dots([(x0 + 3, y0 + 10), (x0 + 4, y0 + 9), (x0 + 5, y0 + 10), (x0 + 6, y0 + 9)], P['mouth'])


def shovel():
    """Schaufel: Griffknauf bei u=+1.5, Stiel nach -u, Blatt am Ende (u -5 .. -9)."""
    w = Weapon()
    w.stick(-5, 1.2, 0.85, P['wood'])
    w.poly([(1.0, -1.6), (2.8, -1.6), (2.8, 1.6), (1.0, 1.6)], P['wood'])
    w.poly([(-4.4, -2.4), (-4.4, 2.4), (-8.6, 2.2), (-10.0, 0), (-8.6, -2.2)], P['rust'])
    return w


def kobold_digger(pose: dict) -> Spr:
    W, H = pose.get('size', (24, 30))
    ox, oy = pose.get('off', (0, 0))
    s = Spr(W, H)
    fr = pose.get('fr', 0)
    hx, hy = pose.get('hx', 0), pose.get('hy', 0)
    bx, by = pose.get('bx', 0) + ox, pose.get('by', 0) + oy
    sk = P['kobold']
    bodyx, bodyy = 7 + bx, 20 + by
    headx, heady = 3 + hx + bx, 8 + hy + by
    fh = pose.get('far_hand', (0, 0))
    arm(s, (bodyx + 7, bodyy + 1), (bodyx + 9 + fh[0], bodyy + 4 + fh[1]),
        [mix(x, '#1a1028', 0.35) for x in sk], [mix(x, '#1a1028', 0.3) for x in sk])
    hand = pose.get('hand', (0, 0))
    gx, gy = bodyx - 3 + hand[0], bodyy + 1 + hand[1]
    behind = pose.get('behind', False)
    if pose.get('tool') is not None and behind:
        shovel().draw(s, gx + 0.5, gy + 0.5, pose['tool'] + 180)
    _kobold_body(s, bodyx, bodyy, pose.get('legs_dx', (0, 0)))
    kobold_ears(s, headx, heady, pose.get('ear', 0))
    face(s, headx, heady, sk, pose.get('eyes', 'open'), iris='#f4d040')
    kobold_face_extras(s, headx, heady, pose.get('mouth', 'grin'))
    if pose.get('candle', True):
        candle(s, headx + 7 + pose.get('cdx', 0), heady - 3 + pose.get('cdy', 0), 3, 3, fr, big_flame='small',
               drips=((0, 2), (2, 1)))
    if pose.get('tool') is not None:
        # Klingenrichtung (Grad) -> Griffrichtung = Klinge + 180
        if not behind:
            shovel().draw(s, gx + 0.5, gy + 0.5, pose['tool'] + 180)
        for (px_, py_) in pose.get('glint', []):
            glow(s, [(px_, py_)], 2)
        arm(s, (bodyx + 3, bodyy + 1), (gx, gy), sk, sk)
    return s


def _kobold_digger_frames():
    W, H = 24, 30
    fr = []
    for i, (hy, e) in enumerate([(0, 0), (0, 0), (1, 1), (1, 0)]):
        fr.append(kobold_digger(dict(fr=i, hy=hy, ear=e, tool=265, hand=(0, hy))).render())
    # attack: Schaufel ueber den Kopf, Hieb nach links, Nachschwung in den Boden, zurueck
    atk = [
        dict(fr=0, tool=15, hand=(10, -4), hy=-1, hx=-1, eyes='angry', mouth='open', far_hand=(1, -1), behind=True),
        dict(fr=1, tool=172, hand=(9, -2), hx=-1, bx=-1, eyes='angry', mouth='open'),
        dict(fr=2, tool=218, hand=(7, 1), hx=-1, bx=-1, hy=1, eyes='angry', mouth='grin'),
        dict(fr=3, tool=255, hand=(0, 0)),
    ]
    for p in atk:
        fr.append(kobold_digger(p).render())
    # cast: holt weit aus, das Schaufelblatt blitzt
    for i in range(4):
        tool = 112 + (i % 2) * 5
        hand = (3, -3)
        gx, gy = 7 - 3 + hand[0], 20 + 1 + hand[1]
        a = math.radians(tool)
        tip = (int(gx + math.cos(a) * 10), int(gy - math.sin(a) * 10))
        glint = [tip] if i in (1, 2) else [(tip[0] + 1, tip[1] + 1)] if i == 3 else []
        fr.append(kobold_digger(dict(fr=i, tool=tool, hand=hand, hy=-(i % 2), eyes='angry', mouth='grin',
                                     far_hand=(1, -1), glint=glint)).render())
    fr.append(shift(kobold_digger(dict(fr=1, hx=1, hy=0, eyes='shut', mouth='ouch', tool=285, ear=1)).render(flash=0.55), 1, 0))
    fr.append(shift(kobold_digger(dict(fr=2, hx=1, eyes='shut', mouth='ouch', tool=275)).render(), 1, 0))
    fr.append(_kobold_dead(kobold_digger, dict(tool=None), prop='shovel'))
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 5, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 10, 'loop': False},
        'cast': {'start': 8, 'count': 4, 'fps': 8, 'loop': True},
        'hit': {'start': 12, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 14, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


def kobold_firestarter(pose: dict) -> Spr:
    """Koboldfunkenzuendler: uebergrosse Kerze in beiden Haenden, Funken ringsum."""
    W, H = pose.get('size', (24, 30))
    ox, oy = pose.get('off', (0, 0))
    s = Spr(W, H)
    fr = pose.get('fr', 0)
    hx, hy = pose.get('hx', 0), pose.get('hy', 0)
    bx, by = pose.get('bx', 0) + ox, pose.get('by', 0) + oy
    sk = P['kobold']
    skd = [mix(x, '#1a1028', 0.3) for x in sk]
    bodyx, bodyy = 8 + bx, 20 + by
    headx, heady = 3 + hx + bx, 8 + hy + by
    cdx, cdy = pose.get('cand', (0, 0))
    cx0, cy0 = 2 + cdx + bx, 15 + cdy + by          # Kerze: links oben
    cw, ch = 5, 9
    _kobold_body(s, bodyx, bodyy, pose.get('legs_dx', (0, 0)), rag=P['rag_red'])
    # ferner Arm greift hinter die Kerze
    arm(s, (bodyx + 2, bodyy + 1), (cx0 + cw, cy0 + 3), skd, skd)
    kobold_ears(s, headx, heady, pose.get('ear', 0))
    face(s, headx, heady, sk, pose.get('eyes', 'open'), iris='#ffb030')
    kobold_face_extras(s, headx, heady, pose.get('mouth', 'grin'))
    if pose.get('candle', True):
        # Feuerschein auf dem Gesicht
        s.tint(s.E(cx0 + 3, cy0 - 3, 7, 6) & s.X.__ge__(headx) & ~s.E(cx0 + 3, cy0 - 3, 4, 3.5), sk, shift=1)
        if pose.get('halo'):
            ring = s.E(cx0 + cw / 2, cy0 - 4.5, 5.5, 6.0) & ~s.E(cx0 + cw / 2, cy0 - 4.5, 4.4, 5.0)
            s.flat(ring & ((s.X.astype(int) + s.Y.astype(int) + fr) % 3 == 0), P['flame'][1])
        candle(s, cx0, cy0, cw, ch, fr, big_flame=pose.get('big', True), drips=((0, 3), (1, 1), (4, 2)))
        # nahe Hand vorne an der Kerze
        arm(s, (bodyx + 3, bodyy + 1), (cx0 + cw - 2, cy0 + 5), sk, sk)
    for (x, y, st) in pose.get('sparks', []):
        if st >= 2:
            glow(s, [(int(x), int(y))], 2)
        else:
            s.dots([(int(x), int(y))], P['flame'][2] if st == 1 else P['flame'][1])
    for (x, y, r) in pose.get('fireball', []):
        s.part(s.E(x, y, r, r * 0.85), P['flame'], bias=0.4, rim=False)
        s.dots([(int(x), int(y))], P['flame'][3])
    return s


# umkreisende Funken (Winkel-Offsets, Radius) - Leerlauf
_SPARK_RING = [(0, 9.0, 1), (95, 10.5, 0), (170, 8.5, 1), (250, 10.0, 0), (320, 9.5, 2)]


def _sparks(center, rot, shrink=1.0, strong=False):
    cx, cy = center
    out = []
    for (a, r, st) in _SPARK_RING:
        ang = math.radians(a + rot)
        out.append((cx + math.cos(ang) * r * shrink, cy - math.sin(ang) * r * shrink * 0.8, 2 if strong and st else st))
    return out


def _kobold_firestarter_frames():
    W, H = 24, 30
    fr = []
    ctr = (12, 16)
    for i in range(4):
        fr.append(kobold_firestarter(dict(fr=i, hy=1 if i in (2, 3) else 0, ear=1 if i == 2 else 0,
                                          sparks=_sparks(ctr, i * 25))).render())
    # attack: Kerze zurueck, nach vorne stossen, Funkenball fliegt, zurueck
    atk = [
        dict(fr=0, cand=(3, -1), hx=1, eyes='angry', mouth='grin', sparks=_sparks(ctr, 100, 0.8)),
        dict(fr=1, cand=(1, 0), bx=-1, hx=-1, eyes='angry', mouth='open', big=True,
             sparks=_sparks(ctr, 130, 0.9)),
        dict(fr=2, cand=(1, 1), bx=-1, hx=-1, eyes='angry', mouth='open', fireball=[(3.0, 11.0, 2.2)],
             sparks=[(5, 8, 2), (1, 16, 1), (6, 6, 0)]),
        dict(fr=3, cand=(0, 0), sparks=_sparks(ctr, 175)),
    ]
    for p in atk:
        fr.append(kobold_firestarter(p).render())
    # cast: Flamme wird gross, Funken sammeln sich an der Kerze
    fc = (3.5, 9.0)
    for i in range(4):
        shrink = [1.0, 0.75, 0.55, 0.4][i]
        sp = _sparks(fc, i * 40, shrink, strong=i >= 2)
        fr.append(kobold_firestarter(dict(fr=i, big=True, hy=-(i % 2), eyes='angry', mouth='grin', halo=i >= 1,
                                          cand=(0, -1), sparks=sp)).render())
    fr.append(shift(kobold_firestarter(dict(fr=1, hx=0, hy=-1, eyes='shut', mouth='ouch', ear=1, cand=(1, 1))).render(flash=0.55), 1, 0))
    fr.append(shift(kobold_firestarter(dict(fr=2, hx=1, eyes='shut', mouth='ouch', cand=(1, 0))).render(), 1, 0))
    fr.append(_kobold_dead(kobold_firestarter, dict(), prop='candle_big'))
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 5, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 10, 'loop': False},
        'cast': {'start': 8, 'count': 4, 'fps': 8, 'loop': True},
        'hit': {'start': 12, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 14, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


def _kobold_dead(fn, pose, prop=None, W=24, H=30):
    """Kobold liegt auf dem Ruecken (gedreht), Kerze erloschen daneben, Werkzeug am Boden."""
    p = dict(pose)
    p.update(size=(40, 40), off=(8, 6), eyes='x', mouth='open', candle=False)
    body = fn(p).render(rot=-1)
    ys, xs = np.where(body.a[:, :, 3] > 0)
    fig = body.crop(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    out = Canvas(W, H)
    # Requisiten dahinter
    s = Spr(W, H)
    g = H - 2
    if prop == 'shovel':
        shovel().draw(s, 19.5, g - 1.5, 185 + 180)
    elif prop == 'candle_big':
        s.part(s.R(15, g - 3, 23, g), P['wax'], light=(18, g - 3, 5, 2))
        s.flat(s.pts([(14, g - 2)]), '#3a2a2a')
    s2 = s.render()
    out.paste(s2, 0, 0)
    out.paste(fig, (W - fig.w) // 2, H - fig.h)
    # erloschene Kerze liegt vorne, Rauchfaden
    s = Spr(W, H)
    s.part(s.R(2, g - 1, 5, g), P['wax'], light=(3.5, g - 1, 2, 1.5))
    s.flat(s.pts([(1, g - 1)]), '#3a2a2a')
    s.flat(s.pts([(0, g - 3), (1, g - 4), (0, g - 6)]), '#b8b4c0')
    out.paste(s.render(), 0, 0)
    return out


# ================================================================ Diebe (Mensch)
FACE_HUMAN = [
    "...OOOOOO.....",
    "..O332222O....",
    ".O33222222O...",
    "O3322222222O..",
    "O3222222222O..",
    "O2222222222O..",
    "O22222222222O.",
    "222222222222O.",
    "O12222222221O.",
    ".O112222221O..",
    "..O111111OO...",
    "....OOOOO.....",
]
HUMAN_EYES = ((2, 6), (6, 6))
HOOD = [
    "......bcccb.......",
    "....bcddcccbb.....",
    "...bcdcccccbbbb...",
    "..bcdkkkkkcbbbbbba",
    ".bck.....kcbbbbbaa",
    ".bk.......kbbbbba.",
    "bck........kbbbba.",
    "bk.........kbbba..",
    "bk.........kbbbba.",
    "bk........kcbbbba.",
    ".b.......kcbbbbaa.",
    ".bb.....kcbbbbaa..",
    "..bbbbbbbbbbbaaa..",
    "...aaabbbbbaaa....",
]
SCARF = [
    "CCCCCCCCc.....",
    "CCCCCCCcc.....",
    ".dcccccdd.....",
]
THIEF_BODY = [
    "..bbcccbb...",
    ".bcccbbbbba.",
    ".bbGGGGgbba.",
    "..GGGGGggf..",
    "..GGGGGggf..",
    "..LLLYLlll..",
    "..GGGGGggf..",
]
THIEF_LEGS = [      # Spalten 0-5 nahes Bein, 6-11 fernes Bein
    "..PPp..ppf..",
    "..PPp..ppf..",
    "..PP...pf...",
    "..PPp..pf...",
    "..PP...pf...",
    "..PP...pf...",
    ".nnN...nnN..",
    ".nnn..nnnn..",
]
# Hauptmann: breiter Mantel, rote Schaerpe, hohe Stiefel
CAPTAIN_BODY = [
    "....CCCCCCc.....",
    "...CCWWCCCccc...",
    "..CCCCWCCCCccc..",
    ".CCCCCCCCCCccce.",
    ".CCCCCCCCCCccce.",
    "..RRRRRRRRRrrr..",
    "..LLLLLYLLllll..",
    "..CCCCCCCCCcce..",
    ".CCCCCCCCCCccee.",
    ".CCCCCC..CCccee.",
]
CAPTAIN_LEGS = [
    "...PPPp..ppf....",
    "...PPPp..ppf....",
    "...PPp...ppf....",
    "..nNNn...nNn....",
    "..nNNn...nNn....",
    "..nNNn...nNn....",
    "..nNNn...nNn....",
    ".nnnnn..nnnnn...",
]
HAT = [
    "..............wWW.....",
    "............wWWWWw....",
    "......bbb..wWYYWw.....",
    "....bRRRRbwWYyyW......",
    "...bRRRRRRrWYyW.......",
    "..bRRRRRRRRrrYy.......",
    ".bRRRRRRRRRRrrr.......",
    "bRrrrrrrrrrrrrrrrb....",
    ".bbbbbbbbbbbbbbbb.....",
]


def _body_legend(captain):
    L = {'b': (P['hood'], 1), 'c': (P['hood'], 2), 'a': (P['hood'], 0), 'd': (P['hood'], 3),
         'G': (P['cloth_g'], 2), 'g': (P['cloth_g'], 1), 'f': (P['cloth_g'], 0),
         'L': (P['wood'], 2), 'l': (P['wood'], 1), 'Y': (P['gold'], 2), 'y': (P['gold'], 1),
         'P': (P['cloth_g'], 2), 'p': (P['cloth_g'], 1), 'n': P['boot'][0], 'N': P['boot'][1]}
    if captain:
        L.update({'C': (P['coat'], 2), 'c': (P['coat'], 1), 'e': (P['coat'], 0), 'W': (P['feather'], 2),
                  'R': (P['hat_red'], 2), 'r': (P['hat_red'], 1), 'n': P['boot'][1], 'N': P['boot'][2]})
    return L


def club():
    w = Weapon()
    w.stick(-1.5, 4, 0.75, P['wood'])
    w.poly([(3, -1.1), (10.5, -1.9), (11.5, 0), (10.5, 1.9), (3, 1.1)], P['wood'])
    return w


def sabre(tint=None):
    """Krummsaebel: Klinge nach +u, leicht nach -v gebogen. tint: Rampe fuer blitzende Klinge."""
    w = Weapon()
    steel = tint or P['steel']
    top, bot = [], []
    for i in range(9):
        u = 2.0 + i * 1.45
        curve = -0.02 * (u - 2) ** 2
        half = 1.0 - i * 0.06
        top.append((u, curve - half))
        bot.append((u, curve + half * 0.9))
    tip = (2.0 + 9 * 1.45, -0.02 * (9 * 1.45) ** 2 - 0.6)
    w.poly(top + [tip] + bot[::-1], steel)
    w.stick(-1.6, 0.8, 0.7, P['wood'])                      # Griff
    w.poly([(1.0, -2.2), (2.0, -2.2), (2.0, 2.2), (1.0, 2.2)], P['gold'])   # Parierstange
    return w


def bandit(pose: dict, captain=False) -> Spr:
    W, H = pose.get('size', (36, 42) if captain else (32, 36))
    ox, oy = pose.get('off', (0, 0))
    s = Spr(W, H)
    hx, hy = pose.get('hx', 0), pose.get('hy', 0)
    bx, by = pose.get('bx', 0) + ox, pose.get('by', 0) + oy
    gy = (40 if captain else 34) + oy
    bl = _body_legend(captain)
    body = CAPTAIN_BODY if captain else THIEF_BODY
    legs = CAPTAIN_LEGS if captain else THIEF_LEGS
    bw = len(body[0])
    body_x = (10 if captain else 10) + bx
    legs_y = gy - len(legs) + 1
    body_y = legs_y - len(body) + by
    fx = (9 if captain else 9) + hx + bx
    fy = body_y - 11 + hy
    skin = P['skin_h']
    sk_far = [mix(x, '#1a1028', 0.3) for x in skin]
    sleeve = P['coat'] if captain else P['cloth_g']
    sleeve_far = [mix(x, '#1a1028', 0.35) for x in sleeve]
    near_sh = (body_x + 2, body_y + 2)
    far_sh = (body_x + bw - 4, body_y + 2)
    hand = pose.get('hand', (0, 0))
    gx, gy_ = body_x + hand[0], body_y + 6 + hand[1]
    fh = pose.get('far_hand', (0, 0))
    far_hand = (far_sh[0] + 2 + fh[0], body_y + 6 + fh[1])
    wpn = pose.get('weapon', 'club')
    wang = pose.get('wang', 60)
    tint = pose.get('tint')

    def draw_weapon():
        if wpn is None:
            return
        wp = sabre(tint) if captain else club()
        wp.draw(s, gx + 0.5, gy_ + 0.5, wang)

    # Umhang/Federbusch hinten, ferner Arm
    arm(s, far_sh, far_hand, sleeve_far, sk_far)
    if pose.get('behind'):
        draw_weapon()
    ldx = pose.get('legs_dx', (0, 0))
    s.grid([r[6 if not captain else 8:].rjust(len(r), '.') for r in legs], body_x + ldx[1], legs_y, bl)
    s.grid([r[:6 if not captain else 8] for r in legs], body_x + ldx[0], legs_y, bl)
    s.grid(body, body_x, body_y, bl)
    face(s, fx, fy, skin, pose.get('eyes', 'open'), iris='#3a6a44' if not captain else '#4a3a2a',
         grid=FACE_HUMAN, eye_pos=HUMAN_EYES, brow=captain)
    if captain:
        # verschmitztes Grinsen, Bartstoppeln
        mo = pose.get('mouth', 'grin')
        if mo == 'grin':
            s.dots([(fx + 2, fy + 9), (fx + 3, fy + 9), (fx + 4, fy + 9), (fx + 5, fy + 8)], P['mouth'])
        elif mo == 'open':
            s.flat(s.R(fx + 2, fy + 8, fx + 4, fy + 9), P['mouth'])
            s.dots([(fx + 2, fy + 8), (fx + 3, fy + 8)], P['teeth'])
        else:
            s.dots([(fx + 2, fy + 9), (fx + 3, fy + 8), (fx + 4, fy + 9)], P['mouth'])
        s.dots([(fx + 1, fy + 10), (fx + 3, fy + 10), (fx + 5, fy + 10), (fx + 7, fy + 10)], skin[0])
        # Haare hinten unter dem Hut
        hair = ['#2a1a1a', '#4a2e22', '#6a4430']
        s.part(s.P([(fx + 9, fy + 1), (fx + 14, fy + 1), (fx + 14.5, fy + 8), (fx + 11, fy + 9), (fx + 9.5, fy + 5)]), hair)
        hat_leg = {'b': (P['hat_red'], 0), 'R': (P['hat_red'], 2), 'r': (P['hat_red'], 1),
                   'w': (P['feather'], 1), 'W': (P['feather'], 2), 'Y': (P['plume'], 2), 'y': (P['plume'], 1)}
        s.grid(HAT, fx - 3, fy - 5 + pose.get('hat_dy', 0), hat_leg)
    else:
        hood = {'a': (P['hood'], 0), 'b': (P['hood'], 1), 'c': (P['hood'], 2), 'd': (P['hood'], 3), 'k': OUTLINE}
        s.grid(HOOD, fx - 2, fy - 2, hood)
        s.grid(SCARF, fx - 1, fy + 8, {'C': (P['scarf'], 2), 'c': (P['scarf'], 1), 'd': (P['scarf'], 0)})
        # Tuchzipfel flattert hinten
        t = pose.get('flap', 0)
        s.part(s.P([(fx + 8, fy + 9), (fx + 12 + t, fy + 10 - t), (fx + 11 + t, fy + 12), (fx + 8, fy + 11)]), P['scarf'])
    if not pose.get('behind'):
        draw_weapon()
    arm(s, near_sh, (gx, gy_), sleeve, skin)
    for (px_, py_, st) in pose.get('glint', []):
        glow(s, [(px_, py_)], st)
        if st >= 3:
            s.dots([(px_ - 2, py_), (px_ + 2, py_), (px_, py_ - 2), (px_, py_ + 2)], '#ffd0c0')
    return s


def _tip(captain, hand, wang, length, bx=0, by=0):
    """Position der Waffenspitze fuer Glanzeffekte."""
    W, H = (36, 42) if captain else (32, 36)
    gy = 40 if captain else 34
    legs = CAPTAIN_LEGS if captain else THIEF_LEGS
    body = CAPTAIN_BODY if captain else THIEF_BODY
    body_x = (10 if captain else 10) + bx
    body_y = gy - len(legs) + 1 - len(body) + by
    gx, gy_ = body_x + hand[0] + 0.5, body_y + 6 + hand[1] + 0.5
    a = math.radians(wang)
    return int(gx + math.cos(a) * length), int(gy_ - math.sin(a) * length)


def _bandit_frames(captain):
    W, H = (36, 42) if captain else (32, 36)
    fr = []
    L = 14 if captain else 10
    idle_w = 80 if captain else 75
    for i in range(4):
        b = 1 if i in (1, 2) else 0
        if captain:
            # Saebel laessig auf der Schulter
            p = dict(hy=b, hand=(5, -3 + b), far_hand=(0, b), wang=32 + (i % 2) * 3, behind=True)
        else:
            # Knueppel locker auf der Schulter
            p = dict(hy=b, hand=(5, -3 + b), far_hand=(0, b), wang=38 + (i % 2) * 3, behind=True, flap=i % 2)
        fr.append(bandit(p, captain).render())
    # attack: ausholen (Waffe hinten oben), Hieb nach links, Nachschwung, zurueck
    atk = [
        dict(hand=(9, -4), wang=40, behind=True, hx=1, eyes='angry', mouth='grin', far_hand=(2, -1), flap=1),
        dict(hand=(6 if captain else 3, -3), wang=165, bx=-2, hx=-2, eyes='angry', mouth='open', legs_dx=(-2, 0), flap=0),
        dict(hand=(6 if captain else 3, 1), wang=218, bx=-2, hx=-2, hy=1, eyes='angry', mouth='open', legs_dx=(-2, 0), flap=1),
        dict(hand=(4, -2), wang=48 if captain else 52, behind=True, flap=0),
    ]
    for p in atk:
        fr.append(bandit(p, captain).render())
    # cast: weit ausholen, Klinge blitzt (Hauptmann: rot-weiss)
    red = ['#6a1020', '#c83040', '#ff8080', '#ffffff']
    for i in range(4):
        hand = (10, -5 - (i % 2))
        wang = 28 + (i % 2) * 4
        tip = _tip(captain, hand, wang, L - 1)
        mid = _tip(captain, hand, wang, L * 0.55)
        glint = [(tip[0], tip[1], 3 if i in (1, 3) else 2)] if i != 0 else [(mid[0], mid[1], 2)]
        p = dict(hand=hand, wang=wang, behind=True, eyes='angry', mouth='grin', far_hand=(2, -2), hx=1,
                 hy=-(i % 2), flap=i % 2, glint=glint)
        if captain:
            p['tint'] = red if i in (1, 3) else None
        fr.append(bandit(p, captain).render())
    fr.append(shift(bandit(dict(hand=(2, -2), wang=110, hx=1, hy=-1, eyes='shut', mouth='ouch', flap=1, hat_dy=-1),
                           captain).render(flash=0.55), 2, 0))
    fr.append(shift(bandit(dict(hand=(1, 0), wang=95, hx=1, eyes='shut', mouth='ouch'), captain).render(), 1, 0))
    fr.append(_bandit_dead(captain))
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 5, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 10, 'loop': False},
        'cast': {'start': 8, 'count': 4, 'fps': 8, 'loop': True},
        'hit': {'start': 12, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 14, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


def _bandit_dead(captain):
    W, H = (36, 42) if captain else (32, 36)
    body = bandit(dict(size=(56, 56), off=(10, 8), eyes='x', mouth='open', weapon=None, hand=(-1, 3), far_hand=(-1, 2)),
                  captain).render(rot=-1)
    ys, xs = np.where(body.a[:, :, 3] > 0)
    fig = body.crop(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    out = Canvas(W, H)
    s = Spr(W, H)
    g = H - 2
    if captain:
        sabre().draw(s, 4.5, g - 0.5, 5)
    else:
        club().draw(s, 3.5, g - 0.5, 8)
    out.paste(s.render(), 0, 0)
    out.paste(fig, (W - fig.w) // 2 + 1, H - fig.h)
    return out


# ================================================================ Boss: Kornkoenig Knarz
def pitchfork(flash=False):
    """Riesige rostige Mistgabel: Stiel nach -u, Zinken nach +u (ab u=15)."""
    w = Weapon()
    rust = P['rust']
    w.stick(-13, 10, 1.1, P['wood'])
    w.poly([(9.0, -5.0), (11.2, -5.0), (11.2, 5.0), (9.0, 5.0)], rust)
    for v in (-4.0, 0.0, 4.0):
        w.poly([(10.5, v - 0.9), (16.5, v - 0.7), (19.0, v), (16.5, v + 0.7), (10.5, v + 0.9)],
               ['#b8b8c8', '#e8e8f0', '#ffffff', '#ffffff'] if flash else rust)
    return w


def knarz(pose: dict) -> Spr:
    W, H = pose.get('size', (56, 56))
    ox, oy = pose.get('off', (0, 0))
    s = Spr(W, H)
    fr = pose.get('fr', 0)
    sk = P['kobold']
    skd = [mix(x, '#1a1028', 0.3) for x in sk]
    gy = H - 2 - (H - 56) + oy
    bx, by = pose.get('bx', 0) + ox, pose.get('by', 0) + oy
    hx_, hy_ = pose.get('hx', 0), pose.get('hy', 0)
    br = pose.get('breath', 0)
    # Anker
    bcx, bcy = 31 + bx, 42 + by
    hcx, hcy = 27 + bx + hx_, 27 + by + hy_ + br * 0.5
    # Hand-/Waffenposition
    hand = pose.get('hand', (0, 0))
    gx, gyy = 10 + bx + hand[0], 41 + by + hand[1]
    fang = pose.get('fork', 95)
    fork_flash = pose.get('fork_flash', False)
    behind = pose.get('behind', False)

    # ferner Arm + Fuesse
    fh = pose.get('far_hand', (0, 0))
    far_h = (44 + bx + fh[0], 42 + by + fh[1])
    s.part(s.C(40 + bx, 35 + by, far_h[0], far_h[1], 2.8, 2.2), skd)
    s.part(s.E(far_h[0] + 0.5, far_h[1] + 1, 2.6, 2.3), skd)
    for (fx_, ramp) in ((36 + bx, skd), (24 + bx, sk)):
        leg = s.C(fx_, bcy + 6, fx_ - 1, gy - 2, 3.2, 2.8)
        s.part(leg, ramp, light=(fx_ - 2, gy - 5, 3, 4))
        s.part(s.E(fx_ - 2.5, gy - 1.2, 4.2, 1.9), ramp, sep=True, light=(fx_ - 3, gy - 2, 4, 2))
    if behind and fang is not None:
        pitchfork(fork_flash).draw(s, gx + 0.5, gyy + 0.5, fang)
    # Bauch
    belly = s.E(bcx, bcy, 13.5 + br * 0.4, 11.5)
    s.part(belly, sk, light=(bcx - 4, bcy - 5, 14, 12), bias=0.15)
    s.tint(belly & s.E(bcx - 3, bcy + 2, 8, 7), sk, shift=1)
    s.dots([(bcx - 3, bcy + 3), (bcx - 2, bcy + 4)], sk[0])             # Bauchnabel
    # Lendenschurz mit Strickguertel
    skirt = s.E(bcx, bcy + 9, 12.5, 4.5) & belly
    s.part(skirt, P['rag'], light=(bcx - 3, bcy + 7, 12, 4))
    for i in range(6):
        x = bcx - 11 + i * 4.3
        s.cut(s.P([(x, bcy + 13.6), (x + 1.6, bcy + 11.6), (x + 3.2, bcy + 13.6)]) & skirt)
    s.part(s.E(bcx, bcy + 5.2, 13.2, 1.5) & belly | s.E(bcx, bcy + 5.2, 13.2, 1.5) & s.E(bcx, bcy, 14, 12),
           P['rope'], light=(bcx - 5, bcy + 4.5, 10, 1.5))
    # Ohren
    ear_t = pose.get('ear', 0)
    s.part(s.P([(hcx - 7, hcy - 3), (hcx - 17 - ear_t, hcy - 8 + ear_t), (hcx - 9, hcy + 2)]), skd)
    near_ear = s.P([(hcx + 8, hcy - 4), (hcx + 22 + ear_t, hcy - 11 + ear_t), (hcx + 17, hcy - 1), (hcx + 10, hcy + 4)])
    s.part(near_ear, sk, bias=0.3)
    s.tint(near_ear & s.P([(hcx + 11, hcy - 2), (hcx + 20 + ear_t, hcy - 9 + ear_t), (hcx + 12, hcy + 2)]),
           P['kobold_ear'], shift=-1)
    # Kopf
    head = s.E(hcx, hcy, 12.5, 10.2)
    head |= s.E(hcx - 3, hcy + 5, 10, 6)          # Hamsterbacken/Doppelkinn
    s.part(head, sk, sep=True, light=(hcx - 4, hcy - 4, 11, 9), bias=0.25)
    # Nase (Hakennase nach links)
    nose = s.P([(hcx - 8, hcy - 2), (hcx - 16, hcy + 3), (hcx - 13, hcy + 5.5), (hcx - 7, hcy + 3)])
    s.part(nose, sk, sep=True, light=(hcx - 12, hcy + 1, 4, 3), bias=0.3)
    # Augen
    eyes = pose.get('eyes', 'open')
    ex, ey = int(hcx - 8), int(hcy - 3)
    fx, fy = int(hcx - 1), int(hcy - 3)
    d = P['eye_dark']
    if eyes == 'x':
        for (x, y) in ((ex + 1, ey + 1), (fx + 1, fy + 1)):
            s.dots([(x - 1, y - 1), (x + 1, y - 1), (x, y), (x - 1, y + 1), (x + 1, y + 1)], d)
    elif eyes == 'shut':
        s.dots([(ex, ey + 2), (ex + 1, ey + 1), (ex + 2, ey + 2), (fx, fy + 2), (fx + 1, fy + 1), (fx + 2, fy + 2)], d)
    else:
        s.flat(s.R(ex, ey, ex + 2, ey + 2), d)
        s.flat(s.R(fx, fy, fx + 2, fy + 2), d)
        s.dots([(ex + 1, ey + 1), (ex + 2, ey + 1), (ex + 1, ey + 2), (ex + 2, ey + 2)], '#f4d040')
        s.dots([(fx + 1, fy + 1), (fx + 2, fy + 1), (fx + 1, fy + 2)], '#f4d040')
        s.dots([(ex + 1, ey + 1), (fx + 1, fy + 1)], '#ffffff')
        s.dots([(ex + 1, ey + 2), (fx + 2, fy + 2)], '#c89020')
        # buschige, boese Brauen
        s.dots([(ex - 1, ey - 2), (ex, ey - 1), (ex + 1, ey - 1), (ex + 2, ey), (ex + 3, ey)], sk[0])
        s.dots([(fx - 1, fy), (fx, fy - 1), (fx + 1, fy - 1), (fx + 2, fy - 1), (fx + 3, fy - 2)], sk[0])
    # Maul
    mo = pose.get('mouth', 'grin')
    mx, my = int(hcx - 9), int(hcy + 6)
    if mo == 'grin':
        s.flat(s.P([(mx, my - 1), (mx + 13, my - 1.5), (mx + 12, my + 1.2), (mx + 2, my + 1.5)]), P['mouth'])
        s.dots([(mx + 2, my - 1), (mx + 5, my - 1), (mx + 9, my - 1), (mx + 5, my), (mx + 10, my + 0)], P['teeth'])
    elif mo == 'open':
        s.flat(s.E(mx + 6, my + 1, 6, 3), P['mouth'])
        s.flat(s.E(mx + 7, my + 2.5, 3.5, 1.3), P['tongue'][1])
        s.dots([(mx + 2, my - 1), (mx + 4, my - 2), (mx + 8, my - 2), (mx + 10, my - 1)], P['teeth'])
    else:
        s.flat(s.C(mx + 2, my + 1, mx + 11, my, 0.5), P['mouth'])
    # Strohkrone (geflochten) mit Zacken
    cy_ = hcy - 8
    band = s.E(hcx, cy_ + 1.5, 10.5, 3.2) & ~s.E(hcx, cy_ + 5.2, 10, 3.2)
    spikes = np.zeros_like(band)
    for i, dxs in enumerate((-8, -4, 0, 4, 8)):
        x = hcx + dxs
        top = cy_ - 5.0 - (1.5 if i % 2 == 0 else 0)
        spikes |= s.P([(x - 2.0, cy_ + 1), (x, top), (x + 2.0, cy_ + 1)])
    crown = band | spikes
    s.part(crown, P['straw'], sep=True, light=(hcx - 4, cy_ - 2, 10, 5), bias=0.3)
    # Flechtmuster: schraege dunkle Striche im Band
    braid = band & (((s.X.astype(int) + s.Y.astype(int)) % 3) == 0)
    s.tint(braid, P['straw'], shift=-1)
    # Kerze auf dem Kopf, tropfend
    cwx, cwy = int(hcx - 2), int(cy_ - 7) + pose.get('cdy', 0)
    candle(s, cwx, cwy, 5, 7, fr, big_flame=pose.get('big', False), drips=((0, 4), (2, 1), (4, 3)),
           lit=pose.get('lit', True))
    for (x, y) in pose.get('drops', []):
        # heisser Wachstropfen: Tropfenform mit glaenzender Spitze
        s.part(s.pts([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1), (x, y - 1)]), P['wax'], bias=0.5, rim=False)
        s.flat(s.pts([(x, y)]), P['wax'][3])
        s.flat(s.pts([(x + 1, y + 1)]), P['flame'][1])
    for (x, y, st) in pose.get('sparks', []):
        glow(s, [(int(x), int(y))], st)
    # Mistgabel vorne + naher Arm
    if not behind and fang is not None:
        pitchfork(fork_flash).draw(s, gx + 0.5, gyy + 0.5, fang)
    for (x, y) in pose.get('glint', []):
        glow(s, [(x, y)], 2)
        s.dots([(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)], '#fff2c0')
    s.part(s.C(22 + bx, 35 + by, gx + 1, gyy, 3.0, 2.4), sk, sep=True, light=(gx, gyy - 3, 4, 4), bias=0.2)
    s.part(s.E(gx + 1, gyy + 0.5, 2.7, 2.4), sk, sep=True, bias=0.3)
    return s


def _knarz_frames():
    W, H = 56, 56
    fr = []
    for i in range(4):
        b = 1 if i in (1, 2) else 0
        fr.append(knarz(dict(fr=i, breath=b, hy=b, hand=(-1, -6 + b), ear=1 if i == 2 else 0, fork=93)).render())
    # attack: Mistgabelstoss nach links
    atk = [
        dict(fr=0, hand=(28, 0), fork=178, bx=2, hx=1, eyes='open', mouth='grin', far_hand=(1, 0)),
        dict(fr=1, hand=(14, -3), fork=180, bx=-2, hx=-2, eyes='open', mouth='open'),
        dict(fr=2, hand=(15, -2), fork=186, bx=-2, hx=-2, hy=1, mouth='open'),
        dict(fr=3, hand=(0, -4), fork=105),
    ]
    for p in atk:
        fr.append(knarz(p).render())
    # cast: Mistgabel weit zurueckgezogen, Zinken blitzen
    for i in range(4):
        hand = (28, -(i % 2))
        glint = [(21 + (i % 2) * 2, 37 + i % 3 - (i % 2))] if i in (1, 3) else [(24, 41)] if i == 2 else []
        fr.append(knarz(dict(fr=i, hand=hand, fork=178, bx=3, hx=2, hy=-(i % 2), mouth='grin',
                             fork_flash=i in (1, 3), glint=glint)).render())
    # cast2: Kerzenwachsregen - Kerze lodert, Wachstropfen spritzen
    drops_seq = [
        [(21, 7), (32, 6)],
        [(17, 4), (37, 3), (25, 2)],
        [(13, 3), (41, 2), (20, 9), (34, 8)],
        [(9, 7), (45, 6), (16, 3), (39, 2)],
    ]
    for i in range(4):
        sp = [(21 + i, 5 - i // 2, 2), (33 - i, 4, 1)] if i % 2 else [(24, 3, 1), (31, 6 - i, 2)]
        fr.append(knarz(dict(fr=i, big=True, cdy=-1 - (i % 2), hy=-1 + (i % 2), mouth='open', eyes='open',
                             drops=drops_seq[i], sparks=sp, far_hand=(0, -6 + (i % 2)), fork=93,
                             hand=(-1, -6))).render())
    fr.append(shift(knarz(dict(fr=1, hx=2, hy=-1, eyes='shut', mouth='ouch', ear=1, fork=100, hand=(0, -6))).render(flash=0.55), 2, 0))
    fr.append(shift(knarz(dict(fr=2, hx=1, eyes='shut', mouth='ouch', fork=96, hand=(0, -5))).render(), 1, 0))
    fr.append(_knarz_dead())
    anims = {
        'idle': {'start': 0, 'count': 4, 'fps': 4, 'loop': True},
        'attack': {'start': 4, 'count': 4, 'fps': 9, 'loop': False},
        'cast': {'start': 8, 'count': 4, 'fps': 8, 'loop': True},
        'cast2': {'start': 12, 'count': 4, 'fps': 8, 'loop': True},
        'hit': {'start': 16, 'count': 2, 'fps': 10, 'loop': False},
        'dead': {'start': 18, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr, anims


def _knarz_dead():
    W, H = 56, 56
    body = knarz(dict(size=(80, 80), off=(12, 12), eyes='x', mouth='open', fork=None, lit=False)).render(rot=-1)
    ys, xs = np.where(body.a[:, :, 3] > 0)
    fig = body.crop(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    out = Canvas(W, H)
    s = Spr(W, H)
    pitchfork().draw(s, 30.5, H - 3.5, 178)
    out.paste(s.render(), 0, 0)
    out.paste(fig, (W - fig.w) // 2, H - fig.h)
    return out


# ================================================================ Trainingspuppe
def dummy(ang=0.0, flash=0.0) -> Canvas:
    """Strohpuppe auf Holzpfahl, Sackleinenkopf, Zielscheibe auf der Brust. ang: Neigung (Grad, + = nach rechts)."""
    W, H = 28, 36
    s = Spr(W, H)
    px_, py_ = 14.0, H - 1.5                # Drehpunkt im Boden
    a = math.radians(ang)

    def T(x, y):
        dx, dy = x - px_, y - py_
        return px_ + dx * math.cos(a) - dy * math.sin(a), py_ + dx * math.sin(a) + dy * math.cos(a)

    straw, wood, burlap = P['straw'], P['wood'], P['burlap']
    # Pfahl (steckt im Boden)
    b0, b1 = T(14, H - 2.5), T(14, 12)
    s.part(s.C(b0[0], b0[1], b1[0], b1[1], 1.4), wood, light=(12.5, 22, 2, 12))
    s.part(s.R(10, H - 3, 18, H - 2) & s.E(14, H - 2.5, 4.5, 1.5), ['#3a3a26', '#5a5a34', '#7a7a44'])   # Erdhuegel
    # Querholz mit Strohaermen
    l0, l1 = T(5, 17), T(23, 17)
    s.part(s.C(l0[0], l0[1], l1[0], l1[1], 1.0), wood)
    for (x, y, d) in ((6, 17, -1), (22, 17, 1)):
        c_ = T(x, y)
        arm_m = s.E(c_[0], c_[1], 3.2, 2.2)
        for k in range(3):            # Strohbueschel am Ende
            e = T(x + d * 3.0, y - 1.5 + k * 1.5)
            arm_m |= s.C(c_[0], c_[1], e[0], e[1], 0.5)
        s.part(arm_m, straw, bias=0.2)
        r0, r1 = T(x - d * 1.2, y - 2.4), T(x - d * 1.2, y + 2.4)
        s.flat(s.C(r0[0], r0[1], r1[0], r1[1], 0.45), P['rope'][1])
    # Strohkoerper
    bc = T(14, 21)
    torso = s.E(bc[0], bc[1], 6.0, 6.6)
    for k in range(5):                # Strohhalme unten
        e0, e1 = T(10.5 + k * 1.8, 25), T(10 + k * 2.0, 29.5 - (k % 2))
        torso |= s.C(e0[0], e0[1], e1[0], e1[1], 0.55)
    s.part(torso, straw, light=(bc[0] - 1.5, bc[1] - 2, 6.5, 8), bias=0.2)
    halme = torso & (((s.X - s.Y * 0.35).astype(int)) % 3 == 0) & (s.Y > bc[1] + 3)
    s.tint(halme, straw, shift=-1)
    w0, w1 = T(8.5, 26), T(19.5, 26)
    s.part(s.C(w0[0], w0[1], w1[0], w1[1], 0.6), P['rope'])          # Strick an der Huefte
    # Zielscheibe (rot/weiss)
    tc = T(13, 20)
    for r, ramp in ((4.3, P['target_r']), (3.1, P['target_w']), (1.9, P['target_r']), (0.8, P['target_w'])):
        s.part(s.E(tc[0], tc[1], r, r), ramp, light=(tc[0] - 1, tc[1] - 1, 4, 4), bias=0.2, sep=(r > 4))
    # Sackleinenkopf
    hc = T(13.5, 8.5)
    head = s.E(hc[0], hc[1], 6.0, 5.6)
    s.part(head, burlap, sep=True, light=(hc[0] - 1.5, hc[1] - 2, 6, 5.6), bias=0.2)
    seam = head & (np.abs(s.X - hc[0] - 3.2) < 0.5)        # Naht des Sacks
    s.tint(seam, burlap, shift=-1)
    # Strohbueschel oben aus dem Sack
    for k, (dx, dy) in enumerate(((-2.5, -4), (-0.5, -5.2), (1.5, -4.6), (3.2, -3.2))):
        e0, e1 = T(13.5 + dx * 0.6, 4.5), T(13.5 + dx, 8.5 + dy - 1.8)
        s.part(s.C(e0[0], e0[1], e1[0], e1[1], 0.5), straw, bias=0.4)
    # Hals zugebunden
    n0, n1 = T(10.5, 14), T(16.5, 14)
    s.part(s.C(n0[0], n0[1], n1[0], n1[1], 0.7), P['rope'])
    # aufgenaehtes Gesicht (nach links versetzt): Kreuzstich-Augen, Nahtmund
    stitch = mix(burlap[0], OUTLINE, 0.75)
    for (ex, ey) in ((10.5, 8.0), (14.5, 8.0)):
        pts = [T(ex - 1, ey - 1), T(ex + 1, ey - 1), T(ex, ey), T(ex - 1, ey + 1), T(ex + 1, ey + 1)]
        s.dots(pts, stitch)
    m = [T(9.5 + k, 11.5 + (0 if k % 2 else 0.6)) for k in range(6)]
    s.dots(m, stitch)
    return s.render(flash=flash)


def _dummy_frames():
    W, H = 28, 36
    fr = [dummy(0), dummy(-3)]
    fr += [dummy(9, flash=0.55), dummy(-6), dummy(3)]
    fr.append(dummy(0))
    anims = {
        'idle': {'start': 0, 'count': 2, 'fps': 2, 'loop': True},
        'hit': {'start': 2, 'count': 3, 'fps': 10, 'loop': False},
        'dead': {'start': 0, 'count': 1, 'fps': 1, 'loop': False},
    }
    return (W, H), fr[:5], anims


# ================================================================ Sheets / Export
def _sheet(frames, W, H) -> Canvas:
    cv = Canvas(W * len(frames), H)
    for i, f in enumerate(frames):
        assert (f.w, f.h) == (W, H), (f.w, f.h, W, H)
        cv.paste(f, i * W, 0)
    return cv


def all_enemies():
    out = {}
    out['wolf_young'] = _wolf_frames(False)
    out['wolf_grey'] = _wolf_frames(True)
    out['boar_piglet'] = _piglet_frames()
    out['boar_elite'] = _boar_frames()
    out['kobold_digger'] = _kobold_digger_frames()
    out['kobold_firestarter'] = _kobold_firestarter_frames()
    out['thief'] = _bandit_frames(False)
    out['thief_captain'] = _bandit_frames(True)
    out['boss_knarz'] = _knarz_frames()
    out['training_dummy'] = _dummy_frames()
    for eid, ((W, H), frames, anims) in out.items():
        out[eid] = ((W, H), _ground(frames, H, anims['dead']['start']), anims)
    return out


def _bottom(cv: Canvas):
    rows = np.where((cv.a[:, :, 3] > 0).any(axis=1))[0]
    return int(rows.max()) if len(rows) else cv.h - 1


def _ground(frames, H, dead_i):
    """Standflaeche auf die unterste Zeile setzen: alle Frames gleich verschieben (Idle 0 als Mass)."""
    dy = (H - 1) - _bottom(frames[0])
    res = []
    for i, f in enumerate(frames):
        if i == dead_i and i != 0:
            res.append(shift(f, 0, (H - 1) - _bottom(f)))
        else:
            res.append(shift(f, 0, dy) if dy else f)
    return res


def build(root):
    gfx = os.path.join(root, 'assets', 'gfx', 'enemies')
    os.makedirs(gfx, exist_ok=True)
    meta = {}
    sheets = {}
    for eid, ((W, H), frames, anims) in all_enemies().items():
        sh = _sheet(frames, W, H)
        sh.save(os.path.join(gfx, eid + '.png'))
        sheets[eid] = sh
        meta[eid] = {'frame_size': [W, H], 'anims': anims}
    os.makedirs(os.path.join(root, 'data'), exist_ok=True)
    with open(os.path.join(root, 'data', 'enemies_gfx.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return sheets, meta


def _preview(sheets, path, scale=4):
    from PIL import Image
    pad = 4
    w = max(s.w for s in sheets.values()) + pad * 2
    h = sum(s.h + pad for s in sheets.values()) + pad
    img = Image.new('RGBA', (w, h), (104, 118, 100, 255))
    y = pad
    for s in sheets.values():
        img.alpha_composite(s.image(), (pad, y))
        y += s.h + pad
    img = img.resize((w * scale, h * scale), Image.NEAREST)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def _lineup(sheets, meta, path, scale=4):
    """Spielerfigur links, Gegner (idle 0) rechts auf gemeinsamer Bodenlinie."""
    from PIL import Image
    import rig3 as RG
    import chars as CH
    L = RG.frames('orc', 'warrior', 0)[0]
    player = RG.preview_frame('orc', 'warrior', 0, CH.SKIN_PALETTES['orc'][1], CH.HAIR_PALETTES['orc'][1], L)
    L2 = RG.frames('human', 'priest', 0)[0]
    player2 = RG.preview_frame('human', 'priest', 0, CH.SKIN_PALETTES['human'][1], CH.HAIR_PALETTES['human'][1], L2)
    items = [player, player2]
    for eid, s in sheets.items():
        W, H = meta[eid]['frame_size']
        items.append(s.crop(0, 0, W, H))
    gap = 4
    w = sum(i.w for i in items) + gap * (len(items) + 1)
    base = max(i.h for i in items) + 6
    img = Image.new('RGBA', (w, base + 8), (104, 118, 100, 255))
    for x in range(w):
        for y in range(base, base + 8):
            img.putpixel((x, y), (84, 96, 70, 255))
    x = gap
    for it in items:
        img.alpha_composite(it.image(), (x, base - it.h))
        x += it.w + gap
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    img.save(path)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, '..', '..', 'healer-simulator'))
    sheets, meta = build(root)
    outdir = os.path.normpath(os.path.join(here, '..', '..', 'output', 'kampf'))
    _preview(sheets, os.path.join(outdir, 'enemies_preview.png'))
    _lineup(sheets, meta, os.path.join(outdir, 'enemies_lineup.png'))
    print('Gegner geschrieben:', ', '.join(sheets))
