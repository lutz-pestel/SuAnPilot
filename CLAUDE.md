# CLAUDE.md

## Projekt
Selbstgebauter Autopilot für ein 15-Tonnen-Schiff mit Hydrauliksteuerung, auf Basis von
TinyPilot mit pypilot 0.24 (Stand 14.03.2020, eigene Änderungen siehe unten). Die Anlage ist eingebaut.
Seit dem Controllertausch und der Optimierung am 01.10.2026 steuert sie deutlich besser (Testbericht); Ziel ist,
sie weiter zu verbessern und daraus die künftige Hardware SuAnPilot abzuleiten.
Das Projekt liegt in Git (lokal), hat kein Build-System und keine automatischen Tests.

## Goldene Regel (gilt für alle Projektteile)
**Ein Kommando ist erst beendet, wenn seine Ausführung überprüft wurde.**

## Einstieg für neue Sitzungen
1. `TODO.md` lesen (was als Nächstes ansteht). 2. Heutiger Aufbau und Werte: `docs/system/Systembeschreibung.md`.
3. Letzte Tests: `docs/tests/`, Ablauf und Sicherheit: `docs/system/Testplan_Autopilot.md`. 4. Lehren: `CHRONIK.md`.
5. Nachfolger: `docs/anforderungen/` (Einstieg `gesamt.md`).
Aufzeichnung und Pumpenüberwachung (Master, Dateien, Befehle): `docs/system/Systembeschreibung.md`, Abschnitt 8.

## Zeilen-Obergrenzen (Regel 1 des Betreibers)
- 60: `tinypilot/rf300-interface/Programmbeschreibung.md`
- 80: `CLAUDE.md`, `TODO.md`, `docs/regler/verbesserungen.md`, `docs/wissen/Weiterentwicklung PyPilot 2020-2026.md`,
  `tinypilot/motorcontroller-hersteller/Motor_Controller_Fakten.md`
- 90: `suanpilot/fertigungsstrategie-platinen.md`
- 100: `docs/anforderungen/notloesung-A2.md`, `docs/system/Testplan_Autopilot.md`
- 150: `CHRONIK.md` (einzige Chronik), `docs/system/Systembeschreibung.md`, jeder Testbericht `docs/tests/*.md`, `docs/regler/entwurf.md`,
  `docs/anforderungen/gesamt.md` und `docs/anforderungen/bedieneinheit.md`
- 200: `docs/anforderungen/motorcontroller.md`
- 300: `suanpilot/motorcontroller/Bauteilauswahl.md`
- 500: `docs/wissen/Wie funktioniert ein Autopilot.md`

## Ablage
- `Handbuecher/` (PyPilot, Andere Schiffe, Motor-Controller, Robertson; nicht in Git): PDFs zu Bedienung und Vorbildern.
- **`tinypilot/` = im Betrieb** (nur Fehler beheben): `hardware/` (GPIO-Belegung, KiCad-Platinen), `rf300-interface/`
  (eigenes Arduino-Programm, `Programmbeschreibung.md`), `coprozessor/`, `motorcontroller-hersteller/`
  (gekaufter Controller: Code **nur als Reserve** in `firmware/`, Faktendokument).
- **`suanpilot/` = Entwurf** (alles Neue, mit Versionsnummer): `motorcontroller/` (Bauteilauswahl, Blockschaltbild);
  Fertigung bei JLCPCB: `suanpilot/fertigungsstrategie-platinen.md`.
- Gemeinsam für beide: `autopilot/`, `werkzeuge/`, `docs/`.
- `werkzeuge/logger/`: Kopie von Aufzeichnung, Pumpenüberwachung, Leitstand (Master); `werkzeuge/auswertung/`.
- `werkzeuge/versuche/`: eigenständige Probeprogramme, keine automatischen Tests.
- `Software/pypilot_Fork/`: eigener Fork von 0.24; `docs/regler/verbesserungen.md` = Liste zu testender Verbesserungen.
- `autopilot/suan-regler/`: eigener Kursregler (Neuentwicklung, nur SuAns eigene Werte) samt Messprogrammen; Entwurf in `docs/regler/entwurf.md`.
- `docs/anforderungen/`: Nachfolger. `gesamt.md` (Gesamtbeschreibung), `bedieneinheit.md` (Pi mit Standard-Betriebssystem),
  `motorcontroller.md` (Controller + Interface); `docs/wissen/`: Hintergrund und Marktrecherche.
- Beide Zukunftsprojekte sind Ideensammlungen: **Jede Schwäche des TinyPilot dort als Anforderung aufnehmen.**
- `tinypilot/coprozessor/TinyPilot_Coprocessor/`: **veralteter** Code des Tasten-/Display-Arduinos (Pro Mini 3,3 V
  auf PyPilot_Main_RS422). Der aufgespielte Code ist verschollen; Verhalten weicht nachweislich ab.

## Versionen (alles Neue)
- Jedes neue Dokument, jede Platine, Firmware und Software trägt ihre Versionsnummer **sichtbar bei sich**, auch mit Git:
  Dokument: Kopfzeile „Version X.Y, Datum"; Platine: Ordner `vX.Y/` und Siebdruck; Code: Versionskonstante (Display/Log).
- Dieselbe Nummer als Git-Etikett je Baugruppe: `ap-vX.Y` Autopilot · `mc-fw-vX.Y` Controller-Firmware · `tp-hw-vX.Y` TinyPilot-Platinen ·
  `mc-hw-vX.Y` Controller-Platine · `proto-vX.Y` Protokoll. Jede Änderung zählt die Nummer hoch.
- KiCad-Dateien (Platinen mit Gerber-Dateien, Verdrahtungspläne) liegen außerhalb:
  `E:\Users\SuAn\Cloud\My Apps\KiCad\Projects\PyPilot_KiCAD\` (Verbindungen am schnellsten aus `PyPilot_Main.net`).
- Karten-Images und Sicherungen: `...\uC_Raspberry\Projects\PyPilot\PyPilot_2021\PyPilot_Imgage\`.

## TinyPilot (im Betrieb)
- Master (OpenPlotter): `ssh pi@10.10.10.1`. Cockpit-Kartenplotter (RPi, OpenCPN): `ssh pi@10.10.10.187`.
  TinyPilot: Name `box`, feste Adresse 10.10.10.164 (DHCP-Reservierung in `/etc/dnsmasq.conf` am Master, Sicherung `.bak-2026-10-05`); SSH-Zugang und Befehle vom PC: `CLAUDE.local.md` (nur lokal).
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
