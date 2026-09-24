# Prototyp 1 – Titel, Charakterauswahl, Charaktererstellung

Godot 4.7 (GDScript), Grundauflösung 640×360, ganzzahlig skaliert.

## Starten
- **Doppelklick auf `Spiel_starten.bat`** (nutzt `Downloads\Godot_v4.7.2-stable_win64.exe\`), oder
- Godot öffnen → Projekt `project.godot` importieren → F5.

## Inhalt
| Bildschirm | Funktionen |
|---|---|
| **Titel** | Animierte Nachtszene (ziehende Wolken, Glühwürmchen, Lichtsäule), Logo, „Beliebige Taste drücken“. Ohne Charakter → direkt zur Erstellung. |
| **Charakterauswahl** | Liste rechts (max. 10, Porträt, Stufe, Welt, Hardcore-Totenkopf, „Gefallen“), **Drag & Drop** zum Umsortieren, Doppelklick = Welt betreten, Charakter mit **Gruppe im Hintergrund**, **Charakter-Info** (Modus, Spielzeit, Gold, Spezialisierung, höchste Welt/Welle), Welt betreten, Löschen (Name eintippen), Menü (Optionen, Spiel beenden). Gefallene Hardcore-Charaktere erscheinen als Geist und sind nicht spielbar. |
| **Charaktererstellung** | Rasse (4, mit **Rassen-Hintergrund** und **Beschreibung**), Geschlecht (nur Anrede Priester/Priesterin), Hautfarbe (5), Frisur (3), Haarfarbe (5), Name (2–12 Buchstaben, **Würfel** schlägt Namen vor), Spielmodus Normal/Hardcore (mit Regel-Bestätigung). |
| **Optionen** | Fenster/Vollbild, Fenstergröße (×2/×3/×4), Lautstärke Gesamt/Musik/Effekte, Sprache Englisch (Standard)/Deutsch. |
| **Ladebildschirm** | Grünhain, Fortschrittsbalken, Tipps. ESC führt zurück (die Welt folgt im nächsten Prototyp). |

## Steuerung
- Maus für alles; **Pfeil hoch/runter** wechselt den Charakter, **Enter** betritt die Welt, **Entf** löscht, **ESC** öffnet/schließt das Menü bzw. geht zurück.

## Struktur (gleich für alle Prototypen)
```
assets/      Grafiken (gfx/), Sounds (sfx/), Schriften (fonts/, SIL OFL)  – erzeugt von werkzeuge/build_assets.py
data/        i18n.json (Texte EN/DE), characters.json, scenes.json, ui_slices.json
src/autoload Settings, Loc, Sfx, SaveGame, UiTheme, Router
src/core     GameData, NameGenerator, CharacterFactory
src/render   CharacterView (Palettentausch-Shader), SceneBackdrop (Hintergrund + Effekte)
src/ui       UI-Fabrik, TileButton, ArrowSelector, ModalDialog
src/scenes   boot, title, character_select, character_create, loading, options
src/tests    smoke_test.gd
```
Speicherstände: `%APPDATA%\Godot\app_userdata\Healer Simulator\` (ein JSON pro Charakter + `roster.json`, Einstellungen in `settings.cfg`).

## Grafiken neu erzeugen
```
python werkzeuge/build_assets.py prototypen/p01_charakter_menue
```

## Tests
```
Godot_console.exe --headless --path . -- profile=smoketest test=1        # Rauchtest (Logik + Szenen)
python werkzeuge/godot_shots.py prototypen/p01_charakter_menue <ordner>   # Screenshots aller Bildschirme
```
Weitere Startargumente (nach `--`): `profile=<name>`, `demo=1` (Beispielcharaktere), `scene=<title|character_select|character_create|loading>`, `lang=de`, `race=`, `gender=`, `mode=hardcore`, `dialog=options|delete|menu|hardcore`.
