# Fahrtest Autopilot 03.10.2026 – Vermessung SuAn, eigener Regler „suan“, Pumpenfehler rückwärts

Daten: Master `/home/pi/aplog/data/signals_2026-10-03_*.csv`, `guete_2026-10-03.csv`, `marks.csv`, Pumpenläufe; TinyPilot
`/mnt/mmcblk0p2/servo_recovery.csv`. Werkzeuge: `autopilot/suan-regler/` (`ident.py`, `sim.py`, `kalib.py`, `fehlertest.py`, `live.py`).
Bedingungen: 08:36–09:38 Motor (spätestens ab 09:17 mit Groß), glattes Wasser, Wind 5–10 kn, SOG 6–6,7 kn; Halse 09:22;
09:38–10:44 nur Groß, 4–5 kn, Wind 9–15 kn, Kurs zum Wind 131–162°, Seegang 1; ab 10:44 Groß + gereffte Genua, 5–5,7 kn.

## 1. Vermessung (Modell T·dṙ + r = K·Ruder, Anzeige um 1 s versetzt)
Rudersprünge von Hand gingen nicht (Steuermann korrigiert am Rad, Ruder bleibt nicht liegen; keine Kupplung).
Stattdessen `ident.py`: Modell je Minute an beliebige Ruderbewegungen angepasst; nur Minuten mit Güte > 0,85 gewertet.
| Fahrt | Drehung je Grad Ruder | Anlaufzeit T | Minuten |
|---|---|---|---|
| 6,0–6,7 kn (Motor, Motor + Groß, beide Bugs) | meist 0,33–0,44 °/s (Spanne 0,29–0,67) | meist 4,5–5,5 s (bis 9,5) | 13 |
| 4,2–4,7 kn (nur Groß) | 0,21–0,26 °/s | 6–6,5 s | 3 (Güte nur 0,78–0,88) |
- Ruderwirkung etwa proportional zur Fahrt (Exponent ~1). Rudergeschwindigkeit Autopilot: vorwärts 6,3–6,9 °/s, rückwärts 3,9–4,0 °/s.
- Geradeaus-Ruder (Anzeige): Motor + Groß Wind von BB +0,9…+1,3°, Wind von StB ~+4,4°; nur Groß −9…−12°;
  Groß + gereffte Genua −9,7° (eine Minute) – die Genua nimmt Luvgierigkeit weg.

## 2. Messlatte „basic“: 10°-Kurswechsel (Ziel ±2° / Überschwingen)
| Bedingung | Anluven | Abfallen |
|---|---|---|
| Motor + Groß, 6,6 kn, Wind von BB ~118° | 8–11 s / 0–2,8° | 11–12 s / 0–1,7° |
| Motor + Groß, 6,0 kn, Wind von StB ~80° | 9–12 s / 0,8–1,2° | **28–31 s** / 0–0,9° |
| nur Groß, 4,1–4,7 kn, Wind von BB 131–145° | 11–16 s / 2–6° | 10–27 s / 1,6–3° |

## 3. Eigener Regler „suan“ (Ruderlage-Regler, Entwurf `docs/regler/entwurf.md`)
Startwerte aus Abschnitt 1 per Simulation: k_ref 1,0 (bei 6,5 kn, mit Fahrt angepasst), Tg 2 s, Drehrate Kurswechsel 1,5 °/s.
Kurshalten, nur Groß, 4,9–5,7 kn, Kurs zum Wind 145–156° (Vergleich „basic“ 09:48–09:52 unter gleichen Bedingungen):
| Stand | Kurs-Trend | Pumpe Ø | Wechsel/min |
|---|---|---|---|
| „basic“ | 0,8–1,1° | 1,6–3,0 W | 2–3 |
| suan, Trimm-Zeit T_I 240 s | 2,4–3,5° (bleibender Versatz) | 3,9–7,7 W | 2–9 |
| suan, T_I 60 s, Totband 1,5° | 0,4–1,2° | 4,0–9,3 W | 9–21 |
| suan, T_I 60 s, Totband 2,5° | 0,7–1,2° | 2,5–5,4 W | 2–8 |
- Kurswechsel suan (4,8 kn): Abfallen 6–16 s (schneller als „basic“), aber Überschwingen 3,4–8,5°.
- Betreiber hörte bei Kurswechseln ein **dunkles Brummen** („wie ein festgehaltener Motor“); 43 Pumpenumkehrungen
  nach 0,2–0,6 s Pause bei 5–7 A. → v2: Mindestpause 1 s vor Umkehr; Simulation mit gemessenem Wellengieren
  (Drehrate-Streuung 0,41 °/s, Periode 2,6–4,4 s) bildet das Überschwingen nach (5–6° gerechnet, 3,4–8,5° gemessen).
