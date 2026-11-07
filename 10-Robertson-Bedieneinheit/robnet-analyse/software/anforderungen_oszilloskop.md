# Robnet-Analyse: Anforderungen an Oberfläche und Speicheroszilloskop

Version 00.07, Stand 07.11.2026. Gilt für Bauart B (Platine v00.01) mit Raspberry Pi Zero 2 W. Vom Betreiber im Dialog festgelegt, gebaut als `oszilloskop_v00.02.py` mit `oszilloskop_v00.02.html`, `management_v00.01.html`, `analyse_v00.01.html`, dazu `messkern_v00.01.c` und `netz_v00.01.py`, Dienste `robnet-oszilloskop` und `robnet-netz`.
Grundlage: Konzept `../hardware/konzeption/robnet-analyse.md`, Klemmen und Kanäle ebenda, Abschnitt 2, Block 4.

## 1. Zweck
Die Platine soll auch außerhalb der Bus-Analyse als einfaches Speicheroszilloskop dienen, vor allem um serielle Signale anzusehen.
Bedienung im Browser am PC oder Handy (`http://robnet.local:8080`, zu Hause auch `192.168.178.50`), ohne Anmeldung per SSH, ohne Passwort (Betreiber).
**Drei Seiten mit gegenseitigen Links:** Messen (`/messen`, dieses Oszilloskop), Management (`/management`, Abschnitt 7), Robnet Analyse (`/analyse`, Abschnitt 8). Das Programm liest nur und sendet nie auf den Bus.
**Kein Testaufbau nötig:** Die Software läuft und prüft sich ohne den Testsender (PC, FTDI232, YL-12B), den es nur am Schreibtisch gibt. Entwickelt wird mit gespeicherten Referenzaufnahmen.

## 2. Was die Platine kann (am Pi gemessen, 06.11.2026)
- **Analog:** Messschleife in C mit direktem Registerzugriff, ein Prozessorkern reserviert. Die Rate teilt sich auf die aktiven Messungen auf.
- **Bereich:** etwa 0 bis 21,7 V, Vsys+ bis etwa 33 V. Keine negativen Spannungen.
- **Grenze Klemme 1 und 2:** Solange der Bus-Empfänger MAX3488 steckt, nur −7 V bis +12 V (Datenblatt −7,5 V bis +12,5 V, davor nur 1 kΩ). Für mehr den Chip ziehen. Die Seite zeigt dazu eine kurze rote Warnung, solange Klemme 1 oder 2 gemessen wird; sie lässt sich ausblenden und kommt nach Neuladen oder wenn beide aus und wieder an sind zurück.
- **Digital:** Bus-Empfänger und Alarm, Zeitauflösung 2 µs. Am Testsender fehlerfrei bis 115 200 Baud. Digital gegen analog gemessen auf etwa 3 µs genau.

| Geschwindigkeit | Takt | Messungen/s | Je Kanal bei 5 Kanälen | Bordspannung roh, ohne Korrektur |
|---|---|---|---|---|
| Maximum (voreingestellt) | 7,14 MHz | 234 000 | 47 000 | 7,4 V statt 11,73 V |
| Schnell | 4 MHz | 139 000 | 28 000 | 8,37 V statt 11,73 V |
| Mittel | 2 MHz | 72 000 | 14 000 | 9,89 V statt 11,73 V |
| Genau | 0,5 MHz | 18 400 | 3 700 | 11,73 V, Bezugswert |

- **Maximum:** Teiler 56. Ab Teiler 52 treten Lesefehler auf, deshalb ist 56 gewählt. Das liegt über dem Datenblatt-Takt des Wandlers.
- **Korrektur:** Der hohe Eingangswiderstand (Teiler 100 kΩ/13 kΩ) lässt den Wandler bei hohem Takt zu niedrig messen. Bei jedem Umschalten vergleicht das Programm die Bordspannung bei 0,5 MHz und im gewählten Takt und rechnet den Faktor ein, dazu einen gemessenen Nullpunkt. So bleibt die Bordspannung bei allen Stufen 11,73 V.
- **Masse nötig:** Ohne gemeinsame Masse stört das PC-Netzteil die Analogkurven über den USB-Testsender (Spitzen bis 8,5 V). Mit Massekabel sind sie weg, die Digitalspur läuft auch ohne.
- **Gegenprobe:** Hoher Pegel bei „Genau“ und „Maximum“ bis zu 4 % auseinander, ein anderes Messgerät fehlt noch.
- **Zeichenfenster, Grenze (07.11.2026, Testsender):** Pakete mit Pausen fehlerfrei bis 115 200 Baud. Dauerdaten ohne Pause bei laufendem Bild fehlerfrei bis 19 200 Baud, bei 38 400 Baud kamen 18 834 von 21 000 Zeichen an. Ohne Bild bei 57 600 Baud 27 065 von 28 000, bei 115 200 Baud 36 251 von 70 000.

