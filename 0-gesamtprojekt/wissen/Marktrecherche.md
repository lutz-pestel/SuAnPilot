# Marktrecherche Autopiloten – Vergleich mit pypilot

Stand: 02.10.2026. Grundlage: Handbücher, Fachartikel, Foren (Quellen am Ende) und der pypilot-Code
von GitHub (Stand 09.09.2026, Version 0.71). **Belegt** = Handbuch/Code; **Angabe** = Herstellerwerbung
oder Erfahrungsbericht, nicht nachgeprüft.

## 1. Überblick
| Merkmal | NKE Gyropilot | B&G H5000 / NAC-3 | Raymarine Evolution | Simrad / Robertson | pypilot 0.24 (an Bord) | pypilot 0.71 |
|---|---|---|---|---|---|---|
| Regelung | Ruderlage | Ruderlage (Rudder Gain je Grad Fehler) | k. A. | Ruderlage (Rudder, Counter Rudder) | „basic“: Pumpengeschwindigkeit; „absolute“: Ruderlage | wie 0.24 |
| Gegenruder (Drehrate) | Drehratenkreisel ab Gain 4 | Counter Rudder | ja (9-Achsen-Sensor) | Counter Rudder | D, DD | D, DD |
| Trimmlage lernen | k. A. | AutoTrim, ~60 s | k. A. | Autotrim, Standard 40 s | I (bei uns 0,05) | im Pilot „basic“ entfernt |
| Krängung | Wind-Korrektur nach Krängung | **Heel Compensation**: schnell lernender Luvgierigkeits-Ausgleich innerhalb einer Böe; **Gust Response** nach Krängungszunahme | k. A. | k. A. | – (bei uns: Glied H) | nur im abgeschalteten Pilot „fuzzy“ |
| Seegang | Bewegungssensor glättet Windwinkel (Angabe: −40 % Ruderbewegung) | Response Perf 1–5 | AI passt an | **Seastate filter** Off/Auto/Manual (Gierband); Deadband | – (bei uns: Filter + gain) | Pilot „deadzone“: Totzone, Standard 5° |
| Stufen / Profile | Böen-, Surf-Modus | Perf 1 (wenig Strom) … 5; Eco/Normal/Sport | Leisure / Cruising / Performance | Response HI/LO | – | Profile (`profiled`-Werte) |
| Selbst lernen | k. A. | Adapt (Erfahrung: nach Update abschalten) | „Evolution AI“, keine Einstellungen nötig | – | – | Autotune, Learning (experimentell) |
| Inbetriebnahme | k. A. | NAC-3: Probewenden kalibrieren Gain und Counter Rudder | ohne Kalibrierfahrt (Angabe) | Rudder zero, Seetest | Ruderkalibrierung von Hand | wie 0.24 |
| Kursgenauigkeit | k. A. | Kompass 2° | „innerhalb 2°“ (Angabe) | k. A. | Trend am 01.10.: ~1° | – |

## 2. Was die Hersteller anders machen
- **Regelung auf die Ruderlage** ist Standard: Rudder Gain (Grad Ruder je Grad Kursfehler), Counter Rudder
  (Gegenruder nach Drehrate), AutoTrim (lernt die Luvgierigkeits-Ruderlage in 40–60 s). Die Pumpe läuft nur,
  bis die Soll-Ruderlage erreicht ist. pypilot „basic“ regelt dagegen die Pumpengeschwindigkeit; „absolute“
  (schon in 0.24) regelt die Ruderlage – Robertson und NAC zeigen, dass das mit üblicher Rückmeldung geht.
- **Schneller Krängungsausgleich zusätzlich zum langsamen AutoTrim** (B&G Heel Compensation, Gust Response) –
  entspricht unserem Glied H, das am 01.10. das Anluven in Böen halbierte. Bestätigt den Ansatz (R2).
- **Seegangsfilter / Totzone:** Der Kurs darf um ein Gierband (1–5°) abweichen, bevor das Ruder reagiert;
  Auto-Stufe passt es dem Seegang an. Entspricht „Trend statt Welle“ (R5). pypilot 0.71: Pilot „deadzone“.
