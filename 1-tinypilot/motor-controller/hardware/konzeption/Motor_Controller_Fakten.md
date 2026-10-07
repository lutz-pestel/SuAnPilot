# Motor-Controller – Fakten

Version 00.01, Stand 07.10.2026

## Status
Der Code liegt hier **nur als Reserve**. Er wird gebraucht, falls der Controller
einmal neu programmiert werden muss. **Dafür gibt es bis auf Weiteres keinen Grund.**
Welcher Programmstand auf dem eingebauten Controller läuft, ist unbekannt.

## 1. Herkunft des Codes
- Quelle: github.com/pypilot/pypilot, Ordner `arduino/motor`, Autor Sean D'Epagnier (GPL v3).
- Heruntergeladen am 2026-09-29, Projektstand 60d855a (2026-09-10).
- `motor.ino` zuletzt geändert am 2021-12-05 („implement brake feature“). Die `Makefile`
  wurde 2023 noch einmal geändert, aber nur an einer Kommentarzeile.
- `motor.ino` wurde zwischen 2020-04-22 und 2021-12-05 30-mal geändert, darunter:
  2020-04-27 „retune rudder reaction rate“, 2021-05 Kupplung per PWM (Pulsweiten-Steuerung),
  2021-07-19 „improve rudder feedback“, 2021-12-05 Bremse.

## 2. Hardware (Datenblatt, Schaltplan `hydraulic_controller.pdf`, Foto in `../datenblaetter/`)
- „pypilot hydraulic motor controller“, Schaltplan vom 29.11.2017, fertig gekauft.
- Arduino Nano, H-Brücke (Motor-Umpolschaltung) aus vier N-Kanal-Transistoren,
  serielle Leitung über Optokoppler (Lichtschranken-Baustein) galvanisch getrennt.
- 11,2–30 V, Motorstrom bis 20 A, Sicherung 20 A.
- Klemmleiste: Motor A, Motor B, Masse, +12 V, Kupplung.
- Kabel Endlagenschalter: schwarz = gemeinsam, gelb = Backbord, rot = Steuerbord.
- Kabel Ruderlagengeber: schwarz = Masse, gelb = Winkelspannung, rot = +5 V.
- Stecker für die serielle Verbindung zum TinyPilot.

## 2a. Leistungsteil laut Plan (`hydraulic_controller.pdf`, Blatt 1) und vermutete Fehler
- H-Brücke: Q1 oben / Q2 unten an Klemme A, Q3 oben / Q4 unten an Klemme B, je Schalter ein Transistor. Treiber NCP5106B U2 (A),
  U3 (B); Bootstrap (Hilfsspannung der oberen Transistoren) C5/C6 je 0,22 µF, Ladedioden D2/D1 1N4001. Strom über 0,5 mΩ/INA180.
- **Fehler Ersatzgerät:** rückwärts (= Ruder nach Steuerbord) zeitweise 1,9 V statt 11 V am Motor, 1,1–1,9 A, Brummen, keine
  Meldung (Testbericht 04.10.); 06.10. unter Segel 11 von 12 Läufen gestört, unter Motor 2 von 29 (Master,
  `signals_2026-10-06_140402.csv`). Bordspannung dabei 12,5 V (04.10.) und 13,0 V (06.10.), Zusammenhang ungeprüft.
- **Verdacht:** ein oberer Transistor schaltet zeitweise nur halb durch; Bootstrap klein, Diode langsam (neuere Bauformen 10 µF,
  schnelle Diode). Unbelegt (eigene Schlussfolgerung): Bei voller Drehzahl lädt der Bootstrap schlecht nach; die Firmware änderte
  das 2020, der Stand auf dem Gerät ist unbekannt. Bestückung nach Plan nicht geprüft. Altes Gerät: Ausfall vorwärts (30.09.).

## 3. Verbindung zu TinyPilot und RF300-Interface
- TinyPilot und Controller sind seriell verbunden, laut Makefile-Monitor mit 38400 Baud.
  Im Dual-Display-Aufbau läuft die Verbindung als RS422 (störfeste Leitung) über das
  8-adrige Kabel zum RF300-Interface im Motorraum (Adern orange und grün).
- Datenpakete: 4 Byte = Befehl, 16-Bit-Wert, Prüfsumme (CRC8). Der Controller reagiert
  erst, wenn mehrere Pakete in Folge eine gültige Prüfsumme haben.
- Befehle vom TinyPilot: Stellbefehl, Stromgrenze, Temperaturgrenzen, Ruderbereich,
  Auskuppeln, Neu-Programmieren, Speicher lesen und schreiben, Kupplung und Bremse.
- Meldungen an den TinyPilot: Strom, Spannung, Temperaturen, Ruderlage, Zustands-Flags.
- Der Ruderwinkel kommt als Spannung 0–5 V vom RF300-Interface an den gelben Draht.

## 3a. Ruderlage-Eingang
- Im Controller: +5 V für den Geber über R7 = 200 Ω; Eingang über Teiler R8 100 kΩ / R9 30 kΩ.
  Messbereich je nach Bauart 0–1,1 V oder 0–5 V („ratiometrisch“, Planvermerk mit
  geänderten Widerständen).
- Der „kleine Umbau für Hall-Sensoren“ (Controller vor Oktober 2019) ist nirgends
  beschrieben. Schluss aus Plan und Forum (Entwickler, 08.04.2022: Hall-Sensor zieht 13 mA):
  R7 überbrücken. **Betrifft diesen Aufbau nicht**: Das RF300-Interface hat eigene Versorgung.
- Das Interface glättet sein PWM-Signal mit R6 1 kΩ / C6 100 µF (Zeitkonstante 0,1 s, berechnet).
  Geschätzte Gesamtverzögerung der Ruderlage: etwa 0,25 s (Spanne 0,2–1 s), nicht gemessen.

## 4. Aufspielen (nur falls nötig)
- **Vorher den vorhandenen Stand sichern.** Die Makefile hat dafür den Befehl
  `make download`, der den Programmspeicher mit einem zweiten Arduino als
  Programmiergerät (ISP) ausliest.
- Windows: Arduino-IDE, `motor.ino` und `crc.h` in einen Ordner `motor` legen,
  Board „Arduino Nano“, Prozessor „ATmega328P“, Anschluss wählen, Hochladen.
- Linux: `make` und `make upload` (avrdude über USB, 57600 Baud).
- Die Fuses (fest eingestellte Chip-Einstellungen, u. a. Unterspannungsschutz) müssen
  stimmen. Sind sie falsch, meldet der Controller das Flag BAD_FUSES.
- Das Programm kennt den Befehl „Neu programmieren“ (Code 0x19): Er springt in den Lader
  (Bootloader). Ein fertiges Werkzeug, das damit über den TinyPilot aufspielt, ist nicht bekannt.
- Lader: Die Makefile nennt den 8-MHz-Lader, die Windows-Anleitung setzt den Standard-Nano voraus.

## 5. Version erkennen
- Der Code enthält keine Versionsnummer und meldet keine. Auch der TinyPilot
  (`pypilot/servo.py`) fragt keine ab.
- Ohne Umbau: den Programmspeicher auslesen und mit selbst übersetzten Ständen
  vergleichen. Das ist aufwendig; ein Treffer ist wahrscheinlich, aber nicht sicher.
- Mit Umbau: eine eigene Versionskennung einbauen, z. B. als Blinkmuster beim Start.

Offene Fragen zum Controller stehen nur in `0-gesamtprojekt/TODO.md` (Abschnitt „Offene Fragen Hardware“).
