"""Szenen Version 2: logisch aufgebaute Welten mit animierten Elementen.

Jede Szene liefert ein Dict:
  layers  : {'bg': Canvas, 'fg': Canvas (optional)}
  sprites : {name: Canvas}  - eigene Spritesheets der Szene (Wolken, Fahnen, Zahnraeder ...)
  props   : Liste animierter Elemente fuer das Spiel (siehe SceneBackdrop in Godot)
  stand   : Standpunkt der Figur (x, y)
"""
from __future__ import annotations

import math

import numpy as np

import props as P
import scenery as S
import world as Wd
from pa import Canvas, c, mix, shade, BAYER4, rng

W, H = 640, 360


def _clouds(name, specs):
    """specs: Liste (band, farben(hell, mittel, dunkel), dichte, skala, geschwindigkeit, seed, hoehe)."""
    sprites, props = {}, []
    for i, (band, cols, dens, scale, speed, seed, h) in enumerate(specs):
        key = f'{name}_clouds{i}'
        sprites[key] = P.cloud_frames(W, h, seed, band, *cols, density=dens, scale=scale, frames=12)
        props.append({'type': 'clouds', 'tex': key, 'frames': 12, 'fps': 1.6, 'speed': speed, 'y': 0, 'h': h})
    return sprites, props


def _lamp_props(flame, pool_at=None, pool='pool_lamp', glow='glow_lamp', alpha=0.8):
    out = [{'type': 'flame', 'x': flame[0], 'y': flame[1]},
           {'type': 'glow', 'tex': glow, 'x': flame[0], 'y': flame[1], 'alpha': alpha, 'flicker': 0.12}]
    if pool_at:
        out.append({'type': 'glow', 'tex': pool, 'x': pool_at[0], 'y': pool_at[1], 'alpha': 0.75, 'flicker': 0.1})
    return out


