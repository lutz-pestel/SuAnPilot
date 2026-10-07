# Systembeschreibung Autopilot

Stand: 05.10.2026. Beschreibt den heutigen Aufbau. Einzelheiten stehen in den Dokumenten am Ende.

## 1. Überblick
- Selbstgebauter Autopilot für ein 15-Tonnen-Schiff mit Hydrauliksteuerung.
- Basis: TinyPilot (Raspberry Pi Zero) mit pypilot **0.24 vom 14.03.2020**, dazu eigene Platinen.
- Die Anlage ist eingebaut und arbeitet; seit Controllertausch und Optimierung am 01.10.2026 steuert sie deutlich besser.
- Seit 2020 hat pypilot 915 Änderungen erfahren (heute 0.71), siehe „Weiterentwicklung“.

## 2. Baugruppen
| Baugruppe | Ort | Aufgabe |
|---|---|---|
| TinyPilot (Pi Zero, pypilot) | PyPilot-Einheit | Kursregler, Kompass/Lagesensor, Anzeige 1, Weboberfläche |
| Hauptplatine PyPilot_Main_RS422 | PyPilot-Einheit | Tasten, Anzeige 2, RS422-Wandler, Lagesensor MPU9250, Infrarot-Empfänger (GPIO 4) |
| Coprozessor-Arduino (Pro Mini 3,3 V) | auf der Hauptplatine | liest die 4 Folientasten, meldet sie an den Pi, Anzeige 2, Summer |
| Motor-Controller (pypilot hydraulic) | Motorraum | treibt die Hydraulikpumpe, misst die Ruderlage |
| RF300 (Robertson) | Ruder | Ruderlagengeber, liefert eine Frequenz (etwa 2,1–3,2 kHz) |
| RF300-Interface (Arduino) | Motorraum | Frequenz → Spannung 0–5 V und NMEA-Satz `$GPRSA` |
| Master (OpenPlotter, Raspberry Pi) | Navigation | WLAN „master“, GPS-Daten, Seekarte, Summer GPIO 24 |
| Cockpit-Kartenplotter (Raspberry Pi, OpenCPN, 10.10.10.187) | Cockpit | Seekarte, NMEA_Monitor, ePaper, Summer GPIO 23 |

Die KiCad-Pläne „General Basic“ (früherer Aufbau, nicht eingebaut) und „General Dual Display“ (eingebaut, ohne den
gezeigten Hall-Sensor) zeigen nur die Verdrahtung. Maßgeblich sind die Platinendateien (so gefertigt) und die Kabelliste
`Kabelverbindung.pdf`; die Schaltpläne wurden nach der Fertigung noch geändert.

## 3. Signalwege
**Ruderlage zum Pi** (nur dieser Weg wird von pypilot genutzt, `rudder.source = servo`):
RF300 → RF300-Interface (Mittel über 30 Messungen, PWM, Glättung R6/C6) → 0–5 V an den gelben
Draht des Motor-Controllers → dessen Arduino misst → serielles Datenpaket über RS422 (8-adriges
Kabel, orange/grün) → Wandler U6 → serielle Schnittstelle des Pi (38400 Baud) → pypilot.
**Gesamtverzögerung gemessen: etwa 1 s.**

**NMEA-Ruderlage:** RF300-Interface → `$GPRSA` (4800 Baud) über RS422 (braunes Paar) → Wandler U7 →
Brücke JP3 → Coprozessor-Arduino (Anzeige 2). Erreicht den Pi nicht.

**Stellbefehle:** pypilot → serielle Schnittstelle → RS422 → Motor-Controller → Pumpe.

**Tasten:** 4 Folientasten → eine Analogleitung → Coprozessor-Arduino → 8 Leitungen direkt an
GPIO 17, 18, 27, 23, 22, 6, 5, 26 des Pi (Auto 17, Select 18, Port_1 27, Menü 23, Stb_1 22,
Port_10 6, Stb_10 5, Tack 26). Ruhe HIGH, Druck LOW. Der Arduino meldet eine Taste
**erst beim Loslassen** mit einem einzelnen Impuls (kurz ≤ 1 s: 1°-Leitung, lang: 10°-Leitung). Folientasten: 1 Backbord,
2 Auto, 3 Menü, 4 Steuerbord; „1°-Leitung“ = kleiner Schritt, an Bord 2° (Angabe Betreiber 03.10.; Menü „small step“).

