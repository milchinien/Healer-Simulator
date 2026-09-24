"""Erzeugt alle Grafiken, Sounds und Daten fuer ein Prototyp-Projekt.

Aufruf:  python werkzeuge/build_assets.py prototypen/p01_charakter_menue
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'pixelart'))

import chars as C  # noqa: E402
import heads as HD  # noqa: E402
import icons as I  # noqa: E402
import ui as U  # noqa: E402
import logo as L  # noqa: E402
import effects as FX  # noqa: E402
import scenes as SC  # noqa: E402
import scenes_race as SR  # noqa: E402
import sfx as SFX  # noqa: E402
from pa import Canvas  # noqa: E402

CLASSES = ['priest', 'warrior']


def out(root, rel):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def build_chars(root):
    import rig as RG
    for race in C.RACE_IDS:
        for klass in CLASSES:
            for style in range(3):
                RG.sheet(race, klass, style).save(out(root, f'assets/gfx/chars/{race}_{klass}_{style}.png'))
        # Portrait fuer die Rassenwahl (Kopf des Priesters, Standard-Aussehen)
        h = HD.HEAD[race]
        L = RG.frames(race, 'priest', 0)[0]
        comp = RG.preview_frame(race, 'priest', 0, C.SKIN_PALETTES[race][1], C.HAIR_PALETTES[race][1], L)
        cx, cy = int(h['cx']), int(h['cy'])
        head = comp.crop(cx - 8, cy - 7, 17, 17)
        bgc = {'human': ('#3a5a9a', '#1e2a4a'), 'dwarf': ('#8a4a2a', '#3a1e14'),
               'orc': ('#6a2a2a', '#2a1014'), 'gnome': ('#2a6a7a', '#12303a')}[race]
        I.race_portrait(race, head, *bgc).save(out(root, f'assets/gfx/icons/race_{race}.png'))


def build_ui(root):
    U.SLICES.clear()
    items = {
        'panel': U.panel(), 'panel_plain': U.panel_plain(), 'header': U.header_plate(),
        'tooltip': U.tooltip(), 'separator': U.separator(),
    }
    for kind in ('red', 'dark'):
        for st in ('normal', 'hover', 'pressed', 'disabled'):
            items[f'btn_{kind}_{st}'] = U.button(kind, st)
    for st in ('normal', 'hover', 'selected'):
        items[f'list_{st}'] = U.list_entry(st)
        items[f'tile_{st}'] = U.tile(st)
        items[f'tab_{st}'] = U.tab(st)
    for st in ('normal', 'focus'):
        items[f'input_{st}'] = U.input_field(st)
    track, fill, knobs = U.slider_parts()
    items['slider_track'] = track
    items['slider_fill'] = fill
    tr, gr = U.scrollbar()
    items['scroll_track'] = tr
    items['scroll_grabber'] = gr
    pb, pf = U.progress_bar()
    items['progress_bg'] = pb
    items['progress_fill'] = pf
    for name, cv in items.items():
        cv.save(out(root, f'assets/gfx/ui/{name}.png'))
    for st, k in knobs.items():
        k.save(out(root, f'assets/gfx/ui/slider_knob_{st}.png'))
    for st, cv in U.checkbox().items():
        cv.save(out(root, f'assets/gfx/ui/check_{st}.png'))
    for d in ('left', 'right'):
        for st in ('normal', 'hover', 'pressed', 'disabled'):
            U.arrow_button(d, st).save(out(root, f'assets/gfx/ui/arrow_{d}_{st}.png'))
    U.swatch_frame(False).save(out(root, 'assets/gfx/ui/swatch_frame.png'))
    U.swatch_frame(True).save(out(root, 'assets/gfx/ui/swatch_frame_sel.png'))
    with open(out(root, 'data/ui_slices.json'), 'w', encoding='utf-8') as f:
        json.dump(U.SLICES, f, indent=1)


def build_icons(root):
    icons = {
        'gender_male': I.gender_male(), 'gender_female': I.gender_female(), 'skull': I.skull('big'),
        'skull_small': I.skull('small'), 'mode_normal': I.sun_shield(), 'dice': I.dice(), 'coin': I.coin(),
        'clock': I.clock(), 'flag': I.flag(), 'spec_holy': I.spec_icon('holy'), 'spec_shadow': I.spec_icon('shadow'),
        'spec_discipline': I.spec_icon('discipline'), 'gear': I.gear(), 'door': I.door(), 'trash': I.trash(),
        'check': I.check(),
    }
    for name, cv in icons.items():
        cv.save(out(root, f'assets/gfx/icons/{name}.png'))
    I.cursor_pointer().save(out(root, 'assets/gfx/cursor/pointer.png'))
    I.cursor_text().save(out(root, 'assets/gfx/cursor/text.png'))


def build_scenes(root):
    import scenes_v2 as V1
    import scenes_v2b as V2
    meta = {}
    jobs = [(V2, 'title'), (V1, 'charselect'), (V2, 'human_city'), (V2, 'dwarf_hall'), (V2, 'orc_steppe'),
            (V2, 'gnome_workshop'), (V2, 'loading_gruenhain')]
    for mod, name in jobs:
        t = time.time()
        sc = getattr(mod, name)()
        for lname, cv in sc['layers'].items():
            cv.save(out(root, f'assets/gfx/bg/{name}_{lname}.png'))
        for sname, cv in sc['sprites'].items():
            cv.save(out(root, f'assets/gfx/bg/{sname}.png'))
        meta[name] = {'layers': list(sc['layers'].keys()), 'props': sc['props'], 'stand': sc['stand']}
        print(f'  Szene {name}: {time.time() - t:.1f}s, {len(sc["props"])} Elemente')
    with open(out(root, 'data/scenes.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=1)


def build_fx(root):
    import props as PR
    PR.fire().save(out(root, 'assets/gfx/fx/fire.png'))
    PR.lantern_flame().save(out(root, 'assets/gfx/fx/lantern_flame.png'))
    for name, cv in {
        'glow_tiny': PR.glow(5, '#ffc070', 0.9), 'glow_small': PR.glow(11, '#ffc070', 0.8),
        'glow_lamp': PR.glow(24, '#ffc070', 0.75), 'glow_window': PR.glow(9, '#ffb050', 0.6),
        'glow_forge': PR.glow(56, '#ff9a3a', 0.6), 'glow_rune': PR.glow(10, '#ffb04a', 0.8),
        'glow_lava': PR.glow(44, '#ff7a2a', 0.55), 'pool_lamp': PR.light_pool(44, 13, '#ffb060', 0.55),
        'pool_fire': PR.light_pool(50, 15, '#ff9a4a', 0.6),
    }.items():
        cv.save(out(root, f'assets/gfx/fx/{name}.png'))
    FX.glow(24, '#ffc070').save(out(root, 'assets/gfx/fx/glow_warm.png'))
    FX.glow(40, '#ffd890').save(out(root, 'assets/gfx/fx/glow_big.png'))
    FX.glow(24, '#a0c8ff').save(out(root, 'assets/gfx/fx/glow_cold.png'))
    FX.glow(20, '#8ff0e0').save(out(root, 'assets/gfx/fx/glow_teal.png'))
    FX.light_beam().save(out(root, 'assets/gfx/fx/beam.png'))
    FX.particle_dot().save(out(root, 'assets/gfx/fx/dot.png'))
    FX.sparkle().save(out(root, 'assets/gfx/fx/sparkle.png'))
    FX.soft_shadow().save(out(root, 'assets/gfx/fx/shadow.png'))
    L.build(os.path.join(root, 'assets/fonts/DungeonMode.ttf')).save(out(root, 'assets/gfx/logo.png'))
    # Programm-Icon: goldenes Sonnenkreuz auf dunklem Grund (32 px, x4 skaliert)
    ic = Canvas(32, 32)
    ic.rect(2, 2, 28, 28, '#1d1626')
    ic.frame(1, 1, 30, 30, '#0e0a14')
    ic.frame(2, 2, 28, 28, '#c99a3a')
    ic.hline(3, 28, 3, '#ffe08a')
    ic.circle(15.5, 15.5, 7, '#8a6424')
    ic.circle(15.5, 15.5, 6, '#f2c14e')
    ic.rect(14, 5, 4, 22, '#fff6c8')
    ic.rect(7, 12, 18, 4, '#fff6c8')
    ic.frame(13, 4, 6, 24, '#8a6424')
    ic.rect(14, 5, 4, 22, '#fff6c8')
    ic.rect(7, 12, 18, 4, '#fff6c8')
    img = ic.image().resize((128, 128), 0)
    img.save(out(root, 'assets/gfx/icon.png'))


def build_data(root):
    import rig as RG
    data = {
        'frame_size': [RG.FW, RG.FH],
        'frames': RG.FRAME_COUNT,
        'layers': RG.LAYERS,
        'anims': RG.ANIMS,
        'outline': C.OUTLINE,
        'races': C.RACE_IDS,
        'skin_palettes': C.SKIN_PALETTES,
        'hair_palettes': C.HAIR_PALETTES,
        'feet_y': C.FH - 1,
        'head_center': {r: [HD.HEAD[r]['cx'], HD.HEAD[r]['cy']] for r in C.RACE_IDS},
    }
    with open(out(root, 'data/characters.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)


def main():
    root = os.path.abspath(sys.argv[1])
    t0 = time.time()
    print('Figuren ...')
    build_chars(root)
    print('UI ...')
    build_ui(root)
    print('Icons ...')
    build_icons(root)
    print('Effekte + Logo ...')
    build_fx(root)
    print('Daten ...')
    build_data(root)
    print('Sounds ...')
    SFX.build(os.path.join(root, 'assets/sfx'))
    print('Hintergruende ...')
    build_scenes(root)
    print(f'Fertig in {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()
