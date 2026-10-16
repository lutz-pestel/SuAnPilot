# Bauteilauswahl Robnet-Analyse – Linie B (SMD, von JLCPCB bestückt)

Version 00.02, Stand 16.10.2026, Obergrenze 200 Zeilen. **Nicht begonnen.** Grundlage: Konzept `../../konzeption/robnet-analyse.md`,
Linie A (THT, selbst gelötet) in `../../tht/`. Gleicher Ordneraufbau wie `tht/`: `konzeption/`, `kicad/vNN.NN/`, `bom/`,
`datenblaetter/`, `3d-modelle/`. Allgemeine Regeln für beide Linien: `0-gesamtprojekt/fertigung/fertigungsstrategie-platinen.md`
(Linien), `jlcpcb-bestueckungsregeln.md` (Regeln und Preise von JLCPCB), `ablauf-smd-bestueckung.md` (sechs Schritte) und
`bauteilauswahl-standard.md` (Schritte je Teil), alle in `0-gesamtprojekt/fertigung/`; hier nur, was für die SMD-Fassung
der Robnet-Analyse gilt.

## 1. Ziel
Platine mit gleicher Schaltung wie Linie A, **automatisch von JLCPCB bestückt** (Betreiber, 16.10.2026): möglichst wenig
Handarbeit, keine selbst gelöteten SMD-Teile. Elektrische Abweichungen von Linie A nur, wenn SMD etwas ermöglicht, das in THT
nicht ging (Fertigungsstrategie, Abschnitt 1).

## 2. Regeln für die automatische Bestückung
1. **Jedes bestückte Teil hat eine LCSC-Nummer** (JLCPCB-Teilenummer), eingetragen im Schaltplan als Feld „LCSC Part #“,
   geprüft im JLCPCB-Katalog (nicht aus dem Gedächtnis) mit Klasse, Lager und Datum.
2. **Nur Basic und Preferred:** Extended nur, wenn es nicht anders geht und der Betreiber es freigegeben hat; Grund und
   Freigabe in `bom/bom.csv`, Spalte Abweichung (Regeln, Abschnitt 6). Gilt auch für J1–J3, Buchsenleisten und die 40-polige Buchse.
3. **Lager reicht** für die Bestellmenge plus Reserve; Teile ohne Lager sind nur Vorbestellung und werden nicht gewählt.
4. **Bauform nach Datenblatt** des tatsächlich gelieferten Herstellers (siehe `0-gesamtprojekt/CHRONIK.md`, 15.10.2026);
   KiCad-Standardbauform nur, wenn sie zum JLCPCB-Gehäuse passt.
5. **Alle SMD-Teile auf einer Seite (oben)**, damit die einseitige, günstigere Bestückung reicht.
6. **Bleibt THT** (Steckverbinder J1–J3, Jumper-Stiftleisten, J4, Buchsenleiste des Zero, Sicherungshalter): je Teil in
   `bom/bom.csv` begründen. JLCPCB lötet Durchsteckteile mit, wenn sie im Katalog stehen (Regeln, Abschnitt 5); sonst selbst.
7. **Drehung prüfen:** in der Vorschau von JLCPCB, SMD in 2D, Durchsteckteile in 3D (Ablauf, Schritt 5).
8. **Fertigungsdaten** (Gerber, Stückliste, Positionsliste) erst nach Freigabe des Betreibers; bestellen nur der Betreiber.
9. **Fassungen für MAX3488 und MCP3208:** offen; Entscheidung nach Vorlage aller Daten, THT-Fassung ausdrücklich möglich
   (Ablauf, Schritt 1).

## 3. Ausgangspunkt
Die SMD-Gegenstücke aus der Teilesuche vom 15.10.2026 stehen in `../../tht/bom/bom.csv` (Spalten „SMD-Gegenstück“,
„LCSC SMD“): MAX3488ESA-TUDI (C53286186, Extended), MCP3208T-CI/SL (C626764, Extended); übrige Teile ungeprüft.
Beim Start eine eigene `bom/bom.csv` anlegen und das KiCad-Projekt unter `kicad/v00.01/` als Kopie des Linie-A-Schaltplans
(gleiche Netze, SMD-Bauformen).

## 4. Offen
- Machbarkeitsprüfung (Ablauf, Schritt 1): je Block Basic/Preferred-Teil suchen; MAX3488 und MCP3208 sind Extended.
- Fassungsfrage MAX3488 und MCP3208 (Regel 9).
- Kleinste Bauform (0603 oder 0805) mit dem Betreiber festlegen.
- Randabstand: Regel 2,5 mm (Regeln, Abschnitt 3); Zero darf bündig bleiben (nicht von JLCPCB
  bestückt), seine 40-polige Buchse liegt in Linie A ~7,7 mm vom Rand. Offen: J1–J3 (heute bündig), U1 und JP1 (~2,5 mm).
