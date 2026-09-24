"""Figuren Version 3: Chibi-Stil in deutlicher 3/4-Ansicht nach rechts, Kleidung je Rasse.

Aufbau wie rig2 (gleiche Schnittstelle fuer build_assets.py und das Spiel):
  FACE[rasse]              Gesicht in 3/4-Ansicht (Hautindex O/1/2/3)
  EYES[rasse]              fernes Auge (schmal, 1x2) und nahes Auge (2x2 mit Glanz)
  EAR[rasse]               Ohr auf der Hinterkopfseite (links)
  HAIR[rasse][frisur]      Frisur (a/b/c), Hinterkopf links voll, Gesicht rechts frei
  BODY[(rasse, klasse)]    Rumpf + Beine in 3/4-Ansicht; Farben je Rasse (OUTFIT_PAL)
Der ferne Arm (links) liegt hinter dem Rumpf, der nahe Arm (rechts) davor.
"""
from __future__ import annotations

import numpy as np

import heads as HD
from pa import Canvas, c, mix

FW, FH = 32, 36
LAYERS = ['skin', 'outfit', 'eyes', 'eyes_closed', 'hair', 'gear']
IDX = {0: (0, 0, 0, 255), 1: (85, 85, 85, 255), 2: (170, 170, 170, 255), 3: (255, 255, 255, 255)}
OUTLINE = '#120e18'

ANIMS = {
    'idle': {'start': 0, 'count': 8, 'fps': 6, 'loop': True},
    'cast': {'start': 8, 'count': 10, 'fps': 10, 'loop': False},
}
FRAME_COUNT = 18

EYE_COLORS = {'human': ('#1c2a5a', '#4a7ad8'), 'dwarf': ('#1c2a4a', '#6aa0e0'),
              'orc': ('#3a0c0c', '#e04a2a'), 'gnome': ('#123a1c', '#3ac25a')}

# ---------------------------------------------------------------- Farben der Kleidung je Rasse
# Gemeinsame Zeichen im Koerperraster:
#   A a d  Hauptstoff hell/mittel/dunkel     B b    Zweitstoff hell/dunkel
#   Y y    Metall/Gold hell/dunkel           F f    Fell/Pelz hell/dunkel
#   t      Knochen/Elfenbein                 n N    Schuhe dunkel/hell
#   k      Kontur                            W      Weiss (Hemd/Kragen)
OUTFIT_PAL = {
    ('human', 'priest'): {'A': '#f6f2e8', 'a': '#d8d0c0', 'd': '#a8998a', 'B': '#5a82d0', 'b': '#3a5aa0',
                          'Y': '#f5c95a', 'y': '#b8862e', 'n': '#3a2630', 'N': '#5e4038'},
    ('dwarf', 'priest'): {'A': '#4a6ab0', 'a': '#34508a', 'd': '#243866', 'B': '#8a5a34', 'b': '#5e3b22',
                          'Y': '#f0b848', 'y': '#a8742a', 'F': '#c8b8a0', 'f': '#8a7a66',
                          'n': '#2e2020', 'N': '#4a3228'},
    ('orc', 'priest'): {'A': '#b08858', 'a': '#86643e', 'd': '#5e4428', 'B': '#c03a30', 'b': '#801e20',
                        'F': '#6a5a4a', 'f': '#403428', 't': '#efe6cc', 'Y': '#d8b060', 'y': '#8a6a30',
                        'n': '#2e2018', 'N': '#4a3424'},
    ('gnome', 'priest'): {'A': '#8a5ac8', 'a': '#6a3ea4', 'd': '#482a78', 'B': '#45c0c0', 'b': '#2a8a8e',
                          'Y': '#f0c050', 'y': '#a8782a', 'W': '#f4f0e6', 'n': '#2a2030', 'N': '#4a3a48',
                          'L': '#8a5a34'},
    ('human', 'warrior'): {'S': '#e2e6ee', 's': '#a8b0c2', 'z': '#6a7288', 'R': '#d04a40', 'r': '#8a2a2e',
                           'L': '#9a643a', 'l': '#5e3b24', 'Y': '#f5c95a', 'y': '#b8862e'},
    ('dwarf', 'warrior'): {'S': '#f0c878', 's': '#c09040', 'z': '#7a5a28', 'R': '#3a5aa0', 'r': '#243e70',
                           'L': '#8a5a34', 'l': '#5e3b22', 'Y': '#f4f0e0', 'y': '#b8b0a0'},
    ('orc', 'warrior'): {'S': '#8a8a96', 's': '#5e5e6a', 'z': '#3a3a44', 'R': '#b02a24', 'r': '#6a1414',
                         'L': '#6a4a30', 'l': '#40281a', 'Y': '#e8dcc0', 'y': '#a89880'},
    ('gnome', 'warrior'): {'S': '#e8c060', 's': '#b08a3a', 'z': '#6a4e1e', 'R': '#2a8a8e', 'r': '#1a5a5e',
                           'L': '#8a5a34', 'l': '#5e3b22', 'Y': '#f4f0e0', 'y': '#b8b0a0'},
}
SLEEVE = {   # (vorne hell, vorne dunkel) fuer die Arme
    ('human', 'priest'): ('#f6f2e8', '#d8d0c0'), ('dwarf', 'priest'): ('#4a6ab0', '#34508a'),
    ('orc', 'priest'): ('#b08858', '#86643e'), ('gnome', 'priest'): ('#8a5ac8', '#6a3ea4'),
}

