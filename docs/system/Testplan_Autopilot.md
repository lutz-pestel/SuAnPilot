# Testplan Autopilot im Automatik-Betrieb

Ziel: Kurshalteleistung messen, Probleme finden, Reglerwerte schrittweise verbessern.
Vorbereitet am 29.09.2026. Systemaufbau siehe `Doc/Systembeschreibung.md`.

## Sicherheit
- Freies Wasser, wenig Verkehr, ruhige bis mäßige Bedingungen.
- Ein Steuermann ist jederzeit bereit: Taste AUTO schaltet den Autopiloten ab; Stromschalter bekannt.
- Claude ändert Werte nur nach Zustimmung des Betreibers, immer **einen** Wert, in kleinen Schritten.
- Nach jeder Wertänderung mindestens 60 s warten, bevor ausgeschaltet wird (Speichertakt).

## Aufzeichnung
- Beschrieben in `Doc/Systembeschreibung.md`, Abschnitt 8. Markierung je Testabschnitt:
  `ssh pi@10.10.10.1 /home/pi/aplog/aplog.sh mark "Text"`. 10/s mit `APLOG_PERIOD=0.1` (38 % frei).
- Werte ändern: pypilot-Server `10.10.10.163:23322` (Adresse per DHCP, Name `box`), Zeile
  `ap.pilot.basic.D=0.25`. Ausgangswerte stehen unten.

## Ausgangswerte (29.09.2026, Regler „basic“, Modus „compass“)
| Wert | Stand | Hinweis |
|---|---|---|
| P / I / D | 0,0099 / 0 / 0,3013 | D über der Grenze heutiger pypilot-Versionen (0,24) |
| DD / PR / FF / R | 0,1013 / 0,0199 / 1,6141 / 0 | |
| servo.period / gain | 0,3 / 2,0 | |
| servo.speed.min / max | 100 / 100 | Pumpe immer volle Drehzahl |
| servo.max_current | 20,31 A | |
| servo.faults | 57 | Zählerstand vor dem Test |
| imu.heading_offset | 94,0 | |

## Ablauf
1. **Vorbereitung:** Aufzeichnung starten; Uhr des TinyPilot prüfen (wird vom Master gestellt).
2. **Vorprüfung (10 min):** gerade Fahrt in 4 Richtungen, Kompasskurs mit GPS-Kurs vergleichen;
   Ruder einmal hart Backbord und hart Steuerbord (Ruderlage ±30°?).
3. **Ausgangslage (15 min):** Kurs halten mit den Ausgangswerten, zwei Kurse zu Wind und Welle.
4. **Sprungtests:** Sollkurs +10°, −10°, +30° (Tasten). Auswertung: Überschwingen, Einschwingzeit, Pendeln.
5. **Optimieren**, je 5–10 min pro Änderung, danach Auswertung:
   a) D schrittweise Richtung 0,24; b) P; c) servo.period. Jede Änderung mit Markierung.
6. **Abschluss:** beste Werte festhalten, Aufzeichnung stoppen, Lehre in `CHRONIK.md`.

## Auswertung (je Abschnitt; Manöver und Standby werden nicht bewertet)
**Gütemaß:** Kurs-Trend Ø in ° (20-s-Mittel, ohne Wellengieren) · Pumpenleistung Ø in W (Strom × Spannung)
· Richtungswechsel der Pumpe pro Minute (Verschleiß) · Anteil der Zeit > 10° neben dem Kurs (Ausreißer).
Dazu bei Bedarf: Pendelperiode, Stromspitzen, neue Servo-Störungen, Selbsthilfe-/Pumpenbefunde.
**Bedingungen** – verglichen wird nur bei gleichen:
- SOG (Fahrtsensor durchs Wasser unzuverlässig, nicht verwenden).
- Wind: Stärke (leicht < 10, mittel 10–18, stark > 18 kn) und Böigkeit.
- Kurs zum Wind (am Wind < 60°, halb 60–110°, raum 110–150°, vor dem Wind > 150°); gilt zugleich als Wellenrichtung.
- Seegang nach Stampfen: 0 glatt < ±0,3° · 1 leicht ±0,3–0,8° · 2 mäßig ±0,8–1,5° · 3 grob > ±1,5°
  (Bewegung des Schiffs, nicht Wellenhöhe; Grenzen vorläufig).
- Krängung: Höhe, Änderung und Ursache – Böe (einseitig, langsam, mit Wind) · Welle (Rollen im Wellentakt)
  · Kurve (eigene Drehung). Segelfläche ergibt sich aus SOG und Krängung.
- Antrieb (Segel / Motor / Motorsegeln) als Angabe des Betreibers; Betriebsart und Manöver werden erkannt.

## Bekannte Verdachtsstellen (siehe `Doc/Weiterentwicklung PyPilot 2020-2026.md`)
- Servo-Logik von 0.24 (später mehrfach korrigiert), hoch eingestellte Reglerwerte.
- 57 Servo-Störungen ohne bekannte Ursache.
- Ruderlage ~1 s verzögert (für den Kursregler laut Chronik nicht maßgeblich – im Test prüfen).
- Kompass-Kalibrierung aktualisiert sich laufend (Alter beim Test im Hafen: ~10 min).
- Freie Rechenzeit des TinyPilot schon ohne Aufzeichnung nur etwa 50 %.

## Offen vor dem Test
- Ist der PC an Bord im WLAN des Masters? Fahrt unter Motor oder Segel?
