"""Figuren im Chibi-Stil (grosser Kopf, kleiner Koerper, klare dunkle Kontur, grosse Augen).

Alles ist Pixel fuer Pixel als Raster gezeichnet:
  FACE[rasse]            Gesicht (Hautindex)          O=Kontur 1=Schatten 2=Basis 3=Licht
  HAIR[rasse][frisur]    Frisur/Bart (Haarindex)      a=dunkel b=Basis c=Licht  (o=Kontur)
  BODY[(rasse, klasse)]  Rumpf + Beine (feste Farben, Zeichen siehe PAL)
Arme werden pro Frame aus Schulter/Hand-Position gezeichnet (fuer Idle und Zauber-Pose).

Ebenen (Zeilen im Spritesheet): skin, outfit, eyes, eyes_closed, hair, gear
"""
from __future__ import annotations

import numpy as np

from pa import Canvas, c, mix
import heads as HD

FW, FH = 32, 36
LAYERS = ['skin', 'outfit', 'eyes', 'eyes_closed', 'hair', 'gear']
IDX = {0: (0, 0, 0, 255), 1: (85, 85, 85, 255), 2: (170, 170, 170, 255), 3: (255, 255, 255, 255)}
OUTLINE = '#120e18'

ANIMS = {
    'idle': {'start': 0, 'count': 8, 'fps': 6, 'loop': True},
    'cast': {'start': 8, 'count': 10, 'fps': 10, 'loop': False},
}
FRAME_COUNT = 18

EYE_COLORS = {   # (dunkel, Iris)
    'human': ('#1c2a5a', '#4a7ad8'),
    'dwarf': ('#2a1a12', '#8a5a2a'),
    'orc': ('#3a0c0c', '#d8402a'),
    'gnome': ('#123a1c', '#3aaa52'),
}

PAL = {
    # Priester
    'W': '#f6f2e8', 'w': '#d8d0c0', 'v': '#a8998a', 'Y': '#f5c95a', 'y': '#b8862e',
    'u': '#4f76c4', 'U': '#86aaf0', 'n': '#3a2630', 'N': '#5e4038',
    # Krieger
    'S': '#e2e6ee', 's': '#a8b0c2', 'z': '#6a7288', 'R': '#d04a40', 'r': '#8a2a2e', 'L': '#9a643a', 'l': '#5e3b24',
    'k': OUTLINE, 't': '#f4ecd0',
}

# Kopfposition (x0, y0 der Rasterecke) und Koerperposition je Rasse
LAYOUT = {
    'human': {'head': (9, 12), 'body': (10, 24), 'shoulder_y': 26, 'shoulder_dx': 5, 'hand_y': 30},
    'dwarf': {'head': (8, 17), 'body': (9, 27), 'shoulder_y': 29, 'shoulder_dx': 6, 'hand_y': 32},
    'orc':   {'head': (8, 10), 'body': (9, 22), 'shoulder_y': 24, 'shoulder_dx': 7, 'hand_y': 29},
    'gnome': {'head': (8, 18), 'body': (11, 28), 'shoulder_y': 29, 'shoulder_dx': 4, 'hand_y': 32},
}

# ---------------------------------------------------------------- Gesichter
FACE = {
    'human': [
        "..............",
        "....OOOOOO....",
        "...O332222O...",
        "..O33222222O..",
        "..O32222222O..",
        "..O22222222O..",
        ".O3222222221O.",
        ".O3222222221O.",
        "..O22222221O..",
        "..O22222211O..",
        "...O111111O...",
        "....OOOOOO....",
    ],
    'dwarf': [
        "................",
        ".....OOOOOO.....",
        "....O3322222O...",
        "...O332222222O..",
        "..O32222222222O.",
        "..O22222222222O.",
        ".O3222222222221O",
        ".O3222223322221O",
        "..O22222332222O.",
        "..O12222112221O.",
        "...OO1111111OO..",
    ],
    'orc': [
        "................",
        ".....OOOOOO.....",
        "....O3322222O...",
        "...O332222222O..",
        "..O32222222222O.",
        "..O22222222222O.",
        "O3O22222222222O1",
        "O32222222222221O",
        ".O2222222222221O",
        ".O2222222222211O",
        "..O22222222211O.",
        "..O12222222211O.",
        "...O111111111O..",
        "....OOOOOOOOO...",
    ],
    'gnome': [
        "................",
        ".....OOOOOO.....",
        "....O3322222O...",
        "...O332222222O..",
        "..O32222222222O.",
        "OO.O222222222O.O",
        "O3OO222222222OO1",
        "O332222222222211",
        ".O322222332222O.",
        "..O2222233222O..",
        "...OO111111OO...",
        ".....OOOOOO.....",
    ],
}

