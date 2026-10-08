# Hafen 08.10.2026 – Pumpe rückwärts: Drehzahl und Bordspannung

Version 00.01, Stand 08.10.2026. Hafen, Autopilot im Standby, Ruder frei. Pumpe über `1-tinypilot/regler/diagnose.py`
(Befehl `servo.command`), Drehzahl über `servo.speed.min/max` (danach immer zurück auf 100 %, zurückgelesen).
Rohdaten: Scratchpad der Sitzung (`lauf*_roh.csv`, `grenze*`, `wiederh*`, `umschalt*`, `laden*`). Vorwärts = Ruder nach
Backbord (Anzeige +), rückwärts = Ruder nach Steuerbord. Multimeter des Betreibers an der Klemmleiste des Controllers.

## 1. Batterie allein (Ruhe 12,6–12,7 V)
| Lauf, je 5 s | Klang | Strom | Ruder | Versorgung im Lauf (Multimeter / Controller) | Ergebnis |
|---|---|---|---|---|---|
| Rückwärts 100 % (10:15, 10:17, 10:26) | Brummen | 1,0–1,3 A | 1,3–1,9° | 12,05–12,3 / 12,2–12,4 V | gestört |
| Rückwärts 60 % (10:23, 10:31) | Surren | 2,7–2,8 A | 12,2–13,8° | 11,5–11,7 / 11,5–11,8 V | normal |
| Vorwärts 100 % (10:29) | Surren | 4,5–5,1 A | 19,7° | 11,4 / 10,9 V | normal |
| Vorwärts 60 % (10:35) | Surren | 2,6–2,8 A | 14,0° | 11,6 / 11,6–11,8 V | normal |
- Im gestörten Lauf an der Pumpe ~1,5 V (Betreiber) bei ~1,1 A: stehender Motor (~1,4 Ω, wie 04.10.). Der Controller bekommt
  über 12 V und gibt 1,5 V weiter – der Verlust liegt in seiner Endstufe.
- Vorab: Ruder stand bei +38,5° (über dem Bereich 30°); beim Zurückfahren waren alle 24 Rückwärtsstöße gestört.

## 2. Grenzdrehzahl rückwärts (Batterie, Ruhe 12,65 V)
| Einstellung | 100 % | 99 % | 95 % | 90 % | 85 % | 80 % |
|---|---|---|---|---|---|---|
| Befehl an den Controller (Kalibrierung 0,2 + 0,8 × Drehzahl) | 1,00 | 0,99 | 0,96 | 0,92 | 0,88 | 0,84 |
| Ergebnis | gestört | gestört | gestört | gestört | normal (4 von 4) | normal (3 von 3) |
- Normal: 85 % 4,05–4,11 A, 18–19° in 5 s; 80 % 3,77–3,80 A, 17° in 5 s. Gestört: 1,1 A, unter 2°.
- Gegenprobe im selben Lauf (vorher vorwärts, 20 s Pause): 100 % 3 s gestört (1,08 A), ohne Stopp 85 % sofort normal
  (4,02 A, 3,8 °/s), dann 80 % normal. Der vorangehende Vorwärtslauf hilft nicht; Absenken wirkt sofort im Lauf.

## 3. Mit Landstrom-Ladegerät (Ruhe 14,0 V)
| Einstellung | 100 % | 99 % | 95 % | 90 % | 85 % | 80 % | Umschalten 100/85/80 % |
|---|---|---|---|---|---|---|---|
| Strom | 6,23 A | 6,24 A | 6,25 A | 6,21 A | 4,35 A | 4,07 A | 6,19 / 4,38 / 4,06 A |
| Versorgung im Lauf | 11,9 V | 12,1 V | 12,1 V | 12,1 V | 12,7 V | 12,7 V | 12,0 / 12,7 / 12,6 V |
- Alle normal, Ruder 26–28° in 5 s bei 90–100 %. Rückwärts versagt also nur bei niedriger Bordspannung.
- Entscheidend ist die Spannung **vor** dem Einschalten: 100 % lief bei 11,9 V im Lauf (Ladegerät), versagte bei 12,2 V im
  Lauf (Batterie). Leitungs- und Kontaktwiderstände sind nicht die Ursache; vorwärts lief sogar bei 10,9 V im Lauf.

## 4. Vergleich mit Schaltung und Firmware: Designfehler oder kaputt?
Plan `1-tinypilot/motor-controller/hardware/datenblaetter/hydraulic_controller.pdf`, Firmware-Reserve `motor.ino` (2021;
der Stand auf dem Gerät ist unbekannt).
- **Rückwärts schaltet Seite B oben** (Q3, Treiber U3, Bootstrap C6 0,22 µF, Diode D1 1N4001), Seite A unten (Q2).
  Vorwärts: Q1/U2/C5/D2 oben, Q4 unten.
