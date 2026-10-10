# Regler adaptive – Entwurf

Version 00.04, Stand: 10.10.2026. Eigener Kursregler für SuAn, Neuentwicklung (kein Fork). Läuft als Reglerbaustein im heutigen
TinyPilot; wird der Kern von SuAnPilot V1.0 auf derselben Hardware. Hardware bleibt vorerst unverändert
(RPi Zero 2 W nur, falls die Rechenleistung nicht reicht). Grundlagen: `0-gesamtprojekt/wissen/Marktrecherche.md`
(Bauart der Hersteller), Testberichte `1-tinypilot/docs/tests/`.

## 1. Ziel
- SuAn bei **jedem Wetter, auf jedem Kurs, bei jedem Seegang** sicher steuern – mindestens so gut wie der Robertson,
  der mit derselben Pumpe ohne Zusatzdaten steuert; mit Drehrate, Krängung und Fahrt besser als er.
- Zwei Wertesätze: **„ruhig“** (wenig Pendeln, mehr Strom) und **„sparsam“** (etwas mehr Pendeln, weniger Strom).
- Bewertung nach dem Gütemaß in `1-tinypilot/docs/system/Testplan_Autopilot.md` (Trend, Pumpe W, Wechsel, Ausreißer).
- **Auf den Sollkurs (Vorgabe Betreiber 10.10.2026):** nach Kurswechsel, Störung und Einschalten zügig innerhalb ±1° („ruhig“) bzw. ±2,5° („sparsam“);
  einmaliges Überschwingen höchstens 3°, keine zweite Schwingung über 2°; kein Pendeln beim Kurshalten,
  Pumpenlaufzeit nicht deutlich höher als heute.

## 2. Grundsätze
- **Nur SuAns eigene Werte.** Handbücher anderer Hersteller liefern nur die Bauart, keine Zahlen.
  Alle Werte entstehen durch die Vermessung in Abschnitt 5.
- **Ruderlage regeln, nicht Pumpengeschwindigkeit** (Lehre 02.10., `0-gesamtprojekt/CHRONIK.md`).
- **Die Ruderanzeige kommt ~1 s verzögert** (gemessen 29.09.) und muss eingerechnet werden.
- **SuAn ist unsymmetrisch:** Trimm je Bug verschieden (02.10.: −8,7° / +3,8° bei 2–4° Krängung).
- Sicherheit vor Leistung: jede Störung führt in einen sicheren Zustand (Abschnitt 4).

## 3. Aufbau
Grundgleichung (Grad Ruder laut Anzeige; die Mitte ist nie genau bekannt – Anzeige-Fehler, gemessen +2,9°,
und Luvgierigkeit stecken beide im Trimm und werden mitgelernt):

    Soll-Ruder = Trimm + k(Fahrt) × ( Kursfehler_gefiltert + Tg × (Drehrate − Soll-Drehrate) ) + Drehruder

### 3.1 Verstärkung k abhängig von der Fahrt
- Ruderwirkung wächst etwa mit dem Quadrat der Fahrt: k = k_ref × (v_ref / v)², v = SOG (Fahrt durchs Wasser ist
  unzuverlässig), nach unten und oben begrenzt. Ob „Quadrat“ für SuAn stimmt, zeigt die Vermessung bei 3/5/7 kn.
- Löst den Widerspruch von „basic“ (Flaute pendelt, Böe zu schwach), ohne Werte umzuschalten.

### 3.2 Trimm
- **Vorsteuerung aus der Krängung je Bug:** Trimm_K = a_Bug + b_Bug × Krängung (Krängung kurz geglättet, Zeit T_K).
  Wirkt sofort in der Böe, bevor SuAn dreht. a, b werden laufend aus dem Geradeaus-Ruder gelernt (Gütedatei).
  Kein Glied auf die Krängungs**änderung** (H ließ am 02.10. pendeln).
- **Langsamer Rest-Trimm:** Integrator auf den Kursfehler-Trend, Zeitkonstante T_I. Eingefroren bei Kurswechsel,
  am Ruderanschlag und bei Autopilot aus (kein Aufschaukeln, kein Überschießen nach Manövern).
