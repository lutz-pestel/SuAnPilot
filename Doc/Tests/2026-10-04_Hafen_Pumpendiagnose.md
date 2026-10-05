# Hafen 04.10.2026 – Pendeln ab 6 kn (Auswertung 03.10.), Pumpen-Diagnose rückwärts

Daten: Master `signals_2026-10-03_112946.csv`; PC `Daten/diagnose/` (`diagnose_2026-10-04_085423_*`, `rueckw_*`,
`messlauf*_roh.csv`); Werkzeuge `Software/SuAn_Regler/` (`diagnose.py --auto`, `rueckw_test.py`, `messlauf*.py`, `rampe.py`).

## 1. Pendeln ab 6 kn (Fahrt 03.10., „basic“ P 0,005 · I 0,08 · D 0,22, raumschots/halber Wind, Wind von BB)
| SOG | Abschnitte à 2 min | Streuung Kursfehler | max | Ruderspanne | Pumpe an | Wind | Krängung |
|---|---|---|---|---|---|---|---|
| < 5,0 kn | 30 | 1,6° | 5,0° | 9° | 10 % | 9,2 kn | 0,2° |
| 5,0–5,5 kn | 38 | 1,6° | 4,9° | 10° | 14 % | 10,9 kn | 1,5° |
| 5,5–6,0 kn | 49 | 1,9° | 5,5° | 12° | 18 % | 11,4 kn | 1,9° |
| ≥ 6,0 kn | 16 | **3,6°** | **9,9°** | **28°** | **40 %** | 13,7 kn | 6,1° |
- **Ursache Regelkreis, nicht Welle** (2-min-Fenster, gleicher Kurs): Kurs schwingt ab 6 kn regelmäßig mit 17–21 s,
  Rollen/Stampfen mit 4,5–7 s; der ~20-s-Takt ist auch darunter da, aber gedämpft. Treiber ist die Fahrt, nicht die
  Krängung (6,2–6,4 kn bei 3–4° Krängung: Streuung 3,5–5,9°). Ruder folgt dem Fehler 1,5 s spät (r 0,9); ab 6 kn
  58 Volllast-Läufe (Pumpe an der Grenze), alle normal (4,7–6 °/s, 5–6 A) – Pumpenfehler unbeteiligt. Rollen mit
  ~20 s erst ab 6,3 kn = Folge des Gierens. Ruderwirkung wächst mit der Fahrt (0,23 → 0,42 °/s je Grad), basic hat
  feste Werte → Abhilfe: Regler „suan“ (Verstärkung nach Fahrt). Ungeklärt: Kursfehler läuft bei jeder Fahrt im
  Wellentakt mit dem Rollen mit (r −0,6; echtes Gieren oder Kompassfehler).

## 2. Pumpe rückwärts (Hafen, Autopilot aus, Ruder frei)
| Versuch | Läufe rückwärts | gestört |
|---|---|---|
| Prüfung A, Rampe 29,9 % (08:55) | 9 (≥ 0,8 s) | 6 |
| Rampe 100 % (09:05) | 13 | 13 |
| Rampe zurück 29,9 % (09:10) | 13 | 13 |
| Messläufe 09:12–09:28 | 9 | 2 (nach Vorwärtsläufen meist gut) |
- Vorwärts **immer** gut: 5–7 °/s, 5–6 A. Rückwärts gut: ~5 °/s, ~5,8 A.
- Stromverlauf gestört: Anlaufspitze 4–5 A, nach 0,1 s abrupt 1,1–1,9 A, bleibt so; Ruder 0–1 °/s. Bordspannung dabei
  höher (12,5 statt 11,3 V). Controller: Befehl voll (raw −1,0), keine Meldung, 26,8 °C.
- **Multimeter an den Motorklemmen (Betreiber): normal 11 V in beiden Richtungen, gestört 1,9 V.**
- Rampe ist nicht die Ursache. Ölstand unwahrscheinlich (Vorrat im höheren Steuerstand). Erste Deutung „Motor dreht
  frei, Pumpe fördert nicht“ war falsch: 1,9 V bei ~1,4 A = stehender Motor.

## 3. Vergleich der Controller-Schaltpläne (pypilot.org/schematics)
| | eingebaut (2017) | High-Power (2022) | Mid-Power (2024) |
|---|---|---|---|
| Bootstrap-Kondensator oberer Transistor | 0,22 µF | 10 µF | 10 µF |
| Ladediode | 1N4001 | MUR160 (schnell) | ohne Typangabe |
| Transistoren je Schalter | 1 | 4 | 2 |
| Treiber | NCP5106B | neuer Typ | wie High-Power |
- Firmware `motor.ino`: 26.04.2020 neue Ansteuerung bei 100 % mit eigener Bootstrap-Ladezeit, geändert 25.05. und
  12.08.2020. Welche Firmware auf dem Gerät läuft, ist unbekannt. Foren: kein gleicher Fehlerbericht gefunden.
- Verdacht: oberer Transistor einer Seite schaltet zeitweise nur halb durch. Offen: Messung Klemme A/B gegen Masse.

## 4. Sonstiges
- `max_slew_slow` wird von pypilot beim Hochsetzen von `max_slew_speed` mitverstellt; zurückgesetzt auf 29,9 / 50
  (geprüft), `rampe.py` setzt jetzt beide zurück.
- Prüfung nach Neustart vom 03.10. erledigt: Prüfsummen und alle Werte stimmen.
- Zwei Mal brach die WLAN-Verbindung des PCs nach ~3 min ab; TinyPilot lief weiter, Pumpe stoppte (Befehl läuft nach 1 s aus).
