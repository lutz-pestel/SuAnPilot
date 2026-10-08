# Unterprojekt Motor-Controller-Neubau

**Ideensammlung.** Noch nicht gestartet. Jede Anforderung wird vor Projektstart einzeln geprüft.
Version 00.08, Stand: 08.10.2026, Obergrenze 200 Zeilen. Bauteilwahl: `Bauteilauswahl.md`.

## 1. Ziel und Abgrenzung
- Ein Gerät ersetzt **Motor-Controller und RF300-Interfaceplatine** gemeinsam.
- Leistungsteil: **handelsübliche H-Brücke** (Motor-Umpolschaltung). Steuerung, Messung und
  Kommunikation („Interface“) bauen wir selbst. Vorab wird recherchiert, ob es etwas Passendes fertig gibt.
- Keine Endlagenschalter, keine Kupplung. Einbau im Motorraum, Verbindung wie heute als RS422 im
  vorhandenen 8-adrigen Kabel zur PyPilot-Einheit.

## 2. Was ersetzt wird und warum
- Heute: RF300 (Frequenz) → RF300-Interface (Arduino, Mittel über 30 Messungen, PWM, Glättung) →
  0–5 V → fertig gekaufter „pypilot hydraulic motor controller“ (Arduino Nano, H-Brücke aus vier
  N-Kanal-Transistoren) → Pumpe; seriell zum TinyPilot, NMEA-Ruderlage über das Interface zur Anzeige.
- Schwächen, belegt in `1-tinypilot/docs/tests/2026-09-30_Fahrtest_Autopilot.md`:
  - Ruderlage kommt etwa 1 s verzögert an (Mittelung, Glättung, zweifache Umwandlung).
  - 30.09.2026: Vorwärtsrichtung fiel im Lauf des Tages aus (Befehl kam an, Strom 1,3 A statt 4–6 A),
    **ohne jede Meldung**; Controller am 01.10.2026 getauscht, Ersatz arbeitet in beide Richtungen.
  - Beim Tausch überschrieb der neue Controller Einstellungen im TinyPilot mit Werkswerten
    (Ruder-Nullpunkt und -Maßstab mit falschem Vorzeichen, Stromgrenze 10 A, servo.gain).
  - Überstrom sperrt in pypilot 0.24 eine Richtung, bis das Ruder zurückgefahren ist.
  - **Einseitiger Förderausfall, auch beim Ersatzgerät** (`1-tinypilot/docs/tests/2026-10-04_Hafen_Pumpendiagnose.md`): rückwärts
    zeitweise nur **1,9 V am Motor** statt 11 V, 1,1–1,9 A, Motor steht und brummt; Befehl voll, keine Meldung. Im Hafen
    reproduzierbar, kommt und geht; nach einem Vorwärtslauf oft wieder gut. Anlauf-Rampe als Ursache ausgeschlossen.
    Altgerät fiel vorwärts aus, Ersatzgerät rückwärts. **Ursache (08.10.2026, Hafen):** Designfehler der Endstufe – ab
    Befehl 0,90 Dauer-Ein mit kurzem Ladepuls für die Hilfsspannung des oberen Transistors (Bootstrap 0,22 µF, Diode 1N4001);
    bei Ruhe 12,6 V versagt die schwächere Seite, bei 14 V und unter 0,90 läuft sie. Leitungswiderstände sind nicht die
    Ursache. Neue pypilot-Controller (2022/2024): 10 µF, schnelle Diode, 2–4 Transistoren parallel.
    Der Robertson an derselben Versorgung zeigt die Symptome nicht: Der gekaufte Controller ist zu empfindlich.

## 3. Anforderungen
### 3.1 Funktion
- F1 Pumpe in beide Richtungen mit voller Drehzahl; beide Richtungen gleichwertig.
- F2 Motorstrom je Richtung messen, Spitzen erfassen.
- F3 RF300-Frequenz direkt messen und in Ruderlage umrechnen; Kalibrierung im Gerät. Anschluss: Abschnitt 3.3.
- F4 **Ruderlage ohne spürbare Verzögerung** (vorher B1): Für den Steuermann, besonders beim
  Manövrieren im Hafen, muss sie sofort angezeigt werden; heute etwa 1 s.
- F5 **NMEA-Ruderlage für die Anzeige am Steuerstand – vorrangig.** Sie muss auch weiterlaufen, wenn
  TinyPilot, Verbindung oder Pumpenteil ausfallen.
- F6 Endlagen per Software aus der Ruderlage (keine Endlagenschalter), mit Sicherheitsabstand zum mechanischen
  Anschlag. **Die Pumpe darf nie gegen den Anschlag laufen:** Läuft sie und bewegt sich das Ruder nicht, schaltet
  das Gerät sie so schnell wie möglich ab und meldet es. Den Abstand legt der Versuch fest.
