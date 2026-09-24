"""Prozedurale Koepfe, Frisuren, Baerte und Helme.

Koepfe werden als Ellipse mit Lichtmodell (Licht von oben links) in 3 Stufen
schattiert. Frisuren sind Formen (Kappe, Zopf, Dutt, Bart ...), die an der
Kopfgeometrie ausgerichtet werden - dadurch sitzen alle Frisuren automatisch.
Die Figur schaut nach rechts (3/4-Ansicht): Hinterkopf links, Gesicht rechts.
"""
from __future__ import annotations

import numpy as np

W, H = 32, 36

# Kopfgeometrie je Rasse (Pixelmittelpunkte: x+0.5 / y+0.5)
HEAD = {
    'human': dict(cx=16.0, cy=13.6, rx=4.7, ry=4.9, eye_y=14, eyes=(17, 19), mouth=(19, 16),
                  nose=[(21, 15)], neck=19),
    'dwarf': dict(cx=15.5, cy=20.0, rx=5.2, ry=4.9, eye_y=20, eyes=(16, 19), mouth=(19, 23),
                  nose=[(21, 21), (21, 22), (20, 22)], neck=25),
    'orc': dict(cx=15.6, cy=13.0, rx=5.4, ry=5.0, eye_y=13, eyes=(17, 20), mouth=(19, 16),
                nose=[(21, 14)], neck=18, jaw=True, tusks=[(17, 15), (20, 15)]),
    'gnome': dict(cx=16.0, cy=21.6, rx=5.3, ry=5.2, eye_y=22, eyes=(17, 20), mouth=(19, 25),
                  nose=[(22, 23), (22, 24), (21, 24)], neck=27, ears=True),
}


# ---------------------------------------------------------------- Masken
def grid():
    ys, xs = np.mgrid[0:H, 0:W]
    return xs + 0.5, ys + 0.5


def ellipse_mask(cx, cy, rx, ry):
    x, y = grid()
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def rect_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), bool)
    m[max(0, y0):min(H, y1 + 1), max(0, x0):min(W, x1 + 1)] = True
    return m


def poly_mask(pts):
    from pa import Canvas
    cv = Canvas(W, H)
    cv.poly(pts, (255, 255, 255, 255))
    return cv.a[:, :, 3] > 0


def dilate(m, n=1):
    out = m.copy()
    for _ in range(n):
        o = out.copy()
        o[1:, :] |= out[:-1, :]
        o[:-1, :] |= out[1:, :]
        o[:, 1:] |= out[:, :-1]
        o[:, :-1] |= out[:, 1:]
        out = o
    return out


def border_of(m):
    """Pixel direkt ausserhalb der Maske (4er-Nachbarschaft)."""
    return dilate(m, 1) & ~m


def light_levels(m, cx, cy, rx, ry, bias=0.0, strands=False):
    """Schattierung 1..3 fuer alle Pixel einer Maske (Licht von oben links)."""
    x, y = grid()
    nx = (x - cx) / rx
    ny = (y - cy) / ry
    light = -(0.55 * nx + 0.75 * ny) + bias
    lv = np.full((H, W), 2)
    lv[light > 0.45] = 3
    lv[light < -0.45] = 1
    # Rand unten rechts dunkler
    edge = m & ~np.roll(m, -1, axis=0) | m & ~np.roll(m, -1, axis=1)
    lv[edge & (light < 0.2)] = 1
    if strands:
        # feine Straehnen: jede 3. Spalte eine Stufe dunkler (nicht im Licht)
        sx = (np.floor(x).astype(int) + np.floor(y / 3).astype(int)) % 3 == 0
        lv[sx & (lv == 2) & (light < 0.2)] = 1
    lv[~m] = 0
    return lv


# ---------------------------------------------------------------- Koepfe
def skull(race):
    h = HEAD[race]
    m = ellipse_mask(h['cx'], h['cy'], h['rx'], h['ry'])
    if h.get('jaw'):
        # breiter Unterkiefer
        m |= ellipse_mask(h['cx'] + 0.8, h['cy'] + 2.4, h['rx'] - 0.2, h['ry'] - 1.6)
    return m


