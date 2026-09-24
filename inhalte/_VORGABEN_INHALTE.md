# Vorgaben für alle Inhaltsdateien (Welten, Raids, Abgrund)

Diese Datei ist die verbindliche Schablone für alle Inhaltsdateien. Grundlage ist `../GAME_DESIGN.md`.

## Allgemeine Regeln
- Sprache: Deutsch (die englische Übersetzung entsteht später).
- **Keine konkreten Balancing-Zahlen** (keine HP-Werte, keine Schadenswerte, keine Prozente). Nur Regeln, Verhältnisse und relative Angaben (z.B. „schwach“, „mittel“, „stark“, „sehr stark“, „kurze/lange Castzeit“). Erlaubt sind: Gegneranzahlen, Levels, Wellennummern, Phasen-Schwellen in HP-% (z.B. „ab 50 % HP“).
- **Keine neuen Spielsysteme erfinden.** Nur Inhalte (Namen, Texte, Gegner, Mechaniken aus der erlaubten Liste, Items).
- Erlaubte Gegnermechaniken: normale Angriffe (physisch/magisch), **AoE-Schaden** auf alle, **Tank-Buster** (mit Castbalken angekündigt), **DoTs/Debuffs** (Typ *Magie* oder *Krankheit* = bannbar, andere = nicht bannbar), **Adds** (Boss ruft Gegner), **Enrage** (nach fester Zeit), **Phasen** (ab HP-Schwelle). Kombinationen erlaubt. Keine Bewegungs-/Positionsmechaniken (es gibt keine Bewegung).
- Gegner sind **Normal**, **Elite** (stärker) oder **Boss**. Adds sind normale Gegner.
- Pixel-Art-Stil: Figuren mit wenigen Pixeln; Aussehen kurz beschreiben (1 Satz).
- Namen sollen eigenständig sein (keine 1:1-WoW-Namen), thematisch zur Welt passen, und jeder Itemname muss **in der gesamten Datei einzigartig** sein und so thematisch gewählt werden, dass er nicht mit anderen Welten kollidiert (z.B. Weltbezug im Namen).

## Priester-Fähigkeiten, auf die sich Mechaniken beziehen dürfen (allgemeine Begriffe verwenden)
- Ab Level 1: Einzelheilung, Angriffszauber. Ab Level 2: Heilung über Zeit (HoT). Ab Level 4: Schadens-DoT. Ab Level 6: schnelle, teure Heilung.
- Ab Level 10: Spezialisierung, Auferstehung (Wiederbelebung im Kampf).
- Ab Level 12: **Bannen** (Magie und Krankheit) → **bannbare Debuffs erst ab Welt 4** einsetzen.
- Ab Level 14: **Gruppenheilung** → starke AoE-Mechaniken erst ab Welt 4; in Welt 1–3 nur leichte AoE.
- Schild (Schadensabsorption), Notfallzauber, Schadensreduktion kommen über die Spezialisierungen.
In Beschreibungen allgemein formulieren: „Schild vorher“, „Gruppenheilung“, „bannen“, „Tank vorheilen“.

## Gruppengröße des Spielers je Welt (für die Gegneranzahl)
- Welt 1–2 (Level 1–7): Spieler + 1 Tank (Krieger).
- Welt 3 (Level 8–12): ab Level 10 Spieler + 2 Mitglieder.
- Welt 4 (13–18): Spieler + 2.
- Welt 5 (19–24): ab Level 20 Spieler + 3.
- Welt 6 (25–30): Spieler + 3, ab Level 30 + 4.
- Welt 7–10, Abgrund: volle Gruppe (Spieler + 4).
- Raids: 20 (deine Gruppe + 2 Tanks, 2 KI-Heiler, 11 DPS als Füller).
Auf dem Schlachtfeld stehen maximal **6 Gegner** gleichzeitig in Welten/Abgrund, **8** in Raids (Adds mitgezählt).

## Garantierte Mindest-Rarität der Auswahl-Belohnung (Items)
Welt 1–2: Ungewöhnlich · Welt 3–5: Selten · Welt 6–8: Episch · Welt 9–10: Legendär · Raid 1: Episch · Raid 2–3: Legendär · Abgrund-Bosse: Legendär.

