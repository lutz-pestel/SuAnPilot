# TEMPORÄR – Umbauplan PyPilot-AI (nach dem Umbau löschen)

Stand: 05.10.2026. Grundlage: Bestandsaufnahme vom 05.10. (347 Dateien, 274 MB, gezählt).
Jeder Schritt in Abschnitt 8 wird einzeln vorgelegt (Regel 3). Nichts ist bisher verändert.

## 1. Begriffe (festgelegt 05.10.2026)
- **TinyPilot** = die heutige Hardware: Pi Zero mit Tiny Core, Hauptplatine PyPilot_Main_RS422, Coprozessor-Arduino,
  gekaufter Motor-Controller, RF300-Interface.
- **SuAnPilot** = die künftige Hardware (Bedieneinheit: Pi mit Standard-Betriebssystem; Motor-Controller: ESP32)
  und der Name des git-Projekts.
- **Autopilot-Software** = eine einzige; läuft auf TinyPilot (Tiny Core) und später auf SuAnPilot (Standard-System).
- **Stand 0** = SD-Karten-Image. Der heutige Stand der Software existiert nur auf dem Pi des TinyPilot.

## 2. Zielaufbau
Der ganze Ordner `PyPilot-AI` ist das git-Projekt (GitHub: lutz-pestel/SuAnPilot, privat). Nur auf dem PC, von git
ausgeschlossen: `Daten/`, `Handbuecher/`, `CLAUDE.local.md` (Zugangsdaten). Die Ordner unten liegen direkt darin.
```
PyPilot-AI/
    CLAUDE.md  CLAUDE.local.md  TODO.md  CHRONIK.md  VERSIONEN.md  .gitignore
    HAFEN_MESSUNG_RF300_TEMPORAER.md   bleibt, bis die Messung erledigt ist
    docs/
      system/                      Systembeschreibung (heutiger Aufbau an Bord), Testplan
      anforderungen/               Gesamtbeschreibung, Bedieneinheit, Motor-Controller, Notlösung A2
      regler/                      Entwurf SuAn-Regler, Verbesserungen (Fork)
      tests/                       Testberichte
      wissen/                      Wie funktioniert ein Autopilot, Weiterentwicklung pypilot, Marktrecherche
    protokoll/                     Verbindung Autopilot ↔ Motor-Controller (heute: pypilot-kompatibel, F7)
    autopilot/
      kern/                        pypilot mit allen eigenen Änderungen + SuAn-Regler, ohne Plattform-Teile
      plattform/tinypilot/         Tasten, Anzeige, Startskripte, gpsdate.py, Paketbau Tiny Core, einstellungen/
      plattform/suanpilot/         später (Standard-System)
    tinypilot/                     IM BETRIEB (nur Fehler beheben)
      motorcontroller-hersteller/  gekaufter Controller: firmware/ (motor.ino, unverändert, Reserve), Fakten
      rf300-interface/             eigener Arduino-Code, läuft heute an Bord
      coprozessor/                 Tasten-Arduino, veralteter Code (aufgespielter verschollen)
      hardware/                    KiCad: PyPilot_Main_RS422, General_Dual_Display, General_Basic, RF300_Interface (Platine);
                                   GPIO-Liste, Kabelverbindung
    suanpilot/                     ENTWURF (alles Neue mit Versionsnummer)
      motorcontroller/             Bauteilauswahl, Blockschaltbild; später test-nano/, esp32/, KiCad
      fertigungsstrategie-platinen.md   JLCPCB, Linie A (THT) und B (SMD)
    werkzeuge/
      logger/                      aplog, pumpwatch, guete, leitstand, wache, ruder (laufen am Master)
      messung/                     diagnose, messlauf 1–3, rampe, rueckw_test, kalib, ident, live, fehlertest, diag_mock
      auswertung/                  opt_eval 1–3, sprung
      simulator/                   sim.py
      versuche/                    Arduino-Probeprogramme (heute Software/Tests)
    Daten/                         Messdaten, Sicherungen, fertige Pakete – nicht in git (zu groß)
    Handbuecher/                   fremde Unterlagen (PDF, Fotos) – nicht in git
```
- **KiCad:** Das alte Original außerhalb gehört nicht zum Projekt. `tinypilot/hardware/` ist eine Kopie (Stand 05.10.2026).