**GPS:** Master, Port 10110 (NMEA über TCP) → pypilot (`nmea.client = 10.10.10.1:10110`).

**Strom:** 12 V → RF300-Interface (Verpolschutz) → Regler 7805 (5 V für Interface und Optokoppler des Motor-Controllers) und
12-V-Ausgang → Wandler 12→5 V → Hauptplatine: Pi, Coprozessor, Regler U1 (3,3 V); Lagesensor
und Infrarot-Empfänger am 3,3 V des Pi. Motor-Controller: eigene 12 V. Der RF300 bekommt Strom und sendet über denselben Draht.

**Kabel Motorraum ↔ PyPilot-Einheit** (8 Adern, weiße Ader = Minus): grün Stellbefehle, orange Meldungen des Motor-Controllers,
braun NMEA-Ruderlage, blau frei. 5 V kommen getrennt (rot/schwarz). Unbenutzt am Interface: NMEA-Klemme, Hall-Eingang, Ausgang J300.

## 4. TinyPilot
**Software:** pypilot 0.24, geladen aus dem schreibgeschützten Paket `pypilot.tcz`. Eigene Änderungen:
- Handsteuerung per Taste als Notlösung (siehe `Anforderungen.md`, A2): Bei ausgeschaltetem
  Autopiloten lässt jeder Tastendruck die Pumpe 1,4 s laufen, gemessen 6–7° Ruderweg.
- Korrektur der Servo-Positionsregelung aus einer späteren pypilot-Version übernommen.
- Selbsthilfe in `servo.py`: Läuft ein Befehl ≥ 1 s mit Strom < 2,5 A, wird „Pumpe steht“ gemeldet (Logbuch
  `/mnt/mmcblk0p2/servo_recovery.csv`); die Abhilfe ist seit 02.10. abgeschaltet (`REC_ACTIONS = False`).
  Pakete davor: `pypilot.tcz.bak-2026-09-30`, `pypilot.tcz.bak-2026-10-02-vor-abhilfe-aus`.
- Krängungs-Glied H in `pilots/basic.py` und dauerhaft gespeicherte Filter in `boatimu.py` (01.10.2026).
  Paket davor: `pypilot.tcz.bak-2026-10-01-heel`.
- Eigener Regler **adaptive** (`pilots/adaptive.py`, 05.10.2026): regelt die Ruderlage, wählbar neben basic.
  Paket davor: `pypilot.tcz.bak-2026-10-05-vor-00.05`. Code `1-tinypilot/regler/`.
- Laut Bedienungsanleitung wurde früher das Vorzeichen der NMEA-Ruderausgabe (`nmea.py`)
  geändert; im heutigen Paket nicht nachgeprüft.

**Start:** Das Betriebssystem (piCore) läuft im Arbeitsspeicher. pypilot startet zuerst, danach
Tasten/Anzeige, GPS-Dienst, nach etwa 12 s WLAN, dann Fernzugang und Weboberfläche.
Die Uhr (der Pi hat keine eigene) wird etwa 1 min nach dem Start aus dem GPS des Masters gestellt
(eigenes Skript `/opt/gpsdate.py`; ohne Master bleibt sie beim 14.03.2020).

**WLAN:** Teilnehmer im WLAN „master“, Adresse per DHCP (wechselt, zuletzt 10.10.10.164, Name „box“).
Kein Rückfall: Ohne Master ist der TinyPilot per WLAN nicht erreichbar; die Steuerung läuft
trotzdem. Die Zugangsdaten stehen im Klartext in `.pypilot/networking.txt` auf der Karte.

**Ausschalten:** Nur Power Off. Einstellungen werden alle 60 s gespeichert; nach dem Ändern
von Einstellungen daher mindestens 60 s warten. Folge harter Abschaltungen: Dateisystemfehler
(am 29.09.2026 repariert); eine Prüfung pro Saison ist sinnvoll.

