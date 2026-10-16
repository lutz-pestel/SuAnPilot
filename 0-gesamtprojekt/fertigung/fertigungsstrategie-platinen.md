# Fertigungsstrategie Platinen (KiCad, JLCPCB)

Version 00.02, Stand: 16.10.2026. Gilt für alle neuen Platinen (Robnet-Analyse, Motor-Controller-Neubau, SuAnPilot). Katalogwerte
(Abschnitt 4) vom 05.10.2026 ändern sich; vor jeder Bestellung neu prüfen.

## 1. Ziel und zwei Linien
Platinen werden in KiCad entworfen und bei JLCPCB gefertigt. Zwei Linien laufen parallel:
- **Linie A (THT, selbst löten):** Durchsteckteile (THT, Anschlussdrähte durch Löcher). Sichere Hauptlinie.
- **Linie B (SMD, bestückt):** Oberflächenteile (SMD, kleine Teile ohne Drähte), von JLCPCB maschinell bestückt.
  Entsteht aus A, indem möglichst viele Teile auf ihr SMD-Gegenstück umgestellt werden. B darf sich elektrisch von A
  unterscheiden, wenn eine SMD-Lösung etwas ermöglicht, das in THT nicht ging.
- Je Linie ein eigenes KiCad-Projekt (Unterordner von `2-motor-controller/hardware/` bzw. `1-tinypilot/autopilot/hardware/kicad/`).
  Änderungen in A werden in B bewusst nachgezogen, nicht automatisch.

## 2. Entwurfsregeln
1. **Jedes Bauteil in A hat von Anfang an sein SMD-Gegenstück:** Gehäuse, LCSC-Nummer (JLCPCB-Teilenummer),
   Klasse Basic/Preferred/Extended (Abschnitt 3) und Lagerbestand.
2. **THT nur bewusst:** In der Teiletabelle steht je Teil eine Spalte „Abweichung" mit dem Grund (Selbstlöten,
   nur als DIP lieferbar, SMD nicht im Katalog). Ohne Grund wird das Teil in B umgestellt.
3. **Nur Basic und Preferred:** Extended-Teile kosten Aufschlag; nur wo es keine Alternative gibt und nur mit Freigabe
   des Betreibers (Abschnitt 3).
4. **Prüfung gegen den echten Katalog,** nicht gegen Erinnerung: JLCPCB-Katalog nach `bauteilauswahl-standard.md`.
5. Vor der Bestellung Lagerbestand und Preis erneut prüfen. Teile ohne Lager sind nur Vorbestellung.

## 3. Was JLCPCB verlangt
Bestückungsarten, Preise, Abstände, Durchsteckteile, Teileklassen, Dateiformate, Drehung: `jlcpcb-bestueckungsregeln.md`
(am 16.10.2026 auf den JLCPCB-Seiten gelesen, mit Links). Dort auch die Regel „Extended nur mit Freigabe des Betreibers“.

## 4. Katalogprüfung der bisherigen Teile (05.10.2026)
| Teil | Befund |
|---|---|
| Widerstand 2,2 kΩ, 0603, 1 % | Basic, C4190, 0,0018 $, Lager sehr groß |
| MCP3208 (A/D-Wandler) | in **jeder** Bauform Extended. DIP-16 CI/P: C1543277, 10 Stück, 4,27 $. SOIC-16 CI/SL (Rolle): C626764, 1088 Stück, 3,32 $ |
| LM4040-2,5 (Spannungsreferenz) SOT-23 | Extended, lieferbar: C107244 (±1 %, 0,48 $, 30 475 Stück), C44215 (±0,5 %, 0,68 $, 8 728 Stück) |
| LM4040DIZ-2,5 (TO-92) | Extended, C1575317, **nicht auf Lager** (nur Vorbestellung, ab 32 Stück) |
Folgerung: Der MCP3208 ist egal in welchem Gehäuse Extended, SMD spart dort keine Gebühr; nur der Lagerbestand
spricht für SOIC. Bei der Referenz spricht die Lieferbarkeit für SOT-23. Rechnerisch bringen zwei Extended-Teile
in Economic 2 × 3,07 $ = 6,14 $ Aufschlag.

## 5. Ablauf KiCad → JLCPCB
Sechs Schritte von der Machbarkeitsprüfung bis zur Prüfung der gelieferten Platine, und welche Datei der Platine welches
Ergebnis aufnimmt: `ablauf-smd-bestueckung.md`.

## 6. Teile, die nur mit SMD möglich werden (Kandidaten für Linie B)
Aus `2-motor-controller/hardware/konzeption/Bauteilauswahl.md`, dort wegen „kein SMD-Löten" verworfen:
- Verstärkerbaustein für den Messwiderstand (Zeile 70)
- MAX9921 (Zeile 128)
- Isolierte Fertigbausteine wie ADM2483 (Zeile 181)
Für jedes ist zu prüfen: gibt es ein Basic/Extended-Teil bei JLCPCB, was kostet es, ersetzt es Aufbau in A?

## 7. Hauptliste (BOM)
Je Baugruppe unter `hardware/bom/bom.csv`, für den Motor-Controller `2-motor-controller/hardware/bom/bom.csv` (Spalten: THT-Teil,
SMD-Gegenstück, LCSC, Klasse, Lager, Abweichung). Katalogstand 05.10.2026. Befund: Für die Schutzdiode 1.5KE20A ist der SMD-Ersatz nicht gleichwertig.

## 8. Offen
- Endstückliste: `bom.csv` des Motor-Controllers ist angelegt, Typen teils offen (Abschnitt 7).
- Zeile 12 in `Bauteilauswahl.md` („Kein SMD-Löten") an Regel 2 anpassen.
- JLCPCB-Werkzeuge in KiCad (Teilesuche, Export) erproben.
