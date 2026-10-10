# CLAUDE.md

## Projekt
**SuAn-Autopilot-Projekt** (`0-gesamtprojekt/SuAn-Autopilot-Projekt.md`): neues Autopilot-System für die SuAn (15 t, Hydraulik), ersetzt
den alten Robertson AP300CX. Ein Projekt, drei Phasen: 1 TinyPilot-Ersatzsystem testen, 2 neuer Motor-Controller, 3 SuAnPilot.
Eingebaut ist heute der TinyPilot mit pypilot 0.24 (Stand 14.03.2020, eigene Änderungen siehe unten).
Das Projekt liegt in Git (lokal), hat kein Build-System und keine automatischen Tests.

## Goldene Regel (gilt für alle Projektteile)
**Ein Kommando ist erst beendet, wenn seine Ausführung überprüft wurde.**

## Einstieg für neue Sitzungen
1. Gesamtprojekt: `0-gesamtprojekt/SuAn-Autopilot-Projekt.md`. 2. `0-gesamtprojekt/TODO.md` (was als Nächstes ansteht). 3. Heutiger Aufbau und Werte:
`1-tinypilot/docs/system/Systembeschreibung.md`. 4. Letzte Tests: `1-tinypilot/docs/tests/`, Ablauf und Sicherheit:
`1-tinypilot/docs/system/Testplan_Autopilot.md`. 5. Lehren: `0-gesamtprojekt/CHRONIK.md`. 6. Phasen 2 und 3: `2-motor-controller/hardware/konzeption/motorcontroller.md`, `3-suanpilot/docs/gesamt.md`.
Aufzeichnung und Pumpenüberwachung (Master, Dateien, Befehle): `1-tinypilot/docs/system/Systembeschreibung.md`, Abschnitt 8.

## Zeilen-Obergrenzen (Regel 1 des Betreibers)
- 60: `1-tinypilot/rf300-interface/software/Programmbeschreibung.md`, `0-gesamtprojekt/VERSIONEN.md`, `99-tools/docs/Robnet.md`
- 80: `0-gesamtprojekt/SuAn-Autopilot-Projekt.md`, `CLAUDE.md`, `0-gesamtprojekt/TODO.md`, `1-tinypilot/regler/verbesserungen.md`, `1-tinypilot/regler/entwurf_pumpenleistung.md`, `0-gesamtprojekt/wissen/Weiterentwicklung PyPilot 2020-2026.md`,
  `1-tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md`, `99-tools/robnet-analyse/hardware/konzeption/robnet-analyse.md`
- 90: `0-gesamtprojekt/fertigung/fertigungsstrategie-platinen.md`
- 100: `1-tinypilot/docs/anforderungen/notloesung-A2.md`, `1-tinypilot/docs/system/Testplan_Autopilot.md`, `99-tools/docs/messgeraet.md`
- 150: `0-gesamtprojekt/CHRONIK.md` (einzige Chronik), `0-gesamtprojekt/Fehlersystematik und Reaktionen.md`, `1-tinypilot/docs/system/Systembeschreibung.md`, jeder Testbericht `1-tinypilot/docs/tests/*.md`, `1-tinypilot/regler/entwurf.md`,
  `3-suanpilot/docs/gesamt.md` und `3-suanpilot/autopilot/hardware/konzeption/bedieneinheit.md`
- 200: `2-motor-controller/hardware/konzeption/motorcontroller.md`
- 350: `2-motor-controller/hardware/konzeption/Bauteilauswahl.md`
- 500: `0-gesamtprojekt/wissen/Wie funktioniert ein Autopilot.md`

## Ablage
Ein Projekt, drei Phasen; je Phase ein Ordner, dazu `0-gesamtprojekt/` und `99-tools/`. Im Hauptordner sonst nur, was die Werkzeuge dort
erwarten (`CLAUDE.md`, `CLAUDE.local.md`, `.gitignore`, `.mcp.json`, `.claude/`). Jede Baugruppe hat `hardware/` (`kicad/`, `datenblaetter/`, `konzeption/`,
`bom/`, `3d-modelle/`) und `software/`; gleichnamige Ordner (`docs/`, `daten/`) in einer Phase enthalten nur deren Inhalt.
Datenblätter und Zeichnungen der Hersteller in `datenblaetter/` (nicht in Git), Name `Hersteller_Teilnummer_Ausgabe.pdf`; keine eigene Liste, die Links stehen in der Bauteilauswahl.
3D-Modelle der Hersteller (STEP) in `3d-modelle/` (nicht in Git); Ziel: Gesamtmodell der Platine für das Gehäuse.
- **`1-tinypilot/` = Phase 1, im Betrieb** (nur Fehler beheben). Baugruppen: `autopilot/` (Software `RPI/` mit `kern/`, `plattform/`,
  `bauen.sh`; `Arduino/` mit dem **veralteten** Coprozessor-Code, der aufgespielte Stand ist verschollen), `rf300-interface/`
  (Platine, Arduino-Code, `Programmbeschreibung.md`), `motor-controller/` (gekauft, **problematisch**: einseitiger Förderausfall,
  überschreibt Einstellungen; läuft noch, wird durch `2-motor-controller/` ersetzt; Firmware nur als Reserve).
  Dazu `regler/` (eigener Kursregler, nur SuAns Werte; hier wird programmiert), `docs/`, `daten/` und
  `werkzeuge/` (`logger/` Kopie vom Master, `auswertung/`, `versuche/`).
- **`2-motor-controller/`** (Phase 2, Neubau, ersetzt auch die RF300-Interfaceplatine): Anforderungen in `hardware/konzeption/`.
  Schaltplan `hardware/kicad/v00.01/` (KiCad 10): Dateien nur bei geschlossenem KiCad ändern; danach `kicad-cli sch erc` und `pruefung_blockschaltbild.py`.
- **`3-suanpilot/`** (Phase 3, nicht begonnen): `autopilot/`, `docs/`. Phasen 2 und 3 sind Ideensammlungen:
  **Jede Schwäche des TinyPilot dort als Anforderung aufnehmen.** Versionsnummern erst im Unterordner `vNN.NN/`.
- **`0-gesamtprojekt/`** (gilt für alle Phasen): `SuAn-Autopilot-Projekt.md`, `CHRONIK.md`, `TODO.md`, `VERSIONEN.md`,
  `wissen/` (Hintergrund, Marktrecherche, pypilot-Geschichte), `handbuecher/` (PyPilot, Andere Schiffe, Robertson; nicht in Git),
  `fertigung/` (JLCPCB-Strategie).
- **`99-tools/`** (Werkzeuge für alle Phasen, gleicher Aufbau): `docs/`, Baugruppe `messgeraet/` (Strom und Spannung, Projektplan `docs/messgeraet.md`), Baugruppe `robnet-analyse/` (Robertson-Bus mitlesen, `docs/Robnet.md`).
- Das Paket baut man auf dem TinyPilot; `bauen.sh` setzt nur den Paketbaum aus `kern/` und `plattform/` zusammen.
- KiCad: Das alte Original (Platinen, Gerber, Pläne) liegt außerhalb, nicht Teil des Projekts:
  `E:\Users\SuAn\Cloud\My Apps\KiCad\Projects\PyPilot_KiCAD\`. `1-tinypilot/autopilot/hardware/kicad/` ist eine Kopie
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