**Karte und Sicherungen** (Ordner `PyPilot_2021\PyPilot_Imgage` auf dem PC):
`2026-09-29_TinyPilot_Karte_vor_Reparatur.img.gz` (Kartenstand vom 29.09.2026),
`2026-09-29_pypilot.tcz.orig` (Originalpaket), `2026-09-29_mydata.tgz.orig` (Startarchiv vor der
Uhr-Korrektur), dazu die älteren Images von 2020 und 2021.

## 5. Eingestellte Werte (Stand 02.10.2026 14:47, geprüft halber Wind 11–17 kn mit Böen; Flaute < 10 kn ungeprüft)
| Wert | Einstellung |
|---|---|
| Regler | basic, Modus compass |
| P / I / D / DD / PR / R / FF / H | 0,005 / 0,08 / 0,22 / 0,05 / 0,01 / 0 / 2,5 / 0,5 |
| Servo max. Strom / Periode / Verstärkung | 20 A / 0,3 / 1,0 |
| Drehrate-Filter | 0,1 |
| Ruderbereich | ±30° (Kalibrierung vom 01.10., Grad etwa 20 % größer als zuvor); Anzeige bei Ruder mittig +2,9° |
| Servo-Störungszähler | 57 |

Herleitung: Testberichte 01.10. (Starkwind: P 0,02, D 0,27, gain 0,7) und 02.10. (Leichtwind P 0,0025; Böen: heutige Werte).

## 6. Motor-Controller, RF300-Interface, Coprozessor
- **Motor-Controller:** fertig gekauft; Code des Herstellers liegt nur als Reserve im Projekt.
  Welcher Stand aufgespielt ist, ist unbekannt. Neu aufspielen ist nicht vorgesehen. Seit 01.10.2026
  Ersatzgerät (altes: Vorwärtsrichtung ausgefallen); er überschrieb beim Verbinden Werte im TinyPilot.
- **RF300-Interface:** eigener Code im Projekt (`1-tinypilot/rf300-interface/software/RF300_Interface`), Kalibrierung im EEPROM.
- **Coprozessor:** der aufgespielte Code ist verschollen; der Code im Projekt ist veraltet.
  Kein Programmierzugang vorhanden.

## 7. Schwachstellen (offene Fragen stehen nur in `0-gesamtprojekt/TODO.md`)
- **Pumpe rückwärts zeitweise schwach** (1,9 V statt 11 V am Motor, Motor steht, brummt; Endstufe des Controllers; Testbericht 04.10.).
- Ruderlage etwa 1 s verzögert: für basic unerheblich, für adaptive eingerechnet (Chronik).
- Handsteuerung per Taste nur als Notlösung (A2); Ziel siehe `3-suanpilot/autopilot/hardware/konzeption/bedieneinheit.md`, B3.
- **AIS-Gerät sendet `$GPRMC` mit Datum 14.02.2007** (vermutlich Überlauf des GPS-Wochenzählers;
  nachgewiesen 30.09.2026 durch Ab-/Einschalten). Die Signal-K-Erweiterung „set-system-time“
  übernahm es ungeprüft, die Master-Uhr sprang 2007↔2026; seit 30.09. abgeschaltet, Uhr stabil.

