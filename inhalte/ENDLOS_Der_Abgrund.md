# Unendliche Wellen – Der Abgrund

## Überblick

- **Freischaltung:** Welt 10 (Drachenhort) **und** Raid 3 (Drachenfeste Ascheschwinge) abgeschlossen; Spielerlevel 60.
- **Gegnerlevel:** immer 60 (die Stärke steigt über die Skalierungsregeln, nicht über das Level).
- **Wellen:** 1, 2, 3, … ohne Ende. **Boss alle 10 Wellen** (Welle 10, 20, 30 …).
- **Gruppengröße:** normale 5er-Gruppe (Spieler + 4 Mitglieder), keine Raidfüller.
- **Maximal gleichzeitige Gegner:** 6 (Adds mitgezählt).
- **Niederlage:** eine Welle zurück (wie überall). Der Rekord (höchste erreichte Welle) bleibt erhalten und wird oben angezeigt („Abgrund – Welle X“, „Rekord: Welle Y“).
- **Thema:** Unter dem erloschenen Krater der Ascheschwinge klafft ein Riss in eine endlose Leere zwischen den Welten. Dort treiben Bruchstücke fremder Orte, und verzerrte Kreaturen aus dem Nichts – Leerwesen ohne feste Gestalt – drängen unaufhörlich nach oben. Die Gruppe steigt immer tiefer hinab, ohne je einen Boden zu erreichen.
- **Hintergründe (Pixel-Art):** Der Hintergrund wechselt alle 10 Wellen (nach jedem Boss) und läuft in einer festen Reihenfolge durch; nach dem sechsten beginnt er von vorn, jedes Mal etwas dunkler und mit mehr violetten Rissen.
  1. **Wellen 1–10 – „Der Riss“:** Zerbrochener Kraterboden, darunter schwarzes Nichts mit violetten Rissen und treibenden Basaltbrocken.
  2. **Wellen 11–20 – „Treibende Trümmer“:** Schwebende Bruchstücke fremder Welten (ein Stück Wald, eine Mauer, eine Wüstendüne) auf tiefblauem Grund.
  3. **Wellen 21–30 – „Das Sternengrab“:** Erlöschende Sterne, die langsam in die Tiefe fallen; kaltes Weiß auf Schwarz.
  4. **Wellen 31–40 – „Der Spiegelschlund“:** Glatte, spiegelnde Flächen, die die Gruppe verzerrt zurückwerfen.
  5. **Wellen 41–50 – „Das Fleischgewölbe“:** Pulsierende, violett-rote Wände aus lebender Leere mit geschlossenen Augen, die sich gelegentlich öffnen.
  6. **Wellen 51–60 – „Das Herz des Nichts“:** Fast völlige Schwärze; nur ein riesiges, langsam schlagendes violettes Licht in der Ferne.
- **Musik:** Schwebende, dissonante Synthesizer-Flächen mit tiefem Brummen und leisen, rückwärts abgespielten Chorstimmen. Mit jeder Hintergrund-Runde wird die Musik eine Spur dichter; Bosswellen haben ein pulsierendes, verzerrtes Kampfthema mit dumpfen Schlägen.

## Skalierungsregeln

Alle Angaben relativ; konkrete Werte beim Balancing.

**Grundsteigerung (jede Welle, ohne Obergrenze):**
- **HP** der Gegner steigen mit jeder Welle ein Stück.
- **Schaden** der Gegner steigt mit jeder Welle ein Stück (etwas langsamer als die HP, damit Wellen länger, aber nicht sofort tödlich werden).
- **Anzahl** der Gegner steigt in den ersten Wellen schnell bis zum Maximum von 6; danach wächst die Schwierigkeit nur noch über HP, Schaden, Elite-Anteil und Mechaniken.
- **Elite-Anteil** steigt mit der Wellennummer: anfangs einzelne Elite-Gegner, später die Mehrheit, schließlich nur noch Elite.
- **Bosse** werden bei jeder Wiederholung stärker (HP, Schaden), ihr Enrage-Timer wird kürzer und sie bekommen Zusatzmechaniken (siehe Bosspool).
- Innerhalb eines 10er-Blocks steigt die Schwierigkeit gleichmäßig; die erste Welle nach einem Boss ist spürbar leichter als der Boss selbst, aber schwerer als die Welle vor dem Boss.

**Neue Mechaniken nach Wellennummer (bleiben dauerhaft aktiv):**

| Ab Welle | Neue Regel |
|---|---|
| 1 | Nur Normal-Gegner, normale Angriffe, leichte AoE und einzelne nicht bannbare DoTs. |
| 5 | Erste Elite-Gegner (einzeln). |
| 11 | Mindestens ein Elite-Gegner in jeder Welle. |
| 20 | **Alle Elite-Gegner** tragen zusätzlich einen bannbaren Debuff (Magie oder Krankheit). |
| 25 | Normal-Gegner-Zauberer wirken ihre Debuffs auf 2 Ziele statt auf 1. |
| 30 | **Enrage auch bei Elite-Gegnern** (nach relativ langer Zeit, Anzeige am Gegner). |
| 40 | Tank-Buster aller Elite-Gegner haben einen kürzeren Castbalken. |
| 50 | Mindestens die Hälfte der Gegner jeder Welle ist Elite. |
| 60 | Elite-Gegner wirken zusätzlich einen leichten AoE auf alle (mit Castbalken). |
| 70 | Beginn des zweiten Boss-Durchlaufs; alle Bosse haben ihre erste Zusatzmechanik. |
| 80 | Jeder Elite-Gegner trägt **beide** bannbaren Debuff-Typen (Magie und Krankheit). |
| 90 | Enrage-Timer aller Elite-Gegner wird kürzer. |
| 100 | In Nicht-Boss-Wellen stehen **nur noch Elite-Gegner**. |
| 100+ | Keine neuen Regeln mehr; alle 10 Wellen steigen HP und Schaden zusätzlich um einen kleinen Sprung, und die Enrage-Timer werden weiter verkürzt (mit einer Untergrenze, sodass der Kampf immer machbar bleibt). |

**Belohnungs-Skalierung:**
- **Gold** und **Drop-Chance** steigen mit der Wellennummer.
- **Raritätschancen** steigen mit der Wellennummer ohne Obergrenze: in frühen Wellen überwiegend Ungewöhnlich bis Episch, ab etwa Welle 30 regelmäßig Legendär, ab etwa Welle 60 Mythisch nicht mehr selten, **Mythisch+** wird mit jeder Welle etwas wahrscheinlicher.
- **Items:** Alle Items haben **Mindestlevel 60**. Ihre Grundwerte bleiben auf **Level-60-Niveau** und steigen nie darüber – nur die Rarität (und damit Raritätsmultiplikator und Enchantments) wird besser.

## Questnamen-Schema

Da der Abgrund unendlich ist, werden Questnamen und Questtexte automatisch aus Bausteinen erzeugt. Bosswellen verwenden stattdessen den festen Bossnamen (siehe Bosspool).

**Aufbau des Questnamens:** `„[Teil A] [Teil B]“` – zufällig kombiniert. Innerhalb eines 10er-Blocks darf sich kein Teil A und kein Teil B wiederholen.

**Teil A (15 Bausteine):**
1. Das Flüstern
2. Der Riss
3. Die Tiefe
4. Das Echo
5. Der Hunger
6. Die Stille
7. Der Sturz
8. Das Auge
9. Die Kälte
10. Der Schlund
11. Das Zerfasern
12. Die Wacht
13. Der Nebel
14. Das Erwachen
15. Die Spur

**Teil B (15 Bausteine):**
1. der ewigen Leere
2. des Abgrunds
3. zwischen den Welten
4. im Nichts
5. der vergessenen Sterne
6. ohne Boden
7. der verzerrten Brut
8. am Rand der Zeit
9. der zerbrochenen Spiegel
10. der stummen Tiefe
11. hinter dem Schleier
12. der hungrigen Dunkelheit
13. der fallenden Trümmer
14. des schlagenden Herzens
15. der namenlosen Wesen

Beispiele: „Das Echo der vergessenen Sterne“, „Der Schlund ohne Boden“, „Die Stille hinter dem Schleier“.

**Questtext-Vorlagen (20, zufällig gewählt):** Platzhalter: `{Welle}` = Wellennummer, `{Gegner}` = Name des stärksten Gegnertyps der Welle.
1. Auf Tiefe {Welle} regt sich etwas Neues. Vernichtet es, bevor es nach oben kriecht.
2. {Gegner} versperrt den Weg in die Tiefe. Räumt ihn beiseite.
3. Die Leere wird hier dichter. Haltet zusammen und kämpft euch hindurch.
4. Etwas beobachtet euch aus der Dunkelheit. Zeigt ihm, dass ihr nicht zu fürchten seid – sondern es zu fürchten hat.
5. Die Trümmer einer fremden Welt treiben vorbei – und mit ihnen ihre verzerrten Bewohner.
6. Tiefer als Tiefe {Welle} ist noch niemand gestiegen, der zurückkam. Ändert das.
7. Ein Flüstern ruft eure Namen. Folgt ihm nicht – bekämpft, was es ausspricht.
8. {Gegner} nährt sich von der Hoffnung der Gefallenen. Nehmt ihm seine Beute.
9. Der Abgrund antwortet auf jeden Sieg mit etwas Schlimmerem. Seid bereit.
10. Hier zerfließt die Zeit. Schlagt zu, bevor sie euch mitreißt.
11. Die Wesen dieser Tiefe haben nie Licht gesehen. Zeigt es ihnen.
12. Ein Riss öffnet sich und spuckt neue Gegner aus. Schließt ihn mit Gewalt.
13. {Gegner} führt eine Schar aus dem Nichts an. Brecht ihre Reihen.
14. Die Kälte der Leere kriecht in eure Knochen. Kämpft, solange ihr noch warm seid.
15. Auf Tiefe {Welle} hallen Kampfgeräusche längst vergangener Helden. Setzt ihren Weg fort.
16. Etwas Hungriges hat eure Spur aufgenommen. Stellt euch ihm.
17. Die Spiegel der Leere zeigen euch verzerrt. Zerschlagt, was aus ihnen tritt.
18. Keine Rast, kein Boden, kein Ende. Nur die nächste Welle.
19. {Gegner} wartet reglos im Dunkel – und doch spürt ihr seinen Blick.
20. Der Abgrund prüft euch erneut. Beweist, dass ihr tiefer gehen könnt.

