# Healer Simulator

Das Spiel (Spielbeschreibung: `../GAME_DESIGN.md`, Inhalte: `../inhalte/`). Enthält Titel, Charakterauswahl, Charaktererstellung, Optionen, Ladebildschirm und den **Hauptbildschirm mit dem Echtzeitkampf in Welt 1 (Grünhain, 10 Wellen, Boss Kornkönig Knarz)** in Normal und Hardcore.

Godot 4.7 (GDScript), Grundauflösung 640×360, ganzzahlig skaliert. Schrift: Dungeon Mode (CC0).

## Starten
- **Doppelklick auf `Spiel_starten.bat`** (nutzt `Downloads\Godot_v4.7.2-stable_win64.exe\`), oder
- Godot öffnen → Projekt `project.godot` importieren → F5. Das Editor-Plugin „Claude MCP Bridge“ (`addons/claude_mcp/`) ist aktiviert.

## Inhalt
| Bildschirm | Funktionen |
|---|---|
| **Titel** | Animierte Nachtszene (ziehende Wolken, Glühwürmchen, Lichtsäule), Logo, „Beliebige Taste drücken“. Ohne Charakter → direkt zur Erstellung. |
| **Charakterauswahl** | Liste rechts (max. 10, Porträt, Stufe, Welt, Hardcore-Totenkopf, „Gefallen“), **Drag & Drop** zum Umsortieren, Doppelklick = Welt betreten, Charakter mit **Gruppe im Hintergrund**, **Charakter-Info** (Modus, Spielzeit, Gold, Spezialisierung, höchste Welt/Welle), Welt betreten, Löschen (Name eintippen), Menü (Optionen, Spiel beenden). Gefallene Hardcore-Charaktere erscheinen als Geist und sind nicht spielbar. |
| **Charaktererstellung** | Zwei Schritte: **1. Rasse (Liste untereinander) + Geschlecht**, rechts Beschreibung, Rassen-Hintergrund, Auswahl-Pose der Figur; **2. Aussehen** (Hautfarbe 5, Frisur 3, Haarfarbe 5). Name immer unten (2–12 Buchstaben, **Würfel**). „Erstellen“ öffnet die große **Modus-Wahl** Normal/Hardcore (Hardcore mit Regel-Haken). |
| **Optionen** | Fenster/Vollbild, Fenstergröße (×2/×3/×4), Hintergründe Fein/Klassisch, Lautstärke Gesamt/Musik/Effekte, Sprache Englisch (Standard)/Deutsch. |
| **Ladebildschirm** | Grünhain, Fortschrittsbalken, Tipps, danach der Hauptbildschirm. |
| **Hauptbildschirm** | Obere Leiste im Holz-Stil, zentriert (Welt, 10 Wellen-Punkte mit Quest-Tooltip, geschaffte anklickbar, Auto-Weiter / Wiederholen, Hardcore-Mana-Schwelle), Schlachtfeld (Gruppe links, Gegner rechts, HP-Balken, Castbalken, Buffs/Debuffs, schwebende Zahlen), Zielfenster, Boss-Balken mit Castbalken und Phasengrenze, EP-Leiste (20 Segmente, füllt sich sichtbar pro Kill), Gruppenfenster (goldenes Stufen-Abzeichen, eigene EP-Linie, Klassenfarbe, Rolle, HP, eingehende Heilung, Ressource, Aggro-Warnung; Rahmen passen sich der Gruppengröße an), eigener Castbalken, untere Leiste als gravierter Stein mit Goldfries, Wappen und Säulen, in die Gruppenfenster, Mana-Rinne, WoW-artige Aktionsplätze (40 px, Metallrahmen, Taste oben rechts, Uhr-Animation, Mana-Färbung, Tooltips) und Mikromenü-Platte eingelassen sind (Grafik: `werkzeuge/pixelart/hud_art.py`, Positionen: `data/hud_layout.json`), NPC-Leiste in einer Steinsäule (Lehrmeister aktiv mit Ausrufezeichen, Schmied/Waffenmeister gesperrt), Trainingspuppe, ESC-Menü. |
| **Kampf** | Echtzeit wie WoW: Bedrohung (110 %/130 %), Rüstung/Resistenz, GCD, Castzeiten, Zauber-Warteschlange, Heilung über Zeit, Schaden über Zeit, Krit. Krieger-KI (Heldenhafter Stoß, Donnerknall, Spott, Schildwall, Wut). Gegner mit Nahkampf, Zaubern, Tank-Buster, Flächenschaden und Bossphasen. Priester-Zauber bis Level 9: Geringe Heilung, Heilige Pein, Erneuerung, Schattenwort: Schmerz, Blitzheilung (mit Rängen, gelernt beim Lehrmeister). |
| **Lehrmeister & Zauberbuch** | Lehrmeister (Porträt links): alle Ränge mit Status lernbar/Stufe zu niedrig/gelernt, Preis in Gold, „Lernen“ und „Alle lernen“; Reiter „Talente zurücksetzen“ ab Stufe 10. Zauberbuch (P): gelernte Zauber mit höchstem Rang, per Drag & Drop auf die Aktionsleiste; Plätze umsortieren und herausziehen. |
| **Regeln** | EP mit Grau-Regel sofort pro Kill sowie für Heilung und Schaden der ganzen Gruppe, Level-Ups sofort mit vollem Auffüllen von HP/Mana und starkem Lichteffekt (Spieler und Krieger), nach jedem eigenen Level-Up Segen-Wahl 1 aus 3 (dauerhaft +%, stapelbar, Seltenheiten), Quest-Belohnung beim ersten Sieg, Gold, Niederlage = eine Welle zurück, Wiederbelebungsschwäche (Normal); Hardcore: 5-Sekunden-Regel, kein Auffüllen, stärkere Gegner, permanenter Tod, Gratis-Krieger, gefallener Charakter. Speichern nach jeder Welle; eine abgebrochene Welle zählt nicht. |

## Steuerung
- Maus für alles; **Pfeil hoch/runter** wechselt den Charakter, **Enter** betritt die Welt, **Entf** löscht, **ESC** öffnet/schließt das Menü bzw. geht zurück.
- Im Kampf: Ziel per Klick auf Gruppenrahmen oder Figur; Zauber auf **1-0, ß, ´** (englisch **-, =**). Maus über einem Rahmen + Taste zaubert auf diesen Rahmen (Mouseover). **Tab** wechselt den Gegner, **X** bricht einen Cast ab, **ESC** bricht ab bzw. öffnet das Menü (pausiert).

## Struktur
```
addons/      Editor-Plugin Claude MCP Bridge (nur im Editor aktiv)
assets/      Grafiken (gfx/), Sounds (sfx/), Schrift (fonts/, Dungeon Mode, CC0)  – erzeugt von werkzeuge/build_assets.py
data/        i18n.json (Texte EN/DE), characters.json, scenes.json, ui_slices.json,
             balancing.json (alle Kampfzahlen), world_1.json (Gegner, Wellen), enemies_gfx.json, battle_bg.json
src/autoload Settings, Loc, Sfx, SaveGame, UiTheme, Router
src/core     GameData, NameGenerator, CharacterFactory, Progression (EP, Level, Aktionsleiste, Wellen)
src/combat   CombatData (Daten + Formeln), CombatUnit, Battle (Kampfsimulation, KI)
src/render   CharacterView (Palettentausch-Shader), EnemyView (Gegner-Sprites), SceneBackdrop
src/ui       UI-Fabrik, TileButton, ArrowSelector, ModalDialog
src/scenes   boot, title, character_select, character_create, loading, options, game (Hauptbildschirm)
src/tests    smoke_test.gd, game_test.gd, combat_sim.gd
```
Speicherstände: `%APPDATA%\Godot\app_userdata\Healer Simulator\` (ein JSON pro Charakter + `roster.json`, Einstellungen in `settings.cfg`).

## Grafiken neu erzeugen
```
python werkzeuge/build_assets.py            # Standard-Projektordner: healer-simulator
```

## Tests
```
Godot_console.exe --headless --path . -- profile=smoketest test=1        # Rauchtest (Logik, Kampfregeln, Szenen, Wellenablauf)
Godot_console.exe --headless --path . -- profile=sim test=combat         # Balancing-Simulation aller Wellen (Bot-Heiler)
python werkzeuge/godot_shots.py healer-simulator <ordner>   # Screenshots aller Bildschirme
```
Weitere Startargumente (nach `--`): `profile=<name>`, `demo=1` (Beispielcharaktere), `scene=<title|character_select|character_create|loading|game>`, `lang=de`, `race=`, `gender=`, `step=2`, `mode=hardcore`, `dialog=options|delete|menu|mode`; im Hauptbildschirm `char=<Name>`, `wave=<n>`, `autostart=1`, `training=1`, `cast=<zauber>` mit `cast_at=<sek>`, `xp_gain=<n>` mit `xp_at=<sek>`, `window=trainer|spellbook`.
