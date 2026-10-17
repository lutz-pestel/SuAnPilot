# JLCPCB-Bestückungsregeln (SMT-Bestückung, gilt für alle Platinen)

Version 00.02, Stand 17.10.2026, Obergrenze 150 Zeilen. Gilt für jede Platine, die JLCPCB bestückt (Robnet-Analyse Linie B,
Motor-Controller, SuAnPilot). Ablauf dazu: `ablauf-smd-bestueckung.md`; Strategie: `fertigungsstrategie-platinen.md`.
**Alle Werte am 16.10.2026 auf den genannten JLCPCB-Seiten selbst gelesen** (Seitentext, keine Suchtreffer-Zusammenfassung).
Die Hilfeartikel tragen „Last updated on Sep 09, 2026“. Preise und Regeln ändern sich: vor jeder Bestellung neu prüfen.

Quellen (Kürzel in eckigen Klammern):
- [F] Fähigkeiten: https://jlcpcb.com/capabilities/pcb-assembly-capabilities (ohne Datum)
- [P] Preise: https://jlcpcb.com/help/article/pcb-assembly-price
- [Q1] FAQ: https://jlcpcb.com/help/article/pcb-assembly-faqs · [Q2] FAQ Teil 2: https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2
- [B] Montagebedingungen: https://jlcpcb.com/help/article/Terms-and-Conditions-of-JLCPCB-Assembly-Service
- [A] SMD-Mindestabstände: https://jlcpcb.com/help/article/minimum-spacing-for-smd-components
- [R] Rand und Passmarken: https://jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order
- [D] Stückliste/Positionsliste: https://jlcpcb.com/help/article/advice-for-bom-and-cpl-files-preparation,
  https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly
- [K] KiCad-Export: https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad
- [Z] Zusatzleistungen: https://jlcpcb.com/help/article/jlcpcb-supported-personalized-services
- [T] Teilebeschaffung: https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction ·
  [S] Konsignation: https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb

## 1. Economic oder Standard [F]
| | Economic (günstig) | Standard |
|---|---|---|
| Bestückte Seiten | nur eine (SMT und Durchsteckteile) | eine oder beide |
| Lagen, Dicke | 2, 4, 6 Lagen; 0,8–1,6 mm | 1–32 Lagen; frei |
| Einzelplatine | 10 × 10 bis 470 × 500 mm | 70 × 70 bis 460 × 500 mm |
| Nutzen (mehrere Platinen in einem Rahmen) | bis 250 × 250 mm, nur mit Stegen („mouse bites“) | bis 250 × 250 mm, Stege oder Ritzung (V-Cut) |
| Stückzahl | 2–50 | 2–80 000 |
| Transportrand, Passmarken | nicht nötig | nötig |
| Kleinste Bauform | 0402 | 0201 |
| Kleinstes IC-Raster | 0,4 mm | 0,35 mm |
| Lötofen | 255 ± 5 °C, fest | 240 ± 5 °C |
| Pastenprüfung (SPI), Bildprüfung (AOI) | nein, ja | ja, ja |
| Bauzeit Bestückung | 1–3 Tage | ab 4 Tage |
Economic-Platinen: z. B. 2 Lagen, 1,6 mm, grün, HASL bleifrei, 2–50 Stück; andere Farben teils erst ab 5 Stück [F].
Economic-Aufträge verschiedener Kunden werden gemeinsam gefertigt; bestellt man mehr Platinen als Bestückungen, können die
unbestückten verzinnt zurückkommen [B]. JLCPCB bestückt nur selbst gefertigte Platinen [Q1].

## 2. Preise [P]
| Posten | Economic | Standard |
|---|---|---|
| Einrichtung | 8,18 $ | 25,56 $ einseitig, 51,12 $ beidseitig |
| Schablone (Lötpaste, wird nicht mitgeliefert) | 1,53 $ | 8,21 $ einseitig, 16,42 $ beidseitig |
| SMT-Lötstelle | 0,0016 $ | 0,0016 $ (bis 50 000) |
| Handbestückung je Lötstelle (bis 10 000) | 0,0164 $ | 0,0164 $ |
| Handlöt-Arbeit | 3,58 $ je Auftrag | 3,58 $ je Auftrag |
| Ladegebühr je Teilesorte | 3,07 $ nur Extended | 1,53 $ Basic und Extended |
| „Confirm Parts Placement“ | 0,45 $ | 0,45 $ |
| Nutzen mit mehreren Entwürfen | 8,21 $ | 8,21 $ |
| Verpackung | frei | 0,50 $ + 0,00003 $ × Fläche (cm²) |
| Röntgen (nur BGA, QFN u. ä.) | 1–10 Stück: 1,64 $ je Teil | wie Economic |
Ältere Preise in [Q1] (8,00 $, 1,50 $, 0,0017 $, 3,5 $, 0,0173 $, „$3 per extended component“) sind überholt; es gilt [P].

