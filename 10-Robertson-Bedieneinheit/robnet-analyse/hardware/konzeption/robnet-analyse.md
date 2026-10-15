# Robnet-Analyse – Anforderungen und Konzept

Version 00.20, Stand 15.10.2026, Obergrenze 100 Zeilen.
Gehört zu Weg B (neue Bedieneinheit für den Robertson, `0-gesamtprojekt/SuAn-Autopilot-Projekt.md`, Abschnitt 4).
Zweck: Platine, die den Robnet-Bus des Robertson AP300X mitliest und jede Ader per Jumper trennen kann, damit Pegel,
Datenrate, Telegramme und die Rolle jeder Seite bestimmt werden – mit dem Ziel, die Bedieneinheit nachzubauen. Robnet-Wissen (Belegung, Messwerte, Hypothesen H1–H8):
`99-tools/docs/Robnet.md`. Alle Verbindungen mit Pins und Netzen: `Blockschaltbild_Robnet-Analyse.html`.

## 0. Stand und nächster Schritt (Einstieg für neue Sitzungen)
- **Fertig:** Konzept (dieses Dokument), Blockschaltbild 00.15, Messwerte am J300 (`Robnet.md`, Abschnitt 2),
  Teileauswahl `Bauteilauswahl.md` 00.04 mit Stückliste `hardware/bom/bom.csv` (vom Betreiber durchgesehen, 15.10.2026).
- **Noch nichts gebaut:** kein Schaltplan, keine Platine, keine Software. Zero 2 W nicht vorhanden.
  Leere Platzhalter: `hardware/kicad/v00.01/`, `software/`.
- **Nächste Schritte in dieser Reihenfolge**, jeder einzeln dem Betreiber vorlegen (Regel 3):
  1. Offene Punkte der Teileauswahl klären (`Bauteilauswahl.md`, Abschnitt 7).
  2. Schaltplan in KiCad (`hardware/kicad/v00.01/`), Platine, Bestellung JLCPCB.
  3. **Später, nicht jetzt** (Betreiber, 15.10.2026; bis dahin nur dokumentiert, `Bauteilauswahl.md` Abschnitt 5):
     Zero 2 W, WLAN-Stick mit 5-m-USB-Kabel und LAN-Adapter beschaffen; einrichten: Netz (Block 6), SSH, Bluetooth aus
     (Seriell-Schnittstelle frei), SPI an, pigpio.
  4. Software: Aufzeichnung, Datenraten durchprobieren, Telegramme zerlegen; dann Trennversuche (Block 8).

## 1. Grundsätze
- **Alle 6 Adern aufzeichnen und die Richtung erkennen:** welche Seite treibt bzw. sendet, auch auf dem Bus (Betreiber,
  14.10.2026). **Einfach halten:** Die Richtung ist eine feste Eigenschaft jeder Ader; sie wird durch kurzes Trennen
  bestimmt, nicht dauernd gemessen (Block 8; Betreiber, 15.10.2026). **Alles von Anfang an bestückt:** Die fertige
  Platine wird nicht mehr geändert. Arbeitshypothese Bus: **RS485** (`Robnet.md`, H4).
- **Nur lesen, nie senden.** Kein Abschlusswiderstand, wenig Last am Bus, kein Strom aus Vsys.
- **Am J300 nichts verändern:** Die Platine wird als Zwischenstecker eingeschleift (Abschnitt 2, Block 1).
- **Signalweg nur passiv (Jumper):** Fällt die Platine aus, läuft der Robertson unverändert. Trennen =
  Jumper ziehen, von Hand, nur durch den Betreiber und nur im Hafen (schaltet den Robertson teilweise ab).
- **Masse (Vsys−, grau) nie trennen.** Grau = Bordmasse (gemessen 0,004 V); galvanische Trennung nicht nötig.
- **Gefertigte Platine (JLCPCB), nur Durchsteckteile, selbst gelötet**; Raspberry Pi Zero 2 W (zu beschaffen) aufgesteckt.
  Kein Oszilloskop nötig (Reserve: Stiftleiste J4).
- Teile und Schaltungen wie im Motor-Controller, wo möglich (`2-motor-controller/hardware/konzeption/Bauteilauswahl.md`).

## 2. Blöcke
1. **Zwischenstecker:** Phoenix **MSTB 2,5, Rastermaß 5,08 mm** (wie an der RF300-Interfaceplatine; Betreiber, 15.10.2026).
   Der 6-polige Stecker der Bedieneinheit (Reihenfolge Bus−, Bus+, Vsys+, Vsys−, On-Off,
   Alarm) wird am J300 abgezogen und in eine **Buchse auf der Platine** gesteckt; ein Kabel mit **Stecker** führt von der
   Platine in den J300. Dazu ein Kabel zur Robertson-Versorgung (+12 V) für die Platine.
2. **Jumper JP3–JP7** in Bus+, Bus−, Vsys+, On-Off, Alarm: **gesteckt = 1:1 verbunden, gezogen = getrennt**. Vsys− durchgehend.
3. **Bus-Empfänger:** ein MAX3488 (U1) im Sockel, nur Empfänger, Sendeausgänge **offen** (sonst sendet er) →
   Seriell-Schnittstelle (RXD) und Zeitstempel-Eingang. **JP2 wählt die Seite** (J300 oder Bedieneinheit), damit er bei
   gezogenem Bus-Jumper jede Seite allein lesen kann. **Stiftleiste J4** (Bus+, Bus−, Masse, Seite J300) für Oszilloskop
   oder Logikanalysator (Betreiber, 15.10.2026).
