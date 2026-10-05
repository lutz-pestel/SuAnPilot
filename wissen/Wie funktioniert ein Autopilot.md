# Wie funktioniert ein Autopilot

Stand: 03.10.2026. Geschrieben nach dem Programmcode und den Fahrtests vom 30.09.–02.10.2026; Weboberfläche und
Werte am 03.10. am Gerät geprüft. Was „nach Code“ heißt, ist am Gerät nicht nachgesehen. Werte: `Systembeschreibung.md`.

# Teil 1 – Der Autopilot

## 1. Das Grundprinzip
Der Autopilot macht dasselbe wie ein Steuermann, nur mehrmals pro Sekunde:
1. Er liest den **Kurs** vom eingebauten Kompass und vergleicht ihn mit dem **Sollkurs**. Der Unterschied heißt
   **Kursfehler**.
2. Er misst außerdem, wie schnell und in welche Richtung das Schiff gerade dreht (**Drehrate**).
3. Ein Rechenprogramm, der **Regler**, macht daraus einen Befehl an die Hydraulikpumpe.
4. Die Pumpe bewegt das Ruder, das Schiff dreht, und alles beginnt von vorn.

Der Regler kennt das Schiff nicht. Er kennt nur seine **Einstellwerte**. Sie sagen ihm, wie kräftig er auf welche
Beobachtung reagieren soll. Gute Werte machen das Schiff ruhig, schlechte lassen es pendeln oder vom Kurs laufen.

## 2. Modus und Regler – zwei verschiedene Dinge
**Der Modus** sagt, *worauf* gesteuert wird (Auswahl auf der Seite „Control“):
| Modus | Hält | Voraussetzung |
|---|---|---|
| compass (heute benutzt) | einen Kompasskurs | keine |
| gps | einen Kurs über Grund | GPS vom Master |
| wind | einen Winkel zum scheinbaren Wind | Windgeber (Anzeige hart am Wind unplausibel, ungeprüft) |
| true wind | einen Winkel zum wahren Wind | Windgeber und GPS |

**Der Regler** sagt, *wie* gesteuert wird (Auswahl „Pilot“ auf der Seite „Gain“). Wichtig sind zwei:
- **basic** (heute benutzt): befiehlt der Pumpe eine **Geschwindigkeit**: „Ruder so schnell nach Backbord bewegen“.
- **absolute** (vorhanden, nie gefahren): befiehlt eine **Ruderlage**: „Ruder auf 8° Backbord“. Ein zweiter, kleiner
  Regler fährt die Pumpe, bis der Ruderlagengeber diese Lage meldet. So arbeitet der Robertson an Bord.

Dazu kommt ein dritter, eigener Regler, **adaptive** (Abschnitt 7; im Gerät bis zur Umbenennung noch „suan“).

## 3. Der wichtigste Unterschied zwischen basic und absolute
Bei **basic** wirkt jeder Befehl, solange er anliegt, und das Ruder wandert immer weiter. Das hat Folgen:
- Ein Kursfehler, der eine Weile besteht, legt immer mehr Ruder. P wirkt deshalb wie ein **Speicher**.
  Bei wenig Fahrt reagiert das Schiff träge, das Ruder läuft zu weit, und das Schiff pendelt.
- Das Glied für die Drehrate (D) ergibt ein Ruder im Verhältnis zur Kursänderung. D ist die Hauptkraft von basic.
  Am 30.09. war der Anteil von D im Mittel etwa neunmal so groß wie der von P.
- Die passenden Werte hängen stark vom Wetter ab: Bei Starkwind war etwa fünfmal so viel P nötig wie bei Leichtwind.

Bei **absolute** gehört zu jedem Kursfehler eine feste Ruderlage. Wie stark das Schiff dreht, macht weniger aus.
Feste Werte für jedes Wetter sind damit eher möglich. Der Haken: Der Ruderlagengeber meldet etwa 1 s zu spät
(gemessen 29.09.). Der kleine Regler sieht deshalb eine alte Ruderlage und kann über das Ziel hinausfahren.

