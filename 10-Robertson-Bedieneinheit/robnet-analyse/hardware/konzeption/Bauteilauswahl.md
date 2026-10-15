# Bauteilauswahl Robnet-Analyse

Version 00.04, Stand 15.10.2026, Obergrenze 200 Zeilen. Grundlage: `robnet-analyse.md` (Konzept 00.18),
`Blockschaltbild_Robnet-Analyse.html` (00.15). Stückliste: `hardware/bom/bom.csv`.
Teile wie im Motor-Controller, wo möglich: dort begründet, hier nur verwiesen
(`2-motor-controller/hardware/konzeption/Bauteilauswahl.md`, kurz „MC"). Preise und Lager vom 15.10.2026, nur zur
Größenordnung; vor der Bestellung neu prüfen. Verworfene Wege stehen in je einem Satz.

## 0. Vorgaben, an denen jede Wahl gemessen wird
- **Nur Durchsteckteile (THT), selbst gelötet** (Linie A wie im MC; Betreiber, 15.10.2026).
- **Einfach halten:** Die Richtung jeder Ader wird durch Trennen per Jumper bestimmt, nicht dauernd gemessen (Konzept,
  Block 8). Keine Shunts, keine Messverstärker.
- **Den Robertson nicht belasten:** Alles, was an einer Robnet-Ader hängt, zieht so wenig Strom wie möglich.
- **Die fertige Platine wird nicht geändert.** Motorraum: warm, Vibration; Bauteile möglichst −40…+85 °C.

## 1. Jumper JP1–JP7
- **JP3–JP7** (Bus+, Bus−, Vsys+, On-Off, Alarm): je eine **Stiftleiste 1 × 2, 2,54 mm, vergoldet**, mit Jumper
  gesteckt = 1:1, gezogen = getrennt.
- **JP1** (A/B des Empfängers gerade oder gekreuzt) und **JP2** (Empfänger an der Seite J300 oder Bedieneinheit): je eine
  Stiftleiste 2 × 3, 2,54 mm, mit zwei Jumpern.
- **Jumper Harwin M7566-05** (vergoldet, 3 A, 250 V, oben offen, damit man mit einer Messspitze ankommt; Farnell 150411),
  9 Stück. 3 A reichen für Vsys+ (Verbrauch der Bedieneinheit). Gegen Lösen durch Vibration: ein Streifen Kapton-Band
  über alle Jumper.
- *Verworfen:* DIP-Schalter (nur für Signalstrom); Lötbrücken (Umstecken nur mit Lötkolben); Relais (Konzept, Abschnitt 4).

## 2. Steckverbinder
- **J3 (Bedieneinheit) und J1 (Kabel zum J300): Phoenix MSTBA 2,5/6-G-5,08**, Bestellnummer 1757284 (Stiftleiste
  liegend, 12 A; lieferbar laut Betreiber, 15.10.2026; Farnell 3705213). Der Stecker der Bedieneinheit passt direkt in J3.
- **Kabel J1 → J300:** an beiden Enden **MSTB 2,5/6-ST-5,08**, Bestellnummer 1757051 (2 Stück), dazwischen
  6 × 0,5 mm² Steuerleitung (LiYY); Länge nach dem Einbauort.
- **J2 Versorgung:** MSTBA 2,5/2-G-5,08 (1757242) mit Stecker MSTB 2,5/2-ST-5,08 (1757019), wie im MC.
- **J4 Messpunkte:** Stiftleiste 1 × 3, 2,54 mm (Bus+, Bus−, Masse) für Oszilloskop oder Logikanalysator.
- **Zero:** Buchsenleiste 2 × 20, 2,54 mm, auf unserer Platine; der Zero steckt mit seiner Stiftleiste darauf.

## 3. Empfänger, Wandler, Referenz — wie MC
- **U1 MAX3488EEPA** (DIP-8, im Sockel; MC Abschnitt 6), nur Empfänger, Sendeausgänge offen. R1/R2 1 kΩ in Reihe
  (Konzept), JP1 und JP2 siehe Abschnitt 1.
- **U2, U6 MCP3208-CI/P** (DIP-16, je im Sockel; MC Abschnitt 3), Hardware-SPI, U2 an CE0, U6 an CE1.
- **U4 Referenz LM4040AIZ-2.5/NOPB** (TO-92, ±0,1 %; MC Abschnitt 3), eine für beide Wandler.
  Vorwiderstand von 3,3 V etwa 1 kΩ (≈ 0,8 mA, gerechnet; Wert im Schaltplan).
- **Teiler:** Vishay MBB0207, 1 %, 0,6 W (Bereich 0,22 Ω–22 MΩ; ±1 % ab 10 Ω): 100 kΩ (12 Stück), 18 kΩ (9),
  8,2 kΩ (2, Vsys+ beidseitig), 180 kΩ (1, Alarm an den Zero), 1 kΩ (2, R1/R2).
- **Klemmdioden BAT85** (MC Abschnitt 3): zwei je Wandlerkanal mit Teiler (11 Kanäle) und eine am Alarm-Teiler: 23 Stück.
- **Abblockkondensatoren 100 nF** KEMET C320C104K5R5TA (MC Abschnitt 9): U1, U2, U6 (3 Stück).

## 4. Versorgung — wie MC Abschnitt 7
Bordnetz 12 V am J300 → **Sicherung 1 A träge**, 5 × 20 mm, im Halter Schurter OGN 0031.8201 (MC: 2 A; hier weniger
Last: Zero, WLAN-Stick oder LAN-Adapter, zusammen unter 1 A bei 5 V, geschätzt) → **Verpolschutz SB540-E3/54** →
**Schutzdiode 1.5KE20A** → Filter wie MC (4,7 µF C320C475K5R5TA ×2, Drossel Bourns RLB0914-100KL, 4,7 µF) →
**Regler Recom R-78B5.0-2.0** (6,5–32 V) → 5 V an Zero Pin 2/4. Rote Leuchtdiode 3 mm mit 4,7 kΩ parallel zur Sicherung.
3,3 V für U1, U2, U4, U6 vom Zero (zusammen wenige mA).

## 5. Rechner und Netz
- **Raspberry Pi Zero 2 W**; mit vorgelöteter Stiftleiste als „Zero 2 WH" (Lieferbarkeit schwankt, im Januar 2026
  bei einem Händler begrenzt). Sonst Zero 2 W und Stiftleiste 2 × 20 selbst einlöten. Speicherkarte microSD 32 GB
  für Dauerschreiben (Ausführung „High Endurance" oder Industrie).
- **Weg 1, WLAN-Stick am 5-m-Kabel:** Stick mit Chip **Ralink RT5370** und Antenne; der Treiber `rt2800usb` ist im
  Linux-Kern. Vor dem Einsatz prüfen: `lsusb` muss `148f:5370` zeigen; gleich aussehende Sticks mit MT7601
  (`148f:7601`) brauchen einen anderen Treiber. Kabel: **USB-2.0-Verlängerung 5 m** (A-Stecker/A-Buchse) und
  **OTG-Adapter** micro-B-Stecker auf A-Buchse. 5 m ist die Grenze von USB 2.0; geht das passive Kabel nicht,
  eine aktive 5-m-Verlängerung.
- **Weg 2, LAN-Adapter: Plugable USB2-OTGE100** (micro-B direkt am Zero, ohne OTG-Adapter, Chip ASIX AX88772A,
  10/100 Mbit/s, für den Zero beworben; 21,95 $ beim Hersteller). Ein Netzwerk-Hub zieht laut Adafruit etwa 280 mA:
  der Regler (2 A) hat Reserve.

## 6. Gehäuse und Einbau — Vorschlag wie MC Abschnitt 9
3D-Druck ASA, nur mechanischer Schutz. Jumper JP1–JP7 und J4 unter einem Deckel zugänglich; USB-Buchse des
Zero zugänglich, Kabel mit Zugentlastung; Steckverbinder J1, J2, J3 an einer Kante. Einbauort nahe J300.

## 7. Offen — vor der Bestellung zu prüfen
- Lager und Preise neu prüfen.
- Bezugsquellen für die Teile, die in der Stückliste „nicht geprüft" heißen (Stift- und Buchsenleisten, Widerstände).

## Quellen
- MBB0207 Bereich: <https://uk.farnell.com/vishay/mbb02070c1502fc100/res-15k-1-600mw-axial-thin-film/dp/2614381>
- Harwin M7566-05: <https://www.digikey.kr/en/products/detail/harwin-inc/M7566-05/3728166>
- Phoenix 1757284: <https://pl.farnell.com/en-PL/phoenix-contact/1757284/header-right-angle-5-08mm-6way/dp/3705213>;
  1757051: <https://automa.net/de/produkt/phoenix-contact/1757051-63a379daca04b4f2592b0d7a>
- RT5370 unter Linux: <https://thepihut.com/blogs/raspberry-pi-tutorials/how-to-set-up-the-ralink-rt5370-wifi-dongle-on-raspian>,
  <https://forum.openwrt.org/t/rpi-3-mediatek-rt5370-usb-wifi-adapter/137643>
- Plugable USB2-OTGE100: <https://www.plugable.com/products/usb2-otge100>; Strombedarf Ethernet: <https://www.adafruit.com/products/2909>
- Zero 2 WH: <https://www.switch-science.com/products/9812>
