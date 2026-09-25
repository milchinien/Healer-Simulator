"""Schlachtfeld-Hintergruende Welt 1 "Gruenhain" (640x360).

Seitenansicht wie in "Slay the Spire": Gruppe links, Gegner rechts, gemeinsame Fusslinie y = 226.
Zwischen x = 60 und x = 630 steht im Bereich y = 120..240 nichts Hohes im Vordergrund; alles
dahinter ist kleiner, ferner und im Kontrast/Saettigung zurueckgenommen.

Szenen:
  gruenhain_day  - Wellen 1-6: sonniger Tag, Huegel, rote Scheune, Zaun, Kornfelder, Kapelle
  gruenhain_dusk - Wellen 7-10: Daemmerung vor einer verlassenen Scheune mit Kerzenschein

Ausgabe:
  assets/gfx/battle/<name>.png          Hintergrund
  assets/gfx/battle/<name>_clouds.png   ziehende Wolkenebene (640 breit, in x nahtlos kachelbar)
  data/battle_bg.json                   Wolken-Parameter und Lichtpunkte je Szene

Gemalt wird ueber Masken (numpy) statt Pixel fuer Pixel: grosse, saubere Farbflaechen,
wenige bewusste Toene je Material, kein Rauschen.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

W, H = 640, 360
FOOT_Y = 226          # Fusslinie der Figuren
GROUND_TOP = 200      # Beginn der Standflaeche
PANEL_Y = 262         # ab hier liegt das untere UI-Panel
CLOUD_Y, CLOUD_H = 18, 66   # Band der ziehenden Wolkenebene (darin liegt kein Laub)


# ================================================================== Farbe
def rgb(col):
    if isinstance(col, str):
        h = col.lstrip('#')
        return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=float)
    return np.array(col[:3], dtype=float)


def hexc(v):
    v = np.clip(np.round(v), 0, 255).astype(int)
    return '#%02x%02x%02x' % tuple(v)


def mixc(a, b, t):
    return hexc(rgb(a) * (1 - t) + rgb(b) * t)


def ramp(a, b, n):
    """n Farbstufen von a nach b (inklusive)."""
    return [mixc(a, b, i / max(1, n - 1)) for i in range(n)]


# ================================================================== Maler
class Painter:
    """RGBA-Leinwand mit Masken-Werkzeugen."""

    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    # -- Masken
    def disc(self, cx, cy, r):
        return (self.xx - cx + 0.5) ** 2 + (self.yy - cy + 0.5) ** 2 <= r * r

    def ell(self, cx, cy, rx, ry):
        return ((self.xx - cx + 0.5) / rx) ** 2 + ((self.yy - cy + 0.5) / ry) ** 2 <= 1.0

    def box(self, x, y, w, h):
        m = np.zeros((self.h, self.w), bool)
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        if x1 > x0 and y1 > y0:
            m[y0:y1, x0:x1] = True
        return m

    def polym(self, pts):
        img = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(img).polygon([(float(x), float(y)) for x, y in pts], fill=255)
        return np.array(img) > 0

    def below(self, ys):
        """Maske aller Pixel unterhalb eines Profils (ys je x)."""
        return self.yy >= np.asarray(ys)[None, :]

    # -- Malen
    def fill(self, mask, col, alpha=1.0):
        if alpha >= 1.0:
            self.a[mask, :3] = rgb(col)
            self.a[mask, 3] = 255
        else:
            base = self.a[mask, :3].astype(float)
            self.a[mask, :3] = np.round(base * (1 - alpha) + rgb(col) * alpha)
            self.a[mask, 3] = np.maximum(self.a[mask, 3], int(255 * alpha))

    def tint(self, mask, col, t):
        """Vorhandene Farben Richtung col verschieben (Dunst, Schatten, Licht)."""
        base = self.a[mask, :3].astype(float)
        self.a[mask, :3] = np.round(base * (1 - t) + rgb(col) * t)

    def px(self, x, y, col):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x, :3] = rgb(col)
            self.a[y, x, 3] = 255

    def rect(self, x, y, w, h, col):
        self.fill(self.box(x, y, w, h), col)

    def hline(self, x0, x1, y, col):
        self.rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, col)

    def vline(self, x, y0, y1, col):
        self.rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, col)

    def line(self, x0, y0, x1, y1, col):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
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

    def poly(self, pts, col):
        self.fill(self.polym(pts), col)

    def image(self):
        return Image.fromarray(self.a, 'RGBA')

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.image().save(path)


# ================================================================== Gelaende
def profile(x0, x1, base, waves, seed=0):
    """Weiches Huegelprofil: base - Summe(amp * sin(x/len + phase)). Liefert float-Array ueber W."""
    r = np.random.default_rng(seed)
    xs = np.arange(W, dtype=float)
    ys = np.full(W, float(base))
    for (amp, length) in waves:
        ys -= amp * np.sin(xs / length + r.uniform(0, 6.28))
    return ys


def bump(ys, cx, half_w, height):
    """Rundliche Kuppe in ein Profil einarbeiten (cos^2-Form)."""
    xs = np.arange(W, dtype=float)
    t = np.clip((xs - cx) / half_w, -1, 1)
    return ys - height * np.cos(t * math.pi / 2) ** 2


def hill_layer(p, ys, body, lit, dark, rim=None, lit_w=5, shade_side=True, clip_bottom=None):
    """Huegel mit Lichtkante oben und Schattenhaengen: Licht kommt von links oben.
    Hang, der nach rechts abfaellt (ys steigt) -> beleuchtet; Hang, der ansteigt -> Schatten."""
    yi = np.round(ys).astype(int)
    m = p.below(yi)
    if clip_bottom is not None:
        m &= p.yy < clip_bottom
    p.fill(m, body)
    # Licht von links: ansteigende Haenge (ys faellt nach rechts) hell, abfallende im Schatten.
    k = 10
    ys_s = np.convolve(np.pad(ys, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), mode='valid')
    fall = ys_s - np.concatenate([np.full(k, ys_s[0]), ys_s[:-k]])      # >0: faellt nach rechts ab
    depth = p.yy - yi[None, :]
    if shade_side:
        sh = m & (depth < np.round(fall * 1.6)[None, :] - 1)
        p.fill(sh, dark)
    lt = m & (depth < np.maximum(lit_w * (fall < 1.5), np.round(-fall * 1.6))[None, :])
    p.fill(lt, lit)
    if rim is not None:
        p.fill(m & (depth == 0), rim)
    return yi


def mountains(p, peaks, base_y, pal, seed=0, snow_depth=0.22):
    """Ferne Bergkette: jeder Gipfel mit heller Westflanke, dunkler Ostflanke entlang eines
    gezackten Grats, Rinnen und gezackter Schneekappe. Hinten stehende Gipfel zuerst."""
    r = np.random.default_rng(seed)
    for (ax, ay, hw) in sorted(peaks, key=lambda q: q[1]):
        hgt = base_y - ay
        left = [(ax - hw, base_y)]
        # linke Flanke mit Schultern
        for t in (0.35, 0.62, 0.84):
            left.append((ax - hw * (1 - t) + r.uniform(-3, 3), base_y - hgt * t + r.uniform(-2, 2)))
        right = []
        for t in (0.84, 0.6, 0.3):
            right.append((ax + hw * (1 - t) + r.uniform(-3, 3), base_y - hgt * t + r.uniform(-2, 2)))
        right.append((ax + hw, base_y))
        outline = left + [(ax, ay)] + right
        p.poly(outline, pal['body'])
        # Grat: vom Gipfel schraeg nach rechts unten, gezackt
        ridge = [(ax, ay)]
        for k in range(1, 6):
            t = k / 5
            ridge.append((ax + hw * 0.28 * t + (2 if k % 2 else -1), ay + hgt * t))
        shadow = ridge + [(ax + hw, base_y)] + right[::-1][1:] + [(ax, ay)]
        p.fill(p.polym(shadow) & p.polym(outline), pal['dark'])
        # beleuchtete Westflanke (oberes Stueck heller)
        litp = [(ax, ay)] + [(x - 1, y) for (x, y) in ridge[1:4]] + [(ax - hw * 0.45, ay + hgt * 0.62)]
        p.fill(p.polym(litp) & p.polym(outline), pal['lit'])
        # Rinnen im Schatten
        for k in range(2):
            x0 = ax + hw * (0.3 + 0.2 * k)
            y0 = ay + hgt * (0.3 + 0.15 * k)
            p.line(x0, y0, x0 + hw * 0.12, y0 + hgt * 0.3, mixc(pal['dark'], pal['body'], 0.5))
        # Schneekappe
        sd = hgt * snow_depth
        cap = [(ax, ay)]
        n = 7
        for k in range(n + 1):
            t = k / n
            xl = ax - hw * 0.62 * snow_depth * 1.6 + t * hw * 0.62 * snow_depth * 3.2
            yb = ay + sd * (0.55 + 0.45 * math.sin(t * math.pi)) + (3 if k % 2 else -1)
            cap.append((xl, yb))
        cap_m = p.polym([(ax, ay)] + cap[1:]) & p.polym(outline)
        p.fill(cap_m, pal['snow'])
        p.fill(cap_m & p.polym(shadow), pal['snow_d'])


# ================================================================== Himmel
def sky_bands(p, y0, y1, cols, jitter=None):
    """Himmel in ruhigen, flachen Baendern (kein Dithering). cols = Farben von oben nach unten.
    jitter: optional sanfte Wellung der Bandgrenzen (amp, laenge) fuer lebendigere Uebergaenge."""
    n = len(cols)
    hgt = (y1 - y0) / n
    xs = np.arange(W)
    for i, col in enumerate(cols):
        top = y0 + i * hgt
        bot = y0 + (i + 1) * hgt
        if jitter and i > 0:
            amp, ln = jitter
            off = np.round(amp * np.sin(xs / ln + i * 1.7) + amp * 0.5 * np.sin(xs / (ln * 0.37) + i)).astype(int)
        else:
            off = np.zeros(W, int)
        m = (p.yy >= (np.round(top) + off)[None, :]) & (p.yy < y1)
        p.fill(m, col)


def cumulus(p, puffs, base_y, tones, wrap=False, from_below=False):
    """Skulptierte Kumuluswolke aus Kugel-Puffs. tones = (licht, mittel, schatten, boden).
    Jeder Puff hat eigene Lichtkappe oben links; untere Puffs ueberdecken obere; flacher Boden.
    wrap: in x um die Leinwandbreite wiederholen (kachelbare Ebene)."""
    cols = list(tones)
    shifts = (-p.w, 0, p.w) if wrap else (0,)
    order = sorted(puffs, key=lambda q: (q[1], -q[2]))
    cut = p.yy <= base_y
    top = min(q[1] - q[2] for q in puffs)
    hc = max(4.0, base_y - top)
    # Grundton nach Hoehe in der Wolke: oben Licht, Mitte Mittelton, unten Schatten
    band = np.where(p.yy < base_y - hc * 0.42, 0, np.where(p.yy < base_y - hc * 0.16, 1, 2))
    if from_below:
        # Abendwolke: von unten/links angestrahlt -> unten hell, oben dunkel
        band = np.where(p.yy >= base_y - hc * 0.2, 0, np.where(p.yy >= base_y - hc * 0.55, 1, 2))
    tone = np.full((p.h, p.w), -1)
    for (cx, cy, r) in order:
        for s in shifts:
            x = cx + s
            if x + r < -2 or x - r > p.w + 2:
                continue
            d = p.disc(x, cy, r) & cut
            if from_below:
                tone[d] = band[d]
                if r > hc * 0.3:
                    cres = d & ~p.disc(x - r * 0.25, cy + r * 0.3, r * 1.02) & (band >= 1)   # Sichel oben rechts
                    tone[cres] = np.minimum(band[cres] + 1, 2)
                continue
            # jeder Puff: eigener heller Kopf, Sichel unten rechts eine Stufe dunkler
            own = np.where(p.yy < cy - r * 0.1, np.minimum(band, 0 if r > hc * 0.25 else 1), band)
            tone[d] = own[d]
            cres = d & ~p.disc(x - r * 0.2, cy - r * 0.3, r * 1.02)
            tone[cres] = np.minimum(own[cres] + 1, 2)
    tone[(tone >= 0) & (p.yy >= base_y)] = 0 if from_below else 3
    for i, col in enumerate(cols):
        p.fill(tone == i, col)
    return tone >= 0


def cloud_puffs(cx, base, width, height, seed=0):
    """Puff-Liste fuer eine Kumuluswolke: grosse Kuppeln oben, kleinere Polster am Boden."""
    r = np.random.default_rng(seed)
    puffs = []
    n_top = max(2, int(round(width / (height * 0.75))))
    for i in range(n_top):
        t = (i + 0.5) / n_top
        x = cx - width * 0.42 + t * width * 0.84 + r.uniform(-2, 2)
        hump = math.sin(t * math.pi) ** 0.7
        rr = height * (0.3 + 0.32 * hump) * r.uniform(0.9, 1.1)
        puffs.append((x, base - rr * 0.35 - hump * height * 0.32, rr))
    n_low = max(3, int(round(width / (height * 0.45))))
    for i in range(n_low):
        t = i / (n_low - 1)
        x = cx - width * 0.42 + t * width * 0.84 + r.uniform(-1.5, 1.5)
        rr = height * r.uniform(0.2, 0.28) * (0.75 + 0.25 * math.sin(t * math.pi))
        puffs.append((x, base - rr * 0.5, rr))
    return puffs


def fields(p, ys, specs, hedge=None):
    """Feld-Flickenteppich auf einem Huegel. specs: (x0, x1, tiefe_oben, tiefe_unten, (grund, furche, licht)).
    Die Furchen laufen parallel zur Huegelkante; die Oberkante jedes Felds bekommt eine Lichtlinie."""
    xs = np.arange(W)
    ysr = np.round(ys).astype(int)
    for (x0, x1, d0, d1, (base, furrow, light)) in specs:
        top = ysr + d0
        bot = ysr + d1
        m = (p.xx >= x0) & (p.xx < x1) & (p.yy >= top[None, :]) & (p.yy < bot[None, :])
        # Feldkanten leicht schraeg (perspektivisch)
        m &= (p.xx >= x0 + (p.yy - top[None, :]) // 3)
        p.fill(m, base)
        rel = p.yy - top[None, :]
        p.fill(m & (rel % 3 == 2), furrow)
        p.fill(m & (rel == 0), light)
        if hedge is not None:
            # Hecke an der Unterkante
            hm = (p.xx >= x0) & (p.xx < x1) & (p.yy == bot[None, :])
            p.fill(hm, hedge[0])
            for x in range(max(0, x0), min(W, x1), 3):
                p.px(x, bot[x] - 1, hedge[0])
                p.px(x + 1, bot[x] - 1, hedge[1])


# ================================================================== Pflanzen
def leaf_tree(p, x, base, h, leaves, trunk, seed=0, spread=1.0, lean=0.0, clumps=None):
    """Laubbaum mit Stamm, zwei Aesten und geformten Blattklumpen.
    leaves = (tief, schatten, mittel, licht), trunk = (dunkel, mittel, licht)."""
    r = np.random.default_rng(seed)
    t_dark, t_mid, t_lit = trunk
    tw = max(2, int(h * 0.075))
    crown_y = base - h * 0.5
    # Stamm leicht verjuengt, Wurzelansatz
    top_x = x + lean * h * 0.3
    for yy in range(int(crown_y) - 4, int(base)):
        t = (yy - crown_y) / (base - crown_y)
        cx = top_x + (x - top_x) * t
        half = tw * (0.6 + 0.4 * t) + (2.5 * max(0, t - 0.82) / 0.18)
        p.rect(round(cx - half), yy, round(2 * half), 1, t_mid)
        p.px(round(cx + half) - 1, yy, t_dark)
        p.px(round(cx + half) - 2, yy, t_dark)
        p.px(round(cx - half), yy, t_lit)
    # Aeste
    for sgn in (-1, 1):
        ax0, ay0 = top_x, crown_y + h * 0.08
        ax1, ay1 = top_x + sgn * h * 0.22 * spread, crown_y - h * 0.12
        for k in range(max(1, tw - 1)):
            p.line(ax0 + k - tw // 2, ay0, ax1 + k * 0.5, ay1, t_mid if sgn < 0 else t_dark)
    # Krone aus Klumpen
    cw = h * 0.36 * spread
    ch = h * 0.34
    ccx, ccy = top_x, base - h + ch
    if clumps is None:
        clumps = []
        n = 7 + int(h / 30)
        for i in range(n):
            a = r.uniform(0, 2 * math.pi)
            d = r.uniform(0.2, 0.75)
            clumps.append((ccx + math.cos(a) * cw * d, ccy + math.sin(a) * ch * d * 0.9,
                           h * r.uniform(0.13, 0.19) * (0.9 + 0.2 * spread)))
        clumps.append((ccx, ccy - ch * 0.35, h * 0.2))
    leaf_clumps(p, clumps, leaves, seed=seed)


def leaf_clumps(p, clumps, leaves, seed=0, outline=True):
    """Blattklumpen: jeder Klumpen hat einen gezackten Rand aus kleinen Blattbuescheln,
    Schattenseite unten rechts, Lichtkappe oben links. Obere Klumpen zuerst."""
    r = np.random.default_rng(seed + 7)
    order = sorted(clumps, key=lambda q: q[1])
    tone = np.full((p.h, p.w), -1)       # 0 tief, 1 schatten, 2 mittel, 3 licht
    lx, ly = -0.62, -0.78                # Lichtrichtung (links oben)
    for (cx, cy, rr) in order:
        # Klumpen = viele kleine Blattbuescheln auf einem versetzten Raster
        s = float(np.clip(rr * 0.34, 2.6, 6.5))
        br = s * 0.78
        blobs = []
        gy = cy - rr
        row = 0
        while gy <= cy + rr:
            gx = cx - rr + (s / 2 if row % 2 else 0)
            while gx <= cx + rr:
                jx, jy = gx + r.uniform(-0.35, 0.35) * s, gy + r.uniform(-0.35, 0.35) * s
                d = math.hypot((jx - cx) / rr, (jy - cy) / (rr * 0.92))
                if d <= 1.0:
                    blobs.append((jx, jy, d))
                gx += s
            gy += s * 0.82
            row += 1
        # im Klumpen-Hintergrund Luecken vermeiden
        _stamp(tone, cx, cy, rr * 0.9, 1)
        for (bx, by, d) in sorted(blobs, key=lambda q: q[1]):
            nx, ny = (bx - cx) / rr, (by - cy) / rr
            lum = (nx * lx + ny * ly) + 0.25 * (1 - d)
            lv = 3 if lum > 0.42 else 2 if lum > -0.05 else 1 if lum > -0.5 else 0
            _stamp(tone, bx, by, br, lv)
            if lv > 0:
                _stamp_crescent(tone, bx, by, br, lv - 1)
    for i, col in enumerate(leaves):
        p.fill(tone == i, col)
    return tone >= 0


def _stamp(tone, cx, cy, r, val):
    h, w = tone.shape
    x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
    y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    m = (xx - cx + 0.5) ** 2 + (yy - cy + 0.5) ** 2 <= r * r
    tone[y0:y1, x0:x1][m] = val


def _stamp_crescent(tone, cx, cy, r, val):
    """Sichel unten rechts eines Buescheln (nur innerhalb des Buescheln)."""
    h, w = tone.shape
    x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
    y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    m = (xx - cx + 0.5) ** 2 + (yy - cy + 0.5) ** 2 <= r * r
    m &= (xx - cx + 0.5 + r * 0.35) ** 2 + (yy - cy + 0.5 + r * 0.45) ** 2 > (r * 1.0) ** 2
    tone[y0:y1, x0:x1][m] = val


def serrate(tone, levels, period=4):
    """Blattzaehne: an Grenzen zwischen zwei Tonstufen ragt die hellere Stufe in kleinen Zacken
    nach unten in die dunklere (regelmaessig versetzt, kein Rauschen)."""
    h, w = tone.shape
    yy, xx = np.mgrid[0:h, 0:w]
    for lv in levels:
        cur = tone == lv
        below = np.zeros_like(cur)
        below[:-1] = (tone[1:] == lv - 1)
        pick = cur & below & (((xx * 3 + yy * 2) % period) == 0)
        ys, xs = np.nonzero(pick)
        for (y, x) in zip(ys, xs):
            for (dx, dy) in ((0, 1), (1, 1), (0, 2)):
                if y + dy < h and x + dx < w and tone[y + dy, x + dx] == lv - 1:
                    tone[y + dy, x + dx] = lv


def pine_row(p, x0, x1, base_ys, hmin, hmax, tones, seed=0, step=(5, 9)):
    """Reihe ferner Nadelbaeume (Silhouetten mit Lichtseite links). base_ys: Profil fuer den Fuss."""
    dark, mid, light = tones
    r = np.random.default_rng(seed)
    x = x0
    while x < x1:
        hgt = r.uniform(hmin, hmax)
        b = base_ys[int(np.clip(x, 0, W - 1))] + r.uniform(0, 3)
        hw = hgt * 0.3
        p.poly([(x - hw, b), (x + hw, b), (x, b - hgt)], mid)
        p.poly([(x, b - hgt), (x + hw, b), (x + 1, b)], dark)
        p.line(x, b - hgt, x - hw * 0.6, b - hgt * 0.35, light)
        for k in (0.45, 0.72):   # Astetagen
            yy = b - hgt * (1 - k)
            ww = hw * k
            p.line(x - ww - 1, yy, x - ww * 0.3, yy - 1, dark)
        x += r.uniform(*step)


def grass_tufts(p, region, count, cols, seed=0, hmax=3, cluster=3):
    """Grasbueschel in kleinen Gruppen (keine Zufallspixel)."""
    x0, y0, x1, y1 = region
    r = np.random.default_rng(seed)
    for _ in range(count):
        cx, cy = r.integers(x0, x1), r.integers(y0, y1)
        col = cols[r.integers(0, len(cols))]
        for k in range(r.integers(1, cluster + 1)):
            x = cx + k * 2 - cluster
            hgt = int(r.integers(1, hmax + 1))
            p.vline(x, cy - hgt, cy, col)
            p.px(x - 1, cy - hgt + 1, col)


def flower_clump(p, x, y, cols, leaf, n=5, seed=0):
    r = np.random.default_rng(seed)
    col = cols[seed % len(cols)]
    for k in range(n):
        fx = x + int(r.integers(-5, 6))
        fy = y + int(r.integers(-1, 2))
        p.vline(fx, fy + 1, fy + 2, leaf)
        p.px(fx, fy, col)
        if k % 2 == 0:
            p.px(fx + 1, fy, col)


# ================================================================== Bauten
def fence(p, x0, x1, y_at, post_h, wood, step=14, broken=()):
    """Holzzaun mit Pfosten und zwei Latten. y_at(x) -> Fussy; wood = (dunkel, mittel, licht)."""
    dark, mid, light = wood
    posts = list(range(int(x0), int(x1) + 1, step))
    for i, px_ in enumerate(posts):
        b = int(round(y_at(px_)))
        p.rect(px_, b - post_h, 2, post_h, mid)
        p.vline(px_ + 1, b - post_h + 1, b - 1, dark)
        p.px(px_, b - post_h, light)
        if i + 1 < len(posts) and i not in broken:
            nx = posts[i + 1]
            nb = int(round(y_at(nx)))
            for frac in (0.3, 0.68):
                ya = b - post_h * (1 - frac)
                yb = nb - post_h * (1 - frac)
                p.line(px_ + 2, ya, nx - 1, yb, mid)
                p.line(px_ + 2, ya + 1, nx - 1, yb + 1, dark)
                p.line(px_ + 2, ya - 1, nx - 1, yb - 1, light)


def farmhouse(p, x, base, w, h, pal, lit=(), lights=None):
    """Kleines fernes Fachwerkhaus (Giebel seitlich). lit: Indizes der erleuchteten Fenster."""
    wall, wall_d, timber, roof, roof_d, win = (pal[k] for k in ('wall', 'wall_d', 'timber', 'roof', 'roof_d', 'win'))
    top = base - h
    p.rect(x, top, w, h, wall)
    p.rect(x + w - 2, top, 2, h, wall_d)
    p.hline(x, x + w - 1, top, timber)
    p.hline(x, x + w - 1, top + h // 2, timber)
    for k in range(0, w, 6):
        p.vline(x + k, top, base - 1, timber)
    p.vline(x + w - 1, top, base - 1, timber)
    rh = int(w * 0.42)
    p.poly([(x - 3, top + 1), (x + w + 2, top + 1), (x + w - 4, top - rh), (x + 3, top - rh)], roof)
    p.poly([(x + w // 2, top - rh), (x + w - 4, top - rh), (x + w + 2, top + 1), (x + w // 2, top + 1)], roof_d)
    p.hline(x + 3, x + w - 4, top - rh, mixc(roof, '#ffffff', 0.15))
    p.rect(x + w - 8, top - rh - 4, 3, 5, timber)
    for i, k in enumerate(range(2, w - 3, 6)):
        on = i in lit
        p.rect(x + k + 1, top + 2, 3, 3, win if on else timber)
        if on and lights is not None:
            lights.append((x + k + 2, top + 3, 6, CANDLE))
    p.rect(x + 2, base - 5, 3, 5, timber)


def windmill_blades(p, hub, length, angle, tones, width=4):
    """Vier Muehlenfluegel: Segeltuch als flache Flaeche, Holm dunkel, Nabe."""
    cloth, cloth_d, spar = tones
    for k in range(4):
        a = angle + k * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa * width, ca * width
        p0 = (hub[0] + ca * 4, hub[1] + sa * 4)
        p1 = (hub[0] + ca * length, hub[1] + sa * length)
        p.poly([p0, p1, (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)], cloth)
        p.line(p0[0] + nx, p0[1] + ny, p1[0] + nx, p1[1] + ny, cloth_d)
        p.line(hub[0], hub[1], p1[0], p1[1], spar)
    p.fill(p.disc(hub[0] + 0.5, hub[1] + 0.5, 1.6), spar)


def haystack(p, x, base, w, h, tones):
    dark, mid, light = tones
    p.fill(p.ell(x, base, w / 2, h) & (p.yy < base), mid)
    p.fill(p.ell(x + w * 0.1, base, w / 2 * 0.8, h * 0.9) & (p.yy < base) & (p.xx > x), dark)
    p.fill(p.ell(x - w * 0.15, base - h * 0.45, w * 0.22, h * 0.35), light)
    p.hline(x - w / 2 + 1, x + w / 2 - 1, base, dark)


def chapel(p, x, base, s, pal):
    """Kleine weisse Dorfkapelle mit Glockenturm (Blick von vorn-links, Licht von links).
    s = Skalierung, x = linke Kante des Kirchenschiffs."""
    wall, wall_d, roof, roof_d, roof_l, dark, gold = (pal[k] for k in
                                                      ('wall', 'wall_d', 'roof', 'roof_d', 'roof_l', 'dark', 'gold'))
    nw, nh = int(30 * s), int(14 * s)       # Schiff
    tx, tw, th = x - int(9 * s), int(11 * s), int(26 * s)   # Turm vorn links
    # Schiff (Seitenansicht)
    p.rect(x, base - nh, nw, nh, wall)
    p.rect(x, base - 2, nw, 2, wall_d)
    p.poly([(x - 1, base - nh), (x + nw + 1, base - nh), (x + nw - 3 * s, base - nh - 9 * s),
            (x + 3 * s, base - nh - 9 * s)], roof)
    p.poly([(x + 3 * s, base - nh - 9 * s), (x + nw - 3 * s, base - nh - 9 * s), (x + nw - 4 * s, base - nh - 8 * s),
            (x + 4 * s, base - nh - 8 * s)], roof_l)
    p.hline(x - 1, x + nw + 1, base - nh, roof_d)
    for k in range(3):   # Rundbogenfenster
        wx = x + int((8 + k * 8) * s)
        p.rect(wx, base - nh + 3 * s, max(2, int(2 * s)), 5 * s, dark)
        p.px(wx, base - nh + 3 * s - 1, wall_d)
    # Chor (Apsis) rechts
    p.fill(p.ell(x + nw, base - nh * 0.5, 4 * s, nh * 0.5) & (p.xx >= x + nw) & (p.yy < base), wall_d)
    # Turm
    p.rect(tx, base - th, tw, th, wall)
    p.rect(tx + tw - int(3 * s), base - th, int(3 * s), th, wall_d)
    p.poly([(tx - 1, base - th), (tx + tw, base - th), (tx + tw / 2 - 0.5, base - th - 14 * s)], roof)
    p.poly([(tx + tw / 2 - 0.5, base - th - 14 * s), (tx + tw, base - th), (tx + tw / 2, base - th)], roof_d)
    p.hline(tx - 1, tx + tw, base - th, roof_d)
    # Schallfenster, Uhr/Rosette, Tuer
    p.rect(tx + tw / 2 - 1.5, base - th + 3 * s, 3, 5 * s, dark)
    p.px(tx + tw / 2 - 0.5, base - th + 3 * s + 2, gold)
    p.fill(p.disc(tx + tw / 2 - 0.5, base - th * 0.52, 1.6 * s), dark)
    p.rect(tx + tw / 2 - 2, base - 7 * s, 4, 7 * s, dark)
    p.px(tx + tw / 2 - 2, base - 7 * s, wall)
    p.px(tx + tw / 2 + 1, base - 7 * s, wall)
    # Kreuz auf der Spitze
    cx, cy = tx + tw / 2 - 0.5, base - th - 14 * s
    p.vline(cx, cy - 5, cy - 1, gold)
    p.hline(cx - 1, cx + 1, cy - 4, gold)


# ================================================================== Szene: Tag
DAY = {
    'sky': ['#4d8bd8', '#5794dc', '#629ee1', '#6ea8e5', '#7ab2e8', '#87bbeb', '#94c4ed', '#a2cdef',
            '#b0d5f0', '#bedcf1', '#cbe3f2', '#d6e8f1'],
    'horizon': '#d6e8f1',
}


def haze_day(col, t):
    return mixc(col, DAY['horizon'], t)


def build_day():
    p = Painter()
    lights = []
    sky_bands(p, 0, 160, DAY['sky'])

    # -- ferne Wolkenbank am Horizont (statisch, tief, verblasst)
    cl = ('#f4f8fb', '#e2ecf4', '#c9d9e9', '#bccfe2')
    cumulus(p, cloud_puffs(80, 138, 84, 22, seed=1), 138, cl)
    cumulus(p, cloud_puffs(390, 134, 70, 20, seed=2), 134, cl)
    cumulus(p, cloud_puffs(585, 140, 60, 16, seed=3), 140, cl)

    # -- ferne Berge (Dunst)
    mountains(p, [(20, 128, 60), (120, 116, 70), (228, 132, 56), (318, 110, 80), (430, 126, 60), (520, 114, 70),
                  (626, 122, 64)], 168,
              {'lit': '#b9cce3', 'body': '#a5bad6', 'dark': '#93a9c9', 'snow': '#eef3fa', 'snow_d': '#cfdbeb'},
              seed=2)

    # -- ferner Waldsaum
    far_ys = profile(0, W, 156, [(4, 60), (2, 23)], seed=3)
    hill_layer(p, far_ys, '#8fb6a4', '#a2c4ae', '#83aa9c')
    pine_row(p, -4, W + 6, far_ys + 3, 9, 16, ('#6f9a90', '#80a99a', '#98bca8'), seed=4, step=(4, 7))
    # dahinter liegende Laubkuppen zwischen den Tannen
    for (bx, by, br) in [(28, 154, 9), (212, 153, 10), (230, 156, 8), (520, 152, 10), (540, 155, 8)]:
        leaf_clumps(p, [(bx, by, br)], ('#6f9a90', '#7ea696', '#8fb3a0', '#a2c2ac'), seed=bx)

    # -- mittlere Huegel mit Kapelle (links) und Feldern
    ys_a = profile(0, W, 172, [(4, 70), (2, 31)], seed=11)
    ys_a = bump(ys_a, 150, 110, 14)
    ys_a = bump(ys_a, 520, 150, 8)
    hill_layer(p, ys_a, '#86ba6c', '#9ccb7e', '#77ab62', lit_w=4)
    # Kornfelder als Streifen, die der Huegelform folgen
    wheat = ('#e7c25e', '#d4a847', '#f2d88c')
    green = ('#94c476', '#84b468', '#a6d086')
    fields(p, ys_a, [(222, 300, 3, 12, wheat), (300, 372, 3, 14, green), (372, 452, 3, 13, wheat),
                     (452, 540, 3, 11, green), (540, 640, 3, 12, wheat), (240, 350, 15, 30, wheat),
                     (350, 440, 16, 30, green), (440, 600, 14, 30, wheat), (-10, 60, 4, 16, wheat),
                     (200, 240, 12, 30, green)],
           hedge=('#5f955a', '#79ad68'))
    # Kapelle auf der Kuppe
    cb = int(round(ys_a[150])) + 3
    chapel(p, 142, cb, 1.0, {'wall': '#f2f0ea', 'wall_d': '#c9ccd4', 'roof': '#6c7ea0', 'roof_d': '#56678a',
                             'roof_l': '#8394b4', 'dark': '#5d6682', 'gold': '#e8c060'})
    leaf_clumps(p, [(118, cb - 6, 7), (126, cb - 4, 6), (186, cb - 5, 7), (196, cb - 3, 5)],
                ('#5f955a', '#6fa566', '#82b672', '#9ac883'), seed=5)

    # -- Windmuehle weit hinten links (Gruenhain-Wahrzeichen)
    mx, mb = 70, int(round(ys_a[70])) + 2
    p.poly([(mx - 6, mb), (mx + 6, mb), (mx + 4, mb - 26), (mx - 4, mb - 26)], '#e6e0d2')
    p.poly([(mx + 1, mb), (mx + 6, mb), (mx + 4, mb - 26), (mx + 1, mb - 26)], '#c8c2b6')
    p.poly([(mx - 6, mb - 26), (mx + 6, mb - 26), (mx, mb - 34)], '#a86a52')
    p.poly([(mx, mb - 34), (mx + 6, mb - 26), (mx + 1, mb - 26)], '#8a5646')
    p.rect(mx - 1, mb - 6, 3, 6, '#8a6a52')
    windmill_blades(p, (mx, mb - 27), 17, 0.35, ('#f2ede2', '#cfc6b6', '#7a5a48'))

    # -- nahe Huegelkante mit Scheune (rechts), Zaun, Heuhaufen
    ys_b = profile(0, W, 197, [(3, 80), (2, 29)], seed=21)
    ys_b = bump(ys_b, 350, 110, 7)
    ys_b = bump(ys_b, 40, 90, 8)
    hill_layer(p, ys_b, '#72ad58', '#88c066', '#65a04e', lit_w=4)
    barn_day(p, 316, int(round(ys_b[340])) + 3, lights)
    # Baeumchen neben der Scheune (hinter/neben, klein)
    leaf_tree(p, 420, int(ys_b[420]) + 3, 44, ('#3f7a44', '#4f8c4e', '#63a05a', '#7fb86a'),
              ('#4a3526', '#65483a', '#7e604a'), seed=31, spread=1.1)
    leaf_tree(p, 290, int(ys_b[290]) + 3, 34, ('#4a8448', '#5a9652', '#6eaa5e', '#88c070'),
              ('#4a3526', '#65483a', '#7e604a'), seed=32)
    for (hx, hw_, hh) in [(452, 12, 7), (468, 9, 5), (598, 11, 6)]:
        haystack(p, hx, int(ys_b[hx]) + 3, hw_, hh, ('#c09038', '#dcb04e', '#f0d080'))
    fence(p, 150, 276, lambda x: ys_b[int(x)] + 4, 8, ('#6a4a34', '#8a6446', '#a8805a'), step=12)
    fence(p, 482, 580, lambda x: ys_b[int(x)] + 4, 8, ('#6a4a34', '#8a6446', '#a8805a'), step=12)
    fence(p, 566, 640, lambda x: ys_b[min(W - 1, int(x))] + 4, 8, ('#6a4a34', '#8a6446', '#a8805a'), step=12)

    # -- Standflaeche (Wiese + Feldweg)
    ground(p, ys_b, DAY_GROUND, seed=5)

    # -- Rahmen: grosse Laubbaeume an den Raendern (Staemme ausserhalb der Figurenzone)
    edge_trees(p, ('#2a5634', '#3a6e40', '#548e4e', '#78b060', '#9ccc78'), ('#3c2a20', '#5a4032', '#7a5a44'))
    return p, lights


DAY_GROUND = {
    'meadow': ['#6aa852', '#64a04d', '#5d9848'],
    'meadow_lit': '#79b65c',
    'path': '#c8a672', 'path_d': '#b08e5e', 'path_l': '#dbbd8a', 'path_rut': '#a4845a',
    'front': ['#579244', '#4f883f', '#477d39', '#3f7134', '#36632e', '#2e562a'],
    'tuft': ['#529243', '#76b25a'],
    'tuft_front': ['#3e7634', '#5f9e4a'],
    'flowers': ['#ffffff', '#f6d860', '#f2a0c0'],
    'flower_count': 16,
    'pebble': '#9e8a6a',
}


def ground(p, ys_back, g, seed=0):
    """Ruhige Standflaeche: Wiese hinten, Feldweg mit Fahrspuren um die Fusslinie, dunklere Wiese
    vorn. Fusslinie FOOT_Y liegt mitten auf dem Weg."""
    r = np.random.default_rng(seed)
    xs = np.arange(W)
    top = np.round(ys_back).astype(int) + 4
    top = np.maximum(top, GROUND_TOP - 6)
    # Wiese hinten in flachen Baendern
    m = p.below(top)
    p.fill(m, g['meadow'][0])
    p.fill(m & (p.yy >= GROUND_TOP + 2), g['meadow'][1])
    p.fill(m & (p.yy >= GROUND_TOP + 8), g['meadow'][2])
    # Feldweg: sanft geschwungene Kanten
    path_top = FOOT_Y - 12 + np.round(1.5 * np.sin(xs / 47.0) + 1.0 * np.sin(xs / 13.0 + 1)).astype(int)
    path_bot = FOOT_Y + 11 + np.round(1.5 * np.sin(xs / 53.0 + 2) + 1.0 * np.sin(xs / 17.0)).astype(int)
    pm = (p.yy >= path_top[None, :]) & (p.yy <= path_bot[None, :])
    p.fill(pm, g['path'])
    p.fill(pm & (p.yy <= path_top[None, :] + 1), g['path_d'])          # Kante hinten (Grasschatten)
    p.fill(pm & (p.yy >= path_bot[None, :] - 1), g['path_l'])          # Kante vorn (Licht)
    # zwei Fahrspuren als ruhige Linien
    for off, col in ((-5, g['path_rut']), (-4, g['path_l']), (5, g['path_rut']), (6, g['path_l'])):
        yy = FOOT_Y + off + np.round(0.8 * np.sin(xs / 61.0 + off)).astype(int)
        seg = (np.sin(xs / 23.0 + off) > -0.6)
        for x in xs[seg]:
            p.px(x, yy[x], col)
    # vereinzelte Kiesel auf dem Weg
    for _ in range(40):
        x = int(r.integers(0, W))
        y = int(r.integers(path_top[x] + 3, path_bot[x] - 2))
        p.px(x, y, g['pebble'])
        p.px(x + 1, y, g['path_l'])
    # Wiese vorn: Baender, nach unten dunkler (zum UI-Panel hin)
    front = p.yy > path_bot[None, :]
    bands = g['front']
    edges = [0, 8, 18, 30, 46, 70]
    for i, col in enumerate(bands):
        p.fill(front & (p.yy >= (path_bot[None, :] + edges[i])), col)
    # Grasbueschel: Kanten des Wegs und Wiese
    grass_tufts(p, (0, GROUND_TOP, W, FOOT_Y - 14), 60, g['tuft'], seed=seed + 1, hmax=2)
    for x in range(0, W, 3):   # Gras ueberhaengend an der hinteren Wegkante
        if r.random() < 0.55:
            h_ = int(r.integers(1, 4))
            p.vline(x, path_top[x] - 1, path_top[x] + h_ - 1, g['meadow'][2])
        if r.random() < 0.5:
            h_ = int(r.integers(1, 4))
            p.vline(x, path_bot[x] - h_ + 1, path_bot[x] + 1, g['front'][0])
    grass_tufts(p, (0, FOOT_Y + 16, W, PANEL_Y + 6), 110, g['tuft_front'], seed=seed + 2, hmax=3)
    # wenige Blumengruppen an den Wegraendern (nicht verstreut)
    for i in range(g.get('flower_count', 0)):
        x = int(60 + (i * 97 + seed * 31) % 570)
        back = i % 2 == 0
        y = path_top[min(W - 1, x)] - 3 if back else path_bot[min(W - 1, x)] + 5 + (i % 3) * 3
        flower_clump(p, x, y, g['flowers'], g['tuft'][0] if back else g['tuft_front'][0], n=3 + i % 3, seed=i)
    return path_top, path_bot


def edge_trees(p, leaves5, trunk):
    """Rahmender Laubbaum links (hinter der NPC-Leiste). Die Krone beginnt erst unterhalb des
    Wolkenbands (y > 84), damit die ziehende Wolkenebene nie ueber Laub gleitet; unterhalb von
    y = 120 bleibt alles links von x = 60."""
    deep, shadow, mid, light, hi = leaves5
    lv = (deep, shadow, mid, light)
    t_dark, t_mid, t_lit = trunk
    # kraeftiger Stamm bei x ~ 18, unten breiter mit Wurzelansatz
    for yy in range(110, 262):
        cx = 18 + 3 * math.sin(yy / 40)
        half = 8 + max(0, (yy - 214)) * 0.22
        p.rect(round(cx - half), yy, round(half * 2), 1, t_mid)
        p.rect(round(cx + half) - 5, yy, 5, 1, t_dark)
        p.rect(round(cx - half), yy, 2, 1, t_lit)
        if yy % 11 in (0, 1):                             # Rindenfurchen
            p.px(round(cx - 1 + (yy // 11) % 3), yy, t_dark)
    for yy in range(118, 250, 7):
        p.vline(round(18 + 3 * math.sin(yy / 40)) + (yy // 7) % 3 - 2, yy, yy + 4, t_dark)
    p.poly([(2, 262), (44, 262), (34, 248), (26, 240)], t_mid)
    p.poly([(30, 262), (50, 262), (36, 250)], t_dark)
    # Ast nach rechts oben (bleibt ueber y = 120)
    for k in range(4):
        p.line(22, 128 + k, 52, 104 + k * 0.6, t_mid if k < 2 else t_dark)
    leaf_clumps(p, [(-8, 110, 22), (18, 98, 20), (44, 104, 16), (62, 98, 10), (4, 128, 20), (32, 124, 14),
                    (-6, 152, 16), (20, 146, 11), (-2, 176, 10)], lv, seed=41)


def barn_day(p, x, base, lights):
    """Rote Scheune mit Mansarddach, weissen Kanten und X-Tor. Front links, Seite rechts im Schatten."""
    red, red_d, red_l, red_dd = '#b8483a', '#8e3530', '#cf5e48', '#6e2a28'
    trim, trim_d = '#f0ebe0', '#c8c2b8'
    roof, roof_l, roof_d = '#6a5a5e', '#84747a', '#4e4248'
    fw, fh = 40, 26          # Giebelfront
    sw = 30                  # Seitenwand (verkuerzt)
    top = base - fh
    # Seitenwand rechts (Schatten)
    p.poly([(x + fw, base), (x + fw + sw, base - 3), (x + fw + sw, top - 1), (x + fw, top)], red_d)
    for k in range(x + fw + 3, x + fw + sw, 3):
        p.vline(k, top + 1 - (k - x - fw) * 1 // sw, base - 1 - (k - x - fw) * 3 // sw, red_dd)
    # Seitendach (Mansarde)
    p.poly([(x + fw / 2, top - 22), (x + fw / 2 + sw, top - 24), (x + fw + sw + 3, top - 4), (x + fw + 3, top - 1)],
           roof)
    p.poly([(x + fw + 3, top - 1), (x + fw + sw + 3, top - 4), (x + fw + sw + 3, top - 1), (x + fw + 3, top + 2)],
           roof_d)
    for k in range(1, 6):   # Schindelreihen
        t = k / 6
        p.line(x + fw / 2 + (fw / 2 + 3) * t, top - 22 + 21 * t, x + fw / 2 + sw + (fw / 2 + 3) * t,
               top - 24 + 20 * t, roof_d)
    p.line(x + fw / 2, top - 22, x + fw / 2 + sw, top - 24, roof_l)
    # Giebelfront (Mansardform)
    g = [(x - 2, top + 1), (x + 3, top - 12), (x + fw / 2, top - 22), (x + fw - 3, top - 12), (x + fw + 2, top + 1)]
    front = p.polym([(x, base)] + g[1:4] + [(x + fw, base)]) | p.box(x, top, fw, fh)
    p.fill(front, red)
    p.fill(front & ((p.xx - x) % 3 == 2), red_d)   # Brettfugen
    p.fill(p.polym(g + [(x + fw + 2, top + 2), (x - 2, top + 2)]) & ~p.polym([(x, base)] + g[1:4] + [(x + fw, base)]),
           trim)
    # Kanten weiss
    p.line(x - 1, top + 1, x + 3, top - 12, trim)
    p.line(x + 3, top - 12, x + fw / 2, top - 22, trim)
    p.line(x + fw / 2, top - 22, x + fw - 3, top - 12, trim_d)
    p.line(x + fw - 3, top - 12, x + fw + 1, top + 1, trim_d)
    p.vline(x, top, base - 1, trim)
    p.vline(x + fw - 1, top, base - 1, trim_d)
    p.hline(x, x + fw - 1, top - 1, trim)
    # Lichtkante links an der Front
    p.vline(x + 1, top, base - 1, red_l)
    # Heubodentuer
    hx, hy = x + fw // 2 - 5, top - 14
    p.rect(hx, hy, 10, 11, red_dd)
    p.fill(p.box(hx, hy, 10, 11) & ~p.box(hx + 1, hy + 1, 8, 9), trim)
    p.line(hx + 1, hy + 1, hx + 8, hy + 9, trim_d)
    p.line(hx + 8, hy + 1, hx + 1, hy + 9, trim_d)
    p.hline(hx + 3, hx + 6, hy - 2, trim)
    p.vline(hx + 4, hy - 2, hy, '#3a3034')
    # Tor mit X
    dx, dy, dw, dh = x + 9, base - 17, 22, 17
    p.rect(dx, dy, dw, dh, red)
    p.fill(p.box(dx, dy, dw, dh) & ~p.box(dx + 1, dy + 1, dw - 2, dh - 1), trim)
    p.vline(dx + dw // 2, dy, base - 1, trim)
    for (a0, a1) in ((dx + 1, dx + dw // 2 - 1), (dx + dw // 2 + 1, dx + dw - 2)):
        p.line(a0, dy + 1, a1, base - 1, trim_d)
        p.line(a1, dy + 1, a0, base - 1, trim_d)
    # Fenster an der Seite
    p.rect(x + fw + 11, top + 8, 6, 6, trim_d)
    p.rect(x + fw + 12, top + 9, 4, 4, '#3a3440')
    # Grundschatten
    p.hline(x - 1, x + fw + sw, base, '#4f7a3c')


# ================================================================== Szene: Daemmerung
DUSK = {
    'sky': ['#2b2150', '#35275c', '#402c68', '#4e3272', '#5e3878', '#723e7c', '#86447c', '#9a4c78',
            '#b05670', '#c46468', '#d67662', '#e48a5e', '#eea062', '#f4b56c', '#f8c67a'],
    'horizon': '#f0a878',
}
CANDLE = '#ffb347'
GLOW_CORE, GLOW_MID, GLOW_EDGE = '#ffe7a0', '#ffc05a', '#e8843a'


def build_dusk():
    p = Painter()
    lights = []
    sky_bands(p, 0, 160, DUSK['sky'])
    # erste Sterne im oberen Himmel (sparsam)
    for (sx, sy, big) in [(92, 24, 1), (170, 40, 0), (236, 22, 0), (330, 34, 1), (402, 26, 0), (468, 44, 0),
                          (544, 20, 1), (600, 38, 0), (286, 52, 0), (520, 58, 0), (140, 62, 0)]:
        p.px(sx, sy, '#f4e8ff')
        if big:
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p.px(sx + dx, sy + dy, '#9c86c8')
    # tiefstehende Sonne mit flachen Lichtringen
    sun_x, sun_y = 262, 148
    for (rr, col, t) in [(52, '#f7b070', 0.25), (38, '#f9c07a', 0.4), (26, '#fcd08a', 0.55)]:
        p.tint(p.disc(sun_x, sun_y, rr) & (p.yy < 160), col, t)
    p.fill(p.disc(sun_x, sun_y, 13), '#ffe2a0')
    p.fill(p.disc(sun_x - 1, sun_y - 1, 10), '#fff0c4')
    # Abendwolken, von unten angestrahlt, und lange Streifen nahe der Sonne
    ev = ('#ffc08a', '#e08078', '#a45a80', '#ffd49a')
    cumulus(p, cloud_puffs(120, 112, 110, 22, seed=31), 112, ev, from_below=True)
    cumulus(p, cloud_puffs(520, 120, 120, 20, seed=32), 120, ev, from_below=True)
    st = ('#ffd49a', '#f09a7c', '#b0607c', '#8a4c7a')
    for (x, y, ln, th, seed) in [(170, 132, 90, 4, 4), (300, 124, 70, 3, 2), (380, 138, 110, 4, 3)]:
        stratus(p, x, y, ln, th, st, seed=seed, sun_x=sun_x)

    # ferne Berge im Gegenlicht
    mountains(p, [(40, 124, 64), (140, 132, 60), (330, 118, 76), (440, 128, 64), (560, 116, 72), (640, 128, 60)],
              168, {'lit': '#9a5c86', 'body': '#7c4c7e', 'dark': '#684274', 'snow': '#e0a0a0', 'snow_d': '#b27a92'},
              seed=5, snow_depth=0.14)
    # ferner Waldsaum als Silhouette
    far_ys = profile(0, W, 158, [(4, 60), (2, 23)], seed=7)
    hill_layer(p, far_ys, '#56406e', '#6a4a76', '#4c3a66')
    pine_row(p, -4, W + 6, far_ys + 3, 9, 17, ('#3f3160', '#4a3868', '#5e4474'), seed=8, step=(4, 7))
    # mittlere Huegel mit abgeernteten Feldern (Stoppeln) und einer Windmuehle
    ys_a = profile(0, W, 174, [(4, 70), (2, 31)], seed=12)
    ys_a = bump(ys_a, 90, 100, 10)
    hill_layer(p, ys_a, '#5c5a70', '#8a6674', '#50506a', lit_w=3)
    stub = ('#7e6270', '#6c5666', '#a47c74')
    fields(p, ys_a, [(150, 260, 3, 14, stub), (470, 560, 3, 12, stub), (560, 640, 3, 16, stub),
                     (230, 330, 13, 28, stub)], hedge=('#3e4254', '#4c5060'))
    mx, mb = 90, int(round(ys_a[90])) + 2
    p.poly([(mx - 6, mb), (mx + 6, mb), (mx + 4, mb - 26), (mx - 4, mb - 26)], '#6e5a70')
    p.poly([(mx - 6, mb), (mx - 3, mb), (mx - 2, mb - 26), (mx - 4, mb - 26)], '#8a6a78')
    p.poly([(mx - 6, mb - 26), (mx + 6, mb - 26), (mx, mb - 34)], '#4e3c5a')
    windmill_blades(p, (mx, mb - 27), 17, 0.1, ('#7a6478', '#5e4c66', '#3e3048'))
    p.px(mx, mb - 14, '#ffc05a')
    lights.append((mx, mb - 14, 5, CANDLE))
    # ferner Hof mit erleuchteten Fenstern
    fx = 118
    farmhouse(p, fx, int(round(ys_a[fx + 14])) + 3, 28, 11,
              {'wall': '#8a7482', 'wall_d': '#6e5c6c', 'timber': '#3e3044', 'roof': '#553a50', 'roof_d': '#44304a',
               'win': '#ffc05a'}, lit=(0, 3), lights=lights)
    for (hx, hw_, hh) in [(292, 9, 5), (306, 7, 4), (500, 9, 5)]:
        haystack(p, hx, int(ys_a[hx]) + 12, hw_, hh, ('#5e4a50', '#7a6060', '#a07e70'))

    # nahe Huegelkante
    ys_b = profile(0, W, 197, [(3, 80), (2, 29)], seed=22)
    ys_b = bump(ys_b, 380, 150, 5)
    hill_layer(p, ys_b, '#4a5650', '#7a6a5a', '#404a4a', lit_w=3)
    # kahler alter Baum links hinten
    bare_tree(p, 172, int(ys_b[172]) + 3, 74, ('#3a2c40', '#4c3a4e', '#8a6062'), seed=3)
    # die alte Scheune
    barn_old(p, 320, int(round(ys_b[364])) + 4, lights)
    # schiefer, kaputter Zaun
    fence(p, 214, 310, lambda x: ys_b[int(x)] + 4, 8, ('#3a3038', '#54464c', '#86685e'), step=12, broken=(3,))
    fence(p, 540, 640, lambda x: ys_b[min(W - 1, int(x))] + 4, 8, ('#3a3038', '#54464c', '#86685e'), step=12,
          broken=(2, 6))
    haystack(p, 566, int(ys_b[566]) + 3, 12, 6, ('#6e5448', '#8a6a52', '#b08a64'))

    # Standflaeche
    path_top, path_bot = ground(p, ys_b, DUSK_GROUND, seed=9)
    # warmer Lichtschein aus dem Scheunentor auf Wiese und Weg (flache Stufen)
    door_x = 320 + 44
    for (rx, ry, t) in [(64, 18, 0.07), (44, 12, 0.09), (24, 7, 0.12)]:
        m = p.ell(door_x, ys_b[door_x] + 9, rx, ry) & (p.yy > ys_b[door_x] + 3)
        p.tint(m, '#ff8a50', t)

    edge_trees(p, ('#191c28', '#222834', '#2c3640', '#3e4a4c', '#6a5458'), ('#1e1624', '#2c2230', '#5e4450'))
    return p, lights


DUSK_GROUND = {
    'meadow': ['#4c5a4e', '#48544a', '#434e46'],
    'meadow_lit': '#5a6450',
    'path': '#7e6660', 'path_d': '#6a5654', 'path_l': '#98786a', 'path_rut': '#62504e',
    'front': ['#3e4a42', '#38433e', '#323c38', '#2c3432', '#262d2c', '#202626'],
    'tuft': ['#3c4a40', '#5e6452'],
    'tuft_front': ['#2e3834', '#46524a'],
    'flowers': ['#b8a8c8', '#d8a870'],
    'flower_count': 6,
    'pebble': '#5e4c4c',
}


def stratus(p, x, y, length, th, tones, seed=0, sun_x=None, wrap=False):
    """Flacher Wolkenstreifen in der Daemmerung: Unterkante vom Sonnenlicht angestrahlt,
    Oberseite im Violett des Himmels. tones = (glut, rosa, violett, dunkel)."""
    glow, pink, violet, dark = tones
    r = np.random.default_rng(seed)
    shifts = (-p.w, 0, p.w) if wrap else (0,)
    for s in shifts:
        m = np.zeros((p.h, p.w), bool)
        n = max(3, int(length / 14))
        for i in range(n):
            t = i / (n - 1)
            cx = x + s + t * length
            hump = math.sin(t * math.pi) ** 0.6
            ry = th * (0.45 + 0.55 * hump) * r.uniform(0.8, 1.1)
            rx = length / n * r.uniform(0.8, 1.2)
            m |= p.ell(cx, y - ry * 0.4, rx, ry)
        m &= p.yy <= y + 1
        if not m.any():
            continue
        p.fill(m, violet)
        # Oberkante dunkler, Unterkante angestrahlt
        up = np.zeros_like(m)
        up[2:] = m[:-2]
        p.fill(m & ~np.roll(m, 2, axis=0) | (m & (p.yy < y - th * 0.9)), dark)
        down1 = np.roll(m, -1, axis=0)
        down3 = np.roll(m, -3, axis=0)
        p.fill(m & ~down3, pink)
        p.fill(m & ~down1, glow)
        if sun_x is not None:
            # zur Sonne hin staerker leuchtend
            near = m & (np.abs(p.xx - sun_x) < 60) & ~down3
            p.fill(near, glow)


def bare_tree(p, x, base, h, tones, seed=0):
    """Kahler, knorriger Baum (Silhouette mit warmer Lichtkante links)."""
    dark, mid, rim = tones
    r = np.random.default_rng(seed)

    def branch(x0, y0, ang, ln, wd, depth):
        x1 = x0 + math.cos(ang) * ln
        y1 = y0 + math.sin(ang) * ln
        steps = int(ln)
        for k in range(steps + 1):
            t = k / max(1, steps)
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            w = max(1.0, wd * (1 - t * 0.4))
            p.rect(round(cx - w / 2), round(cy), max(1, round(w)), 1, mid)
            if w >= 2:
                p.px(round(cx - w / 2), round(cy), rim)
        if depth > 0:
            for da in (-0.5, 0.45):
                branch(x1, y1, ang + da + r.uniform(-0.2, 0.2), ln * r.uniform(0.55, 0.7), wd * 0.6, depth - 1)
    # Stamm
    for yy in range(int(base - h * 0.45), int(base)):
        t = (yy - (base - h * 0.45)) / (h * 0.45)
        w = 4 + t * 3
        cx = x + math.sin(yy / 9) * 1.5
        p.rect(round(cx - w / 2), yy, round(w), 1, mid)
        p.px(round(cx - w / 2), yy, rim)
        p.px(round(cx + w / 2) - 1, yy, dark)
    top = (x + math.sin((base - h * 0.45) / 9) * 1.5, base - h * 0.45)
    branch(top[0], top[1], -math.pi / 2 - 0.5, h * 0.3, 3.5, 3)
    branch(top[0], top[1], -math.pi / 2 + 0.55, h * 0.32, 3.5, 3)
    branch(top[0], top[1] + 4, -math.pi / 2 + 0.05, h * 0.24, 2.5, 2)


def barn_old(p, x, base, lights):
    """Alte, verlassene Scheune: verwitterte Bretter, durchhaengendes Mansarddach mit Loechern,
    fehlende Bretter und Ritzen, durch die Kerzenschein faellt; Tor einen Spalt offen."""
    wood = ['#6c5a62', '#62525c', '#766268']     # Brett-Toene (verwittert, Daemmerlicht)
    wood_d, gap, rim = '#4a3c4a', '#241a26', '#b08070'
    side, side_d = '#4c3e4e', '#3e3242'
    roof, roof_d, roof_l, roof_rim = '#3e3448', '#2e2638', '#54465a', '#a0707a'
    inner = '#4a2a26'
    fw, wh = 88, 44
    top = base - wh
    ridge_x, ridge_y = x + fw / 2 + 2, top - 34
    gable = [(x, top), (x + 9, top - 20), (ridge_x, ridge_y), (x + fw - 9, top - 21), (x + fw, top)]
    sw = 56                                          # Seitenwand nach hinten rechts
    # --- Seitenwand (Schatten) und Seitendach
    p.poly([(x + fw, base), (x + fw + sw, base - 5), (x + fw + sw, top - 4), (x + fw, top)], side)
    sm = p.polym([(x + fw, base), (x + fw + sw, base - 5), (x + fw + sw, top - 4), (x + fw, top)])
    p.fill(sm & ((p.xx - x) % 5 == 0), side_d)
    # Seitendach: Mansarde, leicht durchhaengend
    r_pts = [(ridge_x, ridge_y), (ridge_x + sw, ridge_y - 4), (x + fw - 9 + sw, top - 25),
             (x + fw + 4 + sw, top - 4), (x + fw + 4, top + 1), (x + fw - 9, top - 21)]
    rm = p.polym(r_pts)
    p.fill(rm, roof)
    # Durchhang: mittlere Zone dunkler
    sag = p.polym([(ridge_x + sw * 0.35, ridge_y + 1), (ridge_x + sw * 0.7, ridge_y - 1),
                   (x + fw + sw * 0.7, top - 1), (x + fw + sw * 0.3, top + 1)])
    p.fill(rm & sag, roof_d)
    for k in range(1, 9):                            # Schindelreihen
        t = k / 9
        ax = ridge_x + (x + fw + 4 - ridge_x) * t
        ay = ridge_y + (top + 1 - ridge_y) * t + math.sin(t * math.pi) * 2
        p.line(ax, ay, ax + sw, ay - 4 + math.sin(t * math.pi) * 1, roof_d)
    p.line(ridge_x, ridge_y, ridge_x + sw, ridge_y - 4, roof_l)
    # Loch im Dach mit Sparren
    hole = p.polym([(x + fw + 18, top - 14), (x + fw + 30, top - 17), (x + fw + 34, top - 8), (x + fw + 20, top - 5)])
    p.fill(hole & rm, '#1a1420')
    for k in range(3):
        p.line(x + fw + 20 + k * 5, top - 16 + k * 0.5, x + fw + 22 + k * 5, top - 6, '#4a3a44')
    # --- Giebelfront
    front = p.polym([(x, base)] + gable + [(x + fw, base)])
    p.fill(front, wood[0])
    bw = 4
    for i, bx in enumerate(range(x, x + fw, bw)):
        col = wood[(i * 7 + (i // 3)) % 3]
        p.fill(front & (p.xx >= bx) & (p.xx < bx + bw), col)
        p.fill(front & (p.xx == bx + bw - 1), gap)
    # Querriegel (Holmen) im Dreieck
    p.fill(front & (p.yy == top) | front & (p.yy == top + 1), wood_d)
    # Lichtkante (Abendlicht von links)
    p.line(x, top, x + 9, top - 20, rim)
    p.line(x + 9, top - 20, ridge_x, ridge_y, rim)
    p.vline(x, top, base - 1, rim)
    # Dachueberstand vorn
    p.line(x - 2, top + 1, x + 8, top - 21, roof)
    p.line(x + 8, top - 21, ridge_x, ridge_y - 1, roof)
    p.line(x + fw - 8, top - 22, x + fw + 2, top + 1, roof_d)
    p.line(ridge_x, ridge_y - 1, x + fw - 8, top - 22, roof_d)
    p.line(x - 2, top, x + 8, top - 22, roof_rim)
    p.line(x + 8, top - 22, ridge_x, ridge_y - 2, roof_rim)

    def glow_slit(x0, y0, length, core=True):
        p.vline(x0, y0, y0 + length - 1, GLOW_EDGE)
        if core and length > 3:
            p.vline(x0, y0 + 1, y0 + length - 2, GLOW_MID)
        if core and length > 7:
            p.vline(x0, y0 + length // 2 - 1, y0 + length // 2 + 1, GLOW_CORE)
        lights.append((x0, y0 + length // 2, 6 + length // 2, CANDLE))

    # --- Heuboden-Luke, mit Brettern vernagelt, Licht dahinter
    hx, hy = int(ridge_x) - 9, top - 22
    p.rect(hx - 1, hy - 1, 18, 16, wood_d)
    p.rect(hx, hy, 16, 14, GLOW_MID)
    p.fill(p.ell(hx + 8, hy + 8, 6, 5), GLOW_CORE)
    p.rect(hx, hy + 11, 16, 3, '#c07a3a')              # Heu im Gegenlicht
    for k in range(0, 16, 3):
        p.px(hx + k, hy + 10, '#c07a3a')
    p.line(hx - 1, hy + 2, hx + 16, hy + 9, wood[2])      # schiefe Bretter davor
    p.line(hx - 1, hy + 3, hx + 16, hy + 10, wood_d)
    p.line(hx + 2, hy + 13, hx + 14, hy - 1, wood[1])
    p.line(hx + 3, hy + 13, hx + 15, hy - 1, wood_d)
    lights.append((hx + 8, hy + 7, 16, CANDLE))
    # --- grosses Tor, rechter Fluegel einen Spalt offen
    dx, dw, dh = x + 26, 36, 32
    dy = base - dh
    p.rect(dx - 2, dy - 2, dw + 4, dh + 2, wood_d)
    p.rect(dx, dy, dw, dh, wood[1])
    for k in range(dx, dx + dw, 4):
        p.vline(k + 3, dy, base - 1, wood_d)
    # Spalt mit Innenraum und Kerzenlicht
    gx0 = dx + dw // 2 - 1
    p.rect(gx0, dy, 6, dh, GLOW_MID)
    p.rect(gx0 + 1, dy + 8, 4, dh - 8, GLOW_CORE)
    p.rect(gx0, dy + dh - 5, 6, 5, '#e0a050')           # Kornsaecke im Licht
    p.px(gx0 + 2, dy + dh - 6, '#e0a050')
    p.vline(gx0 + 5, dy, base - 1, '#c8703a')
    lights.append((gx0 + 3, dy + dh // 2, 24, CANDLE))
    # Andreaskreuze auf den Fluegeln (verblasste Farbe)
    for (a0, a1) in ((dx + 1, gx0 - 1), (gx0 + 7, dx + dw - 2)):
        p.line(a0, dy + 1, a1, base - 2, '#8a7270')
        p.line(a1, dy + 1, a0, base - 2, '#8a7270')
    # rechter Fluegel leicht aufgeschwungen (schmaler, dunkler)
    p.poly([(gx0 + 6, dy - 1), (gx0 + 10, dy - 3), (gx0 + 10, base + 1), (gx0 + 6, base)], '#3e3240')
    # --- fehlende Bretter mit Licht
    for (bx, by, ln) in [(x + 10, top + 12, 14), (x + 70, top + 8, 18), (x + 18, top - 8, 9)]:
        p.rect(bx, by, 3, ln, GLOW_MID)
        p.vline(bx + 1, by + 2, by + ln - 3, GLOW_CORE)
        p.hline(bx, bx + 2, by + ln // 2, wood_d)      # Riegel dahinter
        lights.append((bx + 1, by + ln // 2, 10, CANDLE))
    # --- Ritzen mit Kerzenschein
    for (sx, sy, ln) in [(x + 3, top + 20, 8), (x + 67, top + 26, 10), (x + 79, top + 14, 6), (x + 7, top + 4, 5),
                         (x + 83, top + 30, 7), (x + 35, top - 14, 6), (x + 55, top - 6, 7)]:
        glow_slit(sx, sy, ln)
    # Ritzen in der Seitenwand (schwaecher)
    for (sx, sy, ln) in [(x + fw + 9, top + 12, 7), (x + fw + 24, top + 20, 9), (x + fw + 39, top + 8, 6)]:
        p.vline(sx, sy, sy + ln - 1, GLOW_EDGE)
        p.vline(sx, sy + 2, sy + ln - 3, GLOW_MID)
        lights.append((sx, sy + ln // 2, 7, CANDLE))
    # Fundament-Schatten und Kornsaecke vor dem Tor
    p.hline(x - 1, x + fw + sw, base, '#2c3030')
    for (kx, ky) in [(dx - 8, base), (dx - 3, base + 1), (dx + dw + 6, base)]:
        p.fill(p.ell(kx, ky - 3, 3.5, 3.5) & (p.yy <= ky), '#8a6e58')
        p.fill(p.ell(kx - 1, ky - 4, 2, 2), '#a8866a')
        p.px(kx, ky - 7, '#5e4a44')
    for k in range(10):                                 # verstreutes Korn
        p.px(dx + 4 + k * 3, base + 2 + (k % 2), '#c8a060')


# ================================================================== Wolkenebenen
def clouds_day():
    """Ziehende Wolkenebene Tag: drei skulptierte Kumulusgruppen, kachelbar."""
    h = CLOUD_H
    p = Painter(W, h)
    tones = ('#ffffff', '#e4edf6', '#c4d5e8', '#adc2dc')
    for (cx, base, w, hh, seed) in [(96, 50, 104, 36, 11), (318, 26, 50, 16, 12), (500, 58, 124, 40, 13),
                                    (626, 22, 40, 14, 14)]:
        cumulus(p, cloud_puffs(cx, base, w, hh, seed=seed), base, tones, wrap=True)
    return p


def clouds_dusk():
    """Ziehende Wolkenebene Daemmerung: lange, flache Streifen, kachelbar."""
    h = CLOUD_H
    p = Painter(W, h)
    ev = ('#f0a080', '#c46c7c', '#8a4c7c', '#f6b48a')
    for (cx, base, w, hh, seed) in [(90, 44, 120, 22, 21), (330, 24, 70, 14, 22), (500, 58, 140, 24, 23)]:
        cumulus(p, cloud_puffs(cx, base, w, hh, seed=seed), base, ev, wrap=True, from_below=True)
    stratus(p, 600, 60, 90, 4, ('#f6b48a', '#d0787c', '#8e507e', '#6e4078'), seed=24, wrap=True)
    return p


# ================================================================== Probe (Lesbarkeit)
def probe(bg: Image.Image, out_path):
    """Legt Spielfiguren und Gegner-Silhouetten testweise auf die Fusslinie."""
    img = bg.copy()
    try:
        import rig3 as RG
        import chars as C
        for (x, race, klass) in [(120, 'orc', 'warrior'), (240, 'human', 'priest')]:
            L = RG.frames(race, klass, 0)[0]
            f = RG.preview_frame(race, klass, 0, C.SKIN_PALETTES[race][1], C.HAIR_PALETTES[race][1], L)
            fi = f.image().resize((f.w * 2, f.h * 2), Image.NEAREST)
            img.alpha_composite(fi, (x - fi.width // 2, FOOT_Y - fi.height))
    except Exception as e:   # Probe darf nie den Build verhindern
        print('Probe ohne Spielfiguren:', e)
    d = ImageDraw.Draw(img)
    for (x, w, h) in [(400, 40, 56), (480, 56, 90), (570, 44, 70)]:
        d.ellipse([x - w // 2, FOOT_Y - h, x + w // 2, FOOT_Y + 4], fill=(22, 16, 30, 255))
        d.ellipse([x - w // 2 + 3, FOOT_Y - h + 3, x + w // 2 - 3, FOOT_Y + 1], fill=(120, 60, 70, 255))
    d.line([(0, FOOT_Y), (8, FOOT_Y)], fill=(255, 0, 0, 255))
    d.rectangle([0, 0, W, 17], fill=(20, 16, 28, 200))
    d.rectangle([0, PANEL_Y, W, H], fill=(20, 16, 28, 235))
    d.rectangle([0, 18, 43, PANEL_Y], fill=(20, 16, 28, 150))
    img.resize((W * 2, H * 2), Image.NEAREST).save(out_path)


# ================================================================== Build
SCENES = {
    'gruenhain_day': (build_day, clouds_day, {'clouds_y': CLOUD_Y, 'clouds_speed': 4.0}),
    'gruenhain_dusk': (build_dusk, clouds_dusk, {'clouds_y': CLOUD_Y, 'clouds_speed': 2.5}),
}


def build(root, preview_dir=None, only=None):
    gfx = os.path.join(root, 'assets', 'gfx', 'battle')
    os.makedirs(gfx, exist_ok=True)
    meta = {}
    for name, (fn_bg, fn_clouds, cfg) in SCENES.items():
        if only and name not in only:
            continue
        p, lights = fn_bg()
        p.save(os.path.join(gfx, f'{name}.png'))
        cl = fn_clouds() if fn_clouds else None
        entry = {'clouds': None, 'clouds_y': cfg['clouds_y'], 'clouds_speed': cfg['clouds_speed'],
                 'lights': [{'x': int(x), 'y': int(y), 'r': int(rr), 'color': col} for (x, y, rr, col) in lights]}
        if cl is not None and cl.a[:, :, 3].any():
            cl.save(os.path.join(gfx, f'{name}_clouds.png'))
            entry['clouds'] = f'res://assets/gfx/battle/{name}_clouds.png'
        meta[name] = entry
        if preview_dir:
            os.makedirs(preview_dir, exist_ok=True)
            comp = p.image()
            if cl is not None:
                comp.alpha_composite(cl.image(), (0, cfg['clouds_y']))
            comp.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(preview_dir, f'bg_{name}.png'))
            probe(comp, os.path.join(preview_dir, f'bg_{name}_probe.png'))
    if not only:
        data = os.path.join(root, 'data')
        os.makedirs(data, exist_ok=True)
        with open(os.path.join(data, 'battle_bg.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
    return meta


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, '..', '..', 'healer-simulator'))
    prev = os.path.normpath(os.path.join(here, '..', '..', 'output', 'kampf'))
    only = sys.argv[1:] or None
    print(json.dumps(build(root, prev, only), indent=1))
