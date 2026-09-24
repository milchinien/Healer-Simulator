import sys
from pa import Canvas
import chars as C
race = sys.argv[1]; klasses = sys.argv[2].split(',')
out = Canvas(C.FW*3*len(klasses), C.FH, '#2b2536')
i=0
for k in klasses:
    for s in range(3):
        out.paste(C.composite(race, k, s, 1, s+1, 0), i*C.FW, 0); i+=1
out.save_preview(f'C:/Users/tobia/AppData/Local/Temp/race_{race}.png', scale=int(sys.argv[3]) if len(sys.argv)>3 else 8)
