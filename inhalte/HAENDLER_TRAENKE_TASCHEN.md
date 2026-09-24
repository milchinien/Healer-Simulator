# Händler, Tränke und Taschen

Grundlage: `../GAME_DESIGN.md`, Kapitel 21, 24 und 25.

---

## 1. Allgemeine Händlerregeln

- **Warenwechsel:** Schmied und Waffenmeister wechseln ihre Angebote alle **10 Minuten**. Der Timer läuft nur, während das Spiel läuft (pro Charakter gespeichert). Unter dem NPC-Porträt links im UI wird die Restzeit angezeigt.
- **Quelle der Ware:** Die Items im Laden stammen aus dem Item-Katalog der **höchsten freigeschalteten Welt** (bzw. ab Level 40/50/60 zusätzlich aus dem Katalog des freigeschalteten Raids). Das **Level** der Items liegt beim **Spielerlevel** oder knapp darunter.
- **Qualität:** Laden-Items würfeln Grundwert und Enchantments **im unteren Bereich** ihres Zufallsfaktors → in der Regel etwas schlechter als Quest-Belohnungen.
- **Maximale Rarität:** durch die Händler-Stufe begrenzt (Hauptdokument, Tabellen 24.4 und 25.3). Höhere Stufe = höhere Chance auf die maximale Rarität.
- **Klassen:** Angebote für **alle Klassen** (zufällig gemischt).
- **Preise:** steigen mit Level und Rarität. Ein Laden-Item kostet deutlich mehr als sein Verkaufswert.
- **Gekaufte Angebote** verschwinden bis zum nächsten Warenwechsel (der Platz bleibt leer).
- **Verkaufen:** Beide Händler kaufen **alle** Items. Verkaufspreis nach Level und Rarität (Enchantments erhöhen den Preis leicht). Knopf „Alle grauen verkaufen“. Kein Rückkauf.

---

## 2. Schmied

| Reiter | Inhalt |
|---|---|
| Laden | 6 Angebote: Rüstung (alle Rüstungsslots + Umhang) und Schmuck (Halskette, Ring, Schmuckstück) |
| Fusion | 5 / 4 / 3 Items (je nach Stufe) desselben Slots und derselben Rarität → 1 Item der nächsthöheren Rarität (bis Mythisch) |
| Taschen | Taschen der aktuellen Schmied-Stufe und aller niedrigeren Stufen (immer vorrätig, unbegrenzt) |
| Verkaufen | siehe oben |
| Upgrade | Nächste Stufe kaufen (Level 10/20/30/40/50/60, jeweils viel Gold) |

**Fusion – Bedienung:** Fenster mit 5 Plätzen (bzw. 4/3). Items werden per Drag & Drop oder Rechtsklick hineingelegt. Sobald alle Plätze mit passenden Items belegt sind, zeigt die Vorschau: „Zufälliges Item: [Slot], [neue Rarität], Level [höchstes Level]“, die Gewichtung der Typen und die Goldkosten. Knopf „Fusionieren“ mit Bestätigung. Das Ergebnis erscheint mit Aufblitzen in der Raritätsfarbe.

---

## 3. Waffenmeister

| Reiter | Inhalt |
|---|---|
| Laden | 4 Waffen-Plätze (Haupthand und Nebenhand für alle Klassen; beim Warenwechsel kann ein Platz stattdessen einen Spezialtrank enthalten) + dauerhaftes Trankregal |
| Verkaufen | siehe oben |
| Upgrade | Nächste Stufe kaufen (Level 10/20/30/40/50/60) |

**Spezialtrank-Chance:** Pro Warenwechsel hat jeder Waffen-Platz eine Chance, ein Spezialtrank zu sein. Die Chance und die Rarität der Spezialtränke steigen mit der Waffenmeister-Stufe. Spezialtränke gibt es in Mengen von 1–3 Stück.

---

## 4. Tränke

### 4.1 Heil- und Manatränke (dauerhaft im Regal des Waffenmeisters)

| Stufe | Heiltrank | Manatrank | Verfügbar ab Waffenmeister-Stufe |
|---|---|---|---|
| 1 | Schwacher Heiltrank | Schwacher Manatrank | 0 (Start) |
| 2 | Geringer Heiltrank | Geringer Manatrank | 1 |
| 3 | Heiltrank | Manatrank | 2 |
| 4 | Großer Heiltrank | Großer Manatrank | 3 |
| 5 | Überragender Heiltrank | Überragender Manatrank | 4 |
| 6 | Mächtiger Heiltrank | Mächtiger Manatrank | 5 |
| 7 | Meisterlicher Heiltrank | Meisterlicher Manatrank | 6 |

- Wirkung: stellt sofort HP bzw. Mana **des Priesters** her (höhere Stufe = mehr).
- Unbegrenzt vorrätig, Preis steigt mit der Stufe.
- **Gemeinsame Trank-Abklingzeit** (im Kampf).
- Jede Trankstufe hat ein **Mindestlevel** (damit ein Level-5-Charakter keine Stufe-7-Tränke nutzt, falls er sie besitzt). **[Festlegung]**
- Pixel-Icons: rote (Heil) und blaue (Mana) Flaschen; höhere Stufen = größere, verziertere Flaschen.

### 4.2 Spezialtränke (nur zufällig beim Waffenmeister, auch als Auswahl-Belohnung möglich)

Spezialtränke haben eine **Rarität** (Grau bis Legendär); höhere Rarität = stärkerer Effekt bzw. mehr Wellen. **[Festlegung]**

