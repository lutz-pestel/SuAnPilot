# Robnet-Analyse – Anforderungen und Konzept

Version 00.04, Stand 10.10.2026, Obergrenze 80 Zeilen.
Zweck: Platine, die den Robnet-Bus des Robertson AP300X mitliest, damit Pegel, Datenrate und Telegramme bestimmt werden
können. Was über Robnet bekannt ist (Belegung, Messwerte, Hypothesen): `99-tools/docs/Robnet.md`.
Alle Verbindungen mit Pins und Netzen: `Blockschaltbild_Robnet-Analyse.html`.

## 1. Grundsätze
- **Nur lesen, nie senden.** Der Bus wird nicht verändert: kein Abschlusswiderstand, wenig Last, kein Strom aus Vsys.
- **Masse an Grau (Vsys−).** Grau = Bordmasse (gemessen 0,004 V); galvanische Trennung nicht nötig.
- **Gefertigte Platine (JLCPCB)**, Rechner Raspberry Pi Zero 2 W (vorhanden) als aufgesteckter Baustein.
- **Kein Oszilloskop nötig:** Die Platine bestimmt Datenrate und Signalform selbst (Abschnitt 3).
- Teile und Schaltungen wie im Motor-Controller, wo möglich (`2-motor-controller/hardware/konzeption/Bauteilauswahl.md`).

## 2. Blöcke
1. **Abgriff:** kurzes 6-adriges Kabel von der Robnet-Klemmleiste im J300 (jede Ader zusätzlich unter die vorhandene
   Schraube), dazu eine Ader zur Robertson-Versorgung (+). Am Gerät Schraubklemme; in jeder Ader ein Schutzwiderstand.
2. **Bus-Empfänger:** MAX3488 (wie Motor-Controller) im **Sockel**, nur der Empfänger an Bus+/Bus−; Sendeausgänge
   **offen** (dieser Baustein sendet immer, sobald sie angeschlossen sind). Ausgang an zwei Eingänge des Zero:
   Seriell-Schnittstelle (Telegramme) und normaler Eingang (Zeitstempel der Pegelwechsel). Grenze 250 kbit/s, weit über
   Bedarf (Abschnitt 3); Sockel nur zum schnellen Tausch bei Beschädigung.
3. **Spannungsmessung:** MCP3208 mit Referenz LM4040 2,5 V, Teiler und Schutzdioden BAT85 wie im Motor-Controller.
   Teiler 100 kΩ/18 kΩ (bis ~16 V): Bus+, Bus−, On-Off, Alarm, Bordspannung. Vsys+ (26,4 V) mit größerem Teiler,
   Vorschlag 100 kΩ/8,2 kΩ (bis ~33 V). Zwei Kanäle frei.
4. **Schaltleitungen:** On-Off und Alarm zusätzlich an Eingänge des Zero (Zeitstempel), über Spannungsteiler auf 3,3 V
   (Alarm 4,8 V im Alarmfall; On-Off 13,5 V, Bedeutung ungeprüft – TODO, offene Frage 20).
5. **Rechner:** Zero 2 W, per SSH vom PC (kein Umweg über den Master); Aufzeichnung auf der Karte, Uhrzeit vom PC.
   WLAN: Samsung AP, in dem sich alle Geräte anmelden; Ersatz ist das WLAN des Masters.
6. **Versorgung:** aus der Robertson-Versorgung, mit Sicherung und Verpolschutz, Recom R-78B5.0-2.0 auf 5 V für den Zero;
   3,3 V für MAX3488 und MCP3208 vom Zero. **Nicht aus Vsys.**

## 3. Vorgehen zur Datenrate
Zwei Messwege laufen parallel am selben Leitungspaar, mit derselben Uhr (Aufzeichnungen lassen sich übereinanderlegen):
- **Digital über den MAX3488:** Differenz Bus+ − Bus− als Rechteck. Erst die üblichen Datenraten an der
  Seriell-Schnittstelle der Reihe nach durchprobieren. Kommen keine sauberen Bytes: Zeitstempel der Pegelwechsel
  ergeben Bitmuster, Bitzahl (auch 9-Bit-Bytes) und Bitlänge, daraus die Datenrate.
- **Analog über den MCP3208:** Bus+ und Bus− einzeln gegen Masse als Spannung über die Zeit (Hub, Ruhepegel,
  Gegenlauf). Gesamt etwa 60 000 Messungen je Sekunde: sauberes Bitmuster nur bei langsamer Rate.
- **Last am Bus:** je Leitung ~118 kΩ (Teiler) plus Empfängereingang des MAX3488 (12 kΩ, Datenblatt) – gering.
- **Abtastrate (Recherche 10.10.2026, nicht gemessen):** digital tastet pigpio per DMA (Hardware-Kopierbaustein, ohne
  Linux-Schwankungen) alle 1–5 µs ab; bei ≥ 5 Punkten je Bit sicher bis 38 400 Baud, 115 200 Baud knapp (nur bei 1 µs).
  Analog (MCP3208 an 3,3 V: 50 000–100 000 Messungen/s laut Datenblatt, unter Linux weniger, auf zwei Kanäle verteilt):
  Bitmuster bis ~2400–4800 Baud. Belege für den Zero 2 W fehlen.
- **Annahme (Betreiber): höchstens etwa 9600 Baud**, weil das Gerät alt ist (ungemessen). Dann ~20 Punkte je Bit schon
  bei 5 µs: digital sicher, Pi-Test vorab unnötig; analog nur 2–3 Punkte je Bit (Pegel, Hub). Höhere Rate fängt das
  Durchprobieren an der Seriell-Schnittstelle ab. Deshalb keine Reserve (schnellerer Empfänger, ESP32-Steckplatz).

## 4. Bewusst weggelassen
- **Senden:** bräuchte einen Baustein mit Sendefreigabe; erst nach dem Verstehen ein Thema.
- **Zweiter Rechner (Pico oder ESP32) für schnelle Abtastung:** verworfen; Datenraten durchprobieren und der digitale
  Messweg reichen. Zero statt ESP32, weil Linux, SSH und Speicher das Ausprobieren ohne Firmware-Aufspielen erlauben.

## 5. Offen
- Zero 2 W noch nicht vorhanden (beschaffen).
- Werte der Schutzwiderstände, Gehäuse und Einbauort im Motorraum.