- **Start mit jetziger Ruderlage:** beim Einschalten gilt die aktuelle Ruderlage als Trimm (02.10.: ohne das fiel SuAn
  4 min um ~8° ab). Je Bug wird der letzte Trimm gespeichert und bei gleichem Bug wieder verwendet.

### 3.3 Seegang
- Kursfehler über eine Zeit T_S geglättet (Wellengieren aussitzen, Lehre 01.10.).
- **Gierband:** Die Gierschwankung wird laufend gemessen; innerhalb des Bandes wirkt der Kursfehler abgeschwächt
  (weich, kein harter Sprung). „ruhig“ = schmales Band, „sparsam“ = breites Band.

### 3.4 Kurswechsel
- Der Sollkurs läuft als **Rampe** mit begrenzter Soll-Drehrate zum neuen Kurs (statt Sprung mit Ruderstoß).
- Drehruder = Soll-Drehrate / Ruderwirkung(Fahrt) – das Ruder, das die gewünschte Drehung erzeugt.
- Höchste Drehrate **je Seite** getrennt (Anluven ist bei SuAn schneller als Abfallen, Test 02.10.).
- Während der Rampe ist der Trimm-Integrator eingefroren.

### 3.5 Ruderantrieb mit Pumpenmodell
- Der Regler steuert die Pumpe selbst (Befehl Pumpengeschwindigkeit an den Servo) und führt eine **geschätzte
  Ruderlage**: Laufzeit × gemessene Rudergeschwindigkeit je Richtung.
- Abgleich mit der Anzeige um die Verzögerung versetzt: geschätzte Lage von vor ~1 s wird mit der heutigen Anzeige
  verglichen, der Unterschied langsam korrigiert. So kein Überschwingen durch die späte Anzeige.
- Pumpe läuft, bis die geschätzte Lage im Totband um das Soll liegt; Totband und kürzester Stoß aus der Vermessung.
- Ruderbegrenzung um den Trimm und absolut ±30° (die Kalibrierung enthält schon die Reserve zum Anschlag).

### 3.6 Windmodus
- Hält einen Windwinkel statt eines Kurses. Der Windwinkel wird in einen Sollkurs umgerechnet
  (Sollkurs = Kurs + Windwinkel_ist − Windwinkel_soll, stark geglättet); danach gilt derselbe Regler wie oben.
- Windgeber schwankt in Böen und bei Rollen: Glättungszeit aus SuAns Aufzeichnung; Böen-Winddreher nicht nachsteuern.
- Voraussetzung: Windgeber geprüft (TODO „Unterwegs“: hart am Wind nur 12–17° scheinbar).
- Sicherheit: fällt der Windwert aus oder springt er, hält der Regler den zuletzt gültigen Kurs und meldet es.

### 3.7 Zwei Wertesätze
- „ruhig“ und „sparsam“ unterscheiden sich in k_ref, Tg, Gierband, Totband und T_I. Beide gelten für alle
  Bedingungen; Bedingungen gehen nur über Fahrt, Krängung und Bug ein, nicht über Umschalten.
- Umschalten in der Weboberfläche (Bedienung des Autopiloten, ersetzt das Display-Menü) und redundant im Leitstand am
  Master; der Leitstand zeigt vorrangig die Leistung, dazu ausgewählte Einstellungen (Regler, Satz), gibt Alarm/Summer.

## 4. Sicherheit und Rückfall
Fehlererkennung und Reaktionen (beide Regler): `0-gesamtprojekt/Fehlersystematik und Reaktionen.md`. Zusätzlich gilt:
alle Werte des Reglers haben feste Grenzen.

## 5. Vermessung SuAn (liefert alle Werte)
### 5.1 Ruderantrieb (im Hafen)
- Rudergeschwindigkeit je Richtung (°/s), Verzögerung der Anzeige, kürzester wirksamer Pumpenstoß,
  Ruderweg je Stoß; per Handsteuerung mit festen Pumpenzeiten, aus der Aufzeichnung (5/s).
### 5.2 Ruderwirkung und Trägheit (unterwegs)
- Freies Wasser, wenig Seegang, SOG etwa 3, 5 und 7 kn, beide Bugs.
- SuAn geradeaus im Trimm, dann legt der **Betreiber von Hand** (Taste) das Ruder um etwa 5° und 10° nach beiden
  Seiten für einige Sekunden; das Programm misst nur (kein automatisches Ruderlegen – sicherer).