## 3. Kanäle
- **Höchstens 5 Kanäle,** Anzahl einstellbar, **voreingestellt 1.**
- **Nur Seite Hauptgerät (J1), kein Umschalten.** Kanal 1 = Klemme 1 (Bus−), Kanal 2 = Klemme 2 (Bus+), Kanal 3 = Klemme 3 (Vsys+), Kanal 4 = Klemme 5 (On-Off), Kanal 5 = Klemme 6 (Alarm). Alle am oberen Sockel (U2).
- **Je Kanal:** an oder aus schalten.
- **Vergleichsmessungen:** Klemme 1 gegen 2 und Klemme 5 gegen 6.
  - Klemme 1 gegen 2 kann im Chip gemessen werden (nur positive Differenz). Klemme 5 gegen 6: nur in der Software.
  - In der Software zählt eine Differenz als zwei Messungen, mit Zeitversatz von etwa 60 µs (gerechnet).
- **Digitale Spuren:** Bus-Empfänger und Alarm, je ein oder aus. Sie mindern die analoge Rate nicht.

## 4. Betriebsarten
- **Live** (voreingestellt): Die Kurve wird ständig aktualisiert.
- **Aufzeichnen:** Alle Punkte werden auf der Karte gespeichert und danach angesehen, mit Zoom bis auf einzelne Bits. Für alles, was schneller gehen muss.
- **Umschaltbar** in der Oberfläche.

## 5. Einstellungen und Anzeige
- **Maßstab:** Zeit und Spannung je Kästchen, senkrechte Verschiebung.
- **Trigger:** Kanal, Spannung, steigend oder fallend, Vorlauf; Auto, Normal oder Einmal.
- **Serielle Anzeige:** Baudrate von Hand einstellbar, zerlegte Bytes unter der digitalen Spur; „keine Bytes“ schaltet das Zerlegen aus.
- **Baudrate automatisch:** Der Knopf „Automatisch“ misst 4 Sekunden am Bus-Empfänger, sucht den kürzesten Puls, prüft die Rate durch Probe-Zerlegung und stellt sie ein. Liegt die Rate nicht in der Liste oder fehlt das Signal, bleibt die Einstellung und eine Meldung nennt den Grund. Zeigt ein hoher Anteil unlesbarer Zeichen, dass das Format vielleicht nicht passt, wird das gemeldet. Am Testsender alle 10 Raten von 300 bis 115 200 Baud richtig erkannt, auch ohne einzelne Bits im Signal (Zeichen 3C); 14 400 Baud wird als nicht in der Liste gemeldet.
- **Zeit zur Baudrate:** Beim Wechsel der Baudrate springt die Zeit je Kästchen auf mindestens 6 Zeichen im Bild und bleibt danach frei änderbar. Dahinter steht der Bereich „Text lesbar“, rot, wenn die Zeit außerhalb liegt. Unter 6 Zeichen im Bild wurden am Testsender viele Zeichen falsch.
- **Zeichenfenster:** Unter dem Bild, lückenlos aus den Pegelwechseln, unabhängig von Bild und Trigger. Jede Zeile zeigt Hex-Werte und Klartext; neue Zeile nach einer Pause über 3 Zeichendauern, nach Zeilenvorschub oder nach 16 Zeichen. Knöpfe Anhalten (sammelt weiter), Löschen, Speichern als Textdatei. Nennt die Zahl unlesbarer Zeichen; rot nur, wenn in den letzten Sekunden über 5 % unlesbar waren. Verlorene Pegelwechsel sind immer rot.
- **Aufteilung:** Beide Spalten scrollen unabhängig voneinander. Auf Handys stehen sie untereinander, das Bild passt sich an, in beiden Lagen; Bedienkästen sind aufklappbar und beim Laden zu. Eine feste Querlage gibt es nicht (Safari kann sie nicht sperren).
- **Messlinien:** zwei Linien für Zeit- und Spannungsabstand.
- **Aufzeichnung:** Dauer, Name, Speichern als CSV-Datei für Excel.

