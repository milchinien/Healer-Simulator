# Zauber und Talente des Priesters

Grundlage: `../GAME_DESIGN.md`, Kapitel 11–13 und 23.
Alle Zauber werden **beim Lehrmeister für Gold** gelernt. Jeder Rang muss einzeln gekauft werden. Der Lehrmeister bietet **auf jedem geraden Level** (2, 4, 6 … 60) neue Zauber oder Ränge an.
**Keine konkreten Zahlen:** Kosten, Castzeiten, Abklingzeiten und Stärken sind relativ angegeben (sehr kurz / kurz / mittel / lang / sehr lang; gering / mittel / hoch / sehr hoch). Die Werte werden beim Balancing festgelegt.

Legende:
- **Castzeit:** Spontan / kurz / mittel / lang / kanalisiert (wird über Zeit gewirkt, Unterbrechung durch neuen Zauber)
- **Abklingzeit (CD):** keine / kurz / mittel / lang / sehr lang
- **Mana:** gering / mittel / hoch / sehr hoch
- **Ränge bei Level:** Level, auf denen ein neuer Rang beim Lehrmeister erscheint

---

## 1. Allgemeine Zauber (alle Spezialisierungen)

### 1.1 Startzauber (vor Level 10 – bewusst einfach)

| Zauber | Art | Castzeit | CD | Mana | Wirkung | Ränge bei Level |
|---|---|---|---|---|---|---|
| **Geringe Heilung** | Einzelheilung | mittel | keine | gering | Heilt ein Ziel mäßig. Sehr manaeffizient, aber langsam. | 1, 4, 8, 14, 20, 26, 32, 38, 44, 50, 56 |
| **Heilige Pein** | **Angriff 1** (Heilig-Schaden) | mittel | keine | gering | Fügt einem Gegner Heilig-Schaden zu. | 1, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60 |
| **Erneuerung** | Heilung über Zeit (HoT) | spontan | keine | gering | Heilt das Ziel über eine mittlere Dauer. Nicht mehrfach auf demselben Ziel stapelbar. | 2, 8, 14, 20, 26, 32, 38, 44, 50, 56 |
| **Schattenwort: Schmerz** | **Angriff 2** (Schatten-DoT) | spontan | keine | gering | Schatten-Schaden über Zeit auf einem Gegner. | 4, 10, 16, 22, 28, 34, 40, 46, 52, 58 |
| **Blitzheilung** | Schnelle Einzelheilung | kurz | keine | hoch | Heilt ein Ziel schnell, aber teuer. Die „Sofortheilung“ für Notfälle vor der Spezialisierung. | 6, 12, 18, 24, 30, 36, 42, 48, 54, 60 |

Das sind die **5 Zauber vor Level 10**: zwei einfache Angriffe und drei einfache Heilungen. Heilig und Disziplin behalten **genau diese 2 Angriffszauber** als einzige reinen Angriffe.

### 1.2 Allgemeine Zauber ab Level 10

| Zauber | Art | Castzeit | CD | Mana | Wirkung | Ränge bei Level |
|---|---|---|---|---|---|---|
| **Auferstehung** | Wiederbelebung | sehr lang | keine | sehr hoch | Belebt ein totes Gruppenmitglied im Kampf wieder. Es steht mit wenig HP und wenig Mana/Ressource auf. Höhere Ränge: mehr HP beim Aufstehen. | 10, 30, 50 |
| **Reinigung** | Bannen | spontan | kurz | mittel | Entfernt einen **Magie**-Debuff und einen **Krankheits**-Debuff vom Ziel. | 12 |
| **Gebet der Heilung** | Gruppenheilung | lang | keine | sehr hoch | Heilt alle Mitglieder **der eigenen 5er-Gruppe** (im Raid: die Raidgruppe, in der das Ziel steht). | 14, 24, 34, 44, 54 |
| **Verblassen** | Bedrohung senken | spontan | mittel | gering | Senkt die eigene Bedrohung bei allen Gegnern für kurze Zeit stark. Kein GCD. | 16 |

