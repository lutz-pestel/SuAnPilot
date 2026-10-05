# CLAUDE.md

## Projekt
Selbstgebauter Autopilot für ein 15-Tonnen-Schiff mit Hydrauliksteuerung, auf Basis von
TinyPilot mit pypilot 0.24 (Stand 14.03.2020, eigene Änderungen siehe unten). Die Anlage ist eingebaut.
Seit dem Controllertausch und der Optimierung am 01.10.2026 steuert sie deutlich besser (Testbericht); Ziel ist,
sie weiter zu verbessern und daraus den Nachfolger SuAnPilot abzuleiten.
Das Projekt hat kein Git, kein Build-System und keine automatischen Tests.

## Goldene Regel (gilt für alle Projektteile)
**Ein Kommando ist erst beendet, wenn seine Ausführung überprüft wurde.**

## Einstieg für neue Sitzungen
1. `TODO.md` lesen (was als Nächstes ansteht). 2. Heutiger Aufbau und Werte: `Doc/Systembeschreibung.md`.
3. Letzte Tests: `Doc/Tests/`, Ablauf und Sicherheit: `Doc/Testplan_Autopilot.md`. 4. Lehren: `CHRONIK.md`.
5. Nachfolger: `Projekt SuAnPilot/` (Einstieg `Docs/`).
Aufzeichnung und Pumpenüberwachung (Master, Dateien, Befehle): `Doc/Systembeschreibung.md`, Abschnitt 8.

## Zeilen-Obergrenzen (Regel 1 des Betreibers)
- 60: `Software/RF300_Interface/Programmbeschreibung.md`
- 80: `CLAUDE.md`, `TODO.md`, `Software/pypilot_Fork/Verbesserungen.md`, `Doc/Weiterentwicklung PyPilot 2020-2026.md`,
  `Software/Motor_Controller_pypilot/Motor_Controller_Fakten.md`
- 100: `Doc/Anforderungen.md`, `Doc/Testplan_Autopilot.md`
- 150: `CHRONIK.md` (einzige Chronik), `Doc/Systembeschreibung.md`, jeder Testbericht `Doc/Tests/*.md`, `Software/SuAn_Regler/Entwurf.md`,
  in `Projekt SuAnPilot/` jedes Dokument in `Docs/` und `SuAnPilot/Projektdokument.md`
- 200: `Projekt SuAnPilot/Motor_Controller_Neubau/Projektdokument.md`
- 250: `Doc/Wie funktioniert ein Autopilot.md`
- 300: `Projekt SuAnPilot/Motor_Controller_Neubau/Bauteilauswahl.md`
- 500: `Doc/Wie funktioniert ein Autopilot.md`

## Ablage
- `Doc/`, `Operating PyPilot in General/`, `Implementationen auf anderen Schiffen/`: PDFs zu Bedienung und Vorbildern.
- `Hardware/`: GPIO-Belegung TinyPilot, Motor-Controller (Schaltplan, Datenblatt, beschriftetes Foto).
- `Software/RF300_Interface/`: eigenes Arduino-Programm, beschrieben in `Programmbeschreibung.md`.
- `Software/Autopilot_Logger/`: Kopie von Aufzeichnung, Pumpenüberwachung, Leitstand (Master); `Auswertung/`.
- `Software/Tests/`: eigenständige Probeprogramme, keine automatischen Tests.
- `Software/Motor_Controller_pypilot/`: Code des Motor-Controllers **nur als Reserve**, samt Faktendokument.
- `Software/pypilot_Fork/`: eigener Fork von 0.24; `Verbesserungen.md` = Liste zu testender Verbesserungen.
- `Software/SuAn_Regler/`: eigener Kursregler (Neuentwicklung, nur SuAns eigene Werte); `Entwurf.md`, später Code.
- `Projekt SuAnPilot/`: Nachfolger. `Docs/` (Gesamtbeschreibung), `SuAnPilot/` (Bedieneinheit, Wunsch ESP32),
  `Motor_Controller_Neubau/` (Controller + Interface); Anforderungen je Teilprojekt im Projektdokument.
- Beide Zukunftsprojekte sind Ideensammlungen: **Jede Schwäche des TinyPilot dort als Anforderung aufnehmen.**
- `Software/TinyPilot_Coprocessor/`: **veralteter** Code des Tasten-/Display-Arduinos (Pro Mini 3,3 V
  auf PyPilot_Main_RS422). Der aufgespielte Code ist verschollen; Verhalten weicht nachweislich ab.
- KiCad-Dateien (Platinen mit Gerber-Dateien, Verdrahtungspläne) liegen außerhalb:
  `E:\Users\SuAn\Cloud\My Apps\KiCad\Projects\PyPilot_KiCAD\` (Verbindungen am schnellsten aus `PyPilot_Main.net`).
- Karten-Images und Sicherungen: `...\uC_Raspberry\Projects\PyPilot\PyPilot_2021\PyPilot_Imgage\`.

## TinyPilot (im Betrieb)
- Master (OpenPlotter): `ssh pi@10.10.10.1`. Cockpit-Kartenplotter (RPi, OpenCPN): `ssh pi@10.10.10.187`.
  TinyPilot: Name `box`, DHCP (wechselt, zuletzt 10.10.10.164; aktuell in `/var/lib/misc/dnsmasq.leases` am Master); SSH-Zugang und Befehle vom PC: `CLAUDE.local.md` (nur lokal).
  `/home/tc` liegt im RAM: nach jedem Neustart leer (Arbeitsordner zum Packen neu anlegen).
- Werte lesen/setzen: pypilot-Server Port 23322, Textprotokoll (`watch={...}`, `name=wert`).
- Uhr: ~1 min nach Start vom Master-GPS gestellt (eigenes `/opt/gpsdate.py` im Startarchiv `tce/mydata.tgz`;
  Archiv nur Eintrag für Eintrag ändern, sonst ändern sich Ordnerrechte). Tastenprotokoll: `/var/log/pypilot_hat/current`.
- pypilot läuft aus dem schreibgeschützten Paket `tce/optional/pypilot.tcz`, nicht aus dem
  Git-Verzeichnis. Ändern: mit `unsquashfs` auspacken, ändern, mit `mksquashfs -comp gzip -b 131072`
  packen, `.md5.txt` erneuern, neu starten. Original: `pypilot.tcz.orig-2026-09-29` (Karte und PC).
- Eigene Änderungen am Paket: `hat/page.py` (Notlösung A2), `servo.py` (Korrektur 11/2021; Selbsthilfe
  bei stehender Pumpe: nur Melden), `pilots/basic.py` (Krängungs-Glied H),
  `boatimu.py` (Filter gespeichert). Sicherungen: `pypilot.tcz.bak-2026-09-30`, `…bak-2026-10-01-heel`, `…bak-2026-10-01-selbsthilfe`, `…bak-2026-10-02-vor-abhilfe-aus`.
- Motor-Controller: fertig gekauft, Firmware wird nicht neu aufgespielt; Ersatzgerät seit 01.10.2026.
  Ein neuer Controller überschreibt beim Verbinden Ruder-Kalibrierung, Stromgrenze und servo.gain – prüfen.
