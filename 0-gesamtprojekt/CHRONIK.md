# Chronik – nur Lehren

## 2026-09-29 – Die Ruderlage kommt etwa 1 s verzögert an
Ursachen: der Mittelwert über 30 Messungen im RF300-Interface und die Glättung R6/C6
(Zeitkonstante 0,1 s, berechnet). Eine erste Schätzung lag bei 0,25 s; **gemessen** sind es
etwa 1 s: Nach Pumpenstart bleibt der Messwert 1–1,5 s fast stehen, nach Pumpenstopp läuft er
noch etwa 1 s nach (Aufzeichnung mit 0,1 s Auflösung).
- Für den Kursregler nicht maßgeblich (Einstufung des Betreibers: Trägheit eines 15-t-Schiffes;
  der Grundregler von PyPilot braucht die Ruderlage laut Handbuch nicht).
- **Erschwert eine Positionsregelung, schließt sie nicht aus:** Ein einzelnes „fahre 2°“ überschoss um 3–6°,
  ungleich je Richtung. Deshalb arbeitet die Handsteuerung mit fester Pumpenzeit.
**Lehre:** Alles, was auf die gemessene Ruderlage hin regelt, muss mit 1 s Verzögerung rechnen.
Schätzungen von Verzögerungen nicht ohne Messung als Grundlage nehmen.

## 2026-09-30 – Zwei Uhrsteller, zwei GPS-Daten: die Master-Uhr springt
**Lehre:** Stellen zwei Programme die Uhr aus verschiedenen GPS-Quellen, stellen sie sich gegenseitig
um. Ein Aufzeichnungsprogramm, das seinen Takt nach der Uhrzeit richtet, schreibt bei einem Rücksprung
nichts – so fehlten beim Fahrtest bis zu 8 min am Stück. Takt nach einem nicht springenden Zähler richten.

## 2026-10-01 – Neuer Motor-Controller überschreibt Einstellungen im TinyPilot
Beim ersten Verbinden lädt pypilot Ruder-Nullpunkt, -Maßstab, -Bereich und Stromgrenze aus dem Speicher
des Controllers; der Ersatz brachte Werkswerte mit (Ruderrichtung vertauscht, 10 A).
**Lehre:** Nach jedem Controllertausch Ruderrichtung, Kalibrierung, Stromgrenze und servo.gain prüfen.

## 2026-10-01 – Optimiert wird nach dem Trend, nicht nach dem Augenblickskurs
Der Augenblickskurs enthält das Wellengieren (2,6 s), das kein Autopilot aussteuern kann. Nach diesem Maß
optimiert, blieb die Pumpe bei ~55 %; nach dem Trend (20-s-Mittel) sank sie auf 27 % bei gleich gutem Kurs.
**Lehre:** Gütemaß ist der Trend; Wellengieren aussitzen.

## 2026-10-02 – Gegen ein defektes Teil hochgedrehte Werte nach der Reparatur zurücknehmen
P war am 30.09. gegen den ausfallenden Controller verdoppelt worden; mit dem Ersatzgerät pendelte das Schiff
bei Leichtwind mit 40 s Periode und ±25°. Mehr servo.gain verschlimmerte es (erste Deutung war falsch).
**Lehre:** Nach jeder Reparatur alle Notbehelf-Werte prüfen. Reglerwerte hängen stark von den Bedingungen ab
(wirksames P bei Starkwind ~5× Leichtwind) – ein einziger Satz passt nicht für alles.

## 2026-10-02 – Zwei Tage Werte optimiert, ohne die Bauart des Reglers zu prüfen
„basic“ befiehlt Pumpengeschwindigkeit: Pendeln bei Flaute, Ruderanschlag in Böen, P je Wind 5-mal verschieden.
Der Robertson (Ruderlage-Regler, gleiche Pumpe) steuert mit festen Werten bei jedem Wetter; die Marktrecherche
vom 01.10. hatte Ruderlage-Regelung als Standard belegt, „absolute“ wurde wegen 1 s Verzögerung zurückgestellt.
**Lehre:** Erst die Bauart prüfen, dann die Werte. Ein bewährtes Vorbild an Bord ist der Maßstab.

## 2026-10-04 – Pumpenfehler zuerst falsch gedeutet
Rückwärts zeitweise nur ~1,4 A und Brummen; gedeutet als „Motor dreht frei, Pumpe fördert nicht“, dann als Rampe.
Das Multimeter an den Motorklemmen zeigte 1,9 V statt 11 V: Der Motor steht, die Endstufe liefert nicht.
**Lehre:** Erst an den Motorklemmen messen, dann deuten. Strom allein unterscheidet Pumpe und Endstufe nicht.

