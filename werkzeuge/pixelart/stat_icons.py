"""Symbole der Werte (16x16) fuer die Segen-Wahl und spaetere Charakterwerte, plus Gruppen-Abzeichen.

Aufruf: python stat_icons.py            (schreibt nach ../../healer-simulator/assets/gfx/stats)
"""
from __future__ import annotations

import os
import sys

from pa import Canvas, from_grid

K = '#120e18'
PAL = {
    'k': K,
    # Rot (HP)
    'R': '#ff5a5a', 'r': '#d02a36', 'q': '#7a1422',
    # Blau (Mana)
    'B': '#8ad0ff', 'b': '#3a7ae8', 'n': '#1a3a8a',
    # Gold / Licht
    'Y': '#ffe08a', 'y': '#f2c14e', 'o': '#b8862e',
    # Weiss / Silber
    'W': '#ffffff', 'S': '#c4c0d0', 's': '#8a8698', 'd': '#4a4656',
    # Gruen (Regeneration)
    'G': '#9af07a', 'g': '#3cb43c', 'h': '#1e6a2a',
    # Violett (Resistenz / Magie)
    'V': '#d8a8ff', 'v': '#9a4ae0', 'u': '#4a2080',
    # Braun (Holz/Griff)
    'L': '#b07a4a', 'l': '#6a4424',
}

