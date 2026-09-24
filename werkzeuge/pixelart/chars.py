"""Charakter-Sprites: Rassen, Klassen-Kleidung, Frisuren.

Aufbau in Ebenen (werden im Spiel per Palette-Shader eingefaerbt):
  skin     - Graustufen-Index (0=Kontur, 1=Schatten, 2=Basis, 3=Licht) -> Hautfarbe
  hair     - Graustufen-Index -> Haarfarbe
  outfit   - feste Farben (Klassenkleidung, Augen, Details)
  headgear - feste Farben ueber den Haaren (z.B. Helm des Kriegers)

Rahmen: 32 x 36 Pixel, Fuesse auf Zeile 35, Figur schaut nach rechts (3/4-Ansicht).
Idle-Animation: 4 Frames (Atmen: Oberkoerper 0,0,1,1 Pixel nach unten).
"""
from __future__ import annotations

from pa import Canvas, c

FW, FH = 32, 36
FRAMES = 4
BREATH = [0, 0, 1, 1]

# Graustufen-Indexwerte (im Rotkanal), vom Shader zurueckgerechnet: idx = round(r / 85)
IDX = {0: (0, 0, 0, 255), 1: (85, 85, 85, 255), 2: (170, 170, 170, 255), 3: (255, 255, 255, 255)}

OUTLINE = '#1b1424'

SKIN_CH = {'O': 0, '1': 1, '2': 2, '3': 3}
HAIR_CH = {'o': 0, 'a': 1, 'b': 2, 'c': 3}

# Feste Farben (Kleidung/Details). Gemeinsame Zeichen:
COMMON = {
    'k': OUTLINE,
    'e': '#1b1424',   # Auge
    'E': '#f4f0e6',   # Augenweiss / Glanzlicht
    't': '#f1e8c8',   # Hauer (Orc)
    'm': '#6b2a33',   # Mund
    'n': '#4a2f24',   # Schuhe dunkel
    'N': '#6e4633',   # Schuhe hell
}

CLASS_COLORS = {
    'priest': {
        'W': '#f3eedf', 'w': '#cdc3ae', 'v': '#978a78',   # Robe
        'Y': '#f2c14e', 'y': '#b07f2c',                    # Gold
        'u': '#5a7fc6', 'U': '#8fb0ee',                    # Stola blau
    },
    'warrior': {
        'S': '#d3d8e2', 's': '#9199ab', 'z': '#5c6378',   # Stahl
        'R': '#c0443d', 'r': '#80272c',                    # Wappenrock
        'L': '#8e5b36', 'l': '#5d3a23',                    # Leder
        'Y': '#f2c14e', 'y': '#b07f2c',
    },
}

# Rassen (Kopfgeometrie siehe heads.py)
RACES = {
    'human': {'waist': 27},
    'dwarf': {'waist': 30},
    'orc': {'waist': 26},
    'gnome': {'waist': 30},
}

# ------------------------------------------------------------------ Kleidung
# Koerper-Raster je Rasse und Klasse, Ursprung (x0, y0), Zeilen (x_start, muster)

BODIES = {}

BODIES[('human', 'priest')] = (9, 19, [
    (5, 'kYYYk'),
    (3, 'kkWWYyWkk'),
    (2, 'kWWWWYywwk'),
    (1, 'kWWkWWYywkwk'),
    (1, 'kWWkWWYywkvk'),
    (1, 'kWWkWWYywkvk'),
    (1, 'kWWkWWYywkvk'),
    (1, 'kYYkWWYywkyk'),
    (1, 'O22kWWYywk11O'),
    (1, 'kOOkWWYywwkOO'),
    (2, 'kWWWWYywwvk'),
    (2, 'kWWWWYywwvk'),
    (1, 'kWWWWWYywwvvk'),
    (1, 'kYYYYYYyyyyyk'),
    (1, 'kkkNNkkkNNkkk'),
    (3, 'knnk.knnk'),
])

BODIES[('dwarf', 'priest')] = (8, 25, [
    (5, 'kYYYYk'),
    (2, 'kkWWWYyWwkk'),
    (1, 'kWWWWWYywwvk'),
    (0, 'kWWkWWWYywkvvk'),
    (0, 'kWWkWWWYywkvvk'),
    (0, 'kYYkWWWYywkyyk'),
    (0, 'O22kWWWYywk11O'),
    (0, 'kOOkWWWYywwkOO'),
    (1, 'kWWWWWYywwvk'),
    (1, 'kYYYYYYyyyyk'),
    (1, 'kkNNNkkkNNNk'),
])