**Abschlusstext-Vorlagen (10, zufällig gewählt):**
1. Die Leere weicht zurück – für den Augenblick.
2. Tiefe {Welle} ist bezwungen. Unter euch gähnt schon die nächste.
3. Die verzerrten Wesen zerfallen zu violettem Staub.
4. Das Flüstern verstummt kurz, dann beginnt es erneut.
5. Ihr steht noch. Der Abgrund nicht mehr ganz so fest.
6. Ein Riss schließt sich hinter euch.
7. Der Weg nach unten ist frei.
8. Selbst das Nichts scheint kurz den Atem anzuhalten.
9. Die Trümmer treiben still weiter – ohne ihre Bewohner.
10. Ein weiterer Schritt in die Tiefe ist getan.

## Gegnerpool

Die Gegner jeder Nicht-Boss-Welle werden zufällig aus diesem Pool gewählt (gemischt, passend zum aktuellen Elite-Anteil). Der Pool ist über alle Wellen gleich; die Stärke kommt aus der Skalierung.

| Name | Art | Kampfstil | Schadensart | Fähigkeiten (mit Mechanik-Typ) | Aussehen |
|---|---|---|---|---|---|
| Leerenkriecher | Normal | Nahkampf | Physisch | *Zersetzender Biss* (normaler Angriff); *Nichtsfäule* (DoT, nicht bannbar, schwach) | Schwarzer, vielbeiniger Wurm mit violett glühendem Maul |
| Abgrundflüsterer | Normal | Zauberer | Magisch | *Flüsterpfeil* (magischer Angriff); *Wispernde Pein* (Debuff Typ Magie, bannbar, DoT mittel) | Schwebende, verhüllte Gestalt ohne Gesicht, nur ein Mund aus Licht |
| Zerrspiegel | Normal | Zauberer | Magisch | *Gebrochenes Licht* (leichter AoE auf alle, kurzer Castbalken); *Spiegelsplitter* (normaler magischer Angriff) | Schwebende, gesplitterte Spiegelscherbe mit einem verzerrten Gesicht darin |
| Hohle Hülle | Normal | Nahkampf | Physisch | *Leerer Schlag* (normaler Angriff, mittel); *Seelenleere* (Debuff, senkt Heilung auf dem Ziel, nicht bannbar) | Menschenähnliche, durchsichtige Rüstung ohne Körper darin |
| Riftmotten-Schwarm | Normal | Zauberer | Magisch | *Staubschwarm* (leichter AoE auf alle); *Motten-Seuche* (Debuff Typ Krankheit, bannbar, schwach) | Wolke aus kleinen violetten Motten mit leuchtenden Flügeln |
| Nichtshund | Normal | Nahkampf | Physisch | *Reißen* (normaler Angriff); *Blutfaden* (DoT, nicht bannbar, mittel) | Hagerer Hund aus schwarzem Rauch mit drei weißen Augen |
| Sternfresser-Larve | Normal | Nahkampf | Magisch | *Lichtsaugen* (normaler Angriff, heilt sich dabei leicht); *Sternstaub-Seuche* (Debuff Typ Krankheit, bannbar) | Fette, blasse Larve mit einem funkelnden Stern im Bauch |
| Verzerrter Wanderer | Normal | Nahkampf | Physisch | *Falscher Hieb* (normaler Angriff, mittel); *Zeitriss* (Debuff Typ Magie, bannbar, verlangsamt Angriffe des Ziels) | Verzogene Menschengestalt mit zu langen Armen und Laterne |
| Abgrundwächter | Elite | Nahkampf | Physisch | *Nichtshammer* (Tank-Buster, stark, Castbalken); *Wächterhieb* (normaler Angriff, stark) | Riesiger Ritter aus schwarzem Obsidian mit violettem Schlitzvisier |
| Leerenpriester | Elite | Zauberer | Magisch | *Hymne des Nichts* (AoE auf alle, mittel, Castbalken); *Leerenfluch* (Debuff Typ Magie, bannbar, DoT stark); *Dunkle Gnade* (heilt einen Verbündeten) | Hagere Gestalt in zerrissener Robe mit einem Loch statt Gesicht |
| Seuchenfaden-Weberin | Elite | Zauberer | Magisch | *Fadenseuche* (Debuff Typ Krankheit, bannbar, auf 3 Ziele); *Netz der Leere* (magischer Angriff, mittel) | Spinnenartiges Wesen aus violetten Fäden mit Frauenkopf |
| Riss-Koloss | Elite | Nahkampf | Physisch und magisch | *Rissstampfer* (AoE auf alle, stark, Castbalken); *Zerschmettern* (Tank-Buster, Castbalken) | Gewaltiger Steinriese, durch dessen Brust ein violetter Riss läuft |
| Zeitloser Ritter | Elite | Nahkampf | Physisch | *Ewiger Schnitt* (normaler Angriff, stark); *Verfall* (stapelnder DoT auf dem Tank, nicht bannbar) | Verwitterter Ritter, dessen Körper abwechselnd jung und uralt flackert |
| Augenschwarm-Tyrann | Elite | Zauberer | Magisch | *Blick der Leere* (magischer Angriff auf zufälliges Ziel, stark); *Starren* (Debuff Typ Magie, bannbar, auf 2 Ziele, DoT mittel); *Tausend Blicke* (AoE auf alle, Castbalken) | Schwebende Kugel aus Fleisch, übersät mit blinzelnden Augen |

## Bosspool

Die 6 Bosse wechseln sich alle 10 Wellen in fester Reihenfolge ab. Nach Boss 6 beginnt die Reihenfolge von vorn (**Durchlauf**), und jeder Boss kommt stärker (HP, Schaden, kürzerer Enrage) und mit zusätzlichen Mechaniken zurück.

| Boss | Wellen |
|---|---|
| Boss 1 – Oruun, das Auge im Nichts | 10, 70, 130, 190 … |
| Boss 2 – Mahlkiefer, der Weltenschlinger | 20, 80, 140, 200 … |
| Boss 3 – Königin Ysmera der zerrissenen Stunde | 30, 90, 150, 210 … |
| Boss 4 – Der Stumme Chor | 40, 100, 160, 220 … |
| Boss 5 – Vael-Thorun, der Spiegelfürst | 50, 110, 170, 230 … |
| Boss 6 – Nhal'Zeroth, Herz des Abgrunds | 60, 120, 180, 240 … |

**Allgemeine Regel für Durchläufe:**
- **Durchlauf 1** (Wellen 10–60): Grundform.
- **Durchlauf 2** (Wellen 70–120): stärker + erste Zusatzmechanik.
- **Durchlauf 3** (Wellen 130–180): stärker + zweite Zusatzmechanik (die erste bleibt).
- **Durchlauf 4 und später** (ab Welle 190): stärker + dritte Zusatzmechanik; danach kommen keine neuen Mechaniken mehr hinzu, aber jeder weitere Durchlauf erhöht HP und Schaden und verkürzt den Enrage weiter (mit Untergrenze).
- Der Questname einer Bosswelle ist der Bossname mit Durchlauf, z.B. „Oruun, das Auge im Nichts (II)“. Questtext und Abschlusstext sind pro Boss fest.

### Boss 1 – Oruun, das Auge im Nichts
- **Aussehen:** Riesiges, lidloses Auge mit violetter Iris, umgeben von einem Kranz aus schwarzen Tentakeln, das über dem Nichts schwebt.
- **Questtext:** Ein Auge öffnet sich in der Tiefe und starrt direkt in eure Seelen. Schließt es – für immer.
- **Abschlusstext:** Das Auge schließt sich, und für einen Moment ist die Leere blind.
- **Phasen:**
  - **Phase 1 (100–50 % HP):** Blicke und Debuffs.
  - **Phase 2 (ab 50 % HP):** Tentakel lösen sich als Adds, der AoE kommt häufiger.
- **Fähigkeiten:**
  - *Durchdringender Blick* – magischer Angriff auf den Tank (stark).
  - *Starrer Fluch* – Debuff Typ **Magie** (bannbar) auf 2 Ziele, DoT mittel.
  - *Lidschlag* – **AoE** auf alle (magisch, mittel), **Castbalken** (mittel).
  - *Blick der Vernichtung* – **Tank-Buster** (stark), **Castbalken** (kurz).
  - *Tentakelspross* (Phase 2) – ruft 2 **Leerenkriecher** (Adds).
- **Enrage:** Ja, nach langer Zeit (Durchlauf 1).
- **Zusatzmechanik je Durchlauf:**
  - **Durchlauf 2:** *Tränende Leere* – nicht bannbarer DoT auf 2 zufälligen Zielen in Phase 2.
  - **Durchlauf 3:** Starrer Fluch trifft 4 Ziele statt 2.
  - **Durchlauf 4+:** Neue Phase 3 ab 20 % HP: Lidschlag ohne Pause in schneller Folge bis zum Tod.
- **Heiler-Tipps:** Starren Fluch sofort bannen; vor dem Blick der Vernichtung Schild auf den Tank; in Phase 2 Gruppenheilung bereithalten.

### Boss 2 – Mahlkiefer, der Weltenschlinger
- **Aussehen:** Gewaltiger Wurmleib, der nur als endloses, ringförmiges Maul voller Zahnreihen aus dem Nichts ragt.
- **Questtext:** Etwas frisst die Trümmer der Welten – und es hat Hunger auf mehr. Stopft ihm das Maul.
- **Abschlusstext:** Das Maul erstarrt; die verschlungenen Trümmer treiben wieder frei.
- **Phasen:**
  - **Phase 1 (100–60 % HP):** Tank-Druck durch stapelnden Debuff.
  - **Phase 2 (60–30 % HP):** Verschlingen – Adds aus dem Magen.
  - **Phase 3 (ab 30 % HP):** Raserei – alle Fähigkeiten häufiger.