| Trank | Wirkung | Nutzung | Icon |
|---|---|---|---|
| **Regenerationstrank** | Stellt HP **und** Mana des Priesters über einige Sekunden her | Im Kampf, gemeinsame Trank-Abklingzeit | Grün-blau wirbelnde Flasche |
| **Trank der Erkenntnis** (EP-Trank) | + % EP für **X Wellen** – für den Priester **und alle Gruppenmitglieder** | Jederzeit, keine Trank-Abklingzeit | Violette Flasche mit Stern |
| **Trank des Wohlstands** (Gold-Trank) | + % Gold für X Wellen | Jederzeit, keine Trank-Abklingzeit | Goldene Flasche mit Münze |
| **Trank des Lichts** (Werte-Trank) | + % Heilstärke für **eine Welle** | Jederzeit, keine Trank-Abklingzeit | Weiß leuchtende Flasche |
| **Trank der Klarheit** (Werte-Trank) | + % Mana-Reg für eine Welle | Jederzeit, keine Trank-Abklingzeit | Hellblaue Flasche mit Tropfen |
| **Trank der Zerstörung** (Werte-Trank) | + % Schaden für eine Welle | Jederzeit, keine Trank-Abklingzeit | Dunkelrote Flasche mit Flamme |

- Gleichartige Effekte stapeln nicht: Ein neuer Trank derselben Sorte ersetzt den alten (der stärkere bleibt). **[Festlegung]**
- „Für X Wellen“ zählt jede gespielte Welle (auch verlorene und wiederholte). **[Festlegung]**
- Aktive Trank-Effekte werden als Buff-Symbole beim Priester angezeigt (mit Anzahl verbleibender Wellen).

### 4.3 Trank-Paket (Auswahl-Belohnung)
Ein **Trank-Paket** enthält mehrere Heil- und Manatränke der zur Welt passenden Stufe und zusätzlich 1–2 Spezialtränke. Die Zusammensetzung steht in der jeweiligen Welt-/Raid-Datei.

### 4.4 Stapel
Tränke stapeln sich pro Sorte, Stufe und Rarität in einem Inventarplatz bis zu einer festen Stapelgröße.

---

## 5. Taschen

- Start: **Rucksack mit 9 Plätzen** (fest).
- **4 Taschenplätze** für zusätzliche Taschen.
- Taschen haben eine **Rarität** (nur Plätze, keine Enchantments). Höhere Rarität = mehr Plätze.
- Taschen tauschen: nur wenn die alte Tasche leer ist.

### 5.1 Schmied-Taschen (kaufbar, unbegrenzt vorrätig)

| Tasche | Rarität | Plätze (relativ) | Ab Schmied-Stufe | Icon |
|---|---|---|---|---|
| Leinenbeutel | Gewöhnlich | klein | 0 | Kleiner grauer Stoffbeutel |
| Wollsack | Gewöhnlich | klein+ | 1 | Brauner Wollsack |
| Lederranzen | Ungewöhnlich | mittel | 2 | Lederranzen mit Schnalle |
| Seidenbeutel | Ungewöhnlich | mittel+ | 3 | Glänzender Seidenbeutel |
| Runenverstärkte Tasche | Selten | groß | 4 | Tasche mit leuchtender Rune |
| Magiestofftasche | Selten | groß+ | 5 | Violette schimmernde Tasche |
| Traumweberbeutel | Episch | sehr groß | 6 | Sternbestickter Beutel |

### 5.2 Drop-Taschen (nur als Gegner-Drop oder Auswahl-Belohnung)

| Tasche | Rarität | Plätze (relativ) | Herkunft | Icon |
|---|---|---|---|---|
| Geflickter Bauernsack | Gewöhnlich | klein | Welt 1–2 | Geflickter Jutesack |
| Sumpfhautbeutel | Ungewöhnlich | mittel | Welt 2–4 | Grüner schuppiger Beutel |
| Grubenarbeiter-Rucksack | Ungewöhnlich | mittel+ | Welt 3–5 | Rucksack mit Laterne |
| Spinnenseidentasche | Selten | groß | Welt 5–6 | Weiße netzartige Tasche |
| Feuerfeste Truhe-Tasche | Selten | groß+ | Welt 6–7 | Rote Tasche mit Metallbeschlag |
| Pelzbeutel der Frostwacht | Episch | sehr groß | Welt 7–8, Raid 1 | Weißer Pelzbeutel |
| Grabräubersack von Kharet | Episch | sehr groß+ | Welt 8–9, Raid 2 | Sandfarbener Sack mit Hieroglyphen |
| Knochenbeutel des Lichfürsten | Legendär | riesig | Welt 9–10 | Beutel aus Knochenplatten |
| Drachenschuppentasche | Legendär | riesig+ | Welt 10, Raid 3, Abgrund | Rote Schuppentasche |
| Tasche der Leere | Legendär | am größten | Abgrund, Raid 3 (selten) | Schwarz-violette wirbelnde Tasche |

### 5.3 Belohnungs-Taschen (nur aus Auswahl-Belohnungen, einmalig)

| Tasche | Rarität | Plätze (relativ) | Herkunft |
|---|---|---|---|
| Knarz' Kornsack | Ungewöhnlich | mittel | Welt 1, Auswahl-Belohnung |
| Eisenbarts Werkzeugtasche | Selten | groß | Welt 3, Auswahl-Belohnung |
| Glutgewebte Kulttasche | Episch | sehr groß | Welt 6, Auswahl-Belohnung |
| Große Pelztasche des Jarls | Episch | sehr groß+ | Welt 7, Auswahl-Belohnung |
| Frostkönigs Schatztruhe-Beutel | Episch | riesig | Raid 1, Auswahl-Belohnung |