- **Reaktionsstufen** mit ausdrücklichem Zielkonflikt Genauigkeit ↔ Strom (B&G Perf 1–5) – entspricht
  unseren Profilen nach Ziel (R4).
- **Kalibrierfahrt** zur Bestimmung der Verstärkungen (B&G NAC-3) statt Einstellen von Hand.
- **Hard-over time** (Zeit von Anschlag zu Anschlag) bei Leistungsyachten typisch 12–15 s (Angabe);
  bei uns steht 2,14 s – prüfen.
- Hydraulik hat 25–35 % Wirkungsgrad (elektromechanisch 70–80 %); jeder unnötige Pumpenlauf kostet
  entsprechend viel Strom (Angabe).

## 3. Was pypilot 0.71 gegenüber 0.24 bietet
- Pilot **deadzone**: keine Ruderbewegung, solange der Kursfehler unter der Totzone (Standard 5°) liegt.
- Pilot **rate**: regelt die Drehrate auf einen Sollwert, der mit dem Kursfehler wächst (begrenzt).
- Pilot **absolute** (auch in 0.24, dort ohne FF): Ruderlagenregelung mit P, I, D.
- Pilot **autotune**: verstellt P und D selbsttätig nach einem Kostenmaß (Fehler + Verstärkung).
- **Profile** für ausgewählte Werte; korrigierte Pumpenlogik (Sammeln kleiner Befehle).
- Basic: I und R entfernt, engere Bereiche (D ≤ 0,24). **Keine** Krängung in den aktiven Piloten.

## 4. Vorschläge (jeweils einzeln zur Zustimmung)
1. Fork: Pilot „deadzone“ und Profile aus 0.71 nach 0.24 übernehmen und mit unserem Glied H verbinden.
2. Pilot „absolute“ (Ruderlage) mit Selbsttrimm und Startruder ausbauen und testen – siehe Abschnitt 6.
3. `servo.hardover_time` (2,14 s) mit gemessener Anschlag-zu-Anschlag-Zeit vergleichen.
4. SuAnPilot: Ruderlagenregelung mit AutoTrim + schnellem Krängungsausgleich + Seegangsfilter mit
   Auto-Stufe + Reaktionsstufen als Kern; Kalibrierfahrt zur Inbetriebnahme.

## 5. Rechenregeln im Einzelnen (Handbücher, belegt)
| Baustein | Robertson AP300CX (an Bord) | Simrad NAC-2/3 | B&G H5000 |
|---|---|---|---|
| Ruder (P) | Ruder = Rudder × Kursfehler; Segler LO 0,5 / HI 0,35 | Rudder gain; zu hoch → Überschwingen | Rudder Gain 0,37–0,60 |
| Gegenruder (D) | Counter Rudder × Drehrate; LO 1,4 / HI 1,0 | Counter rudder; Trägheit, beide Drehrichtungen prüfen | 0,9–1,3 |
| Selbsttrimm (I) | Autotrim 40 (s); Segler evtl. 0 | Autotrim: kleiner = schneller | Zeit in s ≈ Bootslänge in Fuß |
| Fahrt | 2 Sätze HI/LO, Umschalten bei 9 kn ± 1 | 2 Profile HI/LO, Transition speed | **stufenlos**: Werte gelten 100 % bei Cruising Speed, darunter mehr, darüber weniger |
| Ruder-Totzone | – | Auto: lernt aus Ruderdruck | Auto, 0–4° |
| Seegang | Seastate-Filter Auto (Gierband, Zeitkonstante) | – | Deadband als Seegang-Einstellung |
| Ruderbegrenzung | 20° um die Trimmlage | um den Sollwert, nicht hart | 35° |
| Einschalten | – | **Init rudder „Actual“**: jetzige Lage gilt als Trimm | ~1 min bis Trimm stabil |
| Krängung | – | – | Heel Compensation (Ruder sofort nach Krängung), Gust Response (Soll-Wind kurz abfallen) |
| Selbsteinstellung | Autotune: S-Kurven, 1–2 min, 5–10 kn | Autotune | Autotune, Adapt (lernt, speichert alle 30 min) |
| Stufen | – | – | Perf 1–5, Auto Response, Recovery (kurz Perf 5 nach Einzelereignis) |
Kern aller drei: **Ruderlage = Ruder × Kursfehler + Gegenruder × Drehrate + Trimm**; Trimm langsam (40–60 s);
Werte nach Fahrt angepasst. B&G ergänzt schnelle Krängungsglieder und lernt laufend.