## 4. Einstellungen, die für jeden Regler gelten
| Wert | Bedeutung | Höher | Niedriger |
|---|---|---|---|
| servo.gain (Verstärkung) | multipliziert jeden Pumpenbefehl | alles kräftiger; mit 1,3 schaukelte das Schiff (02.10.) | alles sanfter, Pumpe leiser; unter 0,7 zu schwach (01.10.) |
| servo.period (Takt) | kleine Befehle werden gesammelt, bis sich ein Stoß lohnt; Richtungswechsel frühestens nach dieser Zeit | wenige, grobe Stöße; 0,4 war schlechter (01.10.) | viele kurze Stöße, mehr Verschleiß |
| servo.max_current (Stromgrenze) | Schutz: darüber schaltet die Pumpe ab | schlechterer Schutz für Motor und Controller | Pumpe schaltet gerade in der Böe ab, wenn der Ruderdruck am größten ist |
| servo.speed.min / max | Pumpendrehzahl in % | – | 100/100 (03.10.): Befehl immer voll, nur ein und aus; der Controller fährt die Spannung aber bei jedem Start über eine **Rampe** hoch (servo.max_slew_speed, nach Code) |
| Drehrate-Filter | glättet die gemessene Drehrate | schneller, nervöser | ruhiger, aber verspätet; 0,05 war zu träge (01.10.) |
| Ruderbereich | Anschlag in Grad (±30°) | – | keine Stellschraube, nur bei der Kalibrierung |

Weil die Pumpe nur ein und aus kann, wird ein kleiner Befehl zu wenigen kurzen Stößen (30.09.: unter 0,2 lief sie nur
10–15 % der Zeit, ab 0,8 durchgehend). Kurze Stöße laufen wegen der Rampe zum Teil mit verminderter Spannung.

## 5. Regler basic im Einzelnen
### 5.1 Die Glieder
| Glied | Reagiert auf | Wirkt | Höher | Niedriger |
|---|---|---|---|---|
| **P** | Kursfehler | wie ein Speicher, legt immer mehr Ruder | kommt schneller zurück, pendelt aber bei wenig Fahrt | träge, in der Böe zu schwach |
| **PR** | Wurzel des Kursfehlers | wie P, nimmt kleine Fehler aber ernster | reagiert auf jede Kleinigkeit, mehr Pumpenstöße | kleine Fehler bleiben stehen |
| **I** | Kursfehler, über lange Zeit aufsummiert | hält die Dauer-Ruderlage gegen Luvgierigkeit | Trimm schneller, aber langsames Schwingen | Schiff bleibt auf einer Seite neben dem Kurs |
| **D** | Drehrate | Bremse: nimmt das Ruder weg, wenn das Schiff zurückdreht | ruhiger, aber Pumpe arbeitet bei jeder Welle | Schiff schießt über den Kurs hinaus |
| **DD** | Änderung der Drehrate | merkt früh, dass eine Drehung beginnt | sehr empfindlich für Wellen | reagiert später |
| **FF** | Sollkurs-Änderung per Taste | kurzer Ruderstoß beim Kurswechsel, sonst null | schneller Kurswechsel, schießt über | langsamer Kurswechsel |
| **R** | eigener Befehl von vor 1 s | zieht ihn wieder ab | 0,01 war schlechter (01.10.) | 0 = aus (heute) |
| **H** | Änderung der Krängung (eigener Zusatz 01.10.) | gibt Gegenruder, wenn die Böe das Schiff neigt | nimmt das Ruder nach der Böe ebenso schnell wieder weg | weniger Hilfe in der Böe |

Besonderheiten:
- I beginnt nach jedem Einschalten bei null und ist nach oben begrenzt. Am 02.10. fiel das Schiff deshalb nach dem
  Einschalten 4 min lang etwa 8° ab, bis I die Dauer-Ruderlage aufgebaut hatte.