## 6. Betrieb
- **Automatischer Start** der Oberfläche mit dem Pi.
- **Knöpfe „Herunterfahren“ und „Neu starten“** auf der Seite Management, je mit Sicherheitsabfrage. Nach dem Herunterfahren zeigt die Seite, wann das Netzteil aus darf.
- **Während der Bus-Aufzeichnung** (`aufzeichnung`) läuft die Seite weiter, misst aber nicht: Sie zeigt „Aufzeichnung läuft“, Dauer, gespeicherte Byte, freien Speicher. Oszilloskop-Start ist gesperrt, „Herunterfahren“ warnt vorher.
- **Abtastrate messen:** In Live und Aufzeichnen zählt das Programm selbst die Messungen und zeigt die echte Rate sowie den kleinsten und größten Abstand; beim Aufzeichnen auch gespeichert.
- **Messschleife in C,** die Oberfläche in Python. Sie läuft nur, solange jemand zusieht, und gibt den Wandler nach 15 Sekunden ohne Abruf wieder frei.

## 7. Management und Netz
**Grundsatz (Betreiber):** Der Pi sorgt selbst dafür, dass er immer erreichbar ist, und der Nutzer kann einfach von einem Netz zum anderen wechseln.
- **Anzeige, gut sichtbar:** Netzname, Adresse des Zugangspunkts, eigene Adresse des Pi.
- **Start:** Der Pi bucht sich in ein gespeichertes Netz ein, das zuletzt erfolgreiche zuerst. Am Schreibtisch: nach dem Neustart 22 s bis zur Antwort.
- **Kein Netz:** Nach 60 s ohne bekanntes Netz, beim Start wie im Betrieb, startet er den eigenen Zugangspunkt `robnet`, Adresse `192.168.4.1`, mit Passwort. Das Passwort steht nur auf dem Pi, nicht in Git und nicht auf den Seiten.
- **Zurück vom eigenen Zugangspunkt:** nur auf Anweisung des Nutzers oder nach einem Neustart (Betreiber).
- **Wechsel:** Netz aus der Liste wählen oder eintippen, mit Passwort. Scheitert er, ist das neue Passwort verworfen und der Pi kehrt zum vorigen Netz zurück (am Schreibtisch nach 30 bis 40 s), scheitert auch das, zum eigenen Zugangspunkt.
- **Gespeicherte Netze:** Übersicht zum schnellen Umschalten, einzeln entfernbar. „Nur speichern“ legt ein Netz außer Reichweite an.
- **Passwörter ändern:** Knopf je gespeichertem Netz; „Verbinden“ prüft das neue Passwort und behält bei Fehlschlag das alte, „Nur speichern“ ersetzt es ungeprüft. Das Passwort des eigenen Zugangspunkts wird auf der Seite doppelt eingegeben und gilt sofort; läuft er gerade, startet er neu.
- **Funk:** ein gesteckter WLAN-Stick hat Vorrang vor dem eingebauten WLAN.
- **Im eigenen Zugangspunkt** kann der Pi nicht suchen, die Seite zeigt die letzte Suche, Netznamen lassen sich eintippen.

## 8. Robnet Analyse
Bus-Aufzeichnung (`aufzeichnung_v00.02.py`) im Browser starten und stoppen, Baudrate von Hand oder automatisch, Dauer, Stellung, Notiz. Liste der Aufzeichnungen mit Auswertung (`auswertung_v00.03.py`) und Spannungen als CSV; im Bild ansehen auf der Seite Messen.

## 9. Offen
- **Eigener Zugangspunkt mit Gerät:** Am Pi geprüft, die Anmeldung eines Geräts noch nicht.
- **WLAN-Stick:** Der Vorrang ist nicht erprobt.
- **Handy:** nur in einem schmalen Fenster am PC geprüft, nicht auf dem iPhone.
- **Robnet Analyse mit Daten:** Die Aufzeichnung über die Seite lief ohne Signal; die Auswertung ist mit einer Referenzaufnahme geprüft.
- **Herunterfahren-Knopf:** nicht ausgelöst, der gleiche Weg ist über „Neu starten“ geprüft.
- **Alter Zero:** Die Messschleife ist nur auf dem Zero 2 W gebaut und gemessen.