- **Fähigkeiten:**
  - *Mahlen* – normaler Angriff auf den Tank (physisch, sehr stark).
  - *Verdauungssäure* – stapelnder DoT auf dem Tank (nicht bannbar); bei einer Gruppe mit zwei Tanks spotten diese bei hoher Stapelzahl automatisch, mit einem Tank muss gegengeheilt werden.
  - *Weltenbiss* – **Tank-Buster** (extrem stark), **Castbalken** (mittel).
  - *Beben des Schlunds* – **AoE** auf alle (physisch, mittel), **Castbalken** (lang).
  - *Ausspeien* (Phase 2+) – ruft 2 **Sternfresser-Larven** (Adds).
- **Enrage:** Ja, nach mittlerer Zeit.
- **Zusatzmechanik je Durchlauf:**
  - **Durchlauf 2:** *Magenseuche* – Debuff Typ **Krankheit** (bannbar) auf 3 Ziele nach jedem Beben.
  - **Durchlauf 3:** Ausspeien ruft zusätzlich 1 **Riss-Koloss** (Elite-Add).
  - **Durchlauf 4+:** Verdauungssäure stapelt doppelt so schnell.
- **Heiler-Tipps:** Tank dauerhaft mit HoT versorgen; vor dem Weltenbiss Schild und Schadensreduktion; Larven heilen sich – die DPS sollen sie bevorzugt töten.

### Boss 3 – Königin Ysmera der zerrissenen Stunde
- **Aussehen:** Hochgewachsene, blasse Königin mit einer zerbrochenen Sanduhr als Krone und einem Kleid aus fließendem Sternenstaub.
- **Questtext:** Die Königin der zerrissenen Stunde lässt die Zeit selbst verrotten. Beendet ihre Herrschaft, bevor eure eigene Zeit abläuft.
- **Abschlusstext:** Die Sanduhr zerspringt endgültig – die Zeit fließt wieder.
- **Phasen:**
  - **Phase 1 (100–70 % HP):** Magie-Debuffs.
  - **Phase 2 (70–35 % HP):** Magie und Krankheit gleichzeitig.
  - **Phase 3 (ab 35 % HP):** „Letzte Stunde“ – starker AoE mit langem Castbalken.
- **Fähigkeiten:**
  - *Stundenschlag* – magischer Angriff auf den Tank (mittel).
  - *Zeitfäule* – Debuff Typ **Magie** (bannbar) auf 3 Ziele, DoT mittel.
  - *Welke Jahre* (Phase 2+) – Debuff Typ **Krankheit** (bannbar) auf 2 Ziele, verringert erhaltene Heilung.
  - *Sandsturm der Äonen* – **AoE** auf alle (magisch, mittel), **Castbalken** (mittel).
  - *Letzte Stunde* (Phase 3) – **AoE** auf alle (magisch, sehr stark), **Castbalken** (lang).
- **Enrage:** Ja, nach mittlerer Zeit (die Sanduhr läuft sichtbar ab).
- **Zusatzmechanik je Durchlauf:**
  - **Durchlauf 2:** *Stundensplitter* – ruft in Phase 2 zwei **Verzerrte Wanderer** (Adds).
  - **Durchlauf 3:** *Stillstand* – **Tank-Buster** mit kurzem Castbalken in allen Phasen.
  - **Durchlauf 4+:** Letzte Stunde bereits ab 50 % HP.
- **Heiler-Tipps:** Welke Jahre vor Zeitfäule bannen, damit die Heilung wirkt; vor der Letzten Stunde Schilde auf die ganze Gruppe.

### Boss 4 – Der Stumme Chor
- **Aussehen:** Drei verschmolzene, schwebende Gestalten in grauen Kutten mit zugenähten Mündern, verbunden durch violette Fäden – ein einziger Boss.
- **Questtext:** Der Stumme Chor singt ein Lied, das niemand hören kann – und doch bluten eure Ohren. Bringt ihn endgültig zum Schweigen.
- **Abschlusstext:** Die Fäden reißen; der lautlose Gesang verklingt.
- **Phasen:**
  - **Phase 1 (100–66 % HP):** Einzelner Ton – Debuffs.
  - **Phase 2 (66–33 % HP):** Zweistimmig – AoE wird häufiger, Adds.
  - **Phase 3 (ab 33 % HP):** Dreiklang – dauerhafter leichter Gruppenschaden.
- **Fähigkeiten:**
  - *Lautloser Schrei* – magischer Angriff auf den Tank (mittel).
  - *Zugenähter Klang* – Debuff Typ **Magie** (bannbar) auf 2 Ziele, DoT mittel.
  - *Chorwelle* – **AoE** auf alle (magisch, mittel), **Castbalken** (mittel).
  - *Ruf der Hüllen* (Phase 2) – ruft 2 **Hohle Hüllen** (Adds).
  - *Dreiklang* (Phase 3) – dauerhafter leichter Schaden auf alle (nicht bannbar).
- **Enrage:** Ja, nach langer Zeit.
- **Zusatzmechanik je Durchlauf:**
  - **Durchlauf 2:** *Misston* – Debuff Typ **Krankheit** (bannbar), der beim Ablauf auf ein weiteres Ziel springt.
  - **Durchlauf 3:** *Crescendo* – **Tank-Buster** (stark) mit Castbalken.
  - **Durchlauf 4+:** Chorwelle wird zweimal hintereinander gewirkt.
- **Heiler-Tipps:** In Phase 3 Mana einteilen, denn der Dauerschaden hört erst mit dem Tod des Chors auf. Misston früh bannen, bevor er springt.

### Boss 5 – Vael-Thorun, der Spiegelfürst
- **Aussehen:** Ritterliche Gestalt aus zersplittertem Spiegelglas, die das Licht der Gruppe verzerrt zurückwirft.
- **Questtext:** Im Spiegelschlund herrscht ein Fürst, der jeden Angriff zurückwirft. Zerschlagt sein Spiegelbild.
- **Abschlusstext:** Tausend Scherben fallen in die Tiefe – keine zeigt noch ein Gesicht.
- **Phasen:**
  - **Phase 1 (100–50 % HP):** Tank-Druck und Splitter-AoE.
  - **Phase 2 (ab 50 % HP):** Spiegelbilder als Adds.
- **Fähigkeiten:**
  - *Scherbenklinge* – normaler Angriff auf den Tank (physisch, stark).
  - *Bruchlinie* – stapelnder Debuff auf dem Tank, erhöht erlittenen Schaden (nicht bannbar).
  - *Splitterregen* – **AoE** auf alle (physisch, mittel), **Castbalken** (mittel).
  - *Spiegelschlag* – **Tank-Buster** (stark), **Castbalken** (kurz).
  - *Zerrbild* (Phase 2) – ruft 2 **Zerrspiegel** (Adds).
- **Enrage:** Ja, nach mittlerer Zeit.
- **Zusatzmechanik je Durchlauf:**
  - **Durchlauf 2:** *Blendendes Glas* – Debuff Typ **Magie** (bannbar) auf 3 Ziele, DoT mittel.
  - **Durchlauf 3:** Zerrbild ruft zusätzlich einen **Abgrundwächter** (Elite-Add).
  - **Durchlauf 4+:** Neue Phase 3 ab 25 % HP: Splitterregen ohne Castbalken in festen Abständen.
- **Heiler-Tipps:** Tank bei hohen Bruchlinie-Stapeln besonders stark vorheilen; vor dem Spiegelschlag immer Schild.

### Boss 6 – Nhal'Zeroth, Herz des Abgrunds
- **Aussehen:** Ein gigantisches, schlagendes violettes Herz, umwickelt von schwarzen Adern, aus denen Leerwesen tropfen.
- **Questtext:** Das Herz des Abgrunds schlägt – und mit jedem Schlag wird die Leere stärker. Bringt es zum Stillstand.
- **Abschlusstext:** Das Herz setzt einen Schlag aus … und die Tiefe beginnt von Neuem.
- **Phasen:**
  - **Phase 1 (100–75 % HP):** Herzschlag-AoE und Debuffs.
  - **Phase 2 (75–50 % HP):** Adern reißen – Adds.
  - **Phase 3 (50–25 % HP):** Magie und Krankheit gleichzeitig auf vielen Zielen.
  - **Phase 4 (ab 25 % HP):** Rasendes Herz – dauerhafter Gruppenschaden, AoE häufiger.
- **Fähigkeiten:**
  - *Pulsschlag* – magischer Angriff auf den Tank (stark).
  - *Herzschlag der Leere* – **AoE** auf alle (magisch, mittel), **Castbalken** (kurz), in festem Rhythmus.
  - *Schwarzes Blut* – Debuff Typ **Magie** (bannbar) auf 3 Ziele, DoT stark.
  - *Aderfäule* (Phase 3+) – Debuff Typ **Krankheit** (bannbar) auf 3 Ziele, verringert erhaltene Heilung.
  - *Aderriss* (Phase 2+) – ruft 2 **Nichtshunde** und 1 **Riftmotten-Schwarm** (Adds).
  - *Druckwelle* – **Tank-Buster** (sehr stark), **Castbalken** (mittel).
  - *Rasendes Herz* (Phase 4) – dauerhafter Schaden auf alle, der langsam ansteigt (nicht bannbar).
- **Enrage:** Ja, harter Enrage nach mittlerer Zeit.
- **Zusatzmechanik je Durchlauf:**
  - **Durchlauf 2:** *Herzkammer* – ruft in Phase 3 einen **Leerenpriester** (Elite-Add).
  - **Durchlauf 3:** *Blutstau* – stapelnder, nicht bannbarer Debuff auf dem Tank.
  - **Durchlauf 4+:** Herzschlag der Leere in doppeltem Rhythmus ab Phase 3.
