# Lagesensor (IMU) für die Überarbeitung des TinyPilot

Version 00.01, Stand 01.11.2026, Obergrenze 100 Zeilen.
Gilt für den neuen Lage- und Kompasssensor (Phase 3, `3-suanpilot/autopilot/hardware/konzeption/bedieneinheit.md`, U3).
Heute eingebaut: MPU9250 auf der Hauptplatine. Preise nur zur Größenordnung.

## 1. Was pypilot vom Sensor verlangt (aus dem Code von pypilot 0.24)
1. **Anschluss:** Rohwerte für Beschleunigung, Drehrate und Magnetfeld (je 3 Achsen) über I2C. Die Sensorbibliothek
   RTIMULib2 muss den Chip selbst erkennen. USB oder seriell geht nicht.
2. **Takt:** Der Sensor misst 100-mal je Sekunde. pypilot liest 10- oder 20-mal je Sekunde, und jede Regelrunde wartet darauf.
3. **Bereich:** ±2 g und ±250 °/s. SuAn dreht nur wenige °/s, deshalb zählt die Auflösung mehr als der Bereich.
4. **Der Kreisel (Drehratensensor) bestimmt fast alles:** Der Kurs entsteht fast ganz aus ihm. Kompass und Schwerkraft
   korrigieren nur langsam (Gewicht 1 %). Drehrate und Drehbeschleunigung gehen direkt in den Ruderbefehl (Glieder D, DD).
   Sein Nullpunkt wird alle 30 s gespeichert.
5. **Ausfall:** Bei Kreisel über 55 °/s im Mittel, Kompass über 1000 µT oder einem Lesefehler wird der Sensor neu
   gestartet. Kommt 1 s lang kein Wert, gibt es keinen Kurs mehr.
6. **Kompass-Kalibrierung:** läuft von selbst während der Fahrt. Sie braucht mindestens 240° gefahrene Kurse,
   7–120 µT und eine Inklination unter 82°. Sie gleicht nur eine Verschiebung aus (Kugel-Kalibrierung). Ungleich
   empfindliche oder schiefe Achsen gleicht sie nicht aus; der Ellipsoid-Teil ist im Code abgeschaltet.
7. **SuAn (04.10.2026):** Der Kursfehler läuft im Takt des Rollens mit (r −0,6), Ursache ungeklärt. Deshalb gilt:
   Der Kurs darf sich beim Rollen nicht ändern.
8. **Einbau:** Steuerstand im Freien (Temperatur, Feuchte). Abstand zu Eisen und Stromkabeln ist noch zu klären (TODO 16).
9. **Einbau in jeder Lage** (Betreiber, 01.11.2026): leistet pypilot selbst (Knopf „here“ und Kurs-Versatz).
   Voraussetzung: Kreisel, Beschleunigung und Magnetometer sitzen fest zueinander.

Der pypilot-Entwickler sagt dasselbe wie Punkt 4: Begrenzend ist der Kreisel, nicht der Kompass.

## 2. Rangfolge
1. **SparkFun SEN-19895** (ISM330DHCX + MMC5983MA, beide auf einer Platine). Kreisel und Magnetometer sind von allen
   Kandidaten die besten, beide lieferbar. ST sagt für den ISM330DHCX 10 Jahre Lieferung zu (ab 2023).
   *Haken:* pypilot hat keinen Treiber für den MMC5983MA; er muss geschrieben werden.
2. **Adafruit 4569** (ISM330DHCX + LIS3MDL). Gleicher Kreisel; die neuere RTIMULib2 erkennt ihn ohne Programmierarbeit.
   *Haken:* LIS3MDL abgekündigt; Lager nur bei DigiKey. Als Übergang, mit Reserve kaufen.
3. **Adafruit 4502 + SparkFun 19921** (dieselben Chips wie Platz 1, getrennte Platinen). Das Magnetometer kann weiter
   weg von Pi, Kabeln und Eisen sitzen. *Haken:* Treiber wie Platz 1, dazu Kabel und Ausrichtung zueinander.
   Beide Platinen müssen fest und parallel sitzen, sonst braucht der Treiber ihre Drehung zueinander als festen Wert.
4. **Adafruit 4554** (ICM-20948). Mit diesem Sensor hat der Entwickler die meiste Erfahrung, gut lieferbar.
   *Haken:* Chip abgekündigt; Kreisel laut Entwickler und Forum schwächer (Datenblattwerte nicht geprüft).
5. **MPU9250 behalten.** Kein Aufwand. *Haken:* seit Jahren abgekündigt, Herkunft heutiger Module unsicher, am schwächsten.

**Für alle gilt:** pypilot 0.24 stammt vom 14.03.2020. Die Treiber für ICM-20948 (10/2020) und ISM330DHCX (12/2020)
kamen später. Die Sensorbibliothek muss also wahrscheinlich aktualisiert werden. Die Kugel-Kalibrierung (1.6) reicht
für kein Magnetometer; der MMC5983MA hat laut Datenblatt bis ±5 % Empfindlichkeitsfehler und bis ±3° Achsfehler.