### 1.3 Übersicht: Allgemeines Angebot pro geradem Level

| Level | Neu / Rang |
|---|---|
| 1 | Geringe Heilung R1, Heilige Pein R1 |
| 2 | Erneuerung R1 |
| 4 | Geringe Heilung R2, Schattenwort: Schmerz R1 |
| 6 | Heilige Pein R2, Blitzheilung R1 |
| 8 | Geringe Heilung R3, Erneuerung R2 |
| 10 | Schattenwort: Schmerz R2, **Auferstehung R1** + erste Zauber der Spezialisierung |
| 12 | Heilige Pein R3, Blitzheilung R2, **Reinigung** |
| 14 | Geringe Heilung R4, Erneuerung R3, **Gebet der Heilung R1** |
| 16 | Schattenwort: Schmerz R3, **Verblassen** |
| 18 | Heilige Pein R4, Blitzheilung R3 |
| 20 | Geringe Heilung R5, Erneuerung R4 |
| 22 | Schattenwort: Schmerz R4 |
| 24 | Heilige Pein R5, Blitzheilung R4, Gebet der Heilung R2 |
| 26 | Geringe Heilung R6, Erneuerung R5 |
| 28 | Schattenwort: Schmerz R5 |
| 30 | Heilige Pein R6, Blitzheilung R5, Auferstehung R2 |
| 32 | Geringe Heilung R7, Erneuerung R6 |
| 34 | Schattenwort: Schmerz R6, Gebet der Heilung R3 |
| 36 | Heilige Pein R7, Blitzheilung R6 |
| 38 | Geringe Heilung R8, Erneuerung R7 |
| 40 | Schattenwort: Schmerz R7 |
| 42 | Heilige Pein R8, Blitzheilung R7 |
| 44 | Geringe Heilung R9, Erneuerung R8, Gebet der Heilung R4 |
| 46 | Schattenwort: Schmerz R8 |
| 48 | Heilige Pein R9, Blitzheilung R8 |
| 50 | Geringe Heilung R10, Erneuerung R9, Auferstehung R3 |
| 52 | Schattenwort: Schmerz R9 |
| 54 | Heilige Pein R10, Blitzheilung R9, Gebet der Heilung R5 |
| 56 | Geringe Heilung R11, Erneuerung R10 |
| 58 | Schattenwort: Schmerz R10 |
| 60 | Heilige Pein R11, Blitzheilung R10 |

---

## 2. Heilig (volle Heilung)

**Fantasie:** Der reine Lichtheiler. Stärkste Einzel- und Gruppenheilung, das volle Schild, Rettung in letzter Sekunde. Wenig eigener Schaden (nur die 2 Startangriffe).

| Zauber | Art | Castzeit | CD | Mana | Wirkung | Ränge bei Level |
|---|---|---|---|---|---|---|
| **Machtwort: Schild** ★ | Schild | spontan | keine (siehe Debuff) | mittel | Legt ein **starkes Schild** auf ein Ziel, das Schaden absorbiert. Das Ziel erhält danach für mittlere Zeit **„Geschwächte Seele“** und kann in dieser Zeit nicht erneut geschildet werden. Ikonisch: **nur Heilig hat das volle Schild.** | 10, 16, 22, 28, 34, 40, 46, 52, 58 |
| **Große Heilung** | Einzelheilung | lang | keine | hoch | Sehr große Heilung, langsam. Die klassische „große langsame Heilung“. | 12, 20, 28, 36, 44, 52, 60 |
| **Gebet der Besserung** | Springende Heilung | spontan | kurz | mittel | Legt einen Segen auf ein Ziel. Nimmt das Ziel Schaden, wird es geheilt und der Segen springt auf ein anderes verletztes Mitglied (mehrere Sprünge). | 18, 30, 42, 54 |
| **Heiliges Wort: Heil** | Notfallheilung | spontan | lang | hoch | Sofortige sehr große Heilung auf ein Ziel. Die „Notfallheilung“. Kein GCD. | 24, 36, 48, 60 |
| **Bindende Heilung** | Doppelheilung | mittel | keine | hoch | Heilt das Ziel **und** den Priester selbst. | 30, 38, 46, 54 |
| **Kreis der Heilung** ★ | Gruppenheilung | spontan | kurz | hoch | Heilt sofort mehrere verletzte Mitglieder (im Raid gruppenübergreifend die am meisten verletzten). | 36, 44, 52, 60 |
| **Göttliche Hymne** ★ | Kanalisierte Massenheilung | kanalisiert | sehr lang | sehr hoch | Heilt über mehrere Sekunden die **ganze Gruppe bzw. den ganzen Raid** sehr stark und erhöht kurz die erhaltene Heilung. | 40, 50, 60 |
| **Schutzgeist** ★ | Rettungszauber | spontan | sehr lang | mittel | Erhöht die Heilung auf ein Ziel für kurze Zeit. **Würde das Ziel sterben, wird es stattdessen stark geheilt** und der Effekt endet. Kein GCD. | 50 |