- **Heiler-Tipps:** Rhythmus des Herzschlags lernen und Gruppenheilung direkt danach wirken; Aderfäule auf dem Tank zuerst bannen; in Phase 4 alle Notfallzauber und Tränke einsetzen.

## Belohnungen

**Automatische Quest-Belohnung (jede Nicht-Boss-Welle, nur beim ersten Abschluss):**
- EP für Gruppenmitglieder unter Level 60 (der Spieler ist bereits Level 60).
- Gold (steigt mit der Wellennummer).
- Ein zufälliges Item aus dem Item-Katalog unten (Mindestlevel 60, Rarität gewürfelt, Raritätschancen steigen mit der Wellennummer, bevorzugt für die eigene Gruppe).

**Auswahl-Belohnung (jeder Boss, nur beim ersten Sieg in dieser Welle):**
- Zwei Optionen, der Spieler wählt eine. Zusätzlich Gold und EP wie bei der automatischen Belohnung.
- **Garantierte Mindest-Rarität:** **Legendär** bis einschließlich Welle 60; ab Welle 70 (zweiter Durchlauf) **Mythisch**. Mythisch+ ist in beiden Fällen möglich und wird mit steigender Welle wahrscheinlicher.
- **Art (gemischt, fest pro Boss):**

| Boss | Art | Option X | Option Y |
|---|---|---|---|
| Boss 1 – Oruun | 2 Items | Rüstungsteil der Katalogstufe Legendär–Mythisch+ (zufälliger Slot, Rüstungstyp des Spielers oder eines Mitglieds) | Schmuckstück *Tränendes Abgrundauge* |
| Boss 2 – Mahlkiefer | Item gegen Gold | Haupthand-Waffe der Katalogstufe Legendär–Mythisch+ (Typ passend zur Gruppe) | Eine sehr große Menge Gold |
| Boss 3 – Ysmera | Item gegen Trank-Paket | Ring *Siegel der zerrissenen Stunde* | Trank-Paket: viele Heil- und Manatränke der höchsten Stufe und mehrere Werte-Tränke |
| Boss 4 – Stummer Chor | Item gegen Tasche | Halskette *Kette des stummen Abgrundchors* | Eine Tasche der höchsten Rarität (sehr viele Plätze) |
| Boss 5 – Vael-Thorun | 2 Items | Nebenhand-Item der Katalogstufe Legendär–Mythisch+ (Typ passend zur Gruppe) | Umhang *Schleier des Abgrundherzens* |
| Boss 6 – Nhal'Zeroth | 2 Items | Haupthand *Zepter des Abgrundherzens* | Nebenhand *Herzsplitter des Abgrunds* (Artefakt) |

- **Keine Kartenwahl** im Abgrund.
- Wiederholte Bosssiege (z.B. nach einem Rückfall) geben keine Auswahl-Belohnung, aber Gold, EP und Drops mit hoher Drop-Chance.

## Item-Katalog

Alle Items: Mindestlevel 60, Grundwerte auf Level-60-Niveau. Herkunft: Der Abgrund.

### Stoff

| Name | Slot | Grundwert | Rarität | Icon |
|---|---|---|---|---|
| Abgrundwanderer-Kapuze | Helm | Resistenz | Gewöhnlich–Ungewöhnlich | Dunkelgraue Kapuze mit violettem Saum |
| Rissgesäumte Abgrundhaube | Helm | HP | Ungewöhnlich–Selten | Graue Haube mit violett leuchtender Naht |
| Schleierhaube der Leere | Helm | HP | Selten–Episch | Schwarzer Schleier mit schwebenden Sternpunkten |
| Mottenschleier des Abgrunds | Helm | Resistenz | Selten–Episch | Blasser Schleier mit Mottenflügelmuster |
| Sternengrab-Kapuze | Helm | Resistenz | Episch–Legendär | Schwarze Kapuze, in der erlöschende Sterne treiben |
| Diadem des tausendfachen Abgrundblicks | Helm | Resistenz | Legendär–Mythisch+ | Silberreif mit einem offenen violetten Auge auf der Stirn |
| Zerfaserte Abgrund-Schulterwickel | Schultern | HP | Gewöhnlich–Ungewöhnlich | Graue Stoffbahnen, deren Enden sich in Nichts auflösen |
| Abgrundstaub-Schulterbahnen | Schultern | Resistenz | Gewöhnlich–Ungewöhnlich | Graue, staubige Stoffbahnen |
| Treibgut-Schultertücher der Leere | Schultern | Resistenz | Ungewöhnlich–Selten | Graue Tücher mit schwebenden Steinsplittern |
| Nichtsweber-Schultertücher | Schultern | Resistenz | Selten–Episch | Violette Tücher mit fadenartigen Mustern |
| Chorschultern des stummen Abgrunds | Schultern | HP | Episch–Legendär | Graue Schultern mit zugenähten Mündern |
| Sternenfall-Schultern des Abgrunds | Schultern | HP | Legendär–Mythisch+ | Schwarze Schultern, von denen kleine Sterne herabrieseln |
| Robe des Abgrundpilgers | Brust | Resistenz | Gewöhnlich–Ungewöhnlich | Schlichte graue Robe mit Rissmuster |
| Kittel des Abgrundkartografen | Brust | HP | Ungewöhnlich–Selten | Graublaue Robe mit aufgezeichneten Rissen |
| Gewand des Leerenlauschers | Brust | HP | Selten–Episch | Dunkelblaue Robe mit Ohrsymbolen |
| Spiegelrobe des Spiegelschlunds | Brust | Resistenz | Episch–Legendär | Robe mit eingenähten Spiegelscherben |
| Ornat der Weltenleere | Brust | Resistenz | Legendär–Mythisch+ | Tiefschwarze Robe mit einem Sternbild, das sich bewegt |
| Herzrobe von Nhal'Zeroth | Brust | HP | Legendär–Mythisch+ | Schwarze Robe mit einem schlagenden violetten Licht |
| Stoffbänder des Abgrundrands | Armschienen | HP | Gewöhnlich–Ungewöhnlich | Graue Bänder mit ausgefransten Kanten |
| Sanduhrbänder des Abgrunds | Armschienen | Resistenz | Ungewöhnlich–Selten | Graue Bänder mit winzigen Sanduhrknöpfen |
| Fadenmanschetten der Weberin | Armschienen | Resistenz | Selten–Episch | Violette Manschetten aus glänzenden Fäden |
| Nichtsfaden-Manschetten | Armschienen | HP | Selten–Episch | Schwarze Manschetten aus fast unsichtbaren Fäden |
| Armwickel der zerrissenen Stunde | Armschienen | HP | Episch–Legendär | Violette Wickel mit zerbrochenen Zeigern |
| Armwickel des zeitlosen Abgrunds | Armschienen | HP | Legendär–Mythisch+ | Schwarze Bänder mit einer winzigen Sanduhr |
| Handschuhe des Abgrundstaubs | Handschuhe | Resistenz | Gewöhnlich–Ungewöhnlich | Graue, staubige Stoffhandschuhe |
| Abgrundpilger-Fäustlinge | Handschuhe | HP | Gewöhnlich–Ungewöhnlich | Graue, ausgefranste Stofffäustlinge |
| Rissnäher-Handschuhe des Abgrunds | Handschuhe | HP | Ungewöhnlich–Selten | Graue Handschuhe mit violettem Nähfaden |
| Flüsterhände der Leere | Handschuhe | HP | Selten–Episch | Dunkelviolette Handschuhe mit Mund-Stickerei |
| Sternenpflücker-Handschuhe der Leere | Handschuhe | Resistenz | Episch–Legendär | Dunkelblaue Handschuhe mit funkelnden Fingerspitzen |
| Griffe des namenlosen Abgrunds | Handschuhe | Resistenz | Legendär–Mythisch+ | Schwarze Handschuhe mit leuchtenden Fingerspitzen |
| Abgrundkordel | Gürtel | HP | Gewöhnlich–Ungewöhnlich | Graue Kordel mit schwarzem Knoten |
| Treibkordel der Abgrundtiefe | Gürtel | Resistenz | Ungewöhnlich–Selten | Graue Kordel mit einem schwebenden Steinchen |
| Mottengürtel des Abgrunds | Gürtel | HP | Ungewöhnlich–Selten | Grauer Gürtel mit kleinen Mottenanhängern |
| Schärpe der stummen Tiefe | Gürtel | Resistenz | Selten–Episch | Violette Schärpe mit zugenähtem Muster |
| Schärpe des Spiegelfürsten | Gürtel | HP | Episch–Legendär | Silberne Schärpe mit Spiegelschnalle |
| Gurt des Abgrundherzens | Gürtel | HP | Legendär–Mythisch+ | Schwarzer Gurt mit pulsierendem violettem Stein |
| Beinkleid des Abgrundwanderers | Hose | Resistenz | Gewöhnlich–Ungewöhnlich | Graue Stoffhose mit Rissflicken |
| Beinkleid des Leerenpilgers | Hose | HP | Ungewöhnlich–Selten | Graue Hose mit violetten Flicken |
| Sternstaub-Beinwickel | Hose | HP | Selten–Episch | Dunkelblaue Hose mit glitzerndem Staub |
| Riftstich-Hose des Abgrunds | Hose | Resistenz | Selten–Episch | Dunkle Hose mit leuchtenden Rissnähten |
| Fleischgewölbe-Beinwickel | Hose | Resistenz | Episch–Legendär | Violett-rote Hose mit geschlossenen Augen als Muster |
| Hose der ewigen Abgrundnacht | Hose | Resistenz | Legendär–Mythisch+ | Tiefschwarze Hose mit violetten Lichtfäden |
| Abgrundschleicher-Sandalen | Schuhe | HP | Gewöhnlich–Ungewöhnlich | Graue Sandalen, die leicht über dem Boden schweben |
| Schwebeschuhe des Abgrundrands | Schuhe | Resistenz | Ungewöhnlich–Selten | Graue Schuhe über einem Hauch violetten Nebels |
| Schuhe des bodenlosen Falls | Schuhe | Resistenz | Selten–Episch | Violette Schuhe mit Federn an den Fersen |
| Sternenfall-Pantoffeln der Leere | Schuhe | HP | Episch–Legendär | Schwarze Pantoffeln mit fallenden Sternen |
| Spiegelschritt-Schuhe des Abgrunds | Schuhe | Resistenz | Episch–Legendär | Silberne Schuhe mit spiegelnder Sohle |
| Schritte zwischen den Welten | Schuhe | HP | Legendär–Mythisch+ | Schwarze Schuhe, deren Sohlen fremde Landschaften zeigen |

