# Versionen – was läuft wo

Version 00.02, Stand 05.10.2026. Format der Nummern und Regeln: `CLAUDE.md`, Abschnitt „Versionen".

## An Bord (TinyPilot)
| Baugruppe | Version | Beleg |
|---|---|---|
| Autopilot-Software (Paket `pypilot.tcz`) | `ap-v00.02` | Git-Etikett `ap-v00.02`; Prüfsumme (md5) 4e92d81c8ca35d80b283edbf94c35251; aufgespielt am 05.10.2026 im Hafen, Ruder frei |
| darin Regler `suan` | 00.04 | Datei `tinypilot/regler/suan.py` |
| Platinen (Main, General, RF300-Interface) | keine Version vergeben | Betreiber nennt die Stände |
| Motor-Controller (gekauft) | Firmware-Stand unbekannt | Faktendokument: `tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md` |
| RF300-Interface (Arduino-Code) | keine Version vergeben | `tinypilot/rf300-interface/software/` |

## Reglerfassungen und Pakete
- 00.01 = Paket `bak-2026-10-03-suan-v1` · 00.02 = `bak-2026-10-03-suan-v2` · 00.03 = bis 05.10.2026 an Bord (Paket `ap-v00.01`)
  · 00.04 = an Bord seit 05.10.2026 (Paket `ap-v00.02`).
- Gespeicherte Reglerwerte an Bord blieben beim Aufspielen unverändert (`delay` 0,4, `db` 1,5, `lern` 0,4); neu ist `t_lern` mit Standardwert 1,0.
- Alle Paketstände liegen in Git (`tinypilot/autopilot/software/RPI/kern/`, Geschichte der Datei) und als Dateien in
  `tinypilot/daten/Pakete/2026-10-05_TinyPilot/optional/`.

## Rückweg
- Zurück auf `ap-v00.01`: Auf dem TinyPilot liegt `pypilot.tcz.bak-2026-10-05-vor-00.04` (md5 e528fdce66f957e201d6b75a6c7ca597)
  unter `/mnt/mmcblk0p2/tce/optional/`. Aufspielen über Kopie und Umbenennen (nicht die laufende Datei überschreiben), `.md5.txt` erneuern, neu starten.
- Original pypilot 0.24: `pypilot.tcz.orig-2026-09-29` (md5 870560c74e2947e34ef703448d86de1f).

## Noch offen
- Git-Etiketten für Platinen und Firmware (`tp-hw-vNN.NN`, `mc-hw-vNN.NN`, `mc-fw-vNN.NN`, `proto-vNN.NN`): brauchen die Stände vom Betreiber.