def head_parts(race):
    """Gibt (skin_levels, details) zurueck. details: Liste (x, y, zeichen)."""
    h = HEAD[race]
    m = skull(race)
    extra = np.zeros_like(m)
    for (nx_, ny_) in h.get('nose', []):
        extra[ny_, nx_] = True
    if h.get('ears'):
        # grosse spitze Gnomen-Ohren (hinten links sichtbar, vorne rechts angedeutet)
        extra |= poly_mask([(h['cx'] - h['rx'] + 1.0, h['cy'] - 0.5), (h['cx'] - h['rx'] - 3.2, h['cy'] - 3.4),
                            (h['cx'] - h['rx'] + 1.2, h['cy'] + 1.5)])
    if race == 'orc':
        extra |= poly_mask([(h['cx'] - h['rx'] + 0.6, h['cy'] - 0.6), (h['cx'] - h['rx'] - 1.6, h['cy'] - 2.4),
                            (h['cx'] - h['rx'] + 0.8, h['cy'] + 1.2)])
    full = m | extra
    lv = light_levels(full, h['cx'], h['cy'], h['rx'], h['ry'])
    # Nase immer mittel/hell, damit sie sich abhebt
    for (nx_, ny_) in h.get('nose', []):
        lv[ny_, nx_] = 2
    details = []
    ey = h['eye_y']
    for ex in h['eyes']:
        details.append((ex, ey, 'e'))
    if race == 'orc':
        # grimmige Brauen (Hautschatten ueber den Augen)
        for ex in h['eyes']:
            lv[ey - 1, ex] = 1
            lv[ey - 1, ex - 1] = 1
    mx, my = h['mouth']
    details.append((mx, my, 'm'))
    for (tx, ty) in h.get('tusks', []):
        details.append((tx, ty, 't'))
        details.append((tx, ty - 1, 't'))
    return lv, details


# ---------------------------------------------------------------- Frisuren
def _cap(race, grow=1.0, front=-0.62, back=0.35):
    """Haarkappe: oberer Kopfteil, hinten tiefer als vorne."""
    h = HEAD[race]
    x, y = grid()
    rx, ry = h['rx'] + grow, h['ry'] + grow
    nx = (x - h['cx']) / rx
    ny = (y - h['cy']) / ry
    inside = nx ** 2 + ny ** 2 <= 1.0
    thresh = front + (back - front) * (1 - (nx + 1) / 2)  # nx=-1 -> back, nx=+1 -> front
    return inside & (ny < thresh)


def _beard(race, length=5.0, width=4.2, top_off=2.2):
    h = HEAD[race]
    m = ellipse_mask(h['cx'] + 1.2, h['cy'] + top_off + length / 2, width, length / 2 + 0.6)
    x, y = grid()
    # oberhalb der Mundlinie nur an den Wangen
    m &= y > h['cy'] + top_off - 0.2
    return m


def hair_shape(race, style):
    """Gibt (maske, zusatzdetails) zurueck."""
    h = HEAD[race]
    cx, cy, rx, ry = h['cx'], h['cy'], h['rx'], h['ry']
    det = []
    if race == 'human':
        if style == 0:      # kurz, Seitenscheitel
            m = _cap(race, 1.0, -0.55, 0.45)
            m |= rect_mask(int(cx - rx), int(cy), int(cx - rx + 1), int(cy + 2))
        elif style == 1:    # lang bis ueber die Schultern
            m = _cap(race, 1.0, -0.5, 0.55)
            m |= poly_mask([(cx - rx - 1.0, cy - 1), (cx - 0.5, cy - 1), (cx - 1.5, cy + 8.5), (cx - rx - 1.5, cy + 8.5)])
            m &= ~poly_mask([(cx - 0.4, cy + 0.6), (cx + 6, cy - 0.5), (cx + 6, cy + 10), (cx - 1.8, cy + 10)])
        else:               # Dutt
            m = _cap(race, 1.0, -0.62, 0.3)
            m |= ellipse_mask(cx - 2.2, cy - ry - 0.8, 2.3, 2.0)
    elif race == 'dwarf':
        if style == 0:      # kurzes Haar + langer Vollbart
            m = _cap(race, 1.0, -0.6, 0.35)
            m |= _beard(race, 7.5, 4.6)
        elif style == 1:    # Haarkranz + geflochtener Bart mit Goldperlen
            ring = _cap(race, 1.0, 0.25, 0.4) & ~_cap(race, 1.0, -0.35, -0.2)
            m = ring & (grid()[0] < cx + 1.5)
            m |= _beard(race, 5.0, 4.2)
            m |= rect_mask(int(cx) + 1, int(cy + 7), int(cx) + 2, int(cy + 9))
            det += [(int(cx) + 1, int(cy + 7), 'Y'), (int(cx) + 2, int(cy + 7), 'y'),
                    (int(cx) + 1, int(cy + 9), 'Y'), (int(cx) + 2, int(cy + 9), 'y')]
        else:               # wilde Maehne + breiter kurzer Bart
            m = _cap(race, 1.8, -0.5, 0.65)
            m |= _beard(race, 4.6, 5.0)
    elif race == 'orc':
        if style == 0:      # Irokese
            m = poly_mask([(cx - 3.5, cy - ry + 0.8), (cx - 1.5, cy - ry - 3.2), (cx + 2.0, cy - ry - 2.6),
                           (cx + 2.8, cy - ry + 1.2)])
            m &= ~ellipse_mask(cx, cy, rx - 0.2, ry - 0.2) | (grid()[1] < cy - ry + 1.4)
        elif style == 1:    # langer Zopf nach hinten + Kinnbart
            m = _cap(race, 0.9, -0.45, 0.45)
            m |= poly_mask([(cx - rx - 0.5, cy - 1.0), (cx - rx + 1.6, cy - 1.0), (cx - rx - 0.4, cy + 9.0),
                            (cx - rx - 2.2, cy + 9.0)])
            m |= ellipse_mask(cx + 2.0, cy + 5.2, 1.6, 1.5)
        else:               # Haarknoten + dichter Bart
            m = _cap(race, 0.8, -0.7, 0.2)
            m |= ellipse_mask(cx - 1.0, cy - ry - 1.2, 1.8, 1.6)
            m |= _beard(race, 3.6, 4.2, top_off=3.2)
    else:  # gnome
        if style == 0:      # zwei Zoepfe
            m = _cap(race, 1.0, -0.55, 0.3)
            m |= ellipse_mask(cx - rx - 0.6, cy + 2.2, 1.8, 2.4)
            m |= ellipse_mask(cx + rx - 0.4, cy - 2.6, 1.4, 1.3)
        elif style == 1:    # Tolle, hoch toupiert
            m = _cap(race, 1.0, -0.55, 0.3)
            m |= ellipse_mask(cx - 0.3, cy - ry - 1.6, 3.4, 3.2)
            m |= ellipse_mask(cx + 1.6, cy - ry - 3.6, 1.8, 1.6)
        else:               # kurz, zerzaust + Schnurrbart
            m = _cap(race, 1.2, -0.45, 0.35)
            x, y = grid()
            spikes = ((np.floor(x).astype(int) % 2) == 0) & (y < cy - ry - 0.2) & (y > cy - ry - 1.4) \
                & (x > cx - rx) & (x < cx + rx - 1)
            m |= spikes
            m |= rect_mask(h['mouth'][0] - 1, h['mouth'][1] - 1, h['mouth'][0] + 1, h['mouth'][1] - 1)
    return m, det


