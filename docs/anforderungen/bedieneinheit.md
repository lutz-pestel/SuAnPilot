# Projekt SuAnPilot – neuer Autopilot

**Ideensammlung.** Noch nicht gestartet. Jede Anforderung wird vor Projektstart einzeln geprüft.
Stand: 01.10.2026.

## 1. Ziel und Abgrenzung
- Bedien- und Recheneinheit am Steuerstand: Kursregler, Sensoren, Anzeige, Tasten, Weboberfläche.
- Motor-Controller (mit RF300-Interface) und Stromversorgung sitzen im Motorraum und sind ein eigenes
  Projekt: `docs/anforderungen/motorcontroller.md`. Verbindung RS422 im vorhandenen Kabel.
- Baut auf einem Pi mit Standard-Betriebssystem. Eine einzige, größere Anzeige statt zwei.
- Unterschiede zur Peripherie des TinyPilot (nur diese; der Kern `autopilot/kern/` bleibt gleich, ersetzt wird
  `autopilot/plattform/tinypilot/…/hat/`):
  P1 Nur ein LCD auf der Platine; der Arduino-Coprozessor entfällt ganz.
  P2 Die Tastenabfrage wird neu gebaut und erkennt „gedrückt, solange gehalten“ (B3).
  P3 Kein Menü mehr; alle Einstellungen in der Weboberfläche (B4).

## 2. Erfahrungen mit dem TinyPilot (Ausgangslage)
- Zwei Anzeigen; die zweite samt Tasten hängt an einem Coprozessor, dessen Code verschollen ist und
  der Tasten erst beim Loslassen meldet. Folientasten und Anzeige der alten Robertson-Einheit verschlissen.
- Hängt am Master: GPS, Uhr und WLAN; ohne Master kein Fernzugang, Uhr bleibt auf 2020.
- AIS-Gerät lieferte GPS-Datum 2007; ungeprüft übernommen, Uhren sprangen, Aufzeichnung lückenhaft.
- Ein Neustart des Datenservers auf dem Master ließ den Autopiloten ausfallen (Ursache unbekannt).
- Regler: P am Höchstwert (0,02), D die eigentliche Hauptkraft; keine Kompensation der Luvgierigkeit,
  die mit der Krängung wächst.
- Pumpe lief in einer Richtung nicht an, ohne Meldung; Überstrom sperrt eine Richtung.
- Beim Tausch des Motor-Controllers wurden Einstellungen im TinyPilot überschrieben.
- Keine eingebaute Aufzeichnung; Auswertung erst mit eigenem Programm auf dem Master.
- Rechenleistung knapp: etwa 50 % frei, 42 % mit Aufzeichnung.
Einzelheiten: `docs/tests/2026-09-30_Fahrtest_Autopilot.md`, `CHRONIK.md`.

## 3. Anforderungen (Ideen)
### 3.1 Bedienung
- B1 Mindestens 4 Tasten, robust und seewasserfest, plus Weboberfläche.
- B2 Eine größere Anzeige, bei Sonnenlicht lesbar, am Steuerstand im Freien (Einzelheiten später).
- B3 Handsteuerung per Taste (vorher A1): Solange eine Steuertaste gedrückt ist, bewegt sich das
  Ruder in die gewählte Richtung und wird dabei schneller; beim Loslassen stoppt es sofort. Gilt bei
  ausgeschaltetem Autopiloten; eingeschaltet verstellen die Tasten den Sollkurs (1° bzw. 10°).
  Dazu muss die Tastenauswertung erkennen, **solange** eine Taste gedrückt ist.
- B4 Taste 3 (heute Menü) wird frei: neue Verwendung festlegen (Idee: „ruhig/sparsam“ oder Alarm quittieren).
  Schrittweiten der Kurstasten (heute im Menü, 2°/10°) dann in der Weboberfläche einstellen.
### 3.2 Autonomie
- U1 Arbeitet ohne WLAN und ohne Master vollständig; fehlt das WLAN, baut er einen eigenen
  Zugangspunkt für die Weboberfläche auf.
- U2 GPS und Wind vom Master nutzen, wenn vorhanden (wie heute).
- U3 Eigener Lage- und Kompasssensor; der für pypilot empfohlene ist zu recherchieren.
### 3.3 Regler
- R1 Betriebsarten wie heute (Kompass, GPS, Wind).
- R2 Ruder-Trimmlage aus der gemessenen (geglätteten) Krängung; in der Böe vorausschauend Ruder geben,
  bevor das Schiff anluvt. Bei Geschwindigkeitsbefehlen: Glied auf die Änderung der Krängung.
- R3 Wertebereiche groß genug; kein Regelglied am Anschlag (heute P).
- R4 Mehrere Profile nach dem Bedingungsraster und Gütemaß in `docs/system/Testplan_Autopilot.md` (Hauptprojekt), umschaltbar
  per Taste und Weboberfläche; später selbsttätige Wahl nach Seegang, Wind und Kurs zum Wind.
  Je Profil wird mitgeschrieben, wie gut es war (Kursabweichung, Pumpenzeit, Strom). Anlass: Werte vom
  30.09. (gegen defekte Pumpe erhöht) ließen das Schiff am 01.10. mit 14–17 s Periode pendeln.