## 3. Versionsregeln
- git überschreibt nie: Jeder gespeicherte Stand bleibt abrufbar.
- **Etikett** (git-Tag) für jeden Stand, der an Bord läuft oder bewährt ist. Je Baugruppe eine eigene Nummer:
  `ap-vX.Y` Autopilot-Software · `mc-fw-vX.Y` Controller-Firmware · `tp-hw-vX.Y` TinyPilot-Platinen ·
  `mc-hw-vX.Y` Controller-Platine · `proto-vX.Y` Protokoll.
- „Bewährt“ erst nach Test im Hafen und unterwegs; das Etikett nennt den Testbericht.
- **Fertige Dateien** (pypilot.tcz, Firmware, Gerber) je Version als Anhang zum Etikett auf GitHub („Release“),
  nicht im Code-Ordner. Lokal zusätzlich in `Daten/Pakete/`.
- `VERSIONEN.md` (≤ 60 Zeilen): welche Version wo läuft (an Bord, Reserve) und welche zusammenpassen.
- Rückweg: das Paket eines älteren Etiketts aufspielen.
- `main` = der Stand, der an Bord läuft oder als Nächstes laufen soll. Versuche auf eigenem Zweig.

## 4. Vom Pi holen (eigener Schritt; PC muss im Bordnetz sein)
| Teil | Wohin |
|---|---|
| `pypilot.tcz` (heute) und die Sicherungen `.orig-2026-09-29`, `.bak-2026-09-30`, `…-10-01-heel`, `…-10-01-selbsthilfe`, `…-10-02-vor-abhilfe-aus`, `…-10-03-vor-suan`, `…-suan-v1`, `…-suan-v2` | entpackt, in Zeitfolge als einzelne git-Stände in `autopilot/` |
| Eigene Dateien aus `mydata.tgz` (gpsdate.py, Startskripte), **ohne** `networking.txt` | `autopilot/plattform/tinypilot/` |
| Einstellungen `~/.pypilot/*.conf` (vorher auf Geheimnisse prüfen) | `autopilot/plattform/tinypilot/einstellungen/` |
| Liste der Tiny-Core-Pakete mit Versionen | `autopilot/plattform/tinypilot/` |
| `servo_recovery.csv` | `Daten/` |
| Betriebssystem, fremde Pakete | **nicht** – deckt das Image ab |
- Trennung kern/plattform: beim Holen festlegen, welche pypilot-Dateien von Tiny Core oder TinyPilot-Hardware abhängen
  (`hat/`, Startskripte, übersetzte Programmteile). Vorschlag wird dann einzeln vorgelegt.

## 5. Alt → neu
| Alt | Neu |
|---|---|
| `CLAUDE.md` | Zugangsdaten nach `CLAUDE.local.md` (Schritt 1), Rest bleibt |
| `TODO.md`, `CHRONIK.md` | bleiben |
| `Doc/Systembeschreibung.md`, `Doc/Testplan_Autopilot.md` | `docs/system/` |
| `Doc/Anforderungen.md` (A2) | `docs/anforderungen/notloesung-A2.md` |
| `Doc/Tests/*.md` | `docs/tests/` |
| `Doc/Wie funktioniert ein Autopilot.md`, `Doc/Weiterentwicklung PyPilot 2020-2026.md` | `docs/wissen/` |
| `Doc/*.pdf` | `Handbuecher/PyPilot/` |
| `Projekt SuAnPilot/Docs/Projektbeschreibung.md` | `docs/anforderungen/gesamt.md` |
| `Projekt SuAnPilot/Docs/Marktrecherche.md` | `docs/wissen/` |
| `Projekt SuAnPilot/SuAnPilot/Projektdokument.md` | `docs/anforderungen/bedieneinheit.md` |
| `Projekt SuAnPilot/Motor_Controller_Neubau/Projektdokument.md` | `docs/anforderungen/motorcontroller.md` |
| `…/Motor_Controller_Neubau/Bauteilauswahl.md`, `Blockschaltbild_Controller-V2.0.html` | `suanpilot/motorcontroller/` |
| `Software/SuAn_Regler/Entwurf.md` | `docs/regler/entwurf.md` |
| `Software/SuAn_Regler/suan.py` | `autopilot/kern/` (im Gerät `pilots/suan.py`) – erst Stand v3, dann heutiger Stand |
| `Software/SuAn_Regler/` Messprogramme | `werkzeuge/messung/` |
| `Software/SuAn_Regler/sim.py` · `sprung.py` · `setzen.py` | `werkzeuge/simulator/` · `auswertung/` · `messung/` |
| `Software/pypilot_Fork/pypilot/` | ersetzt durch die Stände vom Pi (Abschnitt 4) |
| `Software/pypilot_Fork/Verbesserungen.md` | `docs/regler/verbesserungen.md` |
| `Software/pypilot_Fork/pypilot.tcz-2026-10-01` | `Daten/Pakete/` |
| `Software/Autopilot_Logger/` (mit `Auswertung/`) | `werkzeuge/logger/`, `werkzeuge/auswertung/` |
| `Software/Motor_Controller_pypilot/` | `tinypilot/motorcontroller-hersteller/firmware/` (Fakten-Dokument nach `motorcontroller/docs/`) |
| `Software/RF300_Interface/` | `tinypilot/rf300-interface/` (`.doc`, `.xls` dort mit) |
| `Software/TinyPilot_Coprocessor/` | `tinypilot/coprozessor/` |
| `Software/Tests/` | `werkzeuge/versuche/` |
| `Hardware/GPIO for TinyPilot.xls` | `tinypilot/hardware/` |
| `Hardware/Motor Controller/*.pdf`, `*.png` (26 MB) | `Handbuecher/Motor-Controller/` |
| `Hardware/KiCad/` + externes Original | `tinypilot/hardware/` (Abschnitt 6) |
| `Robertson/`, `Operating PyPilot in General/`, `Implementationen auf anderen Schiffen/` | `Handbuecher/` |
| `Daten/` | bleibt |

