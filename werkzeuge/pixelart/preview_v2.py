"""Vorschau einer v2-Szene: Hintergrund + erstes Wolkenframe + Lichter/Flammen angedeutet."""
import sys, time
import scenes_v2 as V, scenes_v2b as V2
import props as P
from pa import Canvas
name = sys.argv[1]
t = time.time()
sc = getattr(V if hasattr(V, name) else V2, name)()
out = Canvas(640, 360)
out.paste(sc['layers']['bg'], 0, 0)
glows = {'glow_tiny': P.glow(5, '#ffc070', 0.8), 'glow_small': P.glow(10, '#ffc070', 0.7), 'glow_lamp': P.glow(22, '#ffc070', 0.7),
         'glow_window': P.glow(8, '#ffb050', 0.5), 'pool_lamp': P.light_pool(40, 12, '#ffb060', 0.45), 'glow_forge': P.glow(50, '#ff9a3a', 0.6), 'glow_rune': P.glow(10, '#ffb04a', 0.6), 'glow_lava': P.glow(40, '#ff7a2a', 0.5), 'pool_fire': P.light_pool(46, 14, '#ff9a4a', 0.5)}
for p in sc['props']:
    if p['type'] == 'clouds':
        cl = sc['sprites'][p['tex']]
        out.paste(cl.crop(0, 0, 640, p['h']), 0, p['y'])
for p in sc['props']:
    if p['type'] == 'glow' and p['tex'] in glows:
        g = glows[p['tex']]
        # additiv andeuten
        for y in range(g.h):
            for x in range(g.w):
                a = g.a[y, x, 3]
                if a:
                    X, Y = int(p['x'] - g.w // 2 + x), int(p['y'] - g.h // 2 + y)
                    if out.inside(X, Y):
                        base = out.a[Y, X].astype(int)
                        add = g.a[y, x, :3].astype(int) * a * p.get('alpha', 1) / 255
                        out.a[Y, X, :3] = (base[:3] + add * 0.6).clip(0, 255)
for p in sc['props']:
    if p['type'] == 'anim':
        sh = sc['sprites'][p['tex']]
        fw = sh.w // p.get('hframes', 1); fh = sh.h // p.get('vframes', 1)
        out.paste(sh.crop(0, 0, fw, fh), p['x'], p['y'])
    if p['type'] == 'fire':
        f = P.fire()
        out.paste(f.crop(0, 0, 16, 22), p['x'] - 8, p['y'] - 21)
if 'fg' in sc['layers']:
    out.paste(sc['layers']['fg'], 0, 0)
out.save_preview(f'C:/Users/tobia/AppData/Local/Temp/v2_{name}.png', scale=2)
print(name, round(time.time() - t, 1), 's', len(sc['props']), 'props')
