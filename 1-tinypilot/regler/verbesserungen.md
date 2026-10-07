# Verbesserungen für den pypilot-Fork (Basis 0.24 an Bord)

Stand: 01.10.2026. Ablauf: Idee → im Fork einbauen und auf See testen → **wirkt**: als Anforderung nach
`docs/anforderungen/` übernehmen und hier löschen; **verworfen**: löschen (Lehre ggf. in `0-gesamtprojekt/CHRONIK.md`).
Jeder Einbau wird einzeln vorgelegt. GPL v3: Vermerke des Entwicklers bleiben, eigene werden ergänzt.
Code: `pypilot/` = Paket an Bord vom 01.10. (Kopie `pypilot.tcz-2026-10-01`); pypilot 0.71 bei Bedarf neu
von GitHub holen (verglichen: Stand 09.09.2026). Herkunft: M = eigene Messung, H = Hersteller (`0-gesamtprojekt/wissen/Marktrecherche.md`), P = pypilot 0.71, B = Betreiber.
Priorität P1/P2/P3 = Reihenfolge des Einbaus (Sicherheit → Nutzen/Aufwand → Abhängigkeiten); eingebaut im Hafen, getestet unterwegs.

## Im Test
- Selbsthilfe bei stehender Pumpe (`servo.py`, M): erkennt zuverlässig; Abhilfe (Auskuppeln, Gegenrichtung)
  half beim defekten Controller nicht; greift erst ab 1 s, kurze Stöße bleiben unbewertet.
  Seit 02.10. nur noch Erkennen und Melden (`REC_ACTIONS = False`): Abhilfe half nicht und nahm dem Schiff
  kurz die Steuerung.
- Pumpenüberwachung je Lauf (Master `pumpwatch.py`, M): 333 tote Läufe am 30.09. erkannt, kein Fehlalarm
  am 01.10.; kurze Stöße (< 1,2 s) nicht bewertbar.

## P1
1. **Fester Notfall-Wertesatz** (B): fallen die Master-Daten aus (Wind, Fahrt), steuert der Autopilot mit einem festen
   Satz, der bei allen Bedingungen funktioniert und dafür mehr Strom braucht.
2. **Ausweichkette der Kursquellen** (B): steuern, solange irgendeine brauchbare Quelle da ist –
   eingebauter Sensor → NMEA-Magnetkurs vom Master (`$IIHDM`) → …; jeder Wechsel wird gemeldet.
   Zuerst prüfen, ob 0.24 einen NMEA-Kurs als Ersatz annimmt.
3. Überstrom darf keine Richtung dauerhaft sperren; Wiederanlauf nach Pause (M).
4. `servo.hardover_time` 2,14 s gegen gemessene Anschlag-zu-Anschlag-Zeit prüfen (H: typisch 12–15 s).
5. Korrigierte Pumpenlogik 2021 (Sammeln kleiner Befehle, Richtungswechsel) übernehmen (P).
6. **Verstärkung abhängig von der Fahrt** (M, H: B&G „Cruising Speed“): bei wenig Fahrt größere und schnellere
   Ruderbewegung. Anlass 02.10.: 10 kn Halbwind, 4,5 kn Fahrt, servo.gain 0,7 → Pendeln 40 s, ±20–25°, Hand.
7. **Kurswechsel mit vorgegebener Drehrate** (M, H, P: Pilot „rate“): bei Sollkursänderung > ~3° Schiff mit fester
   Drehrate (z. B. 3°/s) herumsteuern, vor dem Ziel abbremsen, dann ruhiges Kurshalten. Kurshalten und Kurswechsel
   mit getrennten Werten. Anlass 02.10.: 6° per Taste brauchte ~60 s (P 0,0025, PR 0,01; FF wirkt bei Sprüngen kaum).
8. **Trimm-Regelkreis aus der Krängung** (B, H: AutoTrim; M): Soll-Trimmlage = Faktor × Krängung (grob 1° Ruder je °,
   aus Aufzeichnungen genauer bestimmen); Ruder über die gemessene Ruderlage langsam (~10 s) dorthin führen; der
   schnelle Kursregler steuert symmetrisch um diese Lage. Anlass 02.10.: nach Abfallen 3–4° Rest für ~1 min.
   Test 02.10. (FF 3,0, Krängung 6°): Anluven 10° überschossen, Abfallen 94 s – gleiches FF hilft nicht.
   Ruderlage geradeaus = Anzeige-Fehler (Anzeige „Mitte“ ≠ Ruder mittig) + Krängungsanteil (Luvgierigkeit);
   beide getrennt und **je Bug getrennt** bestimmen (nicht symmetrisch).
   Nach Neustart/Einschalten (02.10. 11:56) fiel das Schiff ~8° ab und brauchte 4 min (Trimm −10° fehlte) → Trimm je Bug vorgeben.
   **Schnell vorsteuern:** Ruder = Grundwert je Bug + Faktor × Krängung (2–3 s geglättet), Werte aus der laufenden Messung
   (02.10., BB: 3° → −8,3°, 5° → −10,4°, 7° → −11,4°, Böe 13–17° → −15…−23°). H (Krängungsänderung) dann klein oder weg:
   H 1,0 ließ am 02.10. pendeln (nimmt nach der Böe Gegenruder ebenso schnell weg, Schiff luvte 24° an).

## P2
9. **Anzeige „Problem“ invertiert** auf dem TinyPilot-Display bei jedem ungewollten Zustand (`hat/page.py`, B);
   Weboberfläche nennt die aktuellen Probleme. Erkennen ungewollter Zustände: bei jedem Einbau mitdenken.
10. Krängungsursache trennen – Böe, Welle (Rollen), Kurve –, damit H nur auf Böen reagiert (M; SuAnPilot R9).
11. Totzone / Pilot „deadzone“ (P, H): keine Ruderbewegung unter einem Gierband; Auto-Stufe nach Seegang (H).
12. Drehrate, Drehbeschleunigung **und Kursfehler** nicht gleichmäßig gewichten: Welle aussitzen, Böe überproportional (M).
   Kursfehler < ~3° sanft, ab ~8–10° deutlich überproportional (02.10.: 10° ergaben nur Befehl ~0,06; PR wirkt umgekehrt).
13. Profile (P): Werte je Profil; Achsen Bedingung × Ziel (bestes Kurshalten / minimaler Strom).

## P3
14. Master wertet NMEA aus (Wind, Kurs zum Wind, Fahrt) und **wählt** Profil bzw. Reglerwerte (B).
15. Selbsteinstellung von P und D nach Kostenmaß, Pilot „autotune“ (P).
16. Gust Response im Windmodus: Ziel-Windwinkel in der Böe kurz senken (H, B&G).
17. Kalibrierfahrt: Verstärkungen aus Probewenden bestimmen (H, B&G NAC-3).
18. Ruderlagenregelung, Pilot „absolute“ (P, H) – erst, wenn die Ruderlage ohne 1 s Verzögerung kommt.
