# Robnet (Datennetz des Robertson AP300X)

Version 00.07, Stand 13.10.2026, Obergrenze 60 Zeilen.
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

## 2. Messwerte (Betreiber, an der J300-Klemmleiste)
Die Klemmleiste ist ein steckbarer 6-poliger Phoenix-Verbinder mit Schraubklemmen; Reihenfolge von links: Bus−, Bus+, Vsys+,
Vsys−, On-Off, Alarm. **10.10.2026**, Digitalvoltmeter gegen Masse der Robertson-Versorgung (Zustand nicht notiert):
Bus− 0,7 V · Bus+ 4,4 V · Vsys+ 26,4 V · Vsys− 0,004 V · On-Off 13,5 V · Alarm 0,4 V (im Alarm 4,8 V); Bus+ gegen Bus− 3,7 V.
Oszilloskop am Bus: Pakete aus unregelmäßigen Pulsen mit Pausen, ähnlich der NMEA-Ausgabe der RF300-Interfaceplatine.
**10.–13.10.2026:** On-Off etwa 12 V; beim Kommando ON/OFF an der Bedieneinheit Einbruch auf etwa 8 V.
Offen: Datenrate, Hub beim Springen, Gegenlauf Bus+/Bus−, Paketabstand; welche Seite On-Off herunterzieht und welche
Alarm treibt. Protokoll und Datenrate nennen weder die Handbücher (AP300X, AP11, AP21/22, AP3000X) noch Internet-Suchen.

## 3. Hypothesen (je mit Prüfstand; Grundlage Allgemeinwissen, nicht die Dokumente)
- **H1** „Bus+/Bus−“ ist ein Differenzsignal. (RS422, RS485 und NMEA 0183 sind es alle; „+/−“ allein unterscheidet sie nicht.)
  H1 und H4 gestützt durch die Pegel in Abschnitt 2 (0,7/4,4 V, typisch 5-V-Differenztreiber), nicht bewiesen.
- **H2** Nicht RS422: das bräuchte zwei Datenpaare, Robnet hat eines.
- **H3** Nicht NMEA 0183: dort sendet nur ein Gerät je Leitung; Robnet hat mehrere Teilnehmer und beliebige Abzweige.
- **H4** Am ehesten RS485-artig (ein Paar, mehrere Teilnehmer, abwechselndes Senden). Könnte auch ein eigener Robertson-Aufbau sein.
- **H5** „V System“ ist die Versorgung der Bedieneinheit aus dem J300; gemessen 26,4 V, also über der Bordspannung (J300 erzeugt sie wohl selbst).
- **H6 bestätigt:** Nur „Bus“ ist eine serielle Datenleitung (Datenpakete, Oszilloskop). Alarm ist 5-V-Logik (0,4 / 4,8 V).
  On-Off ist eine Schaltleitung ohne Logikpegel (12 V → 8 V beim Kommando ON/OFF); vermutlich zieht eine Seite sie über
  einen Widerstand herunter – welche, klärt die Robnet-Analyse durch Auftrennen.
- **H7** Datenrate höchstens etwa 9600 Baud, weil das Gerät alt ist (Annahme des Betreibers, ungemessen).

## 4. Weitere Messungen
Multimeter-Messung (Stufe 1) erledigt, Ergebnisse in Abschnitt 2. Datenrate, Signalform, Telegramme und das Auftrennen
einzelner Adern übernimmt die Platine Robnet-Analyse: Einstieg `10-Roberson-Bedieneinheit/robnet-analyse/hardware/konzeption/robnet-analyse.md`.
Sicherheit beim Messen von Hand: Klemmleiste gesteckt lassen, schwarze Spitze fest an Grau, Bordspannung und Pumpenausgang
im J300 nicht berühren.
