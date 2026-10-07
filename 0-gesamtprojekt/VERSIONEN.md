# Versionen – was läuft wo

Version 00.04, Stand 06.10.2026. Format der Nummern und Regeln: `CLAUDE.md`, Abschnitt „Versionen".

## An Bord (TinyPilot)
| Baugruppe | Version | Beleg |
|---|---|---|
| Autopilot-Software (Paket `pypilot.tcz`) | `ap-v00.03` | Prüfsumme (md5) 5093ed0ad1c92d3f3252704d052d6966; aufgespielt am 05.10.2026 im Hafen, Autopilot aus; Git-Etikett `ap-v00.03` |
| darin Regler `adaptive` | 00.05 | Datei `1-tinypilot/regler/adaptive.py` |
| Platinen (Main, General, RF300-Interface) | keine Version vergeben | Betreiber nennt die Stände |
| Motor-Controller (gekauft) | Firmware-Stand unbekannt | Faktendokument: `1-tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md` |
| RF300-Interface (Arduino-Code) | keine Version vergeben | `1-tinypilot/rf300-interface/software/` |

## Am Master (Aufzeichnung und Leitstand)
| Programm | Version | Beleg |
|---|---|---|
| Aufzeichnung `aplog.py` | 00.01 | `1-tinypilot/werkzeuge/logger/`, am Master seit 06.10.2026; Version in `aplog.log` |
| Leitstand `leitstand.py` | 00.01 | wie oben; Version im Fenstertitel |

## Reglerfassungen und Pakete
- 00.01 = Paket `bak-2026-10-03-suan-v1` · 00.02 = `bak-2026-10-03-suan-v2` · 00.03 = bis 05.10.2026 an Bord (Paket `ap-v00.01`)
  · 00.04 = Paket `ap-v00.02` (Regler hieß noch `suan`) · 00.05 = an Bord seit 05.10.2026 (Paket `ap-v00.03`, Regler heißt `adaptive`).
- Die 34 gespeicherten Reglerwerte wurden am 05.10.2026 von `ap.pilot.suan.*` nach `ap.pilot.adaptive.*` kopiert und einzeln geprüft;
  die alten Zeilen stehen noch in der Einstellungsdatei und sind ohne Wirkung. Sicherung: `1-tinypilot/daten/sicherung/`.
- Alle Paketstände liegen in Git (`1-tinypilot/autopilot/software/RPI/kern/`, Geschichte der Datei) und als Dateien in
  `1-tinypilot/daten/Pakete/2026-10-05_TinyPilot/optional/`.

## Rückweg
- Zurück auf `ap-v00.02`: Auf dem TinyPilot liegt `pypilot.tcz.bak-2026-10-05-vor-00.05` (md5 4e92d81c8ca35d80b283edbf94c35251)
  unter `/mnt/mmcblk0p2/tce/optional/`. Aufspielen über Kopie und Umbenennen (nicht die laufende Datei überschreiben), `.md5.txt` erneuern, neu starten.
- Original pypilot 0.24: `pypilot.tcz.orig-2026-09-29` (md5 870560c74e2947e34ef703448d86de1f).

## Noch offen
- Git-Etiketten für Platinen und Firmware (`tp-hw-vNN.NN`, `mc-hw-vNN.NN`, `mc-fw-vNN.NN`, `proto-vNN.NN`): brauchen die Stände vom Betreiber.
