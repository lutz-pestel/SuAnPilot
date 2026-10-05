# Fahrtest Autopilot 02.10.2026 – Leichtwind, Pendeln, Kurswechsel, Ruder-Trimm, Böen

Daten: Master `/home/pi/aplog/data/signals_2026-10-02_081628.csv`, `marks.csv`, ab 11:38 `guete_2026-10-02.csv`.
Gütemaß und Bedingungsraster: `docs/system/Testplan_Autopilot.md`, Abschnitt „Auswertung“ (heute festgelegt).
Ausgangswerte (Stand 01.10.): P 0,02 · PR 0,0199 · D 0,27 · DD 0,05 · I 0,05 · H 0,5 · FF 1,61 · servo.gain 0,7.

## 1. Pendeln bei Leichtwind (09:34–09:50)
- Halber Wind, 8–10 kn, SOG 4,2–5 kn, Krängung 4–6°, Seegang 0. Schwingung ~40 s, Kurs ±20–25°, Ruder −9…+33°;
  Betreiber steuerte von Hand.
- Erste Deutung „Pumpe zu langsam“ (servo.gain 0,7 → 1,3) war **falsch**: Schwingung schneller (~25 s) und aufschaukelnd.
- Ursache: P war am 30.09. gegen den defekten Controller auf 0,02 verdoppelt worden. Bei Geschwindigkeitsbefehlen
  wirkt P aufsummierend; bei wenig Fahrt (träges Schiff) ergibt das Dauerpendeln.
| Einstellung | Kurs Ø | Trend Ø | > 10° | Pumpe | Wechsel/min |
|---|---|---|---|---|---|
| gain 0,7 · P 0,02 | 10,5° | 7,0° | 46 % | 15 W | 3,8 |
| gain 1,3 · P 0,02 | 10,3° | 4,3° | 36 % | 33 W | 6,3 |
| gain 1,0 · P 0,0099 | 2,9° | 2,2° | 2 % | 6 W | 3,1 |

## 2. Optimierung raumschots (10:28–10:58, Wertung = Trend/2 + W/10 + Wechsel/8 + Ausreißer%/2)
Raumschots 117–140°, Wind von 10 auf 6,5 kn abnehmend, Krängung 2–3°, Seegang 1, SOG 5,1 → 3,4 kn.
| Schritt | Trend Ø | Pumpe W | Wechsel/min | Wertung | Ergebnis |
|---|---|---|---|---|---|
| Ausgang (P 0,0099, PR 0,0199, D 0,27, gain 1,0) | 1,36° | 7,9 | 4,4 | 2,03 | |
| P 0,005 | 0,56° | 5,3 | 4,4 | 1,37 | behalten |
| P 0,0025 | 0,73° | 3,9 | 4,3 | 1,29 | behalten |
| PR 0,01 | 0,82° | 2,8 | 3,3 | 1,11 | behalten |
| servo.gain 0,8 | 1,50° | 1,1 | 2,9 | 1,22 | verworfen (Wind 6,5 kn, 3 Sollwechsel) |
| **D 0,22** (gain 1,0) | **0,52°** | **1,7** | **2,3** | **0,72** | **behalten** |
Ab 11:22 bei 10,8 kn, Krängung 6°: Trend 1,6°, Wertung 1,64 – Werte vom Leichtwind dort schon zu sanft.

## 3. Kurswechsel-Tests (10° per Taste, Zeit bis 2° vor Ziel / Überschwingen)
| FF | Wind / Krängung / Ruder Ø | Anluven (BB) | Abfallen (StB) |
|---|---|---|---|
| 1,61 | 7 kn / 3° / – | 30 s / 1,6° | 57 s / 1,6° |
| 2,5 | 10 kn / 4° / −6° | 17 s / 0° | 35 s / 1,4° |
| 3,0 | 11 kn / 6° / −8° | 9 s / **10°**, Eingriff | **94 s** / 0° |
- FF wirkt bei Tastensprüngen nur als kurzer Stoß (geglättet); beim Kurshalten null.
- **Unsymmetrie**: Anluven hilft die Luvgierigkeit, Abfallen bremst sie; nach dem Abfallen blieb 3–4° Rest
  (P, PR, I zu schwach; H nimmt bei abnehmender Krängung Gegenruder weg). Ein gleiches FF kann das nicht lösen.
  → Fork: Trimm-Regelkreis aus der Krängung, Kurswechsel mit Drehrate, Kursfehler ungleich gewichten.