## 6. Übertragung auf pypilot 0.24 „absolute“ (Code geprüft 02.10.)
- Vorhanden: P (Ruder, 0,05–2 °/°), D (Gegenruder, bis 2 °/(°/s)), DD; Servo fährt auf Ruderlage, stoppt bei < 1°
  Abweichung (feste Totzone); fällt ohne Ruderanzeige auf „basic“ zurück.
- **Fehlt:** Selbsttrimm – I wirkt höchstens 0,05° Ruder (Speicher ±1), nötig sind bis −15°; Startruder („Actual“);
  Fahrtanpassung; Krängungsglied. Ohne Selbsttrimm stünde das Schiff bei P 0,5 um bis zu 20° neben dem Kurs.
- Nötig daher eine kleine Paketänderung in `pilots/absolute.py` (Verfahren wie bei H in `basic.py`): Trimm-Integrator
  (Zeitkonstante aus SuAns Vermessung), Start mit jetziger Ruderlage, Werte × (Bezugsfahrt / SOG) begrenzt, später Krängungsglied.

## Quellen
- Robertson AP300X/AP300CX Handbuch (`Robertson/Control-Unit/AP300CX_Manual.pdf`), Abschnitte 2.7, 2.10, 3.13
- [Simrad NAC-2/NAC-3 Commissioning Manual](https://media.hudsonmarine.co.uk/uploads/Navico/Autopilot/NAC-2%20and%20NAC-3%20Commissioning%20Manual.pdf)
- [H5000 Autopilot Setup & Sailing Guide (J109, 2024)](https://vs.j109.org/blog/wp-content/uploads/2025/07/H5000-Autopilot-Setup-Sailing-Guide.pdf)
- [Yachting World: New-age sailing autopilot systems](https://www.yachtingworld.com/gear-reviews/new-age-sailing-autopilot-systems-126909)
- [BLUR: 8 things about the B&G H5000 autopilot (2026)](https://www.blur.se/2026/05/04/8-things-i-wish-id-known-about-the-bg-h5000-autopilot/)
- [B&G H5000 Pilot – Advanced User Information](https://www.manualslib.com/manual/1602599/BAndg-H5000-Pilot.html)
- [Sailing World: How to use a B&G autopilot](https://www.sailingworld.com/gear/how-to-use-a-bg-autopilot-system/)
- [NKE Gyropilot 3 User Manual](https://nke-marine-electronics.fr/wp-content/uploads/user_manuals/EN/40_Gyropilot_3_um_EN.pdf)
- [Sail Magazine: Raymarine Evolution](https://sailmagazine.com/gear/raymarines-evolution-autopilot/)
- [Simrad GO7 Manual – Sea State Filter](https://www.manualslib.com/manual/928811/Simrad-Go7.html?page=72)
- [Simrad Robertson AP300X Manual](https://www.manualslib.com/manual/1801540/Kongsberg-Simrad-Robertson-Ap300x-Series.html)
- [Garmin Reactor 40 Hydraulic Configuration Guide](https://static.garmin.com/pumac/Reactor_40_Hydraulic_Models_Configuration_Guide_GHC_50_EN-US.pdf)
- [Cruising World: Modern Sailboat Autopilots](https://www.cruisingworld.com/modern-sailboat-autopilots/)
- pypilot auf GitHub: `pypilot/pilots/` (basic, deadzone, rate, absolute, autotune, fuzzy), Stand 09.09.2026
