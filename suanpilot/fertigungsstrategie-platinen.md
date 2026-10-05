# Fertigungsstrategie Platinen (KiCad, JLCPCB)

Version 0.1, Stand: 05.10.2026. Gilt für alle neuen Platinen (Motor-Controller-Neubau, SuAnPilot). Zahlen und Lagerbestände
stammen von der JLCPCB-Webseite vom 05.10.2026 und ändern sich; vor jeder Bestellung neu prüfen.

## 1. Ziel und zwei Linien
Platinen werden in KiCad entworfen und bei JLCPCB gefertigt. Zwei Linien laufen parallel:
- **Linie A (THT, selbst löten):** Durchsteckteile (THT, Anschlussdrähte durch Löcher). Sichere Hauptlinie.
- **Linie B (SMD, bestückt):** Oberflächenteile (SMD, kleine Teile ohne Drähte), von JLCPCB maschinell bestückt.
  Entsteht aus A, indem möglichst viele Teile auf ihr SMD-Gegenstück umgestellt werden. B darf sich elektrisch von A
  unterscheiden, wenn eine SMD-Lösung etwas ermöglicht, das in THT nicht ging.
- Je Linie ein eigenes KiCad-Projekt (Unterordner von `suanpilot/motorcontroller/` bzw. `tinypilot/hardware/`).
  Änderungen in A werden in B bewusst nachgezogen, nicht automatisch.

## 2. Entwurfsregeln
1. **Jedes Bauteil in A hat von Anfang an sein SMD-Gegenstück:** Gehäuse, LCSC-Nummer (JLCPCB-Teilenummer),
   Klasse Basic/Extended (Abschnitt 3) und Lagerbestand.
2. **THT nur bewusst:** In der Teiletabelle steht je Teil eine Spalte „Abweichung" mit dem Grund (Selbstlöten,
   nur als DIP lieferbar, SMD nicht im Katalog). Ohne Grund wird das Teil in B umgestellt.
3. **Vorzugsliste zuerst:** Widerstände und Kondensatoren nur als Basic-Teile wählen. Extended-Teile kosten
   Aufschlag, deshalb nur wo es keine Alternative gibt.
4. **Prüfung gegen den echten Katalog,** nicht gegen Erinnerung: JLCPCB-Teilesuche (Abschnitt 5).
5. Vor der Bestellung Lagerbestand und Preis erneut prüfen. Teile ohne Lager sind nur Vorbestellung.

## 3. Was JLCPCB verlangt (Preistabelle der Seite, Stand 05.10.2026)
- **Basic:** ohne Aufschlag. **Extended:** bei „Economic" 3,07 $ je Teilesorte, bei „Standard" 1,53 $ je Teilesorte
  (für Basic und Extended). Im Katalog gibt es zusätzlich „Promotional Extended"; ein eigener Preis dafür ist
  nicht belegt.
- **Economic:** Einrichtung 8,18 $, Schablone 1,53 $, 0,0016 $ je SMD-Lötstelle, Handlöt-Arbeit 3,58 $ je Auftrag,
  Handbestückung 0,0164 $ je Lötstelle. Nach einer Suchtreffer-Zusammenfassung (nicht auf der Seite selbst
  gelesen): nur eine Seite, 2–50 Stück, kleinste Bauform 0402.
- **Standard:** Einrichtung 25,56 $ (einseitig), Schablone 8,21 $, beidseitig möglich, bis 80 000 Stück (Letzteres aus der Suchtreffer-Zusammenfassung, nicht auf der Seite gelesen).
- **Eigene Teile mitschicken (Konsignation)** ist möglich; die Seite bietet es im Katalog an („Consign Parts").
- **Durchsteckteile (THT):** Die Preistabelle nennt Handlöten und Handbestückung. Ob und wie JLCPCB THT in
  Economic bestückt, ist **nicht gesichert** (eine Zusammenfassung sprach von Wellenlöten; nicht geprüft).

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
1. Schaltplan fertig, jedes Teil mit LCSC-Nummer (KiCad-Feld „LCSC Part #", Symbol-Feldtabelle → Feld hinzufügen).
2. Platine fertig, Prüfung (ERC, DRC).
3. Fertigungsdateien erzeugen: Gerber (Platinendaten), Stückliste (BOM), Positionsliste (CPL). Empfohlen: das
   KiCad-Plugin „JLC PCB Fabrication Toolkit"; es liefert die Spalten im JLCPCB-Format. Ohne Plugin müssen BOM
   (Comment, Designator, Footprint, LCSC-Nummer) und CPL (Designator, Mid X, Mid Y, Rotation, Layer) von Hand
   umbenannt werden.
4. Hochladen und Vorschau prüfen (Drehung und Lage der Teile), erst dann bestellen. Bestellen macht der Betreiber.
- Die KiCad-Werkzeuge von Claude haben Funktionen für JLCPCB-Teilesuche, Gerber, BOM und Positionsdatei;
  **noch nicht erprobt**. Lesezugriff auf die JLCPCB-Seite über den Chrome-Browser funktioniert (Teilesuche, Preise).

## 6. Teile, die nur mit SMD möglich werden (Kandidaten für Linie B)
Aus `suanpilot/motorcontroller/Bauteilauswahl.md`, dort wegen „kein SMD-Löten" verworfen:
- Verstärkerbaustein für den Messwiderstand (Zeile 70)
- MAX9921 (Zeile 128)
- Isolierte Fertigbausteine wie ADM2483 (Zeile 181)
Für jedes ist zu prüfen: gibt es ein Basic/Extended-Teil bei JLCPCB, was kostet es, ersetzt es Aufbau in A?

## 7. Teiletabelle (Vorlage, noch leer: Endstückliste fehlt)
| Ref | Funktion | THT-Teil (A) | SMD-Teil (B) | LCSC | Basic/Ext. | Lager | Abweichung (Grund für THT) |
|---|---|---|---|---|---|---|---|
Wird angelegt, sobald die Endstückliste steht. Dann je Teil Katalog prüfen und eintragen.

## 8. Testschaltplan (Probe, nicht Teil der Linien)
`C:\Users\SuAn\AppData\Local\Temp\kicad-test\test.kicad_sch`: Pi-Zero-2-Leiste, MCP3208 (SPI0), LM4040 mit
Vorwiderstand 2,2 kΩ; Referenzsymbol SMD-Typ (TO-92-Symbol der KiCad-Bibliothek defekt). Nur Erprobung des Ablaufs.

## 9. Offen
- Endstückliste und Teiletabelle (Abschnitt 7).
- THT-Bestückung bei JLCPCB: Möglichkeit und Preis klären.
- Zeile 12 in `Bauteilauswahl.md` („Kein SMD-Löten") an Regel 2 anpassen.
- Hilfen für EasyEDA (KI-Unterstützung, KiCad-Import) nicht untersucht.
- JLCPCB-Werkzeuge in KiCad (Teilesuche, Export) erproben.