## 3. Werte aus den Datenblättern
- **ISM330DHCX** (ST DS13012 Rev 7): Rauschen 5 mdps/√Hz; Nullpunkt-Wandern ±0,005 °/s je °C (höchstens 0,015);
  Bias-Instabilität 3 °/h; −40 bis +105 °C; 1,71–3,6 V.
- **MMC5983MA** (MEMSIC Rev. A): ±8 G; Rauschen 0,4 mG (50 Hz) bzw. 0,6 mG (100 Hz); SET/RESET (Umpolung gegen
  Restmagnetisierung), damit Nullpunkt über Temperatur ±3 mG; Kurs ±1,0° typisch; −40 bis +105 °C; 2,8–3,6 V.

## 4. Händler (geprüft 01.11.2026)
| Modul | DigiKey | Mouser |
|---|---|---|
| SparkFun SEN-19895 | 392 Stk., 40,60 € netto | 246 Stk., 39,34 € |
| Adafruit 4569 | 47 Stk., 26,19 € | 0 Stk. (28 bestellt), 25,37 € |
| Adafruit 4554 | 672 Stk., 17,71 € | 898 Stk., 17,16 € |

Links: DigiKey-Suche `digikey.de/de/products/result?keywords=<Nr.>`, Mouser-Suche `mouser.de/c/?q=<Nr.>`.
Eckstein führt SEN-19895 (54,43 € mit MwSt.), Lager unklar, etwa 4 Wochen. BerryBase und Reichelt: nichts Passendes.

## 5. Verworfen
- BNO055 und BNO085: berechnen Lage und Kalibrierung selbst; pypilot braucht Rohwerte und macht beides selbst.
- Sensoren an USB oder seriell (z. B. WT901C): laut Entwickler nicht unterstützt (Verzögerung, Zuverlässigkeit).
- RM3100: rauscht weniger, aber kein Treiber und teurer; pypilot kann den Vorteil nicht nutzen.

## 6. JLCPCB-Bestückung (eigene Platine)
Beide Chips sitzen in LGA-Gehäusen ohne Beinchen (2,5–3 mm), also nur durch JLCPCB bestückbar. Dafür braucht es die
Freigabe des Betreibers für SMD und für jedes Extended-Teil (`0-gesamtprojekt/fertigung/jlcpcb-bestueckungsregeln.md`).

| Chip | JLCPCB-Nr. | Kategorie | Lager 01.11.2026 |
|---|---|---|---|
| ISM330DHCX | C2655101 | Extended | 4531 (4,99 €) |
| MMC5983MA | C404329 | Extended | 7543 (1,78 €) |
| ICM-20948 / MPU-6050 / QMC5883L (ältere) | C726001 / C24112 / C976032 | Extended | 1991 / 6592 / nicht erfasst |

Unter Basic und Promotional Extended (ohne Ladegebühr) fand sich kein Sensor; der Kategorie-Filter dieser Liste zeigt
keine Sensoren (nicht restlos geklärt). Ladegebühr laut Bestückungsregeln: Economic 3,07 $ je Extended-Sorte.
Ob die LGA-Gehäuse Röntgen brauchen (wie QFN), ist zu prüfen.
- **Empfehlung:** ISM330DHCX + MMC5983MA; ältere Chips sparen keine Gebühr und sind schlechter oder abgekündigt.
  Am sinnvollsten auf der Hauptplatine der Phase-3-Bedieneinheit; bis dahin Modul SEN-19895 (dieselben Chips).
- **Schaltplan:** SEN-19895 ist Open-Source-Hardware, Schaltplan bei SparkFun und DigiKey; dazu die Anschlussbeispiele der
  Datenblätter. Layout: Spulen, Stahl und Stromleiterbahnen fern vom Magnetometer; Chips nicht an Schrauben oder Kanten.
- **Treiber:** Kreisel-Teil aus RTIMULib2 (`RTIMULSM6DS33LIS3MDL`, kennt den ISM330DHCX). Magnetometer nach ArduPilot
  `libraries/AP_Compass/AP_Compass_MMC5xx3.cpp` (C++, GPL v3 wie pypilot, mit SET/RESET). Zum Ausprobieren: SparkFun
  `qwiic_mmc5983ma_py` (Python, Pi), SparkFun-Arduino-Bibliothek (ESP32), ST `STMems_Standard_C_drivers`.

## 7. Offen
- Welche RTIMULib-Version läuft auf dem TinyPilot? (SSH, unter 5 min)
- Aufwand für einen MMC5983MA-Treiber in RTIMULib2 schätzen (Vorlage ArduPilot, Abschnitt 6).
- Kompass-Kalibrierung auf Ellipsoid erweitern.
- Platz 3: zwei Händler je Modul prüfen. SEN-19895: Pull-up-Widerstände auf der Platine prüfen.

## 8. Quellen
- Sensorerkennung: github.com/pypilot/RTIMULib2, `RTIMULib/RTIMUSettings.cpp`, Liste der Änderungen.
- Entwickler-Aussagen: forum.openmarine.net, Themen 4344 (12/2022) und pid 19923 (2021).
- Datenblätter: ST DS13012 Rev 7 (ISM330DHCX), MEMSIC MMC5983MA Rev. A; Lebenszyklus: st.com, digikey.com.