# Augen: (x, y) der linken oberen Ecke je Auge (relativ zum Gesichtsraster), 2x2 Pixel
EYES = {   # leicht nach rechts versetzt: Figur schaut in 3/4-Ansicht nach rechts
    'human': [(5, 7), (9, 7)],
    'dwarf': [(6, 6), (10, 6)],
    'orc': [(6, 7), (10, 7)],
    'gnome': [(6, 6), (10, 6)],
}
TUSKS = {'orc': [(6, 11), (11, 11)]}
# Nase auf der rechten Gesichtsseite (Hautindex 3 = Licht, 1 = Schatten darunter)
NOSE = {'human': [(11, 8, 2)], 'dwarf': [(12, 7, 3), (12, 8, 2)], 'orc': [(12, 9, 2)], 'gnome': [(12, 8, 3), (13, 8, 2), (12, 9, 1)]}

# ---------------------------------------------------------------- Frisuren (gleiches Raster wie das Gesicht)
HAIR = {
    'human': [
        [   # Kurz mit Pony
            "....bbbbbb....",
            "..bcccbbbbbb..",
            ".bccbbbbbbbba.",
            ".bcbbbbbbbbba.",
            "bbbbbbbbbbbbba",
            "bbbbabbbbabbba",
            "bba.a....a.bba",
            "ba..........ab",
            "a............a",
        ],
        [   # Lang, offen bis ueber die Schultern
            "....bbbbbb....",
            "..bcccbbbbbb..",
            ".bccbbbbbbbba.",
            ".bcbbbbbbbbba.",
            "bbbbbbbbbbbbba",
            "bbbbbabbbbbbba",
            "bba.a...a..bba",
            "bba........bba",
            "bba........bba",
            "bba........bba",
            "bba........bba",
            "bbba......abba",
            "bbba......abba",
            ".bba......abb.",
            ".ab........ba.",
        ],
        [   # Dutt oben
            ".....bbbb.....",
            "....bccbba....",
            "....bbbbba....",
            "..bcccbbbbbb..",
            ".bccbbbbbbbba.",
            ".bcbbbbbbbbba.",
            "bbbbbbbbbbbbba",
            "bbab.......bab",
            "ba..........ab",
        ],
    ],
    'dwarf': [
        [   # Kurzes Haar + langer Vollbart
            ".....bbbbbb.....",
            "...bcccbbbbbb...",
            "..bccbbbbbbbbb..",
            ".bcbbbbbbbbbbba.",
            ".bbbbbbbbbbbbba.",
            "bba...........ab",
            "ba............ab",
            "ba............ab",
            "bbb..b....b..bbb",
            "bbbbbba..abbbbba",
            "bbbbbbbbbbbbbbba",
            ".bbcbbbbbbbbbba.",
            "..bbbbbbbbbbba..",
            "...abbbbbbbba...",
            "....aabbbbaa....",
        ],
        [   # Haarkranz, geflochtener Bart mit Goldperlen
            "................",
            "................",
            "................",
            "................",
            ".bb..........bb.",
            "bba..........abb",
            "ba............ab",
            "ba............ab",
            "bbb..b....b..bbb",
            ".bbbbba..abbbbb.",
            "..bbbbbbbbbbbb..",
            "...bbbbbbbbbb...",
            "....abbbbbba....",
            "......bbbb......",
            "......YYYY......",
            "......bbbb......",
            "......YYYY......",
        ],
        [   # Wilde Maehne + breiter kurzer Bart
            "...b.bbbbbb.b...",
            "..bbbcccbbbbbb..",
            ".bbccbbbbbbbbbb.",
            "bbcbbbbbbbbbbbba",
            "bbbbbbbbbbbbbbba",
            "bbba.b....b.abbb",
            "bba..........abb",
            "bba..........abb",
            "bbbb.b....b.bbbb",
            "bbbbbba..abbbbbb",
            ".bbbbbbbbbbbbbb.",
            "..abbbbbbbbbba..",
            "....aabbbbaa....",
        ],
    ],
    'orc': [
        [   # Irokese
            ".......bb.......",
            "......bccb......",
            "......bcbb......",
            "......bbba......",
            "......bbba......",
            ".......ba.......",
        ],
        [   # Langer Zopf + Kinnbart
            ".....bbbbbb.....",
            "...bcccbbbbbb...",
            "..bccbbbbbbbbb..",
            "..bcbbbbbbbbba..",
            "..bb.........b..",
            "................",
            "................",
            "................",
            "................",
            "................",
            "................",
            "......bbbb......",
            "......abba......",
            ".......bb.......",
        ],
        [   # Haarknoten + dichter Bart
            "......bbbb......",
            ".....bccbba.....",
            "......bbba......",
            "....bbbbbbbb....",
            "...bcbbbbbbbba..",
            "................",
            "................",
            "................",
            "................",
            "................",
            "..bb..........bb",
            "..bbbb......bbbb",
            "...bbbbbbbbbbba.",
            "....abbbbbbbba..",
            ".....aabbbbaa...",
        ],
    ],
    'gnome': [
        [   # Zwei Zoepfe
            ".....bbbbbb.....",
            "...bcccbbbbbb...",
            "..bccbbbbbbbbb..",
            "..bcbbbbbbbbbba.",
            "..bbbbbbbbbbbba.",
            "...bbab....babb.",
            "...ba........ab.",
            "...b..........b.",
            "..bb..........bb",
            ".bcb..........bbb",
            ".bbb..........bba",
            ".abb..........ba.",
            "..a............a",
        ],
        [   # Hohe Tolle
            ".....bbbb.......",
            "....bccbbb......",
            "...bccbbbbb.....",
            "...bcbbbbbba....",
            "..bcbbbbbbbbb...",
            "..bbbbbbbbbbbb..",
            "..bcbbbbbbbbbba.",
            "..bbbbbbbbbbbba.",
            "...bbab....bab..",
            "...ba........a..",
        ],
        [   # Kurz, zerzaust + Schnurrbart
            "....b.bb.b......",
            "...bbcbbbbbb....",
            "..bcccbbbbbbb...",
            "..bccbbbbbbbbb..",
            "..bbbbbbbbbbbba.",
            "..bbabbabbabbba.",
            "...ba........a..",
            "................",
            "................",
            "......abbba.....",
        ],
    ],
}

