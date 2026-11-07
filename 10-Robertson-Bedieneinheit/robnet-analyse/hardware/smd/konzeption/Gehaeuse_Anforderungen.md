# Gehäuse Robnet-Analyse (SMD-Platine) – Anforderungen

Version 00.11, Stand 07.11.2026. Modell, Baugruppe, Schnitte und Druckdateien: `../gehaeuse/v00.01/`. Gebaut wird **ein** Gehäuse für die bestückte Platine; die zweite Platine ist Reserve.
Maße aus `../kicad/v00.01/Robnet-Analyse.kicad_pcb` und dem 3D-Modell in `../../tht/3d-modelle/kicad-lage/` (Betreiber: stimmt). Lage: x nach rechts, y nach unten, z über der Platine, Ursprung Platinenecke oben links.

## 1. Einsatz
- Motorraum: sauber, trocken, höchstens 45 °C (Betreiber). Nutzungsdauer überschaubar, Werkzeug, nicht überabsichern. Nur mechanischer Schutz, nicht dicht.
- Einbau wahlweise an einer senkrechten Holzwand oder auf einer waagerechten Fläche, mit Holzschrauben.

## 2. Deckel
- Geht **ohne Werkzeug** und schnell ab; hält in beiden Einbaulagen und bei Vibration. Bauart: zwei angedruckte Schnapparme an oberer und unterer Wand. Alle Rasten halten nur durch Kraft, nicht durch Riegel: Die Nasen sind auf beiden Seiten schräg, Deckel und Platine lassen sich ohne Wegdrücken herausziehen.
- Führung: umlaufende Lippe, greift höchstens 3 mm in die Wanne (Betreiber), unterbrochen nur an J1, J2, J3, USB, HDMI und den Schnapparmen.
- Kabel und Stecker bleiben beim Abnehmen stecken. Wannenrand 15,6 mm über der Platinenoberseite, Spalt über den Steckern rund 0,5 mm.
- Durchsichtig, ohne Schleifen und Lackieren von Hand. Eben, ohne Absenkung (Betreiber). Rippen in beiden Achsen zur Versteifung, nicht über den Jumpern.
- Keine Schrift auf dem Deckel (Betreiber). Versionsnummer als Gravur unter dem Boden, mindestens 0,8 mm tief und breit, gerade Balken.
- Abgenommen: alle Jumper JP1–JP7 und die Oszilloskop-Stifte J4 frei, Finger kommen an die Jumper. Gemessen wird nur mit abgenommenem Deckel.

## 3. Platine im Gehäuse
- Platine 100 × 100 mm, 1,6 mm dick, M3-Löcher bei (3,8 / 3,8), (96,2 / 3,8), (3,8 / 96,2), (96,2 / 96,2).
- **Rasten statt Schrauben:** Angedruckte Stifte in den vier Eckenlöchern nehmen die Steckkräfte auf. Zwei Federarme halten sie unten: linke Wand 25 mm von oben, rechte Wand mittig (Betreiber). Muss mit zwei Händen zu lösen sein. So viel wie möglich wird mitgedruckt.
- Nylonschrauben M3 **sehr sparsam**, nur wo Rasten nicht hält; dann Nylonmutter seitlich in die Säule geschoben, kein Gewinde und keine Schmelzmutter im Resin.
- Das Material ist spröde: überall genug Fleisch, wo Kraft angreift.
- Unter der Unterseite der Platine 4 mm frei (Lötstellen ragen laut Modell 2,4 mm heraus); oben mindestens bis z 19,0 (Raspberry mit Kühlkörperset und Schrauben, montiert) plus Luft.
- Der Raspberry hält in seiner Buchsenleiste; das Gehäuse stützt ihn nicht. Stützen über seine Schraublöcher behält sich der Betreiber vor: dort nichts verbauen. Das 5-V-Modul U3 liegt flach und niedriger als Stecker und Raspberry.

## 4. Öffnungen in der Wand
| Wand | Wofür | Bereich | Maße laut Modell |
|---|---|---|---|
| oben | J1 Kabel zum Hauptgerät J300 | x 58,5–90,9 | Stecker ragt 9,5 mm über die Platinenkante, Oberkante z 15,14 |
| oben | J2 12 V | x 11,4–23,5 | wie J1 |
| unten | J3 Bedieneinheit | x 58,5–90,9 | wie J1 |
| links | USB des Raspberry mit Adapter | y 44–56 | Stecker etwa 10,5 × 7 mm (Annahme des Modells) |
| links | HDMI des Raspberry: Stecker bleibt anschließbar (Betreiber) | y 70,5–87,5 | Annahme Stecker bis 17 breit, 10 hoch; nach oben offen |
| unten | Griffraum Speicherkarte, Wand ab z 7,4 offen | x 7–24 | Karte endet bei y 93,4, Wechsel bei abgenommenem Deckel |
| oben, unten | Fenster für die Deckelnasen | x 35,5–46,5 | Wandfenster 11 × 4,5 mm |

- Öffnungen nach oben offen, damit gesteckte Stecker mit Kabel beim Deckelabnehmen bleiben.
- Lüftung: je drei Schlitze links und rechts des Federarms in der rechten Wand und die Öffnungen oben, weil Raspberry und 5-V-Modul im Gehäuse Wärme abgeben.
- Keine angedruckte Zugentlastung (Betreiber, 07.11.2026).

## 5. Befestigung des Gehäuses
Vier angedruckte Laschen, 5 mm dick, außen an den Ecken links und rechts, Loch 4,5 mm für 4-mm-Holzschraube, handfest mit Unterlegscheibe. Das Gehäuse lässt sich mit eingebauter Platine anschrauben.

## 6. Fertigung: JLC3DP (3D-Druckdienst von JLCPCB)
- Verfahren SLA (Resin). Wanne **Grey** (grau, formfest bis 51–59 °C, Dehnung 7–12 %; Betreiber, CBY sah in Hellgelb schlecht aus). Deckel **8001 durchsichtig** (formfest bis 53 °C, Dehnung 12 %, ab Werk geschliffen und klar lackiert). Keine eigene Nachbearbeitung.
- Preis nach Sofortangebot mit den Druckdateien, 07.11.2026: Wanne Grey 6,97 €, Deckel 8001 durchsichtig 9,15 €, zusammen 16,12 €. Dazu Versand 6,21 € sowie Steuer und Zoll an der Kasse. Bestellung nur mit Freigabe; JLC3DP verlangt je Teil eine Produktbeschreibung.
- Regeln JLC3DP: Wand über 1,2 mm, dünnste Stelle mindestens 0,8 mm; Toleranz ±0,2 mm, Löcher ±0,3 mm; Spiel 0,2 mm zwischen Teilen, 0,5 mm bei beweglichen; keine gedruckten Gewinde; große ebene Flächen können sich verziehen.
- JLC3DP warnt beim 8001 vor kleinen Bläschen und nicht ganz klaren verwinkelten Formen. Die Durchsicht zeigt erst der Druck.

## 7. Offen
- Schrauben, falls gebraucht: Set [Glarks M3 Nylon](https://www.amazon.de/dp/B0DLZPM53W) 4,99 €, wenig Lager; Ersatz [Swpeet](https://www.amazon.de/dp/B0DKND2824) 7,99 €, auf Lager (Amazon, 07.11.2026). Zweiter Händler außerhalb von Amazon fehlt.
