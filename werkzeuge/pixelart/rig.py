"""Figuren-Rig: Koerper, Arme und Kleidung werden pro Frame aus Posen berechnet.

Ebenen je Frame (32x36, Fuesse auf Zeile 35, Blick nach rechts):
  skin   - Index-Graustufen (0 Kontur, 1 Schatten, 2 Basis, 3 Licht) -> Hautpalette
  outfit - feste Farben (Kleidung, Hauer, Kontur)
  eyes   - feste Farben (Augen; beim Blinzeln ausgeblendet)
  hair   - Index-Graustufen -> Haarpalette
  gear   - feste Farben ueber den Haaren (Helm, Bartperlen, Lichtzauber)

Animationen:
  idle  8 Frames: Atmen (Oberkoerper), wehende Robe, schwingende Haare
  cast 10 Frames: Haende heben sich, Licht sammelt sich zwischen den Haenden
"""
from __future__ import annotations

import numpy as np

import heads as HD
from pa import Canvas, c, mix, BAYER4

FW, FH = 32, 36
LAYERS = ['skin', 'outfit', 'eyes', 'hair', 'gear']
IDX = {0: (0, 0, 0, 255), 1: (85, 85, 85, 255), 2: (170, 170, 170, 255), 3: (255, 255, 255, 255)}
OUTLINE = '#1b1424'

ANIMS = {
    'idle': {'start': 0, 'count': 8, 'fps': 7, 'loop': True},
    'cast': {'start': 8, 'count': 10, 'fps': 10, 'loop': False},
}
FRAME_COUNT = 18

# Koerperbau je Rasse: Schulter (sy, Halbbreite), Taille, Saum
BODY = {
    'human': dict(cx=16.0, sy=19, shw=4.2, wy=26, ww=3.6, hy=34, hw=5.8),
    'dwarf': dict(cx=15.5, sy=25, shw=6.0, wy=29, ww=5.8, hy=34, hw=6.8),
    'orc': dict(cx=15.6, sy=18, shw=6.6, wy=25, ww=5.2, hy=34, hw=6.8),
    'gnome': dict(cx=16.0, sy=27, shw=3.4, wy=30, ww=3.3, hy=34, hw=4.4),
}

PRIEST = {'W': '#f6f1e2', 'w': '#d8cdb6', 'v': '#a8977f', 'vv': '#7e6e5c',
          'Y': '#f5c95a', 'y': '#b8862e', 'u': '#4f76c4', 'U': '#86aaf0', 'n': '#4a2f24', 'N': '#6e4633'}
WARRIOR = {'S': '#e0e4ec', 's': '#a4acbe', 'z': '#687088', 'zz': '#454b5e',
           'R': '#c8483f', 'r': '#86282d', 'L': '#9a643a', 'l': '#643f24', 'Y': '#f5c95a', 'y': '#b8862e'}

# Posen: Atmen (Oberkoerper-Versatz), Saum-Schwung, Haar-Schwung, Handziele, Leuchten
IDLE_BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
IDLE_HEM = [0, 0, 0, 1, 1, 1, 1, 0]
IDLE_HAIR = [0, 0, 0, 0, 1, 1, 1, 0]
# Cast: Handposition relativ (0 = Ruhe, 1 = Brust, 2 = erhoben), Leuchtstaerke
CAST = [(0.0, 0), (0.35, 0), (0.8, 0), (1.2, 1), (1.7, 2), (2.0, 3), (2.0, 3), (1.6, 2), (0.9, 1), (0.3, 0)]
CAST_BREATH = [0, 0, 0, 0, -1, -1, -1, 0, 0, 0]


# ---------------------------------------------------------------- Helfer
def _shift(mask_or_lv: np.ndarray, dy: int, dx: int = 0) -> np.ndarray:
    out = np.zeros_like(mask_or_lv)
    h, w = mask_or_lv.shape
    ys = slice(max(0, -dy), h - max(0, dy))
    yd = slice(max(0, dy), h - max(0, -dy))
    xs = slice(max(0, -dx), w - max(0, dx))
    xd = slice(max(0, dx), w - max(0, -dx))
    out[yd, xd] = mask_or_lv[ys, xs]
    return out


def _poly_mask(pts):
    cv = Canvas(FW, FH)
    cv.poly(pts, (255, 255, 255, 255))
    return cv.a[:, :, 3] > 0


def _thick_line_mask(p0, p1, r0, r1):
    """Kapsel von p0 nach p1 mit Radius r0 -> r1 (Arme/Aermel)."""
    ys, xs = np.mgrid[0:FH, 0:FW]
    px, py = xs + 0.5, ys + 0.5
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((px - x0) * dx + (py - y0) * dy) / L2, 0, 1)
    cx, cy = x0 + t * dx, y0 + t * dy
    r = r0 + (r1 - r0) * t
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r


