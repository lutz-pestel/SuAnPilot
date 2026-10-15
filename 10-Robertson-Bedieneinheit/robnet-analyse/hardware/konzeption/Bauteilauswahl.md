# Bauteilauswahl Robnet-Analyse

Version 00.09, Stand 15.10.2026, Obergrenze 200 Zeilen. Grundlage: `robnet-analyse.md` (Konzept 00.25),
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
  über alle Jumper. Gleichwertig: Binder MPE 149-1-002 (vergoldet, 3 A, oben offen; Abschnitt 8).
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
- **U1 MAX3488EEPA** (DIP-8, im Sockel; MC Abschnitt 6), nur Empfänger, Sendeausgänge offen. **Auslaufteil:** Mouser
  verkauft nur noch den Restbestand; eine Reserve mitbestellen (Abschnitt 8). R1/R2 1 kΩ in Reihe
  (Konzept), JP1 und JP2 siehe Abschnitt 1.
- **U2, U6 MCP3208-CI/P** (DIP-16, je im Sockel; MC Abschnitt 3), Hardware-SPI, U2 an CE0, U6 an CE1.
- **U4 Referenz LM4040AIZ-2.5/NOPB** (TO-92, ±0,1 %; MC Abschnitt 3), eine für beide Wandler.
  Vorwiderstand von 3,3 V: R4 1 kΩ (≈ 0,8 mA, gerechnet).
- **Teiler:** Vishay MBB0207, 1 %, 0,6 W (Bereich 0,22 Ω–22 MΩ; ±1 % ab 10 Ω): 100 kΩ (12 Stück), 18 kΩ (9),
  8,2 kΩ (2, Vsys+ beidseitig), 180 kΩ (1, Alarm an den Zero), 1 kΩ (2, R1/R2).
- **Klemmdioden BAT85** (MC Abschnitt 3): zwei je Wandlerkanal mit Teiler (11 Kanäle) und eine am Alarm-Teiler: 23 Stück.
- **Abblockkondensatoren 100 nF** KEMET C320C104K5R5TA (MC Abschnitt 9): U1, U2, U6 (3 Stück).

## 4. Versorgung — wie MC Abschnitt 7
Bordnetz 12 V am J300 → **Sicherung 1 A träge**, 5 × 20 mm, im Halter Schurter OGN 0031.8201 (MC: 2 A; hier weniger
Last: Zero, WLAN-Stick oder LAN-Adapter, zusammen unter 1 A bei 5 V, geschätzt) → **Verpolschutz SB540-E3/54** →
**Schutzdiode 1.5KE20A** → Filter wie MC (4,7 µF ×2, Drossel Bourns RLB0914-100KL, 4,7 µF; KEMET C320C475K5R5TA ist
nicht am Lager, gleichwertig TDK FG16X7R1H475KRT06, 50 V, X7R; laut TDK-Katalog FG 11/2024 Körper 5,5 × 3,5 mm,
Höhe 6,0 mm, Raster 2,5 mm, Draht 0,5 mm, Endung RT06 = gegurtet, Maße wie lose; Bohrung 0,8 mm) →
**Regler Recom R-78B5.0-2.0** (6,5–32 V) → 5 V an Zero Pin 2/4. Rote Leuchtdiode 3 mm mit 4,7 kΩ parallel zur Sicherung.
3,3 V für U1, U2, U4, U6 vom Zero (zusammen wenige mA).