# Frisuren, die unter dem Kopf beginnen, werden nach oben versetzt (Irokese, Dutt usw.)
HAIR_OFFSET = {('human', 2): -3, ('orc', 0): -5, ('orc', 2): -3, ('gnome', 1): -3, ('dwarf', 2): -1}

# ---------------------------------------------------------------- Koerper
BODY = {
    ('human', 'priest'): [
        "....kYYk....",
        "...WWYyww...",
        "..WWWYywwv..",
        "..WWWYywwv..",
        "..uuuYyuuu..",
        "..WWWYywwv..",
        ".WWWWYywwvv.",
        ".YYYYYyyyyy.",
        "..nN....nN..",
        "..nn....nn..",
        "............",
        "............",
    ],
    ('dwarf', 'priest'): [
        "....kkYYkk....",
        "..WWWWYywwww..",
        ".WWWWWYywwwwv.",
        ".uuuuuYyuuuuu.",
        ".WWWWWYywwwvv.",
        ".YYYYYYyyyyyy.",
        "..nNn....nNn..",
        "..nnn....nnn..",
        "..............",
    ],
    ('orc', 'priest'): [
        ".....kYYYk......",
        "...WWWWYywwww...",
        "..WWWWWYywwwwv..",
        "..WWWWWYywwwwv..",
        "..WWWWWYywwwwv..",
        "..uuuuuYyuuuuu..",
        "..WWWWWYywwwvv..",
        ".WWWWWWYywwwwvv.",
        ".WWWWWWYywwwwvv.",
        ".YYYYYYYyyyyyyy.",
        "..nnN......nnN..",
        "..nnn......nnn..",
        "................",
    ],
    ('gnome', 'priest'): [
        "..kYYk....",
        ".WWYyww...",
        ".uuYyuu...",
        ".WWYywv...",
        "YYYYyyyy..",
        ".nN..nN...",
        ".nn..nn...",
        "..........",
    ],
    ('human', 'warrior'): [
        "...kSSSk....",
        "..SSRRRsz...",
        ".SsRRYRrzz..",
        "..sRYYYrz...",
        "..sRRYRrz...",
        "..LLLYlll...",
        "..SRRRRrz...",
        "..Ss...sz...",
        "..Ss...sz...",
        ".zzz...zzz..",
        "............",
        "............",
    ],
    ('dwarf', 'warrior'): [
        "....kSSSSk....",
        ".SSSRRRRRszz..",
        ".SsSRRYRRrzz..",
        "..sRRYYYRrz...",
        "..LLLLYllll...",
        "..SSS...szz...",
        ".zzzz...zzzz..",
        "..............",
        "..............",
    ],
    ('orc', 'warrior'): [
        ".....kSSSSk.....",
        "..SSSSRRRRssz...",
        ".SSsSRRYRRrzzz..",
        ".SsssRYYYRrzzz..",
        "...sRRRYRRrz....",
        "...sRRRRRRrz....",
        "...LLLLYllll....",
        "...SRRRRRRrz....",
        "...SSs...szz....",
        "...SSs...szz....",
        "..zzzz...zzzz...",
        "................",
        "................",
    ],
    ('gnome', 'warrior'): [
        "..kSSk....",
        "SSRYRsz...",
        ".sRYRrz...",
        ".LLYlll...",
        ".Ss.sz....",
        "zzz.zzz...",
        "..........",
        "..........",
    ],
}