BODIES[('orc', 'priest')] = (7, 18, [
    (6, 'kYYYYk'),
    (3, 'kkkWWWYyWkkk'),
    (1, 'kkWWWWWYywwwkk'),
    (0, 'kWWWkWWWYywwkvvk'),
    (0, 'kWWWkWWWYywwkvvk'),
    (0, 'kWWWkWWWYywwkvvk'),
    (0, 'kWWWkWWWYywwkvvk'),
    (0, 'kYYYkWWWYywwkyyk'),
    (0, 'O222kWWWYywwk111O'),
    (0, 'kOOOkWWWYywwwkOOO'),
    (1, 'kkkWWWWWYywwvvk'),
    (2, 'kWWWWWWYywwvvk'),
    (2, 'kWWWWWWYywwvvk'),
    (2, 'kWWWWWWYywwvvvk'),
    (2, 'kYYYYYYYyyyyyyk'),
    (2, 'kkkNNNkkkkNNNkk'),
    (4, 'knnnk..knnnk'),
])

BODIES[('gnome', 'priest')] = (10, 27, [
    (3, 'kYYYk'),
    (1, 'kkWWYywkk'),
    (0, 'kWkWWYywkvk'),
    (0, 'kYkWWYywkyk'),
    (0, 'O2kWWYywk1O'),
    (0, 'kOkWWYywwkO'),
    (1, 'kWWWYywwvk'),
    (1, 'kYYYYyyyyk'),
    (1, 'kkNNkkNNkk'),
])

# Krieger: Plattenruestung mit rotem Wappenrock
BODIES[('human', 'warrior')] = (9, 19, [
    (4, 'kzzzzk'),
    (1, 'kkSSSsSSSsskk'),
    (0, 'kSSsSRRRRrsSszk'),
    (0, 'ksszkRRYRrkszzk'),
    (1, 'kzkRRYYYrrkzk'),
    (1, 'kLkRRRYRrrkLk'),
    (1, 'kSkLLLLLlllkSk'),
    (1, 'kSkRRRRRrrrkSk'),
    (1, 'O2kRRRRRrrrk1O'),
    (1, 'kOkRRRRRrrrkOk'),
    (2, 'kRRRRRrrrrk'),
    (2, 'ksSSSkksszk'),
    (2, 'kSSsk.kSszk'),
    (2, 'kSSsk.kSszk'),
    (2, 'kSSSk.kSSzk'),
    (1, 'kzzzzk.kzzzzk'),
    (1, 'kkkkkk.kkkkkk'),
])

BODIES[('dwarf', 'warrior')] = (7, 25, [
    (4, 'kzzzzzzk'),
    (1, 'kkSSSsSSSsSskk'),
    (0, 'kSSsSRRRRRrsSzk'),
    (0, 'ksszkRRYRRrkzzk'),
    (0, 'kSSkLLLLLLllkSk'),
    (0, 'O22kRRRRRRrrk1O'),
    (0, 'kOOkRRRRRRrrkOO'),
    (1, 'kkSSSkkkSSSzk'),
    (1, 'kSSSk..kSSzk'),
    (1, 'kzzzzk.kzzzzk'),
    (1, 'kkkkkk.kkkkkk'),
])

BODIES[('orc', 'warrior')] = (6, 18, [
    (5, 'kzzzzzzk'),
    (1, 'kkkSSSSsSSSSskkk'),
    (0, 'kSSSsSRRRRRrsSSzk'),
    (0, 'kssszkRRRYRRrkszzk'),
    (1, 'kszkRRRYYYRrrkzzk'),
    (2, 'kzkRRRRYRRrrkzk'),
    (2, 'kLkLLLLLLLlllkLk'),
    (2, 'kSkRRRRRRRrrrkSk'),
    (2, 'O22kRRRRRRrrrk11O'),
    (2, 'kOOkRRRRRRrrrkOOk'),
    (4, 'kRRRRRRrrrrk'),
    (3, 'kSSSSSkkSSSszk'),
    (3, 'kSSSsk..kSSSzk'),
    (3, 'kSSSsk..kSSSzk'),
    (3, 'kSSSsk..kSSSzk'),
    (2, 'kzzzzzk..kzzzzzk'),
    (2, 'kkkkkkk..kkkkkkk'),
])

BODIES[('gnome', 'warrior')] = (9, 27, [
    (3, 'kzzzzk'),
    (0, 'kkSSsSSSsskk'),
    (0, 'kSkRRYRRrkSk'),
    (0, 'kSkLLLLLlkSk'),
    (0, 'O2kRRRRRrk1O'),
    (0, 'kOkSSSkSSzkO'),
    (1, 'kSSSk.kSzk'),
    (1, 'kkkkk.kkkk'),
])

