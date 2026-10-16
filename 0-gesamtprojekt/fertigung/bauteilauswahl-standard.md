# Standard: Bauteilauswahl

Version 00.02, Stand 16.10.2026, Obergrenze 120 Zeilen.
Gilt für **jede** Bauteilauswahl im Projekt: alle Platinen, alle Phasen, Weg A und Weg B. Wird **immer und ohne
Aufforderung** angewandt (Betreiber, 15.10.2026). Entstanden an der Robnet-Analyse
(`10-Robertson-Bedieneinheit/robnet-analyse/hardware/tht/konzeption/Bauteilauswahl.md`, Muster für Aufbau und Tabellen).

## Grundsatz
**Ohne Teile kein Projekt.** Ein Teil ohne verifizierte Bezugsquelle wird nicht eingesetzt. Ziel sind zwei unabhängige
Händler je Teil; hat ein Teil nur einen, steht das ausdrücklich unter „Offen" und wird vor der Bestellung gelöst.

## Schritt 1 — Vorgaben zuerst festschreiben
Vor dem ersten Teil steht in Abschnitt 0 der Bauteilauswahl, woran jede Wahl gemessen wird:
- **Nur Durchsteckteile (THT), selbst gelötet** (Linie A, `fertigungsstrategie-platinen.md`). SMD oder Bestückung durch
  JLCPCB nur, wenn der Betreiber es ausdrücklich freigibt — **nie selbst entscheiden**.
- **Zwei unabhängige Händler je Teil** (Schritt 6).
- Einsatzort und Umgebung (z. B. Motorraum: Wärme, Vibration, Bauteile möglichst −40…+85 °C).
- Robustheit und Diagnosefähigkeit vor Preis.
- Ob die Platine später geändert werden kann; wenn nicht, Unbekanntes von Anfang an wählbar machen (z. B. Jumper).
- Vorgaben aus dem Konzept der Baugruppe (z. B. „den Robertson nicht belasten").

## Schritt 2 — Zielprüfung vor jedem Teil
Vor jedem neuen Teil fragen: **Braucht das Ziel dieses Teil überhaupt?** Löst ein Teil nur das Problem des vorigen
Teils, zurück zum Ziel gehen und einfacher denken.
> Anlass: Bei der Robnet-Analyse führte Shunt → zu kleine Spannung → Messverstärker → SMD → teure DIP-Teile zu einem
> Strommessgerät, obwohl nur „wer treibt die Leitung" gefragt war. Ein Trennversuch per Jumper löste es ohne Teile.

## Schritt 3 — Wiederverwenden vor Neusuchen
Was in einer anderen Baugruppe des Projekts schon geprüft und begründet ist, wird **verwiesen, nicht neu begründet**
(z. B. „wie MC Abschnitt 7"). Gleiche Teile in mehreren Baugruppen vereinfachen Lager und Ersatz.

## Schritt 4 — Jedes neue Teil begründen
- Typ mit vollständiger Herstellernummer und Gehäuse.
- Werte, auf die es ankommt, **aus dem Datenblatt** (mit Quelle); gerechnete Werte als „gerechnet" kennzeichnen.
  **Keine Zahl ohne Beleg.**
- Ein bis drei Sätze, warum dieser Typ.
- *Verworfen:* je verworfenem Weg ein Satz mit Grund.
- Lässt sich ein Datenblatt nicht direkt abrufen: über den Browser des Betreibers oder einen Spiegel versuchen;
  gelingt beides nicht, sagen, welche Werte unbelegt sind.

## Schritt 5 — Mengen zählen
Mengen aus Schaltplan oder Blockschaltbild abzählen, nicht schätzen. Reserven (Sicherungen, Auslaufteile) ausweisen
(„1 + 1"). Die Summen in `bom.csv` müssen zu den Angaben in `Bauteilauswahl.md` passen.

## Schritt 6 — Bezugsquellen (für jedes Teil, ohne Ausnahme)
- **Zwei unabhängige Händler**, jeweils mit **Link, Preis, Lagerbestand und Datum**. Ein anderer Artikel beim selben
  Händler ist keine zweite Quelle.
- **Händler** (Deutschland zuerst): Reichelt, Mouser, DigiKey, Farnell, Bürklin, TME, Conrad; für Raspberry-Zubehör
  BerryBase, Eckstein, Pi-Shop; LCSC als Zusatz für Linie B.
- **Zugriff** (Stand 15.10.2026): Reichelt direkt per Abruf der Suchseite; Mouser und DigiKey nur über den Browser des
  Betreibers (direkter Abruf blockiert); BerryBase direkt. Farnell, Bürklin, TME, Conrad und Eckstein waren weder direkt
  noch über den Browser erreichbar — erneut versuchen, sonst als „nicht abfragbar" vermerken.
- **Links:** Reichelt auf die Produktseite; Mouser und DigiKey auf die Suche nach der Teilenummer (die Produktseiten
  tragen Sitzungsdaten). Stichprobe im Browser, ob die Links öffnen.
- **Lebenszyklus prüfen:** „Restbestand", „obsolet", „Lieferzeit" oder „nicht in dieser Region" erkennen. Dann Reserve
  mitbestellen oder **gleichwertigen Ersatz** suchen (gleiche elektrische Werte, gleiches Gehäuse und Raster) und als
  Ersatz kennzeichnen.
- Ergebnis als Tabelle in der Bauteilauswahl: Teil | Menge | Händler 1 | Händler 2.

## Schritt 7 — Kontrolle per Skript
Ein kurzes Skript liest die Tabelle und zählt, wie viele Positionen zwei verschiedene Händler mit Link haben. Das
Ergebnis („29 von 31") wird dem Betreiber genannt; jede Position ohne zweiten Händler wird einzeln aufgeführt.

## Schritt 8 — Lücken offen benennen
Unter „Offen — vor der Bestellung zu prüfen" stehen: Teile mit nur einem Händler, Auslaufteile, nicht lieferbare
Teile, nicht abfragbare Händler. **Ohne verifizierte Quelle kein Einsatz.**

## Schritt 9 — Durchsicht und Sichern
Der Betreiber sieht die Auswahl durch. Erst danach als „durchgesehen" markieren, einchecken und (auf Nachfrage)
hochladen. Lager und Preise werden vor der Bestellung neu geprüft.

## Vorlage `Bauteilauswahl.md`
- Kopf: Version, Stand, Obergrenze (in `CLAUDE.md` eintragen), Grundlage (Konzept, Blockschaltbild), Verweis auf die
  Stückliste, Hinweis „Preise nur zur Größenordnung".
- `## 0. Vorgaben` (Schritt 1) · je Baugruppe ein Abschnitt (Schritt 4) · `Versorgung` · `Gehäuse und Einbau` ·
  `Offen — vor der Bestellung zu prüfen` (Schritt 8) · `Bezugsquellen` (Schritt 6) · `Quellen` (Datenblätter, Belege).

## Vorlage `bom.csv`
- Erste Zeile: Version, Stand, Herkunft der Werte. Trennzeichen Semikolon, im Text kein Semikolon.
- Spalten wie im Motor-Controller: Funktion; Menge; THT-Teil (Linie A); LCSC THT; Klasse THT; Lager THT; Preis THT;
  SMD-Gegenstück (Linie B); LCSC SMD; Klasse SMD; Lager SMD; Preis SMD; Abweichung; Quelle.
- In „Quelle" der Abschnitt der Bauteilauswahl und der Verweis auf die Bezugsquellen.
- Nach jeder Änderung prüfen, dass jede Zeile gleich viele Spalten hat.
