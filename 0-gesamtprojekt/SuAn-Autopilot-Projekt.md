# SuAn-Autopilot-Projekt

Version 00.03, Stand 14.10.2026, Obergrenze 80 Zeilen.
Übersicht über das Gesamtprojekt auf hohem Niveau: Anlass, die zwei Wege, alle Unterprojekte. Einzelheiten stehen in den
Dokumenten der Unterprojekte (Abschnitte 5 und 6).

## 1. Anlass
- An Bord ist ein Autopilot **Robertson AP300X**: Hauptgerät J300X im Motorraum (im Projekt kurz „J300"), Bedieneinheit
  AP300CX am Steuerstand. Er steuert seit 17 Jahren sehr gut.
- Das Problem ist nur die **Bedieneinheit** (Modelle laut Handbuch: AP300CX, AP300PX, AP300DLX): Das LCD ist kaum noch abzulesen, Tasten
  funktionieren kaum oder nicht mehr, Ersatzteile gibt es nicht mehr.
- Der Robertson bleibt bis zum Ende des Projekts angeschlossen und als Rückfall nutzbar.
- Er ist der **Maßstab**: Alles Neue muss mindestens so gut und so zuverlässig steuern.

## 2. Die zwei Wege
Beide lösen dasselbe Problem auf verschiedene Art. Welcher am Ende an Bord bleibt, ist nicht entschieden.

| | Weg A: Neuentwicklung Autopilot auf der Basis von TinyPilot | Weg B: Bedieneinheit für Robertson |
|---|---|---|
| Idee | Ein neuer, eigener Autopilot ersetzt den Robertson | Der Robertson regelt weiter; nur die Bedieneinheit wird neu gebaut |
| Ordner | `1-tinypilot`, `2-motor-controller`, `3-suanpilot` | `10-Robertson-Bedieneinheit` |
| Stand | TinyPilot im Betrieb, neuer Motor-Controller begonnen | Konzept der Analyse-Platine fertig, nichts gebaut |

## 3. Weg A: Neuentwicklung auf der Basis von TinyPilot
Ziel: ein Autopilot für die SuAn (15 t, Hydraulik mit Pumpe RPU160, Ruderlagengeber RF300), der das Schiff unter allen
Bedingungen, auf allen Kursen und bei jeder Wellengröße sicher steuert.
- **Heutiges Ersatzsystem:** TinyPilot (pypilot 0.24) am Steuerstand mit eigener Hardware, Kursregler und Lagesensor;
  gekaufter pypilot-Motor-Controller im Motorraum (erwartet 0–5 V vom Ruderlagengeber); selbst entwickelte
  RF300-Interfaceplatine (wandelt die RF300-Frequenz in diese Spannung, gibt die Ruderlage für die Anzeige aus).
- **Phase 1 – Ersatzsystem testen (läuft):** Schwächen von TinyPilot, Controller und Platine finden; jede Schwäche wird
  Anforderung für Phase 2 oder 3.
- **Phase 2 – neuer Motor-Controller (begonnen):** ersetzt gekauften Controller und Interfaceplatine gemeinsam, liest
  den RF300 direkt, bleibt mit dem TinyPilot voll verträglich.
- **Phase 3 – SuAnPilot (nicht begonnen):** ersetzt den TinyPilot, ohne Arduino und Coprozessor, mit nur einem LCD.
- **Übergang 2 → 3:** erst wenn Motor-Controller und TinyPilot nach **Seetests** (Bedingungsraster: Kurs zum Wind,
  Wellengröße, Krängung; Maßstab Robertson) zur vollen Zufriedenheit steuern. Termine gibt es keine.

## 4. Weg B: Bedieneinheit für Robertson
Ziel: eine neue Bedieneinheit, gebaut auf ESP32 oder Raspberry Pi Zero, die an die Stelle der alten tritt.
- **Grundlage (Handbuch AP300X, Abschnitt 1.1):** Das „Gehirn" ist das Hauptgerät J300; es spricht über das Robnet mit allen
  anderen Geräten. Die Bedieneinheit bedient und zeigt nur an. Bis zu 7 Bedieneinheiten sind an einem System zulässig.
- **Voraussetzung:** Hardware und Protokoll der Verbindung J300 ↔ Bedieneinheit (**Robnet**) kennen; das Handbuch nennt
  es nicht. Die Robnet-Analyse (Platine zum Mitlesen aller 6 Adern, mit Richtungserkennung) klärt das.
- **Umfang der ersten Fassung** (Tasten: 4 Stück mit Mehrfachbelegung):

| Senden (Tasten) | Empfangen (Anzeige, Ton) |
|---|---|
| Ein/Aus, Standby ↔ AP-Mode, Sollkurs ±1° und ±10° | Ruderlage, Alarm, Sollkurs |

- Weitere Funktionen aus dem Handbuch kommen später. Senden ans J300 ist erst nach der Analyse ein Thema.

## 5. Unterprojekte im Überblick
| Ordner | Weg | Was es ist | Stand |
|---|---|---|---|
| `1-tinypilot` | A, Phase 1 | Ersatzsystem im Betrieb; hier nur Fehler beheben und testen | läuft |
| `2-motor-controller` | A, Phase 2 | Neubau Controller, ersetzt auch die RF300-Interfaceplatine | begonnen (Schaltplan) |
| `3-suanpilot` | A, Phase 3 | Ersatz des TinyPilot; Ideensammlung | nicht begonnen |
| `10-Robertson-Bedieneinheit` | B | Baugruppe `robnet-analyse` (Platine, die den Robnet-Bus mitliest) | Konzept |
| `99-tools` | beide | Werkzeuge: Messgerät (Strom, Spannung), Wissen zum Robnet | Messgerät: Idee |
| `0-gesamtprojekt` | beide | diese Übersicht, Aufgaben, Chronik, Handbücher, Fertigung | laufend |

## 6. Wo was steht
| Thema | Ort |
|---|---|
| A: Aufbau und Werte TinyPilot | `1-tinypilot/docs/system/Systembeschreibung.md` |
| A: Testablauf, Testberichte | `1-tinypilot/docs/system/Testplan_Autopilot.md`, `1-tinypilot/docs/tests/` |
| A: Kursregler | `1-tinypilot/regler/` |
| A: Motor-Controller (Anforderungen, Bauteile) | `2-motor-controller/hardware/konzeption/` |
| A: SuAnPilot | `3-suanpilot/docs/gesamt.md` |
| B: Robnet-Analyse (Konzept, Einstieg Abschnitt 0) | `10-Robertson-Bedieneinheit/robnet-analyse/hardware/konzeption/robnet-analyse.md` |
| B: Robnet-Wissen, Messwerte | `99-tools/docs/Robnet.md` |
| Robertson-Handbücher, Pumpe | `0-gesamtprojekt/handbuecher/Robertson/` |
| Aufgaben, Lehren | `0-gesamtprojekt/TODO.md`, `0-gesamtprojekt/CHRONIK.md` |