LAYOUT = {
    'human': {'head': (9, 12), 'body': (10, 24), 'shoulder_y': 26, 'far_x': 12, 'near_x': 19, 'hand_y': 30},
    'dwarf': {'head': (8, 17), 'body': (9, 27), 'shoulder_y': 29, 'far_x': 11, 'near_x': 20, 'hand_y': 32},
    'orc':   {'head': (8, 10), 'body': (9, 22), 'shoulder_y': 24, 'far_x': 11, 'near_x': 21, 'hand_y': 29},
    'gnome': {'head': (8, 18), 'body': (11, 28), 'shoulder_y': 29, 'far_x': 13, 'near_x': 18, 'hand_y': 32},
}

# ---------------------------------------------------------------- Gesichter (3/4 nach rechts)
FACE = {
    'human': [
        "..............",
        ".....OOOOOO...",
        "....O332222O..",
        "...O33222222O.",
        "..O3322222222O",
        "..O3222222222O",
        "..O2222222222O",
        ".O22222222222O",
        ".O222222222222",
        ".O12222222221O",
        "..O122222211O.",
        "...OO111111O..",
        ".....OOOOO....",
    ],
    'dwarf': [
        "................",
        "......OOOOOO....",
        ".....O3322222O..",
        "....O332222222O.",
        "...O33222222222O",
        "..O322222222222O",
        "..O222222222222O",
        ".O2222222222223O",
        ".O22222222222233",
        ".O12222222222211",
        "..O12222222211O.",
        "...OO11111111O..",
    ],
    'orc': [
        "................",
        "......OOOOOO....",
        ".....O3322222O..",
        "....O332222222O.",
        "...O33222222222O",
        "..O322222222222O",
        "..O111222222111O",
        ".O22222222222222",
        ".O22222222222222",
        ".O2222222222222O",
        ".O2222222222221O",
        "..O22222222222O.",
        "..O12222222211O.",
        "...O111111111O..",
        "....OOOOOOOOO...",
    ],
    'gnome': [
        "................",
        "......OOOOOO....",
        ".....O3322222O..",
        "....O332222222O.",
        "...O33222222222O",
        "..O322222222222O",
        "..O222222222222O",
        ".O2222222222223O",
        ".O22222222222233",
        ".O12222222222221",
        "..O122222222211.",
        "...OO111111111O.",
        ".....OOOOOOOO...",
    ],
}
# fernes Auge (x, y) 1 breit, nahes Auge (x, y) 2 breit
EYES = {'human': ((7, 7), (10, 7)), 'dwarf': ((8, 6), (11, 6)), 'orc': ((8, 7), (11, 7)), 'gnome': ((8, 6), (11, 6))}
MOUTH = {'human': [(11, 10)], 'dwarf': [], 'orc': [(10, 12), (11, 12)], 'gnome': [(12, 10)]}
TUSKS = {'orc': [(9, 12), (12, 12)]}
EAR = {   # Ohr auf der Hinterkopfseite: (x_anker, y_anker, raster) relativ zum Gesicht
    'human': (2, 8, ["2", "1"]),
    'dwarf': (2, 7, ["2", "1"]),
    'orc': (-1, 4, ["3.", "23", "22", ".1"]),
    'gnome': (-3, 2, ["3...", "23..", "223.", ".222", "..21"]),
}