- F7 Kommunikation mit dem TinyPilot über RS422. **Protokoll festgelegt 04.10.2026: pypilot-kompatibel**
  (38400 Baud, Pakete aus Befehl, 16-Bit-Wert und Prüfsumme). Es überträgt bereits Strom, Spannung, zwei
  Temperaturen, Ruderlage und Zustands-Flags. Zusätzliche Werte (Klemmenspannungen, Förderausfall mit Richtung,
  Buchführung, Ergebnis des Selbsttests) gehen über freie Befehlsnummern, die pypilot verwirft, oder über die
  zweite Leitung. Grund: Der TinyPilot bleibt unverändert, und der alte Controller ist im Notfall wieder
  ansteckbar – wenn auch nur als Notlösung, da beide vorhandenen Geräte je eine Richtung verloren haben.
  Dabei **nicht** übernehmen: (1) das Überschreiben der Kalibrierung im TinyPilot beim Verbinden (Anlass
  01.10.2026) – diese Pakete lässt unser Gerät weg (S7); (2) doppelte Umrechnung der Ruderlage – liegt die
  Kalibrierung im Gerät (F3), muss die Umrechnung im TinyPilot neutral gestellt werden (Nullpunkt 0, Maßstab 1).
  Das Kabel zum Steuerstand bleibt unverändert: gleicher Stecker und gleiche Belegung wie an der RF300-Interfaceplatine.
- F8 Betrieb am 12-V-Bordnetz im Motorraum (Feuchte, Wärme, Vibration).
- F9 Endstufe muss in beiden Richtungen **dauerhaft 100 %** halten (keine knappe Bootstrap-Hilfsspannung,
  sondern eingebaute Ladungspumpe). Anlauf-Rampe einstellbar. **Belegt 08.10.2026:** Der gekaufte Controller versagt genau beim
  Wechsel auf Dauer-Ein (Befehl ≥ 0,90) bei 12,6 V (`1-tinypilot/docs/tests/2026-10-08_Hafen_Pumpe_Drehzahl_Spannung.md`).
- F10 **Spannung an beiden Motorklemmen messen** (nicht nur Strom und Bordspannung) – nur so ist ein Ausfall der
  Endstufe von einem der Pumpe zu unterscheiden.
- F11 **Übertemperatur der Endstufe über deren Fehlerausgang erkennen**; das Gerät schaltet die Pumpe dann selbst
  ab und meldet es (das Modul meldet nur, es schaltet nicht ab). Zusätzlich **Vorwarnung über einen eigenen
  Temperaturfühler** an der Endstufe: Aufzeichnung und Meldung „wärmer als sonst bei gleicher Arbeit".
- F12 **WLAN für Fernprogrammierung und Zugriff.** Nach dem Einschalten 60 min aktiv, jede Nutzung verlängert;
  ein Taster schaltet es wieder ein; **blaue Leuchtdiode** zeigt an, dass es läuft. Das Gerät meldet sich zuerst
  bei „master" an; schlägt das fehl, baut es einen eigenen Zugangspunkt auf. **Programmieren nur bei stehender
  Pumpe.** Im Motorraum (Metall, geschlossenes Gehäuse) ist eine äußere Antenne nötig.
- F13 **Gemeinsame Stromversorgung:** Das Gerät erzeugt auch die 5 V für die PyPilot-Einheit (heute Aufgabe des
  RF300-Interface) – über einen **eigenen zweiten Regler**, damit ein Kurzschluss dort nicht die Ruderlagen-
  Ausgabe und die Pumpensteuerung mitnimmt (F5, S6). Kabellänge zur Steuersäule höchstens 3 m. Es bleibt beim
  vorhandenen Kabel und 5 V zum Steuerstand; der Zweig versorgt in Phase 3 auch den SuAnPilot.
- F14 **Unterspannungsfest (Pflicht).** Anlass: einseitiger Förderausfall bei tiefer Spannung am Gerät (Abschnitt 2).
  Maßstab: mindestens so unempfindlich wie der Robertson an derselben Versorgung.
  a) Hilfsspannung der Treiber unabhängig von der Bordspannung (Aufwärtswandler oder Treiber mit Ladungspumpe, vgl. F9).
  b) Kein halbes Durchschalten: Unter der Grenzspannung schaltet die Endstufe sauber ganz ab und meldet es – kein Pendeln.
  c) Mikrocontroller und Ruderlage-Ausgabe getrennt versorgt und gepuffert: kein Neustart beim Einbruch durch den Pumpenanlauf.
  d) Einbruch klein halten: Anlauf-Rampe (F9), Eingangskondensatoren.
  e) Eingangsspannung am Gerät schnell messen (kurze Einbrüche, nicht nur Mittelwert) und mit Wert melden (S2).
  f) Abnahmetest: beide Richtungen bei 100 % mit sinkender Spannung; die Ausfallgrenze ist in beiden Richtungen gleich und
     liegt unter dem tiefsten gemessenen Einbruch am Gerät (Wert erst nach Messung festlegen).
  g) Nachrangig: Zuleitung für den Anlaufstrom bemessen (Querschnitt, korrosionsfeste Verbindungen); Spannungsabfall
     unter Last bei der Inbetriebnahme messen, Grenzwert nach Messung festlegen.

