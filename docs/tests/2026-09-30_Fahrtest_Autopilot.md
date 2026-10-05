# Fahrtest Autopilot 30.09.2026

Test abgeschlossen. Planung: `docs/system/Testplan_Autopilot.md`. Folgetag: `2026-10-01_Fahrtest_Autopilot.md`.

## 1. Rahmen
- Schlag durch Dänemark nach Norden (um 55°02' N, 9°38' O), Ziel ist Vorwärtskommen, Test nebenbei.
- Regler „basic“, Modus „compass“. Ausgangswerte: P 0,0099 · I 0 · D 0,3013 · DD 0,1013 · PR 0,0199 ·
  FF 1,6141 · servo.period 0,3 · gain 2,0 · speed 100/100 · max_current 20,31 A · Störungszähler 57.
- Aufzeichnung auf dem Master ab 07:36:45, 5 Werte/s (nur wenn die Master-Uhr stimmt, siehe 4.1).
- Wertänderungen über pypilot-Server `10.10.10.163:23322`, jede mit Markierung.

## 2. Ablauf
| Zeit | Betrieb / Kurs zum Wind (scheinbar) | Wind kn (Böen) | Seegang Roll/Stampf ± | Ereignis |
|---|---|---|---|---|
| 07:36 | Maschine, 70–135° | 10–13 | 0,9 / 0,2 | Aufzeichnung an, Kursänderungen in 10°-Schritten |
| 07:46 | Genua gesetzt, ~52° | 12 (16) | 1,3 / 0,3 | |
| 07:50 | angeluvt, 47°, nur Genua | 14 (17–18) | 1,0–1,3 / 0,3–0,6 | beste Strecke des Tages (siehe 3) |
| 08:15 | 44–50° | 16,5 (21) | 1,3–2,2 / 1,0 | Wind und Welle nehmen zu |
| 08:39 | – | – | – | Autopilot fällt aus (4.3) |
| 08:42 | 56–58° | 15 (21) | 2,1 / 1,0 | wieder an, Kurs in 2°-Schritten nachgestellt |
| 08:53 | 42–45° | 17–20 (22–26) | 3–4 / 1,3 | Reglerversuche (3), Sonnenschüsse |
| 09:37 | – | – | – | Ausweichmanöver (nicht ausgewertet) |
| 09:41 | 83° scheinbar ≈ 108° wahr, raumschots | 14 | 2,4 / 1,1 | Kurs 0° |
| 09:51 | raumschots | – | – | +10° Kursänderung, Schiff dreht durch (4.5) |

## 3. Reglerversuche (am Wind, Sollkurs 26°, Windeinfall 42–49°)
| ab | Änderung | Grund | Wind (Böen) / Krängung | Kursfehler Ø | nach Luv Ø | >10° |
|---|---|---|---|---|---|---|
| 08:45 | Ausgang (D 0,3013) | Bezug | 15 (21) / 7° | 3,0° | 2,4° | 0,2 % |
| 08:53 | D → 0,27 | weniger Pumpenarbeit bei Wellengieren | 17,5 (24) / 10° | 7,1° | 6,8° | 19 % |
| 09:01 | (D noch 0,27) | – | 19,3 (25) / 13° | 7,9° | 7,6° | 22 % |
| 09:08 | D → 0,3013 zurück | Sonnenschüsse | 20 (25) / 13° | 6,1° | 5,8° | 14 % |
| 09:10 | P → 0,02 (Höchstwert) | Ruder wird zu früh weggenommen | 20 (26) / 14° | 6,1° | 5,2° | 16 % |
| 09:18 | I → 0,05 | Dauerversetzung nach Luv | 20 (26) / 12,5° | **4,4°** | **1,9°** | **9 %** |
| 09:27 | D → 0,27 | Pumpe läuft 72 % der Zeit | noch nicht ausgewertet | | | |
| 09:36 | PR → 0,05 (Höchstwert) | kleine Befehle bewegen die Pumpe nicht | noch nicht ausgewertet | | | |

