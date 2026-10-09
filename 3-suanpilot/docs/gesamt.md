# Projekt SuAnPilot – Gesamtbeschreibung

**Ideensammlung.** Noch nicht gestartet; jede Anforderung wird vor Projektstart einzeln geprüft.
Version 00.02, Stand: 09.10.2026. Grundlage sind die Erfahrungen mit dem heutigen TinyPilot (pypilot 0.24),
beschrieben in `1-tinypilot/docs/system/Systembeschreibung.md` und `1-tinypilot/docs/tests/` des Hauptprojekts.

## 1. Ziel
SuAnPilot ist die künftige Hardware; die Autopilot-Software läuft auf TinyPilot und später auf SuAnPilot.
Ein eigener Autopilot für das 15-t-Schiff mit Hydrauliksteuerung:
- steuert wie ein guter Rudergänger – nach dem Trend, nicht nach jeder Welle; um eine Trimmlage, die
  sich aus der Krängung ergibt; mit möglichst wenig Pumpenarbeit;
- ist fehlertolerant: erkennt jede Abweichung vom Soll, hilft sich selbst, meldet, führt Buch;
- arbeitet autonom, auch ohne WLAN und Master; alle Software liegt im Projekt.

## 2. Komponenten
| Komponente | Ort | Aufgabe | Teilprojekt |
|---|---|---|---|
| SuAnPilot-Bedieneinheit | Steuerstand (im Freien) | Kursregler, Lage-/Kompasssensor, eine größere Anzeige, ≥ 4 Tasten, Weboberfläche, Aufzeichnung | `SuAnPilot/` |
| Motor-Controller mit Interface | Motorraum | H-Brücke (handelsüblich), Pumpenansteuerung, Strommessung, RF300-Frequenz → Ruderlage, NMEA-Ruderlage | `2-motor-controller/hardware/konzeption/motorcontroller.md` |
| Stromversorgung | Motorraum | 12-V-Bordnetz für Pumpe und Elektronik | `2-motor-controller/hardware/konzeption/motorcontroller.md` |
| Hydraulikpumpe | Motorraum | vorhanden, seit Jahren mit Robertson J300 bewährt | – |
| Ruderlagengeber RF300 | Ruder | vorhanden (Robertson), liefert Frequenz | – |
| Ruderlagenanzeige | Steuerstand | vorhanden, empfängt NMEA-Ruderlage – **vorrangig** | – |
| Master (OpenPlotter) | Navigation | optional: GPS, Wind, WLAN, Kartenplotter | – |

## 3. Zusammenwirken
```
 Steuerstand                                   Motorraum
 ┌──────────────────────┐   RS422 (8-adriges  ┌────────────────────────────┐
 │ SuAnPilot             │   Kabel, vorhanden) │ Motor-Controller + Interface│── Pumpe
 │ Regler, Sensor,       │◄──────────────────►│ H-Brücke, Strom, Ruderlage  │◄─ RF300
 │ Anzeige, Tasten, Web  │  Befehle / Messwerte│ NMEA-Ruderlage ─────────────┼─► Ruderlagenanzeige
 └──────────▲───────────┘                     └────────────────────────────┘
            │ WLAN (falls vorhanden; sonst eigener Zugangspunkt für die Weboberfläche)
       Master (GPS, Wind)
```
- **Befehle** gehen von der Bedieneinheit zum Controller; **Messwerte** (Ruderlage, Strom, Spannung,
  Temperatur, Störungen) zurück. Protokoll ist frei wählbar (offener Punkt).
- **Ruderlage** wird im Controller direkt aus der RF300-Frequenz gewonnen – ohne die heutige zweifache
  Umwandlung und ohne die gemessene Verzögerung von etwa 1 s.
- Die **NMEA-Ruderlage** zur Anzeige läuft im Controller unabhängig weiter, auch wenn die Bedieneinheit
  oder die Verbindung ausfällt.
- **GPS und Wind** kommen, wenn vorhanden, vom Master; die Steuerung hängt aber von keinem anderen Dienst ab.
- **Aufzeichnung** aller Mess- und Stellwerte in der Bedieneinheit, auswertbar auch nachträglich.

## 4. Aufteilung der Fehlertoleranz (offen)
Fehler, Symptome und Reaktionen: `0-gesamtprojekt/Fehlersystematik und Reaktionen.md` im Hauptprojekt.
Welche Prüfungen im Controller liegen (Strom, Ruderbewegung, Verbindungsverlust) und welche in der
Bedieneinheit (Kurs, Sensor-Plausibilität, Selbsthilfe, Buchführung), ist noch festzulegen.

## 5. Dokumente
- `3-suanpilot/autopilot/hardware/konzeption/bedieneinheit.md` – Anforderungen an die Bedieneinheit (B, U, R, L, Z, W) und Nachbesserungsbedarf gegenüber pypilot 0.24.
- `2-motor-controller/hardware/konzeption/motorcontroller.md` – Anforderungen an Controller und Interface (F, S).
- Kursregler (Kern von V1.0, läuft vorher schon im TinyPilot): `1-tinypilot/regler/entwurf.md` im Hauptprojekt.
- Lehren des Hauptprojekts: `0-gesamtprojekt/CHRONIK.md`; Aufgaben am heutigen TinyPilot: `0-gesamtprojekt/TODO.md`.
