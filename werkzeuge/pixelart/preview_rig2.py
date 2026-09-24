import sys
from pa import Canvas
import rig2 as R, chars
klass = sys.argv[1] if len(sys.argv) > 1 else 'priest'
out = Canvas(R.FW * 12, R.FH * 2 + 4, '#6e6e6e')
i = 0
for race in ['human', 'dwarf', 'orc', 'gnome']:
    for s in range(3):
        L = R.frames(race, klass, s)[0]
        out.paste(R.preview_frame(race, klass, s, chars.SKIN_PALETTES[race][(s + 1) % 5], chars.HAIR_PALETTES[race][(s * 2 + 1) % 5], L), i * R.FW, 0)
        L2 = R.frames(race, klass, s)[13]
        out.paste(R.preview_frame(race, klass, s, chars.SKIN_PALETTES[race][(s + 1) % 5], chars.HAIR_PALETTES[race][(s * 2 + 1) % 5], L2), i * R.FW, R.FH + 4)
        i += 1
out.save_preview(f'C:/Users/tobia/AppData/Local/Temp/rig2_{klass}.png', scale=int(sys.argv[2]) if len(sys.argv) > 2 else 4, bg=(110, 110, 110, 255))
