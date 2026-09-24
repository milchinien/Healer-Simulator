import sys, time
import scenes, scenes_race
from pa import Canvas
name = sys.argv[1]
t=time.time()
mod = scenes if hasattr(scenes, name) else scenes_race
layers, meta = getattr(mod, name)()
out = Canvas(640, 360)
for k in ['bg','clouds','fg']:
    if k in layers: out.paste(layers[k], 0, 0)
out.save_preview(f'C:/Users/tobia/AppData/Local/Temp/scene_{name}.png', scale=2)
print(name, 'ok', round(time.time()-t,1),'s', meta)
