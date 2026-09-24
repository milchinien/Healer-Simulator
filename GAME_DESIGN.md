# Healer Simulator – Vollständige Spielbeschreibung (Game Design Document)

> **Status:** Vollständige Beschreibung des fertigen Spiels (kein Prototyp, kein MVP).
> **Zahlen:** Dieses Dokument legt **Regeln und Verhältnisse** fest, keine konkreten Balancing-Zahlen. Konkrete Werte werden beim Balancing bestimmt. Die wenigen festen Zahlen (z.B. Level 60, 10 Welten, Timer) wurden vom Auftraggeber vorgegeben.
> **Inhaltsdateien:** Welten, Gegner, Quests, Bosse und die vollständigen Itemlisten stehen im Ordner `inhalte/`. Zauber und Talente stehen in `inhalte/ZAUBER_UND_TALENTE.md`.
> **Markierung:** Abschnitte mit **[Festlegung]** sind Details, die nicht ausdrücklich abgefragt wurden und die ich im Sinne deiner Vorgaben festgelegt habe. Sie sind in Kapitel 27 gesammelt, damit du sie prüfen kannst.

---

## Inhaltsverzeichnis

1. Spielidee und Kern-Gefühl
2. Plattform, Technik-Rahmen, Sprache, Audio
3. Grafikstil
4. Startbildschirm: Charakterauswahl
5. Charaktererstellung
6. Spielmodi: Normal und Hardcore
7. Der Hauptbildschirm (ein Screen für alles)
8. Werte (Stats) und Berechnung
9. Der Spieler: Priester
10. Level-System und Erfahrungspunkte (EP)
11. Spezialisierung ab Level 10
12. Talentbaum
13. Zauber, Zauberbuch, Aktionsleiste, Steuerung
14. Kampfsystem (Echtzeit)
15. Gruppe, Klassen, Rekrutierung, Rassen
16. Welten, Wellen und Quests
17. Raids
18. Unendliche Wellen (Endgame)
19. Belohnungen: Quest-Belohnungen, Drops, Gold
20. Item-System
21. Inventar und Taschen
22. Karten-System
23. Lehrmeister
24. Schmied
25. Waffenmeister
26. Speichern, Optionen, Menüs
27. Übersicht aller Festlegungen zur Prüfung
28. Glossar
29. Zusätzliche Features (vom Auftraggeber genehmigt)

---

## 1. Spielidee und Kern-Gefühl

**Healer Simulator** ist ein 2D-Pixel-Art-Spiel, das das Gefühl vermittelt, **Heiler in einem MMORPG wie World of Warcraft** zu sein, ohne ein echtes MMORPG zu sein. Der Spieler steuert ausschließlich einen **Priester**. Seine Gruppenmitglieder werden vom Computer gesteuert (KI) und kämpfen selbstständig. Der Spieler hält die Gruppe am Leben, verwaltet sein Mana, reagiert auf Bossmechaniken und kämpft mit 1–2 Angriffszaubern selbst mit.

**Ablauf in einem Satz:** Man erstellt einen Charakter, startet auf Level 1 im Startgebiet mit einem einzigen Begleiter (einem Krieger als Tank), spielt Wellen von Gegnern, die wie Quests aufgebaut sind, sammelt Items, Gold und EP, lernt Zauber beim Lehrmeister, rekrutiert weitere Gruppenmitglieder und steigt bis Level 60 auf. Ab Level 40 kommen Raids mit 20 Spielern dazu. Nach dem letzten Raid gibt es unendliche Wellen, die immer schwerer werden.

**Kern-Gefühl (muss immer erhalten bleiben):**
- Die HP-Balken der Gruppe im Blick haben und im richtigen Moment den richtigen Zauber wirken.
- Mana ist knapp; effizient heilen ist wichtig.
- Überheilen ist Verschwendung; Notfallzauber retten Situationen.
- Bossmechaniken ankündigen (Castbalken) und darauf reagieren (Schild vor dem Tank-Buster, Gruppenheilung nach AoE, Bannen von Debuffs).
- Es wird mit der Spielzeit schwerer: mehr Gegner, stärkere Gegner, mehr Gruppenmitglieder, schließlich Raids mit 20 Leuten.

---

## 2. Plattform, Technik-Rahmen, Sprache, Audio

| Punkt | Festlegung |
|---|---|
| Plattform | PC Desktop (Windows), eigenständiges Programm |
| Steuerung | Maus und Tastatur |
| Anzeige | Vollbild und Fenstermodus, Seitenverhältnis 16:9. Die Pixel-Art wird **ganzzahlig** skaliert (scharfe Pixel, kein Verschwimmen). Auflösung in den Optionen wählbar. |
| Sprache | Englisch und Deutsch, in den Optionen umschaltbar. **Standard: Englisch.** |
| Audio | Musik und Soundeffekte. Eigene Musik pro Welt, pro Raid, für Bosskämpfe und für den Charakterauswahl-Bildschirm. Soundeffekte für Zauber, Treffer, Heilung, UI-Klicks, Level-Up, Quest abgeschlossen, Item-Drop (je Rarität eigener Klang). Lautstärke getrennt einstellbar: Gesamt, Musik, Effekte. |
| Speichern | Automatisch, lokal auf dem PC (siehe Kapitel 26). |
| Technik | **Godot 4.7 mit GDScript**, Export als Windows-Programm (.exe). |
| Grundauflösung | **640×360 Pixel**. Wird ganzzahlig skaliert: ×2 = 1280×720, ×3 = 1920×1080, ×4 = 2560×1440. |
| Grafiken | Alle Pixel-Art-Grafiken (Figuren, Hintergründe, Icons, UI) werden selbst erstellt, in Ebenen aufgebaut (Körper, Haare, Kleidung; Farben per Palette) und sind jederzeit austauschbar. |
| Schrift | **Dungeon Mode** von Vinicius Menezio (CC0, gemeinfrei) im ganzen Spiel: normale Texte 9 px, Überschriften 18 px. Festbreitenschrift; die Zeichen – — „ “ × € fehlen und werden in Texten vermieden. |
| Entwicklung | Ein Godot-Projekt `healer-simulator/` (das Spiel), das Schritt für Schritt erweitert wird (anfangs in Prototypen entwickelt, Prototyp 1 ist darin aufgegangen). Git-Repository mit GitHub-Remote. |

---

## 3. Grafikstil

- **2D-Pixel-Art.** Figuren (Spieler, Gruppe, Gegner) haben **wenige Pixel** (grob, kleine Sprites, ähnlich Screenshot 1). **Icons** von Items, Waffen, Zaubern und Tränken haben **mehr Pixel** und sind detaillierter.
- **Ansicht wie Slay the Spire:** Seitenansicht. Die Gruppe steht **links**, die Gegner stehen **rechts**, alle auf einer Bodenlinie vor einem Hintergrund der jeweiligen Welt.
- **Anordnung der Gruppe (links):** Der/die Tanks stehen ganz vorne (am nächsten zu den Gegnern), dahinter Nahkämpfer, dahinter Fernkämpfer, ganz hinten der Spieler (Priester).
- **Raid-Darstellung:** Im Raid werden **alle 20 Figuren** gezeigt, gestaffelt in mehreren Reihen und etwas kleiner skaliert. Die eigenen 4 Gruppenmitglieder und der Spieler sind durch einen leichten Umriss/Markierung erkennbar.
- **Ausrüstung ändert das Aussehen nicht.** Weder Rüstung noch Waffe sind an der Figur sichtbar. Das Aussehen wird nur durch Rasse, Hautfarbe, Frisur und Haarfarbe bestimmt. Klassen sind an einer **klassentypischen Grundkleidung/Silhouette** erkennbar (z.B. Krieger mit Helm-Silhouette, Magier mit Spitzhut), die sich nie ändert. Die Grundkleidung ist **je Rasse unterschiedlich** (Priester: Mensch weiß-goldener Kleriker, Zwerg Runenpriester in blauer Wolle mit Lederschürze und Pelzkragen, Orc Schamane mit Lederwams, Knochenkette und rotem Tuch, Gnom Tüftler-Priester im violetten Mantel mit Messingknöpfen; Krieger-Rüstungen in rassentypischen Farben). Stil: Chibi (großer Kopf, dunkle Kontur, große Augen), **3/4-Ansicht nach rechts**.
- **Rassen-Silhouetten:** Mensch = groß und schlank, Zwerg = klein und füllig, Orc = groß und breit, Gnom = klein und schlank. Das Geschlecht verändert das Aussehen nicht.
- **Animationen (Figuren):** Idle (8 Frames: Atmen, wehende Robe, schwingende Haare, zufälliges Blinzeln), Auswahl-Pose (10 Frames: Heilzauber mit Lichtkugeln an beiden Händen), Angriff, Zaubern (Cast-Pose), Treffer, Tod (liegt am Boden), Wiederbelebung, Sieg-Jubel. Figuren bestehen aus beweglichen Teilen (Körper, Arme, Kopf, Haare) und werden pro Frame zusammengesetzt.
- **Zauber-Effekte:** Kleine Pixel-Partikel (Licht für Heilig, Schatten-Violett für Schatten, Gold-Weiß für Disziplin), Schild als sichtbare Blase um die Figur.
- **Farben der Raritäten:** Grau (Gewöhnlich), Grün (Ungewöhnlich), Blau (Selten), Lila (Episch), Gold/Orange (Legendär), Rot (Mythisch), Rot mit Stern (Mythisch+).

---

## 4. Startbildschirm: Charakterauswahl

### 4.0 Titelbildschirm

Beim Programmstart erscheint zuerst ein **Titelbildschirm**: das Spiellogo „Healer Simulator“ in Pixel-Art über einer animierten Pixel-Szene, darunter blinkend **„Beliebige Taste drücken“**. Jede Taste oder ein Mausklick führt zur Charakterauswahl (bzw. zur Charaktererstellung, wenn noch kein Charakter existiert).

### 4.1 Charakterauswahl

Aufbau wie im WoW-Charakterauswahl-Bildschirm (Screenshot 3):

- **Hintergrund:** Pixel-Art-Szene (Stadtplatz).
- **Rechts:** Liste aller Charaktere, **maximal 10**. Jeder Eintrag zeigt:
  - Name
  - Level
  - „Priester“ bzw. „Priesterin“ (je nach gewähltem Geschlecht) und, falls gewählt, die Spezialisierung (Heilig/Schatten/Disziplin)
  - Aktuelle Welt (Name)
  - **Hardcore-Symbol**, falls Hardcore-Charakter
  - **„Gefallen“** (grau mit Totenkopf), falls der Hardcore-Charakter gestorben ist
- **Mitte:** Die Pixel-Figur des ausgewählten Charakters (groß, Idle-Animation) mit Namen darunter.
- **Gruppe im Hintergrund:** Hinter dem Charakter stehen klein seine aktuellen Gruppenmitglieder (bis zu 4, in ihrer Klassen-Silhouette).
- **Charakter-Info:** Beim ausgewählten Charakter werden zusätzlich angezeigt: Spielzeit, Gold, Symbol der Spezialisierung (falls gewählt) und die höchste erreichte Welt/Welle.
- **Unten Mitte:** Knopf **„Enter World“ / „Welt betreten“**.
- **Unter der Liste rechts:** Knopf **„Neuen Charakter erstellen“** (deaktiviert, wenn 10 Charaktere existieren).
- **Unten rechts:** Knopf **„Charakter löschen“**.
- **Unten links:** Knopf **„Menü“** mit **Optionen** und **Spiel beenden**.

**Bedienung:**
- Einfacher Klick auf einen Charakter rechts → er wird ausgewählt und in der Mitte angezeigt.
- Die **Reihenfolge** der Charaktere in der Liste kann per **Drag & Drop** geändert werden (wird gespeichert).
- **Doppelklick** auf einen Charakter rechts **oder** Klick auf „Enter World“ → Spiel startet mit diesem Charakter.
- Ein **gefallener Hardcore-Charakter** kann ausgewählt und angesehen werden (Figur in der Mitte als Geist/grau, Anzeige des erreichten Levels und der Welt), aber **nicht gespielt** werden. „Enter World“ ist deaktiviert. Er belegt einen Platz, bis er gelöscht wird.
- **Charakter löschen:** Sicherheitsabfrage, bei der man den Charakternamen eintippen muss.
- Hat man **keinen Charakter**, öffnet sich beim Spielstart direkt die Charaktererstellung. **[Festlegung]**

