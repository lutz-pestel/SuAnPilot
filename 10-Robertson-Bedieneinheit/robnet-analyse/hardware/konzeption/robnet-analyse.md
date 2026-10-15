# Robnet-Analyse – Anforderungen und Konzept

Version 00.09, Stand 15.10.2026, Obergrenze 80 Zeilen.
Gehört zu Weg B (neue Bedieneinheit für den Robertson, `0-gesamtprojekt/SuAn-Autopilot-Projekt.md`, Abschnitt 4).
Zweck: Platine, die den Robnet-Bus des Robertson AP300X mitliest, die Richtung jeder Ader über Shunts erkennt und jede Ader per Jumper trennen kann, damit Pegel,
Datenrate, Telegramme und die Rolle jeder Seite bestimmt werden – mit dem Ziel, die Bedieneinheit nachzubauen. Robnet-Wissen (Belegung, Messwerte, Hypothesen H1–H7):
`99-tools/docs/Robnet.md`. Alle Verbindungen mit Pins und Netzen: `Blockschaltbild_Robnet-Analyse.html`.

## 0. Stand und nächster Schritt (Einstieg für neue Sitzungen)
- **Fertig:** Konzept (dieses Dokument), Blockschaltbild 00.05, Messwerte am J300 (`Robnet.md`, Abschnitt 2).
- **Noch nichts gebaut:** keine Teileauswahl, kein Schaltplan, keine Platine, keine Software. Zero 2 W nicht vorhanden.
  Leere Platzhalter: `Bauteilauswahl.md`, `hardware/bom/bom.csv`, `hardware/kicad/v00.01/`, `software/`.
- **Nächste Schritte in dieser Reihenfolge**, jeder einzeln dem Betreiber vorlegen (Regel 3):
  1. Betreiber: Typ und Rastermaß des 6-poligen Phoenix-Steckers am J300 (Foto mit Lineal oder Aufschrift).
  2. Teileauswahl in `Bauteilauswahl.md` (Abschnitt 5 „Offen“ ist die Liste); vorher dessen Zeilengrenze in `CLAUDE.md`
     eintragen. Muster: `2-motor-controller/.../Bauteilauswahl.md`.
  3. Zero 2 W beschaffen und einrichten: beide WLANs, SSH, Bluetooth aus (Seriell-Schnittstelle frei), SPI an, pigpio.
  4. Schaltplan in KiCad (`hardware/kicad/v00.01/`), Platine, Bestellung JLCPCB.
  5. Software: Aufzeichnung, Datenraten durchprobieren, Telegramme zerlegen; dann Trennversuche (Abschnitt 1).

## 1. Grundsätze
- **Alle 6 Adern aufzeichnen und die Richtung erkennen:** welche Seite treibt bzw. sendet, auch auf dem Bus (Betreiber,
  14.10.2026). Komplexität sinnvoll begrenzen. **Alles von Anfang an bestückt:** Die fertige Platine wird nicht mehr
  geändert; Unbekanntes wird per Jumper wählbar gemacht. Arbeitshypothese Bus: **RS485** (`Robnet.md`, H4).
- **Nur lesen, nie senden.** Kein Abschlusswiderstand, wenig Last am Bus, kein Strom aus Vsys.
- **Am J300 nichts verändern:** Die Platine wird als Zwischenstecker eingeschleift (Abschnitt 2, Block 1).
- **Signalweg nur passiv (Shunts und Jumper):** Fällt die Platine aus, läuft der Robertson unverändert. Trennen =
  Jumper ziehen, von Hand, nur durch den Betreiber und nur im Hafen (schaltet den Robertson teilweise ab).
- **Masse (Vsys−, grau) nie trennen.** Grau = Bordmasse (gemessen 0,004 V); galvanische Trennung nicht nötig.
- **Gefertigte Platine (JLCPCB)**, Raspberry Pi Zero 2 W (zu beschaffen) aufgesteckt. Kein Oszilloskop nötig.
- Teile und Schaltungen wie im Motor-Controller, wo möglich (`2-motor-controller/hardware/konzeption/Bauteilauswahl.md`).

## 2. Blöcke
1. **Zwischenstecker:** Der 6-polige Phoenix-Stecker der Bedieneinheit (Reihenfolge Bus−, Bus+, Vsys+, Vsys−, On-Off,
   Alarm) wird am J300 abgezogen und in eine **Buchse auf der Platine** gesteckt; ein Kabel mit **Stecker** führt von der
   Platine in den J300. Dazu ein Kabel zur Robertson-Versorgung (+12 V) für die Platine.
2. **Shunts und Jumper (Betreiber, 14.10.2026):** In Bus+, Bus−, Vsys+, On-Off, Alarm je zwei Shunts; ein Jumper wählt
   klein oder groß, **gezogen = vollständig getrennt**. Werte (gerechnet, nicht gemessen): Bus 2,2 Ω (mit Abschluss) /
   100 Ω (ohne); Vsys+ 0,1 Ω / 1 Ω; On-Off, Alarm 10 Ω / 100 Ω. Vsys− durchgehend, ohne Shunt.
