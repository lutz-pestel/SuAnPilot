# Bauteilauswahl Robnet-Analyse – Linie B (SMD, von JLCPCB bestückt)

Version 00.04, Stand 16.10.2026, Obergrenze 200 Zeilen. **Nicht begonnen.** Grundlage: Konzept `../../konzeption/robnet-analyse.md`,
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
6. **Bleibt THT** (J4, Buchsenleiste des Zero, Sicherungshalter; J1–J3 und Jumper-Stiftleisten siehe Regel 10): je Teil in
   `bom/bom.csv` begründen. JLCPCB lötet Durchsteckteile mit, wenn sie im Katalog stehen (Regeln, Abschnitt 5); sonst selbst.
7. **Drehung prüfen:** in der Vorschau von JLCPCB, SMD in 2D, Durchsteckteile in 3D (Ablauf, Schritt 5).
8. **Fertigungsdaten** (Gerber, Stückliste, Positionsliste) erst nach Freigabe des Betreibers; bestellen nur der Betreiber.
9. **SMD-Fassungen im DIP-Raster** für U1 (DIP-8) und U2, U6 (DIP-16), bestückt von JLCPCB; die DIP-Chips (MAX3488EEPA,
   MCP3208-CI/P wie Linie A) stecken wir selbst – Chips bleiben tauschbar. XKB X5621FVS-2x04 C2883643 (100 Stück, 0,31 $) und
   X5621FVS-2x08 C2689750 (1988 Stück, 0,62 $), Katalog 16.10.2026, **Extended, freigegeben vom Betreiber 16.10.2026**.
   Keine Fassung im Katalog ist Basic/Preferred; SOIC-Fassungen praktisch nicht lieferbar. 8-polige: Lager knapp, neu prüfen.
10. **J1–J3 Phoenix MSTBA wie Linie A und Jumper-Stiftleisten JP1–JP7, beschafft und gelötet vom Betreiber** (16.10.2026): nicht in den
   JLCPCB-Listen, Randregel gilt nicht. SMD-Steckleisten im Raster 5,08 mm hat der Katalog nicht auf Lager (16.10.2026).

## 3. Ausgangspunkt
Die SMD-Gegenstücke aus der Teilesuche vom 15.10.2026 stehen in `../../tht/bom/bom.csv` (Spalten „SMD-Gegenstück“,
„LCSC SMD“); MAX3488 und MCP3208 entfallen dort (DIP in Fassungen, Regel 9); übrige Teile ungeprüft.
Beim Start eine eigene `bom/bom.csv` anlegen und das KiCad-Projekt unter `kicad/v00.01/` als Kopie des Linie-A-Schaltplans
(gleiche Netze, SMD-Bauformen).

## 4. Offen
- Machbarkeitsprüfung (Ablauf, Schritt 1): je Block Basic/Preferred-Teil suchen.
- Fassungen (Regel 9): Datenblätter lesen (LCSC-Abruf gesperrt), zweiter Händler.
- J3 (Bedieneinheit) an die Unterkante verlegen (Betreiber, 16.10.2026, beide Linien; Ablauf, Schritt 3).
- Kleinste Bauform (0603 oder 0805) mit dem Betreiber festlegen.
- Randabstand: Regel 2,5 mm (Regeln, Abschnitt 3); Zero darf bündig bleiben (nicht von JLCPCB
  bestückt), seine 40-polige Buchse liegt in Linie A ~7,7 mm vom Rand. Offen: U1-Fassung (~2,5 mm).