---

## 5. Charaktererstellung

Die Charaktererstellung ist ein eigener Bildschirm in **zwei Schritten** (wie im neueren WoW). In der Mitte steht die Pixel-Figur, die sich live mit jeder Auswahl ändert.

- **Schritt 1 – Rasse & Geschlecht:** links die Rassen **untereinander als Liste** (Porträt + Name, erweiterbar für spätere Rassen) und darunter das Geschlecht; rechts Name und Beschreibung der gewählten Rasse. Beim Wechsel der Rasse macht die Figur die **Auswahl-Pose** (Heilzauber mit Lichtfunken). Knöpfe: „Zurück“ (zur Charakterauswahl) und „Weiter“.
- **Schritt 2 – Aussehen:** rechts Hautfarbe, Frisur und Haarfarbe; links eine Zusammenfassung (Rasse, Klasse). Knöpfe: „Zurück“ (zu Schritt 1) und „Erstellen“.
- **Name:** steht in **beiden Schritten unten** in der Mitte (mit Würfel-Knopf).
- **Spielmodus:** Nach Klick auf „Erstellen“ erscheint **groß in der Mitte** die Wahl zwischen zwei Karten **Normal** und **Hardcore**. Die Hardcore-Karte listet alle Hardcore-Regeln; Hardcore kann erst erstellt werden, wenn der Haken „Ich habe die Hardcore-Regeln verstanden“ gesetzt ist.

| Einstellung | Auswahl |
|---|---|
| **Rasse** | Mensch, Zwerg, Orc, Gnom (keine spielerischen Unterschiede, nur Aussehen) |
| **Geschlecht** | Männlich, Weiblich – nur für die Klassenbezeichnung (Priester/Priesterin), kein optischer Unterschied |
| **Hautfarbe** | 5 pro Rasse (rassentypisch, z.B. Orcs grün- und brauntöne) |
| **Frisur** | 3 pro Rasse (bei Zwergen und Orcs inklusive Bart als Teil der Frisur) |
| **Haarfarbe** | 5 pro Rasse |
| **Name** | Freie Eingabe. **[Festlegung]** 2–12 Buchstaben, nur Buchstaben, darf nicht mit einem eigenen vorhandenen Charakter übereinstimmen. Daneben ein **Würfel-Knopf**, der einen passenden Namen zu Rasse und Geschlecht vorschlägt. |
| **Spielmodus** | Normal (Standard) oder Hardcore – **endgültig**, später nicht änderbar (siehe Kapitel 6); Auswahl in der großen Modus-Wahl nach „Erstellen“ |
| **Klasse** | Immer Priester (nicht wählbar, wird angezeigt) |

- **Rassen-Hintergründe:** Der Hintergrund der Charaktererstellung wechselt mit der gewählten Rasse: Mensch = Stadt, Zwerg = Bergfestung, Orc = Steppe, Gnom = Werkstatt.
- **Rassen-Beschreibung:** Zur gewählten Rasse wird ein kurzer Lore-Text angezeigt (rein erzählerisch, keine Boni).

Die Hardcore-Regeln werden auf der Hardcore-Karte der Modus-Wahl erklärt und per Haken bestätigt (siehe oben).

Nach dem Erstellen startet der Charakter auf **Level 1** in **Welt 1, Welle 1**, mit einem **Krieger (Level 1)** in der Gruppe, Startausrüstung (graue Items für Priester und Krieger) und einer kleinen Menge Gold. **[Festlegung: Startausrüstung]**

---

## 6. Spielmodi: Normal und Hardcore

Der Modus wird bei der Erstellung gewählt und ist **endgültig**.

| Regel | Normal (Standard) | Hardcore |
|---|---|---|
| Gegnerstärke | Normal | **Stärkere Gegner** (mehr HP und Schaden, fester Multiplikator) |
| Tod eines Gruppenmitglieds | Tot bis Wellenende. **Nach der Welle automatisch wiederbelebt** mit dem Debuff **„Wiederbelebungsschwäche“** | Wer bei Wellenende tot ist, ist **permanent tot**. Seine getragenen **Items gehen verloren**. |
| Wiederbelebung im Kampf | Mit dem Zauber „Auferstehung“ (lange Castzeit) | Ebenfalls möglich; wer im Kampf rechtzeitig wiederbelebt wird, ist nicht permanent tot |
| Tod des Spielers (Priester) | Gruppe kämpft ohne Heilung weiter. Gewinnt sie, steht der Spieler nach der Welle mit „Wiederbelebungsschwäche“ wieder auf | Gruppe kämpft weiter. **Gewinnt sie, überlebt der Spieler** (steht mit wenig HP und wenig Mana wieder auf). **Verliert sie, ist der Charakter endgültig tot („Gefallen“).** |
| Mana-Regeneration | **Konstant** (immer volle Regeneration) | **5-Sekunden-Regel** wie WoW Classic: volle Regeneration erst, wenn man 5 Sekunden lang keinen Zauber mit Manakosten gewirkt hat, sonst stark reduziert |
| HP/Mana zwischen Wellen | **Komplett aufgefüllt** (Spieler und Gruppe) | **Nicht aufgefüllt.** Spieler: nur durch eigene Zauber, eigene Regeneration und Tränke. Gruppenmitglieder: **regenerieren langsam selbst** (HP und ihre Ressource) außerhalb des Kampfes |
| Raids | Mitglieder sterben nie permanent im Raid | **Permanenter Tod gilt auch im Raid** |
| Niederlage (alle tot) | Eine Welle zurück | Charakter ist „Gefallen“ (da der Spieler dann tot ist) |

**Wiederbelebungsschwäche (Normal-Modus):** Debuff auf wiederbelebten Figuren, senkt **alle Werte um einen festen Prozentsatz** für die **nächste Welle**. Wird ein Mitglied im Kampf per Zauber wiederbelebt, bekommt es diesen Debuff nicht. **[Festlegung: Dauer = nächste Welle]**

**Gratis-Krieger:** Ist die Gruppe (ohne Spieler) leer – weil alle Mitglieder permanent gestorben sind (Hardcore) oder weil der Spieler alle entlassen hat – tritt automatisch ein **kostenloser Krieger auf Level 1** mit grauer Startausrüstung bei.

---

## 7. Der Hauptbildschirm (ein Screen für alles)

Es gibt **einen einzigen Spielbildschirm**. Alle Menüs öffnen sich als **Fenster darüber**. Menüs können **jederzeit** geöffnet werden, **auch während eines Kampfes** (der Kampf läuft weiter). Nur das ESC-Menü pausiert.

### 7.1 Aufteilung

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [Weltname]  Welle: ①②③④⑤⑥⑦⑧⑨⑩  [Auto-Weiter ☐] [Wiederholen ☐] [Karte] [Raids] │  ← Obere Leiste
├────────┬─────────────────────────────────────────────────────────────────┤
│Lehr-   │                                        [Boss-HP-Balken + Castbalken]│
│meister │                                                                   │
│        │   GRUPPE (links)                     GEGNER (rechts)              │
│Schmied │   Priester  DPS  DPS  Tank     ⟷     Gegner Gegner Boss           │
│        │   (Figuren mit kleinem HP-Balken    (Figuren mit HP-Balken,        │
│Waffen- │    und Buff-/Debuff-Symbolen)        Castbalken, Debuff-Symbolen)  │
│meister │                                                                   │
│        │            [Eigener Castbalken]                                   │
│ Gold   │            [Raidfenster / Gruppenfenster]                        │
│        │ [Spieler-HP/Mana] [ Aktionsleiste 1–12 ]  [Mikromenü]  [Meter]   │
└────────┴─────────────────────────────────────────────────────────────────┘
```

### 7.2 Elemente

- **Obere Leiste:**
  - Name der aktuellen Welt/des Raids/„Abgrund“ (unendliche Wellen).
  - **Wellen-Anzeige:** 10 Punkte (Raids: 5/7/10). Geschaffte Wellen sind markiert und **anklickbar** (zu dieser Welle wechseln). Die aktuelle Welle ist hervorgehoben. Bosswellen haben ein Totenkopfsymbol.
  - Schalter **„Auto-Weiter“**: Nach einer gewonnenen Welle startet automatisch die **nächste** Welle.
  - Schalter **„Welle wiederholen“**: Nach einer gewonnenen Welle startet automatisch **dieselbe** Welle erneut (zum Farmen). Die beiden Schalter schließen sich gegenseitig aus. Ist keiner aktiv, startet man jede Welle manuell mit dem Knopf **„Welle starten“** in der Mitte des Schlachtfelds.
  - **Pause zwischen Wellen:** Normal: 5 Sekunden Countdown. Hardcore: Die nächste Welle startet erst, wenn das Mana des Spielers über einem **einstellbaren Schwellwert (X %)** liegt (Regler neben den Schaltern).
  - Knopf **„Karte“** (Weltkarte), Knopf **„Raids“**.
- **Linke NPC-Leiste:** Pixel-Porträts von **Lehrmeister**, **Schmied**, **Waffenmeister**. Klick öffnet das jeweilige Fenster. Ein kleiner Timer unter Schmied und Waffenmeister zeigt die Zeit bis zum nächsten Warenwechsel. Darunter die **Goldanzeige**.
- **Schlachtfeld (Mitte):** Figuren wie in Kapitel 3. Über/unter jeder Figur ein kleiner HP-Balken, Buff-/Debuff-Symbole und **schwebende Zahlen** (Schaden weiß/gelb, Heilung grün, Krits größer, absorbierte Werte „Absorbiert“). Gegner zeigen Castbalken. Bei Bosswellen oben rechts ein großer Boss-HP-Balken mit Castbalken.
- **Raidfenster/Gruppenfenster (unten Mitte, über der Aktionsleiste):** Rahmen pro Mitglied (auch Spieler) mit Name, Klassenfarbe, Rollensymbol (Tank/DPS/Heiler), HP-Balken, Ressourcenbalken (Mana/Wut/Energie), Buff-/Debuff-Symbolen (bannbare Debuffs farbig umrandet: Magie blau, Krankheit braun), eingehende Heilung als heller Vorschau-Balken, Schild als weißer Überlagerungs-Balken, Aggro-Warnung (roter Rand, wenn ein Nicht-Tank angegriffen wird). Gruppe: 1 Reihe. Raid: 4 Gruppen à 5 in einem Raster.
- **Spieler-HP/Mana-Anzeige** links neben der Aktionsleiste.
- **Eigener Castbalken** über dem Raidfenster.
- **Aktionsleiste:** 12 Plätze (siehe Kapitel 13).
- **Mikromenü (unten rechts):** Knöpfe für Charakter (C), Zauberbuch (P), Talente (N, ab Level 10 aktiv), Taschen (B), Gruppe (G), Karten-Sammlung (K), Weltkarte (M), Raids (R), Optionen. **[Festlegung: Standardtasten]**
- **Meter (unten rechts, ein-/ausklappbar):** Heilungs- und Schadensmeter wie Details!/Recount. Zeigt die aktuelle bzw. letzte Welle: Heilung pro Person, Überheilung, Schaden pro Person, erlittener Schaden, Tode. Umschaltbar zwischen „Heilung“, „Schaden“, „Erlittener Schaden“.
- **Zielfenster:** **[Festlegung]** Oben links neben dem Schlachtfeld wird das aktuelle **freundliche Ziel** und das aktuelle **feindliche Ziel** angezeigt (Name, HP, Debuffs).

### 7.3 Pop-up-Fenster (erscheinen automatisch)

- **„Quest abgeschlossen!“** – nach dem ersten Abschluss einer Welle, mit Questname, Abschlusstext und Belohnung.
- **Auswahl-Belohnung** – nach dem ersten Sieg über einen Endboss (2 Optionen).
- **Kartenwahl** – nach der Auswahl-Belohnung einer Welt/eines Raids.
- **Level-Up** – kurze Einblendung „Level X erreicht!“ mit Wertezuwachs (auch für Gruppenmitglieder: „[Name] hat Level X erreicht“ als kleine Einblendung über der Figur).
- **Spezialisierungswahl** – Pflichtfenster bei Level 10.
- **Neuer Gruppenplatz frei** – bei Level 10, 20, 30.
- **Niederlage** – „Die Gruppe wurde besiegt“ mit Hinweis auf den Rückfall um eine Welle.

### 7.4 ESC-Menü

ESC **pausiert** das Spiel (auch im Kampf) und öffnet: **Fortsetzen**, **Optionen**, **Zur Charakterauswahl**, **Spiel beenden**. Verlässt man das Spiel während eines Kampfes, **zählt die Welle nicht** (siehe Kapitel 26).

---

## 8. Werte (Stats) und Berechnung

### 8.1 Werteliste

| Wert | Wirkung |
|---|---|
| **HP** | Lebenspunkte. 0 = tot. |
| **Mana** | Maximaler Manavorrat (Spieler und Mana-Klassen). |
| **Mana-Reg** | Mana-Regeneration pro Sekunde. |
| **Schaden** | Erhöht den Schaden von Angriffen und Schadenszaubern. |
| **Heilstärke** | Erhöht die Stärke von Heilzaubern und Schilden. |
| **Rüstung** | Verringert erlittenen **physischen** Schaden (prozentual, mit abnehmendem Nutzen). |
| **Resistenz** | Verringert erlittenen **magischen** Schaden (prozentual, mit abnehmendem Nutzen). |
| **Krit** | Chance auf kritischen Treffer/kritische Heilung (doppelte Wirkung). **[Festlegung: Krit-Multiplikator]** |
| **Tempo** | Verkürzt Castzeiten, die globale Abklingzeit (mit Untergrenze) und die Tick-Abstände von Heilung/Schaden über Zeit. |

Mitglieder mit Wut (Krieger) oder Energie (Schurke) haben statt Mana diese Ressource; Mana und Mana-Reg haben für sie keine Wirkung.

### 8.2 Berechnungsreihenfolge (für jeden Wert einzeln)

```
Endwert = (Levelbasis + Summe der Item-Grundwerte)
          × (1 + Summe aller Enchantment-% + Summe aller Talent-%)
          × (1 + Summe aller Karten-%)