def _shade_by_x(mask, lit=0.3, dark=0.72):
    """Schattierung quer ueber eine Flaeche in klaren Baendern: links hell, rechts dunkel."""
    lv = np.zeros(mask.shape, int)
    for y in range(FH):
        xs = np.where(mask[y])[0]
        if len(xs) == 0:
            continue
        x0, x1 = xs.min(), xs.max()
        for x in xs:
            t = (x - x0 + 0.5) / max(1, x1 - x0 + 1)
            lv[y, x] = 3 if t < lit else (1 if t > dark else 2)
    return lv


def _border(mask):
    return HD.border_of(mask)


# ---------------------------------------------------------------- Pose -> Ebenen
def hand_positions(race, amount, breath):
    """Handpositionen: Ruhe (0) -> vor der Brust (1) -> seitlich erhoben (2)."""
    b = BODY[race]
    cx, sy, shw, wy = b['cx'], b['sy'] + breath, b['shw'], b['wy']
    rest_l = (cx - shw - 0.4, wy + 1.8)
    rest_r = (cx + shw + 0.6, wy + 1.8)
    chest_l = (cx - shw + 1.2, sy + 4.5)
    chest_r = (cx + shw + 2.2, sy + 3.8)
    up_l = (cx - shw - 2.0, sy - 1.5)
    up_r = (cx + shw + 2.6, sy - 2.0)

    def lerp(a, bb, t):
        return (a[0] + (bb[0] - a[0]) * t, a[1] + (bb[1] - a[1]) * t)
    if amount <= 1:
        return lerp(rest_l, chest_l, amount), lerp(rest_r, chest_r, amount)
    t = min(1.0, amount - 1)
    return lerp(chest_l, up_l, t), lerp(chest_r, up_r, t)


