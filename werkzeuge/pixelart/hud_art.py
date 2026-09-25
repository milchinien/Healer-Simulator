"""Untere Bedienleiste und linke NPC-Saeule des Hauptbildschirms (WoW-inspiriert).

Gravierter dunkler Schieferstein mit Goldbeschlaegen. Alle Fassungen (Gruppenfenster-Mulde,
Mana-Rinne, Aktionsplaetze, Mikromenue-Platte, NPC-Nischen) sind pixelgenau an den Stellen
eingelassen, an denen das Spiel die Elemente zeichnet. Die Positionen stehen in LAYOUT und
werden als data/hud_layout.json ausgegeben - das Spiel liest sie von dort.

Aufruf: python hud_art.py            (schreibt nach ../../healer-simulator)
"""
from __future__ import annotations

import json
import math
import os
import sys

from pa import Canvas, c, from_grid, mix

# ---------------------------------------------------------------- Layout (absolute Bildschirmkoordinaten)
PANEL_Y = 238            # Bild beginnt hier (Endkappen der EP-Leiste ragen ueber die Kante)
EDGE_Y = 247             # Oberkante der Leiste (Kontur), darunter EP-Rinne
LAYOUT = {
    'panel': {'x': 0, 'y': PANEL_Y, 'w': 640, 'h': 360 - PANEL_Y, 'edge_y': EDGE_Y},
    'cast': {'x': 225, 'y': 234, 'w': 190, 'h': 11},       # Castbalken ueber der EP-Leiste
    'xp': {'x': 16, 'y': 249, 'w': 608, 'h': 8},           # EP-Leiste zwischen Kampfszene und Gruppenfenster
    'tray': {'x': 16, 'y': 259, 'w': 608, 'h': 40},          # Gruppenfenster (Rahmen 40 px hoch)
    'mana': {'x': 16, 'y': 302, 'w': 608, 'h': 11},
    'bar': {'x': 16, 'y': 317, 'slot': 40, 'gap': 2, 'count': 12},
    'micro': {'x': 524, 'y': 317, 'cell': 20, 'cols': 5, 'rows': 2},
    'column': {'x': 0, 'y': 20, 'w': 44, 'h': EDGE_Y - 20,
               'niches': [[5, 26, 34, 34], [5, 66, 34, 34], [5, 106, 34, 34]], 'gold': [3, 231, 38, 13]},
}

# ---------------------------------------------------------------- Farben
INK = c('#0a0710')
ST_DD = c('#15111c')     # tiefe Fugen / Mulden
ST_D = c('#221c2b')      # Stein dunkel
ST = c('#2d2638')        # Stein
ST_L = c('#3b3348')      # Stein hell
ST_LL = c('#4d4460')     # Lichtkante
GV_D = c('#171220')      # Gravur Schattenseite
GV_L = c('#453c55')      # Gravur Lichtseite
G_DD = c('#4e3516')
G_D = c('#8a6424')
G_M = c('#c99a3a')
G = c('#f2c14e')
G_L = c('#ffe08a')
GEM_D = c('#7a4a0e')
GEM = c('#f0b030')
GEM_L = c('#fff2b0')
IRON_D = c('#1a1822')
IRON = c('#4a4656')
IRON_L = c('#8a8698')
IRON_LL = c('#c4c0d0')