# ---------------------------------------------------------------- Frisuren (Hinterkopf links, Gesicht rechts frei)
HAIR = {
    'human': [
        [   # Kurz, seitlich nach rechts gekaemmt
            "......bbbbb...",
            "....bbcccbbb..",
            "..bbccbbbbbbb.",
            ".bbcbbbbbbbbba",
            ".bcbbbbbbbbbba",
            "bbbbbbbbbabbba",
            "bbbbbbb.ab..a.",
            "bbbba.........",
            "bbba..........",
            "bba...........",
            ".ba...........",
        ],
        [   # Lang, offen, faellt hinter die Schulter
            "......bbbbb...",
            "....bbcccbbb..",
            "..bbccbbbbbbb.",
            ".bbcbbbbbbbbba",
            ".bcbbbbbbbbbba",
            "bbbbbbbbbabbba",
            "bbbbbbb.ab..ab",
            "bbbba.......ab",
            "bbba........ab",
            "bbba.........a",
            "bbbba.........",
            "bbbba.........",
            "bbbbba........",
            ".bbbba........",
            ".abbba........",
            "..aba.........",
        ],
        [   # Pferdeschwanz hinten
            "......bbbbb...",
            "....bbcccbbb..",
            "..bbccbbbbbbb.",
            ".bbcbbbbbbbbba",
            "bbcbbbbbbbbbba",
            "bbbbbbbbbabbba",
            "bbbbbbb.a...a.",
            "bbba..........",
            "cbba..........",
            "bba...........",
            "bba...........",
            "ba............",
            "ba............",
            "a.............",
        ],
    ],
    'dwarf': [
        [   # Kurz + langer Vollbart
            "......bbbbbb....",
            "....bbcccbbbb...",
            "...bccbbbbbbbb..",
            "..bcbbbbbbbbbbb.",
            ".bbbbbbbbbbbbbba",
            "bbbbbbba.ab..ba.",
            "bbbba...........",
            "bbba............",
            "bbb.......ab.ba.",
            "bbbb..abbbbbbbbb",
            ".bbbbbbbbbbbbbba",
            "..bbcbbbbbbbbba.",
            "...abbbbbbbbba..",
            ".....aabbbbaa...",
        ],
        [   # Haarkranz + geflochtener Bart mit Goldperlen
            "................",
            "................",
            "................",
            "................",
            ".bb.............",
            "bbba............",
            "bbba............",
            "bba.............",
            "bb........bb.bb.",
            ".bbb..bbbbbbbbbb",
            "..bbbbbbbbbbbba.",
            "....bbbbbbbbba..",
            "......abbbba....",
            "........bb......",
            "........YY......",
            "........bb......",
            "........YY......",
        ],
        [   # Wilde Maehne + breiter kurzer Bart
            "...b.bbbbbbb.b..",
            "..bbbbcccbbbbbb.",
            ".bbbccbbbbbbbbbb",
            "bbbcbbbbbbbbbbbb",
            "bbbbbbbbbbbbbbba",
            "bbbbbbbbbbabbbba",
            "bbbbba......a.b.",
            "bbbba...........",
            "bbbbb.....bb.bb.",
            "bbbbbb.bbbbbbbbb",
            ".bbbbbbbbbbbbbb.",
            "..abbbbbbbbbba..",
            "....aabbbbaa....",
        ],
    ],
    'orc': [
        [   # Irokese
            "......bbb.......",
            ".....bccbb......",
            ".....bcbbbb.....",
            "......bbbbba....",
            ".......bbba.....",
        ],
        [   # Langer Zopf nach hinten + Kinnbart
            "......bbbbbb....",
            "....bbcccbbbb...",
            "...bccbbbbbbbb..",
            "..bcbbbbbbbbbba.",
            ".bbbbbbbbbbbba..",
            "bbbba...........",
            "bbba............",
            "bba.............",
            "ba..............",
            "bb..............",
            "ba..............",
            "bb..........bb..",
            "ba..........ba..",
            "a...........b...",
        ],
        [   # Haarknoten + dichter Bart
            "..bbbb..........",
            ".bccbba.........",
            "..bbba..........",
            "...bbbbbbbb.....",
            "..bcbbbbbbbba...",
            ".bbbbbbbbbbba...",
            "bbba............",
            "bba.............",
            "................",
            "................",
            ".bb.........b...",
            ".bbbb.....bbbb..",
            "..bbbbbbbbbbbb..",
            "...abbbbbbbbba..",
            "....aabbbbbaa...",
        ],
    ],
    'gnome': [
        [   # Zwei Zoepfe
            "......bbbbbb....",
            "....bbcccbbbb...",
            "...bccbbbbbbbb..",
            "..bcbbbbbbbbbbb.",
            ".bbbbbbbbbbbbbba",
            "bbbbbbbbbbabbba.",
            "bbbba.......a...",
            "bbba............",
            "bbb.............",
            ".bcb............",
            ".bbb............",
            ".bbb............",
            "..ba............",
        ],
        [   # Hohe Tolle nach rechts
            ".......bbbbb....",
            "......bcccbbbb..",
            ".....bccbbbbbbb.",
            "....bcbbbbbbbba.",
            "...bcbbbbbbbba..",
            "..bbbbbbbbbbbb..",
            ".bbbbbbbbbbbbbba",
            "bbbbbbbbbbabbba.",
            "bbbba.......a...",
            "bbba............",
            "bba.............",
        ],
        [   # Kurz, zerzaust + Schnurrbart
            ".....b.bbb.b....",
            "....bbbcbbbbb...",
            "...bcccbbbbbbb..",
            "..bccbbbbbbbbbb.",
            ".bbbbbbbbbbbbbba",
            "bbbbbbbabbabbba.",
            "bbba.b......a...",
            "bba.............",
            "b...............",
            "................",
            "...........bbb..",
        ],
    ],
}
HAIR_OFFSET = {('orc', 0): -3, ('orc', 2): -3, ('gnome', 1): -3, ('dwarf', 2): -1}