- **Die Firmware wechselt ab Befehl 0,90 in einen „Dauer-Ein“-Betrieb:** 62,5 Hz statt 16 kHz; der Bootstrap wird nur
  einmal je Takt mit einem Puls von zwei Totzeiten nachgeladen. Unter 0,90 pulst die Brücke mit 16 kHz und lädt in jedem
  Takt nach. **Gemessene Grenze: 0,88 läuft, 0,92 versagt – genau dieser Wechsel.**
- **Das Brummen passt dazu:** reicht die Hilfsspannung nicht, schaltet der obere Transistor im 62,5-Hz-Takt aus und ein.
- **Bewertung:**
  - Grundursache ist ein **Designfehler**: kurzer Ladepuls bei Dauer-Ein, kleiner Kondensator (0,22 µF) und langsame Diode.
    Bei 14 V reicht die Reserve, bei 12,6 V nicht. Neuere pypilot-Controller (2022/2024) haben 10 µF und schnelle Dioden.
  - Dass nur **eine Seite** ausfällt, kommt aus der Streuung oder Alterung eines Teils auf Seite B (C6, D1, U3, Q3). Code
    und Plan sind für beide Seiten gleich. Das Altgerät fiel auf der anderen Seite aus (vorwärts, 30.09.).
  - **Nicht kaputt** im engeren Sinn: Unter Befehl 0,90 und bei 14 V arbeitet Seite B einwandfrei. Ein defektes Teil
    versagte immer.
  - Das Ersatzgerät lief am 01.10. in beide Richtungen; seither hat sich Seite B verschlechtert oder die Bordspannung war
    damals höher. Nicht geklärt.

## 5. Ergebnis und Entscheidungen
1. Ursache: Endstufe des gekauften Controllers im Dauer-Ein-Betrieb (Befehl ≥ 0,90), rückwärts, bei Bordspannung um 12,6 V.
2. Überbrückung: Pumpe unter Befehl 0,90 halten. Höchstdrehzahl 80 % (Befehl 0,84) läuft mit Abstand; entschieden wird
   die **adaptive Pumpenleistung je Richtung** (`1-tinypilot/regler/entwurf_pumpenleistung.md`). Bis dahin 80 % möglich.
3. Kein tieferer Entladeversuch: Unterwegs kann die Maschine jederzeit laden (Betreiber).
4. Neuer Controller: Pololu G2 mit Ladungspumpe (F9) behebt diesen Mechanismus; Nachweis im Abnahmetest (F14 f).

## 5a. Adaptive Pumpenleistung und Autopilot-Betrieb (Abend, Paket `ap-v00.05`)
- Dauerlauf rückwärts voll (Programm, 12,82 V): Absenkung 100 → 95 → 90 → 85 %, danach 4,3 A und Ruder läuft. Erkennung
  anfangs zu langsam (gestörtes Ruder kroch 0,3–0,7 °/s); Schwelle seitdem abhängig von der Grenze. Grenzen nicht gespeichert.
- **Autopilot basic gibt auch bei 30° Abweichung nur Stöße von ~0,5 s** (volle Leistung). Rückwärts einzelne Stöße gestört
  (1,1 A), Ruder 0,55 °/s; vorwärts 1,0 °/s. Die Erkennung (braucht ≥ 2 s Dauerlauf) griff nie.
- **Entscheidung (Betreiber): feste Höchstdrehzahl 80 % beide Richtungen** (`servo.speed.min/max = 80`, gespeichert;
  Befehl 0,84). Autopilot-Test ±30°: rückwärts 1,06 °/s, vorwärts 1,01 °/s, Stöße 2,0–4,8 A. Rückweg: beide Werte auf 100.
- Handsteuerung per Taste im Standby: halbe Geschwindigkeit (Befehl 0,6), unter der Fehlergrenze, funktioniert.
  Die alte Selbsthilfe meldet dabei „Pumpe steht“ (feste Grenze 2,5 A > 2,3 A normal) – Fehlalarm.

## 6. Offen
- Fahrtest mit begrenzter Drehzahl: steuert der Autopilot gut genug, wie oft wird abgesenkt?
- Welcher Firmware-Stand auf dem Gerät läuft (die Grenze bei 0,90 passt zur Reserve, ist aber kein Beweis).
- Vorwärts-Grenze bei niedriger Spannung nicht gemessen (vorwärts lief heute immer).