# ---------------------------------------------------------------- Grundbausteine
def stone(cv: Canvas, x, y, w, h, seed=0):
    """Ruhige Steinflaeche: zwei Toene in breiten Lagen, Quaderfugen, keine Sprenkel."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            band = ((yy // 5) + (xx // 37) + seed) % 3
            cv.px(xx, yy, ST if band else ST_D)


def carve_line_h(cv: Canvas, x0, x1, y):
    """Eingravierte Linie: dunkle Rille, darunter Lichtkante."""
    cv.hline(x0, x1, y, GV_D)
    cv.hline(x0, x1, y + 1, GV_L)


def carve_line_v(cv: Canvas, x, y0, y1):
    cv.vline(x, y0, y1, GV_D)
    cv.vline(x + 1, y0, y1, GV_L)


def recess(cv: Canvas, x, y, w, h, fill=ST_DD):
    """Eingelassene Mulde: Innenflaeche + Schatten oben/links, Lichtkante unten/rechts (1 px Rand aussen)."""
    cv.rect(x, y, w, h, fill)
    cv.hline(x - 1, x + w, y - 1, INK)
    cv.vline(x - 1, y - 1, y + h, INK)
    cv.hline(x - 1, x + w, y + h, ST_LL)
    cv.vline(x + w, y - 1, y + h, ST_LL)
    cv.px(x - 1, y + h, ST_L)
    cv.px(x + w, y - 1, ST_L)


def rivet(cv: Canvas, x, y):
    """Goldniete 3x3 mit Glanzpunkt."""
    cv.rect(x, y, 3, 3, G_M)
    cv.px(x, y, G_L)
    cv.px(x + 1, y, G)
    cv.px(x, y + 1, G)
    cv.px(x + 2, y + 2, G_D)
    cv.px(x + 2, y + 1, G_D)
    cv.px(x + 1, y + 2, G_D)


def gold_rail(cv: Canvas, x0, x1, y, notch=6):
    """Goldleiste 2 px hoch mit eingekerbten Kerben (Einkerbungen)."""
    cv.hline(x0, x1, y, G)
    cv.hline(x0, x1, y + 1, G_D)
    for x in range(x0 + 3, x1 - 1, notch):
        cv.px(x, y, G_DD)
        cv.px(x, y + 1, INK)
        cv.px(x + 1, y, G_L)


def gem(cv: Canvas, cx, cy):
    """Heiliger Bernstein in Goldfassung (7x9)."""
    pts = [(0, -4), (3, -1), (3, 1), (0, 4), (-3, 1), (-3, -1)]
    cv.poly([(cx + px + 0.5, cy + py + 0.5) for px, py in [(0, -5), (4, -1), (4, 2), (0, 6), (-3, 2), (-3, -1)]], G_D)
    cv.poly([(cx + px + 0.5, cy + py + 0.5) for px, py in pts], GEM)
    cv.px(cx - 1, cy - 2, GEM_L)
    cv.px(cx, cy - 2, GEM_L)
    cv.px(cx - 1, cy - 1, GEM_L)
    cv.px(cx + 1, cy + 2, GEM_D)
    cv.px(cx + 2, cy + 1, GEM_D)
    cv.px(cx, cy + 3, GEM_D)


def lattice(cv: Canvas, x, y, w, h, step=10):
    """Gravierte Rautenranke (Hintergrund der Gruppenfenster-Mulde): Rillen mit Lichtkante."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            u = (xx - x + (yy - y)) % step
            v = (xx - x - (yy - y)) % step
            if u == 0 or v == 0:
                cv.px(xx, yy, GV_D)
            elif u == 1 or v == 1:
                cv.px(xx, yy, c('#2a2336'))
    # Goldpunkte an den Kreuzungen der Mittellinie
    my = y + h // 2
    for xx in range(x + (step - (my - y) % step) % step, x + w, step):
        cv.px(xx, my, G_DD)
    # Einfassung: feine Goldlinie innen
    cv.hline(x, x + w - 1, y, G_DD)
    cv.hline(x, x + w - 1, y + h - 1, G_DD)
    cv.vline(x, y, y + h - 1, G_DD)
    cv.vline(x + w - 1, y, y + h - 1, G_DD)
    for (cx, cy) in [(x, y), (x + w - 4, y), (x, y + h - 4), (x + w - 4, y + h - 4)]:
        cv.rect(cx, cy, 4, 4, G_D)
        cv.px(cx + 1, cy + 1, G_L)
        cv.px(cx + 2, cy + 2, G_M)


def xp_band(cv: Canvas, oy):
    """EP-Rinne ueber die ganze Breite: Goldrahmen mit Kerben, dunkle Rinne, Endkappen mit Fluegeln und Bernstein."""
    xp = LAYOUT['xp']
    y0 = xp['y'] - oy
    cv.hline(0, 639, y0 - 2, INK)
    gold_rail(cv, 0, 639, y0 - 1, notch=8)
    cv.hline(0, 639, y0 - 1 + 1, G_D)
    cv.rect(xp['x'], y0, xp['w'], xp['h'], c('#140c1e'))
    cv.hline(xp['x'], xp['x'] + xp['w'] - 1, y0, INK)
    cv.hline(0, 639, y0 + xp['h'], G_D)
    # Endkappen links und rechts
    wing = from_grid([
        '...............kk.',
        '...........kkkkLLk',
        '........kkkLLLLMk.',
        '......kkLLLMMMMk..',
        '....kkLLMMMMDDk...',
        '...kLLMMMDDkDk....',
        '..kLMMMDkDkDk.....',
        '.kLMMDkDkDk.......',
        'kLMMDkDkk.........',
    ], {'k': INK, 'L': G_L, 'M': G_M, 'D': G_D})
    for side, x0 in ((-1, 0), (1, xp['x'] + xp['w'])):
        cv.rect(x0, y0, 16, xp['h'], G_M)
        cv.hline(x0, x0 + 15, y0, G_L)
        cv.hline(x0, x0 + 15, y0 + xp['h'] - 1, G_DD)
        cv.vline(x0 if side < 0 else x0 + 15, y0 - 2, y0 + xp['h'], INK)
        cx = x0 + 8
        cv.circle(cx - 0.5, y0 + 3.5, 5.6, INK)
        cv.circle(cx - 0.5, y0 + 3.5, 4.6, G_D)
        gem(cv, cx, y0 + 4)
        if side < 0:
            cv.paste(wing, cx + 2, y0 - 10)
        else:
            cv.paste(wing, cx - 2 - wing.w, y0 - 10, flip=True)