def compose(race: str, klass: str, style: int, breath=0, hem=0, hair_sway=0, hands=0.0, glow=0) -> dict:
    b = BODY[race]
    cx, sy, shw, wy, ww, hy, hw = b['cx'], b['sy'] + breath, b['shw'], b['wy'], b['ww'], b['hy'], b['hw']
    L = {name: Canvas(FW, FH) for name in LAYERS}
    pal = PRIEST if klass == 'priest' else WARRIOR

    # ---- Kopf (mit Atmen-Versatz)
    lv_head, details = HD.head_parts(race)
    lv_head = _shift(lv_head, breath)
    head_m = lv_head > 0

    # ---- Arme / Haende
    hl, hr = hand_positions(race, hands, breath)
    shoulder_l = (cx - shw + 1.0, sy + 1.2)
    shoulder_r = (cx + shw - 0.6, sy + 1.2)
    sleeve_l = _thick_line_mask(shoulder_l, (hl[0], hl[1] - 1.2), 1.6, 2.1)
    sleeve_r = _thick_line_mask(shoulder_r, (hr[0], hr[1] - 1.2), 1.6, 2.1)
    hand_l = _thick_line_mask((hl[0], hl[1] - 0.2), (hl[0], hl[1] + 0.4), 1.1, 1.1)
    hand_r = _thick_line_mask((hr[0], hr[1] - 0.2), (hr[0], hr[1] + 0.4), 1.1, 1.1)

    # ---- Rumpf
    if klass == 'priest':
        torso = _poly_mask([(cx - shw, sy), (cx + shw, sy), (cx + ww + 0.3, wy), (cx + hw + hem * 0.8, hy + 1),
                            (cx - hw + hem * 0.5, hy + 1), (cx - ww - 0.3, wy)])
        legs = np.zeros_like(torso)
    else:
        torso = _poly_mask([(cx - shw, sy), (cx + shw, sy), (cx + ww, wy + 1), (cx - ww, wy + 1)])
        legs = _poly_mask([(cx - ww + 0.5, wy), (cx - 0.6, wy), (cx - 0.6, hy + 1), (cx - ww + 0.2, hy + 1)]) | \
            _poly_mask([(cx + 0.6, wy), (cx + ww - 0.3, wy), (cx + ww - 0.1, hy + 1), (cx + 0.6, hy + 1)])

    body_lv = _shade_by_x(torso | legs, 0.3, 0.7)
    arm_back = sleeve_l
    arm_front = sleeve_r

    if klass == 'priest':
        cols = {3: pal['W'], 2: pal['w'], 1: pal['v']}
        for y, x in zip(*np.where(torso)):
            L['outfit'].px(x, y, cols[body_lv[y, x]])
        # Stola (goldenes Band vorne), Saum, Guertel, Kragen
        stx = int(cx + 1)
        for y in range(sy + 1, hy + 1):
            if torso[y, stx]:
                L['outfit'].px(stx, y, pal['Y'])
            if torso[y, stx + 1]:
                L['outfit'].px(stx + 1, y, pal['y'])
        for x in range(FW):
            if torso[hy, x]:
                L['outfit'].px(x, hy, pal['Y'] if x < cx + 2 else pal['y'])
            if torso[wy, x]:
                L['outfit'].px(x, wy, pal['u'] if x != stx and x != stx + 1 else pal['Y'])
                if torso[wy - 1, x] and x < cx:
                    pass
        for x in range(int(cx - 2), int(cx + 3)):
            L['outfit'].px(x, sy, pal['Y'] if x < cx + 1 else pal['y'])
        # Fuesse
        for fx in (cx - 2, cx + 1):
            L['outfit'].px(fx, hy + 1, pal['n'])
            L['outfit'].px(fx + 1, hy + 1, pal['N'])
        sleeve_cols = (pal['W'], pal['w'], pal['v'])
        cuff = pal['Y']
    else:
        cols = {3: pal['S'], 2: pal['s'], 1: pal['z']}
        for y, x in zip(*np.where(torso | legs)):
            L['outfit'].px(x, y, cols[body_lv[y, x]])
        # Wappenrock
        tab = _poly_mask([(cx - 1.8, sy + 2), (cx + 2.6, sy + 2), (cx + 2.8, hy - 2), (cx - 2.0, hy - 2)])
        tlv = _shade_by_x(tab, 0.3, 0.7)
        for y, x in zip(*np.where(tab)):
            L['outfit'].px(x, y, pal['R'] if tlv[y, x] >= 2 else pal['r'])
        ex, ey = int(cx), sy + 4
        for (dx, dy) in [(0, 0), (1, 0), (0, -1), (0, 1), (-1, 0)]:
            L['outfit'].px(ex + dx, ey + dy, pal['Y'])
        for x in range(FW):
            if (torso | legs)[wy, x]:
                L['outfit'].px(x, wy, pal['L'] if x < cx + 2 else pal['l'])
        L['outfit'].px(int(cx), wy, pal['Y'])
        # Stiefel
        for y in (hy, hy + 1):
            for x in range(FW):
                if legs[y, x]:
                    L['outfit'].px(x, y, pal['zz'])
        # Schulterstuecke
        for (px_, py_) in [shoulder_l, shoulder_r]:
            m = HD.ellipse_mask(px_, py_ - 0.2, 2.3, 1.9)
            for y, x in zip(*np.where(m)):
                L['outfit'].px(x, y, pal['S'] if y < py_ - 0.4 else pal['s'])
        sleeve_cols = (pal['S'], pal['s'], pal['z'])
        cuff = pal['zz']

    # Arme: hinterer Arm dunkler, vorderer normal
    for arm, dark in ((arm_back, True), (arm_front, False)):
        alv = _shade_by_x(arm, 0.35, 0.7)
        for y, x in zip(*np.where(arm)):
            lvl = alv[y, x] - (1 if dark else 0)
            L['outfit'].px(x, y, sleeve_cols[0] if lvl >= 3 else (sleeve_cols[1] if lvl == 2 else sleeve_cols[2]))
    # Aermelsaum
    for hand, arm in ((hl, arm_back), (hr, arm_front)):
        for y, x in zip(*np.where(arm)):
            if abs(y + 0.5 - (hand[1] - 1.0)) < 0.7:
                L['outfit'].px(x, y, cuff)

    # Haende (Haut, beim Krieger Handschuhe)
    for hmask in (hand_l, hand_r):
        for y, x in zip(*np.where(hmask)):
            if klass == 'priest':
                L['skin'].px(x, y, IDX[3 if y < hl[1] else 2])
            else:
                L['outfit'].px(x, y, pal['s'])

    # Kopfhaut + Gesicht
    for y, x in zip(*np.where(head_m)):
        L['skin'].px(x, y, IDX[int(lv_head[y, x])])
    for (x, y, ch) in details:
        y += breath
        if ch == 'e':
            L['eyes'].px(x, y, '#1b1424')
            L['eyes'].px(x, y - 1, '#1b1424')
            L['skin'].px(x, y, IDX[2])
            L['skin'].px(x, y - 1, IDX[2])
        elif ch == 'm':
            L['skin'].px(x, y, IDX[1])
        elif ch == 't':
            L['outfit'].px(x, y, '#f4ecd0')

    # Frisur (mit Schwung der unteren Teile)
    hm, hlv, hdet = HD.hair_levels(race, style)
    if klass == 'warrior':
        gm, gch = HD.helmet(race)
        hm = hm & ~gm
    hlv = np.where(hm, hlv, 0)
    if hair_sway:
        h = HD.HEAD[race]
        low = np.zeros_like(hm)
        low[int(h['cy'] + 2):, :] = True
        moved = _shift(np.where(low, hlv, 0), 0, -hair_sway)
        hlv = np.where(low, 0, hlv)
        hlv = np.where(moved > 0, moved, hlv)
    hlv = _shift(hlv, breath)
    hm2 = hlv > 0
    for y, x in zip(*np.where(hm2)):
        L['hair'].px(x, y, IDX[int(hlv[y, x])])
    for (x, y, ch) in hdet:
        L['hair'].clear_px(x, y + breath)
        L['gear'].px(x, y + breath, {'Y': '#f5c95a', 'y': '#b8862e'}[ch])

    # Helm
    if klass == 'warrior':
        gm2 = _shift(gm, breath)
        gch2 = np.full(gch.shape, '.', dtype='<U1')
        if breath > 0:
            gch2[breath:, :] = gch[:-breath, :]
        elif breath < 0:
            gch2[:breath, :] = gch[-breath:, :]
        else:
            gch2 = gch
        wcol = {'S': WARRIOR['S'], 's': WARRIOR['s'], 'z': WARRIOR['z'], 't': '#f4ecd0', 'R': WARRIOR['R']}
        for y, x in zip(*np.where(gm2)):
            L['gear'].px(x, y, wcol.get(gch2[y, x], WARRIOR['s']))

    # Lichtzauber: kleine Lichtkugeln an beiden Haenden
    if glow > 0:
        core = ['#fff6d0', '#ffffff', '#ffffff'][glow - 1]
        pts = {1: [(0, 0)], 2: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)],
               3: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, -2), (0, 2)]}[glow]
        for hx, hy_ in (hl, hr):
            gx, gy = int(hx), int(hy_ - 2)
            for (dx, dy) in pts:
                d = abs(dx) + abs(dy)
                L['gear'].px(gx + dx, gy + dy, core if d == 0 else ('#ffe38a' if d == 1 else '#f5c95a'))

    # ---- Aussenkontur um die ganze Figur (in der Outfit-Ebene, unter Haaren/Helm)
    solid = np.zeros((FH, FW), bool)
    for name in LAYERS:
        solid |= L[name].a[:, :, 3] > 0
    ring = _border(solid)
    for y, x in zip(*np.where(ring)):
        L['outfit'].px(x, y, OUTLINE)
    # Innenkonturen: Haare gegen Gesicht und Arme gegen Rumpf leicht absetzen
    hair_edge = _border(hm2) & head_m & ~hm2
    for y, x in zip(*np.where(hair_edge)):
        if L['eyes'].a[y, x, 3] == 0:
            L['skin'].px(x, y, IDX[1])
    front_edge = _border(arm_front) & torso & ~arm_front
    for y, x in zip(*np.where(front_edge)):
        if L['outfit'].a[y, x, 3] > 0 and x > cx - 1:
            L['outfit'].px(x, y, pal['v'] if klass == 'priest' else pal['z'])
    return L


