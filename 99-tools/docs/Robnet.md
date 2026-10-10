# Robnet (Datennetz des Robertson AP300X)

Version 00.05, Stand 10.10.2026, Obergrenze 60 Zeilen.
Zweck: Was über das Robnet bekannt ist, was nicht, und was nur vermutet wird.

## 1. Belegt (Handbuch AP300X `handbuecher/Robertson/Control-Unit/AP300CX_Manual.pdf`, Abschnitte 1.1, 3.x; AP11-Handbuch)
- Robnet verbindet alle Geräte und verteilt zugleich die Versorgung. Bis zu 7 Bedieneinheiten pro System.
- Der Steuerrechner sitzt in der Verteilereinheit J300 im Motorraum, nicht in der Bedieneinheit am Steuerstand.
  Die Bedieneinheit ist nur am Robnet angeschlossen; Ruderlagengeber RF300 und Kompass melden an den J300.
- Stecker 6-polig, Crimp-Stecker, IP67. Es gibt keine festen Ein- und Ausgänge: Jedes Gerät hat 2–3 gleiche Buchsen,
  jede ist als Abzweig nutzbar. Unbenutzte Buchsen bekommen eine Kappe.
- Kabel 7 m, 15 m (am J300 nur am Bedieneinheit-Ende ein Stecker), Verlängerung 10 m. Gesamtlänge höchstens 50 m.
- Drei verdrillte Aderpaare (Ansicht von der Kabelseite):

| Pin | Ader | Signal | Paar |
|---|---|---|---|
| 1 | braun | Bus− | Daten |
| 2 | weiß | Bus+ | Daten |
| 3 | gelb | On-Off | Ein/Aus |
| 4 | grau | V System− | Versorgung |
| 5 | rosa | V System+ | Versorgung |
| 6 | grün | Alarm | Ein/Aus |

- Fehlerhilfe im Handbuch: „Comm. failure“ (Bedieneinheit still) → Robnet-Kabel prüfen oder reparieren.
- NMEA 0183 hat am J300 eigene Anschlüsse (4800 Baud, eigene LEDs), getrennt vom Robnet.

## 2. Messwerte 10.10.2026 (Betreiber, J300-Klemmleiste, Zustand des Robertson nicht notiert)
Reihenfolge auf der Klemmleiste von links: Bus−, Bus+, Vsys+, Vsys−, On-Off, Alarm. Digitalvoltmeter gegen Masse der
Robertson-Versorgung: Bus− 0,7 V · Bus+ 4,4 V · Vsys+ 26,4 V · Vsys− 0,004 V · On-Off 13,5 V · Alarm 0,4 V (im Alarm 4,8 V); Bus+ gegen Bus− 3,7 V.
Oszilloskop am Bus: Pakete aus unregelmäßigen Pulsen mit Pausen, ähnlich der NMEA-Ausgabe der RF300-Interfaceplatine.
Offen: Datenrate (kürzester Puls), Hub beim Springen, Gegenlauf Bus+/Bus−, Paketabstand, On-Off beim Ausschalten.
Protokoll und Datenrate nennen weder die Handbücher (AP300X, AP11, AP21/22, AP3000X) noch zwei Internet-Suchen.

## 3. Hypothesen (alle unbestätigt, aus Allgemeinwissen, nicht aus Dokumenten)
- **H1** „Bus+/Bus−“ ist ein Differenzsignal. (RS422, RS485 und NMEA 0183 sind es alle; „+/−“ allein unterscheidet sie nicht.)
- **H2** Nicht RS422: das bräuchte zwei Datenpaare, Robnet hat eines.
- **H3** Nicht NMEA 0183: dort sendet nur ein Gerät je Leitung; Robnet hat mehrere Teilnehmer und beliebige Abzweige.
- **H4** Am ehesten RS485-artig (ein Paar, mehrere Teilnehmer, abwechselndes Senden). Könnte auch ein eigener Robertson-Aufbau sein.
- **H5** „V System“ ist die Versorgung der Bedieneinheit aus dem J300; gemessen 26,4 V, also über der Bordspannung (J300 erzeugt sie wohl selbst).
- **H6** Nur „Bus“ ist eine serielle Datenleitung. On-Off und Alarm sind einfache Schaltleitungen (fester Pegel, Wechsel nur beim
  Ein-/Ausschalten oder Alarm); das Handbuch erklärt sie nicht. Alarm bestätigt (0,4 V / 4,8 V, 5-V-Logik); On-Off offen.

## 4. Messplan
**Messort:** Robnet-Klemmleiste der Hauptplatine im J300 (Motorraum; Handbuch S. 78: Schraubklemmen, Farben beschriftet).
Klemmleiste bleibt eingesteckt; schwarze Spitze fest (Krokodilklemme) an Grau. Bordspannung und Pumpenausgang nicht berühren.

**Stufe 1 – Multimeter** (Mittelwerte; Gleichspannung gegen Grau, je Robertson aus / STBY / AUTO):
Rosa (Vsys+), Weiß (Bus+), Braun (Bus−), Weiß gegen Braun (auch Wechselspannung), Gelb (On-Off), Grün (Alarm),
Grau gegen Bordmasse. Gelb beobachten, während STBY 3–5 s gedrückt wird. Zeigt Versorgung (H5), Ruhepegel (H1, H4),
Schaltleitungen (H6) und ob Daten laufen (Anzeige springt). **Entscheidet, ob der MAX3488 passt.**

**Stufe 2 – Oszilloskop** (wahlweise; Verlauf über die Zeit): Spannungshub eines Bits, Gegenlauf von Bus+/Bus− (Nachweis H1),
Bitdauer (Datenrate), Pausen und Telegrammlängen.

**Stufe 3 – Platine Robnet-Analyse** (Zero 2 W, MAX3488, MCP3208; nur mitlesen): Konzept und Blockschaltbild in
`99-tools/robnet-analyse/hardware/konzeption/`.
