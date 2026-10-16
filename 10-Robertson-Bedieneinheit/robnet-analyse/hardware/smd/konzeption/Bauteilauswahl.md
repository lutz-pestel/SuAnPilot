# Bauteilauswahl Robnet-Analyse – Linie B (SMD, von JLCPCB bestückt)

Version 00.10, Stand 16.10.2026, Obergrenze 200 Zeilen. Teilewahl und Schaltplan fertig, Platine platziert (ohne Leiterbahnen). Grundlage: Konzept `../../konzeption/robnet-analyse.md`,
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
6. **THT nur, was der Betreiber lötet** (Regel 10); JLCPCB lötet nichts von Hand. Grund je Teil in `bom/bom.csv`.
7. **Drehung prüfen:** in der Vorschau von JLCPCB, SMD in 2D, Durchsteckteile in 3D (Ablauf, Schritt 5).
8. **Fertigungsdaten** (Gerber, Stückliste, Positionsliste) erst nach Freigabe des Betreibers; bestellen nur der Betreiber.
9. **Keine Extended-Teile** (Betreiber, 16.10.2026): JLCPCB bestückt nur Basic und Preferred. Fassungen (alle im Katalog
   Extended) und Zero-Buchse sind THT vom Betreiber: Fassungen DIP-8 (U1) und 2 × DIP-16 (U2, U6), Buchsenleiste 2 × 20;
   die DIP-Chips (MAX3488EEPA, MCP3208-CI/P wie Linie A) steckt er – Chips bleiben tauschbar. Mehr Lötaugen auf beiden
   Lagen erschweren das Routing (Ablauf, Schritt 3).
10. **Beschafft und gelötet vom Betreiber** (16.10.2026), wie Linie A: Fassungen und Zero-Buchse (Regel 9), J1–J3 Phoenix
   MSTBA (SMD-Leisten 5,08 mm nicht am Lager), Jumper-Stiftleisten JP1–JP7, J4, Referenz LM4040 TO-92 (SMD ±0,1 % nur Extended), Regler R-78B (nicht im
   Katalog), Drahtbrücke im Drosselplatz. Nicht in den JLCPCB-Listen, Randregel gilt nicht.
11. **Schaltungsänderungen gegen Linie A** (nur Linie B, Betreiber 16.10.2026): Klemmdioden 12 × BAT54S statt 23 × BAT85;
   Verpolschutz SS54, Schutzdiode SMCJ18CA (klemmt 29,2 V statt 27,7 V; Grenze R-78B 32 V). **Sicherung, Halter und
   Anzeige-Leuchtdiode entfallen** (Sicherung sitzt in der Versorgungsleitung). **Filter ohne Drossel:** 4,7 µF – 0,5 Ω
   (2 × 1 Ω) – 2 × 10 µF; Recom R-78B (Datenblatt 5/2021) schlägt eine Drossel vor (3,3 µH Klasse A, 10 µH Klasse B);
   Dämpfung bei 460 kHz gerechnet ~29 statt ~840-fach. Platz für RLB0914 mit Drahtbrücke, nachrüstbar.

## 3. Machbarkeit (Ablauf, Schritt 1, 16.10.2026)
Alle 75 Bauteile des Linie-A-Schaltplans (Netzliste, per Skript) im JLCPCB-Katalog geprüft (Filter Basic/Preferred,
am Lager): machbar ohne Abstrich an der Funktion, ohne Extended; Ergebnis in `../bom/bom.csv`.
- **Bauformen** (größer vor kleiner, Reparatur): Kondensatoren 1206; Widerstände 0805, weil 18 kΩ, 8,2 kΩ, 180 kΩ in 1206
  nicht Basic/Preferred sind (andere Teilerwerte würden den Bus stärker belasten); Filterwiderstände 1206.
- **Datenblätter** (über LCSC, 16.10.2026): BAT54S (Hongjiacheng Rev 2.0) und BAT85S (Vishay Rev 2.0, 16.11.2021) je
  I_R max 2 µA bei 25 V, V_F bis 30 mA gleich (240–500 mV) → gleichwertig; Verschaltung Masse – Messpunkt – 3,3 V passt
  laut Netzliste. SMCJ18CA: 1500 W, V_RWM 18 V, V_C 29,2 V. SS54 (MDD): 40 V, 5 A, V_F 0,55 V bei 5 A.
  UNI-ROYAL-Widerstände: 0805 1/8 W, 1206 1/4 W (Filter: 0,06–0,17 W je Widerstand, gerechnet). Kondensatoren: Katalogwerte.
- **Kosten je Auftrag** (Preisseite und Katalog, gerechnet, ohne Platine und Versand): Einrichtung 8,18 $, Schablone 1,53 $,
  keine Ladegebühr; Teile ~1,2 $ und ~110 Lötstellen ~0,18 $ je Platine.
- **Zweiter Händler** entfällt für Teile, die JLCPCB bestückt (Betreiber, 16.10.2026); THT-Teile wie Linie A.
**Schaltplan** (Ablauf, Schritt 2, 16.10.2026): `../kicad/v00.01/`, erzeugt mit `schaltplan_erzeugen/robnet.py` (Kopie
Linie A mit Regel 11; dort ändern, nicht in KiCad); Feld „LCSC Part #“ an jedem JLCPCB-Teil; 67 Bauteile = `bom.csv`;
ERC 0 Meldungen, `pruefung_blockschaltbild.py` (für Linie B angepasst) 87 von 87; alle Blätter als Bild geprüft.
BAT54S-Anschlüsse aus der Datenblattzeichnung: 1 Anode, 2 Kathode, 3 Mitte = KiCad-Bibliothek.
**Platine** (Ablauf, Schritt 3, 16.10.2026): `../kicad/v00.01/Robnet-Analyse.kicad_pcb`, erzeugt mit `platine_erzeugen/robnet_platine.py`.
100 × 100 mm, 2 Lagen (günstigste Stufe: „$2 for 5pcs, 2-layer, ≤ 10cmx10cm“, jlcpcb.com/help/article/how-do-i-place-an-order,
Stand 09.09.2026). J1 oben rechts genau über J3 unten rechts (Klemmenfolge gespiegelt, Adern kreuzen sich beim Routing);
Jumper JP3–JP7 senkrecht unter ihren J1-Klemmen (Masse „fest“), Klemmen und Jumper mit Nummer und Name; JP2/JP1 je
Stiftreihe beschriftet, daneben Bildtabelle der Stellungen A–E und „nie quer“ (`Jumper_JP1_JP2.html`); J2 und Versorgung oben links; Zero links, 8 mm hochgesetzt; M3-Löcher in allen vier Ecken (alles Betreiber,
16.10.2026). U1, C1 vom Betreiber in KiCad verschoben, ins Skript übernommen. SMD nur oben, ≥ 2,5 mm vom Rand (Skript). DRC: Schaltplanabgleich 0,
keine Hof- oder Aufdrucküberlappung; nur Aufdruck J1–J3/Zero an der Kante (gewollt) und offene Verbindungen.
Nächster Schritt: Leiterbahnen (Ablauf, Schritt 3, Punkt 7).

## 4. Offen
- Platinengröße: ob ≤ 100 × 100 mm (heute 113,5 mm lang) die Leiterplatte verbilligt – Preisseite noch nicht gelesen.