HELMET = {   # Krieger-Helme: Raster ueber dem Kopf (gleiches Raster wie das Gesicht)
    'human': [
        "....SSSSSS....",
        "..SSSSSSSsss..",
        ".SSSSSSSSssz..",
        ".SsRRSSSSsszz.",
        "SSSSSSSSSSszzz",
        "zzzzzzzzzzzzzz",
        "zz..........zz",
    ],
    'dwarf': [
        "t..............t",
        "t....SSSSSS....t",
        "tt.SSSSSSSSss.tt",
        ".tSSSSSSSSSsszt.",
        ".SSSSSSSSSSsssz.",
        "zzzzzzzzzzzzzzzz",
        "zz............zz",
    ],
    'orc': [
        "t..............t",
        "tt...SSSSSS...tt",
        ".tSSSSSSSSSssst.",
        ".SSSSSSSSSSsssz.",
        "SSSSSSSSSSSsszzz",
        "zzzzzzzzzzzzzzzz",
        "zz............zz",
    ],
    'gnome': [
        ".......SS.......",
        "......SSSs......",
        "....SSSSSSss....",
        "..SSSSSSSSSsss..",
        "..SSSSSSSSSssz..",
        ".zzzzzzzzzzzzzz.",
        ".zz..........zz.",
    ],
}


# ---------------------------------------------------------------- Zeichnen
def _grid_to(cv_map, grid, x0, y0, dy=0, dx_rows=None):
    """Zeichnet ein Raster; cv_map(zeichen) -> (ebene, farbe) oder None."""
    for yy, row in enumerate(grid):
        sx = dx_rows(yy) if dx_rows else 0
        for xx, ch in enumerate(row):
            if ch in '. ':
                continue
            res = cv_map(ch)
            if res is None:
                continue
            layer, col = res
            layer.px(x0 + xx + sx, y0 + yy + dy, col)


def _mask_of(layer: Canvas):
    return layer.a[:, :, 3] > 0


def _arm(L, shoulder, hand, sleeve_cols, skin_hand=True, glove=None):
    """Chibi-Arm: kurzer Aermel (2 px breit) von der Schulter zur Hand, Hand 2x2."""
    (sx, sy), (hx, hy) = shoulder, hand
    steps = max(abs(hx - sx), abs(hy - sy), 1)
    for i in range(steps + 1):
        t = i / steps
        x = round(sx + (hx - sx) * t)
        y = round(sy + (hy - sy) * t)
        if i < steps:
            L['outfit'].px(x, y, sleeve_cols[0])
            L['outfit'].px(x + 1, y, sleeve_cols[1])
    for (dx, dy) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        if skin_hand:
            L['skin'].px(hx + dx, hy + dy, IDX[3 if dy == 0 and dx == 0 else 2])
        else:
            L['outfit'].px(hx + dx, hy + dy, glove if dy == 0 else mix(glove, '#000000', 0.25))