★ = ikonisch, **für Schatten und Disziplin gesperrt**.

Angebot Heilig pro Level (zusätzlich zu Kapitel 1.3): 10 Schild R1 · 12 Große Heilung R1 · 16 Schild R2 · 18 Gebet der Besserung R1 · 20 Große Heilung R2 · 22 Schild R3 · 24 Heiliges Wort: Heil R1 · 28 Schild R4, Große Heilung R3 · 30 Gebet der Besserung R2, Bindende Heilung R1 · 34 Schild R5 · 36 Große Heilung R4, Heiliges Wort: Heil R2, Kreis der Heilung R1 · 38 Bindende Heilung R2 · 40 Schild R6, Göttliche Hymne R1 · 42 Gebet der Besserung R3 · 44 Große Heilung R5, Kreis R2 · 46 Schild R7, Bindende Heilung R3 · 48 Heiliges Wort: Heil R3 · 50 Göttliche Hymne R2, **Schutzgeist** · 52 Schild R8, Große Heilung R6, Kreis R3 · 54 Gebet der Besserung R4, Bindende Heilung R4 · 58 Schild R9 · 60 Große Heilung R7, Heiliges Wort: Heil R4, Kreis R4, Göttliche Hymne R3.

---

## 3. Schatten (voller Schaden)

**Fantasie:** Der Schattenpriester, der mit dunkler Magie großen Schaden macht. Heilt **schwächer**: Die normalen Heilzauber bleiben, sind aber in Schattengestalt abgeschwächt; Heilung kommt zusätzlich über **Vampirumarmung** (Schaden heilt die Gruppe ein wenig) und Selbstheilung.