- Die **Krängung selbst** (wie stark das Schiff geneigt ist) kennt basic nicht. H reagiert nur auf ihre **Änderung**.
  Die Dauer-Ruderlage, die mit der Krängung wächst, muss deshalb das langsame I liefern.
- Alles wird mit servo.gain multipliziert. Wer gain ändert, ändert alle Glieder zugleich.
- basic regelt nur den Kurs, nicht die Ruderlage. Fördert die Pumpe schlecht, gibt er einfach länger Befehle; das Schiff
  wird nur träge. Darum fällt ein Pumpenfehler bei basic kaum auf, bei einem Regler mit Ruderlage dagegen sofort.

### 5.2 Symptome und was hilft (aus den Fahrtests)
| Was man sieht | Ursache | Abhilfe | Beleg |
|---|---|---|---|
| Langsames Pendeln, 25–40 s, ±10–25°, bei wenig Wind oder wenig Fahrt | P zu groß (Speichereffekt) | **P senken**, etwa halbieren. **Nicht** gain erhöhen | 02.10.: P 0,02 → 0,0099, Kurs Ø 10,5° → 2,9° |
| Pumpe schaltet im Wellentakt ständig hin und her, Kurs im Mittel gut | Regler steuert jeder Welle nach | **gain senken**, dann DD; Filter 0,1 | 01.10.: gain 1,6 → 0,7, Pumpe von 56 % auf 27 % der Zeit |
| Schiff bleibt dauerhaft einige Grad auf einer Seite (meist nach Luv) | I fehlt oder ist zu klein | **I erhöhen** | 30.09.: I 0 → 0,05, Versatz nach Luv 5,2° → 1,9° |
| Nach dem Einschalten minutenlang Abfallen oder Anluven, dann gut | I beginnt bei null | Abwarten oder kurz von Hand nachsteuern; kein Wert hilft | 02.10., 11:56 |
| Anluven in Böen (Sonnenschuss) | Böe neigt das Schiff, Ruder kommt zu spät | **H** 0,5; bei Starkwind **P und I etwas erhöhen** | 01.10.: H halbierte das Anluven; 02.10.: P 0,005, I 0,08 bei 11–17 kn meist ±5° |
| Pendeln, nachdem P für Starkwind erhöht wurde und der Wind nachlässt | Starkwind-Werte passen nicht zum Leichtwind | **P wieder senken** | 02.10.: P 0,01 bei 9–10 kn: ±20° |
| Ruder am Anschlag (±30°), Schiff luvt trotzdem an | Gegenruder kommt zu spät oder zu schwach | **P und I erhöhen** (früher, kräftiger); liegt es dann noch am Anschlag, reicht das Ruder nicht | 02.10.: mit P 0,0025 Anschlag bei 18,5 kn; mit P 0,005 / I 0,08 Böen bis 17 kn bei höchstens −27° |
| Kleine Abweichungen bleiben stehen | PR zu klein | **PR erhöhen** | – |
| Viele kleine Pumpenstöße, Kurs trotzdem gut | PR zu groß | **PR senken** | 02.10.: 0,0199 → 0,01, Wechsel 4,3 → 3,3/min |
| Schießt nach Kurswechsel per Taste über das Ziel | FF zu groß | **FF senken** | 02.10.: FF 3,0: 10° über das Ziel |
| Kurswechsel dauert sehr lange | FF zu klein | **FF erhöhen**, vorsichtig | 02.10.: FF 1,61: Abfallen 57 s |
| Anluven geht schnell, Abfallen langsam | Schiff ist unsymmetrisch | mit basic nicht lösbar | 02.10. |
| Kein oder zu wenig Gegenruder; Pumpe läuft, aber mit wenig Strom, brummt dunkel | **Technik**, kein Reglerwert | Leitstand „läuft ohne Strom“; im Hafen `diagnose.py`, Spannung an den Motorklemmen messen | 30.09. |
| Nach einer Reparatur pendelt das Schiff | Notbehelf-Werte gegen das defekte Teil noch gesetzt | alle zuletzt erhöhten Werte zurücknehmen | 02.10., Chronik |

