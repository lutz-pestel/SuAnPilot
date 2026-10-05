# Fahrtest Autopilot 01.10.2026 – neuer Motor-Controller, Optimierung

Daten: Master `/home/pi/aplog/data/signals_2026-10-01_065703.csv`, `events_…`, `marks.csv`;
Selbsthilfe-Logbuch auf der TinyPilot-Karte `/mnt/mmcblk0p2/servo_recovery.csv`.

## 1. Motor-Controller getauscht (vor Anker)
- Betreiber tauschte den defekten Controller (Vorwärtsrichtung ausgefallen, Bericht 30.09.) gegen einen Ersatz.
- Der Ersatz überschrieb beim Verbinden Werte im TinyPilot mit Werkswerten: Ruder-Nullpunkt 2,98 → 0,
  Maßstab −107,25 → +100 (**Richtung vertauscht**), Bereich 30 → 45, Stromgrenze 20,3 → 10 A, servo.gain 2,0 → 1,0.
- Neu kalibriert mit pypilot-Verfahren (Bereich 45: Backbord, Steuerbord, Mitte), dann Bereich 30:
  Backbord positiv wie zuvor, Mitte −0,3°. Endpunkte lagen nicht ganz am Anschlag → Grad etwa 20 % größer als am 30.09.
- servo.gain wieder 2,0; Stromgrenze auf Wunsch des Betreibers 20 A.
- Tastentest: vorwärts 9/9 und rückwärts 9/9 mit Pumpe (4,1–5,4 A), je Druck etwa 7°, Spitzen bis 8,3 A
  ohne Last; Endanschlag Backbord bei 34,6° gemeldet (richtige Seite). Selbsthilfe-Logbuch leer.

## 2. Unter Segel (Groß und Fock)
| Zeit | Kurs zum Wind (scheinbar) | Wind (Böen) | Krängung / Stampfen | Kursfehler Ø | Befund |
|---|---|---|---|---|---|
| 08:09 | 116°, raumschots | 10 (13) kn | 3° / ±0,1° | 1,6° | Pendeln 14–17 s, Ruder ±7–12° |
| 08:18 | 77° | 12 (14) kn | 6° / ±0,1° | 1,0° | nach PR 0,05 → 0,0199 kaum Pendeln |
| 08:22 | 39° | 14 (19) kn | 7,5° / ±0,5° | 1,1° | |
| 08:54–09:04 | 13°, hart am Wind | 22 (28) kn | 17° / ±2,5° | 2,7° | 137 Pumpenläufe, alle gut; Ruder bis 28,9° |
- Windwinkel 12–17° hart am Wind ist unplausibel klein – Windgeber prüfen.
- Pendeln am Morgen: Werte vom 30.09. waren gegen die defekte Pumpe erhöht und mit funktionierender Pumpe zu stark.

## 3. Optimierung hart am Wind (09:13–10:12, Betreiber am Ruder)
Ziel: Kursfehler Ø ≤ 4° und ≤ 2 % über 10°, dabei möglichst wenig Pumpenarbeit. Je Schritt 4 min, ein Wert.
Bedingungen durchweg 20–21 kn (Böen 24–27), Windeinfall 13–17°, Krängung 14–17°, Stampfen ±2,1–3,0°.
| Schritt | Fehler Ø | >10° | Wechsel/min | Läufe/min | Pumpe | Ergebnis |
|---|---|---|---|---|---|---|
| Ausgang (DD 0,1013, gain 2,0) | 3,1° | 1,0 % | 29 | 38 | 62 % | |
| DD 0,05 | 2,8° | 0,2 % | 19 | 35 | 57 % | behalten |
| DD 0,02 | 3,5° | 5,1 % | 18 | 33 | 57 % | verworfen |
| servo.period 0,4 | 4,0° | 2,3 % | 12 | 30 | 62 % | verworfen |
| D 0,24 | 3,4° | 2,8 % | 19 | 33 | 58 % | verworfen |
| PR 0,01 | 2,7° | 0,7 % | 23 | 37 | 57 % | verworfen |
| servo.gain 1,6 | 3,6° | 0,4 % | 18 | 34 | 54 % | behalten |
| Drehrate-Filter 0,1 | 3,2° | 0,4 % | 14 | 31 | 53 % | **behalten – Bestwert** |
| Drehrate-Filter 0,05 | 4,5° | 4,4 % | 7 | 30 | 66 % | verworfen (zu träge) |
| R 0,01 | 3,8° | 2,4 % | 16 | 31 | 62 % | verworfen (R wirkt auf eigene Befehle von vor 1 s) |
- Ursache der Pumpenarbeit: Das Schiff giert im Wellentakt (2,6 s = Stampfperiode); pypilot steuert jeder Welle nach.
- Zwischenstand: servo.gain 1,6, Drehrate-Filter 0,1, übrige Werte wie Ausgang außer DD 0,05.
- Ideen des Betreibers (Trend statt Welle, Trimmlage wie Robertson J300) als SuAnPilot R5/R6 aufgenommen.