### Leder

| Name | Slot | Grundwert | Rarität | Icon |
|---|---|---|---|---|
| Nichtshund-Lederkappe | Helm | Rüstung | Gewöhnlich–Ungewöhnlich | Graue Lederkappe mit Rauchfell |
| Abgrundspäher-Lederkappe | Helm | HP | Gewöhnlich–Ungewöhnlich | Graue, abgewetzte Lederkappe |
| Rauchfell-Haube des Nichtshunds | Helm | Resistenz | Ungewöhnlich–Selten | Graue Haube mit Rauchfellbesatz |
| Maske des Abgrundpirschers | Helm | HP | Selten–Episch | Schwarze Ledermaske mit drei weißen Augenschlitzen |
| Augenmaske von Oruun | Helm | Rüstung | Episch–Legendär | Schwarze Maske mit einem großen violetten Auge |
| Hornhaube des Leerenjägers | Helm | Resistenz | Legendär–Mythisch+ | Violette Haube mit gewundenen Schattenhörnern |
| Abgrund-Lederschultern | Schultern | HP | Gewöhnlich–Ungewöhnlich | Graue, abgewetzte Lederpolster |
| Trümmerleder-Schultern der Leere | Schultern | Rüstung | Ungewöhnlich–Selten | Braune Schultern mit Steinsplittern |
| Mottenflügel-Schultern | Schultern | Rüstung | Selten–Episch | Schultern aus violetten Mottenflügeln |
| Rissleder-Schulterpolster des Abgrunds | Schultern | Resistenz | Selten–Episch | Dunkle Polster mit violetten Rissen |
| Mahlkiefers Kieferschultern | Schultern | Resistenz | Episch–Legendär | Schwarze Schultern aus zwei Zahnreihen |
| Schulterkrallen des Weltenschlingers | Schultern | HP | Legendär–Mythisch+ | Schwarze Schultern mit Zahnreihen |
| Wams des Abgrundspähers | Brust | Rüstung | Gewöhnlich–Ungewöhnlich | Graues Lederwams mit violetten Nähten |
| Wams des Abgrundkletterers | Brust | HP | Ungewöhnlich–Selten | Graues Wams mit Seilschlaufen |
| Treibgutweste des Abgrunds | Brust | Rüstung | Ungewöhnlich–Selten | Braune Weste aus Flicken fremder Welten |
| Harnisch der Riftjagd | Brust | HP | Selten–Episch | Dunkler Harnisch mit Rissmuster |
| Spiegelschuppen-Harnisch der Leere | Brust | Rüstung | Episch–Legendär | Harnisch aus spiegelnden Lederschuppen |
| Harnisch des tiefsten Abgrunds | Brust | Resistenz | Legendär–Mythisch+ | Schwarzer Harnisch mit leuchtendem Sternbild |
| Lederbänder der Abgrundtiefe | Armschienen | HP | Gewöhnlich–Ungewöhnlich | Graue Armbänder mit Knoten |
| Abgrundpilger-Armriemen | Armschienen | Rüstung | Gewöhnlich–Ungewöhnlich | Einfache graue Lederriemen |
| Mottenstaub-Armbinden | Armschienen | Resistenz | Ungewöhnlich–Selten | Graue Armbinden mit Mottenstaub |
| Sternfresser-Armbinden | Armschienen | Rüstung | Selten–Episch | Blasse Armbinden mit funkelndem Stern |
| Armschienen des Sternengrabs | Armschienen | HP | Episch–Legendär | Schwarze Armschienen mit erlöschenden Sternen |
| Armschienen des schweigenden Abgrunds | Armschienen | Resistenz | Legendär–Mythisch+ | Schwarze Armschienen mit zugenähtem Mund |
| Abgrundgreifer | Handschuhe | Rüstung | Gewöhnlich–Ungewöhnlich | Graue Lederhandschuhe mit Rissen |
| Rissgreifer der Leere | Handschuhe | HP | Ungewöhnlich–Selten | Graue Handschuhe mit violetten Rissen an den Fingern |
| Fänge des Nichtshunds | Handschuhe | HP | Selten–Episch | Rauchschwarze Handschuhe mit weißen Krallen |
| Stundengriffe der Königin Ysmera | Handschuhe | Resistenz | Selten–Episch | Violette Handschuhe mit Uhrzeigern auf dem Handrücken |
| Zahnhandschuhe des Weltenschlingers | Handschuhe | Resistenz | Episch–Legendär | Schwarze Handschuhe mit Zahnreihen an den Knöcheln |
| Klauen der zerrissenen Stunde | Handschuhe | Rüstung | Legendär–Mythisch+ | Violette Handschuhe mit Sanduhr-Knöcheln |
| Ledergurt des Abgrundläufers | Gürtel | HP | Gewöhnlich–Ungewöhnlich | Grauer Gurt mit leerer Tasche |
| Treibgut-Ledergurt | Gürtel | Rüstung | Ungewöhnlich–Selten | Brauner Gurt mit fremden Münzen |
| Riftriemen | Gürtel | Resistenz | Selten–Episch | Violetter Riemen mit Rissschnalle |
| Gürtel des stummen Chors | Gürtel | Resistenz | Episch–Legendär | Grauer Gurt mit drei zugenähten Anhängern |
| Riftjäger-Gurt des Abgrunds | Gürtel | HP | Episch–Legendär | Schwarzer Gurt mit violetter Rissschnalle |
| Gürtel der verschlungenen Welten | Gürtel | HP | Legendär–Mythisch+ | Schwarzer Gürtel mit Miniaturwelten als Nieten |
| Beinlinge des Abgrundspurers | Hose | Rüstung | Gewöhnlich–Ungewöhnlich | Graue Lederhose mit Staubflecken |
| Abgrundstaub-Lederhose | Hose | HP | Gewöhnlich–Ungewöhnlich | Graue Lederhose voller Staub |
| Nichtshund-Beinlinge | Hose | HP | Ungewöhnlich–Selten | Graue Hose mit Rauchfellbesatz |
| Leerenhaut-Beinlinge | Hose | Resistenz | Selten–Episch | Violette, schimmernde Hose |
| Beinlinge des Spiegelschlunds | Hose | Rüstung | Episch–Legendär | Dunkle Hose mit spiegelnden Kniescheiben |
| Beinschützer des Abgrundjägers | Hose | Rüstung | Legendär–Mythisch+ | Schwarze Hose mit violetten Klauenspuren |
| Abgrundstapfer | Schuhe | HP | Gewöhnlich–Ungewöhnlich | Graue, weiche Lederstiefel |
| Trümmerspringer-Stiefel der Leere | Schuhe | Resistenz | Ungewöhnlich–Selten | Braune Stiefel mit Steinsporen |
| Stiefel der fallenden Trümmer | Schuhe | Rüstung | Selten–Episch | Braune Stiefel mit Steinsplittern |
| Mottenschritt-Stiefel des Abgrunds | Schuhe | HP | Episch–Legendär | Violette Stiefel mit Mottenflügeln an den Fersen |
| Schleichschritte des Nichts | Schuhe | Resistenz | Legendär–Mythisch+ | Schwarze Stiefel, die keine Spur hinterlassen |
| Stiefel von Nhal'Zeroth | Schuhe | Rüstung | Legendär–Mythisch+ | Schwarze Stiefel mit pulsierenden violetten Adern |

### Kette