# ---------------------------------------------------------------- Untere Leiste
def bottom_panel() -> Canvas:
    L = LAYOUT
    ph = L['panel']['h']
    cv = Canvas(640, ph)
    oy = PANEL_Y                     # Umrechnung absolut -> Bild
    top = EDGE_Y - oy
    stone(cv, 0, top, 640, ph - top, seed=1)
    xp_band(cv, oy)

    # Seitensaeulen (unter der EP-Leiste)
    ptop = LAYOUT['tray']['y'] - 1 - oy
    for x0 in (0, 625):
        pillar(cv, x0, ptop, 15, ph - ptop - 1)

    # Gruppenfenster-Mulde mit Rautenranke
    t = L['tray']
    recess(cv, t['x'], t['y'] - oy, t['w'], t['h'])
    lattice(cv, t['x'], t['y'] - oy, t['w'], t['h'], step=10)
    # Gravierte Sonne in der Mitte (hinter den Rahmen, bei kleiner Gruppe sichtbar)
    sun(cv, 320, t['y'] - oy + t['h'] // 2)

    # Stein zwischen Mulde und Mana-Rinne: Kerbenfries
    y_sep = t['y'] + t['h'] + 1 - oy
    for x in range(18, 622, 4):
        cv.px(x, y_sep, GV_D)

    # Mana-Rinne mit Goldkappen an beiden Enden
    m = L['mana']
    recess(cv, m['x'], m['y'] - oy, m['w'], m['h'], fill=c('#0e1428'))
    for ex in (m['x'] - 4, m['x'] + m['w']):
        yy = m['y'] - oy
        cv.rect(ex, yy - 2, 4, m['h'] + 4, G_M)
        cv.vline(ex, yy - 2, yy + m['h'] + 1, G)
        cv.vline(ex + 3, yy - 2, yy + m['h'] + 1, G_DD)
        cv.hline(ex, ex + 3, yy - 2, G_L)
        cv.rect(ex + 1, yy + m['h'] // 2 - 1, 2, 3, c('#6ab0ff'))
        cv.px(ex + 1, yy + m['h'] // 2 - 1, c('#d8f0ff'))

    # Doppelte Kerbenlinie zwischen Mana und Aktionsleiste
    b = L['bar']
    y_bar = b['y'] - oy
    carve_line_h(cv, 16, 623, y_bar - 3)

    # Fassungen der Aktionsplaetze (Rahmen kommt aus dem Slot-Bild), Nieten dazwischen
    for i in range(b['count']):
        x = b['x'] + i * (b['slot'] + b['gap'])
        recess(cv, x, y_bar, b['slot'], b['slot'], fill=ST_DD)
    for i in range(1, b['count']):
        x = b['x'] + i * (b['slot'] + b['gap']) - b['gap']
        cv.vline(x, y_bar, y_bar + b['slot'] - 1, G_DD)
        cv.vline(x + 1, y_bar, y_bar + b['slot'] - 1, G_D)
        cv.px(x, y_bar + b['slot'] // 2, G)
        cv.px(x + 1, y_bar + b['slot'] // 2, G_L)

    # Mikromenue-Platte: Bronze mit runden Mulden
    mi = L['micro']
    mw, mh = mi['cols'] * mi['cell'], mi['rows'] * mi['cell']
    mx, my = mi['x'], mi['y'] - oy
    cv.rect(mx - 1, my - 1, mw + 2, mh + 2, INK)
    cv.rect(mx, my, mw, mh, c('#3a2c1e'))
    cv.hline(mx, mx + mw - 1, my, c('#6a5034'))
    cv.vline(mx, my, my + mh - 1, c('#5a4430'))
    for r in range(mi['rows']):
        for col in range(mi['cols']):
            ccx = mx + col * mi['cell'] + mi['cell'] / 2 - 0.5
            ccy = my + r * mi['cell'] + mi['cell'] / 2 - 0.5
            cv.circle(ccx, ccy, 8.6, c('#1c140e'))
            cv.circle(ccx, ccy, 7.6, c('#2a1f16'))
            # Lichtkante unten rechts der Mulde
            for a in range(0, 90, 15):
                ang = math.radians(a)
                cv.px(round(ccx + math.cos(ang) * 8.3), round(ccy + math.sin(ang) * 8.3), c('#6a5034'))
    for (rx, ry) in [(mx + 1, my + 1), (mx + mw - 4, my + 1), (mx + 1, my + mh - 4), (mx + mw - 4, my + mh - 4)]:
        rivet(cv, rx, ry)

    # Unterkante
    cv.hline(0, 639, ph - 2, G_DD)
    cv.hline(0, 639, ph - 1, INK)
    return cv


def pillar(cv: Canvas, x, y, w, h):
    """Verzierte Seitensaeule: Goldkapitell, Kanneluren, Bernstein, Sockel."""
    cv.rect(x, y, w, h, ST_D)
    cv.vline(x, y, y + h - 1, ST_LL)
    cv.vline(x + w - 1, y, y + h - 1, INK)
    # Kanneluren (senkrechte Rillen)
    for gx in range(x + 3, x + w - 3, 4):
        carve_line_v(cv, gx, y + 8, y + h - 9)
    # Kapitell
    cv.rect(x, y, w, 6, G_M)
    cv.hline(x, x + w - 1, y, G_L)
    cv.hline(x, x + w - 1, y + 5, G_DD)
    cv.hline(x + 1, x + w - 2, y + 2, G_D)
    for kx in range(x + 2, x + w - 1, 3):
        cv.px(kx, y + 3, G_L)
    # Sockel
    cv.rect(x, y + h - 6, w, 6, G_M)
    cv.hline(x, x + w - 1, y + h - 6, G_L)
    cv.hline(x, x + w - 1, y + h - 1, G_DD)
    cv.hline(x + 1, x + w - 2, y + h - 3, G_D)
    # Bernstein in der Mitte, von Goldbeschlag gehalten
    cy = y + h // 2
    cv.rect(x + 2, cy - 7, w - 4, 15, G_D)
    cv.rect(x + 3, cy - 6, w - 6, 13, INK)
    gem(cv, x + w // 2, cy)


def sun(cv: Canvas, cx, cy):
    """Eingravierte Sonne (Symbol des Lichts) in der Mulde."""
    for a in range(12):
        ang = a * math.pi / 6
        for rr in range(8, 14):
            cv.px(round(cx + math.cos(ang) * rr * 1.6), round(cy + math.sin(ang) * rr), GV_L if rr % 2 else GV_D)
    for a in range(48):
        ang = a * math.pi / 24
        cv.px(round(cx + math.cos(ang) * 10), round(cy + math.sin(ang) * 6), GV_L)
        cv.px(round(cx + math.cos(ang) * 11), round(cy + math.sin(ang) * 7), GV_D)


# ---------------------------------------------------------------- Linke NPC-Saeule
def left_column() -> Canvas:
    col = LAYOUT['column']
    w, h = col['w'], col['h']
    cv = Canvas(w, h)
    stone(cv, 0, 0, w, h, seed=2)
    # rechte Kante: Goldleiste senkrecht mit Kerben
    cv.vline(w - 3, 0, h - 1, G)
    cv.vline(w - 2, 0, h - 1, G_D)
    cv.vline(w - 1, 0, h - 1, INK)
    for yy in range(3, h - 1, 6):
        cv.px(w - 3, yy, G_DD)
        cv.px(w - 2, yy, INK)
    # Nischen fuer die Portraets (Rundbogen oben)
    for nx, ny, nw, nh in col['niches']:
        ny -= col['y']
        recess(cv, nx - 1, ny - 1, nw + 2, nh + 2)
        cv.hline(nx - 2, nx + nw + 1, ny + nh + 2, G_D)
        cv.hline(nx - 2, nx + nw + 1, ny + nh + 3, G_DD)
        rivet(cv, nx - 3, ny + nh + 1)
        rivet(cv, nx + nw, ny + nh + 1)
    # Gravuren zwischen und unter den Nischen
    last = col['niches'][-1]
    y0 = last[1] - col['y'] + last[3] + 8
    gx, gy, gw, gh = col['gold']
    gy -= col['y']
    for yy in range(y0, gy - 6, 6):
        carve_line_h(cv, 6, w - 8, yy)
    # Goldplakette fuer die Goldanzeige
    cv.rect(gx - 1, gy - 1, gw + 2, gh + 2, INK)
    cv.rect(gx, gy, gw, gh, c('#2a1f16'))
    cv.hline(gx, gx + gw - 1, gy, G_D)
    cv.hline(gx, gx + gw - 1, gy + gh - 1, G_M)
    return cv


# ---------------------------------------------------------------- Aktionsplatz (WoW-artig)
def slot_frame() -> Canvas:
    """Metallrahmen 40x40, Mitte frei: wird UEBER das Zauber-Icon gelegt."""
    s = 40
    cv = Canvas(s, s)
    cv.frame(0, 0, s, s, INK)
    # Bevel: oben/links hell, unten/rechts dunkel
    cv.hline(1, s - 2, 1, IRON_L)
    cv.vline(1, 1, s - 2, IRON_L)
    cv.hline(1, s - 2, s - 2, IRON_D)
    cv.vline(s - 2, 1, s - 2, IRON_D)
    cv.px(1, 1, IRON_LL)
    cv.px(2, 1, IRON_LL)
    cv.px(1, 2, IRON_LL)
    # innere Schattenkante ueber dem Icon-Rand (Tiefe)
    cv.hline(2, s - 3, 2, (0, 0, 0, 150))
    cv.vline(2, 3, s - 3, (0, 0, 0, 150))
    cv.hline(3, s - 3, s - 3, (255, 255, 255, 40))
    cv.vline(s - 3, 3, s - 4, (255, 255, 255, 40))
    # Eckbeschlaege
    for (x, y) in [(0, 0), (s - 3, 0), (0, s - 3), (s - 3, s - 3)]:
        cv.rect(x, y, 3, 3, IRON)
        cv.px(x + 1, y + 1, IRON_LL)
    return cv


def slot_empty() -> Canvas:
    """Leerer Platz: dunkle, gravierte Vertiefung (unter dem Rahmen)."""
    s = 40
    cv = Canvas(s, s)
    cv.rect(0, 0, s, s, c('#120e18'))
    cx = cy = s / 2 - 0.5
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy)
            if d < 17:
                cv.px(x, y, mix('#1a1522', '#120e18', min(1.0, d / 17)))
    # eingravierter Kreis mit Kreuz (Priester)
    for a in range(64):
        ang = a * math.pi / 32
        cv.px(round(cx + math.cos(ang) * 9), round(cy + math.sin(ang) * 9), c('#241e2e'))
        cv.px(round(cx + math.cos(ang) * 10), round(cy + math.sin(ang) * 10), c('#0c0910'))
    cv.rect(19, 13, 2, 14, c('#221c2b'))
    cv.rect(14, 18, 12, 2, c('#221c2b'))
    return cv


def slot_glow(col, strength) -> Canvas:
    """Leuchtender Innenrand (Maus drueber / gedrueckt), wird ueber alles gelegt."""
    s = 40
    cv = Canvas(s, s)
    cc = c(col)
    for i, a in enumerate([strength, strength * 0.55, strength * 0.25]):
        cv.frame(2 + i, 2 + i, s - 4 - 2 * i, s - 4 - 2 * i, (cc[0], cc[1], cc[2], int(255 * a)))
    return cv


# ---------------------------------------------------------------- Ausgabe
def build(root):
    def out(rel):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p
    bottom_panel().save(out('assets/gfx/hud/bottom_panel.png'))
    left_column().save(out('assets/gfx/hud/left_column.png'))
    slot_frame().save(out('assets/gfx/hud/slot_frame.png'))
    slot_empty().save(out('assets/gfx/hud/slot_empty.png'))
    slot_glow('#fff6d0', 0.55).save(out('assets/gfx/hud/slot_hover.png'))
    slot_glow('#ffd84a', 0.95).save(out('assets/gfx/hud/slot_pressed.png'))
    with open(out('data/hud_layout.json'), 'w', encoding='utf-8') as f:
        json.dump(LAYOUT, f, indent=1)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', 'healer-simulator'))
