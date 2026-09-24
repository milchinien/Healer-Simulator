import sys
from pa import Canvas
import rig, chars
races = sys.argv[1].split(',') if len(sys.argv)>1 else ['human','dwarf','orc','gnome']
klass = sys.argv[2] if len(sys.argv)>2 else 'priest'
frames_sel = [0,2,4,6, 8,10,12,13,15,17]
out = Canvas(rig.FW*len(frames_sel), rig.FH*len(races)*3, '#2b2536')
for ri, race in enumerate(races):
    for s in range(3):
        fr = rig.frames(race, klass, s)
        for j, f in enumerate(frames_sel):
            cv = rig.preview_frame(race, klass, s, chars.SKIN_PALETTES[race][(s+1)%5], chars.HAIR_PALETTES[race][(s*2+1)%5], fr[f])
            out.paste(cv, j*rig.FW, (ri*3+s)*rig.FH)
out.save_preview('C:/Users/tobia/AppData/Local/Temp/rig.png', scale=int(sys.argv[3]) if len(sys.argv)>3 else 4)