### 5.3 Vorgehen beim Verbessern
- Immer **einen** Wert ändern, in kleinen Schritten (etwa ×1,5 oder ÷2), dann **4–5 min** beobachten.
- Nur bei **gleichen Bedingungen** vergleichen: Wind, Kurs zum Wind, Seegang, Krängung, Fahrt
  (Leitstand Seite „Güte“, Kasten Umwelt). Ändert sich der Wind mitten im Versuch, zählt der Versuch nicht.
- Reihenfolge, die sich bewährt hat: zuerst P (Pendeln weg), dann D (Überschießen), dann gain (Pumpenarbeit),
  zuletzt I und PR (Rest-Abweichung).
- Nach jeder Änderung **mindestens 60 s warten**, bevor ausgeschaltet wird; erst dann ist sie gespeichert.
- Werte für Leichtwind und Starkwind sind verschieden. Bei basic gibt es keinen Satz, der für alles passt.

## 6. Regler absolute im Einzelnen
### 6.1 Die Glieder (Grundwert nach Code; im Gerät am 03.10. abweichend: P 0,0272, D 0,6295 – Herkunft unbekannt, nie gefahren)
| Glied | Reagiert auf | Wirkt | Höher | Niedriger |
|---|---|---|---|---|
| **P** (Grundwert 0,05, höchstens 2) | Kursfehler | Soll-Ruderlage = P × Kursfehler: 10° Fehler × 0,05 = 0,5° Ruder | mehr Ruder je Grad Fehler; zu viel: Pendeln | Schiff bleibt neben dem Kurs |
| **I** (0, höchstens 0,05) | aufsummierter Kursfehler | Dauer-Ruderlage gegen Luvgierigkeit | Trimm schneller, Schwingen möglich | Schiff bleibt neben dem Kurs |
| **D** (0,2) | Drehrate, **ungeglättet** | Gegenruder, solange das Schiff dreht | ruhiger, aber unruhig in der Welle | Überschießen |
| **DD** (0) | Änderung der Drehrate | wie bei basic | wie bei basic | wie bei basic |
| **position.p** (0,15) | Abstand Ruder ↔ Soll-Lage | wie forsch die Pumpe zur Soll-Lage fährt | schneller am Ziel, wegen 1 s Verzögerung Überfahren | langsam |
| **position.d** (0,02) | eigene Pumpengeschwindigkeit | bremst kurz vor dem Ziel | ruhigeres Ankommen, aber langsamer | Überfahren |
| **position.i** (0) | Rest-Abstand | gleicht kleine Rest-Abstände aus | – | – |

Besonderheiten:
- Innerhalb von 1° um die Soll-Lage bleibt die Pumpe stehen.
- Fällt der Ruderlagengeber aus, schaltet der Autopilot selbst auf basic zurück.
- PR, FF, R und H gibt es in absolute nicht, die Krängung ebenfalls nicht.
- Der Grundwert P 0,05 ergibt sehr wenig Ruder. Den richtigen Wert für SuAn zeigt erst ein Versuch.

### 6.2 Symptome und was hilft (nur die Richtung, keine Messungen)
| Was man sieht | Abhilfe |
|---|---|
| Schiff bleibt deutlich neben dem Kurs, Ruder bewegt sich kaum | **P erhöhen** |
| Schiff pendelt langsam um den Kurs | **P senken** oder **D erhöhen** |
| Schiff schießt nach jeder Störung über den Kurs | **D erhöhen** |
| Ruder zuckt im Wellentakt | **D senken** |
| Dauerhafter Versatz zu einer Seite | **I erhöhen** |
| Ruder fährt über die Soll-Lage hinaus und kommt zurück (Ruder pendelt, Kurs nicht) | **position.p senken** oder **position.d erhöhen** |
| Ruder kommt nur zögernd in der Soll-Lage an | **position.p erhöhen** |
| Autopilot springt von selbst auf „basic“ | Ruderlagengeber gestört; Technik prüfen |
Erster Versuch nur in freiem Wasser, bei ruhigen Bedingungen, mit Steuermann bereit. Rückweg: Pilot „basic“ wählen.