# ---------------------------------------------------------------- Koerper (3/4 nach rechts)
BODY = {
    # Mensch: weiss-goldener Kleriker mit Stola und blauer Schaerpe
    ('human', 'priest'): [
        "....kYYYk...",
        "...AAAAYya..",
        "..AAAAAYyad.",
        "..AAAAAYyad.",
        "..BBBBBYyBb.",
        "..AAAAAYyad.",
        ".AAAAAAYyadd",
        ".YYYYYYYyyyy",
        "..nN...nNN..",
        "..nn...nnn..",
    ],
    # Zwerg: Runenpriester - blaue Wolltunika, Pelzkragen, Lederschuerze, Bronzeschnalle
    ('dwarf', 'priest'): [
        "..FFFFFFFFFf..",
        ".AFfFFFFFFffa.",
        ".AAAABBBBBaad.",
        ".AAAABbYbBaad.",
        ".AAAABBBBBaad.",
        ".AAAABBBBBBad.",
        "..nNn...nNNn..",
        "..nnn...nnnn..",
    ],
    # Orc: Schamane - Lederwams, Fellumhang auf der Schulter, Knochenkette, rotes Tuch
    ('orc', 'priest'): [
        "..FFFf..........",
        ".FFFFfft.t.t....",
        ".FFfAAAtAtAtAa..",
        "..AAAAAAAAAAad..",
        "..AAAAAAAAAAad..",
        "..BBBBBBYbBBBb..",
        "..AAAAAAAAAAdd..",
        "..BBbAAAAAABbb..",
        ".BBbbAAAAAAabbb.",
        "..bb.AAAAAa.bb..",
        "...nnN....nnNN..",
        "...nnn....nnnn..",
    ],
    # Gnom: Tueftler-Priester - violetter Mantel, tuerkiser Saum, Messingknoepfe, Guertel
    ('gnome', 'priest'): [
        "..kWWk....",
        ".AAWWYaa..",
        ".AAAAYad..",
        ".LLLLYLL..",
        "AAAAAYadd.",
        "BBBBBBBbb.",
        ".nN..nNN..",
        ".nn..nnn..",
    ],
    ('human', 'warrior'): [
        "...kSSSk....",
        "..SSSRRRsz..",
        ".SsSRRYRrzz.",
        "..SsRYYYrz..",
        "..SsRRYRrz..",
        "..LLLLYlll..",
        "..SRRRRRrz..",
        "..Ss...Ssz..",
        "..Ss...Ssz..",
        ".zzz...zzzz.",
    ],
    ('dwarf', 'warrior'): [
        "....kSSSSk....",
        ".SSSSRRRRRsz..",
        ".SsSRRRYRRrzz.",
        "..SsRRYYYRrz..",
        "..LLLLLYllll..",
        "..SSS...Sszz..",
        ".zzzz...zzzzz.",
        "..............",
    ],
    ('orc', 'warrior'): [
        ".Y...kSSSSk.....",
        ".SSSSSRRRRRssz..",
        "SSsSSRRRYRRrzzz.",
        "SsssSRRYYYRrzzz.",
        "...sSRRRYRRrz...",
        "...sSRRRRRRrz...",
        "...LLLLLYllll...",
        "...SRRRRRRRrz...",
        "...SSs...SSzz...",
        "...SSs...SSzz...",
        "..zzzz...zzzzz..",
    ],
    ('gnome', 'warrior'): [
        "..kSSk....",
        "SSSRYRsz..",
        ".sSRYRrz..",
        ".LLLYlll..",
        ".Ss.Ssz...",
        "zzz.zzzz..",
    ],
}