- Die Zeile 08:53/09:01 wurde erst D zugeschrieben; der Vergleich mit 09:01–09:08 (D 0,3013 zurück,
  noch mehr Wind) zeigt: **Die Verschlechterung kam vom Wind, nicht von D.**
- Stand jetzt: P 0,02 · I 0,05 · D 0,27 · PR 0,05, übrige Werte wie Ausgang.

## 4. Störungen
**4.1 Master-Uhr springt 2007 ↔ 2026.** Das AIS-Gerät sendet `$GPRMC` mit Datum 14.02.2007 (vermutlich
Überlauf des GPS-Wochenzählers; nachgewiesen durch Ab-/Einschalten). Die Signal-K-Erweiterung
„set-system-time“ übernahm es alle 10 s, das eigene `gps_time_sync.py` stellte auf 2026 zurück.
Um 08:39 abgeschaltet (Sicherung `set-system-time.json.bak-2026-09-30`); seitdem stabil.
**4.2 Aufzeichnungslücken** bis 8 min: Das Aufzeichnungsprogramm richtet den Takt nach der Uhrzeit und
schreibt nach einem Rücksprung nichts. Seit 4.1 behoben keine Lücken mehr.
**4.3 Ausfall des Autopiloten 08:39:39**, 2 s nach dem Neustart des Signal-K-Servers: Verbindung zum
TinyPilot brach ab, danach Autopilot aus, Sollkurs 186° (alter Wert), Ruder blieb bei 10°, das Schiff
drehte in 30 s um ~75°. Ursache der Kopplung unbekannt.
**4.4 Hartruder beim Wiedereinschalten 08:40:17**: Ruder lief in 4 s auf −27°. Ungeklärt.
**4.5 Durchdrehen nach +10° (09:51:48–09:52:12)**: Ruder auf −11°, Schiff dreht mit 4°/s. Danach 17 s
volle Pumpe in Gegenrichtung befohlen; gemessene Ruderlage nur −11° → +2° (0,7°/s, Strom 1,4 A),
blieb also auf der Drehseite (Ruder für Geradeauslauf auf diesem Kurs ~+5…+10°). Betreiber sah
**überhaupt kein Gegenruder**, Pumpe lief nicht. Schiff bis 44° über den Kurs, dann Hand. Ursache: 5.
**4.6 Sonnenschüsse** am Wind bei Böen: bis 39° neben dem Kurs, Rückkehr 25–50 s.

## 5. Erkenntnisse
- **Pumpe läuft „vorwärts“ zeitweise nicht an** (Ruder positiv = Gegenruder beim Anluven, Kurs nach
  Backbord, Stoppen einer Steuerborddrehung). Betreiber bestätigt: Pumpe lief nicht. Pumpenläufe ≥2 s:
  | Lauf | davor | tot | gut |
  |---|---|---|---|
  | vorwärts | rückwärts | 2 | 132 |
  | vorwärts | vorwärts | 68 | 28 |
  | rückwärts | beliebig | 0 | 109 |
  Tot = Ruder <1,3°/s, Strom ~1,5 A statt 4,5–6 A. pypilot sendet in beiden Fällen denselben Befehl
  (1,0), kein Störungskennzeichen; Spannung, Pumpenlast, Ruderlage erklären es nicht.
  **Verdacht (unbewiesen):** Speicherkondensator bzw. Diode für den oberen Transistor der
  Vorwärtsseite im Motor-Controller. Er wird nur bei einem Lauf in Gegenrichtung nachgeladen (im
  Stillstand bleiben die unteren Transistoren aus, `motor.ino` `position()`); gealtert hält er nicht.
  Dann schaltet der Transistor nur halb durch (1,5 A) und wird warm.
