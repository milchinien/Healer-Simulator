import sys
from pa import Canvas
import rig3 as R, chars
out = Canvas(32 * 12, 36 * 4 + 12, '#6e6e6e')
i = 0
for race in ['human', 'dwarf', 'orc', 'gnome']:
    for s in range(3):
        for row, (klass, fr) in enumerate([('priest', 0), ('priest', 13), ('warrior', 0), ('warrior', 3)]):
            L = R.frames(race, klass, s)[fr]
            out.paste(R.preview_frame(race, klass, s, chars.SKIN_PALETTES[race][(s + 1) % 5], chars.HAIR_PALETTES[race][(s * 2 + 1) % 5], L), i * 32, row * 39)
        i += 1
out.save_preview('C:/Users/tobia/AppData/Local/Temp/rig3.png', scale=int(sys.argv[1]) if len(sys.argv) > 1 else 3, bg=(110, 110, 110, 255))
zoom = Canvas(32 * 4, 36, '#6e6e6e')
for k, race in enumerate(['human', 'dwarf', 'orc', 'gnome']):
    L = R.frames(race, 'priest', 0)[0]
    zoom.paste(R.preview_frame(race, 'priest', 0, chars.SKIN_PALETTES[race][1], chars.HAIR_PALETTES[race][1], L), k * 32, 0)
zoom.save_preview('C:/Users/tobia/AppData/Local/Temp/rig3_zoom.png', scale=9, bg=(110, 110, 110, 255))