- R5 Steuern nach dem langsamen Trend, wie ein Rudergänger: kurze Wellenbewegungen aussitzen. Am 01.10.
  steuerte pypilot jedem 2,6-s-Wellengieren nach (29 Pumpenwechsel/min); Filter halbierten das.
- R6 Ruderlagen-Regelung um eine selbst lernende Trimmlage (wie Robertson J300): Pumpe läuft nur, bis
  die Soll-Ruderlage erreicht ist. pypilot gibt Geschwindigkeitsbefehle und kennt keine Trimmlage.
- R8 Drehrate und Drehbeschleunigung nicht gleichmäßig gewichten: kleine (Welle) aussitzen, große und
  anhaltende (Böe) überproportional beantworten – wie ein Rudergänger. pypilot 0.24 gewichtet linear.
- R9 Krängungsursache erkennen – Böe (einseitig, langsam, mit Wind → vorausschauend Gegenruder), Welle
  (Rollen im Wellentakt, vor dem Wind bis ±30° → aussitzen), Kurve (eigene Drehung → keine Reaktion).
- R10 Ruder-Offset getrennt kennen: Anzeige-Fehler (Anzeige „Mitte“ ≠ Ruder mittig) und Krängungsanteil
  (Luvgierigkeit wächst mit der Krängung) – beide je Bug getrennt bestimmen, da nicht symmetrisch.
### 3.4 Aufzeichnung und Überwachung
- L1 Eingebaut wie heute auf dem Master: Messwerte, Einstellungen, Markierungen; Auswertung je Pumpenlauf.
- L2 Plausibilitätsprüfung von Uhr, GPS-Datum, Kompass und Ruderlage; Meldung bei Abweichung.
- L3 Leitstand auf Master und Kartenplotter: Live-Werte, Verlauf in Ampelfarben, Problemprotokoll mit Zeitstempel,
  Summer (Vorbild: `leitstand.py` vom 01.10.2026).
### 3.5 Zuverlässigkeit
- Z1 Die Steuerung hängt von keinem anderen Dienst ab; Ausfälle von Master, WLAN oder Datenserver
  dürfen sie nicht beeinflussen.
- Z2 Angeschlossene Geräte dürfen Einstellungen nicht ungefragt überschreiben.
- Z3 Fehlertoleranz des Pumpenteils siehe Motor-Controller-Projekt (S1–S8).
- Z4 **Ausweichkette:** steuern, solange irgendeine brauchbare Kursquelle da ist – eigener Sensor →
  fremder Magnetkompass über NMEA → …; jeder Wechsel wird gemeldet. Funktioniert ohne WLAN.
- Z5 Master (falls erreichbar) wertet alle NMEA-Daten aus (Wind, Kurs zum Wind, Fahrt) und schlägt vor.
- Z6 **Problemanzeige:** jeder ungewollte Zustand von System oder Komponente wird erkannt; Display zeigt
  invertiert „Problem“, Weboberfläche und Programm auf Master/Kartenplotter nennen Einzelheiten, Summer.
### 3.6 Software
- W1 Gesamter Code im Projekt, mit Versionsstand und Programmierzugang zu jedem Prozessor
  (vorher A3; Anlass: verschollener Coprozessor-Code, unbekannter Controller-Stand).
- W2 Lizenz: Übernommener pypilot-Code bleibt GPL v3 mit Vermerken des Entwicklers; neu geschriebener Code
  ohne pypilot-Anteile kann eigene Rechte tragen.

### 3.7 Was pypilot 0.24 nicht kann – Nachbesserungsbedarf (Befunde 30.09./01.10.2026)
- Nur Geschwindigkeitsbefehle an die Pumpe; keine Regelung auf Ruderlage oder Trimmlage (R6).
- Keine Trimmung aus der Krängung (R2); kein Seegangsfilter nach Trend (R5); Filterwerte nicht gespeichert.
- P auf 0,02 begrenzt (R3). Überstrom sperrt eine Richtung. Keine Erkennung einer stehenden Pumpe.
- Ein angeschlossener Controller überschreibt Einstellungen (Z2). Keine eingebaute Aufzeichnung (L1).
- Gütemaß: nicht der Augenblickskurs (enthält Wellengieren), sondern der **Trend** (z. B. 20-s-Mittel).
  Am 01.10. lag der Trend im Mittel 1,2° neben dem Soll; 79 % der Pumpenläufe begannen bei Trend < 2°,
  ihre Richtung passte nur in 49 % zum Trend.

## 4. Offene Punkte
- Welcher Lage- und Kompasssensor? Anzeige (Typ, Größe) – später.
- Protokoll zum neuen Motor-Controller.

## 5. Pflege
- Für Bau und Betrieb gilt die Goldene Regel aus `CLAUDE.md`: Ein Kommando ist erst beendet, wenn seine
  Ausführung überprüft wurde.
- Jede Schwäche und jedes Problem des TinyPilot wird als Anforderung hier oder im
  Motor-Controller-Projekt aufgenommen (vorher angesagt, Regel 1).