def frames(race, klass, style):
    out = []
    for i in range(8):
        out.append(compose(race, klass, style, IDLE_BREATH[i], IDLE_HEM[i], IDLE_HAIR[i], 0.0, 0))
    for i, (amt, glow) in enumerate(CAST):
        out.append(compose(race, klass, style, CAST_BREATH[i], 0, 0, amt, glow if klass == 'priest' else 0))
    return out


def sheet(race, klass, style) -> Canvas:
    fr = frames(race, klass, style)
    cv = Canvas(FW * len(fr), FH * len(LAYERS))
    for i, L in enumerate(fr):
        for r, name in enumerate(LAYERS):
            cv.paste(L[name], i * FW, r * FH)
    return cv


def colorize(layer: Canvas, ramp3) -> Canvas:
    pal = [c(OUTLINE)] + [c(x) for x in ramp3]
    out = Canvas(layer.w, layer.h)
    alpha = layer.a[:, :, 3] > 0
    idx = (layer.a[:, :, 0].astype(int) + 42) // 85
    for i in range(4):
        out.a[alpha & (idx == i)] = pal[i]
    return out


def preview_frame(race, klass, style, skin_ramp, hair_ramp, L) -> Canvas:
    out = Canvas(FW, FH)
    out.paste(colorize(L['skin'], skin_ramp), 0, 0)
    out.paste(L['outfit'], 0, 0)
    out.paste(L['eyes'], 0, 0)
    out.paste(colorize(L['hair'], hair_ramp), 0, 0)
    out.paste(L['gear'], 0, 0)
    return out
