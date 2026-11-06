# Robnet-Analyse: Anforderungen an das Speicheroszilloskop

Version 00.02, Stand 06.11.2026. Gilt für Bauart B (Platine v00.01) mit Raspberry Pi Zero 2 W. Vom Betreiber im Dialog festgelegt, noch nicht gebaut.
Grundlage: Konzept `../hardware/konzeption/robnet-analyse.md`, Klemmen und Kanäle ebenda, Abschnitt 2, Block 4.

## 1. Zweck
Die Platine soll auch außerhalb der Bus-Analyse als einfaches Speicheroszilloskop dienen, vor allem um serielle Signale anzusehen.
Bedienung im Browser am PC, ohne Anmeldung per SSH, ohne Passwort (Betreiber). Das Programm liest nur und sendet nie auf den Bus.
**Kein Testaufbau nötig:** Die Software läuft und prüft sich ohne den Testsender (PC, FTDI232, YL-12B), den es nur am Schreibtisch gibt. Entwickelt wird mit gespeicherten Referenzaufnahmen.

## 2. Was die Platine kann (Grenzen)
- **Analog:** gemessen rund 17 000 Messungen pro Sekunde mit Python, ein Chip. Die Rate teilt sich auf die aktiven Messungen auf.
- **Bereich:** etwa 0 bis 21,7 V, Vsys+ bis etwa 33 V. Keine negativen Spannungen.
- **Digital:** Bus-Empfänger und Alarm, Zeitauflösung 2 µs. Am Testsender fehlerfrei bis 115 200 Baud.
- **Kein Ersatz für ein echtes Oszilloskop:** Kurvenformen gehen nach Faustregel bis etwa 1–2 kHz (ein Kanal).

| Messungen | Rate je Messung (gerechnet) | Punkte je Bit bei 1200 Baud | Bei 9600 Baud |
|---|---|---|---|
| 1 | 17 000/s | etwa 14 | etwa 2 |
| 2 | 8 500/s | etwa 7 | unter 1 |
| 3 | 5 700/s | etwa 5 | unter 1 |
| 4 | 4 250/s | etwa 3,5 | unter 1 |
| 5 | 3 400/s | etwa 3 | unter 1 |

Das serielle Signal zeigt daher die **digitale Spur** genau. Die analogen Kanäle zeigen Pegel und Pakete.

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
- **Serielle Anzeige:** Baudrate von Hand einstellbar, zerlegte Bytes unter der digitalen Spur. Automatische Erkennung nicht in der Oberfläche.
- **Messlinien:** zwei Linien für Zeit- und Spannungsabstand.
- **Aufzeichnung:** Dauer, Name, Speichern als CSV-Datei für Excel.

## 6. Betrieb
- **Automatischer Start** der Oberfläche mit dem Pi.
- **Knöpfe „Pi herunterfahren“ und „Neu starten“,** je mit Sicherheitsabfrage. Nach dem Herunterfahren zeigt die Seite, wann das Netzteil aus darf.
- **Während der Bus-Aufzeichnung** (`aufzeichnung`) läuft die Seite weiter, misst aber nicht: Sie zeigt „Aufzeichnung läuft“, Dauer, gespeicherte Byte, freien Speicher. Oszilloskop-Start ist gesperrt, „Herunterfahren“ warnt vorher.
- **Abtastrate messen:** In Live und Aufzeichnen zählt das Programm selbst die Messungen und zeigt die echte Rate sowie den kleinsten und größten Abstand; beim Aufzeichnen auch gespeichert.
- **Messschleife in C,** die Oberfläche in Python: bei 1 MHz Takt rund 40 000 Messungen pro Sekunde als Obergrenze (gerechnet), gleichmäßigere Abstände, ein Prozessorkern dafür reserviert. Erst bauen, wenn die Messung den Nutzen zeigt.

## 7. Offen
- **Live-Rate:** Wie viele Punkte Live über WLAN wirklich ankommen, ist nicht gemessen.
- **Abtastung in C:** Die erreichbare Rate ist noch nicht gemessen.