- Umgehungsversuche im TinyPilot (`servo.py`, je Neustart): Rückwärtsimpuls 0,3 s – mit Autopilot 57 von 83
  Läufen weiter tot; kurzes Auskuppeln – ohne Wirkung; Selbsthilfe (Erkennung, 4 Maßnahmen reihum,
  Logbuch) – erkannte zuverlässig, keine Maßnahme half. Ab 11:35 alle 41 Vorwärtsläufe tot, ab 11:46
  auch per Taste (8 von 8), selbst direkt nach Rückwärtslauf. Strom springt kurz auf 2–4,5 A, fällt auf 1,3 A.
  **Schluss: Bauteil im Motor-Controller fiel im Lauf des Tages aus** (Pumpe/Hydraulik liefen jahrelang mit
  Robertson einwandfrei). Controller am 01.10. getauscht; Ersatz arbeitet in beide Richtungen.
- Folge für die Versuche: Tote Läufe ab 08:25, gehäuft ab 09:25, fast alle ab 09:44 (mehr Vorwärts-
  folgen gegen Luvgierigkeit und raumschots). Der Sonnenschuss 08:54 fällt auf einen 14 s toten Lauf.
  **Alle Reglervergleiche in 3 sind dadurch verfälscht.**
- Rückkehrzeiten 10°-Schritte: Steuerbord Ruder bewegt nach 1–2 s, Backbord nach 2,6–6,8 s,
  halbe Kursänderung Backbord bis 39 s.
- **D ist die Hauptkraft des Reglers:** Anteil D am Ruderbefehl im Mittel ~9× so groß wie P.
  Dreht das Schiff zurück, nimmt D das Ruder weg, obwohl es noch 10–20° neben dem Kurs liegt.
- **P hat mit 0,02 den Höchstwert dieser pypilot-Version** (Bereiche: I ≤ 0,1, PR ≤ 0,05, D ≤ 1).
- **I = 0,05 wirkt:** Das Integral steht bei Dauerversetzung am Anschlag (+1), I gibt dann einen
  festen Zusatzbefehl von 0,05. Dauerversetzung nach Luv 5,2° → 1,9°.
- **Kleine Befehle bewegen die Pumpe kaum:** Befehl <0,2 → Pumpe läuft 10–15 % der Zeit,
  0,3–0,4 → 58 %, ≥0,8 → 100 %.
- **Luvversetzung wächst mit der Krängung** (mit I): 5–10° Krängung −0,8°, >15° Krängung +5,6°.
  pypilot 0.24 hat keinen Reglerwert, der auf die Krängung reagiert.
- Kompass minus GPS-Kurs konstant ~7–8° (Missweisung, Abdrift, Strom; Kalibrierung ungeprüft).
- Keine neuen Servo-Störungen (Zähler 57), Ströme ≤ 8 A.

## 6. Offene Punkte und Ideen für an Land
1. **Defekten Motor-Controller untersuchen** (Ersatz seit 01.10. eingebaut): Ansteuerung des oberen
   Transistors der Vorwärtsseite messen, Speicherkondensatoren/Dioden prüfen. Reglerversuche wurden
   am 01.10. mit dem Ersatz wiederholt.
2. Ausfall bei Signal-K-Neustart (4.3) und Hartruder (4.4) nachstellen. Bis dahin: Signal K nie bei
   eingeschaltetem Autopiloten neu starten.
3. Krängungsabhängiger Ruderanteil (Programmänderung im Paket `pypilot.tcz`).
4. Totzone kleiner Befehle: `servo.period`/`servo.gain` untersuchen.
5. AIS: Positionsmeldungen an den Master abstellen oder Datum korrigieren.
6. Aufzeichnungsprogramm: Takt nach nicht springendem Zähler.
7. Kompass: Abweichung je Kurs prüfen (mehrere Kurse, Vergleich mit GPS-Kurs).
8. Signal-K-Passwort zurücksetzen.

## 7. Daten
Master `/home/pi/aplog/data/`: `signals_2026-09-30_073645.csv` (Messwerte), `events_…csv`
(Einstellungen), `marks.csv` (Markierungen). Zeit in `signals` = Unix-Zeit (UTC). Kopie im
Projekt: `Daten/aplog/`.
