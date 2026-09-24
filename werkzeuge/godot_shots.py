"""Startet ein Prototyp-Projekt mehrfach und speichert Screenshots (Test-Werkzeug).

Aufruf: python werkzeuge/godot_shots.py <projektordner> <zielordner> [name ...]
Ohne Namen werden alle Standard-Aufnahmen gemacht.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

from PIL import Image

GODOT = r'C:\Users\tobia\Downloads\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64_console.exe'

SHOTS = {
    'title': ['scene=title'],
    'select': ['scene=character_select'],
    'select_menu': ['scene=character_select', 'dialog=menu'],
    'select_options': ['scene=character_select', 'dialog=options'],
    'select_delete': ['scene=character_select', 'dialog=delete'],
    'create_human': ['scene=character_create'],
    'create_dwarf': ['scene=character_create', 'race=dwarf', 'gender=female'],
    'create_orc': ['scene=character_create', 'race=orc', 'mode=hardcore'],
    'create_gnome': ['scene=character_create', 'race=gnome', 'gender=female'],
    'create_hardcore': ['scene=character_create', 'dialog=hardcore'],
    'loading': ['scene=loading'],
}


def run(project, out_dir, names, lang='en', frames=110):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for name in names:
        path = os.path.join(out_dir, f'{name}.png').replace('\\', '/')
        args = [GODOT, '--path', project, '--', 'profile=shots', 'demo=1', f'shot={path}', f'frames={frames}',
                f'lang={lang}'] + SHOTS[name]
        p = subprocess.run(args, capture_output=True, text=True, timeout=90)
        errs = [l for l in (p.stdout + p.stderr).splitlines()
                if ('ERROR' in l or 'SCRIPT' in l) and 'leaked' not in l and 'RID allocations' not in l]
        if errs:
            print(f'[{name}]')
            for e in errs[:8]:
                print('   ', e)
        if os.path.exists(path):
            im = Image.open(path)
            im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(path.replace('.png', '_2x.png'))
            results.append(path)
    return results


if __name__ == '__main__':
    project, out_dir = sys.argv[1], sys.argv[2]
    names = sys.argv[3:] or list(SHOTS.keys())
    lang = 'en'
    if names and names[0].startswith('lang='):
        lang = names.pop(0).split('=')[1]
        names = names or list(SHOTS.keys())
    for r in run(project, out_dir, names, lang):
        print('ok', r)