def compose(race, klass, style, breath=0, hair_sway=0, hands=0.0, glow=0):
    lay = LAYOUT[race]
    L = {n: Canvas(FW, FH) for n in LAYERS}
    hx0, hy0 = lay['head']
    bx0, by0 = lay['body']
    hy = hy0 + breath

    # Koerper (Rumpf bewegt sich beim Atmen nicht, Kopf schon -> wirkt wie Nicken/Atmen)
    body = BODY[(race, klass)]
    _grid_to(lambda ch: (L['outfit'], PAL[ch]) if ch in PAL else None, body, bx0, by0)

    # Arme: Schulter an der Rumpfkante, Hand je nach Pose
    cx = 16
    sdx = lay['shoulder_dx']
    sy = lay['shoulder_y']
    rest_l = (cx - sdx - 2, lay['hand_y'])
    rest_r = (cx + sdx, lay['hand_y'])
    up_l = (cx - sdx - 4, sy - 6)
    up_r = (cx + sdx + 2, sy - 6)
    mid_l = (cx - sdx - 3, sy)
    mid_r = (cx + sdx + 1, sy)

    def pick(a, b, c_, t):
        if t <= 1:
            return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t))
        t -= 1
        return (round(b[0] + (c_[0] - b[0]) * t), round(b[1] + (c_[1] - b[1]) * t))
    hl = pick(rest_l, mid_l, up_l, hands)
    hr = pick(rest_r, mid_r, up_r, hands)
    if klass == 'priest':
        sleeves = (PAL['W'], PAL['w'])
        _arm(L, (cx - sdx, sy), hl, sleeves)
        _arm(L, (cx + sdx - 1, sy), hr, (PAL['w'], PAL['v']))
    else:
        _arm(L, (cx - sdx, sy), hl, (PAL['S'], PAL['s']), skin_hand=False, glove=PAL['s'])
        _arm(L, (cx + sdx - 1, sy), hr, (PAL['s'], PAL['z']), skin_hand=False, glove=PAL['s'])

    # Gesicht
    _grid_to(lambda ch: (L['skin'], IDX[{'O': 0, '1': 1, '2': 2, '3': 3}[ch]]) if ch in 'O123' else None,
             FACE[race], hx0, hy)
    # Augen (offen / geschlossen)
    dark, iris = EYE_COLORS[race]
    for i, (ex, ey) in enumerate(EYES[race]):
        X, Y = hx0 + ex, hy + ey
        L['eyes'].px(X, Y, dark)
        L['eyes'].px(X + 1, Y, dark)
        if i == 0:
            L['eyes'].px(X, Y + 1, '#ffffff')
            L['eyes'].px(X + 1, Y + 1, iris)
        else:
            L['eyes'].px(X, Y + 1, iris)
            L['eyes'].px(X + 1, Y + 1, '#ffffff')
        L['eyes_closed'].px(X, Y + 1, dark)
        L['eyes_closed'].px(X + 1, Y + 1, dark)
    for (nx, ny, lv) in NOSE.get(race, []):
        L['skin'].px(hx0 + nx, hy + ny, IDX[lv])
    for (tx, ty) in TUSKS.get(race, []):
        L['outfit'].px(hx0 + tx, hy + ty, PAL['t'])
        L['outfit'].px(hx0 + tx, hy + ty - 1, PAL['t'])

    # Frisur
    grid = HAIR[race][style]
    off = HAIR_OFFSET.get((race, style), 0)
    helmet = HELMET.get(race) if klass == 'warrior' else None

    def hair_map(ch):
        if ch in 'abc':
            return (L['hair'], IDX[{'a': 1, 'b': 2, 'c': 3}[ch]])
        if ch == 'o':
            return (L['hair'], IDX[0])
        if ch in 'Yy':
            return (L['gear'], PAL[ch])
        return None

    def sway_rows(yy):
        # untere Haarpartien (Zoepfe, lange Haare) schwingen leicht
        return hair_sway if (yy + off) >= 9 else 0
    _grid_to(hair_map, grid, hx0, hy + off, dx_rows=sway_rows)
    # 3/4-Ansicht nach rechts: Hinterkopf links voller, rechte Wange frei
    face_w = len(FACE[race][0])
    hair_a = L['hair'].a
    for yy in range(hy + 5, hy + 10):
        row = np.where(hair_a[yy, :, 3] > 0)[0]
        right = [x for x in row if x >= hx0 + face_w - 3]
        for x in right[:1]:
            if hair_a[yy, x + 1, 3] == 0:
                hair_a[yy, x] = 0
        left = [x for x in row if x <= hx0 + 3]
        if left:
            x = min(left) - 1
            if 0 <= x < FW and hair_a[yy, x, 3] == 0:
                hair_a[yy, x] = IDX[1]
    if helmet:
        # Helm verdeckt die Haare oben
        hm = np.zeros((FH, FW), bool)
        for yy, row in enumerate(helmet):
            for xx, ch in enumerate(row):
                if ch not in '. ':
                    hm[hy - 2 + yy, hx0 + xx] = True
        L['hair'].a[hm] = 0
        _grid_to(lambda ch: (L['gear'], PAL[ch]) if ch in PAL else None, helmet, hx0, hy - 2)

    # Schatten unter dem Pony: Haut direkt unter Haaren eine Stufe dunkler
    hair_m = _mask_of(L['hair'])
    skin_a = L['skin'].a
    below = np.zeros_like(hair_m)
    below[1:, :] = hair_m[:-1, :]
    sel = below & ~hair_m & (skin_a[:, :, 3] > 0) & (skin_a[:, :, 0] > 100)
    skin_a[sel] = IDX[1]

    # Lichtzauber an den Haenden
    if glow > 0:
        pts = {1: [(0, 0)], 2: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)],
               3: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, -2), (0, 2)]}[glow]
        for (gx, gy) in (hl, hr):
            for (dx, dy) in pts:
                d = abs(dx) + abs(dy)
                L['gear'].px(gx + dx, gy - 2 + dy, '#ffffff' if d == 0 else ('#ffe38a' if d == 1 else '#f5c95a'))

    # Aussenkontur um die ganze Figur
    solid = np.zeros((FH, FW), bool)
    for n in LAYERS:
        if n != 'eyes_closed':
            solid |= _mask_of(L[n])
    ring = HD.border_of(solid)
    for y, x in zip(*np.where(ring)):
        L['outfit'].px(x, y, OUTLINE)
    # Innenkontur zwischen Haaren und Gesicht an den Seiten (klare Trennung wie in der Vorlage)
    edge = HD.border_of(hair_m) & (skin_a[:, :, 3] > 0) & ~hair_m
    for y, x in zip(*np.where(edge)):
        if L['eyes'].a[y, x, 3] == 0 and y < hy + len(FACE[race]) - 3:
            neighbors_hair = hair_m[y, max(0, x - 1)] or hair_m[y, min(FW - 1, x + 1)]
            if neighbors_hair:
                skin_a[y, x] = IDX[1]
    return L