| Name | Slot | Grundwert | Rarität | Icon |
|---|---|---|---|---|
| Kettenhaube des Abgrundpostens | Helm | Rüstung | Gewöhnlich–Ungewöhnlich | Graue Kettenhaube mit violettem Schimmer |
| Abgrundstaub-Kettenkapuze | Helm | Resistenz | Gewöhnlich–Ungewöhnlich | Graue, verstaubte Kettenkapuze |
| Spiegelring-Kettenhaube des Abgrunds | Helm | HP | Ungewöhnlich–Selten | Kettenhaube aus spiegelnden Ringen |
| Riftwacht-Kettenhelm | Helm | HP | Selten–Episch | Dunkler Kettenhelm mit Rissvisier |
| Augenhelm von Oruun | Helm | Resistenz | Episch–Legendär | Schwarzer Kettenhelm mit einem violetten Auge über dem Visier |
| Visier des Abgrundfalken | Helm | Rüstung | Legendär–Mythisch+ | Schwarzer Helm mit silbernem Falkenschnabel und violetten Augen |
| Abgrund-Kettenschultern | Schultern | Rüstung | Gewöhnlich–Ungewöhnlich | Einfache graue Kettenschultern |
| Treibgut-Kettenschultern der Leere | Schultern | HP | Ungewöhnlich–Selten | Kettenschultern mit schwebenden Steinbrocken |
| Sternsplitter-Schultern | Schultern | Resistenz | Selten–Episch | Dunkelblaue Schultern mit eingesetzten Sternsplittern |
| Mottenketten-Schultern des Abgrunds | Schultern | HP | Selten–Episch | Violette Kettenschultern mit Mottenflügelplättchen |
| Chorschultern der Leerenwacht | Schultern | Rüstung | Episch–Legendär | Graue Schultern mit drei zugenähten Masken |
| Schulterschuppen des Spiegelfürsten | Schultern | HP | Legendär–Mythisch+ | Spiegelnde Schuppenschultern |
| Kettenhemd des Abgrundwächters | Brust | HP | Gewöhnlich–Ungewöhnlich | Graues Kettenhemd mit Obsidianringen |
| Sternengrab-Kettenhemd | Brust | Resistenz | Ungewöhnlich–Selten | Schwarzes Kettenhemd mit fahlen Sternen |
| Brünne der treibenden Trümmer | Brust | Rüstung | Selten–Episch | Brünne mit eingearbeiteten Steinsplittern |
| Brünne des Weltenschlingers | Brust | HP | Episch–Legendär | Brünne mit Zahnreihen am Kragen |
| Spiegelbrünne des Vael-Thorun | Brust | Rüstung | Episch–Legendär | Brünne aus spiegelnden Plättchen |
| Brünne des Abgrundadlers | Brust | Resistenz | Legendär–Mythisch+ | Schwarze Brünne mit violettem Adlerwappen |
| Kettenstulpen des Abgrunds | Armschienen | Rüstung | Gewöhnlich–Ungewöhnlich | Graue, einfache Stulpen |
| Abgrundpilger-Kettenstulpen | Armschienen | HP | Gewöhnlich–Ungewöhnlich | Graue, schlichte Kettenstulpen |
| Rissbänder der Abgrundjäger | Armschienen | Resistenz | Ungewöhnlich–Selten | Dunkle Kettenbänder mit violetten Rissen |
| Riftjäger-Kettenbänder | Armschienen | HP | Selten–Episch | Violette Kettenbänder mit Rissgravur |
| Stundenstulpen der Königin Ysmera | Armschienen | Rüstung | Episch–Legendär | Violette Stulpen mit zerbrochenen Ziffernblättern |
| Stulpen des Abgrundfährtensuchers | Armschienen | Rüstung | Legendär–Mythisch+ | Schwarze Stulpen mit leuchtendem Kompass |
| Kettenhandschuhe des Abgrundstaubs | Handschuhe | Resistenz | Gewöhnlich–Ungewöhnlich | Graue, staubige Kettenhandschuhe |
| Treibgut-Kettenhandschuhe | Handschuhe | HP | Ungewöhnlich–Selten | Graue Kettenhandschuhe mit Steinsplittern |
| Leerengriff-Handschuhe | Handschuhe | Rüstung | Selten–Episch | Violett schimmernde Kettenhandschuhe |
| Mottenfänger-Handschuhe der Leere | Handschuhe | Resistenz | Episch–Legendär | Violette Kettenhandschuhe mit Netzmuster |
| Fänge des Augenschwarms | Handschuhe | HP | Legendär–Mythisch+ | Schwarze Handschuhe mit kleinen Augen auf den Knöcheln |
| Weltenriss-Fäuste von Nhal'Zeroth | Handschuhe | Rüstung | Legendär–Mythisch+ | Schwarze Handschuhe mit violett schlagendem Licht |
| Kettengurt des Abgrundrands | Gürtel | Rüstung | Gewöhnlich–Ungewöhnlich | Grauer Gurt mit einfacher Schnalle |
| Kettengurt des Abgrundkletterers | Gürtel | HP | Ungewöhnlich–Selten | Grauer Kettengurt mit Kletterhaken |
| Gliedergurt der Leere | Gürtel | Resistenz | Selten–Episch | Violetter Gurt aus schwebenden Gliedern |
| Sternensplitter-Gurt der Leere | Gürtel | HP | Selten–Episch | Dunkler Gurt mit glitzernden Splittern |
| Spiegelgliedergurt des Abgrunds | Gürtel | Resistenz | Episch–Legendär | Gurt aus spiegelnden Kettengliedern |
| Gürtel des Abgrundschützen | Gürtel | Rüstung | Legendär–Mythisch+ | Schwarzer Gurt mit violetten Pfeilspitzen |
| Kettenbeinlinge des Abgrundpfads | Hose | Rüstung | Gewöhnlich–Ungewöhnlich | Graue Kettenhose |
| Nichtshund-Kettenhose | Hose | Resistenz | Ungewöhnlich–Selten | Graue Kettenhose mit Rauchfell an den Knien |
| Treibgut-Beinlinge der Riftwacht | Hose | Rüstung | Ungewöhnlich–Selten | Dunkle Kettenhose mit Steinplättchen |
| Schuppenbeinlinge der Riftwacht | Hose | HP | Selten–Episch | Dunkle Schuppenhose mit Rissmuster |
| Beinkette des stummen Chors | Hose | HP | Episch–Legendär | Graue Kettenhose mit zugenähten Kniemasken |
| Beinkette der Sternenleere | Hose | Rüstung | Legendär–Mythisch+ | Schwarze Kettenhose mit wandernden Sternen |
| Kettenstiefel des Abgrundpostens | Schuhe | HP | Gewöhnlich–Ungewöhnlich | Graue Kettenstiefel |
| Abgrundrand-Kettenschuhe | Schuhe | Rüstung | Gewöhnlich–Ungewöhnlich | Graue, schlichte Kettenschuhe |
| Sternenstaub-Kettenstiefel | Schuhe | Rüstung | Ungewöhnlich–Selten | Dunkelblaue Kettenstiefel mit glitzerndem Staub |
| Stiefel der Riftjagd | Schuhe | Resistenz | Selten–Episch | Violette Kettenstiefel mit Rissschnallen |
| Stiefel des Spiegelschlunds | Schuhe | HP | Episch–Legendär | Kettenstiefel mit spiegelnden Kappen |
| Sabatons des bodenlosen Laufs | Schuhe | Rüstung | Legendär–Mythisch+ | Schwarze Stiefel, die über violettem Licht schweben |

### Platte

| Name | Slot | Grundwert | Rarität | Icon |
|---|---|---|---|---|
| Abgrundwächter-Topfhelm | Helm | Rüstung | Gewöhnlich–Ungewöhnlich | Grauer Topfhelm mit schmalem Sehschlitz |
| Rissvisier des Abgrundpostens | Helm | HP | Ungewöhnlich–Selten | Grauer Helm mit violettem Rissvisier |
| Obsidianhelm der Leere | Helm | HP | Selten–Episch | Schwarzer Obsidianhelm mit violettem Schlitzvisier |
| Obsidian-Großhelm der Abgrundwacht | Helm | Rüstung | Selten–Episch | Schwarzer Großhelm mit silbernem Augenkamm |
| Kieferhelm des Mahlkiefers | Helm | Resistenz | Episch–Legendär | Schwarzer Helm mit Zahnreihen als Visier |
| Krone des Abgrundbezwingers | Helm | Rüstung | Legendär–Mythisch+ | Schwarz-silberner Helm mit schwebender Sternkrone |
| Abgrund-Schulterplatten | Schultern | Rüstung | Gewöhnlich–Ungewöhnlich | Klobige graue Schulterplatten |
| Abgrundpilger-Schulterplatten | Schultern | HP | Gewöhnlich–Ungewöhnlich | Graue, zerkratzte Schulterplatten |
| Trümmerplatten-Schultern der Leere | Schultern | Resistenz | Ungewöhnlich–Selten | Schultern aus fremden Mauersteinen |
| Riss-Koloss-Schulterplatten | Schultern | HP | Selten–Episch | Steinerne Schultern mit violettem Riss |
| Spiegelschultern des Vael-Thorun | Schultern | Rüstung | Episch–Legendär | Spiegelnde Schulterplatten mit Rissen |
| Schulterwälle des Abgrundherzens | Schultern | Rüstung | Legendär–Mythisch+ | Riesige schwarze Schultern mit pulsierenden Adern |
| Brustplatte des Abgrundrands | Brust | HP | Gewöhnlich–Ungewöhnlich | Graue Brustplatte mit Kratzern |
| Sternengrab-Brustplatte | Brust | Rüstung | Ungewöhnlich–Selten | Schwarze Brustplatte mit fahlen Sternen |
| Treibgut-Harnisch des Abgrundkletterers | Brust | Resistenz | Ungewöhnlich–Selten | Harnisch aus Plattenstücken fremder Welten |
| Kürass des zeitlosen Ritters | Brust | Rüstung | Selten–Episch | Verwitterter Kürass, der jung und alt flackert |
| Kürass des schlagenden Abgrunds | Brust | HP | Episch–Legendär | Violett-roter Kürass mit pulsierenden Adern |
| Harnisch des Leerenbezwingers | Brust | HP | Legendär–Mythisch+ | Schwarzer Harnisch mit einem geschlossenen Auge im Zentrum |
| Abgrund-Armschienen | Armschienen | Rüstung | Gewöhnlich–Ungewöhnlich | Graue, einfache Plattenarmschienen |
| Rissarmschienen der Abgrundwacht | Armschienen | HP | Ungewöhnlich–Selten | Graue Armschienen mit violetten Rissen |
| Obsidianarmschienen der Tiefe | Armschienen | Resistenz | Selten–Episch | Schwarze, glänzende Armschienen |
| Obsidian-Armwälle des Abgrunds | Armschienen | HP | Selten–Episch | Dicke schwarze Armschienen |
| Stundenarmplatten der Königin Ysmera | Armschienen | Rüstung | Episch–Legendär | Goldene Armschienen mit stillstehenden Zeigern |
| Armplatten des ewigen Abgrunds | Armschienen | Rüstung | Legendär–Mythisch+ | Schwarze Armschienen mit silbernen Sternkanten |
| Abgrundfäuste | Handschuhe | HP | Gewöhnlich–Ungewöhnlich | Graue Panzerhandschuhe |
| Abgrundrand-Plattenhandschuhe | Handschuhe | Rüstung | Gewöhnlich–Ungewöhnlich | Schlichte graue Plattenhandschuhe |
| Treibgut-Panzerhandschuhe | Handschuhe | Resistenz | Ungewöhnlich–Selten | Graue Panzerhandschuhe mit Steinsplittern |
| Nichtshammer-Handschuhe | Handschuhe | Rüstung | Selten–Episch | Schwere Handschuhe mit Obsidianknöcheln |
| Fäuste des Weltenschlingers | Handschuhe | Rüstung | Episch–Legendär | Schwarze Panzerhandschuhe mit Zahnknöcheln |
| Panzerfäuste des Weltenrisses | Handschuhe | HP | Legendär–Mythisch+ | Schwarze Handschuhe mit violetten Rissen |
| Plattengurt des Abgrundpostens | Gürtel | Rüstung | Gewöhnlich–Ungewöhnlich | Grauer Plattengurt |
| Obsidiangurt der Abgrundposten | Gürtel | HP | Ungewöhnlich–Selten | Schwarzer Plattengurt mit grauer Schnalle |
| Gurt des Riss-Kolosses | Gürtel | HP | Selten–Episch | Steinerner Gurt mit violettem Kern |
| Chorgurt der stummen Wacht | Gürtel | Rüstung | Episch–Legendär | Grauer Plattengurt mit drei Maskenschnallen |
| Herzschlag-Gurt des Abgrunds | Gürtel | HP | Episch–Legendär | Schwarzer Gurt mit pulsierender violetter Schnalle |
| Gürtel der Abgrundwacht | Gürtel | Resistenz | Legendär–Mythisch+ | Silberner Gurt mit Augenschnalle |
| Beinplatten des Abgrundrands | Hose | HP | Gewöhnlich–Ungewöhnlich | Graue Beinplatten |
| Sternengrab-Beinplatten | Hose | Rüstung | Ungewöhnlich–Selten | Schwarze Beinplatten mit fallenden Sternen |
| Obsidian-Beinschienen der Leere | Hose | Rüstung | Selten–Episch | Schwarze, glänzende Beinschienen |
| Riftwacht-Beinplatten des Abgrunds | Hose | Resistenz | Selten–Episch | Dunkle Beinplatten mit violetten Kanten |
| Beinschienen des Spiegelfürsten | Hose | HP | Episch–Legendär | Spiegelnde Beinschienen mit Rissen |
| Beinpanzer des tiefsten Falls | Hose | Rüstung | Legendär–Mythisch+ | Schwarze Beinplatten mit violetten Lichtbahnen |
| Abgrundtreter | Schuhe | Rüstung | Gewöhnlich–Ungewöhnlich | Klobige graue Plattenstiefel |
| Trümmerstampfer der Leere | Schuhe | Resistenz | Ungewöhnlich–Selten | Graue Stiefel mit Mauerresten an den Sohlen |
| Obsidianschreiter der Leere | Schuhe | HP | Selten–Episch | Schwarze Stiefel mit violetten Sohlen |
| Sabatons des Spiegelschlunds | Schuhe | Rüstung | Episch–Legendär | Spiegelnde Plattenstiefel |
| Sabatons des Abgrundherrschers | Schuhe | Rüstung | Legendär–Mythisch+ | Schwarz-silberne Stiefel mit Sternensporen |
| Herzschritt-Sabatons von Nhal'Zeroth | Schuhe | HP | Legendär–Mythisch+ | Schwarze Stiefel, deren Sohlen violett pulsieren |