## 4. Ruder-Offset (Geradeaus-Ruder = mittlere Ruderanzeige je Minute mit Autopilot, ohne Manöver)
- Anzeige-Fehler: Motor ohne Segel 08:45–08:57, Krängung −0,2°, 3600 Werte: Anzeige **+2,9°** bei Ruder mittig.
- Geradeaus-Ruder laut Anzeige, 7–11 kn Wind (in Klammern Minuten):

| Krängung | Wind von BB | Wind von StB |
|---|---|---|
| 2–4° | −5,8° (45) | +6,7° (15) |
| 4–6° | −7,7° (36) | +7,6° (32) |
| 6–8° | −9,5° (15) | – |

- Abzüglich Anzeige-Fehler bei 2–4°: BB −8,7°, StB +3,8° – unsymmetrisch; schon bei wenig Krängung 4–6° Ruder-Trimm.
- Verfahren: Mittel der Ausschläge je Minute (der Autopilot hält den Kurs, Restdrehung vernachlässigbar); gleiche Werte
  wie in ruhigen 20-s-Abschnitten (±0,2°). Läuft seit 12:23 fortlaufend in der Gütedatei.

## 5. Nachmittag: Böen bis 17 kn, halber Wind, Wind von BB (Markierungen in `marks.csv`)
| Zeit | Werte | Bedingungen | Ergebnis |
|---|---|---|---|
| 13:16 | P 0,0025 · I 0,05 · H 0,5 | 18,5 kn, Krängung 15–20° | 32° angeluvt, Ruder am Anschlag (−30°) |
| 13:39 | P 0,01 | Wind schon 9–10 kn | Pendeln ±20°, Autopilot aus |
| 13:46 | P 0,01 · H 1,0 | 12–15 kn | 24° angeluvt: H nimmt nach der Böe Gegenruder ebenso schnell weg |
| 13:56 | P 0,005 · H 0,5 | 15 kn, Krängung 21° | kein Pendeln, aber −20°; I-Speicher am Anschlag (±1 → höchstens I) |
| 14:01–14:19 | P 0,005 · I 0,08 | 11–17 kn, Krängung bis 21° | meist ±5°, Böe 14:17 ±5°, 14:19 kurz −15° bei Ruder −27° |
- Nach Einschalten setzt pypilot den I-Speicher auf null: 11:56 fiel das Schiff 4 min ~8° ab (Trimm fehlte).
- 14:40–14:47 (Ankermanöver, wenig Fahrt): Drehrate und Kurs passten nicht zusammen – nicht bewertet, bei freier Fahrt prüfen.

## 6. Erkenntnisse
- Werte hängen stark von den Bedingungen ab: wirksames P (P × gain) am 01.10. (20 kn, Krängung 15°, Seegang 3)
  0,014, heute (7–10 kn, Krängung 2–5°, Seegang 0–1) 0,0025; wirksames D ähnlich (0,19 / 0,22). → Profile nötig.
- Gütedatei je Minute seit 11:38 aktiv (`guete.py` in `pumpwatch.py`), Speichergrenze Datenordner 2 GB.
- Endstand 14:47: P 0,005 · PR 0,01 · D 0,22 · DD 0,05 · I 0,08 · H 0,5 · FF 2,5 · servo.gain 1,0 · Filter 0,1.
  Bei Flaute unter 10 kn mit diesen Werten nicht geprüft.