```

- **Levelbasis:** Grundwert aus Klasse und Level (Kapitel 10).
- **Item-Grundwerte:** feste Werte der ausgerüsteten Items (Kapitel 20).
- **Enchantments und Talente:** Prozent-Boni, addiert.
- **Karten:** ganz zum Schluss als **eigener Multiplikator** (addierte Karten-Prozente). Dadurch haben Karten den größten Einfluss, wie gewünscht.
- **Buffs/Debuffs im Kampf** (z.B. Wiederbelebungsschwäche, Tränke) wirken nach den Karten auf den Endwert. **[Festlegung]**

---

## 9. Der Spieler: Priester

- Klasse: **Priester** (fest).
- Rüstungstyp: **Stoff**.
- Waffen: **Haupthand:** Stab **oder** Streitkolben. **Nebenhand:** **Artefakt** (immer, auch mit Stab – der Stab ist in diesem Spiel nicht zweihändig).
- Ressource: Mana.
- Rolle: Heiler, kämpft mit 1–2 Angriffszaubern mit (Schatten-Spezialisierung: viele Schadenszauber, schwächere Heilung).
- Level-Up-Profil: **wenig HP**, **viel Mana**, **viel Mana-Reg** (Kapitel 10).

---

## 10. Level-System und Erfahrungspunkte (EP)

### 10.1 Grundregeln

- Maximallevel: **60** – für den Spieler und für alle Gruppenmitglieder.
- EP gibt es für **jeden getöteten Gegner** und für **jede abgeschlossene Quest** (erster Abschluss einer Welle).
- **Alle bekommen die vollen EP:** der Spieler und jedes lebende Gruppenmitglied erhalten jeweils den vollen EP-Betrag (keine Aufteilung). Wer bei Wellenende tot ist, bekommt die EP für die Quest trotzdem, wenn er wiederbelebt wird (Normal). **[Festlegung]**
- Gruppenmitglieder leveln **unabhängig** vom Spieler und können **höher als der Spieler** werden (bis 60).
- Die EP-Menge pro Level **steigt** mit jedem Level (Kurve beim Balancing).
- **Graue Gegner (wie WoW):** Liegt ein Gegner deutlich unter dem Level der Figur, gibt er weniger EP; ab einem bestimmten Levelabstand gibt er **keine EP** mehr. Das gilt für jede Figur einzeln (ein niedriges Mitglied bekommt noch EP, der Spieler vielleicht nicht). **Gold ist davon nicht betroffen.** Gegner-Levelnamen werden farbig angezeigt (grau, grün, gelb, orange, rot) wie in WoW.

### 10.2 Level-Up-Zuwachs pro Klasse

Jede Klasse bekommt pro Level unterschiedlich viel. Die Tabelle zeigt das **Verhältnis** (★ = wenig, ★★★★★ = sehr viel). Konkrete Werte beim Balancing.

| Klasse | HP | Mana/Ressource | Mana-Reg | Rüstung | Resistenz | Schaden | Heilstärke |
|---|---|---|---|---|---|---|---|
| **Priester (Spieler)** | ★★ | ★★★★★ | ★★★★★ | ★ | ★★★ | ★★ | ★★★★ |
| Priester (KI-Raidheiler) | ★★ | ★★★★ | ★★★★ | ★ | ★★★ | ★ | ★★★ |
| Krieger (Tank) | ★★★★★ | – (Wut) | – | ★★★★★ | ★★ | ★★★ | – |
| Paladin (Tank) | ★★★★ | ★★ | ★★ | ★★★★ | ★★★★ | ★★★ | ★ |
| Magier | ★★ | ★★★★ | ★★★ | ★ | ★★★ | ★★★★★ | – |
| Hexenmeister | ★★★ | ★★★★ | ★★ | ★ | ★★★ | ★★★★ | – |
| Jäger (Hunter) | ★★★ | ★★★ | ★★ | ★★★ | ★★ | ★★★★ | – |
| Schurke | ★★★ | – (Energie) | – | ★★ | ★★ | ★★★★★ | – |
| Druide | ★★★ | ★★★ | ★★★ | ★★ | ★★★ | ★★★★ | ★ |

Zusätzlich hat jede Klasse feste Grundwerte für Krit und Tempo, die mit dem Level leicht steigen.

### 10.3 Was ein Level-Up außerdem bringt (Spieler)

- Neue Zauber/Ränge werden beim Lehrmeister **kaufbar** (nicht automatisch gelernt).
- Ab Level 10: **1 Talentpunkt pro Level** (Level 10 bis 60 = **51 Punkte**).
- Level 10, 20, 30: **neuer Gruppenplatz**.
- Level 10, 20, 30, 40, 50, 60: **Upgrade-Stufe** für Schmied und Waffenmeister kaufbar.
- Neue Welten und Raids werden durch Mindestlevel zugänglich.

---

## 11. Spezialisierung ab Level 10

Beim Erreichen von **Level 10** erscheint nach dem Kampf ein **Pflichtfenster**. Das Spiel geht erst weiter, wenn eine Spezialisierung gewählt wurde.

| Weg | Name | Fokus | Ikonisch |
|---|---|---|---|
| Volle Heilung | **Heilig** | Stärkste Heilung, stärkste Schilde, Rettungszauber | Machtwort: Schild (volle Stärke), Schutzgeist, Göttliche Hymne, Kreis der Heilung |
| Voller Schaden | **Schatten** | Sehr viel eigener Schaden, Heilung **schwächer**, Heilung vor allem als Selbstheilung/Lebensentzug | Schattengestalt, Vampirberührung, Gedankenschlag, Leerenausbruch |
| Kombination | **Disziplin** | Mischung aus Heilung und Schaden, beide **mittel**; die besten Zauber von Heilig und Schatten sind **gesperrt**, dafür eigene ikonische Zauber | Sühne (Schaden heilt Verbündete), Bußgebet, Schmerzunterdrückung, Machtwort: Barriere |

**Ablauf:**
1. Fenster zeigt die 3 Wege mit Beschreibung, Beispiel-Zaubern (Symbole mit Tooltip) und Vorschau auf den Talentbaum.
2. Spieler wählt einen Weg → **Bestätigungsfenster**: „Bist du sicher? Diese Entscheidung kann **NICHT** rückgängig gemacht werden.“ mit „Ja, diesen Weg einschlagen“ / „Zurück“.
3. Nach Bestätigung: Talentbaum wird freigeschaltet, beim Lehrmeister erscheinen die Zauber des Weges.

**Wichtig:** Bis Level 10 hat man nur **einfache, „langweilige“** Heil- und Schadenszauber. Die **spannenden, ikonischen** Zauber kommen erst **nach** der Spezialisierung. Die Startzauber **bleiben erhalten** und bekommen weiter Ränge.

Alle Zauber: siehe `inhalte/ZAUBER_UND_TALENTE.md`.

---

## 12. Talentbaum

- Freigeschaltet mit der Spezialisierung auf Level 10.
- **Jede Spezialisierung hat genau einen eigenen Talentbaum.** Man sieht nur den Baum des eigenen Weges.
- **1 Talentpunkt pro Level** ab Level 10 → **51 Punkte** auf Level 60.
- **Nicht alles ist lernbar:** Der Baum enthält deutlich mehr Ränge, als Punkte vorhanden sind. Man muss sich entscheiden.
- **Aufbau (alle 3 Bäume gleich):**
  - **9 Reihen.** Reihe 1 ist sofort offen. Jede weitere Reihe wird freigeschaltet, wenn **5 Punkte mehr** im Baum verteilt sind (Reihe 2 ab 5 Punkten, Reihe 3 ab 10 … Reihe 9 ab 40 Punkten).
  - Jede Reihe hat **3 Talente**.
  - **Normale Talente** haben 1–5 Ränge (jeder Rang = 1 Punkt).
  - **Wahl-Reihen** (Reihe 3, 6 und 9): Von den 3 Talenten darf **nur eines** gewählt werden (1 Punkt, sehr starker Effekt). Das sind die ikonischsten Talente.
  - Manche Talente setzen ein Talent in der Reihe darüber voraus (Pfeil-Verbindung).
- Talente geben: Prozent-Boni auf Werte (z.B. + % Heilstärke), Verbesserungen einzelner Zauber (Castzeit, Manakosten, Abklingzeit, Zusatzeffekte) und **neue Zauber/passive Effekte** (nur über Talente erhältlich).
- **Zurücksetzen:** Beim **Lehrmeister für Gold**. Die Kosten steigen mit jedem Zurücksetzen. Die **Spezialisierung** kann nie zurückgesetzt werden.
- Talent-Fenster: Baum grafisch mit Pixel-Icons, Tooltip pro Talent (aktueller und nächster Rang), Anzeige „Verfügbare Punkte“, Knopf „Übernehmen“ (Punkte werden erst nach Bestätigung fest gesetzt), „Abbrechen“.

Alle Talente: siehe `inhalte/ZAUBER_UND_TALENTE.md`.

---

## 13. Zauber, Zauberbuch, Aktionsleiste, Steuerung

### 13.1 Zauber

- Zauber werden **beim Lehrmeister für Gold gelernt** (nie automatisch).
- **Zauber-Ränge wie WoW Classic:** Viele Zauber haben mehrere Ränge. Jeder höhere Rang ist stärker (und teurer an Mana) und muss **einzeln beim Lehrmeister gekauft** werden. Der Lehrmeister bietet **alle 2 Level** neue Zauber oder neue Ränge an.
- Wird ein neuer Rang gelernt, ersetzt er auf der Aktionsleiste automatisch den alten Rang.
- Zaubereigenschaften: Manakosten, Castzeit (oder Spontanzauber), Abklingzeit (Cooldown), Reichweite spielt keine Rolle, Ziel (Verbündeter, Gegner, selbst, Gruppe), Schule (Heilig/Schatten).
- **Globale Abklingzeit (GCD):** Nach jedem Zauber kurze gemeinsame Sperre, durch Tempo verkürzt (Untergrenze).
- **Anzahl Angriffszauber:** Heilig und Disziplin haben insgesamt **1–2 Angriffszauber**. Schatten bekommt zusätzlich viele Schadenszauber.

### 13.2 Zauberbuch

- Wie in WoW: Fenster mit Seiten und Reitern: **„Allgemein“** (Startzauber und Zauber für alle Wege) und **Reiter der Spezialisierung**.
- Jeder Eintrag: Icon, Name, höchster gelernter Rang, Tooltip (Kosten, Castzeit, Abklingzeit, Wirkung).
- Zauber werden per **Drag & Drop** auf die Aktionsleiste gezogen.
- Passive Talente/Effekte werden grau als „Passiv“ angezeigt (nicht ziehbar).

### 13.3 Aktionsleiste

- **1 Leiste mit 12 Plätzen**.
- Standardtasten: **1, 2, 3, 4, 5, 6, 7, 8, 9, 0, ß, ´** (deutsches Layout; auf englischem Layout entsprechend **1–0, -, =**).
- Auf die Leiste können gezogen werden: Zauber und **Tränke** (Trank zeigt Anzahl im Inventar).
- Symbole zeigen Abklingzeit (Uhr-Animation), fehlendes Mana (blau eingefärbt), GCD.
- Plätze können per Drag & Drop umsortiert und herausgezogen werden. Leiste ist sperrbar (Option).

### 13.4 Zielauswahl und Zaubern

- **Freundliches Ziel:** Klick auf einen Rahmen im **Raid-/Gruppenfenster**. (Figuren auf dem Schlachtfeld sind ebenfalls anklickbar. **[Festlegung]**)
- **Zaubern:** Zwei Modi, **in den Optionen umschaltbar**, beide gleichzeitig aktivierbar:
  1. **Ziel anklicken, dann Taste** (WoW-Standard).
  2. **Mouseover:** Maus über einen Raidrahmen halten und Taste drücken – der Zauber geht auf den Rahmen unter der Maus, ohne das Ziel zu wechseln.
- Ohne freundliches Ziel gehen Heilzauber auf den Spieler selbst. **[Festlegung]**
- **Feindliches Ziel:** Klick auf eine Gegnerfigur. Taste **Tab** wechselt zum nächsten Gegner. Ohne gewähltes Ziel greifen Angriffszauber den Gegner an, den der Tank gerade angreift. **[Festlegung]**
- Zaubern lässt sich durch Bewegung nicht unterbrechen (es gibt keine Bewegung). Ein Cast kann mit **ESC** oder einer eigenen Taste abgebrochen werden. **[Festlegung: Taste „X“ für Abbrechen; ESC öffnet nur das Menü, wenn kein Cast läuft]**

### 13.5 Tastenbelegung

Alle Tasten sind in den **Optionen frei belegbar**: 12 Leistenplätze, Zielwechsel (Tab), Cast abbrechen, Fenster (Charakter, Zauberbuch, Talente, Taschen, Gruppe, Karten, Weltkarte, Raids), Auto-Weiter umschalten, Welle starten.

---

## 14. Kampfsystem (Echtzeit)

### 14.1 Grundprinzip

- Kämpfe laufen in **Echtzeit** wie in WoW. Gegner und Gruppe greifen dauerhaft an. Der Spieler wirkt Zauber mit Castzeit, GCD und Abklingzeiten.
- **Eine Welle = ein Kampf:** Alle Gegner der Welle stehen zu Beginn auf dem Schlachtfeld (Bosse können während des Kampfes **Adds** rufen). Sind alle Gegner besiegt, ist die Welle gewonnen.
- **Niederlage:** Die Welle ist verloren, wenn **alle tot** sind (Spieler und alle Gruppenmitglieder).

### 14.2 Aggro-System wie WoW

- Jeder Gegner hat eine **Bedrohungsliste**. Er greift die Figur mit der höchsten Bedrohung an.
- **Schaden** erzeugt Bedrohung beim getroffenen Gegner.
- **Heilung** erzeugt Bedrohung bei **allen Gegnern**, die im Kampf sind (aufgeteilt).
- Schilde erzeugen Bedrohung wie Heilung.
- **Tanks** haben Fähigkeiten und passive Boni, die viel Bedrohung erzeugen, und einen **Spott** (übernimmt sofort die höchste Bedrohung).
- Ein Wechsel des Ziels geschieht erst, wenn jemand die aktuelle Bedrohung deutlich überschreitet (wie WoW: Nahkampf 110 %, Fernkampf 130 %). **[Festlegung]**
- Zu viel Heilung oder Schaden **kann Aggro ziehen** – dann wird der Spieler oder ein DPS angegriffen. Das Raidfenster zeigt dies mit rotem Rand.
- Stirbt der Tank, suchen sich die Gegner das nächste Ziel nach Bedrohung.
- Der Priester hat (je Spezialisierung) Möglichkeiten, Bedrohung zu senken (siehe Zauber).

### 14.3 Schadensarten

- **Physisch:** verringert durch Rüstung.
- **Magisch:** verringert durch Resistenz.
- Schilde absorbieren jeden Schaden, bis sie verbraucht sind.

### 14.4 Gegner- und Bossmechaniken

| Mechanik | Beschreibung | Antwort des Heilers |
|---|---|---|
| **Normale Angriffe** | Gegner schlagen ihr Aggro-Ziel regelmäßig | Tank gleichmäßig heilen |
| **AoE-Schaden** | Schaden auf alle Gruppen-/Raidmitglieder, meist mit Castbalken angekündigt | Gruppenheilung, Schilde vorher, danach hochheilen |
| **Tank-Buster** | Sehr starker Schlag auf den Tank, mit **Castbalken** angekündigt | Schild/Schadensreduktion vorher, danach schnelle Heilung |
| **DoTs / Debuffs** | Schaden über Zeit oder Schwächung auf Mitgliedern. Typ **Magie** oder **Krankheit** sind **bannbar** (farbiger Rand); andere Effekte sind nicht bannbar und müssen gegengeheilt werden | Bannen (Zauber „Reinigung“), Gegenheilen |
| **Adds** | Boss ruft zusätzliche Gegner | Mehr Schaden auf die Gruppe, AoE der Adds |
| **Enrage** | Nach einer festen Zeit wird der Boss wütend (stark erhöhter Schaden/Angriffstempo). Zeit-Anzeige am Boss-HP-Balken | Schnell genug Schaden machen (Schatten/Disziplin helfen), bis dahin durchheilen |

Bosse kombinieren mehrere Mechaniken und können **Phasen** haben (z.B. ab 50 % HP neue Fähigkeit). Konkrete Mechaniken pro Boss: siehe `inhalte/`.

### 14.5 Gruppen-KI

- Jedes Mitglied nutzt **automatisch** seine **Klassenfähigkeiten** (2–4 pro Klasse, siehe Kapitel 15) nach festen Prioritäten.
- Tanks spotten Gegner, die jemand anderen angreifen.
- DPS greifen standardmäßig das Ziel des Tanks an; Adds werden bevorzugt angegriffen, wenn der Boss es erfordert (in den Bossbeschreibungen angegeben).
- Mitglieder haben **Ressourcen wie WoW:** Krieger **Wut** (steigt durch Schaden austeilen und erleiden), Schurke **Energie** (regeneriert schnell, fester Maximalwert), alle anderen **Mana**. Ein Mitglied ohne Mana/Ressource macht nur noch schwache Standardangriffe, bis genug regeneriert ist.

### 14.6 Tod und Wiederbelebung im Kampf

- Tote Figuren liegen am Boden, ihr Raidrahmen wird grau mit „Tot“.
- Zauber **„Auferstehung“** (ab Level 10, alle Spezialisierungen): lange Castzeit, hohe Manakosten; das Ziel steht mit geringen HP und geringem Mana wieder auf. **[Festlegung: HP/Mana nach Auferstehung]**
- Stirbt der Spieler: Er kann nichts mehr tun, die Gruppe kämpft weiter (Kapitel 6).

---

## 15. Gruppe, Klassen, Rekrutierung, Rassen

### 15.1 Gruppengröße und Plätze

- **Gruppe:** maximal **5** (Spieler + 4 Mitglieder).
- Gruppenplätze werden durch das **Spielerlevel** freigeschaltet:

| Platz | Frei ab Spielerlevel |
|---|---|
| Platz 1 | Level 1 (Start-Krieger) |
| Platz 2 | Level 10 |
| Platz 3 | Level 20 |
| Platz 4 | Level 30 |

- Die Zusammenstellung ist **frei** (beliebig viele Tanks und DPS erlaubt, auch 0 Tanks).

### 15.2 Klassen der Gruppenmitglieder

Jede Klasse hat eine **feste Rolle**, keine Talente, keine Spezialisierung.

| Klasse | Rolle | Rüstung | Ressource | Haupthand | Nebenhand | Fähigkeiten (KI) |
|---|---|---|---|---|---|---|
| **Krieger** | Tank | Platte | Wut | Schwert **oder** Axt | Schild | *Heldenhafter Stoß* (Einzelziel-Schaden, viel Bedrohung), *Donnerknall* (AoE-Schaden, Bedrohung auf alle), *Spott* (Aggro übernehmen), *Schildwall* (lange Abklingzeit, großer Schadensreduktion bei niedrigen HP) |
| **Paladin** | Tank | Platte | Mana | Streitkolben | Schild | *Kreuzfahrerstoß* (Schaden, Bedrohung), *Weihe* (AoE-Heiligschaden, Bedrohung), *Hand der Abrechnung* (Spott), *Handauflegen* (heilt sich selbst einmal pro Welle voll, wenn fast tot) |
| **Magier** | Fernkampf-DPS | Stoff | Mana | Stab | Zauberkugel | *Frostblitz* (Hauptschaden), *Feuerball* (hoher Schaden, lange Castzeit), *Arkane Explosion* (AoE bei 3+ Gegnern), *Eisblock* (einmal pro Welle unverwundbar bei niedrigen HP) |
| **Hexenmeister** | Fernkampf-DPS | Stoff | Mana | Stab | Grimoire | *Schattenblitz* (Hauptschaden), *Verderbnis* (DoT auf mehrere Gegner), *Aderlass* (tauscht eigene HP gegen Mana – erzeugt Heilbedarf), *Lebensentzug* (Schaden + Selbstheilung) |
| **Jäger** | Fernkampf-DPS | Kette | Mana | Bogen | Köcher | *Gezielter Schuss* (hoher Schaden), *Mehrfachschuss* (mehrere Ziele), *Arkaner Schuss* (schneller Schaden), *Totstellen* (verliert alle Bedrohung) |
| **Schurke** | Nahkampf-DPS | Leder | Energie | Dolch | Nebenhand-Dolch | *Finsterer Stoß* (Schaden, baut Kombopunkte auf), *Ausweiden* (Finisher, hoher Schaden), *Klingenwirbel* (AoE), *Entrinnen* (weicht Angriffen aus, wenn angegriffen) |
| **Druide** | Fernkampf-DPS | Leder | Mana | Stab | Götze | *Zorn* (Hauptschaden), *Mondfeuer* (Schaden + DoT), *Hurrikan* (AoE, kanalisiert), *Baumrinde* (Schadensreduktion auf sich) |

**Klassenfarben** im Raidfenster wie WoW (Krieger braun, Paladin rosa, Magier hellblau, Hexenmeister violett, Jäger grün, Schurke gelb, Druide orange, Priester weiß).

### 15.3 Rekrutierung (Gruppen-Menü)

- Das **Gruppen-Menü** (Mikromenü, Taste G) zeigt:
  - Die aktuellen Mitglieder (Name, Rasse, Klasse, Level, EP-Balken, Werte) – Klick öffnet das **Ausrüstungsfenster des Mitglieds** (gleiches Layout wie das Charakterfenster des Spielers, siehe Kapitel 20.8).
  - Knopf **„Entlassen“** pro Mitglied (mit Bestätigung). Beim Entlassen kommen seine **Items in das Inventar des Spielers** zurück. (Ist das Inventar voll, erscheint vorher ein Hinweis.) **[Festlegung]** Ist danach niemand mehr in der Gruppe, tritt der Gratis-Krieger bei.
  - Reiter **„Rekrutieren“**: **5 zufällige Kandidaten**. Jeder Kandidat zeigt: Name, Rasse, Klasse, Rolle, Level, Startausrüstung (anklickbar mit Tooltips), Preis in Gold.
- **Kandidaten-Level:** zufällig im Bereich **Spielerlevel ± 5** (mindestens 1, höchstens 60).
- **Preis:** steigt mit dem Level des Kandidaten.
- **Startausrüstung:** Kandidaten bringen eigene Ausrüstung mit (zufällige Items passend zu Klasse und Level, meist Grau/Grün, selten Blau). **[Festlegung: Raritätsbereich]** Der Spieler kann diese Items jederzeit durch eigene ersetzen.
- **Erneuerung:** Die Kandidaten werden alle **10 Minuten** neu gewürfelt (Timer läuft nur, während das Spiel läuft). Ein rekrutierter Kandidat verschwindet aus der Liste.
- Rekrutieren ist nur möglich, wenn ein **freier Gruppenplatz** vorhanden ist und genug Gold vorhanden ist.

### 15.4 Rassen der Gruppenmitglieder

Rassen haben keinen spielerischen Unterschied. Die Wahrscheinlichkeit der Rasse hängt von der Klasse ab (so sieht man z.B. Tanks eher als Orc oder Zwerg):

| Klasse | Mensch | Zwerg | Orc | Gnom |
|---|---|---|---|---|
| Krieger | 20 % | 35 % | 40 % | 5 % |
| Paladin | 35 % | 45 % | 15 % | 5 % |
| Magier | 40 % | 5 % | 10 % | 45 % |
| Hexenmeister | 35 % | 5 % | 25 % | 35 % |
| Jäger | 30 % | 35 % | 30 % | 5 % |
| Schurke | 45 % | 5 % | 10 % | 40 % |
| Druide | 45 % | 15 % | 30 % | 10 % |
| Priester (KI-Raidheiler) | 40 % | 30 % | 10 % | 20 % |

Namen, Hautfarbe, Frisur und Haarfarbe der Mitglieder werden zufällig bestimmt (Namenslisten pro Rasse).

### 15.5 Gruppenmitglieder und Items

- Mitglieder tragen Items in **denselben 14 Slots** wie der Spieler (Kapitel 20.2), jedoch mit ihrem Rüstungstyp und ihren Klassenwaffen.
- Items brauchen das **Mindestlevel** des Mitglieds.
- Hardcore: Stirbt ein Mitglied permanent, sind seine getragenen Items **verloren**.

---

## 16. Welten, Wellen und Quests

### 16.1 Überblick

- **10 Welten** von Level 1 bis 60. Jede Welt hat **10 Wellen**. **Welle 10 ist immer ein Bosskampf.**
- Die Levelbereiche sind am Anfang schmal und später breiter (schneller Start, langsamer später):

| Welt | Name | Level | Mindestlevel zum Betreten |
|---|---|---|---|
| 1 | Grünhain (Startgebiet) | 1–3 | 1 |
| 2 | Nebelmoor | 4–7 | 4 |
| 3 | Kupferklamm-Minen | 8–12 | 8 |
| 4 | Dornensteppe | 13–18 | 13 |
| 5 | Verwunschener Forst | 19–24 | 19 |
| 6 | Glutklippen | 25–30 | 25 |
| 7 | Frostwacht | 31–37 | 31 |
| 8 | Sonnenwüste Kharet | 38–44 | 38 |
| 9 | Schattenlande | 45–52 | 45 |
| 10 | Drachenhort | 53–60 | 53 |

- Eine Welt ist betretbar, wenn die **vorherige Welt abgeschlossen** (Boss besiegt) **und** das **Mindestlevel** erreicht ist.
- Die Gegner jeder Welle haben ein festgelegtes Level innerhalb des Levelbereichs der Welt; es steigt von Welle 1 bis 10.
- **Innerhalb einer Welt** werden die Wellen schwerer: **mehr Gegner** und **stärkere Gegner** (Elite-Gegner ab der Mitte der Welt, Boss in Welle 10).
- Wellen müssen **in Reihenfolge** freigeschaltet werden (Welle n+1 erst nach Sieg in Welle n).
- **Geschaffte Wellen** können jederzeit **erneut gespielt** werden (Klick auf die Welle oben oder Schalter „Welle wiederholen“). Wiederholungen geben Gegner-EP (mit Grau-Regel), Gold und Item-Drops, aber **keine Quest-Belohnung** mehr.

### 16.2 Quests

- **Jede Welle ist eine Quest** mit **Questnamen** und einem **kurzen Questtext** (1–2 Sätze), der vor der Welle angezeigt wird (kleines Fenster beim Anklicken der Welle / oben als Tooltip).
- Beim **ersten Sieg** erscheint **„Quest abgeschlossen!“** mit einem kurzen Abschlusstext und der Belohnung.

### 16.3 Niederlage und Rückfall

- Verliert man eine Welle (alle tot), fällt man **eine Welle zurück**: Die aktuelle Welle wird auf die vorherige gesetzt. Bei Welle 1 einer Welt bleibt man auf Welle 1. **[Festlegung]**
- Mit „Auto-Weiter“ wird danach automatisch die vorherige Welle gespielt und anschließend wieder die verlorene versucht.
- Der Fortschritt (höchste geschaffte Welle) geht nicht verloren; nur die aktuell gespielte Welle ändert sich. **[Festlegung]**

### 16.4 Weltkarte

- Fenster mit einer Pixel-Art-Karte aller 10 Welten, der 3 Raids und des Abgrunds (unendliche Wellen).
- Jeder Ort zeigt: Name, Levelbereich, Status (gesperrt mit Grund / offen / abgeschlossen), Anzahl geschaffter Wellen.
- Klick auf eine Welt → Wechsel in diese Welt (Wellen-Auswahl oben zeigt deren Wellen). Weltwechsel ist nur **zwischen** Wellen möglich. **[Festlegung]**
- Schneller Wellenwechsel innerhalb der Welt über die obere Leiste.

Inhalte aller Welten (Quests, Gegner, Bosse, Items): `inhalte/WELT_01_…md` bis `inhalte/WELT_10_…md`.

---

## 17. Raids

### 17.1 Überblick

| Raid | Name | Level | Voraussetzung | Wellen | Bosswellen |
|---|---|---|---|---|---|
| Raid 1 | Eisfeste Hrimgard | 40 | Level 40 **und** Welt 7 abgeschlossen | 5 | Welle 3, Welle 5 (Endboss) |
| Raid 2 | Grabkammern von Kharet | 50 | Level 50 **und** Welt 8 abgeschlossen | 7 | Welle 3, 5, Welle 7 (Endboss) |
| Raid 3 | Drachenfeste Ascheschwinge | 60 | Level 60 **und** Welt 10 abgeschlossen | 10 | Welle 3, 6, 8, Welle 10 (Endboss, „ultra stark“) |

- Raids sind **mehrere schwere Wellen** mit **mehreren Bossen** und einem **finalen, extrem starken Endboss**.
- Zugang über den eigenen Knopf **„Raids“** (obere Leiste/Mikromenü) – ein Fenster mit den 3 Raids, Voraussetzungen, Abklingzeit und Knopf „Raid betreten“.

### 17.2 Raidgruppe (20 Spieler)

- **Deine Gruppe** (Spieler + bis zu 4 Mitglieder) **plus automatische Raidfüller**, bis 20 erreicht sind.
- Die Raidfüller bestehen immer aus: **2 Tanks, 2 Heilern (KI-Priester), Rest DPS** – bei voller Gruppe also 2 Tanks + 2 Heiler + 11 DPS = 15 Füller. Hat der Spieler weniger als 4 Mitglieder (nur theoretisch, da Raid 1 Level 40 erfordert und alle Plätze ab Level 30 frei sind), werden zusätzliche DPS-Füller ergänzt. **[Festlegung]**
- Raidfüller: zufällige Klassen (Tanks: Krieger/Paladin; DPS: Magier, Hexenmeister, Jäger, Schurke, Druide), Rasse nach Tabelle 15.4, **Level = Raidlevel**, automatisch passende Ausrüstung. Sie werden **für jeden Raid-Versuch neu gestellt** und können **nie permanent sterben** (auch nicht in Hardcore).
- **KI-Heiler:** Priester, deutlich schwächer als der Spieler; heilen einfache Ziele, **bannen nicht** und nutzen keine Notfallzauber. Der Spieler ist der Hauptheiler. **[Festlegung: KI-Heiler bannen nicht]**
- **Eigene Mitglieder:** Normal-Modus: sterben im Raid nie permanent. Hardcore: permanenter Tod gilt auch im Raid.

### 17.3 Ablauf und Fortschritt

- Ein Raid muss **am Stück** geschafft werden. Wird eine Welle verloren (alle tot), ist der **Raid-Versuch gescheitert** und man muss wieder bei **Welle 1** beginnen. Man kehrt danach in die zuletzt gespielte Welt zurück. **[Festlegung]**
- Zwischen den Raidwellen gelten die Regeln des Modus (Normal: HP/Mana aufgefüllt; Hardcore: nicht).
- Auto-Weiter funktioniert im Raid; „Welle wiederholen“ ist im Raid deaktiviert.
- Verlässt man den Raid oder schließt das Spiel, gilt der Versuch als abgebrochen (kein Fortschritt, keine Abklingzeit). **[Festlegung]**
- **Abklingzeit:** Nach dem **Sieg über den Endboss** ist der Raid **2 Stunden Echtzeit** gesperrt. Die Abklingzeit läuft auch, wenn das Spiel geschlossen ist. **[Festlegung: Echtzeit auch offline]** Gescheiterte Versuche lösen keine Abklingzeit aus.

### 17.4 Raid-Belohnungen

- **Gleich wie Welten:** Jede Welle gibt beim **ersten** Abschluss eine automatische Quest-Belohnung (EP + zufälliges Item); der **Endboss** gibt beim ersten Sieg eine **Auswahl-Belohnung** und danach die **Kartenwahl**.
- Die Quest-Belohnung einer Welle wird sofort beim ersten Sieg vergeben, auch wenn der Versuch später scheitert. **[Festlegung]**
- Wiederholungen (nach Ablauf der Abklingzeit): Gegner-EP, Gold und Drops; Bosse haben eine **hohe Drop-Chance** und bessere Raritätschancen.
- Raid-Items haben das **Raidlevel** (40/50/60) als Mindestlevel.

Inhalte: `inhalte/RAID_1_…md` bis `inhalte/RAID_3_…md`.

---

## 18. Unendliche Wellen (Endgame)

- **Ort:** Eigenes Endgebiet **„Der Abgrund“** (eigene Hintergründe, gemischte Gegner aus einem eigenen Gegnerpool).
- **Freischaltung:** Welt 10 **und** Raid 3 (Level 60) abgeschlossen.
- **Wellen:** 1, 2, 3, … ohne Ende. Jede Welle ist stärker als die vorherige (HP, Schaden, Anzahl, Mechaniken); die Steigerung hat **keine Obergrenze**.
- **Boss alle 10 Wellen** (Welle 10, 20, 30 …), Bosse rotieren aus einem Pool und werden mit jeder Runde stärker und bekommen zusätzliche Mechaniken.
- **Gruppe:** Normale 5er-Gruppe (keine Raidfüller).
- **Niederlage:** Eine Welle zurück (wie überall).
- **Belohnungen skalieren mit:**
  - Erster Abschluss einer Welle: Quest-Belohnung (EP für nicht-maximale Mitglieder + zufälliges Item).
  - Erster Sieg über einen Boss (alle 10 Wellen): Auswahl-Belohnung.
  - **Keine Kartenwahl** im Abgrund.
  - Gold und Drops steigen mit der Wellennummer.
- **Items:** Alle Items haben **Mindestlevel 60**. Ihre Grundwerte steigen **nicht** über das Level-60-Niveau. Stattdessen **steigen die Chancen auf höhere Raritäten** (bis Mythisch+) mit der Wellennummer.
- Die Anzeige oben zeigt „Abgrund – Welle X“ und die höchste erreichte Welle (Rekord).

Inhalte: `inhalte/ENDLOS_Der_Abgrund.md`.

---

## 19. Belohnungen: Quest-Belohnungen, Drops, Gold

### 19.1 Zwei Arten von Quest-Belohnungen

1. **Automatische Belohnung** (Wellen 1–9 jeder Welt, Nicht-Endboss-Wellen der Raids, alle Nicht-Boss-Wellen des Abgrunds; nur beim **ersten** Abschluss):
   - Eine feste, großzügige Menge **EP** (für Spieler und alle Mitglieder).
   - **Gold**. **[Festlegung]**
   - **Ein zufälliges Item** (Level der Welle, Rarität gewürfelt, bevorzugt für die eigene Gruppe – siehe 19.3).
   - Der Spieler muss nichts auswählen.
2. **Auswahl-Belohnung** (Welle 10 jeder Welt, Endboss jedes Raids, jeder Boss im Abgrund; nur beim ersten Sieg):
   - Fenster mit **2 Optionen**, der Spieler wählt **eine** (X oder Y).
   - Die Art ist **gemischt** und je Welt festgelegt (siehe Inhaltsdateien): mal **2 Items**, mal **Item gegen Gold**, mal **Item gegen Trank-Paket**, mal **Item gegen Tasche**.
   - Items aus Auswahl-Belohnungen haben eine **garantierte Mindest-Rarität**, die von Welt zu Welt steigt.
   - Zusätzlich gibt es EP und Gold wie bei der automatischen Belohnung.
   - **Nach** der Auswahl-Belohnung einer Welt/eines Raids folgt die **Kartenwahl** (Kapitel 22).

### 19.2 Gegner-Drops

- Jeder getötete Gegner gibt **Gold** und **EP** (EP mit Grau-Regel).
- Jeder Gegner hat eine **kleine Chance auf ein Item**. Elite-Gegner höhere Chance, Bosse sehr hohe Chance (Raidbosse garantiert mindestens ein Item). **[Festlegung]**
- Gilt auch bei Wiederholungen.
- Items werden automatisch in das Inventar gelegt. Ist das Inventar voll, geht das Item verloren und eine Meldung erscheint („Inventar voll – [Item] verloren“). **[Festlegung]**
- Gold-Trank und EP-Trank erhöhen Gold bzw. EP (Kapitel 25).

### 19.3 Item-Wahl bei Drops und automatischen Quest-Belohnungen

1. **Rarität würfeln:** Jede Rarität kann **überall** droppen. Die Chancen auf höhere Raritäten steigen mit dem Inhalt (spätere Welten, Raids, höhere Abgrund-Wellen, Elite, Boss).
2. **Level:** = Level der Welle (Mindestlevel des Items).
3. **Für wen:** Items sind **bevorzugt für die eigene Gruppe**: höhere Chance auf Rüstungstypen und Waffentypen, die der Spieler oder seine aktuellen Mitglieder tragen können; kleinere Chance auf andere Klassen.
4. **Slot** zufällig.
5. **Benanntes Item** zufällig aus den Items der aktuellen Welt/des Raids, deren **Raritätsbereich** die gewürfelte Rarität enthält.
6. **Werte und Enchantments** würfeln (Kapitel 20).

### 19.4 Gold

- Quellen: Gegner, Quests, Verkauf von Items.
- Ausgaben: Zauber und Ränge (Lehrmeister), Talent-Reset, Rekrutierung, Schmied (Kauf, Fusion, Taschen, Upgrades), Waffenmeister (Kauf, Tränke, Upgrades), Karten neu würfeln.

---

## 20. Item-System

### 20.1 Raritäten

| Rarität | Farbe | Enchantments (Chance) | Fusion | Besonderheit |
|---|---|---|---|---|
| Gewöhnlich (Common) | Grau | Selten eins | 5 → Ungewöhnlich | – |
| Ungewöhnlich (Uncommon) | Grün | Oft eins | → Selten | – |
| Selten (Rare) | Blau | Meist eins, manchmal zwei | → Episch | – |
| Episch (Epic) | Lila | Meist 1–2, manchmal 3 | → Legendär | – |
| Legendär (Legendary) | Gold/Orange | Meist 2–3, manchmal 4 | → Mythisch | – |
| Mythisch (Mythic) | Rot | Meist 3, oft 4 | **Nicht weiter fusionierbar** | – |
| Mythisch+ (Mythic+) | Rot mit Stern | Wie Mythisch **+ 1 garantiertes Extra-Enchantment** (bis 5) | Nicht fusionierbar | **Nur als Drop** erhältlich, stärkere Werte als Mythisch |

- **Enchantment-Anzahl:** Immer zufällig. Je höher die Rarität, desto wahrscheinlicher hat das Item überhaupt ein Enchantment und desto wahrscheinlicher mehrere. **Maximum 4**, bei Mythisch+ **maximal 5**. Jedes Enchantment auf einem Item ist ein anderer Werttyp (keine Doppelung). **[Festlegung]**

### 20.2 Slots (14)

**Links** im Charakterfenster (wie WoW): Kopf (Helm), Hals (Halskette), Schultern, Rücken (Umhang), Brust, Handgelenke (Armschienen).
**Rechts:** Hände (Handschuhe), Taille (Gürtel), Beine (Hose), Füße (Schuhe), Ring, Schmuckstück.
**Unten:** **Haupthand** (Waffe), **Nebenhand** (Artefakt beim Priester).

| Slot | Kategorie |
|---|---|
| Helm, Schultern, Brust, Armschienen, Handschuhe, Gürtel, Hose, Schuhe | Rüstung mit Rüstungstyp |
| Umhang | Rüstung **ohne** Rüstungstyp (alle Klassen) |
| Halskette, Ring, Schmuckstück | Schmuck (alle Klassen) |
| Haupthand | Waffe (klassenabhängig) |
| Nebenhand | Nebenhand-Item (klassenabhängig) |

### 20.3 Rüstungstypen

| Typ | Klassen |
|---|---|
| Stoff | Priester, Magier, Hexenmeister |
| Leder | Schurke, Druide |
| Kette | Jäger |
| Platte | Krieger, Paladin |

Ein Item kann nur von Klassen seines Rüstungstyps getragen werden.

### 20.4 Waffen- und Nebenhandtypen

| Typ | Slot | Tragbar von |
|---|---|---|
| Stab | Haupthand | Priester, Magier, Hexenmeister, Druide |
| Streitkolben | Haupthand | Priester, Paladin |
| Schwert | Haupthand | Krieger |
| Axt | Haupthand | Krieger |
| Dolch | Haupthand | Schurke |
| Bogen | Haupthand | Jäger |
| Artefakt | Nebenhand | Priester |
| Schild | Nebenhand | Krieger, Paladin |
| Zauberkugel | Nebenhand | Magier |
| Grimoire | Nebenhand | Hexenmeister |
| Götze | Nebenhand | Druide |
| Köcher | Nebenhand | Jäger |
| Nebenhand-Dolch | Nebenhand | Schurke |

### 20.5 Grundwerte (Basiseffekt)

Jedes **benannte Item** hat **immer denselben Grundwert-Typ** (z.B. „Schildkrötenhelm“ gibt **immer** Rüstung, **nie** HP). Nur die Höhe variiert.

| Item-Kategorie | Möglicher Grundwert (einer pro benanntem Item) |
|---|---|
| Rüstung (alle Rüstungsslots, Umhang) | **HP** oder **Rüstung** oder **Resistenz** |
| Haupthand-Waffen, Artefakt, Zauberkugel, Grimoire, Götze | **Schaden** oder **Heilstärke** |
| Schild | **Rüstung** oder **HP** |
| Köcher, Nebenhand-Dolch | **Schaden** |
| Halskette | **Mana** oder **Mana-Reg** |
| Ring | **Krit** oder **Tempo** |
| Schmuckstück | **Heilstärke**, **Schaden**, **Mana-Reg**, **Krit** oder **Tempo** |

**Höhe des Grundwerts:**
```
Grundwert = Levelwert(Mindestlevel des Items) × Slotgewicht × Raritätsmultiplikator × Zufallsfaktor
```
- **Levelwert:** steigt mit dem Level. **Das Level ist wichtiger als die Rarität:** Ein graues Item auf Level 48 kann besser sein als ein blaues auf Level 38.
- **Slotgewicht:** Brust/Hose/Haupthand höher, Armschienen/Gürtel/Ring niedriger.
- **Raritätsmultiplikator:** steigt von Grau bis Mythisch+.
- **Zufallsfaktor (Variation):** Jedes Item würfelt innerhalb seiner Rarität eine Stärke (z.B. zwischen schwach und stark). Dadurch ist **nicht jeder grüne Helm gleich gut**. Die Stärke wird im Tooltip als Qualitätsbalken bzw. Prozent angezeigt. **[Festlegung: Anzeige]**

### 20.6 Enchantments

| Enchantment | Wirkung |
|---|---|
| + % Mana-Reg | |
| + % Mana | |
| + % Schaden | |
| + % Heilstärke | |
| + % HP | |
| + % Rüstung | |
| + % Resistenz | |
| + % Krit | |
| + % Tempo | |

- Jedes Enchantment hat eine **eigene Rarität** (gleiche Farben). Die Enchantment-Rarität ist **höchstens so hoch wie die Item-Rarität** (ein graues Item kann nur graue Enchantments haben, ein episches Item graue bis epische).
- Stärke eines Enchantments = Grundwert der Enchantment-Rarität × **Zufallsfaktor** (Variation innerhalb der Rarität).
- Enchantments sind **zufällig** und **nicht veränderbar** (kein Neuwürfeln, kein Übertragen).
- Enchantments können auf jedem Slot vorkommen; sie sind **unabhängig** vom Grundwert-Typ (ein Stab mit Heilstärke-Grundwert kann + % Schaden als Enchantment haben).
- Enchantment-Prozente gelten für den **gesamten** Wert der Figur (Formel Kapitel 8.2), nicht nur für das Item.

### 20.7 Benannte Items

- **Jedes Item hat einen eigenen Namen** (z.B. „Schildkrötenhelm“).
- Jedes benannte Item hat fest: **Name, Slot, Rüstungs-/Waffentyp, Grundwert-Typ, Raritätsbereich, Herkunft** (Welt/Raid/Abgrund/Händler) und ein eigenes Pixel-Icon.
- **Raritätsbereich:** Jedes benannte Item kann nur in bestimmten Raritäten vorkommen (z.B. Schildkrötenhelm: Grau–Grün; ein anderer Helm derselben Welt: Episch–Legendär). Pro Welt/Raid/Abgrund gibt es für jeden Slot und Typ **6 benannte Items** mit den Bereichen Grau–Grün, Grün–Blau, Blau–Lila, Lila–Gold, Gold–Rot★ und einem **Zusatz-Item**, das einen dieser Bereiche doppelt belegt (so gibt es z.B. mehrere Helme, die nur Grau–Grün droppen). Damit ist **jede Rarität** überall möglich.
- **Mindestlevel:** ergibt sich aus dem **Ort des Drops** (Level der Welle bzw. Raidlevel/60).
- Anzeige des Namens in der Raritätsfarbe; Mythisch+ mit Stern-Symbol „★“ hinter dem Namen.
- Vollständige Listen: in den Inhaltsdateien pro Welt/Raid.

### 20.8 Charakterfenster (Ausrüstung)

Aufbau wie Screenshot 2 (WoW-Charakterfenster):
- **Oben:** Porträt (Pixel-Kopf), Name, „Level X [Rasse] Priester(in)“, Spezialisierung.
- **Mitte:** große Pixel-Figur des Spielers (Aussehen ändert sich durch Ausrüstung nicht). Pfeile zum Drehen sind nicht nötig (2D). **[Festlegung]**
- **Links:** 6 Slots (Helm, Halskette, Schultern, Umhang, Brust, Armschienen).
- **Rechts:** 6 Slots (Handschuhe, Gürtel, Hose, Schuhe, Ring, Schmuckstück).
- **Unten:** 2 Slots (Haupthand, Nebenhand/Artefakt).
- **Werte-Anzeige** (unter oder neben dem Fenster): alle Werte aus Kapitel 8 mit Endwert; Tooltip zeigt Aufschlüsselung (Level, Items, Enchantments, Talente, Karten).
- **Reiter:** „Ausrüstung“, „Karten“ (gesammelte Karten, Kapitel 22).
- Ausrüsten per **Drag & Drop** oder **Rechtsklick** im Inventar. Items, die man nicht tragen kann (falscher Typ, zu niedriges Level), sind im Inventar rot markiert.
- **Für Gruppenmitglieder** gibt es dasselbe Fenster (über das Gruppen-Menü). Rechtsklick auf ein Item im Inventar, während das Fenster eines Mitglieds offen ist, rüstet es beim Mitglied aus.

### 20.9 Tooltips

- Name (Raritätsfarbe), Rarität, Slot, Typ, Mindestlevel, Grundwert, Qualitätsbalken, Enchantments (jeweils in ihrer Raritätsfarbe), Verkaufspreis.
- **Automatischer Vergleich:** Daneben wird das aktuell getragene Item desselben Slots angezeigt (vom Spieler bzw. vom geöffneten Mitglied), mit **grünen/roten Differenzen** der Endwerte.

---

## 21. Inventar und Taschen

- **Start:** Rucksack mit **9 Plätzen** (fest, kann nicht entfernt werden).
- **4 zusätzliche Taschenplätze.** In jeden kann eine Tasche gelegt werden.
- **Taschen** sind Items mit einer Anzahl Plätze; es gibt schlechtere und bessere Taschen.
- **Quellen:** **Kauf beim Schmied** (bessere Taschen mit höherer Schmied-Stufe) und **Drops** (Taschen können als Drop oder als Auswahl-Belohnung vorkommen; seltenere Taschen haben mehr Plätze).
- Taschen haben eine Rarität (Grau bis Legendär), die nur die Anzahl Plätze bestimmt. Taschen haben keine Enchantments. **[Festlegung]**
- Eine Tasche kann nur ausgetauscht werden, wenn sie leer ist.
- Taschenfenster (Taste B): alle Taschen nebeneinander, Sortier-Knopf, Anzeige freier Plätze.
- Tränke stapeln sich (gleicher Trank = ein Platz, bis zu einer Stapelgröße). **[Festlegung]**
- **Verkaufen:** Items können an **Schmied und Waffenmeister** verkauft werden (beide kaufen alle Items). Preis nach Level und Rarität. Mehrfachverkauf: „Alle grauen verkaufen“. **[Festlegung]**
- Items können auch weggeworfen werden (Bestätigung bei Blau und höher). **[Festlegung]**

Taschenliste: `inhalte/HAENDLER_TRAENKE_TASCHEN.md`.

---

## 22. Karten-System

- **Wann:** Nach dem **ersten Abschluss jeder Welt** (nach der Auswahl-Belohnung von Welle 10) und nach dem **ersten Abschluss jedes Raids**. **Nicht** im Abgrund.
- **Auswahl:** Es werden **2 Karten** angezeigt. Der Spieler wählt **1**.
- **Neu würfeln:** Für Gold können beide Karten neu gewürfelt werden, **unbegrenzt oft**; jeder Reroll bei derselben Wahl kostet mehr. Die Kosten steigen außerdem mit der Welt.
- **Rarität:** Karten haben die 7 Raritäten. Höhere Rarität = stärkerer Effekt. Spätere Welten/Raids geben bessere Chancen auf seltene Karten. Innerhalb einer Rarität variiert der Wert.
- **Dauer:** **Permanent** auf dem Charakter. Karten **stapeln** sich (auch gleiche Karten).
- **Wirkung:** Als **letzter Multiplikator** (Kapitel 8.2): Summe aller Karten-% eines Wertes.
- **Arten:**
  1. **Spieler-Werte:** + % auf einen Wert des Spielers (Mana-Reg, Mana, Heilstärke, Schaden, HP, Rüstung, Resistenz, Krit, Tempo).
  2. **Gruppen-Werte:** + % auf einen Wert **aller Gruppenmitglieder** (und Raidfüller) – HP, Schaden, Rüstung, Resistenz, Krit, Tempo.
  3. **Zaubereffekte:** Verbessern einen bestimmten Zauber (z.B. „Blitzheilung kostet X % weniger Mana“, „Machtwort: Schild absorbiert X % mehr“). Solche Karten werden nur angeboten, wenn der Spieler den Zauber gelernt hat oder lernen kann (Spezialisierung passt).
- Karten-Sammlung im Charakterfenster (Reiter „Karten“) und über Taste K: alle Karten, Summen pro Wert.

Kartenliste: `inhalte/KARTEN.md`.

---

## 23. Lehrmeister

Links im UI. Fenster mit Porträt und zwei Reitern.

**Reiter „Zauber“:**
- Liste aller Zauber und Ränge des Priesters (Allgemein + eigene Spezialisierung).
- Jeder Eintrag: Icon, Name, Rang, benötigtes Level, Preis in Gold, Status: **lernbar** (grün), **Level zu niedrig** (grau mit Level), **bereits gelernt** (abgehakt).
- Zauber, die man erst später lernen kann, werden **ausgegraut mit benötigtem Level** angezeigt (Vorschau).
- Zauber anderer Spezialisierungen werden nicht angezeigt.
- Knopf „Lernen“; Knopf „Alle lernbaren lernen“ (zeigt Gesamtpreis). **[Festlegung]**
- Neue lernbare Zauber: Das Porträt des Lehrmeisters zeigt ein Ausrufezeichen.

**Reiter „Talente zurücksetzen“** (ab Level 10): Preis wird angezeigt, steigt mit jedem Reset.

**Spezialisierung** wird nicht hier gewählt (Pflichtfenster bei Level 10).

---

## 24. Schmied

Links im UI. Fenster mit Porträt und Reitern: **Laden**, **Fusion**, **Taschen**, **Verkaufen**, **Upgrade**.

### 24.1 Laden (Rüstung)
- Verkauft **Rüstung** (alle Rüstungsslots inkl. Umhang) und **Schmuck** (Halskette, Ring, Schmuckstück) **für alle Klassen**. **[Festlegung: Schmuck beim Schmied]**
- **6 Angebote** gleichzeitig. **[Festlegung]**
- Items haben **Level nahe dem Spielerlevel** (aus den benannten Items der höchsten freigeschalteten Welt).
- Die Ware ist **in der Regel etwas schlechter als Quest-Belohnungen**: Der Zufallsfaktor der Grundwerte und Enchantments wird im unteren Bereich gewürfelt, und die Rarität ist durch die Schmied-Stufe begrenzt.
- Höhere Rarität und höheres Level = teurer.
- **Warenwechsel alle 10 Minuten** (Timer läuft nur, während das Spiel läuft; Anzeige unter dem Porträt).

### 24.2 Fusion
- **5 Items** desselben **Slots** und derselben **Rarität** → **1 Item der nächsthöheren Rarität**.
- Kosten: Gold (steigt mit Rarität und Level).
- **Ergebnis:** Ein **zufälliges benanntes Item desselben Slots**. **Level = höchstes Level** der eingesetzten Items. Es wird aus den benannten Items der Welt/des Raids gewählt, zu dem dieses Level gehört, **deren Raritätsbereich die neue Rarität enthält** (die Fusion hebt ein Item nie über seinen Bereich; es wird ein anderes passendes Item gewählt).
- Rüstungs-/Waffentyp des Ergebnisses: zufällig, gewichtet nach den Typen der eingesetzten Items (z.B. 4 Platte + 1 Stoff → 80 % Platte). **[Festlegung]**
- Werte und Enchantments werden neu gewürfelt.
- **Grenze:** Nur bis **Mythisch**. Mythisch → Mythisch+ ist nicht möglich.
- Ausgerüstete Items müssen zuerst abgelegt werden. **[Festlegung]**
- Die Fusion gilt für **alle Slots** (auch Waffen).

### 24.3 Taschen
- Verkauft Taschen. Bessere Taschen (mehr Plätze) mit höherer Schmied-Stufe; bessere Taschen sind teurer.

### 24.4 Upgrade
- Upgrade-Stufen können bei **Spielerlevel 10, 20, 30, 40, 50, 60** gekauft werden (jeweils **viel Gold**).

| Schmied-Stufe | Benötigt | Laden: max. Rarität | Fusion kostet | Taschen |
|---|---|---|---|---|
| 0 (Start) | – | Ungewöhnlich | **5** Items | kleine Taschen |
| 1 | Level 10 | Selten | 5 | + größere |
| 2 | Level 20 | Selten | **4** Items | + größere |
| 3 | Level 30 | Episch | 4 | + größere |
| 4 | Level 40 | Episch | **3** Items (Minimum) | + größere |
| 5 | Level 50 | Legendär | 3 | + größere |
| 6 | Level 60 | Legendär | 3 | beste Taschen |

**[Festlegung: Max. Rarität pro Stufe]** Jede Stufe verbessert außerdem die Chance auf höhere Raritäten im Laden. Bessere Ware ist auch teurer.

### 24.5 Verkaufen
Siehe Kapitel 21.

---

## 25. Waffenmeister

Links im UI. Fenster mit Reitern: **Laden**, **Verkaufen**, **Upgrade**.

### 25.1 Laden
- Verkauft **Waffen und Nebenhand-Items für alle Klassen** und **Tränke**.
- **Weniger Waffen-Angebote** als der Schmied: **4 Waffen-Plätze**. **[Festlegung]** Waffen sind wie beim Schmied etwas schlechter als Quest-Belohnungen.
- **Heiltränke und Manatränke:** immer verfügbar (unbegrenzter Vorrat). Mit Stufe 0 nur die schwächste Trankstufe, **jede Upgrade-Stufe fügt die nächstbessere Trankstufe hinzu** (die alten bleiben im Angebot).
- **Warenwechsel alle 10 Minuten** (nur während das Spiel läuft). Beim Warenwechsel kann **statt einer Waffe** auf einem Waffen-Platz ein **Spezialtrank** erscheinen (begrenzte Menge, meist 1–3 Stück). **[Festlegung: Menge]**

### 25.2 Tränke

| Trank | Wirkung | Nutzung |
|---|---|---|
| **Heiltrank** (7 Stufen) | Stellt sofort HP des Spielers her | Im Kampf, **gemeinsame Trank-Abklingzeit** |
| **Manatrank** (7 Stufen) | Stellt sofort Mana her | Im Kampf, gemeinsame Trank-Abklingzeit |
| **Regenerationstrank** (Spezial) | Stellt HP und Mana des Spielers über einige Sekunden her | Im Kampf, gemeinsame Trank-Abklingzeit |
| **EP-Trank** (Spezial) | + % EP für **X Wellen**, gilt für **den Spieler und die ganze Gruppe** | Jederzeit, keine Trank-Abklingzeit |
| **Gold-Trank** (Spezial) | + % Gold für X Wellen | Jederzeit, keine Trank-Abklingzeit |
| **Werte-Trank** (Spezial, mehrere Sorten) | + % Heilstärke **oder** + % Mana-Reg **oder** + % Schaden für **eine Welle** | Jederzeit, keine Trank-Abklingzeit |

- Heil-, Mana- und Regenerationstränke wirken **nur auf den Spieler**.
- Die Trank-Abklingzeit ist eine eigene, von Zaubern unabhängige Abklingzeit.
- Tränke können auf die Aktionsleiste gezogen oder im Inventar per Rechtsklick benutzt werden.
- Spezialtränke haben Raritäten (Stärke). **[Festlegung]**

### 25.3 Upgrade

| Waffenmeister-Stufe | Benötigt | Laden: max. Rarität | Trankstufen verfügbar |
|---|---|---|---|
| 0 (Start) | – | Ungewöhnlich | Stufe 1 (Schwach) |
| 1 | Level 10 | Selten | + Stufe 2 (Gering) |
| 2 | Level 20 | Selten | + Stufe 3 (Normal) |
| 3 | Level 30 | Episch | + Stufe 4 (Groß) |
| 4 | Level 40 | Episch | + Stufe 5 (Überragend) |
| 5 | Level 50 | Legendär | + Stufe 6 (Mächtig) |
| 6 | Level 60 | Legendär | + Stufe 7 (Meisterlich) |

Jede Stufe erhöht außerdem die Chance auf Spezialtränke und deren Rarität beim Warenwechsel.

Listen: `inhalte/HAENDLER_TRAENKE_TASCHEN.md`.

---

## 26. Speichern, Optionen, Menüs

### 26.1 Speichern
- **Automatisch, lokal**: nach jeder Welle, nach jedem Kauf/Verkauf/Fusion/Upgrade, nach Ausrüstungsänderungen, nach Kartenwahl/Belohnungswahl, beim Wechsel zur Charakterauswahl und beim Beenden.
- Jeder Charakter wird einzeln gespeichert (Level, EP, Gold, Inventar, Ausrüstung, Gruppe mit Ausrüstung, Zauber, Aktionsleiste, Talente, Spezialisierung, Karten, Welt-/Raid-/Abgrund-Fortschritt, Shop-Angebote und Timer, Rekrutierungs-Kandidaten, Raid-Abklingzeiten, Modus, Status „Gefallen“).
- **Spiel während eines Kampfes geschlossen:** Die Welle **zählt nicht**. Beim nächsten Start steht man vor derselben Welle, als wäre sie nie gestartet worden (keine Tode, keine Strafe; im Kampf verbrauchte Tränke bleiben verbraucht). **[Festlegung: Tränke]** In Hardcore gilt das ebenso.
- Hardcore: Um Missbrauch zu verhindern, wird der Tod des Spielers **sofort** gespeichert, sobald die Welle verloren ist.

### 26.2 Optionen
- **Grafik:** Vollbild/Fenster, Auflösung, Skalierung der Oberfläche.
- **Audio:** Gesamt-, Musik-, Effektlautstärke.
- **Sprache:** Englisch (Standard) / Deutsch.
- **Steuerung:** Tastenbelegung (Kapitel 13.5), Zaubermodus (Ziel-Klick, Mouseover, beides), Aktionsleiste sperren.
- **Interface:** Schwebende Zahlen an/aus, Meter an/aus.
- **Hardcore:** Mana-Schwellwert für Auto-Weiter (auch in der oberen Leiste).

---

## 27. Übersicht aller Festlegungen zur Prüfung

Diese Details wurden nicht ausdrücklich abgefragt. Ich habe sie so festgelegt, dass sie zu deinen Vorgaben passen, ohne neue Systeme zu erfinden. Bitte prüfen:

1. Klassen sind an einer festen Grundkleidung/Silhouette erkennbar (Ausrüstung ändert nichts).
2. Ohne Charakter startet das Spiel direkt in der Charaktererstellung.
3. Namensregeln: 2–12 Buchstaben.
4. Startausrüstung (graue Items) und etwas Start-Gold.
5. Wiederbelebungsschwäche gilt für die nächste Welle; wer im Kampf wiederbelebt wird, bekommt sie nicht.
6. Mikromenü unten rechts mit Standardtasten C, P, N, B, G, K, M, R.
7. Buffs/Debuffs im Kampf wirken nach den Karten.
8. Krit = doppelte Wirkung.
9. Tote Mitglieder bekommen Quest-EP (Normal).
10. Figuren auf dem Schlachtfeld sind auch anklickbar; ohne Ziel heilt man sich selbst; Tab für Gegnerwechsel; Angriff ohne Ziel trifft das Ziel des Tanks; Taste X bricht einen Cast ab.
11. Aggro-Wechsel bei 110 % (Nahkampf) / 130 % (Fernkampf).
12. Auferstehung: Ziel steht mit wenig HP und Mana auf.
13. Beim Entlassen kommen die Items ins Inventar.
14. Kandidaten-Startausrüstung meist Grau/Grün, selten Blau.
15. Niederlage in Welle 1 einer Welt: man bleibt auf Welle 1; der Höchstfortschritt geht nie verloren.
16. Weltwechsel nur zwischen Wellen.
17. Raidfüller werden bei weniger als 4 Mitgliedern mit DPS ergänzt; KI-Heiler bannen nicht.
18. Gescheiterter Raid → zurück in die Welt; abgebrochener Raid = kein Fortschritt; Abklingzeit startet nach dem Endboss und läuft auch offline.
19. Raid-Quest-Belohnungen werden pro Welle sofort vergeben, auch wenn der Versuch später scheitert.
20. Automatische Quest-Belohnungen geben auch Gold.
21. Raidbosse droppen garantiert mindestens ein Item; volles Inventar = Drop verloren.
22. Jedes Enchantment auf einem Item ist ein anderer Werttyp.
23. Qualitätsbalken im Tooltip zeigt die Variation.
24. Taschen: Rarität bestimmt nur die Plätze, keine Enchantments; Tränke stapeln sich; „Alle grauen verkaufen“; Wegwerfen mit Bestätigung.
25. Schmied verkauft auch Schmuck (Halskette, Ring, Schmuckstück); 6 Angebote; Waffenmeister 4 Waffen-Plätze.
26. Max. Rarität im Laden pro Stufe (Tabellen 24.4 und 25.3).
27. Fusion: Typ gewichtet nach Eingabe-Items; ausgerüstete Items können nicht fusioniert werden.
28. Spezialtränke erscheinen in Mengen von 1–3 und haben Raritäten.
29. Tränke, die in einem abgebrochenen Kampf verbraucht wurden, bleiben verbraucht.
30. „Alle lernbaren lernen“-Knopf beim Lehrmeister.
31. Welt-Levelbereiche und Raid-Voraussetzungen (Tabellen 16.1 und 17.1).
32. Klassen-Fähigkeiten der Mitglieder (Tabelle 15.2) und Rassenverteilung (Tabelle 15.4).
33. Zauber aus Talenten sind nach dem Lernen sofort im Zauberbuch (keine Kosten beim Lehrmeister).
34. Die beiden angebotenen Karten sind nie identisch; Mythisch+-Karten wirken zusätzlich auf einen verwandten Wert.
35. Heil-/Manatränke haben ein Mindestlevel; Spezialtränke haben Raritäten; gleiche Trank-Effekte ersetzen sich (der stärkere bleibt); „X Wellen“ zählt jede gespielte Welle.
36. Taschen: Schmied-Taschen immer vorrätig; zusätzliche Drop-Taschen pro Welt (Liste in `inhalte/HAENDLER_TRAENKE_TASCHEN.md`).
37. In Welt 9 und 10 können auch Elite-Gegner (Nekromant, Brutbeschwörer) Adds rufen, und der Drachenwächter (Elite, Welt 10) hat ein Enrage.
38. Abgrund: Die Auswahl-Belohnung der Bosse ist bis Welle 60 mindestens Legendär, ab Welle 70 mindestens Mythisch.
39. Abgrund-Boss „Mahlkiefer“ nutzt einen stapelnden Tank-Debuff; mit 2 eigenen Tanks wechseln sie automatisch, mit 1 Tank muss gegengeheilt werden.
40. Einige Inhaltsdateien nennen feste Mengen bei Mechaniken (z.B. „Debuff auf 3 Ziele“, „ruft 2 Adds“).
41. Grundwerte von Schmuck: Halskette = Mana oder Mana-Reg, Ring = Krit oder Tempo, Schmuckstück = Heilstärke/Schaden/Mana-Reg/Krit/Tempo; Schild = Rüstung oder HP; Köcher/Nebenhand-Dolch = Schaden (Kapitel 20.5).
42. Konkrete Waffentypen pro Klasse (Krieger Schwert/Axt + Schild, Paladin Streitkolben + Schild, Magier Stab + Zauberkugel, Hexenmeister Stab + Grimoire, Druide Stab + Götze, Jäger Bogen + Köcher, Schurke Dolch + Nebenhand-Dolch).
43. Auch der Spieler bekommt im Normal-Modus nach seinem Tod die Wiederbelebungsschwäche; in Hardcore steht er nach einer gewonnenen Welle mit wenig HP und Mana auf.
44. Zielfenster (freundliches und feindliches Ziel) oben links am Schlachtfeld.
45. Namen werden automatisch mit großem Anfangsbuchstaben und sonst klein geschrieben; beim Tippen werden nur Buchstaben angenommen.
46. Start-Gold eines neuen Charakters: 10.
47. Englische Weltnamen (z. B. Grünhain = Greengrove, Nebelmoor = Mistmoor), da Englisch die Standardsprache ist.
48. Charakterauswahl per Tastatur: Pfeil hoch/runter wählt, Enter betritt die Welt, Entf löscht, ESC öffnet das Menü.
49. Die Lautstärke-Regler (auch Musik) sind bereits in den Optionen; die Musik selbst folgt in einer späteren Version.
50. Hintergründe als zusammenhängende Orte mit Logik über den Bildrand hinaus; Wolken in 3 Ebenen mit 12 Verformungs-Frames; Straßenlaternen mit flackernder Flamme, Lichtschein und Lichtkegel am Boden; Glühwürmchen, Rauch, Dampf, Funken, Vögel, wehende Fahnen, drehende Zahnräder und Windmühlenflügel.
51. Alle Zauber, Ränge, Talente, Weltinhalte, Gegner, Bosse, Quests, Items und Karten in `inhalte/` sind **Vorschläge** und können frei geändert werden.

---

## 28. Glossar

| Begriff | Bedeutung |
|---|---|
| **Aggro / Bedrohung** | Bestimmt, wen ein Gegner angreift |
| **AoE** | Flächenschaden auf mehrere/alle Ziele |
| **Add** | Zusätzlicher Gegner, der während eines Bosskampfes erscheint |
| **Bannen** | Entfernen eines Debuffs (Magie/Krankheit) |
| **Cast / Castzeit** | Zeit, die ein Zauber zum Wirken braucht |
| **DoT / HoT** | Schaden bzw. Heilung über Zeit |
| **DPS** | Schadensrolle |
| **Enrage** | Boss wird nach Zeit stark gefährlicher |
| **EP** | Erfahrungspunkte |
| **GCD** | Globale Abklingzeit nach jedem Zauber |
| **Tank** | Rolle, die Gegner auf sich hält |
| **Tank-Buster** | Sehr starker Einzelangriff auf den Tank |
| **Wipe** | Alle sind tot, Welle verloren |

---

## 29. Zusätzliche Features (vom Auftraggeber genehmigt)

Diese Features wurden nachträglich vorgeschlagen und genehmigt. Details, die nicht abgefragt wurden, sind als **[Festlegung]** markiert.

| Feature | Beschreibung |
|---|---|
| **Titelbildschirm** | Siehe Kapitel 4.0. |
| **Rassen-Hintergründe, Namen würfeln, Rassen-Beschreibung** | Siehe Kapitel 5. |
| **Charakter-Info, Gruppe im Hintergrund, Reihenfolge ändern** | Siehe Kapitel 4.1. |
| **Einführung in Welt 1** | Beim ersten Spielen erscheinen kurze Hinweis-Blasen an den passenden Stellen (Ziel wählen und heilen, Mana, HoT, Tank-Buster am Castbalken, Lehrmeister, Ausrüstung, Kartenwahl). Jeder Hinweis erscheint nur einmal pro Charakter. In den Optionen abschaltbar. |
| **Trainingspuppe** | Zwischen den Wellen kann der Spieler einen **Übungsmodus** starten: Eine Trainingspuppe steht bei den Gegnern, die Gruppe nimmt gleichmäßigen Übungsschaden. Zauber können ohne Risiko ausprobiert werden (niemand kann sterben, Mana und HP werden nach dem Übungsmodus wieder auf den Stand davor gesetzt, keine EP/Gold/Drops). Beenden jederzeit per Knopf. **[Festlegung: Ablauf]** |
| **Spielgeschwindigkeit** | Option 0,75× / 1× / 1,25× für die Kampfgeschwindigkeit. **Nur im Normal-Modus** wählbar; Hardcore läuft immer mit 1×. |
| **Erfolge** | Sammel-Erfolge ohne Belohnung (z.B. „Welt 1 ohne Tod“, „100.000 Heilung“, „Erster Raid-Endboss“). Fenster „Erfolge“ im Mikromenü; Pop-up beim Freischalten. Erfolge gelten pro Charakter. **[Festlegung: pro Charakter]** |
| **Kampf-Statistik (Charakter)** | Lebenslange Statistik pro Charakter: gesamte Heilung, Überheilung, gesamter Schaden, besiegte Gegner und Bosse, Tode, gerettete Mitglieder (per Auferstehung), gespielte Wellen, Spielzeit. Anzeige als Reiter im Charakterfenster. |
| **Item-Sperre** | Items können per Rechtsklick-Menü/Taste mit einem **Schloss** gesperrt werden. Gesperrte Items können nicht verkauft, fusioniert oder weggeworfen werden. |
| **Ausrüstungs-Sets** | Im Charakterfenster können mehrere Ausrüstungs-Sets gespeichert (Name + Symbol) und per Knopf gewechselt werden (z.B. Heil-Set / Schadens-Set). Wechsel nur außerhalb des Kampfes. Items in einem Set bleiben im Inventar, wenn sie nicht getragen werden. **[Festlegung: Anzahl Sets = 5, Wechsel nur außerhalb des Kampfes]** |