### Umhang

| Name | Slot | Grundwert | Rarität | Icon |
|---|---|---|---|---|
| Staubmantel des Abgrunds | Umhang | Resistenz | Gewöhnlich–Ungewöhnlich | Grauer, ausgefranster Umhang |
| Treibgut-Mantel der Leere | Umhang | HP | Ungewöhnlich–Selten | Grauer Umhang aus Flicken fremder Stoffe |
| Riftumhang der Leere | Umhang | HP | Selten–Episch | Violetter Umhang mit Rissmuster |
| Sternengrab-Umhang | Umhang | Resistenz | Selten–Episch | Schwarzer Umhang mit erlöschenden Sternen |
| Mottenschwingen-Umhang des Abgrunds | Umhang | Rüstung | Episch–Legendär | Violetter Umhang in Form großer Mottenflügel |
| Schleier des Abgrundherzens | Umhang | Rüstung | Legendär–Mythisch+ | Schwarzer Umhang mit einem schlagenden violetten Herz auf dem Rücken |

### Schmuck

| Name | Slot | Grundwert | Rarität | Icon |
|---|---|---|---|---|
| Abgrundperlen-Kette | Halskette | Mana | Gewöhnlich–Ungewöhnlich | Kette aus kleinen schwarzen Perlen |
| Treibgut-Halskette der Leere | Halskette | Mana-Reg | Gewöhnlich–Ungewöhnlich | Kette mit einem kleinen schwebenden Steinchen |
| Mottenstaub-Anhänger des Abgrunds | Halskette | Mana-Reg | Ungewöhnlich–Selten | Kleiner Anhänger mit gefangenem Mottenstaub |
| Amulett des Leerenflüsterns | Halskette | Mana-Reg | Selten–Episch | Silberamulett mit einem leuchtenden Mund |
| Spiegelamulett des Vael-Thorun | Halskette | Mana | Episch–Legendär | Silberamulett mit spiegelndem Stein |
| Kette des stummen Abgrundchors | Halskette | Mana | Legendär–Mythisch+ | Drei verbundene graue Anhänger mit violettem Faden |
| Obsidianring des Abgrunds | Ring | Krit | Gewöhnlich–Ungewöhnlich | Schlichter schwarzer Ring |
| Nichtshund-Zahnring | Ring | Krit | Ungewöhnlich–Selten | Ring aus einem weißen Zahn |
| Riftsiegel-Ring | Ring | Tempo | Selten–Episch | Silberring mit violettem Riss im Stein |
| Sternengrab-Ring | Ring | Tempo | Episch–Legendär | Schwarzer Ring mit fahlem Stern |
| Kieferring des Mahlkiefers | Ring | Krit | Episch–Legendär | Ring mit winzigen Zahnreihen |
| Siegel der zerrissenen Stunde | Ring | Tempo | Legendär–Mythisch+ | Goldring mit einer winzigen zerbrochenen Sanduhr |
| Treibender Abgrundsplitter | Schmuckstück | Mana-Reg | Gewöhnlich–Ungewöhnlich | Kleiner schwebender Gesteinsbrocken |
| Zugenähte Chormaske des Abgrunds | Schmuckstück | Schaden | Ungewöhnlich–Selten | Kleine graue Maske mit zugenähtem Mund |
| Sternfresser-Funke | Schmuckstück | Tempo | Selten–Episch | Funkelnder Stern in einer blassen Hülle |
| Spiegelscherbe des Spiegelschlunds | Schmuckstück | Heilstärke | Episch–Legendär | Leuchtende Spiegelscherbe in Silberfassung |
| Tränendes Abgrundauge | Schmuckstück | Heilstärke | Legendär–Mythisch+ | Violettes Auge, aus dem eine leuchtende Träne rinnt |
| Pulsherz von Nhal'Zeroth | Schmuckstück | Krit | Legendär–Mythisch+ | Kleines violettes Herz, das im Takt leuchtet |

### Haupthand

| Name | Slot | Typ | Grundwert | Rarität | Icon |
|---|---|---|---|---|---|
| Stab des Abgrundpilgers | Haupthand | Stab | Heilstärke | Gewöhnlich–Ungewöhnlich | Grauer, gerader Stab mit schwarzem Stein |
| Rissstab des Abgrundpredigers | Haupthand | Stab | Schaden | Ungewöhnlich–Selten | Grauer Stab mit violettem Riss im Holz |
| Leerenruf-Stab | Haupthand | Stab | Schaden | Selten–Episch | Dunkler Stab mit einem schwebenden violetten Riss an der Spitze |
| Sternengrab-Stab | Haupthand | Stab | Heilstärke | Selten–Episch | Schwarzer Stab mit einem fahlen Stern in einem Käfig |
| Stab der Abgrundmotte | Haupthand | Stab | Heilstärke | Episch–Legendär | Silberner Stab mit einer leuchtenden Motte an der Spitze |
| Stab des letzten Sterns | Haupthand | Stab | Heilstärke | Legendär–Mythisch+ | Schwarzer Stab mit einem hell leuchtenden Stern in einer Klaue |
| Abgrundkolben | Haupthand | Streitkolben | Schaden | Gewöhnlich–Ungewöhnlich | Grauer Kolben mit Obsidiankopf |
| Pilgerkolben des Abgrunds | Haupthand | Streitkolben | Heilstärke | Gewöhnlich–Ungewöhnlich | Schlichter grauer Kolben mit violettem Schimmer |
| Treibgut-Kolben der Leere | Haupthand | Streitkolben | Schaden | Ungewöhnlich–Selten | Kolben mit einem Kopf aus fremdem Mauerstein |
| Weihekolben des Leerenlichts | Haupthand | Streitkolben | Heilstärke | Selten–Episch | Silberner Kolben mit violett-weißem Licht |
| Stundenkolben der Königin Ysmera | Haupthand | Streitkolben | Schaden | Episch–Legendär | Goldener Kolben mit Sanduhrkopf |
| Zepter des Abgrundherzens | Haupthand | Streitkolben | Heilstärke | Legendär–Mythisch+ | Schwarzes Zepter mit einem pulsierenden violetten Herz |
| Klinge des Abgrundwanderers | Haupthand | Schwert | Schaden | Gewöhnlich–Ungewöhnlich | Graues Kurzschwert mit Riss in der Klinge |
| Spiegelsplitter-Klinge des Abgrunds | Haupthand | Schwert | Schaden | Ungewöhnlich–Selten | Kurzschwert aus zusammengefügten Spiegelscherben |
| Treibgut-Säbel der Leere | Haupthand | Schwert | Schaden | Ungewöhnlich–Selten | Gebogener Säbel mit fremdartigem Griff |
| Spiegelschwert des Spiegelschlunds | Haupthand | Schwert | Schaden | Selten–Episch | Klinge aus spiegelndem Glas |
| Stundenschwert der zerrissenen Zeit | Haupthand | Schwert | Schaden | Episch–Legendär | Silberne Klinge mit zerbrochenem Ziffernblatt |
| Weltenschnitter des Abgrunds | Haupthand | Schwert | Schaden | Legendär–Mythisch+ | Schwarzes Langschwert, dessen Schneide ein violetter Riss ist |
| Abgrundbeil | Haupthand | Axt | Schaden | Gewöhnlich–Ungewöhnlich | Grobe graue Axt |
| Rissbeil der Abgrundwacht | Haupthand | Axt | Schaden | Ungewöhnlich–Selten | Graue Axt mit violettem Rissblatt |
| Obsidianspalter der Leere | Haupthand | Axt | Schaden | Selten–Episch | Große schwarze Axt mit violetter Kante |
| Sternenfall-Axt der Leere | Haupthand | Axt | Schaden | Selten–Episch | Schwarze Axt mit einem fallenden Stern im Blatt |
| Kieferaxt des Mahlkiefers | Haupthand | Axt | Schaden | Episch–Legendär | Axt mit gezahntem Kieferblatt |
| Axt des Weltenschlingers | Haupthand | Axt | Schaden | Legendär–Mythisch+ | Doppelaxt mit Zahnreihen statt Schneiden |
| Abgrundsplitter-Dolch | Haupthand | Dolch | Schaden | Gewöhnlich–Ungewöhnlich | Kleiner Dolch aus schwarzem Splitter |
| Abgrundpilger-Messer | Haupthand | Dolch | Schaden | Gewöhnlich–Ungewöhnlich | Einfaches graues Messer |
| Mottenflügel-Dolch des Abgrunds | Haupthand | Dolch | Schaden | Ungewöhnlich–Selten | Dünner Dolch mit Mottenflügel-Parierstange |
| Flüsterklinge der Leere | Haupthand | Dolch | Schaden | Selten–Episch | Schlanker violetter Dolch mit Mundgravur |
| Stilett des stummen Chors | Haupthand | Dolch | Schaden | Episch–Legendär | Graues Stilett mit zugenähtem Griff |
| Stachel des namenlosen Abgrunds | Haupthand | Dolch | Schaden | Legendär–Mythisch+ | Langer schwarzer Stachel mit Sternenspitze |
| Abgrundposten-Bogen | Haupthand | Bogen | Schaden | Gewöhnlich–Ungewöhnlich | Einfacher grauer Bogen |
| Treibgut-Bogen der Leere | Haupthand | Bogen | Schaden | Ungewöhnlich–Selten | Bogen aus zusammengebundenen fremden Hölzern |
| Riftsehnen-Bogen | Haupthand | Bogen | Schaden | Selten–Episch | Dunkler Bogen mit violett leuchtender Sehne |
| Spiegelbogen des Vael-Thorun | Haupthand | Bogen | Schaden | Episch–Legendär | Silberner Bogen mit spiegelnder Sehne |
| Augenbogen von Oruun | Haupthand | Bogen | Schaden | Episch–Legendär | Schwarzer Bogen mit einem violetten Auge am Griff |
| Bogen des fallenden Sterns | Haupthand | Bogen | Schaden | Legendär–Mythisch+ | Schwarzer Bogen, an dessen Enden Sterne glühen |