### 3.2 Fehlertoleranz (vorher B2, ergänzt)
- S1 Jeder Befehl hat eine erwartete Wirkung (Pumpe läuft, Strom im erwarteten Bereich, Ruder bewegt
  sich in der befohlenen Richtung mit der erwarteten Geschwindigkeit, Schiff reagiert). Bleibt sie aus
  oder weicht sie ab, ist das eine Störung – getrennt nach Richtung erkannt.
- S2 Jede Störung wird sofort angezeigt und akustisch gemeldet; der Autopilot steuert nicht
  stillschweigend weiter. Ebenso Sensoren außerhalb plausibler Werte (Uhr, Kompass, Ruderlage, GPS-Datum).
- S3 Die Ansteuerung darf nicht davon abhängen, in welche Richtung die Pumpe zuletzt lief.
- S4 Bei Störung selbsttätig Abhilfe versuchen: verschiedene Maßnahmen nacheinander, mit
  **Buchführung**, welche gewirkt hat; die erfolgreichste kommt künftig zuerst. Kein Mensch am Ruder
  wird vorausgesetzt.
- S5 **Ein kurzer Überstromimpuls darf eine Richtung nicht dauerhaft sperren.** Nach dem Abschalten
  läuft die Pumpe nach kurzer Pause selbsttätig wieder an, mit Meldung und Buchführung; erst bei
  wiederholtem Überstrom wird gestuft reagiert.
- S6 Verbindungsverlust zum TinyPilot: Pumpe stoppt; Ruderlagenausgabe (F5) läuft weiter.
- S7 Kalibrierung und Grenzwerte bleiben beim Tausch eines Geräts erhalten bzw. werden geprüft;
  ein neues Gerät darf keine Werte ungefragt überschreiben.
- S8 Option: Doppelung des Leistungsteils (zweite H-Brücke als Reserve).
- S9 **Förderausfall selbst erkennen** und mit Richtung melden: Befehl voll, aber Klemmenspannung oder Strom zu
  niedrig bzw. Ruder steht (Anlass 04.10.2026). Der Regler muss weitersteuern können (Entwurf SuAn-Regler, Abschnitt 4).
  Ursache eingrenzen (Befehl voll, und …):
  | Spannung am Motor | Strom | Ruder | Ursache |
  |---|---|---|---|
  | niedrig (z. B. 1,9 V statt 11 V) | – | steht | Endstufe |
  | voll | keiner | steht | Kabel, Motorkohlen |
  | voll | normal | steht | Pumpe oder Hydraulik |
- S10 **Selbsttest beim Einschalten**, bevor der Autopilot gebraucht wird: erst in Ruhe (Brücke hochohmig) die
  Klemmenspannungen prüfen – ein dauerhaft leitender, also durchgebrannter Schalter verrät sich hier –, dann je
  Richtung ein kurzer Antippimpuls mit Prüfung von Klemmenspannung, Strom und Ruderbewegung. Ergebnis melden.
- Anlass S1–S3: 30.09.2026, Pumpe lief vorwärts nach vorwärts oft nicht an, ohne jede Meldung.
  Anlass S10: Derselbe Ausfall wäre vor dem Ablegen sichtbar gewesen statt mitten auf dem Wasser.

### 3.3 Anschluss des RF300
- RF300 (`1-tinypilot/rf300-interface/hardware/datenblaetter/RF 300 Ruderlagensensor.xls`): Mitte 3400 Hz, 20 Hz je Grad, ±90° = 1600–5200 Hz,
  Versorgung und Signal auf denselben zwei Adern, **polaritätsunabhängig** (Robertson-Handbücher AP300CX/AP11: Klemmen
  RF+/RF–, „non polarized“); keine Ader an Schiffsmasse (gemessen). Linearität ±3° bis 45°. Kabel an Bord höchstens
  3 m, geschirmt, Schirm an Masse, fern von Lichtmaschine und Starter (Betreiber; geliefert wird der Geber mit 10 m).
