import sys
from pa import Canvas
import chars as C
out = Canvas(C.FW*12+8, C.FH*2+8, '#2b2536')
for ci, klass in enumerate(['priest','warrior']):
    for ri, race in enumerate(C.RACE_IDS):
        for s in range(3):
            cv = C.composite(race, klass, s, (s+ri) % 5, (s*2+ri) % 5, 0)
            out.paste(cv, 4 + (ri*3+s)*C.FW, 4 + ci*C.FH)
out.save_preview(sys.argv[1] if len(sys.argv)>1 else 'C:/Users/tobia/AppData/Local/Temp/chars.png', scale=4)