3. **Bus-Empfänger:** zwei MAX3488 im Sockel, nur Empfänger, Sendeausgänge **offen** (der Baustein sendet sonst immer).
   U1 Seite J300 → Seriell-Schnittstelle (RXD) und Eingang für Zeitstempel. U5 Seite Bedieneinheit → eigener Eingang,
   Lesen per pigpio (Software-Empfang, reicht bei 9600 Baud). Beide sehen dieselben Bits.
4. **Spannungsmessung:** MCP3208, Referenz LM4040 2,5 V, Teiler und Schutzdioden BAT85 wie im Motor-Controller.
   Teiler 100 kΩ/18 kΩ (bis ~16 V), Vsys+ 100 kΩ/8,2 kΩ (bis ~33 V). CH0/CH1 Bus+/Bus− Seite J300, CH2 Vsys+, CH3 On-Off,
   CH4 Alarm, CH5 Bordspannung, CH6/CH7 Bus+/Bus− Seite Bedieneinheit. Bus-Kanäle ohne Glättungskondensator.
5. **Schaltleitungen:** Alarm zusätzlich über Teiler an einen Zero-Eingang (Zeitstempel). **On-Off nur über den Wandler:**
   12 V und 8 V lägen nach einem Teiler beide über der Schaltschwelle des Zero.
6. **Rechner:** Zero 2 W, per SSH vom PC (nicht über den Master); Aufzeichnung auf der Karte, Uhrzeit vom PC.
   WLAN: Samsung AP, in dem sich alle Geräte anmelden; Ersatz ist das WLAN des Masters.
7. **Versorgung:** Robertson-Versorgung → Sicherung → Verpolschutz → Recom R-78B5.0-2.0 → 5 V für den Zero;
   3,3 V für MAX3488 und MCP3208 vom Zero. **Nicht aus Vsys.**
8. **Richtungserkennung:** Die Richtung folgt aus dem Spannungsunterschied über dem Shunt. Ein **zweiter MCP3208** (an CE1)
   misst Vsys+, On-Off, Alarm auf der Seite Bedieneinheit. Bus: Bei RS485 sendet immer nur einer; die Senderseite ist
   stärker (CH0/CH1 gegen CH6/CH7, je Telegramm gemittelt). Je Shunt ein Strommessverstärker (U7–U11) an den zweiten MCP3208.

## 3. Datenrate
- **Digital (MAX3488):** übliche Datenraten an der Seriell-Schnittstelle durchprobieren; sonst ergeben die Zeitstempel
  der Pegelwechsel (pigpio, Abtastung alle 1–5 µs per DMA ohne Linux-Schwankungen) Bitmuster, Bitzahl und Bitlänge.
- **Analog (MCP3208):** Bus+/Bus− einzeln gegen Masse (Hub, Ruhepegel, Gegenlauf); 50 000–100 000 Messungen/s laut
  Datenblatt, unter Linux weniger: Bitmuster nur bis ~2400–4800 Baud.
- **Annahme ≤ 9600 Baud** (Robnet.md, H7): ~20 Punkte je Bit schon bei 5 µs, digital sicher; deshalb kein Pi-Test vorab und
  keine Reserve (schnellerer Empfänger, ESP32). Werte aus Recherche 10.10.2026, nicht gemessen.
- **Last am Bus:** je Leitung ~118 kΩ (Teiler) plus Empfängereingang MAX3488 (12 kΩ, Datenblatt) – gering.

## 4. Bewusst weggelassen
- **Senden:** bräuchte einen Baustein mit Sendefreigabe; erst nach dem Verstehen ein Thema.
- **Zweiter Rechner (Pico oder ESP32):** unnötig bei ≤ 9600 Baud; Zero statt ESP32, weil Linux und SSH das Ausprobieren
  ohne Firmware-Aufspielen erlauben.
- **Relais (Betreiber, 14.10.2026):** Jumper sind passiv, ausfallsicher und sparen Relais, Treiber, Freigabeschalter und
  5 Zero-Ausgänge. Preis: Trennen nur von Hand an der Platine im Motorraum, nicht per Software vom PC.

## 5. Offen
- Typ und Rastermaß des Phoenix-Steckers (Buchse und Stecker passend bestellen).
- Jumper, der sich durch Vibration und Feuchte nicht löst (sonst ist die Ader getrennt); für Vsys+ strombelastbar.
- Strommessverstärker passend zu beiden Shunt-Werten; Shunt-Werte bestätigen. Hilfreich, nicht zwingend, vorher messen:
  Bus-Abschluss (Ohmmeter zwischen Bus+ und Bus−, alles aus) und die Ströme in Vsys+, On-Off, Alarm.
- Werte der Schutz- und Teilerwiderstände, Vorwiderstand LM4040, Sicherung, Verpolschutz; Gehäuse und Einbauort.
- Erst mit der Platine klärbar: welche Seite On-Off auf 8 V zieht, wer Alarm treibt, wie der Robertson auf jede
  getrennte Ader reagiert (nur im Hafen, Standby).