## 3. Abstände
- **Bauteil–Bauteil** [A], gemessen von Außenkante Lötfläche zu Außenkante Lötfläche (Bild in [A]), Auszug in mm:
  | | 0603 | 0805 | 1206 | SOT | SOIC | QFN |
  |---|---|---|---|---|---|---|
  | 0603 | 0,18 | 0,18 | 0,25 | 0,2 | 0,4 | 1,0 |
  | 0805 | | 0,18 | 0,25 | 0,2 | 0,4 | 1,0 |
  | SOT | | | | 0,4 | 0,4 | 1,0 |
  | SOIC | | | | | 0,5 | 1,0 |
- Bauformen und Abstände nach IPC-7351B (Norm für Lötflächen), Dichte „medium“ oder „low“; „high“ wird nicht unterstützt [B].
- Bezeichner in der Positionsliste mindestens 0,2 mm auseinander [D].
- **Bauteil–Platinenrand: Widerspruch.** [B]: Bauteilkörper mindestens 2,5 mm vom Rand. [Q2] für Economic: Bahnen und
  Bauteile mehr als 0,3 mm vom Rand (Fräs-Toleranz beim Trennen etwa 0,2 mm). **Unsere Regel (Betreiber, 16.10.2026): immer
  2,5 mm** für jedes Teil, das JLCPCB bestückt (selbst gesteckte Teile wie der Zero dürfen bündig sitzen); näher nur nach schriftlicher Bestätigung durch JLCPCB, festgehalten in der Bauteilauswahl der Platine.

## 4. Transportrand und Passmarken
- Economic: beides nicht nötig [F]; JLCPCB setzt Passmarken selbst [Q1]. Standard: beides nötig [F]; fehlt es, ergänzt
  JLCPCB es [B]. Bestückte Platinen kommen mit Transportrand; Abtrennen auf Wunsch gegen Gebühr [F], [R].
- Maße, wenn wir sie selbst setzen [R]: Transportrand mindestens 5 mm breit. Passmarke: runde Kupferfläche ohne Bohrung,
  1 mm Durchmesser, Lackfreistellung doppelt so groß, 3–4 Stück am Rand, mindestens 3,35 mm vom Rand (mit Freistellung).

## 5. Durchsteckteile (THT)
- JLCPCB bestückt Durchsteckteile und gemischte Platinen (SMD + THT) in einem Auftrag, bei Economic und Standard [F].
- Löten: SMD im Ofen, Durchsteckteile mit Welle [F]; Teile mit Montageart „wave soldering“ im Katalog werden von Hand
  bestückt [Q1]. Kosten: Handlöt-Arbeit und Handbestückung je Lötstelle (Abschnitt 2).
- Unbenutzte Löcher bleiben frei von Lot; dort können wir später selbst bestücken [F].
- Prüfung der Lage: SMD in der 2D-, Durchsteckteile in der 3D-Fertigungsansicht [B].
- Zusatzleistungen [Z]: Teile nur stecken ohne Löten (z. B. Jumper-Kappen) ab 0,03 $ je Teil. Nachträglich ergänzte
  Durchsteckteile 7,88 $ + 0,0157 $ je Lötstelle. IC auf Fassung: beide in Stückliste und Positionsliste, Koordinate des
  ICs mehr als 0,2 mm neben der Fassung, Hinweis im Auftrag, Handarbeit gegen Aufpreis [F].
- Unbestückte Teile werden nicht mitgeschickt (Zoll) [Q2].

