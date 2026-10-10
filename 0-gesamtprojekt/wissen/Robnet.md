# Robnet (Datennetz des Robertson AP300X)

Version 00.01, Stand 10.10.2026, Obergrenze 60 Zeilen.
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

## 2. Nicht gefunden
Spannungspegel, Protokoll, Datenrate, Höhe der Versorgungsspannung „V System“. Handbücher AP300X, AP11, AP21/22, AP3000X
und zwei Internet-Suchen (10.10.2026) nennen nichts. Das Handbuch erwähnt nur eine interne 15-V-Versorgung im J300;
dass sie ins Robnet geht, steht dort nicht.

## 3. Hypothesen (alle unbestätigt, aus Allgemeinwissen, nicht aus Dokumenten)
- **H1** „Bus+/Bus−“ ist ein Differenzsignal. (RS422, RS485 und NMEA 0183 sind es alle; „+/−“ allein unterscheidet sie nicht.)
- **H2** Nicht RS422: das bräuchte zwei Datenpaare, Robnet hat eines.
- **H3** Nicht NMEA 0183: dort sendet nur ein Gerät je Leitung; Robnet hat mehrere Teilnehmer und beliebige Abzweige.
- **H4** Am ehesten RS485-artig (ein Paar, mehrere Teilnehmer, abwechselndes Senden). Könnte auch ein eigener Robertson-Aufbau sein.
- **H5** „V System“ ist die Versorgung der Bedieneinheit aus dem J300; Höhe unbekannt.
- **H6** Nur „Bus“ ist eine serielle Datenleitung. On-Off und Alarm sind einfache Schaltleitungen (fester Pegel, Wechsel nur beim
  Ein-/Ausschalten oder Alarm); das Handbuch erklärt sie nicht. Prüfung: Multimeter, flackert die Spannung ständig (dann Daten)?

## 4. Vorschlag zur Klärung (nicht beauftragt)
Messung am Robnet-Stecker: Versorgungsspannung, Ruhepegel und Verlauf der Busleitung (Oszilloskop oder Logikanalysator),
Zeit pro Bit. Daraus folgen Typ (H1–H4) und Datenrate.
