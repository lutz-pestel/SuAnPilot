# Ablauf: Platine mit SMD-Bestückung durch JLCPCB

Version 00.01, Stand 16.10.2026, Obergrenze 150 Zeilen. Gilt für jede Platine, die JLCPCB bestückt (Robnet-Analyse Linie B,
Motor-Controller, SuAnPilot). Regeln und Werte von JLCPCB: `jlcpcb-bestueckungsregeln.md` (Abschnittsnummern dort = „R“).
Teilewahl je Teil: `bauteilauswahl-standard.md`. Strategie (Linien A und B): `fertigungsstrategie-platinen.md`.
Mit dem Betreiber Schritt für Schritt festgelegt am 16.10.2026.

## Grundsätze
- Entworfen wird in **KiCad** (R 11), gefertigt und bestückt bei **JLCPCB**, Bestückungsart **Economic** (R 1), solange die
  Platine deren Grenzen einhält (eine Seite, 2–50 Stück, kleinste Bauform 0402).
- Die Schaltung der THT-Fassung (Linie A) bleibt möglichst gleich. Kompromisse wegen der Teile-Verfügbarkeit sind erlaubt,
  **die Funktion der Baugruppe nie.**
- **Extended nur mit Freigabe** des Betreibers, dokumentiert (R 6).
- Jeder Schritt endet mit einem Ergebnis, das dem Betreiber vorgelegt wird; der nächste Schritt beginnt erst nach Freigabe.
- Allgemeines steht hier, alles Platinen-Eigene in den Dateien der Platine (Tabelle am Ende).

## Schritt 1: Machbarkeit prüfen (vor dem Schaltplan oder kurz danach)
Ziel: wissen, ob die SMD-Platine mit Basic- und Preferred-Teilen gebaut werden kann, bevor Arbeit in Schaltplan und
Platine fließt.
1. Die Schaltung in Blöcke teilen (z. B. Bus-Empfänger, A/D-Wandler, Referenz, Versorgung, Stecker, Buchsenleisten).
2. Je Teil im **JLCPCB-Katalog** (nicht LCSC, nicht aus dem Gedächtnis) ein Gegenstück suchen: LCSC-Nummer, Klasse, Lager,
   Preis, Datum, dazu ein Ersatzteil; nach `bauteilauswahl-standard.md`.
3. Gibt es kein Basic/Preferred-Teil: eine andere Schaltung suchen, die dieselbe Funktion erfüllt. Erst wenn keine geht,
   das Extended-Teil mit Begründung dem Betreiber zur Freigabe vorlegen.
4. **Stecker, Klemmen, Buchsenleisten, Fassungen** gleich behandeln: Katalogteil mit Montageart „wave soldering“ suchen
   (JLCPCB lötet mit, R 5) oder ausdrücklich „selbst löten“.
5. **Fassungsfrage** für jedes IC, das tauschbar sein soll: alle Daten sammeln (Fassung SMD oder THT, IC in passender
   Bauform, je Katalognummer, Klasse, Lager, Preis; wer lötet und wer steckt; Kosten, Tauschbarkeit). Der Betreiber
   entscheidet nach Vorlage aller Daten; THT ist dabei eine ausdrückliche Möglichkeit.
6. Kleinste Bauform (0603 oder 0805) mit dem Betreiber festlegen.

Ergebnis: Liste Block – Teil – Klasse – Lager – Ersatzteil – „bestückt JLCPCB / selbst“ in `bom/bom.csv` der Platine,
offene Entscheidungen in ihrer Bauteilauswahl. **Ja oder Nein des Betreibers zur SMD-Fassung.**

## Schritt 2: Schaltplan
1. Schaltplan der Linie A nach `hardware/smd/kicad/vNN.NN/` kopieren; wird er per Skript erzeugt, im Skript ändern.
2. Freigegebene Änderungen aus Schritt 1 einarbeiten, jede mit Grund im Konzept der Baugruppe.
3. Je Teil: Feld **„LCSC Part #“**; Bauform nach dem Datenblatt des Herstellers, den JLCPCB liefert; Lage von Pin 1 und
   0-Grad-Lage im Gurt (R 9) prüfen.
4. Teile, die wir selbst stecken oder löten, im Schaltplan kennzeichnen (sie kommen nicht in die JLCPCB-Listen).
5. Prüfen: ERC (elektrische Regelprüfung) ohne Meldung, Prüfskript gegen das Blockschaltbild, Vergleich mit Linie A
   (jede Abweichung = freigegebene Änderung aus Schritt 1).

Ergebnis: geprüfter Schaltplan, jedes bestückte Teil mit LCSC-Nummer.

## Schritt 3: Platine
1. Ausgangspunkt ist die Platine der Linie A (Lage, Stecker); Bauformen auf SMD.
2. **Alle SMD-Teile auf die Oberseite** (Economic bestückt eine Seite, R 1).
3. Abstände nach R 3 (Tabelle Bauteil–Bauteil; IPC-7351B medium/low).
4. **Rand: immer 2,5 mm** vom Körper jedes von JLCPCB bestückten Teils zur Kante (R 3); selbst gesteckte Teile frei. Näher nur nach schriftlicher Bestätigung durch JLCPCB;
   Antwort in die Bauteilauswahl der Platine.