## 7. Der dritte Regler: adaptive (eigener Regler, eingebaut)
Eigene Neuentwicklung für SuAn (`tinypilot/regler/entwurf.md`). Er befiehlt wie absolute eine **Ruderlage**,
rechnet aber ein, was SuAn ausmacht:
- **Fahrt:** Die Ruderwirkung wächst mit der Fahrt (03.10.: 0,23 °/s Drehung je Grad Ruder bei 4,4 kn, 0,42 bei
  6,5 kn). Der Regler passt seine Stärke selbst an, statt dass man P je Wetter umstellen muss.
- **Trimm:** Start mit der jetzigen Ruderlage (kein minutenlanges Abfallen), lernt langsam nach, ruht bei Kurswechsel
  und am Anschlag.
- **Geschätzte Ruderlage** aus der Pumpenlaufzeit; die 1 s verspätete Anzeige wird zeitversetzt verglichen. Die
  Rudergeschwindigkeit je Richtung lernt er laufend.
- **Kurswechsel als Rampe** mit Höchstdrehrate je Seite. **Pumpenschutz:** mindestens 1 s Pause vor jeder Umkehr.
- **Fehlertoleranz:** Pumpe schwach → melden und weitersteuern. Erst „Ruder folgt nicht“ oder fehlende Ruderanzeige →
  Übergabe an basic.
- **Werte** nur aus Messungen an SuAn (`ident.py`, Simulation `sim.py`). Geplant: zwei Sätze „ruhig“ und „sparsam“.
- **Noch nicht drin:** Dauer-Ruderlage direkt aus der Krängung, Windmodus; Filter für Wellengieren vorhanden, aber aus.
- Wählen: Weboberfläche, Reiter Gain, Pilot „adaptive“ (heute noch „suan“). Rückweg: „basic“. Werte: `setzen.py`.

# Teil 2 – Die Weboberfläche des TinyPilot
Aufruf im Browser: `http://10.10.10.164` (Adresse per DHCP, kann wechseln; Name `box`). Am 03.10. am Gerät durchgesehen.
Fünf Reiter; unten steht immer die Statuszeile. **Jede Änderung wirkt sofort**, auch während der Autopilot steuert.

**Control** – Bedienen
- Schalter **AP**: Autopilot ein (grün) / aus. Daneben Kurs (Heading) und Sollkurs (Command).
- Auswahl **Modus**: compass, gps, wind, true wind (Abschnitt 2).
- Vier große Knöpfe: Sollkurs um 10° bzw. 2° nach Backbord (links) oder Steuerbord (rechts).

**Gain** – Reglerwerte
- Oben die Auswahl **Pilot**: absolute, basic, simple, adaptive (heute noch „suan“). Hier wechselt man den Regler.
- Darunter je Glied ein Schieberegler mit Zahl, nur die Glieder des gewählten Reglers
  (bei basic: P, I, D, DD, PR, FF, R, H; bei adaptive über 30 Werte, dort besser `setzen.py`).
- Schieberegler lassen sich schlecht fein stellen. Für genaue Werte besser über den pypilot-Server setzen
  (Port 23322, `tinypilot/regler/setzen.py`).
- **Nicht hier:** servo.gain, der Drehrate-Filter und die Werte des kleinen Ruderlage-Reglers von absolute
  (position.p/i/d). Sie lassen sich nur über den pypilot-Server lesen und setzen.