## 6. Teileklassen (unsere Regel und JLCPCB)
- **Basic:** liegt fest in der Maschine, ohne Ladegebühr [Q1].
- **Preferred Extended:** früher Basic; bei Economic ohne Ladegebühr [Q1].
- **Extended:** Rolle wird von Hand eingelegt, Ladegebühr je Teilesorte (Abschnitt 2).
- **Unsere Regel (Betreiber, 16.10.2026):** Nur Basic und Preferred. Extended nur, wenn es nachweislich nicht anders geht
  **und** der Betreiber es freigegeben hat; Grund und Freigabe (Datum) in `bom/bom.csv` der Platine. Gilt auch für
  Stecker, Klemmen, Buchsenleisten und Fassungen.
- Lager des JLCPCB-Katalogs kann von LCSC abweichen (zwei Lager) [Q2]; nur der JLCPCB-Katalog zählt.

## 7. Teilebeschaffung [T], [S]
- Wege: öffentlicher Katalog, „Global Sourcing“ (weltweit beschafft, 9–15 Tage), Vorbestellung (erst nach Eingang nutzbar),
  Konsignation (eigene Teile), Antrag auf neues Teil [T].
- **Konsignation aus Deutschland** [S]: Teile werden an JLCPCB verkauft (Lager Hongkong); Zoll und 13 % Einfuhr-MwSt als
  Pfand, Bearbeitung 2 % des Werts, mindestens 10 $ je Sendung; 3 Jahre kostenlos gelagert, danach verfallen; Rückholung
  30 % des Werts, mindestens 30 $. JLCPCB prüft mitgeschickte Teile nicht [B]. **Folgerung: nicht nutzen**, außer der
  Betreiber entscheidet es für ein bestimmtes Teil.

## 8. Stückliste (BOM) und Positionsliste (CPL) [D], [K]
- Stückliste: .csv, .xls oder .xlsx; Spalten Comment (Wert), Designator (Bezeichner), Footprint (Bauform), LCSC Part #.
  Höchstens 200 Bezeichner je Zeile, jeder Bezeichner nur einmal. R für Widerstände, C für Kondensatoren.
- Positionsliste: Designator, Mid X, Mid Y, Rotation, Layer; Millimeter; Ober- und Unterseite in einer Datei (T/B).
- Bezeichner in beiden Listen gleich, auch Groß-/Kleinschreibung; nur Teile in beiden Listen werden erkannt.
- KiCad 10: Zusatzprogramm „Fabrication Toolkit“ (bennymeg, Plugin-Manager) erzeugt Gerber, `bom.csv` und
  `positions.csv` im JLCPCB-Format; Einstellung „Apply automatic component translations“ korrigiert Drehungen [K].

## 9. Drehung und Polung [Q2]
- Roter Punkt in der Vorschau = Lagemarke des Teils; richtig, wenn er auf der Markierung im Aufdruck liegt.
  Bei Dioden: „+“ Anode, „−“ Kathode.
- 0 Grad einer Bauform = Lage des Teils im Gurt (Datenblatt „Tape and Reel“ des Herstellers, teils je Teilenummer anders).
- Falsche Drehung: in der Positionsliste ändern, oder JLCPCB richtet nach dem Aufdruck aus. Widerspricht der Aufdruck der
  Positionsliste, gilt der Aufdruck. Ohne Polungsmarke im Aufdruck fragt JLCPCB per E-Mail nach (Verzögerung).
- Nur bestätigte Teile werden bestückt. Zahlung sofort (Geld zurück, wenn die Prüfung scheitert) oder „Review Before Payment“ (Kasse, 17.10.2026).

## 10. Mängel [B]
Reklamation nur innerhalb von drei Monaten nach Erhalt; ersetzt wird auf Grundlage des Lötpreises, nicht die ganze Platine.

## 11. EasyEDA statt KiCad – geprüft, nicht gewählt
EasyEDA Pro (Online-Programm von JLCPCB) lädt Gerber selbst hoch und öffnet die Bestellseite
(https://prodocs.easyeda.com/en/pcb/order-order-pcb/). Seine JLCPCB-Teilewahl wird nicht im Projekt gespeichert
(https://prodocs.easyeda.com/en/pcb/tools-jlcpcb-smt-part-selection-tool/). Import aus KiCad nur für 5.1 und 5.9 genannt
(https://prodocs.easyeda.com/en/import-export/import-kicad/), wir nutzen KiCad 10. Stückliste und Positionsliste werden wie
bei KiCad ausgegeben (https://jlcpcb.com/help/article/how-to-generate-the-bom-and-pick&place-file-from-easyeda).
Kein belegter Vorteil, der einen Wechsel rechtfertigt: **es bleibt bei KiCad.**