## 4. Zweite Optimierung nach Trend (10:32–11:05)
- Analyse: Trend (20-s-Mittel) lag nur 1,2° neben dem Soll; 79 % der Pumpenläufe begannen bei Trend < 2°,
  ihre Richtung passte nur in 49 % zum Trend → die meiste Pumpenarbeit galt dem Wellengieren.
- Neues Gütemaß: Trend im Mittel ≤ 2°, nie länger über 5°; Wellengieren zählt nicht.
| Schritt | Trend Ø | Wechsel/min | Pumpe | Strom | Ergebnis |
|---|---|---|---|---|---|
| Ausgang (gain 1,6) | 1,0–1,2° | 13 | 56 % | 2,7 A | |
| Drehrate-Filter 0,05 | 1,3° | 6,5 | 76 % | 3,8 A | verworfen (länger) |
| servo.gain 1,3 / 1,0 / 0,8 | 0,8 / 0,7 / 0,8° | 12 / 11 / 7 | 50 / 41 / 36 % | 2,3 / 1,9 / 1,7 A | besser |
| servo.gain 0,6 / 0,5 | 1,4 / 2,0° | 5 / 5 | 26 / 19 % | 1,1 / 0,9 A | Grenze erreicht |
| **servo.gain 0,7** | **1,0°** | **5,5** | **27 %** | **1,2 A** | **behalten** (Stampfen nur ±1,0°) |
- Betreiber: „Die Pumpe ist kaum noch zu hören.“

## 5. Krängungs-Glied H (ab 11:13)
- Neues Glied in `pilots/basic.py`: Befehl += H × (−Änderung der geglätteten Krängung, zusätzlich über 3 s gemittelt).
  Bei Geschwindigkeitsbefehlen ergibt das eine Ruder-Trimmlage proportional zur Krängung, vorausschauend in Böen.
- H 0,1 zu schwach (Beitrag ~1/30 von D). Wechseltest H 0 / 0,5 je 2 × 4 min auf Halbwind (14–15 kn,
  Krängung 7–8°): nur 6 Böen, Anluven 6° bzw. 5°, Pumpe und Trend gleich → **nicht eindeutig**,
  bei mehr Wind wiederholen. H 0,5 bleibt.
- Wechseltest wiederholt 13:10–13:27, hart am Wind 16–17 kn, Krängung 10,5–11,5°, je 2 × 4 min:
  H 0: 9 Böen, Anluven Ø 8,6° (max 11,8°), Trend 2,1/1,5°, Pumpe 26/21 %.
  H 0,5: 6 Böen, Anluven Ø 4,5° (max 8,4°), Trend 1,1/1,7°, Pumpe 23/22 %.
  **Krängungs-Glied halbiert das Anluven in Böen**, in beiden Durchgängen; Pumpe nicht mehr.
- Filter jetzt dauerhaft gespeichert (`boatimu.py`). Endstand nach Neustart 12:18, ohne Nachsetzen geprüft:
  P 0,02 · I 0,05 · D 0,27 · DD 0,05 · PR 0,0199 · R 0 · H 0,5 · FF 1,6141 · servo.gain 0,7 · period 0,3 ·
  Strom 20 A · Drehrate-Filter 0,1.
