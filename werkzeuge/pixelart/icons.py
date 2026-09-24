"""Icons (mehr Pixel als die Figuren) und Mauszeiger."""
from __future__ import annotations

from pa import Canvas, from_grid, mix, shade

INK = '#0e0a14'
GOLD_L = '#ffe08a'
GOLD = '#f2c14e'
GOLD_M = '#c99a3a'
GOLD_D = '#8a6424'


def _g(rows, legend):
    return from_grid(rows, legend)


def gender_male():
    return _g([
        '.....kkkk',
        '......kbk',
        '.kkk.kbbk',
        'kbbbkbk.k',
        'kbkkbk...',
        'kbk.kbk..',
        'kbk.kbk..',
        'kbbbbk...',
        '.kkkk....',
    ], {'k': INK, 'b': '#8fc0ff'})


def gender_female():
    return _g([
        '..kkkk...',
        '.kbbbbk..',
        'kbk..kbk.',
        'kbk..kbk.',
        '.kbbbbk..',
        '..kbbk...',
        '.kbbbbk..',
        '..kbbk...',
        '...kk....',
    ], {'k': INK, 'b': '#ff9ccf'})


def skull(size='big'):
    if size == 'small':
        return _g([
            '.kkkkk.',
            'kwwwwwk',
            'kwkwkwk',
            'kwwwwwk',
            '.kwkwk.',
            '..kkk..',
        ], {'k': INK, 'w': '#e8e2d6'})
    return _g([
        '...kkkkkk...',
        '..kwwwwwwk..',
        '.kwwwwwwwwk.',
        'kwwwwwwwwwsk',
        'kwkkkwwkkksk',
        'kwkrkwwkrksk',
        'kwkkkwwkkksk',
        '.kwwwkkwwsk.',
        '..kswwwwsk..',
        '..kwkwkwkk..',
        '...kkkkkk...',
    ], {'k': INK, 'w': '#efe9dc', 's': '#b3aa9c', 'r': '#e0402f'})


def sun_shield():
    """Symbol fuer den Normal-Modus: Schild mit Lichtstrahl."""
    return _g([
        'kkkkkkkkkkkk',
        'kGYYYYYYYYgk',
        'kYwwwYYwwwgk',
        'kYwwwYYwwwgk',
        'kYYYYYYYYYgk',
        'kYYYYYYYYYgk',
        'kYwwwYYwwwgk',
        '.kYwwYYwwgk.',
        '.kYYwYYwYgk.',
        '..kYYYYYgk..',
        '...kYYYgk...',
        '....kkkk....',
    ], {'k': INK, 'G': GOLD_L, 'Y': GOLD, 'g': GOLD_D, 'w': '#fff6d6'})


def dice():
    return _g([
        '.kkkkkkkkk.',
        'kwwwwwwwwsk',
        'kwkwwwwwwsk',
        'kwwwwwwwwsk',
        'kwwwwkwwwsk',
        'kwwwwwwwwsk',
        'kwwwwwwkwsk',
        'kwwwwwwwwsk',
        'ksssssssssk',
        '.kkkkkkkkk.',
    ], {'k': INK, 'w': '#f4efe4', 's': '#b8b0a2'})


def coin():
    return _g([
        '.kkkk.',
        'kGYYgk',
        'kYGYgk',
        'kYYYgk',
        'kggggk',
        '.kkkk.',
    ], {'k': INK, 'G': GOLD_L, 'Y': GOLD, 'g': GOLD_D})


def clock():
    return _g([
        '.kkkkk.',
        'kwwkwwk',
        'kwwkwwk',
        'kwwkkwk',
        'kwwwwwk',
        '.kkkkk.',
    ], {'k': INK, 'w': '#d8d2e6'})


def flag():
    return _g([
        'krrrrk.',
        'krrrrrk',
        'krrrrk.',
        'kkkkk..',
        'k......',
        'k......',
    ], {'k': INK, 'r': '#5aa0e0'})


def spec_icon(spec):
    if spec == 'holy':
        return _g([
            '...k...',
            '.k.Y.k.',
            '..YYY..',
            'kYYWYYk',
            '..YYY..',
            '.k.Y.k.',
            '...k...',
        ], {'k': GOLD_D, 'Y': GOLD, 'W': '#fffbe6'})
    if spec == 'shadow':
        return _g([
            '..ppp..',
            '.pPPkp.',
            'pPkkPPp',
            'pPkPkPp',
            'pPPkkPp',
            '.pkPPp.',
            '..ppp..',
        ], {'k': '#1b0f2a', 'P': '#9b5de5', 'p': '#5a2d8a'})
    return _g([   # Disziplin: halb Licht, halb Schatten
        '..kkk..',
        '.kYYpk.',
        'kYYWppk',
        'kYYWPpk',
        'kYYWppk',
        '.kYYpk.',
        '..kkk..',
    ], {'k': INK, 'Y': GOLD, 'W': '#fffbe6', 'P': '#9b5de5', 'p': '#5a2d8a'})


def gear():
    return _g([
        '...kk...',
        '.kkggkk.',
        '.kgggkk.',
        'kggkkggk',
        'kggkkggk',
        '.kkgggk.',
        '.kkggkk.',
        '...kk...',
    ], {'k': INK, 'g': '#c8c2d4'})


def door():
    return _g([
        'kkkkkk.',
        'kbbbbk.',
        'kbbbbk.',
        'kbbGbk.',
        'kbbbbk.',
        'kbbbbk.',
        'kkkkkk.',
    ], {'k': INK, 'b': '#8a5a36', 'G': GOLD})


def trash():
    return _g([
        '..kkk..',
        'kkkkkkk',
        '.kgkgk.',
        '.kgkgk.',
        '.kgkgk.',
        '.kgkgk.',
        '..kkk..',
    ], {'k': INK, 'g': '#c8c2d4'})


def check():
    return _g([
        '......k',
        '.....kg',
        'k...kg.',
        'gk.kg..',
        '.gkg...',
        '..g....',
    ], {'k': '#3d9a3a', 'g': '#8ff08a'})


def cursor_pointer():
    """Mauszeiger: Kettenhandschuh-Hand wie in klassischen MMOs."""
    return _g([
        'kk..........',
        'kGk.........',
        'kGGk........',
        'kGYGk.......',
        'kGYYGk......',
        'kGYYYGk.....',
        'kGYYYYGk....',
        'kGYYYYYGk...',
        'kGYYYYYYGk..',
        'kGYYYYkkkkk.',
        'kGYkYYk.....',
        'kGk.kYYk....',
        'kk..kYYk....',
        '.....kYYk...',
        '.....kkk....',
    ], {'k': INK, 'G': '#fff2c0', 'Y': GOLD_M})


def cursor_text():
    return _g([
        'kkk.kkk',
        '.kwkwk.',
        '..kwk..',
        '..kwk..',
        '..kwk..',
        '..kwk..',
        '..kwk..',
        '.kwkwk.',
        'kkk.kkk',
    ], {'k': INK, 'w': '#f4e9cf'})


def race_portrait(race, head_canvas: Canvas, bg_top, bg_bot):
    """18x18 Portrait: Kopf des Priesters vor einem Farbverlauf."""
    cv = Canvas(18, 18)
    cv.vgradient(0, 0, 18, 18, [bg_top, bg_bot])
    cv.paste(head_canvas, 0, 0)
    return cv
