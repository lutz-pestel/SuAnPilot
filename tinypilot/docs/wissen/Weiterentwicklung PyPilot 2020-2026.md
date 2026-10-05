# Weiterentwicklung PyPilot 2020–2026

## Ausgangslage
- Eingebaut: pypilot **0.24**, Git-Stand a7143e5 vom **14.03.2020**. Karte und Image
  `20210921_pypilot_jlx12864_4GB.img` sind im Stand gleich; das Image-Datum ist nur das Kopiedatum.
- Aktuell (September 2026): pypilot **0.71**. Dazwischen liegen 915 Änderungen
  (2020: 66, 2021: 309, 2022: 128, 2023: 148, 2024: 82, 2025: 16, 2026: 166).
- Grundlage: Beschreibungen aller Änderungen, Code von etwa zehn ausgewählten Änderungen,
  `pypilot.conf` von der Karte.

## Eingestellte Werte (pypilot.conf der Karte)
| Wert | Anlage | Grundwert 0.24 | Grenze heute |
|---|---|---|---|
| Regler P (Kursfehler) | 0,0099 | 0,003 | 0,03 |
| Regler D (Drehrate) | 0,3013 | 0,09 | **0,24** |
| Regler DD | 0,1013 | 0,075 | 0,24 |
| Regler PR | 0,0199 | 0,005 | 0,02 |
| Regler FF (Vorsteuerung) | 1,6141 | 0,6 | 2,4 |
| Regler I, R | 0 | 0,005 / 0 | entfallen |

Außerdem: `servo.faults` = 57, `servo.hardover_time` = 2,14 s, `servo.speed.min` = `max` = 100,
`servo.period` = 0,3, `servo.gain` = 2,0, `rudder.range` = 30, Modus „compass“, Regler „basic“.

## Befunde nach Bereich
### 1. Servo-Logik (Ansteuerung von Pumpe und Ruder) – wichtigster Verdacht
- 0.31 (07.09.2021): Die Windup-Logik (Sammeln kleiner Stellbefehle bis zum Pumpenstoß) bei
  Richtungswechsel und langsamer Bewegung wurde korrigiert. In 0.24 ist der alte Stand.
- 04.11.2021: Die Zeitlogik, wann Stellbefehle verfallen, wurde korrigiert.
  05.11.2021: Verrauschte Strommessung wird gefiltert. Ob das mit den 57 Störungen zusammenhängt, ist offen.
- 23.09.2022: Die fehlerhafte Schätzung der Ruder-Laufzeit („hardover time“) wurde entfernt.
  In 0.24 ist sie aktiv, wirkt aber nur, wenn die Ruderlage ungültig ist. 2,14 s erscheint für
  15 t mit Hydraulik sehr kurz (Vermutung, nicht geprüft).

### 2. Kursregler „basic“
- Heute vereinfacht: Die Anteile I und R sind entfernt, die Einstellbereiche enger.
- Das eingestellte D (0,30) liegt über der heutigen Grenze von 0,24. Schluss daraus, nicht belegt:
  Der Entwickler hält so hohe Werte nicht mehr für sinnvoll.
- Integralrechnung 2023 und 2026 überarbeitet; bei I = 0 ohne Bedeutung.

### 3. Kompass und Lagesensor
- 2021: Bewegungsausgleich korrigiert, eigene Taste für die Lageausrichtung, 28 statt weniger
  Kalibrierpunkte. 2022: Roll- und Nickrate korrigiert (die Drehrate für den Regler war nicht betroffen).
  2025: Filter verbessert.
- Der 2023 behobene „große Rundungsfehler“ betrifft 0.24 nicht: Damals wurden Reglerwerte mit
  4 Nachkommastellen gespeichert.

### 4. Aktuelle Entwicklung
- Mai 2026: Regler und Filter „nach Segeltests“ verbessert.
- pypilot läuft seit 2026 vollständig auf OpenPlotter.

## Offen
- Welche Änderung die Anlage tatsächlich verbessert, ist nicht bewiesen.
- Servo-Einstellungen prüfen (Drehzahl fest 100 %, `period`, `gain`, Laufzeit 2,14 s).