## 2026-10-05 – Platine nicht nach ihrem eigenen Schaltplan bestückt
Der RF300 bekommt an der Interfaceplatine 6,89 V, am Robertson-Originalgerät dagegen 10,8 V – gut die doppelte
Spannung. Aus Strom und Spannung gerechnet sitzt in der Zuleitung ein Widerstand von rund 410 Ω; gezeichnet sind
im eigenen Schaltplan 100 Ω. Über Jahre unbemerkt, gefunden erst beim Vergleich mit dem Gerät des Herstellers.
**Lehre:** Der Schaltplan beweist nicht, was auf der Platine sitzt. Wo ein Messwert nicht passt, zuerst das
Bauteil nachmessen – und wenn ein Vorbild des Herstellers an Bord ist, daran vergleichen.
Danach wurden die 10,8 V ohne Beleg zum Sollwert erklärt; es folgten eine riskante Abhilfe (R1 auf 100 Ω, schwächt
das Signal) und eine unnötig aufwendige Neuschaltung. **Lehre:** Ein Vorbild liefert Vergleichswerte, keine Sollwerte.

## 2026-10-06 – Der Leitstand zeigte eingefrorene Werte als echt
Nach einem Neustart des TinyPilot blieb die Verbindung der Aufzeichnung am Master „offen“, lieferte aber nichts mehr.
Die Aufzeichnung schrieb weiter jede Zeile mit frischer Uhrzeit und den alten Werten; der Leitstand prüfte nur diese Uhrzeit
und zeigte Kurs 259° statt 289°, Autopilot AUS statt AN. Gemessen: 400 Zeilen mit demselben Kurs.
**Lehre:** Bei einem Zeitstempel zählt, wann der Wert ankam, nicht wann er aufgeschrieben wurde. Eine Verbindung ohne
Daten ist tot, auch wenn sie noch „offen“ heißt: nach 6 s Stille neu verbinden, im Leitstand alles grau.

## 2026-10-06 – WLAN des Masters nahm einen PC 40 Minuten lang nicht an
Seit 12:47 kam keine Anmeldung des PCs mehr im Zugangspunkt an; das Systemprotokoll des Masters war von 12:47 bis zum
Neustart um 13:27 leer, die Aufzeichnung lief weiter. Vorher hatte der PC sich ab 12:22 ständig neu angemeldet.
Gleichzeitig suchte der Leitstand alle 30 s das ganze Netz ab (254 Rundrufe); ob das die Ursache war, ist **nicht bewiesen**.
**Lehre:** Der eingebaute WLAN-Chip des Pi 3B+ ist empfindlich: keine Rundruf-Suche im Dauerbetrieb. Netzsuche nur auf Anforderung.

## 2026-10-08 – Zwei Tage die Stromversorgung verdächtigt, die Drehzahl klärte es in einer Stunde
Nach den Fahrdaten (06.10.) galten Spannungseinbrüche in Leitungen und Kontakten als Auslöser des Rückwärtsausfalls.
Im Hafen zeigte ein einziger Lauf mit 60 % statt 100 %: Die Pumpe läuft, obwohl die Spannung dabei am tiefsten war.
Die Grenze (Befehl 0,88 läuft, 0,92 versagt) traf genau den Wechsel der Firmware auf Dauer-Ein bei 0,90.
**Lehre:** Bei einem Leistungsfehler zuerst die eigene Stellgröße (Drehzahl, Richtung) stufenweise ändern und mit dem
Code der Gegenseite vergleichen. Höhere Spannung in gestörten Läufen ist Folge des kleinen Stroms, kein Gegenbeweis.

## 2026-10-09 – Schaltplan Motor-Controller: zwei Fehler, die erst die Prüfung fand
Ein Spannungszeichen (PWR_FLAG) lag mitten auf einer Leitung und war **nicht** verbunden — KiCad verbindet nur an
Leitungsenden; erst die Regelprüfung meldete die Referenz als unversorgt. Eine Notiz im Plan behauptete, bestimmte
ESP32-Anschlüsse gäben beim Start nichts aus; Espressif sagt das nicht, erst der Abgleich mit dem Herstellerdokument fand es.
**Lehre:** Ein Schaltplan ist erst fertig, wenn die Regelprüfung ohne Fehler ist, jede Verbindung des Blockschaltbilds in
der Netzliste nachgewiesen ist und jede Aussage über Anschlüsse einen Herstellerbeleg hat.

## 2026-10-09 – Leitstand und Pumpenüberwachung drei Tage blind, ohne Fehlermeldung
Die Aufzeichnung legt ihre Datei an, bevor der TinyPilot antwortet; Leitstand und Überwachung lasen die leere Kopfzeile und
verwarfen danach jede Zeile. Seite „Güte“ zeigte seit 06.10. die Werte von damals als aktuell.
**Lehre:** Wer einer neuen Datei folgt, liest sie erst, wenn die Kopfzeile vollständig ist. Jede Anzeige prüft das Alter ihrer Daten.