| Zauber | Art | Castzeit | CD | Mana | Wirkung | Ränge bei Level |
|---|---|---|---|---|---|---|
| **Gedankenschlag** ★ | Angriff | mittel | kurz | mittel | Hoher Schatten-Schaden auf einen Gegner. | 10, 16, 22, 28, 34, 40, 46, 52, 58 |
| **Vampirumarmung** | Passiv | – | – | – | Ein Anteil des Schatten-Schadens des Priesters heilt die ganze Gruppe. Höhere Ränge: größerer Anteil. | 12, 30, 48 |
| **Gedankenschinden** | Angriff | kanalisiert | keine | mittel | Schatten-Schaden über mehrere Sekunden, solange kanalisiert wird. | 14, 20, 26, 32, 38, 44, 50, 56 |
| **Schattengestalt** ★ | Haltung | spontan | kurz (Umschalten) | – | Priester wechselt in Schattengestalt: **deutlich mehr Schatten-Schaden** und weniger erlittener Schaden, **Heilig-Zauber und Heilungen deutlich schwächer**. Kann jederzeit an- und ausgeschaltet werden (dann wieder normale Heilung, aber kein Schadensbonus). | 20 |
| **Vampirberührung** ★ | Angriff (DoT) | mittel | keine | mittel | Schatten-DoT; solange er tickt, gibt jeder Schaden des Priesters an diesem Ziel **Mana zurück**. | 26, 34, 42, 50, 58 |
| **Verschlingende Seuche** | Angriff (DoT) | spontan | mittel | hoch | Schatten-DoT, dessen Schaden den **Priester heilt**. | 32, 40, 48, 56 |
| **Dispersion** ★ | Verteidigung | spontan | sehr lang | – | Priester wird zu Schatten: nimmt für kurze Zeit **stark reduzierten Schaden** und **regeneriert viel Mana**, kann in der Zeit nicht zaubern. | 38 |
| **Schattenwort: Tod** | Angriff (Hinrichtung) | spontan | kurz | mittel | Sehr hoher Schaden auf Gegner mit **niedrigen HP** (unter einer Schwelle); sonst geringer Schaden. | 44, 52, 60 |
| **Leerenausbruch** ★ | Burst | mittel | sehr lang | hoch | Öffnet die Leere: Für eine mittlere Dauer macht der Priester **sehr viel mehr Schatten-Schaden** und Gedankenschlag hat keine Abklingzeit. | 50 |

★ = ikonisch, **für Heilig und Disziplin gesperrt**.

Angebot Schatten pro Level: 10 Gedankenschlag R1 · 12 Vampirumarmung R1 · 14 Gedankenschinden R1 · 16 Gedankenschlag R2 · 20 Gedankenschinden R2, **Schattengestalt** · 22 Gedankenschlag R3 · 26 Gedankenschinden R3, Vampirberührung R1 · 28 Gedankenschlag R4 · 30 Vampirumarmung R2 · 32 Gedankenschinden R4, Verschlingende Seuche R1 · 34 Gedankenschlag R5, Vampirberührung R2 · 38 Gedankenschinden R5, **Dispersion** · 40 Gedankenschlag R6, Verschlingende Seuche R2 · 42 Vampirberührung R3 · 44 Gedankenschinden R6, Schattenwort: Tod R1 · 46 Gedankenschlag R7 · 48 Vampirumarmung R3, Verschlingende Seuche R3 · 50 Gedankenschinden R7, Vampirberührung R4, **Leerenausbruch** · 52 Gedankenschlag R8, Schattenwort: Tod R2 · 56 Gedankenschinden R8, Verschlingende Seuche R4 · 58 Gedankenschlag R9, Vampirberührung R5 · 60 Schattenwort: Tod R3.

---

## 4. Disziplin (Kombination)

**Fantasie:** Der Priester zwischen Licht und Schatten. **Heilung und Schaden beide mittel.** Die besten Zauber von Heilig (★) und Schatten (★) sind gesperrt. Dafür eigene ikonische Zauber: **Sühne** (eigener Schaden heilt Verbündete), **Bußgebet**, **Schmerzunterdrückung**, **Machtwort: Barriere**.
Reine Angriffszauber bleiben **Heilige Pein und Schattenwort: Schmerz** (die 2 Startangriffe). **Bußgebet** ist ein Hybridzauber (Gegner = Schaden, Verbündeter = Heilung).