# ============================================================ Charakterauswahl: Marktplatz am Abend
def charselect():
    bg = Canvas(W, H)
    sprites, props = {}, []
    S.sky(bg, ['#131031', '#261f4e', '#4e3266', '#95496a', '#dc7e5c', '#f6b877'], 0, 214)
    S.stars(bg, 11, 120, 90)
    S.glow_disc(bg, 318, 46, 8, 24, '#fff1d0', '#ffd49a')
    bg.circle(315, 43, 2, '#f4dcb8')
    bg.circle(321, 49, 1, '#f0d4ae')
    # Ferne Berge
    S.peaks(bg, [(40, 158, 90), (170, 172, 80), (470, 150, 110), (600, 166, 90)],
            '#3a2c5a', '#56427c', '#2c2248', 214, seed=2)
    # Burghuegel mit Serpentinenstrasse
    hill = [(210, 214), (262, 176), (300, 160), (380, 158), (420, 172), (480, 214)]
    bg.poly(hill, '#2e2448')
    bg.poly([(300, 160), (380, 158), (420, 172), (360, 174)], '#382c56')
    road = [(318, 212), (360, 200), (322, 188), (356, 176), (338, 165)]
    for a, b in zip(road, road[1:]):
        bg.line(a[0], a[1], b[0], b[1], '#5a4870')
    castle_lights = Wd.castle(bg, 282, 162, '#231a3c', '#3a2e5c', '#ffcf6a')
    for (x, y) in road[1:]:
        props.append({'type': 'glow', 'tex': 'glow_tiny', 'x': x, 'y': y - 1, 'alpha': 0.9, 'flicker': 0.2})
        bg.px(x, y - 1, '#ffd46b')
    for (x, y) in castle_lights[:6]:
        props.append({'type': 'glow', 'tex': 'glow_tiny', 'x': x, 'y': y, 'alpha': 0.6, 'flicker': 0.08})
    # Entfernte Daecher der Unterstadt
    r = rng(4)
    x = 100
    while x < 560:
        w_ = r.randint(12, 22)
        h_ = r.randint(10, 20)
        base = 236
        bg.rect(x, base - h_, w_, h_ + 20, '#2a2042')
        bg.poly([(x - 2, base - h_), (x + w_ + 1, base - h_), (x + w_ / 2, base - h_ - w_ * 0.5)], '#221a36')
        for _ in range(r.randint(0, 2)):
            bg.rect(x + r.randint(2, w_ - 4), base - h_ + r.randint(3, max(4, h_ - 4)), 2, 2, '#e8a860')
        x += w_ + r.randint(-3, 2)
    # Gasse zur Burg (zwischen den hinteren Haeusern) - laeuft zum Fluchtpunkt
    vp = (320, 214)
    bg.poly([(296, 252), (344, 252), (326, 222), (314, 222)], '#3a3048')
    for k in range(4):
        y = 250 - k * 7
        bg.hline(int(296 + (314 - 296) * k / 4), int(344 - (344 - 326) * k / 4), y, '#2a2236')
    Wd.side_facade(bg, 296, 312, 252, 226, 62, 30, _pal_a(), windows=[(0.4, True)], seed=9, roof_near=10, roof_far=6)
    Wd.side_facade(bg, 344, 328, 252, 226, 62, 30, _pal_b(), windows=[(0.5, True)], seed=10, roof_near=10, roof_far=6)
    far_lamp = Wd.wall_lamp(bg, 322, 232)
    props.append({'type': 'glow', 'tex': 'glow_tiny', 'x': far_lamp[0], 'y': far_lamp[1], 'alpha': 0.9, 'flicker': 0.15})
    Wd.bunting(bg, 294, 196, 346, 196, sag=7, seed=1)
    # Hintere Haeuserreihe (steht an der Rueckseite des Platzes)
    chim = []
    lights = []
    for (hx, hw, hh, pal, sd, sign) in [(118, 44, 56, _pal_a(), 1, None), (162, 40, 64, _pal_b(), 2, None),
                                        (202, 46, 52, _pal_a(), 3, [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (1, 2), (1, 3)]),
                                        (248, 46, 60, _pal_c(), 4, None),
                                        (348, 50, 58, _pal_b(), 5, None), (398, 44, 66, _pal_a(), 6, None),
                                        (442, 48, 54, _pal_c(), 7, None), (490, 50, 62, _pal_b(), 8, None)]:
        li, ch = Wd.townhouse(bg, hx, 252, hw, hh, pal, seed=sd, sign=sign)
        lights += li
        chim += ch
    # Seitliche Haeuser in Perspektive (umschliessen den Platz)
    left_lights = Wd.side_facade(bg, 0, 118, 318, 252, 206, 88, _pal_b(),
                                 windows=[(0.1, True), (0.27, False), (0.44, True), (0.62, True), (0.8, False)],
                                 door_t=0.55, seed=11, roof_near=28, roof_far=14)
    right_lights = Wd.side_facade(bg, 639, 540, 318, 252, 206, 88, _pal_a(),
                                  windows=[(0.1, False), (0.27, True), (0.44, True), (0.62, False), (0.8, True)],
                                  door_t=0.36, seed=12, roof_near=28, roof_far=14)
    # Platz
    Wd.perspective_cobbles(bg, 252, H, vp, '#463a50', '#5e5068', '#241c2c', seed=9)
    # Uebergaenge Platz <-> Seitenhaeuser (Bordstein)
    for i in range(119):
        t = i / 118
        y = int(318 + (252 - 318) * t)
        bg.px(i, y, '#2a2032')
        bg.px(639 - i, y, '#2a2032')
    Wd.mosaic_circle(bg, 226, 296, 54, 12, '#7a6c84', '#4a3e56', '#f2c14e', '#b8862e')
    # Marktstand und Brunnenrand links vorne
    Wd.market_stall(bg, 22, 334, w=60, seed=3)
    # Laternen
    lamp_l = Wd.street_lamp(bg, 112, 316, h=54)
    lamp_r = Wd.street_lamp(bg, 356, 312, h=52)
    props += _lamp_props(lamp_l, (112, 316))
    props += _lamp_props(lamp_r, (356, 312))
    # Wandlampen an Tueren + Fensterlicht
    for L in (left_lights, right_lights):
        for item in L:
            if item[0] == 'door':
                _, dx, dy, sc = item
                p = Wd.wall_lamp(bg, dx + 4, dy)
                props.append({'type': 'glow', 'tex': 'glow_small', 'x': p[0], 'y': p[1], 'alpha': 0.8, 'flicker': 0.12})
    for item in lights:
        if item[0] == 'door':
            _, dx, dy = item
            p = Wd.wall_lamp(bg, dx + 5, dy + 2)
            props.append({'type': 'glow', 'tex': 'glow_small', 'x': p[0], 'y': p[1], 'alpha': 0.75, 'flicker': 0.12})
        else:
            props.append({'type': 'glow', 'tex': 'glow_window', 'x': item[0], 'y': item[1], 'alpha': 0.35, 'flicker': 0.04})
    for (x, y) in chim[::2]:
        props.append({'type': 'particles', 'kind': 'smoke', 'x': x, 'y': y})
    props.append({'type': 'particles', 'kind': 'fireflies_town', 'x': 330, 'y': 190, 'w': 150, 'h': 30})
    props.append({'type': 'particles', 'kind': 'fireflies_town', 'x': 60, 'y': 300, 'w': 60, 'h': 30})
    S.vignette(bg, 0.55)
    cs, cp = _clouds('charselect', [
        ((6, 70), ('#8a5a8a', '#5e3e70', '#3e2a56'), 0.58, 70, 1.2, 31, 80),
        ((30, 120), ('#f7b08a', '#b8667a', '#6a3f66'), 0.57, 60, 2.6, 32, 130),
        ((110, 170), ('#ffc890', '#d0787a', '#8a4a6a'), 0.62, 46, 4.5, 33, 175),
    ])
    sprites.update(cs)
    props = cp + props
    return {'layers': {'bg': bg}, 'sprites': sprites, 'props': props, 'stand': (226, 296)}


def _pal_a():
    return {'wall': '#76667a', 'wall_d': '#5a4c62', 'stone': '#5e5466', 'stone_d': '#463e50', 'timber': '#2a1c26',
            'roof': '#5e2836', 'roof_d': '#421a26', 'shutter': '#3e4a6a'}


def _pal_b():
    return {'wall': '#84746c', 'wall_d': '#665850', 'stone': '#62586a', 'stone_d': '#4a4254', 'timber': '#2e2026',
            'roof': '#40345a', 'roof_d': '#2c2440', 'shutter': '#5a3a3a'}


def _pal_c():
    return {'wall': '#8a7a62', 'wall_d': '#6a5c4a', 'stone': '#5a5464', 'stone_d': '#443e4c', 'timber': '#2e2020',
            'roof': '#6a3a2a', 'roof_d': '#4a2618', 'shutter': '#3a5a3a'}
