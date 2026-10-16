# Bauteilauswahl Robnet-Analyse – Linie B (SMD, von JLCPCB bestückt)

Version 00.01, Stand 16.10.2026, Obergrenze 200 Zeilen. **Nicht begonnen.** Grundlage: Konzept `../../konzeption/robnet-analyse.md`,
Linie A (THT, selbst gelötet) in `../../tht/`. Gleicher Ordneraufbau wie `tht/`: `konzeption/`, `kicad/vNN.NN/`, `bom/`,
`datenblaetter/`, `3d-modelle/`. Allgemeine Regeln für beide Linien: `0-gesamtprojekt/fertigung/fertigungsstrategie-platinen.md`
(Linien, JLCPCB-Preise, Ablauf) und `0-gesamtprojekt/fertigung/bauteilauswahl-standard.md` (Schritte je Teil); hier nur, was für
die SMD-Fassung der Robnet-Analyse gilt.

## 1. Ziel
Platine mit gleicher Schaltung wie Linie A, **automatisch von JLCPCB bestückt** (Betreiber, 16.10.2026): möglichst wenig
Handarbeit, keine selbst gelöteten SMD-Teile. Elektrische Abweichungen von Linie A nur, wenn SMD etwas ermöglicht, das in THT
nicht ging (Fertigungsstrategie, Abschnitt 1).

## 2. Regeln für die automatische Bestückung
1. **Jedes bestückte Teil hat eine LCSC-Nummer** (JLCPCB-Teilenummer), eingetragen im Schaltplan als Feld „LCSC Part #“,
   geprüft im JLCPCB-Katalog (nicht aus dem Gedächtnis) mit Klasse, Lager und Datum.
2. **Basic vor Extended:** Widerstände und Kondensatoren nur als Basic-Teile; jedes Extended-Teil kostet einen Aufschlag je
   Teilesorte. Extended nur, wo es keine Basic-Alternative gibt; Grund in `bom/bom.csv`, Spalte Abweichung.
3. **Lager reicht** für die Bestellmenge plus Reserve; Teile ohne Lager sind nur Vorbestellung und werden nicht gewählt.
4. **Bauform nach Datenblatt** des tatsächlich gelieferten Herstellers (siehe `0-gesamtprojekt/CHRONIK.md`, 15.10.2026);
   KiCad-Standardbauform nur, wenn sie zum JLCPCB-Gehäuse passt.
5. **Alle SMD-Teile auf einer Seite (oben)**, damit die einseitige, günstigere Bestückung reicht.
6. **Bleibt THT** (Steckverbinder J1–J3, Jumper-Stiftleisten, J4, Buchsenleiste des Zero, Sicherungshalter): je Teil in
   `bom/bom.csv` begründen. Offen: ob JLCPCB diese Teile mitbestückt oder sie von Hand gelötet werden (Fertigungsstrategie,
   Abschnitt 9) – vor der Teilewahl klären.
7. **Drehung prüfen:** In der Vorschau von JLCPCB jedes Teil mit Pin 1 gegen die Platine prüfen, bevor bestellt wird.
8. **Fertigungsdaten** (Gerber, Stückliste, Positionsliste) erst nach Freigabe des Betreibers; bestellen nur der Betreiber.
9. **Sockel entfallen** (MAX3488, MCP3208 gelötet); Ersatz nur durch Tausch der Platine – mit dem Betreiber klären.

## 3. Ausgangspunkt
Die SMD-Gegenstücke aus der Teilesuche vom 15.10.2026 stehen in `../../tht/bom/bom.csv` (Spalten „SMD-Gegenstück“,
„LCSC SMD“): MAX3488ESA-TUDI (C53286186, Extended), MCP3208T-CI/SL (C626764, Extended); übrige Teile ungeprüft.
Beim Start eine eigene `bom/bom.csv` anlegen und das KiCad-Projekt unter `kicad/v00.01/` als Kopie des Linie-A-Schaltplans
(gleiche Netze, SMD-Bauformen).

## 4. Offen
- THT-Bestückung bei JLCPCB: möglich und zu welchem Preis (Regel 6).
- Kleinste Bauform (0603 oder 0805) mit dem Betreiber festlegen.