## 5. Rechner und Netz
- **Raspberry Pi Zero 2 W**; mit vorgelöteter Stiftleiste als „Zero 2 WH" (Lieferbarkeit schwankt, im Januar 2026
  bei einem Händler begrenzt). Sonst Zero 2 W und Stiftleiste 2 × 20 selbst einlöten. Speicherkarte microSD 32 GB
  für Dauerschreiben (Ausführung „High Endurance" oder Industrie).
- **Weg 1, WLAN-Stick am 5-m-Kabel:** Stick mit Chip **MediaTek MT7601** (Treiber `mt7601u`, seit Linux 4.2 im Kern)
  oder **Ralink RT5370** (Treiber `rt2800usb`). Vor dem Einsatz prüfen: `lsusb` zeigt `148f:7601` bzw. `148f:5370`;
  meldet `dmesg` einen Fehler der Firmware, das Paket `linux-firmware` nachinstallieren. Kabel: **USB-2.0-Verlängerung 5 m** (A-Stecker/A-Buchse) und
  **OTG-Adapter** micro-B-Stecker auf A-Buchse. 5 m ist die Grenze von USB 2.0; geht das passive Kabel nicht,
  eine aktive 5-m-Verlängerung.
- **Weg 2, LAN-Adapter:** USB-A-Adapter mit **Realtek RTL8152** (Treiber `r8152` im Linux-Kern) am OTG-Adapter, in
  Deutschland ab Lager. Plugable USB2-OTGE100 (micro-B direkt, ASIX AX88772A) gibt es hier nur aus den USA. Ein Netzwerk-Hub zieht laut Adafruit etwa 280 mA:
  der Regler (2 A) hat Reserve.

## 6. Gehäuse und Einbau — Vorschlag wie MC Abschnitt 9
3D-Druck ASA, nur mechanischer Schutz. Jumper JP1–JP7 und J4 unter einem Deckel zugänglich; USB-Buchse des
Zero zugänglich, Kabel mit Zugentlastung; Steckverbinder J1, J2, J3 an einer Kante. Einbauort nahe J300.

## 7. Offen — vor der Bestellung zu prüfen
- Lager und Preise neu prüfen (Stand der Tabelle: 15.10.2026).
- MAX3488EEPA: Restbestand bei Mouser und DigiKey; Reserve mitbestellen, Ersatz gegebenenfalls neu suchen.
- Steuerleitung und WLAN-Stick: nur ein Händler geprüft (Abschnitt 8); zweite Quelle vor der Bestellung.
- Raspberry Pi Zero 2 W: am 15.10.2026 bei Reichelt und BerryBase nicht lieferbar (Beschaffung ohnehin später).

## 8. Bezugsquellen (gesucht 15.10.2026; Preise mit MwSt., ohne Versand)
Regel: Jedes Teil braucht zwei unabhängige Händler. Mouser- und DigiKey-Links führen zur Suche nach der Teilenummer.

| Teil | Menge | Händler 1 | Händler 2 |
|---|---|---|---|
| MAX3488EEPA (U1) | 1 + 1 | [Mouser 700-MAX3488EEPA](https://www.mouser.de/c/?q=MAX3488EEPA): 12,90 €, 99 Stück, **Restbestand** | [DigiKey MAX3488EEPA+-ND](https://www.digikey.de/de/products/result?keywords=MAX3488EEPA%2B): 13,17 €, 45 Stück |
| MCP3208-CI/P (U2, U6) | 2 | [Reichelt MCP 3208-CI/P](https://www.reichelt.de/de/de/shop/produkt/12-bit_serieller_a_d-wandler_8-kanal_2_7v_spi_dip-16-90079): 3,05 € | [Mouser 579-MCP3208CIP](https://www.mouser.de/c/?q=MCP3208-CI%2FP): 2,39 €, 2 544 Stück |
| LM4040AIZ-2.5/NOPB (U4) | 1 | [DigiKey LM4040AIZ-2.5/NOPB-ND](https://www.digikey.de/de/products/result?keywords=LM4040AIZ-2.5%2FNOPB): 2,49 €, 663 Stück | [Mouser 926-LM4040AIZ25NOPB](https://www.mouser.de/c/?q=LM4040AIZ-2.5%2FNOPB): 2,11 €, 43 Stück |
| Widerstände 0207, 1 % | 28 | [Mouser Vishay MBB0207](https://www.mouser.de/c/?q=MBB02070C1003FCT00): je um 0,21 €, auf Lager: MBB02070C1003FCT00 (100 kΩ), …1802… (18 kΩ), …8201… (8,2 kΩ), …1803… (180 kΩ), …1001… (1 kΩ, 3 Stück), …4701… (4,7 kΩ) | [Reichelt METALL 100K](https://www.reichelt.de/de/de/shop/produkt/widerstand_metallschicht_100_kohm_0207_0_6_w_1_-11458) usw. (0207, 0,6 W, 1 %): 0,09 € |
| BAT85 | 23 | [Reichelt BAT 85](https://www.reichelt.de/de/de/shop/produkt/schottkydiode_30_v_0_2_a_do-35-4857): 0,08 € | [Mouser 78-BAT85S-TAP](https://www.mouser.de/c/?q=BAT85-TAP): 0,43 €, 42 572 Stück |
| 100 nF KEMET C320C104K5R5TA | 3 | [Mouser 80-C320C104K5R5TA](https://www.mouser.de/c/?q=C320C104K5R5TA): 0,79 €, 87 429 Stück | [DigiKey C320C104K5R5TA](https://www.digikey.de/de/products/result?keywords=C320C104K5R5TA): 1,31 € |
| 4,7 µF 50 V X7R, TDK FG16X7R1H475KRT06 | 3 | [Mouser 810-FG16X7R1H475KRT6](https://www.mouser.de/c/?q=X7R1H475KRT06): 0,83 €, 1 970 Stück | [DigiKey 445-173161-1-ND](https://www.digikey.de/de/products/result?keywords=FG16X7R1H475KRT06): 0,89 €, 5 691 Stück |
| Drossel Bourns RLB0914-100KL | 1 | [Mouser 652-RLB0914-100KL](https://www.mouser.de/c/?q=RLB0914-100KL): 0,33 €, 1 272 Stück | [DigiKey RLB0914-100KL-ND](https://www.digikey.de/de/products/result?keywords=RLB0914-100KL): 0,36 €, 966 Stück |
| Regler Recom R-78B5.0-2.0 | 1 | [Reichelt R-78B50-20](https://www.reichelt.de/de/de/shop/produkt/dc_dc-wandler_r-78_6_5-32_vin_single_5_vout_2000_ma_sip3-422370): 12,95 € | [Mouser 919-R-78B5.0-2.0](https://www.mouser.de/c/?q=R-78B5.0-2.0): 11,98 €, 8 338 Stück |
| Schottky-Diode Vishay SB540-E3/54 | 1 | [Mouser 625-SB540-E3](https://www.mouser.de/c/?q=SB540-E3%2F54): 0,96 €, 955 Stück | [Reichelt SB 540 DIO](https://www.reichelt.de/de/de/shop/produkt/schottkydiode_40_v_5_a_do-201-216766) (gleiche Daten, Hersteller Diotec): 0,30 € |
| Schutzdiode 1.5KE20A | 1 | [Reichelt 1,5KE20A](https://www.reichelt.de/de/de/shop/produkt/tvs-diode_unidirektional_17_1_v_1500_w_do-201-272804): 0,37 € | [Mouser 576-1.5KE20A](https://www.mouser.de/c/?q=1.5KE20A) (Littelfuse): 0,91 €, 5 818 Stück |
| Sicherung 1 A träge, 5 × 20 | 1 + 1 | [Reichelt Schurter 0034.3117](https://www.reichelt.de/de/de/shop/produkt/feinsicherung_5x20mm_traege_t_1a-440465): 0,27 €, 3–5 Werktage | [Mouser 576-0215001.MXP](https://www.mouser.de/c/?q=0215001.MXP) (Littelfuse): 2,02 €, 5 575 Stück |
| Sicherungshalter Schurter OGN 0031.8201 | 1 | [Mouser 693-0031.8201](https://www.mouser.de/c/?q=0031.8201): 1,03 €, 27 553 Stück | [DigiKey 0031.8201](https://www.digikey.de/de/products/result?keywords=0031.8201): 1,19 € |
| Leuchtdiode rot 3 mm | 1 | [Reichelt 3004R1C-DSA-B](https://www.reichelt.de/de/de/shop/produkt/led_3mm_bedrahtet_rot_1000_mcd_40_-361560): 0,05 € | [DigiKey Kingbright WP710A10ID](https://www.digikey.de/de/products/result?keywords=WP710A10ID): 0,21 € |
| Phoenix MSTBA 2,5/6-G-5,08 (J1, J3) | 2 | [Reichelt MSTBA 6-G 5,08](https://www.reichelt.de/de/de/shop/produkt/leiterplatten-grundleiste_6-polig_rm_5_08_mm-361707): 1,50 € | [Mouser 651-1757284](https://www.mouser.de/c/?q=1757284): 1,51 € |
| Phoenix MSTB 2,5/6-ST-5,08 (Kabel) | 2 | [Reichelt MSTB 6-ST 5,08](https://www.reichelt.de/de/de/shop/produkt/leiterplattenstecker_6-polig_rm_5_08_mm-361692): 3,99 € | [Mouser 651-1757051](https://www.mouser.de/c/?q=1757051): 4,64 €, 4 247 Stück |
| Phoenix MSTBA 2,5/2-G-5,08 (J2) | 1 | [Reichelt MSTBA 2-G 5,08](https://www.reichelt.de/de/de/shop/produkt/leiterplatten-grundleiste_2-polig_rm_5_08_mm-361704): 0,60 € | [Mouser 651-1757242](https://www.mouser.de/c/?q=1757242): 0,48 €, 23 646 Stück |
| Phoenix MSTB 2,5/2-ST-5,08 (J2) | 1 | [Reichelt MSTB 2-ST 5,08](https://www.reichelt.de/de/de/shop/produkt/leiterplattenstecker_2-polig_rm_5_08_mm-361689): 1,40 € | [Mouser 651-1757019](https://www.mouser.de/c/?q=1757019): 1,56 €, 29 858 Stück |
| Stiftleiste 1 × 40, vergoldet (JP3–JP7, J4) | 1 | [Reichelt BKL 10120183](https://www.reichelt.de/de/de/shop/produkt/stiftleiste_40_polig_vergoldet_2_54_mm-235641): 0,85 €; auf Länge abbrechen | [Mouser Würth 710-61304011121](https://www.mouser.de/c/?q=61304011121): 1,32 €, 20 300 Stück |
| Stiftleiste 2 × 20/36, vergoldet (JP1, JP2) | 1 | [Reichelt BKL 10120172](https://www.reichelt.de/de/de/shop/produkt/stiftleiste_2x36-polig_vergoldet_2_54-235638) (2 × 36): 1,10 € | [Mouser Würth 710-61304021121](https://www.mouser.de/c/?q=61304021121) (2 × 20): 1,73 €, 4 730 Stück |
| Jumper vergoldet, 3 A | 9 | [Mouser Harwin 855-M7566-05](https://www.mouser.de/c/?q=M7566-05): 0,40 €, 8 174 Stück | [Reichelt Binder MPE 149-1-002-F0](https://www.reichelt.de/de/de/shop/produkt/jumper_2_54_mm_geoeffnet_schwarz-119941): 0,05 € |
| Buchsenleiste 2 × 20, 2,54 mm (Zero) | 1 | [Reichelt BKL 10120963](https://www.reichelt.de/de/de/shop/produkt/buchsenleiste_2_54mm_2x20_gerade-266688) (vergoldet): 1,87 € | [Mouser Samtec 200-SSW12001GD](https://www.mouser.de/c/?q=SSW-120-01-G-D): 5,44 €, 3 904 Stück |
| IC-Sockel DIP-8 | 1 | [Reichelt GS 8P](https://www.reichelt.de/de/de/shop/produkt/ic-sockel_8-polig_superflach_gedreht-8231): 0,20 € | [Mouser Mill-Max 575-11043308](https://www.mouser.de/c/?q=110-43-308-41-001000): 1,62 €, 16 659 Stück |
| IC-Sockel DIP-16 | 2 | [Reichelt GS 16P](https://www.reichelt.de/de/de/shop/produkt/ic-sockel_16-polig_superflach_gedreht_vergold_-8209): 0,25 € | [Mouser Mill-Max 575-110433161](https://www.mouser.de/c/?q=110-43-316-41-001000): 2,95 €, 14 791 Stück |
| Steuerleitung 6 × 0,5 mm² | 5 m | [Reichelt PUR 6X0,50 5](https://www.reichelt.de/de/de/shop/produkt/steuerleitung_li12y11y_6_x_0_5_mm_5_m_schwarz-154233) (Li12Y11Y, ölbeständig): 22,10 € | **nicht gefunden** (Mouser/DigiKey führen sie nicht am Lager; Conrad ließ sich nicht abfragen); gängige Ware im Elektrogroßhandel |
| Raspberry Pi Zero 2 W / 2 WH | 1 | [Reichelt Zero 2 WH](https://www.reichelt.de/de/de/shop/produkt/raspberry_pi_zero_2_wh_4x_1_ghz_512_mb_ram_wlan_bt-383360): 22,10 €, ab 22.12.2026 | [BerryBase Zero 2 W](https://www.berrybase.de/raspberry-pi-zero-2-w): 18,90 €; [Zero 2 WH](https://www.berrybase.de/en/raspberry-pi-zero-2-wh): 20,90 €; derzeit nicht lieferbar |
| microSD 32 GB High Endurance | 1 | [Reichelt SanDisk SDSQQNR-032G](https://www.reichelt.de/de/de/shop/produkt/microsdhc-speicherkarte_32gb_sandisk_high_endurance-298156): 25,95 € | [BerryBase SanDisk High Endurance 32 GB](https://www.berrybase.de/sandisk-high-endurance-microsdhc-uhs-i-u3-speicherkarte-adapter-32gb): 28,60 €, 20 Stück |
| WLAN-Stick MT7601 (Weg 1) | 1 | [Reichelt ALLNET ALLWA0150](https://www.reichelt.de/de/de/shop/produkt/wlan-adapter_usb_150_mbit_s-149756): 6,95 € | **nicht gefunden** (BerryBase führt keine Sticks, Eckstein ließ sich nicht abfragen); RT5370-Sticks nur über eBay.de aus China |
| USB-2.0-Verlängerung 5 m | 1 | [Reichelt Goobay 68916](https://www.reichelt.de/de/de/shop/produkt/usb_2_0_verlaengerungskabel_mit_usb_zertifikat_5_m-249979) (passiv): 4,00 €; aktiv [Delock 82308](https://www.reichelt.de/de/de/shop/produkt/aktives_usb_2_0_verlaengerungskabel_5_m-416748): 10,09 € | [BerryBase aktive Verlängerung 5 m](https://www.berrybase.de/aktive-usb-2.0-verlaengerung-repeater-5m): 8,40 €, 6 Stück |
| OTG-Adapter micro-B auf A | 1 | [Reichelt LogiLink AA0035](https://www.reichelt.de/de/de/shop/produkt/usb_2_0_adapter_micro-b_stecker_a-buchse_otg_schwarz-314909): 2,50 € | [BerryBase OTG-Adapterkabel 0,15 m](https://www.berrybase.de/usb-2.0-hi-speed-otg-adapterkabel-a-buchse-micro-b-stecker-0-15m-weiss): 1,80 €, 100+ Stück |
| LAN-Adapter RTL8152 (Weg 2) | 1 | [Reichelt LogiLink UA0144](https://www.reichelt.de/index.html?ACTION=446&SEARCH=UA0144): 9,90 €, mit OTG-Adapter | Plugable USB2-OTGE100 (ASIX): [eBay.de](https://www.ebay.de/itm/336009260018), etwa 27 € + 10 € Versand aus den USA |

**Nur eine geprüfte Quelle:** Steuerleitung und WLAN-Stick (beides Massenware ohne besondere Anforderung; vor der Bestellung
einen zweiten Händler suchen oder einen anderen Typ wählen). **MAX3488:** zwei Händler, aber Restbestände; Reserve mitbestellen.
Farnell, Bürklin, TME, Conrad und Eckstein ließen sich am 15.10.2026 weder direkt noch über den Browser abfragen.

## Quellen
- MBB0207 Bereich: <https://uk.farnell.com/vishay/mbb02070c1502fc100/res-15k-1-600mw-axial-thin-film/dp/2614381>
- Harwin M7566-05: <https://www.digikey.kr/en/products/detail/harwin-inc/M7566-05/3728166>
- Phoenix 1757284: <https://pl.farnell.com/en-PL/phoenix-contact/1757284/header-right-angle-5-08mm-6way/dp/3705213>;
  1757051: <https://automa.net/de/produkt/phoenix-contact/1757051-63a379daca04b4f2592b0d7a>
- RT5370 unter Linux: <https://thepihut.com/blogs/raspberry-pi-tutorials/how-to-set-up-the-ralink-rt5370-wifi-dongle-on-raspian>,
  <https://forum.openwrt.org/t/rpi-3-mediatek-rt5370-usb-wifi-adapter/137643>
- Plugable USB2-OTGE100: <https://www.plugable.com/products/usb2-otge100>; Strombedarf Ethernet: <https://www.adafruit.com/products/2909>
- Zero 2 WH: <https://www.switch-science.com/products/9812>
- mt7601u im Linux-Kern ab 4.2: <https://forum.libreelec.tv/thread/23210-installing-a-driver-for-a-mt7601u-wireless-adapter/>