## 6. Löschliste (erst nach Sicherung, Schritt 1)
- `Hardware/KiCad/` (Kopie): Inhalt gleich dem Original außerhalb, bis auf 10 Dateien (Projektdateien, Sicherungs-
  ordner, Verknüpfung). Übernommen wird die Vereinigung beider nach `tinypilot/hardware/`, dann Kopie löschen.
- `Software/SuAn_Regler/suan_v3_vor_2026-10-04.py`, `rampe_original.txt`: werden als früherer git-Stand gespeichert,
  danach gelöscht.
- `__pycache__/` (automatisch erzeugt), Verknüpfungen `*.lnk` (3 Stück, zeigen auf alte Orte).
- Nicht in git (`.gitignore`): KiCad-Sicherungen (`*-backups`, `*-bak`, `*.kicad_prl`, `fp-info-cache`),
  `PyPilot_Main_PCB.step` (82 MB, 3D-Modell, aus KiCad jederzeit neu erzeugbar), Zugangsdaten.

## 7. Dokumente anpassen (Regel 1: Überholtes löschen)
- Pfadverweise: 72 Zeilen in 19 Dokumenten (gezählt), alle auf den neuen Aufbau.
- „Wunsch ESP32“ für die Bedieneinheit streichen: `bedieneinheit.md` Abschnitte 1 und 4, `CLAUDE.md`.
  Neu: Bedieneinheit = Pi mit Standard-Betriebssystem.
- „SuAnPilot löst den TinyPilot ab“ umformulieren: TinyPilot ist Hardware; die Software läuft auf beiden.
- `CLAUDE.md`: Obergrenze für „Wie funktioniert ein Autopilot“ steht doppelt – 250 streichen, 500 gilt.
- `docs/regler/entwurf.md` Abschnitt 6: Code-Orte neu.

## 8. Reihenfolge (jeder Schritt einzeln vorgelegt)
1. git einrichten, `.gitignore`, Zugangsdaten nach `CLAUDE.local.md`, Prüfung, erster Stand = Zustand vor dem Umbau;
   Kopie der von git ausgeschlossenen Dateien nach `..\PyPilot-AI_Sicherung_2026-10-05\`.
2. Ordner anlegen, verschieben, löschen (Abschnitte 5 und 6).
3. Dokumente anpassen (Abschnitt 7).
4. Vom Pi holen (Abschnitt 4), Stände in Zeitfolge, Etikett `ap-v0.1` für den Stand an Bord.
5. GitHub-Projekt `SuAnPilot` anlegen (Betreiber), hochladen, Zugriff für Claude prüfen.
