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