| Zauber | Art | Castzeit | CD | Mana | Wirkung | Ränge bei Level |
|---|---|---|---|---|---|---|
| **Bußgebet** ◆ | Hybrid | kanalisiert (kurz) | kurz | mittel | Auf einen **Gegner**: mehrere Lichtblitze mit Schaden. Auf einen **Verbündeten**: mehrere Heilstöße. | 10, 18, 26, 34, 42, 50, 58 |
| **Sühne** ◆ | Passiv | – | – | – | Jeder Schaden des Priesters **heilt das am stärksten verletzte Gruppenmitglied** um einen Anteil. | 12 |
| **Heilung** | Einzelheilung | mittel–lang | keine | mittel | Mittlere Heilung (zwischen Geringer und Großer Heilung). | 16, 22, 28, 34, 40, 46, 52, 58 |
| **Schmerzunterdrückung** ◆ | Schadensreduktion | spontan | lang | gering | Das Ziel erleidet für kurze Zeit **stark reduzierten Schaden**. Kein GCD. Perfekt gegen Tank-Buster. | 20 |
| **Schutzwort: Licht** | Schild | spontan | keine (siehe Debuff) | mittel | **Schwächeres Schild** als Machtwort: Schild. Gleicher Debuff „Geschwächte Seele“. | 24, 30, 36, 42, 48, 54, 60 |
| **Machtwort: Strahlkraft** | Gruppenheilung | kurz | mittel | hoch | Heilt mehrere Mitglieder mäßig und verstärkt für kurze Zeit die Sühne-Heilung auf ihnen. | 32, 40, 48, 56 |
| **Machtwort: Barriere** ◆ | Gruppen-Schadensreduktion | spontan | sehr lang | hoch | Alle Mitglieder der Gruppe (im Raid: der ganze Raid) erleiden für eine mittlere Dauer weniger Schaden. | 38 |
| **Evangelium** ◆ | Verstärkung | spontan | lang | – | Für kurze Zeit ist die Sühne-Heilung stark erhöht und heilt zusätzlich ein zweites verletztes Ziel. Kein GCD. | 44 |
| **Erleuchtung** | Mana | spontan | sehr lang | – | Für kurze Zeit kosten alle Zauber **kein Mana**. Kein GCD. | 50 |

◆ = ikonisch für Disziplin, **für Heilig und Schatten gesperrt**.

Angebot Disziplin pro Level: 10 Bußgebet R1 · 12 Sühne · 16 Heilung R1 · 18 Bußgebet R2 · 20 **Schmerzunterdrückung** · 22 Heilung R2 · 24 Schutzwort: Licht R1 · 26 Bußgebet R3 · 28 Heilung R3 · 30 Schutzwort: Licht R2 · 32 Machtwort: Strahlkraft R1 · 34 Bußgebet R4, Heilung R4 · 36 Schutzwort: Licht R3 · 38 **Machtwort: Barriere** · 40 Heilung R5, Strahlkraft R2 · 42 Bußgebet R5, Schutzwort: Licht R4 · 44 **Evangelium** · 46 Heilung R6 · 48 Schutzwort: Licht R5, Strahlkraft R3 · 50 Bußgebet R6, **Erleuchtung** · 52 Heilung R7 · 54 Schutzwort: Licht R6 · 56 Strahlkraft R4 · 58 Bußgebet R7, Heilung R8 · 60 Schutzwort: Licht R7.

---

## 5. Talentbäume

Aufbau (siehe Hauptdokument Kapitel 12):
- 9 Reihen × 3 Talente. Reihe *n* öffnet sich bei **5 × (n − 1)** verteilten Punkten.
- Reihen **3, 6 und 9** sind **Wahl-Reihen**: nur **eines** der 3 Talente wählbar (1 Punkt).
- Normale Talente: 1–5 Ränge. Wirkung pro Rang relativ: **klein**, **mittel**, **groß**.
- „→“ = setzt das genannte Talent voraus (voll ausgebaut).
- Summe aller wählbaren Ränge pro Baum: **Heilig 64, Schatten 62, Disziplin 64** (Wahl-Reihen zählen je 1). Verfügbar: **51** Punkte. Man kann also nicht alles lernen.

### 5.1 Talentbaum Heilig