### Nebenhand

| Name | Slot | Typ | Grundwert | Rarität | Icon |
|---|---|---|---|---|---|
| Abgrundkiesel | Nebenhand | Artefakt | Heilstärke | Gewöhnlich–Ungewöhnlich | Glatter schwarzer Kiesel mit violettem Glimmen |
| Gefangene Abgrundmotte | Nebenhand | Artefakt | Heilstärke | Ungewöhnlich–Selten | Leuchtende Motte in einem Glasgefäß |
| Laterne des verzerrten Wanderers | Nebenhand | Artefakt | Schaden | Selten–Episch | Alte Laterne mit einer violetten Flamme |
| Sternengrab-Laterne | Nebenhand | Artefakt | Heilstärke | Selten–Episch | Kleine Laterne mit einem fahlen Stern |
| Stundenglas der Königin Ysmera | Nebenhand | Artefakt | Schaden | Episch–Legendär | Zerbrochene Sanduhr, deren Sand nach oben fließt |
| Herzsplitter des Abgrunds | Nebenhand | Artefakt | Heilstärke | Legendär–Mythisch+ | Schwebender violetter Kristall in Herzform, der langsam schlägt |
| Abgrundwächter-Schild | Nebenhand | Schild | Rüstung | Gewöhnlich–Ungewöhnlich | Runder grauer Schild |
| Abgrundpilger-Buckler | Nebenhand | Schild | HP | Gewöhnlich–Ungewöhnlich | Kleiner grauer Rundschild |
| Treibgut-Schild der Leere | Nebenhand | Schild | HP | Ungewöhnlich–Selten | Schild aus einem fremden Mauerstück |
| Obsidianwall der Leere | Nebenhand | Schild | HP | Selten–Episch | Schwarzer Turmschild mit violettem Rand |
| Kieferschild des Mahlkiefers | Nebenhand | Schild | Rüstung | Episch–Legendär | Runder Schild mit Zahnreihen am Rand |
| Spiegelwall des Spiegelfürsten | Nebenhand | Schild | Rüstung | Legendär–Mythisch+ | Großer Schild aus spiegelndem Glas mit Rissen |
| Trübe Abgrundkugel | Nebenhand | Zauberkugel | Schaden | Gewöhnlich–Ungewöhnlich | Graue Kugel mit wirbelndem Nebel |
| Mottenlicht-Kugel des Abgrunds | Nebenhand | Zauberkugel | Schaden | Ungewöhnlich–Selten | Kugel mit flatternden Lichtmotten |
| Sternengrab-Kugel | Nebenhand | Zauberkugel | Schaden | Selten–Episch | Schwarze Kugel mit erlöschenden Sternen |
| Spiegelkugel des Spiegelschlunds | Nebenhand | Zauberkugel | Heilstärke | Episch–Legendär | Spiegelnde Kugel, die den Betrachter verzerrt zeigt |
| Kugel des tausendäugigen Abgrunds | Nebenhand | Zauberkugel | Heilstärke | Legendär–Mythisch+ | Kugel, auf der sich viele kleine Augen öffnen |
| Herzschlagkugel von Nhal'Zeroth | Nebenhand | Zauberkugel | Schaden | Legendär–Mythisch+ | Schwarze Kugel mit schlagendem violettem Kern |
| Zerfleddertes Abgrundbuch | Nebenhand | Grimoire | Schaden | Gewöhnlich–Ungewöhnlich | Graues Buch mit ausgerissenen Seiten |
| Rissgebundenes Abgrundbuch | Nebenhand | Grimoire | Schaden | Ungewöhnlich–Selten | Buch mit violett leuchtendem Riss im Einband |
| Mottenbuch der Leere | Nebenhand | Grimoire | Heilstärke | Ungewöhnlich–Selten | Graues Buch, aus dem Motten flattern |
| Kodex des stummen Chors | Nebenhand | Grimoire | Schaden | Selten–Episch | Zugenähtes Buch mit violetten Fäden |
| Stundenbuch der Königin Ysmera | Nebenhand | Grimoire | Schaden | Episch–Legendär | Goldenes Buch mit Uhrzeigern auf dem Deckel |
| Foliant der namenlosen Leere | Nebenhand | Grimoire | Schaden | Legendär–Mythisch+ | Schwarzer Foliant mit leeren Seiten, die violett leuchten |
| Abgrund-Götzenfigur | Nebenhand | Götze | Schaden | Gewöhnlich–Ungewöhnlich | Kleine graue Figur ohne Gesicht |
| Treibgut-Idol der Leere | Nebenhand | Götze | Heilstärke | Ungewöhnlich–Selten | Kleine Figur aus fremdem Stein |
| Motten-Idol der Leere | Nebenhand | Götze | Heilstärke | Selten–Episch | Violette Mottenfigur mit leuchtenden Flügeln |
| Chorgötze des stummen Abgrunds | Nebenhand | Götze | Schaden | Selten–Episch | Drei kleine graue Figuren mit zugenähten Mündern |
| Augengötze von Oruun | Nebenhand | Götze | Schaden | Episch–Legendär | Schwarze Figur mit einem großen violetten Auge |
| Götze des schlagenden Abgrunds | Nebenhand | Götze | Schaden | Legendär–Mythisch+ | Schwarze Figur mit pulsierendem Herz |
| Abgrundköcher | Nebenhand | Köcher | Schaden | Gewöhnlich–Ungewöhnlich | Grauer Lederköcher |
| Abgrundpilger-Köcher | Nebenhand | Köcher | Schaden | Gewöhnlich–Ungewöhnlich | Schlichter grauer Köcher |
| Treibgut-Köcher der Riftwacht | Nebenhand | Köcher | Schaden | Ungewöhnlich–Selten | Köcher aus fremdem Leder mit Steinpfeilen |
| Riftfeder-Köcher | Nebenhand | Köcher | Schaden | Selten–Episch | Violetter Köcher mit schimmernden Pfeilen |
| Spiegelköcher des Vael-Thorun | Nebenhand | Köcher | Schaden | Episch–Legendär | Silberner Köcher mit Pfeilen aus Glas |
| Köcher der Sternenjagd | Nebenhand | Köcher | Schaden | Legendär–Mythisch+ | Schwarzer Köcher mit Pfeilen aus Sternenlicht |
| Abgrundsplitter-Parierdolch | Nebenhand | Nebenhand-Dolch | Schaden | Gewöhnlich–Ungewöhnlich | Kleiner grauer Parierdolch |
| Mottenstachel der Leere | Nebenhand | Nebenhand-Dolch | Schaden | Ungewöhnlich–Selten | Dünne Klinge mit Mottenflügelgriff |
| Nichtshund-Zahn | Nebenhand | Nebenhand-Dolch | Schaden | Selten–Episch | Weißer Zahn mit Rauchgriff |
| Stundenzeiger der Königin Ysmera | Nebenhand | Nebenhand-Dolch | Schaden | Episch–Legendär | Klinge in Form eines goldenen Uhrzeigers |
| Kieferklinge des Mahlkiefers | Nebenhand | Nebenhand-Dolch | Schaden | Episch–Legendär | Gezackte Klinge aus einem Zahn |
| Riss des Abgrundherrn | Nebenhand | Nebenhand-Dolch | Schaden | Legendär–Mythisch+ | Klinge aus einem erstarrten violetten Riss |