HELMET = {
    'human': [
        ".....SSSSSS...",
        "...SSSSSSSsss.",
        "..SSSSSSSSsszz",
        "..SsRRSSSSsszz",
        ".SSSSSSSSSSszz",
        ".zzzzzzzzzzzzz",
        ".zz.......zz..",
    ],
    'dwarf': [
        "Y..............Y",
        "Y.....SSSSSS...Y",
        "YY..SSSSSSSSssYY",
        ".YSSSSSSSSSSsszY",
        ".SSSSSSSSSSSsssz",
        "zzzzzzzzzzzzzzzz",
        "zz..........zz..",
    ],
    'orc': [
        "Y...............",
        "YY....SSSSSS....",
        ".YSSSSSSSSSSsss.",
        ".SSSSSSSSSSSsssz",
        "SSSSSSSSSSSSsszz",
        "zzzzzzzzzzzzzzzz",
        "zz...........zz.",
    ],
    'gnome': [
        "........SS......",
        ".......SSSs.....",
        ".....SSSSSSss...",
        "...SSSSSSSSSsss.",
        "...SSSSSSSSSssz.",
        "..zzzzzzzzzzzzzz",
        "..zz.........zz.",
    ],
}


# ---------------------------------------------------------------- Zeichnen
def _check():
    for name, table in (('FACE', FACE), ('HELMET', HELMET)):
        for k, g in table.items():
            assert len(set(len(r) for r in g)) == 1, f'{name}[{k}] ungleich breit'
    for k, styles in HAIR.items():
        for i, g in enumerate(styles):
            assert len(set(len(r) for r in g)) == 1, f'HAIR[{k}][{i}] ungleich breit'
    for k, g in BODY.items():
        assert len(set(len(r) for r in g)) == 1, f'BODY[{k}] ungleich breit'


_check()


def _grid_to(fn, grid, x0, y0, dx_rows=None):
    for yy, row in enumerate(grid):
        sx = dx_rows(yy) if dx_rows else 0
        for xx, ch in enumerate(row):
            if ch in '. ':
                continue
            res = fn(ch)
            if res is None:
                continue
            layer, col = res
            layer.px(x0 + xx + sx, y0 + yy, col)


def _mask(layer: Canvas):
    return layer.a[:, :, 3] > 0