| Reihe | Talent | Ränge | Wirkung |
|---|---|---|---|
| 1 | Göttliche Weisheit | 5 | Pro Rang: + klein % Heilstärke |
| 1 | Klarer Geist | 5 | Pro Rang: + klein % Mana-Reg |
| 1 | Schnelle Gebete | 3 | Pro Rang: Castzeit von Geringe Heilung und Große Heilung etwas kürzer |
| 2 | Verbesserte Erneuerung | 3 | Pro Rang: Erneuerung heilt mehr |
| 2 | Verbessertes Machtwort: Schild | 3 | Pro Rang: Schild absorbiert mehr |
| 2 | Heilige Konzentration | 5 | Pro Rang: kleine Chance, dass der nächste Heilzauber nach einem kritischen Treffer kein Mana kostet |
| **3 (Wahl)** | **Lichtbrunnen** | 1 | Neuer Zauber (CD mittel): Legt einen Segen auf die ganze Gruppe; die nächsten mehreren Male, wenn ein Mitglied unter die Hälfte seiner HP fällt, wird es automatisch geheilt |
| **3 (Wahl)** | **Heilige Wacht** | 1 | Erneuerung auf einem Tank heilt deutlich stärker und hält länger |
| **3 (Wahl)** | **Aufgestiegenes Licht** | 1 | Blitzheilung und Große Heilung setzen zusätzlich eine kurze Erneuerung auf das Ziel |
| 4 | Heilige Reichweite | 3 | Pro Rang: Gebet der Heilung heilt mehr |
| 4 | Gesegnete Genesung | 3 | Pro Rang: Wird der Priester kritisch getroffen, heilt er sich über Zeit |
| 4 | Göttliche Fügung | 5 | Pro Rang: + klein % Krit für Heilzauber |
| 5 | Verbessertes Heiliges Wort | 3 | Pro Rang: Abklingzeit von Heiliges Wort: Heil kürzer |
| 5 | Segensreiche Besserung | 3 | Pro Rang: Gebet der Besserung heilt mehr; auf Rang 3 springt es einmal öfter |
| 5 | Innerer Fokus | 1 | Neuer Zauber (CD lang): Der nächste Zauber kostet kein Mana und hat erhöhte Krit-Chance |
| **6 (Wahl)** | **Seelenschutz** | 1 | Machtwort: Schild hinterlässt beim Zerbrechen eine kleine Heilung auf dem Ziel |
| **6 (Wahl)** | **Kreis des Lebens** | 1 | Kreis der Heilung heilt ein zusätzliches Ziel und hat kürzere Abklingzeit |
| **6 (Wahl)** | **Heilende Hand** | 1 | Große Heilung hat eine Chance, die nächste Große Heilung spontan zu machen |
| 7 | Anhaltende Gnade | 5 | Pro Rang: Nach jeder Heilung erhält das Ziel kurz + klein % Rüstung |
| 7 | Tiefe Andacht | 3 | Pro Rang: + klein % Mana |
| 7 | Verbesserte Hymne | 2 | Pro Rang: Göttliche Hymne heilt mehr, Abklingzeit kürzer → setzt „Heilige Reichweite“ voraus |
| 8 | Engelsgleiche Präsenz | 3 | Pro Rang: + mittel % Heilstärke auf Ziele unter der Hälfte ihrer HP |
| 8 | Gesegnete Resilienz | 3 | Pro Rang: Der Priester erleidet weniger Schaden |
| 8 | Unerschütterlicher Glaube | 3 | Pro Rang: Schutzgeist hat kürzere Abklingzeit → setzt „Verbessertes Heiliges Wort“ voraus |
| **9 (Wahl)** | **Apotheose** | 1 | Neuer Zauber (CD sehr lang): Für kurze Zeit werden alle Heiligen Wörter und Kreis der Heilung ohne Abklingzeit gewirkt |
| **9 (Wahl)** | **Heiliger Wächter** | 1 | Machtwort: Schild ignoriert „Geschwächte Seele“ einmal pro mittlerer Zeit |
| **9 (Wahl)** | **Lichtflut** | 1 | Jede kritische Heilung heilt zusätzlich die zwei am stärksten verletzten Mitglieder um einen Anteil |

### 5.2 Talentbaum Schatten

