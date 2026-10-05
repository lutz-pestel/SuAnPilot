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
1. `TODO.md` lesen (was als Nächstes ansteht). 2. Heutiger Aufbau und Werte: `tinypilot/docs/system/Systembeschreibung.md`.
3. Letzte Tests: `tinypilot/docs/tests/`, Ablauf und Sicherheit: `tinypilot/docs/system/Testplan_Autopilot.md`. 4. Lehren: `CHRONIK.md`.
5. Neues: `suanpilot-v01.00/docs/gesamt.md`, `motor-controller/hardware/konzeption/motorcontroller.md`.
Aufzeichnung und Pumpenüberwachung (Master, Dateien, Befehle): `tinypilot/docs/system/Systembeschreibung.md`, Abschnitt 8.

## Zeilen-Obergrenzen (Regel 1 des Betreibers)
- 60: `tinypilot/rf300-interface/software/Programmbeschreibung.md`, `VERSIONEN.md`
- 80: `CLAUDE.md`, `TODO.md`, `tinypilot/regler/verbesserungen.md`, `tinypilot/docs/wissen/Weiterentwicklung PyPilot 2020-2026.md`,
  `tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md`
- 90: `fertigung/fertigungsstrategie-platinen.md`
- 100: `tinypilot/docs/anforderungen/notloesung-A2.md`, `tinypilot/docs/system/Testplan_Autopilot.md`
- 150: `CHRONIK.md` (einzige Chronik), `tinypilot/docs/system/Systembeschreibung.md`, jeder Testbericht `tinypilot/docs/tests/*.md`, `tinypilot/regler/entwurf.md`,
  `suanpilot-v01.00/docs/gesamt.md` und `suanpilot-v01.00/autopilot/hardware/konzeption/bedieneinheit.md`
- 200: `motor-controller/hardware/konzeption/motorcontroller.md`
- 300: `motor-controller/hardware/konzeption/Bauteilauswahl.md`
- 500: `wissen/Wie funktioniert ein Autopilot.md`

## Ablage
Drei gleichberechtigte Projekte im Hauptordner. Jede Baugruppe hat `hardware/` (`kicad/`, `datenblaetter/`, `konzeption/`,
`bom/`) und `software/`; gleichnamige Ordner (`docs/`, `daten/`) in einem Projekt enthalten nur dessen Inhalt.
- **`tinypilot/` = im Betrieb** (nur Fehler beheben). Baugruppen: `autopilot/` (Software `RPI/` mit `kern/`, `plattform/`,
  `bauen.sh`; `Arduino/` mit dem **veralteten** Coprozessor-Code, der aufgespielte Stand ist verschollen), `rf300-interface/`
  (Platine, Arduino-Code, `Programmbeschreibung.md`), `motor-controller/` (gekauft, **problematisch**: einseitiger Förderausfall,
  überschreibt Einstellungen; läuft noch, wird durch `motor-controller/` ersetzt; Firmware nur als Reserve).
  Dazu `regler/` (eigener Kursregler, nur SuAns Werte; hier wird programmiert), `docs/`, `daten/`, `handbuecher/` und
  `werkzeuge/` (`logger/` Kopie vom Master, `auswertung/`, `versuche/`).
- **`motor-controller/`** (Neubau, ersetzt auch den am TinyPilot): Entwurf, Anforderungen in `hardware/konzeption/`.
- **`suanpilot-v01.00/`** (künftig, nicht begonnen): `autopilot/`, `docs/`. Beide Zukunftsprojekte sind Ideensammlungen:
  **Jede Schwäche des TinyPilot dort als Anforderung aufnehmen.**
- Übergreifend: `wissen/` (Hintergrund, Marktrecherche), `handbuecher/` (Andere Schiffe, Robertson; nicht in Git),
  `fertigung/` (JLCPCB-Strategie).
- Das Paket baut man auf dem TinyPilot; `bauen.sh` setzt nur den Paketbaum aus `kern/` und `plattform/` zusammen.
- KiCad: Das alte Original (Platinen, Gerber, Pläne) liegt außerhalb, nicht Teil des Projekts:
  `E:\Users\SuAn\Cloud\My Apps\KiCad\Projects\PyPilot_KiCAD\`. `tinypilot/autopilot/hardware/kicad/` ist eine Kopie
  (Stand 05.10.2026); Netzlisten dort, z. B. `PyPilot_Main.net`.
- Karten-Images und Sicherungen: `...\uC_Raspberry\Projects\PyPilot\PyPilot_2021\PyPilot_Imgage\`.

## Versionen (alles Neue)
- Jedes neue Dokument, jede Platine, Firmware und Software trägt ihre Versionsnummer **sichtbar bei sich**, auch mit Git.
  Format immer `NN.NN` (major.minor, beide zweistellig): `v00.01`, `v01.00`. Dokument: Kopfzeile „Version NN.NN, Stand TT.MM.JJJJ"
  (Datum der letzten Änderung). Platine: Ordner `vNN.NN/` und Siebdruck. Quellen und Lieferstücke (Firmware, Pakete):
  Version im Dateinamen; technische Namen im Paket bleiben, dort Versionskonstante (Display/Log).
- Gibt es mehrere Versionen und keinen genauen Verweis, gilt immer die **letzte**.
- Dieselbe Nummer als Git-Etikett je Baugruppe: `ap-vNN.NN` Autopilot · `mc-fw-vNN.NN` Controller-Firmware · `tp-hw-vNN.NN` TinyPilot-Platinen ·
  `mc-hw-vNN.NN` Controller-Platine · `proto-vNN.NN` Protokoll. Jede Änderung zählt die Nummer hoch.

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