def hair_levels(race, style):
    h = HEAD[race]
    m, det = hair_shape(race, style)
    lv = light_levels(m, h['cx'] - 0.5, h['cy'] - 1.5, h['rx'] + 2, h['ry'] + 3, bias=0.15, strands=True)
    return m, lv, det


# ---------------------------------------------------------------- Helme
def helmet(race):
    """Helm des Kriegers: gibt (maske, farbzeichen je Pixel) zurueck."""
    h = HEAD[race]
    cx, cy, rx, ry = h['cx'], h['cy'], h['rx'], h['ry']
    m = _cap(race, 1.0, -0.12, 0.05)
    x, y = grid()
    rim_y = int(np.max(np.where(m)[0])) if m.any() else 0
    chars = np.full((H, W), '.', dtype='<U1')
    lv = light_levels(m, cx - 1, cy - 2, rx + 1, ry + 1, bias=0.2)
    chars[(lv == 3)] = 'S'
    chars[(lv == 2)] = 's'
    chars[(lv == 1)] = 'z'
    # Rand unten
    rim = m & ~np.roll(m, -1, axis=0)
    chars[rim & m] = 'z'
    # Nasenschutz vorne
    nx_ = h['eyes'][1] - 1
    for yy in range(rim_y, rim_y + 3):
        m[yy, nx_] = True
        chars[yy, nx_] = 's'
    if race in ('orc', 'dwarf'):
        # Hoerner
        side = -1
        base_x = cx - rx * 0.6
        horn = poly_mask([(base_x, cy - ry + 0.5), (base_x - 3.0, cy - ry - 3.0), (base_x - 1.4, cy - ry + 0.2)])
        horn2 = poly_mask([(cx + rx * 0.5, cy - ry + 0.2), (cx + rx * 0.5 + 2.6, cy - ry - 3.2), (cx + rx * 0.5 + 1.2, cy - ry + 0.4)])
        for hm in (horn, horn2):
            hm &= ~m
            m |= hm
            chars[hm] = 't'
    if race == 'gnome':
        # Topfhelm mit Zipfel
        tip = ellipse_mask(cx, cy - ry - 1.2, 1.2, 1.2) & ~m
        m |= tip
        chars[tip] = 'S'
    if race == 'human':
        crest = rect_mask(int(cx) - 1, int(cy - ry - 1.6), int(cx) + 1, int(cy - ry - 1.6)) & ~m
        m |= crest
        chars[crest] = 'R'
    return m, chars