| Reihe | Talent | Ränge | Wirkung |
|---|---|---|---|
| 1 | Dunkle Gedanken | 5 | Pro Rang: + klein % Schaden |
| 1 | Schattenfokus | 5 | Pro Rang: Schatten-Zauber kosten weniger Mana |
| 1 | Verbesserter Schmerz | 3 | Pro Rang: Schattenwort: Schmerz macht mehr Schaden |
| 2 | Verbesserter Gedankenschlag | 3 | Pro Rang: Abklingzeit von Gedankenschlag kürzer |
| 2 | Schattenreichweite | 3 | Pro Rang: Vampirumarmung heilt mehr |
| 2 | Qualvolle Gedanken | 5 | Pro Rang: + klein % Krit für Schatten-Zauber |
| **3 (Wahl)** | **Schattenhafte Erscheinung** | 1 | Kritische Treffer von Schattenwort: Schmerz beschwören kurz eine Schattenerscheinung, die dem Ziel einmalig Schaden zufügt |
| **3 (Wahl)** | **Dunkle Heilung** | 1 | Heilzauber sind in Schattengestalt weniger abgeschwächt |
| **3 (Wahl)** | **Seelenraub** | 1 | Stirbt ein Gegner mit Schattenwort: Schmerz, erhält der Priester Mana zurück |
| 4 | Gedankenflut | 3 | Pro Rang: Gedankenschinden macht mehr Schaden |
| 4 | Schattenschutz | 3 | Pro Rang: + klein % Resistenz |
| 4 | Verbesserte Vampirberührung | 3 | Pro Rang: Vampirberührung gibt mehr Mana zurück |
| 5 | Schattenbindung | 3 | Pro Rang: DoTs dauern länger |
| 5 | Verstärkte Schattengestalt | 3 | Pro Rang: Schattengestalt gibt mehr Schaden → setzt „Gedankenflut“ voraus |
| 5 | Schattenschleier | 1 | Verblassen senkt die Bedrohung länger und hat kürzere Abklingzeit |
| **6 (Wahl)** | **Psychischer Horror** | 1 | Gedankenschlag hat eine Chance, eine kurze Schwächung auf den Gegner zu legen (weniger Schaden verursacht) |
| **6 (Wahl)** | **Schattenwahnsinn** | 1 | Schattenwort: Tod setzt bei Gegnern unter der Schwelle zusätzlich Gedankenschlag zurück |
| **6 (Wahl)** | **Leerenseuche** | 1 | Verschlingende Seuche springt beim Tod des Ziels auf einen anderen Gegner über |
| 7 | Dunkle Macht | 5 | Pro Rang: + klein % Schaden aller DoTs |
| 7 | Mentale Stärke | 3 | Pro Rang: + klein % Mana |
| 7 | Verbesserte Dispersion | 2 | Pro Rang: Dispersion hat kürzere Abklingzeit → setzt „Schattenschutz“ voraus |
| 8 | Schattenmacht | 3 | Pro Rang: + mittel % Krit-Schaden von Schatten-Zaubern |
| 8 | Unersättlicher Hunger | 3 | Pro Rang: Verschlingende Seuche heilt mehr |
| 8 | Verlängerte Leere | 3 | Pro Rang: Leerenausbruch dauert länger → setzt „Verstärkte Schattengestalt“ voraus |
| **9 (Wahl)** | **Leerengestalt** | 1 | Während Leerenausbruch heilt Vampirumarmung stark erhöht |
| **9 (Wahl)** | **Gedankenbrecher** | 1 | Neuer Zauber (CD kurz, spontan): Großer Schatten-Schaden, wird bei jedem Gedankenschlag-Krit zurückgesetzt |
| **9 (Wahl)** | **Schattenfürst** | 1 | Alle DoTs des Priesters können kritisch treffen und jeder Krit gibt etwas Mana zurück |

### 5.3 Talentbaum Disziplin