# ------------------------------------------------------------------ Paletten
# 3 Stufen (Schatten, Basis, Licht). Index 0 = feste Konturfarbe.
SKIN_PALETTES = {
    'human': [
        ['#c98f73', '#f2c2a0', '#fde0c6'],
        ['#b8795a', '#e0a47e', '#f4c6a2'],
        ['#9a6242', '#c98a5e', '#e2ab7c'],
        ['#6e432e', '#9a6446', '#bd8560'],
        ['#48291e', '#6b3f2c', '#8c5a3f'],
    ],
    'dwarf': [
        ['#c47e6a', '#efb69a', '#fcd6bf'],
        ['#b06a54', '#dd9a7c', '#f2bea0'],
        ['#8e5a40', '#bc8660', '#dca67c'],
        ['#6a4232', '#94664a', '#b88864'],
        ['#6e6a70', '#9c979b', '#bdb8b9'],
    ],
    'orc': [
        ['#3f6b2c', '#62973f', '#8cbe5a'],
        ['#56692d', '#7f9444', '#a6b863'],
        ['#2d4f33', '#467548', '#65995f'],
        ['#5b4a2c', '#836a3e', '#a8905a'],
        ['#445e5c', '#62837d', '#86a79c'],
    ],
    'gnome': [
        ['#d08e82', '#f7c4b4', '#ffe2d6'],
        ['#be7d68', '#eaaa8f', '#f8cbb2'],
        ['#9a6a4e', '#c9946e', '#e5b58c'],
        ['#6d4636', '#976450', '#b98670'],
        ['#9b8ba6', '#c5b6cf', '#e4d9ea'],
    ],
}

HAIR_PALETTES = {
    'human': [
        ['#2a2230', '#40364a', '#5d5068'],   # Schwarz
        ['#5a3620', '#7e4e2c', '#a4703f'],   # Braun
        ['#b58a3a', '#e0bb5c', '#f6df90'],   # Blond
        ['#8c2f1c', '#be4a28', '#e0773e'],   # Rot
        ['#8e8b95', '#c4c1c8', '#eceaf0'],   # Weiss
    ],
    'dwarf': [
        ['#8a2b17', '#bd4a22', '#e27a3a'],   # Rot
        ['#523219', '#7a4b26', '#a06b3a'],   # Braun
        ['#241c26', '#3b3040', '#574a5e'],   # Schwarz
        ['#a8823a', '#d6b25a', '#f0d88a'],   # Blond
        ['#7d7a82', '#b3b0b8', '#e2dfe6'],   # Grau
    ],
    'orc': [
        ['#1e1a22', '#332c38', '#4b4252'],   # Schwarz
        ['#3e2718', '#5c3b24', '#7e5634'],   # Dunkelbraun
        ['#6b6870', '#9a979e', '#c6c3ca'],   # Grau
        ['#9c9aa2', '#d4d2d8', '#f4f3f6'],   # Weiss
        ['#6e1d18', '#9a2c22', '#c44a34'],   # Blutrot
    ],
    'gnome': [
        ['#a03e7a', '#d864a8', '#f596cf'],   # Pink
        ['#2d7f86', '#45b3b5', '#7fdad4'],   # Tuerkis
        ['#9c9aa8', '#d6d4de', '#f6f5fa'],   # Weiss
        ['#b0521e', '#e07c2c', '#f7a95a'],   # Orange
        ['#5a3a92', '#7f58c4', '#a988e6'],   # Violett
    ],
}

RACE_IDS = ['human', 'dwarf', 'orc', 'gnome']


# ------------------------------------------------------------------ Rendering
def _draw_rows(cv: Canvas, spec, legend, dy=0, layer_filter=None):
    x0, y0, rows = spec
    for i, (xs, pat) in enumerate(rows):
        for j, ch in enumerate(pat):
            if ch in '. ':
                continue
            if layer_filter is not None and not layer_filter(ch):
                continue
            col = legend.get(ch)
            if col is None:
                raise KeyError(f'Zeichen {ch!r} fehlt (Zeile {i}: {pat!r})')
            cv.px(x0 + xs + j, y0 + i + dy, col)


def _layer_legends(klass):
    skin = {k: IDX[v] for k, v in SKIN_CH.items()}
    hair = {k: IDX[v] for k, v in HAIR_CH.items()}
    fixed = dict(COMMON)
    fixed.update(CLASS_COLORS.get(klass, {}))
    return skin, hair, {k: c(v) for k, v in fixed.items()}