- Gemessen: Drehrate nach dem Einschwingen je Grad Ruder (Ruderwirkung K) und Anlaufzeit (Trägheit T).
- Ergebnis: K und T je Fahrt und Seite; daraus der Exponent der Fahrtanpassung (3.1).
### 5.3 Trimm, Seegang
- Trimm je Bug und Krängung: läuft schon jede Minute (`geradeaus_ruder` in der Gütedatei).
- Gierschwankung je Seegangsklasse: aus der Aufzeichnung.
### 5.4 Startwerte berechnen
- k_ref, Tg aus K und T so, dass SuAn ohne Überschwingen einschwenkt (am PC mit dem Modell aus 5.2 durchgerechnet).
- Höchste Drehrate je Seite, T_I, T_K, T_S, Gierband, Totband aus 5.1–5.3.
### 5.5 Feinabstimmung (unterwegs)
- Reihenfolge k_ref → Tg → T_I → Gierband, je 5 min, Kurswechsel ±10° und ±30° nach beiden Seiten.
- Wertung je Satz: „ruhig“ gewichtet Trend und Ausreißer, „sparsam“ gewichtet Pumpe W.
- Wiederholen bei anderen Bedingungen; ein Satz muss alle abdecken, sonst Modell (3.1/3.2) verbessern.

## 6. Umsetzung im TinyPilot
- **Erste Stufe:** nur der neue Reglerbaustein im heutigen Paket, sonst nichts ändern (Rückweg: Regler „basic“ wählen).
  Bestandsaufnahme „übernehmen oder neu“ und Wahl des Betriebssystems erst danach. Reihenfolge: Vermessung → Modell und
  Simulation am PC → `adaptive.py` am PC testen → einbauen, Hafen, unterwegs.
- Neuer Reglerbaustein `pilots/adaptive.py` im Paket `pypilot.tcz` (Verfahren wie bei den bisherigen Paketänderungen,
  `CLAUDE.md`). Messung, Servo, Bedienung und „basic“ von pypilot bleiben unverändert.
- Werte als eigene pypilot-Werte (`ap.pilot.adaptive.*`, gespeichert); Satz „ruhig“/„sparsam“ als ein Wert.
- Zusätzliche Aufzeichnung: Soll-Ruder, geschätzte Ruderlage, Trimm-Anteile, k, Gierband.
- Rechenlast prüfen (TinyPilot heute 42 % frei mit Aufzeichnung, gemessen); Zero 2 W nur bei Bedarf.
- Code im Projekt `1-tinypilot/regler/`: `adaptive.py` (Regler, erste Fassung ohne Krängung/Gierband/Fahrtwerte), `sim.py`
  (Simulation, Startwerte), `sprung.py` (Auswertung Rudersprünge), `setzen.py` (Werte setzen und prüfen).
- **Bedienung V1.0:** Tasten und Display an der Steuersäule bleiben genau wie heute (über den Arduino-Coprozessor):
  Autopilot ein/aus und Kurs ändern. Einzige Änderung: Taste 3 (Menü) entfällt – alle Einstellungen in der
  Weboberfläche. Der Coprozessor entfällt erst mit V2.0.

## 7. Prüfung
1. **Am PC:** Modell aus 5.2 mit 1 s Anzeigeverzögerung und aufgezeichneten Störungen (Wellengieren, Böen-Krängung);
   Vergleich „basic“ / adaptive; Sicherheitsfälle durchspielen (Anzeige fällt aus, Ausnahme im Programm).
2. **Im Hafen:** Ruderantrieb und Pumpenmodell, Rückfall auf „basic“.
3. **Unterwegs:** nur in freiem Wasser, Betreiber am Ruder bereit; je Schritt Gütemaß und Bedingungsraster.

## 8. Offene Fragen (Entscheidung Betreiber)
- Was wird von pypilot/TinyPilot übernommen, was neu gebaut? Davon hängt das Betriebssystem ab
  (Tiny Core oder Standard-System mit Schreibschutz).