| Reihe | Talent | Ränge | Wirkung |
|---|---|---|---|
| 1 | Geistige Balance | 5 | Pro Rang: + klein % Heilstärke **und** + klein % Schaden (jeweils halb so viel wie die reinen Bäume) |
| 1 | Meditation | 5 | Pro Rang: + klein % Mana-Reg |
| 1 | Zwielicht | 3 | Pro Rang: Heilige Pein macht mehr Schaden |
| 2 | Verbessertes Bußgebet | 3 | Pro Rang: Bußgebet feuert einen Blitz mehr (Rang 3: +1 insgesamt, dazwischen mehr Stärke) |
| 2 | Verbessertes Schutzwort | 3 | Pro Rang: Schutzwort: Licht absorbiert mehr |
| 2 | Geistige Stärke | 5 | Pro Rang: + klein % Krit |
| **3 (Wahl)** | **Tiefere Sühne** | 1 | Sühne heilt einen größeren Anteil |
| **3 (Wahl)** | **Schattenlicht** | 1 | Schattenwort: Schmerz löst bei jedem Tick auch Sühne aus |
| **3 (Wahl)** | **Göttliches Aegis** | 1 | Kritische Heilungen hinterlassen ein kleines Schild |
| 4 | Verbesserte Schmerzunterdrückung | 3 | Pro Rang: Abklingzeit von Schmerzunterdrückung kürzer |
| 4 | Gnade | 3 | Pro Rang: Heilungen erhöhen kurz die erhaltene Heilung auf dem Ziel |
| 4 | Fokussierter Wille | 5 | Pro Rang: + klein % Tempo |
| 5 | Verbesserte Strahlkraft | 3 | Pro Rang: Machtwort: Strahlkraft heilt ein Ziel mehr |
| 5 | Ruhiger Geist | 3 | Pro Rang: Der Priester erleidet weniger Schaden → setzt „Gnade“ voraus |
| 5 | Innere Ruhe | 1 | Neuer Zauber (CD lang): Stellt sofort einen Teil des Manas wieder her |
| **6 (Wahl)** | **Rettende Hand** | 1 | Schmerzunterdrückung heilt das Ziel beim Wirken zusätzlich |
| **6 (Wahl)** | **Leuchtende Barriere** | 1 | Machtwort: Barriere reduziert mehr Schaden, aber kürzer |
| **6 (Wahl)** | **Zorn des Lichts** | 1 | Bußgebet auf einen Gegner löst Sühne auf zwei Zielen aus |
| 7 | Verlängerte Sühne | 5 | Pro Rang: + klein % Sühne-Heilung |
| 7 | Tiefe Reserven | 3 | Pro Rang: + klein % Mana |
| 7 | Verbessertes Evangelium | 2 | Pro Rang: Evangelium dauert länger → setzt „Verbesserte Schmerzunterdrückung“ voraus |
| 8 | Engelsschwingen | 3 | Pro Rang: Schutzwort: Licht erhöht auf dem Ziel kurz Tempo |
| 8 | Harmonie | 3 | Pro Rang: + mittel % Heilstärke **und** Schaden, wenn Sühne gerade aktiv geheilt hat |
| 8 | Erleuchteter Geist | 3 | Pro Rang: Erleuchtung dauert länger → setzt „Innere Ruhe“ voraus |
| **9 (Wahl)** | **Strahlende Buße** | 1 | Bußgebet hat keine Abklingzeit während Evangelium |
| **9 (Wahl)** | **Märtyrer des Lichts** | 1 | Schmerzunterdrückung wirkt auch auf den Priester selbst |
| **9 (Wahl)** | **Gleichgewicht** | 1 | Jeder Heilzauber verstärkt den nächsten Schadenszauber und jeder Schadenszauber verstärkt den nächsten Heilzauber |

> **Hinweis:** Neue Zauber aus Talenten (Lichtbrunnen, Innerer Fokus, Apotheose, Gedankenbrecher, Innere Ruhe) erscheinen nach dem Lernen automatisch im Zauberbuch und kosten beim Lehrmeister nichts. **[Festlegung]**