def _is_skin(ch):
    return ch in SKIN_CH


def _is_hair(ch):
    return ch in HAIR_CH


def _breath_shift(cv: Canvas, waist: int, d: int) -> Canvas:
    """Alles oberhalb der Taille um d Pixel nach unten verschieben."""
    if d == 0:
        return cv
    out = cv.copy()
    out.a[:waist + 1] = 0
    out.a[d:waist + 1] = cv.a[:waist + 1 - d]
    # Zeile an der Taille mit Original-Unterkoerper fuellen, falls leer
    return out


def race_layers(race: str, klass: str, style: int) -> dict[str, Canvas]:
    """Einzelne Ebenen (1 Frame, ohne Animation)."""
    import numpy as np
    import heads as HD
    skin_l, hair_l, fixed_l = _layer_legends(klass)
    skin = Canvas(FW, FH)
    outfit = Canvas(FW, FH)
    hair = Canvas(FW, FH)
    gear = Canvas(FW, FH)

    # Koerper: Haende (Hautzeichen) in skin, Rest in outfit
    body = BODIES[(race, klass)]
    _draw_rows(skin, body, skin_l, layer_filter=_is_skin)
    _draw_rows(outfit, body, fixed_l, layer_filter=lambda ch: not _is_skin(ch))

    # Kopf (prozedural)
    lv, details = HD.head_parts(race)
    head_m = lv > 0
    for y, x in zip(*np.where(head_m)):
        skin.px(x, y, IDX[int(lv[y, x])])
    for (x, y, ch) in details:
        outfit.px(x, y, fixed_l[ch])
    # Kontur um den Kopf (nur wo noch nichts ist)
    occupied = (skin.a[:, :, 3] > 0) | (outfit.a[:, :, 3] > 0)
    for y, x in zip(*np.where(HD.border_of(head_m) & ~occupied)):
        skin.px(x, y, IDX[0])

    # Frisur
    hm, hlv, hdet = HD.hair_levels(race, style)
    if klass == 'warrior':
        gm, gch = HD.helmet(race)
        hm = hm & ~gm
        hlv[~hm] = 0
    for y, x in zip(*np.where(hm)):
        hair.px(x, y, IDX[int(hlv[y, x])])
    for (x, y, ch) in hdet:
        hair.clear_px(x, y)
        gear.px(x, y, fixed_l[ch])
    head_all = head_m | hm
    for y, x in zip(*np.where(HD.border_of(hm) & ~head_all)):
        hair.px(x, y, IDX[0])

    # Helm
    if klass == 'warrior':
        for y, x in zip(*np.where(gm)):
            gear.px(x, y, fixed_l[gch[y, x]])
        allm = head_m | hm | gm
        for y, x in zip(*np.where(HD.border_of(gm) & ~allm)):
            gear.px(x, y, fixed_l['k'])
    return {'skin': skin, 'outfit': outfit, 'hair': hair, 'gear': gear}


def animated_layers(race: str, klass: str, style: int) -> dict[str, Canvas]:
    """Ebenen als Spritesheet mit FRAMES Frames nebeneinander."""
    base = race_layers(race, klass, style)
    waist = RACES[race]['waist']
    sheets = {}
    for name, cv in base.items():
        sheet = Canvas(FW * FRAMES, FH)
        for f, d in enumerate(BREATH):
            sheet.paste(_breath_shift(cv, waist, d), f * FW, 0)
        sheets[name] = sheet
    return sheets


def colorize(layer: Canvas, ramp3: list[str]) -> Canvas:
    """Vorschau: Index-Ebene mit Palette einfaerben (macht im Spiel der Shader)."""
    pal = [c(OUTLINE)] + [c(x) for x in ramp3]
    out = Canvas(layer.w, layer.h)
    alpha = layer.a[:, :, 3] > 0
    idx = (layer.a[:, :, 0].astype(int) + 42) // 85
    for i in range(4):
        m = alpha & (idx == i)
        out.a[m] = pal[i]
    return out


def composite(race, klass, style, skin_i, hair_i, frame=0) -> Canvas:
    sheets = animated_layers(race, klass, style)
    out = Canvas(FW, FH)
    parts = [
        colorize(sheets['skin'], SKIN_PALETTES[race][skin_i]),
        sheets['outfit'],
        colorize(sheets['hair'], HAIR_PALETTES[race][hair_i]),
        sheets['gear'],
    ]
    for p in parts:
        out.paste(p.crop(frame * FW, 0, FW, FH), 0, 0)
    return out