5. Aufdruck: Polungs- bzw. Pin-1-Marke an jedem gepolten Teil (R 9), sonst Rückfragen und falsche Lage.
6. Transportrand und Passmarken bei Economic nicht nötig (R 4); bei Standard nach R 4 setzen.
7. Leiterbahnen gruppenweise, ohne Autorouter; je Gruppe Bild und DRC (Regelprüfung der Platine).
8. Prüfen: DRC ohne Meldung, Abgleich mit dem Schaltplan ohne Abweichung, 3D-Ansicht.

Ergebnis: geprüfte Platine, Randabstand eingehalten.

## Schritt 4: Fertigungsdateien (nur nach Freigabe des Betreibers)
1. In KiCad das Zusatzprogramm **„Fabrication Toolkit“** verwenden (R 8); vor dem ersten Einsatz erproben.
2. „Apply automatic component translations“ eingeschaltet lassen; Kupferflächen füllen lassen.
3. Ergebnis im Ordner `production/` neben der Platine: Gerber (ZIP), `bom.csv` (Stückliste), `positions.csv`
   (Positionsliste).
4. Selbst gesteckte oder gelötete Teile dürfen nicht in Stückliste und Positionsliste stehen.
5. Eigene Prüfung per Skript: jedes bestückte Teil des Schaltplans in beiden Listen, gleiche LCSC-Nummern, keine doppelten
   Bezeichner, höchstens 200 Bezeichner je Zeile, Bezeichner in beiden Listen gleich geschrieben (R 8).

Ergebnis: drei geprüfte Dateien.

## Schritt 5: Bei JLCPCB hochladen und prüfen (noch nicht bestellen)
1. Gerber hochladen, Platine einstellen (Lagen, Dicke, Farbe, Stückzahl), „PCB Assembly“, Economic, Oberseite.
2. Stückliste und Positionsliste hochladen, „Process BOM & CPL“.
3. **Jedes Teil bestätigen** (nur bestätigte werden bestückt). Je Teil Klasse, Bauform, Lager, Preis mit `bom/bom.csv`
   vergleichen. Extended ohne Freigabe = Fehler, zurück zu Schritt 1.
4. Vorschau: SMD in 2D (roter Punkt auf Aufdruckmarke, bei Dioden + und −), Durchsteckteile in 3D (R 5, R 9).
5. Falsch gedreht: Drehung in der Positionsliste ändern und neu hochladen (nicht JLCPCB raten lassen).
6. Nicht mehr leere Platinen bestellen als bestückte, sonst kommen die übrigen bei Economic eventuell verzinnt (R 1).
7. Bilder der Vorschau und Endpreis dem Betreiber vorlegen. Bezahlt wird vor der Prüfung durch JLCPCB (R 9),
   deshalb muss unsere Prüfung vollständig sein.

Ergebnis: Vorschaubilder und Endpreis in `bestellung.md` der Platine.

## Schritt 6: Bestellen, Empfang, Prüfung
1. **Bestellen nur der Betreiber.** Vorher Lager und Preise am Bestelltag erneut prüfen.
2. Auftragsnummer, Datum, Stückzahl, Endpreis und die verwendeten Fertigungsdateien in `bestellung.md` festhalten.
3. Empfang: Sichtprüfung (jedes Teil da und richtig gedreht, keine Lötbrücken, Löcher für eigene Teile frei).
4. Selbst nachrüsten: Teile, die nicht JLCPCB bestückt hat (Fassungen, ICs, Stecker – je nach Schritt 1).
5. Elektrische Prüfung vor dem ersten Anschluss: Kurzschlussprüfung, Versorgung ohne Last, Spannungen messen. Die
   Einzelschritte werden je Platine vorher aufgeschrieben.
6. Mängel innerhalb von drei Monaten bei JLCPCB melden (R 10); Befund in `bestellung.md`.

## Wohin die Ergebnisse gehören (je Platine, unter `hardware/smd/`)
| Datei | Inhalt | Schritt |
|---|---|---|
| `konzeption/Bauteilauswahl.md` | Entscheidungen der Platine: Schaltungsänderungen, freigegebene Extended-Teile, Fassungen, Randabstand, kleinste Bauform | 1, 3 |
| `bom/bom.csv` | je Teil LCSC-Nummer, Klasse, Lager, Datum, Ersatzteil, Abweichung, „bestückt JLCPCB / selbst“ | 1, 2 |
| `kicad/vNN.NN/` | Schaltplan, Platine, `production/` mit den Fertigungsdateien | 2–4 |
| `kicad/vNN.NN/bestellung.md` | höchstens 40 Zeilen: Auftragsnummer, Datum, Stückzahl, Endpreis, Vorschaubilder, Befund beim Empfang | 5, 6 |
Baugruppen ohne Trennung in `tht/` und `smd/` (heute der Motor-Controller) bekommen diese Struktur, wenn ihre SMD-Fassung beginnt.
