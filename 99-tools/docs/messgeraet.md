# Projektplan Messgerät

Version 00.03, Stand 09.10.2026, Obergrenze 100 Zeilen. Unterprojekt in `99-tools/` (Werkzeuge für alle Phasen),
Baugruppe `99-tools/messgeraet/`. **Ideensammlung**; jeder Schritt wird dem Betreiber einzeln vorgelegt (Regel 3).

## 1. Zweck
Ein eigenes, nicht fest eingebautes Gerät misst Strom und Spannung an Bord und ist über das Netz abfragbar,
damit Claude die Werte direkt bekommt. Erste Aufgaben:
- **Pumpenstrom** zwischen Pololu und Pumpe, verglichen mit der eingebauten Messung des G2: Ist der Versatz stabil,
  wie schnell folgt sie einer Anlaufspitze? (`2-motor-controller/hardware/konzeption/Bauteilauswahl.md`, Abschnitt 2)
- **Strom der RPU160 im Betrieb beobachten**, Blockierstrom (`2-motor-controller/hardware/konzeption/motorcontroller.md`, Abschnitt 4).
- **Heute am TinyPilot:** Spannung an den Motorklemmen A/B beim Brummen (`motorcontroller.md`, Abschnitt 4, „Offene Messung“),
  Bordspannung während des Pumpenlaufs (Unterspannung, F14 in `motorcontroller.md`).
- Später: Prüfung des Motor-Controller-Neubaus (Phase 2).

## 2. Anforderungen (Vorschlag)
- M1 **Zwei Stromkanäle**, Gleichstrom, beide Richtungen. Pumpe 4–6 A, Spitzen bisher 8,3 A, bei Blockade bis zur
  Strombegrenzung (im Neubau in der Software, unter 20 A).
- M2 **Mindestens vier Spannungskanäle bis 20 V** gegen Masse (Bordspannung, Klemme A, Klemme B, frei), geschützt gegen
  Spitzen aus dem Bordnetz.
- M3 **Schnell genug für Anlaufspitzen** von wenigen Millisekunden: auf den Stromkanälen 5 000–10 000 Messungen je
  Sekunde wie beim Motor-Controller (Bauteilauswahl Abschnitt 3).
- M4 **Zugriff über das WLAN des Masters:** per SSH, Werte live abfragen und als Datei mit Zeitstempel aufzeichnen.
- M5 Versorgung aus dem 12-V-Bordnetz, verpolgeschützt.
- M6 **Ohne Eingriff in die Verkabelung**, wo möglich: Strom über eine Zange um eine Ader.
- M7 Klein und tragbar, Messleitungen mit Klemmen; verträgt Motorraum (warm, Vibration).
- M8 Gleiche Bauteile und Messtechnik wie im Motor-Controller, wo es passt (ein Ersatzteil, erprobte Schaltung).

## 3. Offene Entscheidungen
| Thema | Möglichkeit | Dafür | Dagegen |
|---|---|---|---|
| Rechner | Raspberry Pi Zero 2 W | Linux, SSH, Python, Platz für lange Aufzeichnungen; Zugriff wie beim TinyPilot | keine Analogeingänge; will heruntergefahren werden, sonst leidet die Speicherkarte |
| | ESP32 | startet sofort, verträgt Abschalten, gleicher Rechner wie der Motor-Controller | kein SSH, wenig Speicher, Programm in C++ |
| Wandler | MCP3208 (12 Bit, 8 Kanäle) | gleicher Baustein wie im Motor-Controller, schnell genug | — |
| | ADS1115 (16 Bit, 4 Kanäle) | feinere Auflösung | fest 860 Messungen je Sekunde, verfehlt kurze Spitzen |
| Stromsensor | Strommesszange: aufklappbarer Hall-Sensor, z. B. YHDC HSTS016L | keine Klemme im Leistungspfad, schnell angelegt | Nullpunkt wandert, vor jeder Messung abgleichen; Daten bisher nur vom Händler |
| | ACS758 fest eingeschleift | genau, schnell | Leitung auftrennen, zusätzliche Klemmen |
| Gehäuse | 3D-Druck ASA wie beim Motor-Controller | erprobt | — |

**Vorläufiger Vorschlag:** Pi Zero 2 W, MCP3208 und zwei Strommesszangen. Eine gute Zange wäre zugleich die bessere
Vorbereitung für den Motor-Controller als der eingeschleifte ACS758 (dort entscheiden).

## 4. Schritte
Aufwand geschätzt, nicht gemessen; jeder Schritt wird vor Beginn mit Aufwand und Kosten vorgelegt.
| Schritt | Inhalt | Ergebnis |
|---|---|---|
| 1 | Entscheidungen aus Abschnitt 3 treffen | Festlegung in diesem Plan |
| 2 | Datenblätter holen, Bauteile wählen | `messgeraet/hardware/konzeption/Bauteilauswahl.md`, `bom/` |
| 3 | Schaltplan zeichnen | `messgeraet/hardware/kicad/v00.01/` |
| 4 | Aufbau: Lochraster oder eigene Platine (entscheiden) | Gerät |
| 5 | Programm: messen, aufzeichnen, abfragen | `messgeraet/software/` |
| 6 | Prüfen an bekannten Werten (Netzteil, Multimeter), dann an Bord | Prüfbericht |

## 5. Offene Fragen
1. Wie viele Spannungskanäle wirklich? Nur gegen Masse oder auch Spannungsfall über einer Leitung (zwei Punkte)?
2. Muss das Gerät vom Bordnetz getrennt sein, wenn es an Stellen mit verschiedener Masse misst?
3. Versorgung nur aus dem Bordnetz oder auch aus einem Akku?
4. Messbereich der Zange: der kleinste, der die Blockade (bis 20 A) noch abdeckt.
5. Temperaturbereich des Rechners im Motorraum.