4. **Spannungsmessung:** MCP3208, Referenz LM4040 2,5 V, Teiler und Schutzdioden BAT85 wie im Motor-Controller.
   Teiler 100 kΩ/18 kΩ (bis ~16 V), Vsys+ 100 kΩ/8,2 kΩ (bis ~33 V). Bus-Kanäle ohne Glättungskondensator.
   **U2 (CE0) = Seite J300:** CH0/CH1 Bus+/Bus−, CH2 Vsys+, CH3 On-Off, CH4 Alarm, CH5 Bordspannung; CH6, CH7 frei.
   **U6 (CE1) = Seite Bedieneinheit:** CH0 Vsys+, CH1 On-Off, CH2 Alarm, CH3/CH4 Bus+/Bus−; CH5–CH7 frei.
5. **Schaltleitungen:** Alarm zusätzlich über Teiler an einen Zero-Eingang (Zeitstempel). **On-Off nur über den Wandler:**
   12 V und 8 V lägen nach einem Teiler beide über der Schaltschwelle des Zero.
6. **Rechner:** Zero 2 W, per SSH vom PC (nicht über den Master); Aufzeichnung auf der Karte, Uhrzeit vom PC.
   **Netz aus dem Motorraum** (abgeschirmt wie ein Faradayscher Käfig; Betreiber, 15.10.2026), über den einzigen
   Daten-USB des Zero, jeweils eins: (1) **WLAN-Stick am 5-m-USB-Kabel** außerhalb des Motorraums (einfacher);
   (2) **LAN-Adapter** am USB (umständlicher). Eingebautes WLAN nur, wenn es doch Empfang hat. WLAN: Samsung AP,
   Ersatz das WLAN des Masters. USB-Anschluss im Gehäuse zugänglich, Kabel mit Zugentlastung.
7. **Versorgung:** Robertson-Versorgung → Sicherung → Verpolschutz → Recom R-78B5.0-2.0 → 5 V für den Zero;
   3,3 V für MAX3488 und MCP3208 vom Zero. **Nicht aus Vsys.**
8. **Richtungserkennung durch Trennversuche** (im Hafen, Robertson im Standby):
   - **Bus:** Was wer sendet, zeigt zuerst der Inhalt (Taste gedrückt → neue Nachricht). Sicher: Bus-Jumper ziehen,
     U1 per JP2 erst auf die Seite J300, dann auf die Seite Bedieneinheit; was jede Seite allein sendet, ist ihres.
   - **On-Off, Alarm:** Jumper ziehen, Taste drücken bzw. Alarm auslösen; die Seite, deren Spannung sich ändert, treibt.
   - **Vsys+:** laut Handbuch versorgt der J300 die Bedieneinheit; getrennt zeigt U6, ob das stimmt.

## 3. Datenrate
- **Digital (MAX3488):** übliche Datenraten an der Seriell-Schnittstelle durchprobieren; sonst ergeben die Zeitstempel
  der Pegelwechsel (pigpio, Abtastung alle 1–5 µs per DMA ohne Linux-Schwankungen) Bitmuster, Bitzahl und Bitlänge.
- **Analog (MCP3208) = Rückfall, falls der Bus nicht RS485 folgt** (Betreiber): Bus+/Bus− einzeln gegen Masse (Hub,
  Ruhepegel, Gegenlauf); laut Datenblatt 50 000–100 000 Messungen/s, unter Linux weniger: Bitmuster vermutlich nur bis
  ~2400–4800 Baud, bei 9600 nur Pegel und Pakete (geschätzt, ungemessen). Dritter Weg: Stiftleiste J4.
- **Annahme ≤ 9600 Baud** (Robnet.md, H7): ~20 Punkte je Bit schon bei 5 µs, digital sicher; kein Vorab-Test auf Steckplatine (Betreiber, 15.10.2026),
  keine Reserve (schnellerer Empfänger, ESP32). Werte aus Recherche 10.10.2026, nicht gemessen.
- **Last am Bus:** je Leitung ~118 kΩ (Teiler) plus Empfängereingang MAX3488 (12 kΩ, Datenblatt) – gering.

## 4. Bewusst weggelassen
- **Senden:** bräuchte einen Baustein mit Sendefreigabe; erst nach dem Verstehen ein Thema.
- **Zweiter Rechner (Pico oder ESP32):** unnötig bei ≤ 9600 Baud; Zero statt ESP32, weil Linux und SSH das Ausprobieren
  ohne Firmware-Aufspielen erlauben.
- **Relais (Betreiber, 14.10.2026):** Jumper sind passiv, ausfallsicher und sparen Relais, Treiber, Freigabeschalter und
  5 Zero-Ausgänge. Preis: Trennen nur von Hand an der Platine im Motorraum, nicht per Software vom PC.
- **Shunts mit Messverstärkern (Betreiber, 15.10.2026):** Die Spannung über einem Shunt beträgt nur Millivolt, auf
  einer Ader mit bis zu 26 V. Das braucht Präzisionsverstärker (THT nur teuer und knapp: AD623, AD629). Der Trennversuch
  (Block 8) beantwortet dieselbe Frage ohne zusätzliche Teile.

## 5. Offen
- Teile gewählt (`Bauteilauswahl.md`); dort Abschnitt 7: was vor der Bestellung zu prüfen ist.
- Gegenstelle für das Netzkabel des LAN-Adapters; Einbauort.
- Erst mit der Platine klärbar: welche Seite On-Off auf 8 V zieht, wer Alarm treibt, wie der Robertson auf jede
  getrennte Ader reagiert (nur im Hafen, Standby).
