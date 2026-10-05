# Versionen – was läuft wo

Version 00.01, Stand 05.10.2026. Format der Nummern und Regeln: `CLAUDE.md`, Abschnitt „Versionen".

## An Bord (TinyPilot)
| Baugruppe | Version | Beleg |
|---|---|---|
| Autopilot-Software (Paket `pypilot.tcz`) | `ap-v00.01` | Git-Etikett `ap-v00.01`; Prüfsumme (md5) e528fdce66f957e201d6b75a6c7ca597, am 05.10.2026 vom Gerät geholt |
| darin Regler `suan` | 00.03 | Datei gleich `suan_v3_vor_2026-10-04.py` (357 Zeilen), Vergleich am 05.10.2026 |
| Platinen (Main, General, RF300-Interface) | keine Version vergeben | Betreiber nennt die Stände |
| Motor-Controller (gekauft) | Firmware-Stand unbekannt | Faktendokument: `tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md` |
| RF300-Interface (Arduino-Code) | keine Version vergeben | `tinypilot/rf300-interface/software/` |

## Arbeitsstand (nicht an Bord)
| Baugruppe | Version | Ort |
|---|---|---|
| Regler `suan` | 00.04 | `tinypilot/regler/suan.py`, nicht aufgespielt |

## Reglerfassungen und Pakete
- 00.01 = Paket `bak-2026-10-03-suan-v1` (259 Zeilen) · 00.02 = `bak-2026-10-03-suan-v2` (288 Zeilen) · 00.03 = an Bord (357 Zeilen).
- Alle Paketstände liegen in Git (`tinypilot/autopilot/software/RPI/kern/`, Geschichte der Datei) und als Dateien in
  `tinypilot/daten/Pakete/2026-10-05_TinyPilot/optional/`.

## Rückweg
- Original pypilot 0.24: `pypilot.tcz.orig-2026-09-29` (md5 870560c74e2947e34ef703448d86de1f). Aufspielen: `CLAUDE.md`,
  Abschnitt „TinyPilot (im Betrieb)".

## Noch offen
- Git-Etiketten für Platinen und Firmware (`tp-hw-vNN.NN`, `mc-hw-vNN.NN`, `mc-fw-vNN.NN`, `proto-vNN.NN`): brauchen die Stände vom Betreiber.