## Aufbau einer Welt-Datei
1. `# Welt N – Name`
2. `## Überblick`: Level, Mindestlevel, Gruppengröße, Thema, Hintergrund (für Pixel-Art), Musikstimmung, Story-Kurzabriss (3–5 Sätze), welche Mechaniken in dieser Welt neu eingeführt werden.
3. `## Gegner`: Tabelle `| Name | Art (Normal/Elite/Boss/Add) | Kampfstil (Nahkampf/Fernkampf/Zauberer) | Schadensart | Fähigkeiten (mit Mechanik-Typ) | Aussehen |`. 6–10 Gegnertypen pro Welt + Boss + ggf. Adds.
4. `## Wellen (Quests)`: Für jede Welle 1–10 ein Unterabschnitt:
   - `### Welle X – „Questname“`
   - **Gegnerlevel:** (innerhalb des Levelbereichs, steigend)
   - **Questtext:** 1–2 Sätze (vor der Welle)
   - **Gegner:** Anzahl × Typ (steigend in Anzahl/Stärke; Elite ab ca. Welle 5)
   - **Besonderheit:** was diese Welle spielerisch fordert (1 Satz)
   - **Abschlusstext:** 1 Satz („Quest abgeschlossen“)
5. `## Endboss (Welle 10)`: Name, Aussehen, Hintergrund (1–2 Sätze), Phasen, alle Fähigkeiten mit Mechanik-Typ, Castbalken-Ankündigung ja/nein, Enrage (ja/nein, relativ), Adds, Heiler-Tipps.
6. `## Auswahl-Belohnung (Welle 10)`: Option X und Option Y (gemischte Arten: 2 Items / Item gegen Gold / Item gegen Trank-Paket / Item gegen Tasche). Items mit Slot/Typ/Grundwert und garantierter Mindest-Rarität. Gold/Trank-Paket/Tasche relativ beschreiben.
7. `## Item-Katalog` (vollständig, siehe unten).

## Item-Katalog (vollständig, pro Welt/Raid/Abgrund exakt diese Struktur, 294 Items)
Jedes benannte Item hat: **Name, Slot, Typ, Grundwert-Typ (fest), Raritätsbereich, Icon (kurze Pixel-Art-Beschreibung)**.
Pro Slot/Typ gibt es **6 Items** mit unterschiedlichen, teilweise überlappenden Raritätsbereichen, sodass jede Rarität möglich ist:
1. **Gewöhnlich–Ungewöhnlich**
2. **Ungewöhnlich–Selten**
3. **Selten–Episch**
4. **Episch–Legendär**
5. **Legendär–Mythisch+**
6. **Zusatz-Item:** hat denselben Bereich wie eines der Items 1–5 (je Slot/Typ ein anderer Bereich wählen, gut über den Katalog verteilen, am häufigsten Gewöhnlich–Ungewöhnlich und Selten–Episch). So gibt es z.B. mehrere Helme, die nur Grau–Grün droppen.
Zwei Items mit gleichem Bereich im selben Slot/Typ haben möglichst **unterschiedliche Grundwert-Typen** (z.B. einer Rüstung, einer HP).

Grundwert-Regeln:
- Rüstungsslots und Umhang: **HP**, **Rüstung** oder **Resistenz** (gut mischen; Stoff eher Resistenz/HP, Platte eher Rüstung/HP).
- Haupthand-Waffen, Artefakt, Zauberkugel, Grimoire, Götze: **Schaden** oder **Heilstärke** (Stab und Streitkolben und Artefakt: sowohl Heilstärke- als auch Schaden-Varianten; Schwert/Axt/Dolch/Bogen: Schaden; Zauberkugel/Grimoire/Götze: meist Schaden).
- Schild: **Rüstung** oder **HP**. Köcher, Nebenhand-Dolch: **Schaden**.
- Halskette: **Mana** oder **Mana-Reg**. Ring: **Krit** oder **Tempo**. Schmuckstück: **Heilstärke, Schaden, Mana-Reg, Krit** oder **Tempo**.

Tabellen:
1. `### Stoff` – 8 Slots (Helm, Schultern, Brust, Armschienen, Handschuhe, Gürtel, Hose, Schuhe) × 6 = 48 Zeilen
2. `### Leder` – 48 Zeilen
3. `### Kette` – 48 Zeilen
4. `### Platte` – 48 Zeilen
5. `### Umhang` – 6 Zeilen
6. `### Schmuck` – Halskette, Ring, Schmuckstück × 6 = 18 Zeilen
7. `### Haupthand` – Stab, Streitkolben, Schwert, Axt, Dolch, Bogen × 6 = 36 Zeilen
8. `### Nebenhand` – Artefakt, Schild, Zauberkugel, Grimoire, Götze, Köcher, Nebenhand-Dolch × 6 = 42 Zeilen

Tabellenformat: `| Name | Slot | Grundwert | Rarität | Icon |` (bei Haupthand/Nebenhand zusätzlich Spalte `Typ`).
Beispiel: `| Schildkrötenhelm | Helm | Rüstung | Gewöhnlich–Ungewöhnlich | Grüner Panzerhelm mit Schuppenmuster |`

Das Mindestlevel steht nicht in der Tabelle; es ergibt sich aus dem Drop-Ort (Welle bzw. Raidlevel).
