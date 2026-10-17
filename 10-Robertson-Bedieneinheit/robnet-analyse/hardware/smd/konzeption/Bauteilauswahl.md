# Bauteilauswahl Robnet-Analyse – Linie B (SMD, von JLCPCB bestückt)

Version 00.19, Stand 17.10.2026, Obergrenze 200 Zeilen. Platine fertig, bei JLCPCB bestellt (17.10.2026). Grundlage: Konzept `../../konzeption/robnet-analyse.md`,
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
- **Bauformen** (größer vor kleiner, Reparatur): Kondensatoren 1206; Widerstände 0805, weil 13 kΩ, 8,2 kΩ, 180 kΩ in 1206
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
**Platine** (Ablauf, Schritt 3, 16.10.2026): `../kicad/v00.01/Robnet-Analyse.kicad_pcb`. Lage und Aufdruck: `platine_erzeugen/robnet_platine.py` → Zwischendatei
`platine_erzeugen/Robnet-Analyse_platziert.kicad_pcb`; Bahnen: `bahnen_erzeugen/robnet_bahnen.py` liest sie und schreibt die Platine
(bricht ab, wenn in KiCad Teile verschoben oder Bahnen gezeichnet wurden; nach geprüfter Lageänderung im Skript `--neue-lage --ueberschreiben`).
100 × 100 mm, 2 Lagen (günstigste Stufe: „$2 for 5pcs, 2-layer, ≤ 10cmx10cm“, jlcpcb.com/help/article/how-do-i-place-an-order,
Stand 09.09.2026). J1 oben rechts genau über J3 unten rechts (Klemmenfolge gespiegelt, Adern kreuzen sich beim Routing);
Jumper JP3–JP7 senkrecht unter ihren J1-Klemmen (Masse „fest“), Klemmen und Jumper mit Nummer und Name; JP2/JP1 je
Stiftreihe beschriftet, daneben Bildtabelle der Stellungen A–E und „nie quer“ (`Jumper_JP1_JP2.html`); J2 und Versorgung oben links; Zero links, 8 mm hochgesetzt; M3-Löcher in allen vier Ecken (alles Betreiber,
16.10.2026). U1, C1 vom Betreiber in KiCad verschoben, ins Skript übernommen. SMD nur oben, ≥ 2,5 mm vom Rand (Skript). DRC: Schaltplanabgleich 0,
keine Hof- oder Aufdrucküberlappung.
**Leiterbahnen** (Ablauf, Schritt 3, Punkt 7; gruppenweise, je Gruppe freigegeben): Gruppe 1 fertig: 12 V (1,0 mm), 5 V (1,5 mm, außen herum,
damit die Mitte für SPI frei bleibt), 3,3 V (unten, je BAT54S eine Durchkontaktierung, weil die Messleitung oben unter der Diode durchläuft),
Massefläche unten (Abstand 0,2 mm, damit sie zwischen die Stifte des Zero reicht), SMD-Massepads je mit Durchkontaktierung.
Gruppe 2 fertig (Adern J1 → Jumper → J3, dazu Teiler-Eingänge, JP2, J4, R23, Bordspannung zu R21): Seite J300 über J1 hinweg nach links und
in einer Gasse zwischen U2/U6 und den Teilern hinunter; Seite Bedieneinheit rechts am Rand hinunter und in ineinanderliegenden Bögen unter J3 durch
(gespiegelte Klemmenfolge ohne Kreuzung; Vsys dadurch lang, 1,5 mm, Strom der Bedieneinheit nicht gemessen – vom Betreiber
so angenommen, 16.10.2026); 11 Durchkontaktierungen für Kreuzungen und Wege unten (JP2, J4, R23, R21). Dafür (Betreiber, 16.10.2026):
R31–R39 um 180° gedreht (Ader außen), Kanalzeilen von unten nach oben in Kanalfolge (CH0 unten wie an U2/U6). Gruppe 3 fertig: Messleitungen oben kurz (R – BAT54S – R), dann je eine Durchkontaktierung und unten ohne Kreuzung zum Wandlerpin;
Referenz unten zu U2/U6; Alarm zum Zero unten rechts an U1 vorbei, unter U6 durch, links hinauf in Pin 13 (daneben frei für die
Empfängerleitung: unten y 86,9, oben x 30,2 zu Pin 10). Massefläche ein Stück (geprüft).
Gruppe 4 fertig: SPI unten waagerecht aus der Stiftleiste, je Ast eine Durchkontaktierung 0,5 mm, oben zu U2 hinauf und zu U6
hinunter (Pinfolge am Zero umgekehrt zu den Wandlern, so ohne Kreuzung); 7 Durchkontaktierungen.
Gruppe 5 fertig: JP2 → R1/R2 → JP1 (Kreuzung Bus+ unten, Bus− oben), A und B zu U1, Empfängerleitung zum Zero Pin 10 und 16.
**Stand:** 79 Durchkontaktierungen, keine offene Verbindung, DRC ohne Meldung (Aufdruck von J1–J3 und Zero an der Kante gewollt: Regel
`Robnet-Analyse.kicad_dru`, vom Platzierungsskript geschrieben; Betreiber, 16.10.2026), Abgleich 0,
Massefläche ein Stück. Ablauf Schritt 3 abgeschlossen (16.10.2026).
**Fertigungsdateien** (Schritt 4, 16.10.2026): `../kicad/v00.01/production/` (Gerber-ZIP, `bom.csv`, `positions.csv`) mit Fabrication Toolkit 5.3.1,
geprüft mit `pruefung_fertigung.py` (49 Teile, 0 Fehler); selbst gelötete Teile (18) in Schaltplan und Platine aus den Listen genommen.
Beschaffung: `../bom/bom_tht_beschaffung.csv` (2 Platinen), `../bom/bom_zubehoer.csv`.
**Bestellt** (Schritt 5 und 6, 17.10.2026, Betreiber): Auftrag W2026101717094445 – Platinen Y23-3620191A (5 Stück, 1,6 mm, grün, HASL mit Blei),
Bestückung SMT026101760935-3620191A (2 Stück, Economic, oben); Dateien `../kicad/v00.01/production/` (Stand Commit 1e8e63b). Geprüft: 12 Zeilen = `../bom/bom.csv`;
SMCJ18CA, BAT54S, 13 kΩ, 180 kΩ als „Extended“ angezeigt, aber keine Extended-Gebühr (= Preferred). Vorschau: BAT54S-Punkt auf Aufdruck-Dreieck,
D1-Ring auf Kathodenseite, D2 zweiseitig → Drehungen richtig. Bezahlt 38,27 € (Ware 16,17, Versand 10,67, Steuer und Zoll 11,43; Gutschein nicht
abgezogen); Versand „Global Standard Direct Line“ (Steuer und Zoll an der Kasse bezahlt, 9–13 Werktage). Weiter: Empfang und Prüfung (Schritt 6).

## 4. Offen
- Nichts offen (Platinengröße 100 × 100 mm erledigt, Abschnitt 3).