def _arm(layer_cloth, layer_skin, shoulder, hand, cols, hand_skin=True, glove=None, width=2):
    (sx, sy), (hx, hy) = shoulder, hand
    steps = max(abs(hx - sx), abs(hy - sy), 1)
    for i in range(steps):
        t = i / steps
        x = round(sx + (hx - sx) * t)
        y = round(sy + (hy - sy) * t)
        layer_cloth.px(x, y, cols[0])
        if width > 1:
            layer_cloth.px(x + 1, y, cols[1])
    for (dx, dy) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        if hand_skin:
            layer_skin.px(hx + dx, hy + dy, IDX[3 if (dx, dy) == (0, 0) else 2])
        else:
            layer_cloth.px(hx + dx, hy + dy, glove if dy == 0 else mix(glove, '#000000', 0.3))


def compose(race, klass, style, breath=0, hair_sway=0, hands=0.0, glow=0):
    lay = LAYOUT[race]
    L = {n: Canvas(FW, FH) for n in LAYERS}
    back = Canvas(FW, FH)            # ferner Arm hinter dem Rumpf
    hx0, hy0 = lay['head']
    bx0, by0 = lay['body']
    hy = hy0 + breath
    pal = dict(OUTFIT_PAL[(race, klass)])
    pal['k'] = OUTLINE

    # Arme
    sy = lay['shoulder_y']
    far_x, near_x = lay['far_x'], lay['near_x']
    rest_far = (far_x - 1, lay['hand_y'] - 1)
    rest_near = (near_x + 1, lay['hand_y'])
    mid_far = (far_x - 3, sy - 1)
    mid_near = (near_x + 2, sy - 1)
    up_far = (far_x - 4, sy - 7)
    up_near = (near_x + 3, sy - 7)

    def pick(a, b, c_, t):
        if t <= 1:
            return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t))
        t -= 1
        return (round(b[0] + (c_[0] - b[0]) * t), round(b[1] + (c_[1] - b[1]) * t))
    h_far = pick(rest_far, mid_far, up_far, hands)
    h_near = pick(rest_near, mid_near, up_near, hands)
    if klass == 'priest':
        sl = SLEEVE[(race, klass)]
        _arm(back, back, (far_x, sy), h_far, (mix(sl[1], '#000000', 0.2), mix(sl[1], '#000000', 0.35)))
        skin_far = Canvas(FW, FH)
        _arm(back, skin_far, (far_x, sy), h_far, (mix(sl[1], '#000000', 0.2), mix(sl[1], '#000000', 0.35)))
    else:
        _arm(back, back, (far_x, sy), h_far, (pal['s'], pal['z']), hand_skin=False, glove=pal['z'])
        skin_far = None

    # Koerper
    body = BODY[(race, klass)]
    body_layer = Canvas(FW, FH)
    _grid_to(lambda ch: (body_layer, pal[ch]) if ch in pal else None, body, bx0, by0)

    # Reihenfolge: ferner Arm, Rumpf, naher Arm
    L['outfit'].paste(back, 0, 0)
    if skin_far is not None:
        # Hand des fernen Arms in die Hautebene, aber unter dem Rumpf verdeckt
        cover = _mask(body_layer)
        sk = skin_far.a.copy()
        sk[cover] = 0
        L['skin'].a = np.where(sk[:, :, 3:4] > 0, sk, L['skin'].a)
    L['outfit'].paste(body_layer, 0, 0)
    if klass == 'priest':
        sl = SLEEVE[(race, klass)]
        _arm(L['outfit'], L['skin'], (near_x - 1, sy), h_near, sl)
    else:
        _arm(L['outfit'], L['skin'], (near_x - 1, sy), h_near, (pal['S'], pal['s']), hand_skin=False, glove=pal['s'])

    # Gesicht
    _grid_to(lambda ch: (L['skin'], IDX[{'O': 0, '1': 1, '2': 2, '3': 3}[ch]]) if ch in 'O123' else None,
             FACE[race], hx0, hy)
    dark, iris = EYE_COLORS[race]
    (fx, fy), (nx, ny) = EYES[race]
    # fernes Auge (schmal)
    L['eyes'].px(hx0 + fx, hy + fy, dark)
    L['eyes'].px(hx0 + fx, hy + fy + 1, iris)
    L['eyes_closed'].px(hx0 + fx, hy + fy + 1, dark)
    # nahes Auge (gross, mit Glanz)
    L['eyes'].px(hx0 + nx, hy + ny, dark)
    L['eyes'].px(hx0 + nx + 1, hy + ny, dark)
    L['eyes'].px(hx0 + nx, hy + ny + 1, '#ffffff')
    L['eyes'].px(hx0 + nx + 1, hy + ny + 1, iris)
    L['eyes_closed'].px(hx0 + nx, hy + ny + 1, dark)
    L['eyes_closed'].px(hx0 + nx + 1, hy + ny + 1, dark)
    for (mx, my) in MOUTH.get(race, []):
        L['skin'].px(hx0 + mx, hy + my, IDX[1])
    for (tx, ty) in TUSKS.get(race, []):
        L['outfit'].px(hx0 + tx, hy + ty, '#f4ecd0')
        L['outfit'].px(hx0 + tx, hy + ty - 1, '#f4ecd0')

    # Frisur
    grid = HAIR[race][style]
    off = HAIR_OFFSET.get((race, style), 0)

    def hair_map(ch):
        if ch in 'abc':
            return (L['hair'], IDX[{'a': 1, 'b': 2, 'c': 3}[ch]])
        if ch in 'Yy':
            return (L['gear'], {'Y': '#f5c95a', 'y': '#b8862e'}[ch])
        return None

    def sway(yy):
        return -hair_sway if (yy + off) >= 9 and grid[yy][:4].strip('.') else 0
    _grid_to(hair_map, grid, hx0, hy + off, dx_rows=sway)
    if klass == 'warrior':
        helm = HELMET[race]
        hm = np.zeros((FH, FW), bool)
        for yy, row in enumerate(helm):
            for xx, ch in enumerate(row):
                if ch not in '. ':
                    hm[hy - 2 + yy, hx0 + xx] = True
        L['hair'].a[hm] = 0
        _grid_to(lambda ch: (L['gear'], pal[ch]) if ch in pal else None, helm, hx0, hy - 2)
    # Ohr auf der Hinterkopfseite (ueber den Haaren sichtbar)
    if race in EAR:
        ax, ay, eg = EAR[race]
        for yy, row in enumerate(eg):
            for xx, ch in enumerate(row):
                if ch in '123':
                    X, Y = hx0 + ax + xx, hy + ay + yy
                    L['hair'].clear_px(X, Y)
                    L['gear'].clear_px(X, Y)
                    L['skin'].px(X, Y, IDX[int(ch)])

    # Schatten unter dem Pony
    hair_m = _mask(L['hair'])
    skin_a = L['skin'].a
    below = np.zeros_like(hair_m)
    below[1:, :] = hair_m[:-1, :]
    sel = below & ~hair_m & (skin_a[:, :, 3] > 0) & (skin_a[:, :, 0] > 100)
    skin_a[sel] = IDX[1]

    # Lichtzauber
    if glow > 0:
        pts = {1: [(0, 0)], 2: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)],
               3: [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, -2), (0, 2)]}[glow]
        for (gx, gy) in (h_far, h_near):
            for (dx, dy) in pts:
                d = abs(dx) + abs(dy)
                L['gear'].px(gx + dx, gy - 2 + dy, '#ffffff' if d == 0 else ('#ffe38a' if d == 1 else '#f5c95a'))

    # Aussenkontur
    solid = np.zeros((FH, FW), bool)
    for n in LAYERS:
        if n != 'eyes_closed':
            solid |= _mask(L[n])
    for y, x in zip(*np.where(HD.border_of(solid))):
        L['outfit'].px(x, y, OUTLINE)
    # Innenkontur: Haar/Gesicht, Kopf/Koerper
    for y, x in zip(*np.where(HD.border_of(hair_m) & (skin_a[:, :, 3] > 0) & ~hair_m)):
        if L['eyes'].a[y, x, 3] == 0:
            if hair_m[y, max(0, x - 1)] or hair_m[y, min(FW - 1, x + 1)]:
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