ICONS = {
    'hp': [
        '................',
        '..kkkk....kkkk..',
        '.kRRrrk..kRRrrk.',
        'kRWRrrrkkrRRrrrk',
        'kRRrrrrrrrrrrrqk',
        'kRrrrrrrrrrrrrqk',
        'krrrrrrrrrrrrrqk',
        '.krrrrrrrrrrrqk.',
        '..krrrrrrrrrqk..',
        '...krrrrrrrqk...',
        '....krrrrrqk....',
        '.....krrrqk.....',
        '......krqk......',
        '.......kk.......',
        '................',
        '................',
    ],
    'hp_reg': [
        '.........kkk....',
        '..kkkk...kGk....',
        '.kRRrrk.kkGkk...',
        'kRWRrrrkkGGGGk..',
        'kRRrrrrkkkGkkk..',
        'kRrrrrrrrkGkqk..',
        'krrrrrrrrrkkqk..',
        '.krrrrrrrrrrqk..',
        '..krrrrrrrrqk...',
        '...krrrrrrqk....',
        '....krrrrqk.....',
        '.....krrqk......',
        '......kqk.......',
        '.......k........',
        '................',
        '................',
    ],
    'mana': [
        '.......kk.......',
        '......kBBk......',
        '......kBbk......',
        '.....kBBbbk.....',
        '....kBBbbbbk....',
        '....kBWbbbbk....',
        '...kBWBbbbbbk...',
        '...kBBbbbbbbk...',
        '..kBBbbbbbbbnk..',
        '..kBbbbbbbbbnk..',
        '..kbbbbbbbbbnk..',
        '..kbbbbbbbbnnk..',
        '...kbbbbbbnnk...',
        '....kknnnnkk....',
        '......kkkk......',
        '................',
    ],
    'mana_reg': [
        '......kk...kkk..',
        '.....kBBk..kGk..',
        '.....kBbk.kkGkk.',
        '....kBBbbkkGGGGk',
        '...kBBbbbbkkGkk.',
        '...kBWbbbbkkGk..',
        '..kBWBbbbbbkkk..',
        '..kBBbbbbbbk....',
        '.kBBbbbbbbbnk...',
        '.kBbbbbbbbbnk...',
        '.kbbbbbbbbbnk...',
        '.kbbbbbbbbnnk...',
        '..kbbbbbbnnk....',
        '...kknnnnkk.....',
        '.....kkkk.......',
        '................',
    ],
    'heal_power': [
        '.....kkkkkk.....',
        '.....kYYYyk.....',
        '.....kYWYyk.....',
        '.....kYYYyk.....',
        'kkkkkkYYYykkkkkk',
        'kYYYYYYWYYYYYyyk',
        'kYWWWYWWWYWWYyyk',
        'kYYYYYYWYYYYYyok',
        'kkkkkkYYYykkkkkk',
        '.....kYYYyk.....',
        '.....kYYyyk.....',
        '.....kYYyyk.....',
        '.....kyyyok.....',
        '.....kyyook.....',
        '.....kkkkkk.....',
        '................',
    ],
    'damage': [
        '.............kk.',
        '............kWSk',
        '...........kWSk.',
        '..........kWSk..',
        '.........kWSk...',
        '........kWSk....',
        '.......kWSk.....',
        '..kk..kWSk......',
        '..kok kWSk......',
        '...kokWSk.......',
        '....koSk........',
        '...kLkok........',
        '..kLlk.kk.......',
        '.kLlk...........',
        '.kkk............',
        '................',
    ],
    'crit': [
        '.......kk.......',
        '.......kYk......',
        '..k....kYk....k.',
        '..kYk.kYYYk..kYk',
        '...kYkYWWYYkkYk.',
        '....kYWWWWYYYk..',
        '.kkkYWWWWWWYkkkk',
        'kYYYYWWWWWWYYYYk',
        '.kkkkYWWWWYYkkk.',
        '....kYYWWYYYk...',
        '...kYkkYYYkkYk..',
        '..kYk..kYk..kYk.',
        '..kk...kYk...kk.',
        '.......kyk......',
        '........k.......',
        '................',
    ],
    'haste': [
        '...kkkkkkkkkk...',
        '...kooooooook...',
        '....kYYYYYYk....',
        '....kYYYYYYk....',
        '.....kYYYYk.....',
        '......kYYk......',
        '.......kk.......',
        '......kWSk......',
        '.....kSSSSk.....',
        '....kSSSSSSk....',
        '....kSYYYYSk....',
        '...kSYYYYYYSk...',
        '...kooooooook...',
        '...kkkkkkkkkk...',
        '................',
        '................',
    ],
    'armor': [
        '..kkkkkkkkkkkk..',
        '..kSSSSSSSSssk..',
        '..kSWSSSSSSssk..',
        '..kSSSoooosssk..',
        '..kSSSoYYosssk..',
        '..kSSSoYYosssk..',
        '..kSSSoooosssk..',
        '..kSSSSSSSssdk..',
        '...kSSSSSSssk...',
        '...kSSSSSsssk...',
        '....kSSSSssk....',
        '.....kSSssk.....',
        '......kssk......',
        '.......kk.......',
        '................',
        '................',
    ],
    'resist': [
        '.....kkkkkk.....',
        '...kkVVVVvvkk...',
        '..kVVWVVVvvvuk..',
        '.kVVWVVVVVvvuuk.',
        '.kVWVVVkkVvvvuk.',
        'kVVVVVkYYkvvvuuk',
        'kVVVVkYWYYkvvvuk',
        'kVVVVkYYYykvvuuk',
        'kVVVVVkyykvvvuuk',
        '.kVVVVVkkvvvvuk.',
        '.kvVVVVvvvvvuuk.',
        '..kvvvvvvvvuuk..',
        '...kkvvvvuukk...',
        '.....kkkkkk.....',
        '................',
        '................',
    ],
}

GROUP_BADGE = [
    '.kk.kk.kk.',
    'kSSkSSkSSk',
    'kSSkSSkSSk',
    '.kk.kk.kk.',
    'kSSkSSkSSk',
    'kSSSSSSSSk',
    '.kkkkkkkk.',
]


def icon(name) -> Canvas:
    rows = [r.replace(' ', '.') for r in ICONS[name]]
    return from_grid(rows, PAL, w=16)


def build(root):
    out = os.path.join(root, 'assets', 'gfx', 'stats')
    os.makedirs(out, exist_ok=True)
    for name in ICONS:
        icon(name).save(os.path.join(out, f'{name}.png'))
    from_grid(GROUP_BADGE, PAL).save(os.path.join(out, 'group_badge.png'))


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', 'healer-simulator')
    build(root)
    # Vorschau
    names = list(ICONS)
    prev = Canvas(len(names) * 20, 20, '#1d1626')
    for i, n in enumerate(names):
        prev.paste(icon(n), i * 20 + 2, 2)
    prev.save_preview(os.path.join(here, '..', '..', 'output', 'kampf', 'stat_icons.png'), scale=5)