**Calibration** – Kalibrieren (nur bewusst benutzen, im Hafen)
- Oben Kompasskurs, Stampfen (Pitch) und Krängung (Roll).
- Knopf **here**: Lagesensor ausrichten, wenn das Schiff gerade liegt. Der Balken darunter zeigt den Fortschritt.
- **Magnetic Heading Offset**: Korrektur für die Einbaurichtung des Kompasses (03.10.: 94).
- **Lock Calibration**: hält die Kompass-Kalibrierung fest; nicht gesetzt, sie passt sich also laufend an.
- **calibration plot**: Bild der Kompass-Kalibrierung.
- **Rudder**: Ruderanzeige, darunter die Kalibrierwerte (Offset, Scale, Non Linearity) und vier Knöpfe:
  centered (Mitte), port range (Backbord-Anschlag), starboard range (Steuerbord-Anschlag), reset.
  Ein Druck verstellt die Ruderanzeige, danach stimmen alle Ruderwerte und der Trimm im Leitstand nicht mehr.
- **Rudder Range**: Ruderbereich in Grad (30).

**Configuration** – Geräteeinstellungen (Stand 03.10.)
| Wert | Stand | Bedeutung |
|---|---|---|
| ap.tack.angle / delay / rate / threshold | 101,9° / 0 s / 19,74°/s / 50 % | Wendeautomatik (Taste Tack): Wendewinkel, Wartezeit, Drehrate |
| servo.max_current | 20 A | Stromgrenze (Abschnitt 4) |
| servo.max_slew_slow / speed | 50 / 29,9 | Anlauf-Rampe: wie schnell der Controller die Motorspannung herunter-/hochfährt (Versuch: `rampe.py`) |
| servo.period | 0,3 s | Takt (Abschnitt 4) |
| servo.speed.max / min | 100 / 100 % | volle Drehzahl, nur ein/aus |
| wind.offset | −29,32° | Einbauversatz des Windgebers |
- Dazu Verweise auf die WLAN-Einstellung und die Tasten-/Display-Einstellung.

**Statistics** – Zähler
- Amperestunden seit dem letzten Rücksetzen (03.10.: 116,8 Ah, Knopf reset), Bordspannung, Controller-Temperatur,
  Laufzeit des Autopiloten, Servo eingekuppelt (Engaged).

**Statuszeile** (immer unten)
- pypilot Server (Connected), **Servo Flags** (Meldungen des Motor-Controllers; normal „SYNC ENGAGED“, auffällig
  z. B. Überstrom), Autopilot Errors (normal leer), Antwortzeit der Webseite.

**Tasten an der Steuersäule** (gemeldet erst beim Loslassen): **1** kurz 2° nach Backbord, gehalten 10° · **2** Autopilot
ein/aus · **3** Menü (entfällt künftig, Taste dann frei) · **4** kurz 2° nach Steuerbord, gehalten 10°. Die Schrittweiten
(kleiner Schritt 2°, Grundwert 1°) stellt heute das Menü ein. Bei ausgeschaltetem Autopiloten lässt jeder Druck auf
1 oder 4 die Pumpe 1,4 s laufen (gemessen 6–7° Ruder).

# Teil 3 – Der Leitstand am Master
Programm am Master (Desktop-Symbol „Leitstand Autopilot“, Bildschirm oder VNC). Er zeigt vorrangig, **wie gut** der
Autopilot steuert (Aufzeichnung 5 Werte/s, Gütedatei je Minute). Seiten: Knöpfe oder Taste 1/2/3. Oben rechts auf jeder
Seite die **Statuszeile** (bestehende Fehler/Hinweise); eine neue rote Meldung färbt Knopf 3 rot, bis man hinsieht.

## Seite 1 „Lage“ – was passiert gerade
- **Kopfzeile:** Autopilot AN/AUS, **Regler** (bei adaptive mit Satz; gelb/rot bei Störung), Soll, Ist, Abweichung,
  **Trend 20 s** (Kursfehler über 20 s gemittelt; Wellengieren fällt so heraus), Krängung, Wind, Fahrt.