- **Arbeitspunkt gemessen 05.10.2026** (Multimeter, Bordspannung 12,73 V), an der eigenen Interfaceplatine:

  | Ruderlage | Spannung am RF300 | Strom | daraus Vorwiderstand |
  |---|---|---|---|
  | mittschiffs | 6,89 V | 14,05 mA | 416 Ω |
  | Backbord | 6,62 V | 14,8 mA | 413 Ω |
  | Steuerbord | 7,23 V | 13,5 mA | 407 Ω |

  Am Robertson-Originalgerät liegen 10,8 V am selben Geber. Das ist, was der Robertson liefert, **kein belegter
  Sollwert**: Eine Mindestspannung steht weder im Datenblatt noch in den Handbüchern, und mit 6,89 V arbeitet der
  Geber. Der Strom ändert sich mit der Ruderlage um knapp 10 % (13,5–14,8 mA). Das Robertson-Gerät schaltet ab,
  sobald die Sensorleitung unterbrochen wird; deshalb war dort kein Strom zu messen.
- Prinzip „Stromschnittstelle über zwei Adern“: Der Sensor schaltet seine Stromaufnahme im Takt zwischen zwei Werten
  um. Bewährt bei ABS-Drehzahlsensoren (7/14 mA, Frequenz als Messwert) und NAMUR-Sensoren (Industrie).
- Heutige Lösung (Interfaceplatine): Widerstand in der Zuleitung, Kondensator-Kopplung, Transistor (BC337) auf den
  Interrupt-Eingang des Arduino. Gezeichnet sind 100 Ω (R1 in der Netzliste), aus der Messung ergeben sich rund
  360–410 Ω (je nachdem, ob die Verpolschutzdiode mitzählt). Mit dem großen Widerstand werden die Sprünge groß.
- Anforderung: Speisung über einen Widerstand, der zugleich bei Kurzschluss und Masseschluss begrenzt; Auswertung
  nur der Sprünge (mitlaufend, ohne Kenntnis der Stromstufen); Schutz gegen Überspannung und Störspitzen; Störung
  erkennen über die Frequenz (kein Takt oder außerhalb 1600–5200 Hz, S2). Lösung: `Bauteilauswahl.md` Abschnitt 4.
- Unbekannt: die beiden einzelnen Stromstufen und das Tastverhältnis (ohne Oszilloskop nicht zu trennen), und ob die
  Sensorspannung die Messung beeinflusst (Frequenz mittschiffs an der Interfaceplatine und am Robertson vergleichen).

## 4. Offene Punkte
- Pumpe RPU160: Anlauf- und Blockierstrom messen; hat sie ein Überdruckventil? (Typenschild: 12 V, 7,5 A,
  3500 min⁻¹, 1,6 l/min, IP 44. Gemessen: Betrieb 4–6 A, Spitzen 8,3 A ohne Last.)
- Stromaufnahme der PyPilot-Einheit auf der 5-V-Leitung und Querschnitt des rot/schwarzen Paares messen.
- Welche Befehlsnummern des pypilot-Protokolls frei sind (Quelltext `servo.py` und `motor.ino` nachsehen).
- Doppelung (S8) ja oder nein; Gehäuse und Steckverbinder.
- Welcher Teil der Fehlertoleranz (S1–S5) liegt im Gerät, welcher im TinyPilot?
- Offene Messung: im Fehlerfall Motorklemme A und B gegen Masse an der Klemmleiste des Controllers
  (2 V an einer Klemme = oberer Transistor; 11 V = Leitung zum Motor).
- Nachrangig, erst nach bestätigter Ursache: Wo entsteht der Spannungseinbruch (Batterie, Zuleitung, Sicherung, Kontakte)?
  Batteriepole und Controller-Eingang im selben Lauf vergleichen (Hafenversuch Unterspannung, `Testplan_Autopilot.md`).
- Neuer pypilot-Controller (Mid-Power 15 A / High-Power 30 A, OpenMarine-Shop, zuletzt nicht lieferbar):
  Verträglichkeit mit pypilot 0.24 ungeprüft.

## 5. Nächste Schritte
1. Recherche fertiger Lösungen und handelsüblicher H-Brücken (Strom, Schutz, Ansteuerung).
2. Pumpendaten einholen, H-Brücke auswählen.
3. Aufbau des Interfaces festlegen (Mikrocontroller, Frequenzmessung, RS422, NMEA-Ausgang).
4. Prototyp am Tisch, dann Test an der Pumpe im Hafen.
Jeder Schritt wird einzeln vorgelegt.

## 6. Pflege
- Jede Schwäche und jedes Problem des TinyPilot wird als Anforderung hier oder in
  `3-suanpilot/autopilot/hardware/konzeption/bedieneinheit.md` aufgenommen (vorher angesagt, Regel 1).