IDLE_BREATH = [0, 0, 0, 1, 1, 1, 0, 0]
IDLE_SWAY = [0, 0, 0, 0, 1, 1, 1, 0]
CAST = [(0.0, 0), (0.4, 0), (0.9, 0), (1.3, 1), (1.8, 2), (2.0, 3), (2.0, 3), (1.6, 2), (0.9, 1), (0.3, 0)]
CAST_BREATH = [0, 0, 0, 0, -1, -1, -1, 0, 0, 0]


def frames(race, klass, style):
    out = []
    for i in range(8):
        out.append(compose(race, klass, style, IDLE_BREATH[i], IDLE_SWAY[i], 0.0, 0))
    for i, (amt, glow) in enumerate(CAST):
        out.append(compose(race, klass, style, CAST_BREATH[i], 0, amt, glow if klass == 'priest' else 0))
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


def preview_frame(race, klass, style, skin_ramp, hair_ramp, L, closed=False) -> Canvas:
    out = Canvas(FW, FH)
    out.paste(colorize(L['skin'], skin_ramp), 0, 0)
    out.paste(L['outfit'], 0, 0)
    out.paste(L['eyes_closed' if closed else 'eyes'], 0, 0)
    out.paste(colorize(L['hair'], hair_ramp), 0, 0)
    out.paste(L['gear'], 0, 0)
    return out