- **Ruderbalken:** Ruderlage (BB/StB), ob die Pumpe läuft, Strom.
- **Vier Verläufe der letzten 10 min:** Kursfehler (gefärbt nach Trend, weiße Linie = Trend), Ruder, Krängung, Strom
  mit Marken für jeden Pumpenlauf. **Rote Marke = Pumpe läuft ohne Strom** (≥ 1,2 s unter 2 A): Die Pumpe steht,
  das ist ein Technikfehler.
- Farben: Trend gelb ab 2°, rot ab 5°; Ruder gelb ab 25°, rot ab 29°; Krängung gelb ab 20°, rot ab 28°;
  Strom gelb ab 10 A, rot ab 15 A.

## Seite 2 „Güte“ – wie gut steuert er
- **AP-Health**, vier Kästen mit Ampel, je der letzte bewertete Wert und das Mittel über 10 min mit Tendenzpfeil:
| Kasten | Bedeutung | grün | gelb | rot |
|---|---|---|---|---|
| Kurs-Trend | wie weit der Kurs im Mittel danebenliegt | < 2° | 2–4° | > 4° |
| Pumpe Ø | Pumpenleistung (Strom × Spannung) | < 10 W | 10–25 W | > 25 W |
| Richtungswechsel | Pumpe wechselt die Richtung, pro Minute (Verschleiß) | < 8 | 8–20 | > 20 |
| Ausreißer > 10° | Anteil der Zeit mehr als 10° neben dem Kurs | < 2 % | 2–10 % | > 10 % |
  Bewertet wird nur bei eingeschaltetem Autopiloten, ohne Manöver und nach dem Einschwingen.
- **Gesamtampel 60 min:** je Minute ein Feld in der schlechtesten der vier Farben. „aus“ = Autopilot aus,
  „M“ = Manöver. Ein **blauer Strich** mit Namen (z. B. „P“, „Regler“) zeigt einen Wert- oder Reglerwechsel.
- **Umwelt:** Wind und Böen, Kurs zum Wind, Seegang (aus dem Stampfen), Krängung mit Ursache, Fahrt; je Ø 10 min.
- **Trimm:** Dauer-Ruderlage geradeaus je Bug (Wind von BB/StB), um den Anzeigefehler (+2,9°) berichtigt.
- **Reglerwerte:** wann zuletzt was geändert wurde.

## Seite 3 „Einstellungen & Meldungen“
- **Regler** (basic/adaptive) und **Satz** (ruhig/sparsam) umschalten, wie in der Weboberfläche: mit Rückfrage, der
  TinyPilot bestätigt, die Änderung wird markiert. „sparsam“ gesperrt, bis eingestellt. Daneben Zustand von adaptive.
- **Bestehende Probleme** und **Meldungen** mit Uhrzeit (rot = Fehler, gelb = Hinweis): keine Daten, Servo-Meldung,
  kein Kompasskurs, Bordspannung, Controller-Temperatur, Ruder am Bereichsende, Uhrzeit falsch, Autopilot aus,
  Selbsthilfe, adaptive „Pumpe schwach“ und Übergabe an basic.

## So hilft der Leitstand beim Einstellen
1. Umwelt-Kästen merken, Gesamtampel 5 min beobachten. Dann einen Wert ändern (blauer Strich markiert ihn).
2. 4–5 min warten, die vier Kästen vergleichen. Ändern sich Wind oder Kurs zum Wind stark, zählt es nicht.
3. Roter Kasten → Symptomtabelle: Trend = Pendeln/Versatz, Pumpe/Wechsel = zu viel Arbeit (gain, DD), Ausreißer = Böen.
4. Rote Marken „läuft ohne Strom“ oder Servo-Meldungen: erst die Technik prüfen, dann die Werte.
