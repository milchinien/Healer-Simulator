# Marktplatz v2

Erzeugt mit dem eingebauten Imagegen-Tool. Referenz: Screenshot des Nutzers vom 24.09.2026. Hintergrund ohne UI oder Figuren.

`charselect_market_v2.png` ist das unveränderte generierte Original. Godot skaliert es mit Nearest-Neighbor auf 640 × 360. Spielerposition bleibt (226, 296). Die Steinplattform ist Teil des Hintergrunds.

`data/scene_art_overrides.json` bindet die Grafik ein und definiert separate Flammen, flackernde Lichtkegel und Lichtflecken. Diese Datei überlebt `build_assets.py`. `src/render/market_sky.gdshader` bewegt zwei abgegrenzte Wolkenbereiche langsam und pixelweise hin und her (keine Endlos-Wolkenfahrt); Gebäude und Mond bleiben fest. Das Quellbild ist flach, kein vollständig separiertes Parallax-Layerset.

## Generierungs-Prompt

Use case: stylized-concept. Asset type: finished 16:9 pixel-art game environment background for a 640x360 Godot game, preferably deliver 1536x864 or 1920x1080 landscape.
Input image: attached screenshot is ONLY a reference for pixel art palette, sky dithering and medieval setting. Completely exclude ALL interface, lettering, borders, buttons, people and character sprites.
Create a beautiful professionally hand-pixelled medieval town marketplace at early night. Preserve the reference's navy to violet to dusty rose to warm peach horizon SKY WITH PROMINENT ORDERED PIXEL DITHERING between stepped color bands, tiny square stars and a small moon. No smooth gradients. Keep uppermost 22 percent mostly clear sky WITHOUT CLOUDS, clouds will be animated separately in engine.
Strong convincing 3D depth expressed entirely in crisp 2D pixel art: large timber framed houses at left and right foreground edges seen on two sides, overlapping smaller houses receding along winding lanes toward a distant stone castle on a high rocky mountain centered at x=53%, with towers silhouette beginning around y=27%. Castle is distant, tall hill clearly visible, atmospheric perspective. Slate and muted terracotta roofs, warm little windows, dark timber beams. Broad cobblestone market square fills bottom 38%, perspective paving shrinking into distance. Market stalls with fabric awnings, crates, barrels along edges, leaving open center.
IMPORTANT placement: a broad low raised stone platform, elliptical due to perspective, centered at x=35.3%, y=81.5%, width=29%, depth=11% of full image. Flat EMPTY stone top for existing player and companions, clearly visible beveled front edge and 2 shallow steps toward viewer. Not a fountain, not a magic portal. The feet of the existing main player will land at x=35.3%, y=82.2%. Platform stays in that position, do not recenter it on full image.
Sparse warm lanterns on town facades and street posts, contrasting cool purple night shadows. The art must feel like a 16-bit RPG environment at logical 640x360 pixel density, consistent square pixel clusters, clean hard stair-step edges and checkerboard dithering especially in sky. Not painterly, no blur, no antialiasing, no actual 3D rendering. Beautiful spatial composition and readable large forms.
Absolutely NO UI, NO text, NO letters, NO buttons, NO frames, NO logos, NO characters or creatures. Only background environment.