## 8. Aufzeichnung und Überwachung
Läuft auf dem Master, unabhängig von Claude; startet beim Hochfahren selbst (`crontab` pi, `@reboot`, 90 s).
Programme `/home/pi/aplog/` (`aplog.py`, `pumpwatch.py`, `aplog.sh`; Kopie `1-tinypilot/werkzeuge/logger/`).
| Datei in `/home/pi/aplog/data/` | Inhalt |
|---|---|
| `signals_<Datum>_<Zeit>.csv` | 5/s: Kurs, Soll, Fehler, Drehrate, Krängung, Roll/Stampf, Ruder, Pumpe, Strom, Spannung, Wind, GPS, Reglerglieder, Controller-Temperatur, Selbsthilfe; je Start neue Datei; Zeit = Unix-Zeit (UTC) |
| `events_<…>.csv` / `marks.csv` | jede Wertänderung mit Uhrzeit / Markierungen |
| `pumpruns_<…>.csv` / `pumpstatus.txt` | jeder Pumpenlauf ≥ 0,6 s mit Strom, Ruderweg, Befund / Zusammenfassung 10 min |
| `aplog.log` / `verbindung.json` | Verbindungsprotokoll / Zustand je Sekunde; `aplog.py` 00.01 verbindet nach 6 s ohne Daten neu |
Im TinyPilot: Selbsthilfe-Logbuch `/mnt/mmcblk0p2/servo_recovery.csv`.
- Ansehen am Master (Bildschirm oder VNC): Dateimanager, oder im Terminal `~/aplog/aplog.sh status` (läuft alles?),
  `~/aplog/aplog.sh pumpe [n]` (Pumpe, Auffälligkeiten), `~/aplog/aplog.sh mark "Text"`, `cat ~/aplog/data/marks.csv`,
  `~/aplog/aplog.sh ruder [Datum]` (Ruder-Trimm je Bug, Wind, Krängung; `ruder.py`).
- **Wache** `python3 ~/aplog/wache.py [s]`: liest live mit, endet bei Böe (Krängung 10 s > 17°), Flaute (2 min < 10 kn),
  Kursfehler > 15° für 10 s oder Autopilot aus; zeigt 2 min davor bis s danach in 10-s-Schritten.
- **Gütedatei** `guete_<Datum>.csv` (je Minute Gütemaß, Bedingungen, Ampel, Reglerwerte; `guete.py` in `pumpwatch.py`),
  je Tag eine Datei; Speichergrenze Datenordner 2 GB, älteste Rohdaten werden zuerst gelöscht.
  Dazu je Minute mit Autopilot ohne Manöver: `bug` (Wind von BB/StB), `geradeaus_ruder` (mittlere Ruderanzeige,
  Anzeige-Fehler +2,9° nicht abgezogen), `drehung` (°/s). Ändern sich die Spalten, wird die alte Tagesdatei `…-1.csv`.
- **Leitstand** (`leitstand.py` 00.01, Desktop-Symbol „Leitstand Autopilot“ am Master, Tasten 1–4): Seite 1 Lage, Ruderbalken, Verlauf
  10 min in Ampelfarben; Seite 2 „Güte“ (AP-Health, Umwelt, Ruder-Trimm, Gesamtampel 60 min); Seite 3 schaltet Regler und Satz
  (Rückfrage, Bestätigung) und zeigt alle Meldungen; Seite 4 „Geräte“: oben Internet (alle 3 s geprüft), darunter alle Geräte
  des Netzes 10.10.10.0/24 mit IP (grün online, rot offline, gelb neu) nach `geraete.csv` (Kennung = MAC-Adresse oder Anfang, IP, Name, Funktion).
  Bekannte Geräte werden alle 5 s angepingt, die Suche nach neuen (254 Rundrufe) läuft nur bei offener Seite 4: einmal im Stoß, dann alle 60 s verteilt.
  Daten älter als 10 s: alles grau, roter Balken „NICHT VERBUNDEN“ mit Ursache auf jeder Seite. ~10 % eines Kerns, ohne Summer.
- Kopie im Projekt: `1-tinypilot/daten/aplog/` (für Excel: Unix-Zeit umrechnen). Last: TinyPilot 49 % frei ohne, 42 % mit Aufzeichnung.

## 9. Weitere Dokumente
- `1-tinypilot/docs/anforderungen/notloesung-A2.md` – Notlösung A2; künftige Systeme: `docs/anforderungen/`
- `0-gesamtprojekt/wissen/Weiterentwicklung PyPilot 2020-2026.md` – Änderungen seit 0.24, Verdachtsstellen
- `1-tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md` – Motor-Controller
- `0-gesamtprojekt/CHRONIK.md` – Lehren
- `CLAUDE.md` – Arbeitshinweise (Zugang, Paket ändern, Ablage)