- v2-Test 10:48–10:53: Überschwingen 5–6°; 10:52:54–10:53:10 Pumpe rückwärts mit 1,4 A, Ruder 0,5–1,4 °/s →
  17,8° Überschwingen, suan schaltete selbst auf „basic“ (Abweichung Schätzung/Anzeige).
- v3 (11:24 installiert, **nicht getestet**): lernt Rudergeschwindigkeit je Richtung, gleicht Schätzung an die Anzeige
  an statt abzubrechen, meldet „Pumpe schwach“; „basic“ erst bei „Ruder folgt nicht“. Simulation: weitersteuern bei
  25 % Förderung rückwärts, Übergabe nach ~2,5 s bei totem Rückwärtslauf.

## 4. Pumpenfehler rückwärts (beide Regler, seit mindestens 02.10.)
- Zeitweise läuft die Pumpe **nur rückwärts** mit ~1,4 A statt ~4 A; Ruder 0,5–1,4 statt ~4 °/s. Controller bekommt vollen
  Befehl, keine Fehlermeldung, 26,8 °C, Bordspannung 12,6 V. Vorwärts nie.
- Selbsthilfe „Pumpe steht, rückwärts“: 02.10. 9×, 03.10. 19×. Läufe rückwärts ≥ 1 s mit Strom < 2,5 A: Wind von BB
  29 von 65, Wind von StB 30 von 39 – beide Bugs, also abhängig von der Pumpenrichtung, nicht von Luv/Lee.
- „basic“ merkt es kaum (kurze Stöße 0,4 s, regelt nur den Kurs) – vermutlich Ursache des langsamen Abfallens in Abschnitt 2.
- Betreiber: Brummen auch bei langsamem Antrieb. Der Controller fährt die Spannung über eine Rampe hoch
  (`servo.max_slew_speed` 29,9 %). Ölmangel unwahrscheinlich (Vorrat im höher liegenden Steuerstand, Handsteuerung geht).
- Altes Gerät (bis 30.09.): Ausfall **vorwärts**; Ersatzgerät: Schwäche **rückwärts** – eher Controller-Endstufe oder
  Richtungsabhängiges in der Pumpe als ein gemeinsamer Kabel-/Motorfehler (Folgerung, nicht gemessen).
- Verdacht (offen): zu wenig Spannung am Motor (Rampe, Kabel, Kontakte, Endstufe), Kohlen/Kollektor, klemmendes
  Sperrventil der AP-Pumpe. **Entscheidend:** Spannung an den Motorklemmen beim Brummen messen; Klopftest am Motor.

## 5. Sonstiges
- TinyPilot nach Neustart unter neuer Adresse 10.10.10.164 (DHCP); `setzen.py` sucht ihn über den Master.
- Pakete auf der Karte: `pypilot.tcz.bak-2026-10-03-vor-suan`, `…-suan-v1`, `…-suan-v2`; aktiv suan v3, „basic“ gewählt.
- Endstand: „basic“ P 0,005 · I 0,08 · D 0,22 · DD 0,05 · PR 0,01 · FF 2,5 · H 0,5 · servo.gain 1,0 (unverändert).
