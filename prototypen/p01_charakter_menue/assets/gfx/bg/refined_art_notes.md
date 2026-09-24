# Feine Hintergrundfassung

Erstellt mit dem integrierten ImageGen-Tool (style-transfer), 24.09.2026. Die bisherigen PNG-Dateien und klassischen Shader bleiben erhalten.

Im Spiel: Optionen → Anzeige → Hintergründe → Fein / Klassisch. Fein ist die neue Voreinstellung. OK speichert die Auswahl, Abbrechen stellt die vorherige Auswahl wieder her. Die Auswahl gilt für alle neun Motive. Die drei Grünhain-Ladebilder wechseln weiterhin unabhängig vom gewählten Stil.

Fein rendert auf einem 640×360-Raster, Klassisch weiter auf 320×180 mit den bisherigen Paletten. Vorhandene dezente Wolken-, Licht-, Wasser- und Werkstatteffekte werden weiterhin verwendet. Standflächen und Szenenmetadaten bleiben erhalten.

Bild 1 jedes Auftrags ist die bisherige Szene; Bilder 2–4 sind die vom Nutzer gelieferten Stilreferenzen (Berglandschaft, Haus, große Wolke). Ziel: feinere Pixel, klarere Flächen und weniger kleinteiliges Texturrauschen bei gleicher Szene.

## Charakterauswahl – Marktplatz

Neue Datei: [charselect_refined_v1.png](charselect_refined_v1.png)

Klassisches Original: [charselect_market_v3.png](charselect_market_v3.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Medieval marketplace, hillside castle and houses; keep platform TOP at x35.3%,y82%, retain lantern positions and the same perspective.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Menschen – Stadt

Neue Datei: [human_city_refined_v1.png](human_city_refined_v1.png)

Klassisches Original: [human_city_art_v1.png](human_city_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: White stone city gate framing cathedral and descending street, platform top at x50%,y77.2%, fountain to left and lanterns either side of arch.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Zwerge – Schmiedehalle

Neue Datei: [dwarf_hall_refined_v1.png](dwarf_hall_refined_v1.png)

Klassisches Original: [dwarf_hall_art_v1.png](dwarf_hall_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Vast underground dwarven forge hall, layered pillars, furnace and braziers. Platform top at x50%,y71.7%. Flat carefully shaped stone surfaces, restrained warm light. No sky.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Orks – Steppe

Neue Datei: [orc_steppe_refined_v1.png](orc_steppe_refined_v1.png)

Klassisches Original: [orc_steppe_art_v1.png](orc_steppe_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Orc tent camp in mesa steppe at dusk, firepit left, canyon distance. Platform top at x50%,y75%. Sculptural layered mesas and calm sky. Keep red banners.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Gnome – Werkstatt

Neue Datei: [gnome_workshop_refined_v1.png](gnome_workshop_refined_v1.png)

Klassisches Original: [gnome_workshop_art_v1.png](gnome_workshop_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Gnome workshop with central round night window, hanging lamps, copper pipes, benches and gear mechanisms. Platform top at x50%,y71.7%. Simplify objects to coherent readable shapes.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Titel – Bergkapelle

Neue Datei: [title_refined_v1.png](title_refined_v1.png)

Klassisches Original: [title_art_v1.png](title_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Moon valley sanctuary, receding forest and mountains, waterfall at right, overlook in foreground. Upper center needs quiet sky for separately overlaid game logo. No logo or letters in image.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Grünhain – Mühle

Neue Datei: [loading_gruenhain_refined_v1.png](loading_gruenhain_refined_v1.png)

Klassisches Original: [loading_gruenhain_art_v1.png](loading_gruenhain_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Green valley with stream, stone bridge, farmhouse and windmill at right. Preserve sunset location, rolling land and large left tree.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Grünhain – Waldweg

Neue Datei: [loading_gruenhain_woods_refined_v1.png](loading_gruenhain_woods_refined_v1.png)

Klassisches Original: [loading_gruenhain_woods_art_v1.png](loading_gruenhain_woods_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Woodland path framed by two near trees, little stone bridge, cottage and distant mountains, lamps on both foreground trees. Calm lush landscape at sunset.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

## Grünhain – See

Neue Datei: [loading_gruenhain_lake_refined_v1.png](loading_gruenhain_lake_refined_v1.png)

Klassisches Original: [loading_gruenhain_lake_art_v1.png](loading_gruenhain_lake_art_v1.png)

Prompt:

```text
Use case: style-transfer. EDIT IMAGE 1, keeping its scene, camera, architecture placement, object locations, lighting time of day, depth, platform position and broad perspective. Images 2-4 are STYLE REFERENCES ONLY, not objects or scenery to insert.
The user likes the scene but dislikes the coarse, noisy, AI-looking pseudo-pixel treatment. Redraw image 1 from scratch in the confident CLEAN FINER PIXEL ART of the references. The difference must be substantial: about half as much fine surface texture, much larger coherent color shapes, elegant deliberate silhouette edges, natural hue-shifted shading. Logical pixel grid 640x360, 16:9 frame, not the coarse 320x180 look. Pixels remain discrete and aligned, but less blocky. Think meticulous illustrated adventure-game background, simple readable masses rather than an automated pixel filter.
Use the reference mountain's broad angular planes, house's clean structural edges and restrained detail, tree foliage in shaped clumps, cloud reference's sculpted grouped volumes in 3-5 flat shades. Stones and roofs should have designed rhythms with QUIET smooth flat interiors. Remove random speckles, confetti highlights, muddy texture, crawling linework, excessive little stones, over-rendered repeated windows. No airbrush, blur, photorealistic shading or 3D render.
SKY: remove ALL repeated horizontal checkerboard STRIPES and decorative dither bands. Use broad clean color fields and beautifully shaped quiet clouds like the references, recolored to the existing dusk/night mood. Very sparse localized dithering at one or two transitions is allowed, never patterned wallpaper. Do not turn night scenes into daytime. Preserve atmospheric depth with overlapping silhouettes, cooler distant tones and coherent light direction. Reduce bloom to small clearly shaped warm highlights.
SCENE LOCK: Lakeside village and chapel, left tree, foreground overlook and boathouse with tiny empty boat, mountains and sunset reflected in water. Keep moon and sun positions.
Return only the finished full-bleed environment artwork, no gray margins from reference pictures. No characters, UI, text, lettering, logos, borders, buttons or watermarks. Preserve usable character standing area where present. Do not add decorations or redesign the scene.
```

