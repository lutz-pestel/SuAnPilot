# Bauteilauswahl Motor-Controller V2.0

Version 00.09, Stand 07.10.2026, Obergrenze 300 Zeilen. Grundlage: `Projektdokument.md` Abschnitt 3,
`Blockschaltbild_Controller-V2.0.html`.
Abschnitte 1 bis 7 sind **festgelegt**; 8 und 9 sind Vorschlag und werden noch besprochen.
Preise sind Einzelpreise aus Händlerlisten, nur zur Größenordnung. Verworfene Wege stehen in je einem Satz;
wird eine Festlegung unbeschaffbar, wird neu gesucht, nicht in alten Listen nachgeschlagen.

## 0. Vorgaben, an denen jede Wahl gemessen wird
- Pumpe **Robertson RPU160**, Typenschild: 12 V DC, **7,5 A**, 3500 min⁻¹, 1,6 l/min, IP 44, Bj. 1995.
  Gemessen: Betrieb 4–6 A, Spitzen 8,3 A ohne Last. Endstufe soll 40 A Spitze vertragen (Reserve, Blockierfall).
- **Linie A (THT):** kein SMD-Löten auf unserer Platine: Einzelteile in Drahtform (DIP, TO-220) oder Module mit
  Stiftleiste. Je Teil SMD-Gegenstück prüfen, Abweichung begründen (`0-gesamtprojekt/fertigung/fertigungsstrategie-platinen.md`).
- Vor Preis gehen **Robustheit** und **Diagnosefähigkeit** (Strom *und* Klemmenspannung zurücklesen).
- Motorraum: warm, feucht, Vibration. Bauteile möglichst −40…+85 °C.

## 1. Endstufe (Leistungstreiber) — **festgelegt 04.10.2026**

**Pololu G2 High-Power Motor Driver 18v25**, Nr. 2994, 57 $ — <https://www.pololu.com/product/2994>.
Deutsche Händler laut Pololu: **Eckstein GmbH** (<https://eckstein-shop.de/pololu>), **TME Germany**
(<https://www.tme.eu/de/>), RobotShop; über DigiKey nur als „Marketplace", Versand aus den USA.
6,5–30 V, 25 A dauernd ohne Kühlkörper, Strombegrenzung, Verpolschutz, Stromrückmeldung 10 mV/A, Fehlerausgang.
Entscheidend für F9: Pololu benennt unser Schadensbild selbst — diskrete Brücken vertragen oft kein dauerhaftes
Durchschalten, weil die Bootstrap-Kondensatoren keine Ladezeit bekommen — und baut dagegen eine **zusätzliche
Ladungspumpe** ein, mit der die oberen Transistoren unbegrenzt eingeschaltet bleiben. Fehler verriegeln nicht:
Nach Wegfall der Ursache läuft das Modul selbst wieder an (S5).

**Einbau: gesteckt und mechanisch verschraubt.** Steuersignale über Stift-/Buchsenleiste, Leistung über Phoenix
MSTBA 2,5 wie alle Anschlüsse (Abschnitt 9; die mitgelieferten Pololu-Klemmen, 5 mm, 16 A, entfallen), Modul
zusätzlich auf Abstandsbolzen geschraubt — gesteckt für den schnellen Tausch, verschraubt gegen Vibration.
**Der Widerstand für die Strombegrenzung sitzt auf unserer Platine, nicht auf dem Modul**: Ein Ersatzmodul ist
dann ohne Nacharbeit einsatzbereit und bringt keine eigenen Werte mit (S7) — anders als der gekaufte Controller
am 01.10. Ein Ersatzmodul gehört trocken verpackt an Bord.

**Blockiertes Ruder meldet das Modul nicht.** Öffnet das Überdruckventil, steigt der Strom nur mäßig: nichts
greift, nichts wird gemeldet, das Ruder steht trotzdem. Steht der Motor still, springt der Strom (Faustregel
3–5× Nennstrom, grob 22–37 A — **nicht gemessen**); die Begrenzung steht ab Werk bei etwa 60 A und greift gar
nicht, ihr Ansprechen wäre auch kein Fehlerzustand. **Die Blockade erkennt nur die Software** aus Befehl +
Strom + stehender Ruderlage (S1, F6). Die Endstufe ist die letzte Verteidigungslinie, nicht die erste.

**Zwei Auflagen:** (1) Strombegrenzung über einen Widerstand zwischen VREF und Masse auf **15 A** senken, unter
den Wert der 20-A-Sicherung (Pololu nennt 100 kΩ → ca. 41 A; der Widerstand für 15 A ist zu erfragen). (2) **Temperatursensor am
Kühlwinkel ist Pflicht** (F11): Das Modul hat keine Übertemperatur-Abschaltung, und seine Fehlerleitung meldet
nur „Platine zu heiß", nicht die Transistoren, die zuerst sterben.

*Verworfen:* RoboClaw (teuer, Firmware verschlossen); VNH5019 (100 % nicht zugesichert); IBT-2/BTS7960 trotz
Vorhandensein (belegte Entwurfs- und Fertigungsmängel); eigene Brücke (heikelste Baugruppe, ohne Vorteil).

## 2. Strommessung — **festgelegt 04.10.2026**

**ACS758LCB-050B-PFF-T**, Hall-Sensor in Drahtform mit Schraubfahnen, **im Motorzweig**, ~8–20 €
(<https://de.farnell.com/allegro-microsystems/acs758lcb-050b-pff-t/ic-current-sensor-50a-3cb/dp/1791392>,
Farnell 1791392): ±50 A bidirektional, 40 mV je Ampere, ±2 % genau, ±1 % linear, 100 µΩ Innenwiderstand, 120 kHz
Bandbreite, Ansprechzeit 4 µs, −40…+150 °C, AEC-Q100. Ausgelesen über den ADS1115.

**Warum ein Hall-Sensor und kein Messwiderstand — es geht um den Messort.** Gemessen werden muss im
**Motorzweig**; dort springt das Potential bei PWM mit jeder Flanke zwischen Masse und Bordspannung. Ein
Verstärker müsste diesen Sprung ausblenden, der Hall-Sensor misst das Magnetfeld und weiß vom Potential nichts.
Dazu: 4 µs Ansprechzeit zeigen Anlauf- und Blockierspitzen wirklich (F2); galvanisch getrennt und mit 100 µΩ
ohne nennenswerten Spannungsverlust; und die Messung gilt immer — ob das Modul treibt, bremst, begrenzt oder
selbst ausgefallen ist.

**Zweite Quelle zur Gegenprobe:** die eingebaute Rückmeldung des G2 (10 mV/A plus 50 mV Versatz) hochohmig am
einfachen Eingang des ESP32 mitlesen; weichen beide Messungen ab, ist eine defekt. **An diesen Pin kein
Kondensator** — der Treiber benutzt ihn selbst für seine Strombegrenzung.

*Verworfen:* eingebaute Rückmeldung als einzige Messung (misst nur im Antriebsmodus, nur eine Richtung, Versatz
größer als das Nutzsignal bei kleinen Strömen — blind im Blockierfall); Messwiderstand mit INA226/INA219-Modul
im Motorzweig (müsste den PWM-Potentialsprung ausblenden, wandelt mit 0,14–8 ms zu träge für Spitzen);
Messwiderstand in der Batteriezuleitung (misst nicht den Motorstrom, sobald die Brücke bremst oder begrenzt);
Messwiderstand mit einzelnem Verstärkerbaustein (nur in SMD).

## 3. Messwerterfassung und Spannungsmessung — **festgelegt 04.10.2026**

**Wandler: MCP3208-CI/P** (DIP-16, im Sockel, 
<https://de.rs-online.com/web/p/ad-wandler/8895657>
<https://www.mouser.de/en/ProductDetail/Microchip-Technology/MCP3208-CI-P?qs=9y3LFqDLL8IuAGJEebQX9g%3D%3D>) mit Referenz
**LM4040DIZ-2.5, TO-92** (RS 534-3059 bei de.rs-online.com);
<https://de.rs-online.com/web/c/?searchType=MPN&searchTerm=LM4040DIZ-2.5>
<https://www.mouser.de/en/c/?q=LM4040DIZ-2.5>
zusammen ~3–7 €. 12 Bit, 8 Eingänge, SPI.
**Betrieb mit 3,3 V**, weil der ESP32 an seinen Eingängen keine 5 V verträgt und umgekehrt ein 5-V-Wandler an
seinen Eingängen 3,5 V erwarten würde, die der ESP32 nicht liefert. Daraus folgt die Referenz von 2,5 V — sie
darf die Versorgung nicht überschreiten — und ein Messtempo von etwa 60 000 statt 100 000 Messungen je Sekunde.
Begründung der Wahl:
- **Das Messtempo bestimmen wir selbst.** Eine Anlauf- oder Blockierspitze dauert wenige Millisekunden; mit
  5 000–10 000 Messungen je Sekunde liegen 100–200 Messpunkte darüber (F2, Spitzen erfassen). Im ruhigen Betrieb
  wird langsam gemessen, bei Verdacht schnell. Die Grenze setzt unsere Software, nicht das Bauteil.
- **Acht Eingänge, sieben Messstellen:** Klemme A, Klemme B, Bordspannung, Motorstrom, Stromrückmeldung des
  Leistungsmoduls, Temperatur am Kühlwinkel (F11) und die 3,3-V-Versorgung selbst (siehe unten). Ein Eingang ist frei.
- **Steckbar im Sockel**, ohne Lötkolben tauschbar.
**Anschluss über Hardware-SPI, nicht nachgebildet in Software.** Der Wandler hält die Messspannung in einem
Kondensator von 20 pF, der während der Wandlung Ladung verliert; unter 10 000 Takten je Sekunde leidet die
Genauigkeit, **bei Wärme besonders**. Software-SPI stünde bei jeder Unterbrechung still — mit eingeschaltetem
WLAN ständig — und lieferte dann Werte, die nicht falsch aussehen, aber falsch sind.
Auflösung: ein Schritt ist 0,61 mV, also 23 mA am Stromsensor und 4 mV an den Klemmen — weit feiner als die
Unterschiede, um die es geht (1,3 A statt 5 A; 1,9 V statt 11 V).

**Der Stromsensor wird ebenfalls aus 3,3 V versorgt**, sonst läge sein Ausgang über der Referenz. Seine
Empfindlichkeit hängt an dieser Spannung und sinkt im gleichen Verhältnis auf etwa 26 mV je Ampere; bei 20 A
liegt der Ausgang zwischen 1,1 und 2,2 V, also sauber im Messbereich. Weil jede Schwankung der 3,3 V den
Messwert mitverschiebt, **misst der achte Kanal diese Versorgung selbst** — die Software rechnet sie heraus.
Damit hängt die Strommessung nicht mehr an der Güte des Spannungsreglers.

**Messstellen:** je Stelle ein Spannungsteiler 100 kΩ / 18 kΩ, 1 % (16 V Bordspannung ergeben 2,44 V, unterhalb
der Referenz), dazu zwei Klemmdioden; bei einem Spannungsstoß von 100 V fließt durch den Vorwiderstand nur
1 mA. **Die Glättung ist je Kanal verschieden:** Klemmenspannungen mit ~10 ms, damit bei zerhackter Ansteuerung
der Mittelwert herauskommt (der Fall vom 04.10. — 1,9 V statt 11 V — wäre so sofort sichtbar); der Stromkanal
**ohne** diese Glättung, sonst verschenkt man die Spitzen.

*Verworfen:* ADS1115-Modul (nur 4 Eingänge und fest 860 Messungen je Sekunde — eine 2 ms kurze Spitze wird
verfehlt oder zufällig getroffen, und ein zufälliger Wert ist schlimmer als keiner, weil man ihn für den
Höchstwert hält; seine Vorteile, feinere Skala und eingebaute Verstärkung, brauchen wir seit der Entscheidung
für den Hall-Sensor nicht mehr); der Wandler im ESP32 (misst nicht geradlinig, nur 10–11 nutzbare Bit) — er
bleibt nur für die grobe Gegenprobe der Modul-Rückmeldung.

**Ein Widerstand mehr für den Selbsttest (S10):** 100 kΩ von einer Motorklemme nach Plus. Ohne ihn ziehen die
Messteiler die freien Klemmen in Ruhe nach Masse — „alles 0 V" wäre dann sowohl der gesunde Ruhezustand als auch
ein durchgebrannter unterer Schalter, ununterscheidbar. Mit dem Widerstand stellt sich in Ruhe eine mittlere,
berechenbare Spannung ein; 0 V oder volle Bordspannung heißt dann eindeutig: ein Schalter ist dauerhaft leitend.

## 4. RF300-Eingang (Zweidraht-Stromschnittstelle) — **festgelegt 07.10.2026, Versuch steht aus**

**Prinzip der alten RF300-Interfaceplatine, mit kleinerem Vorwiderstand** (Schaltplan `kicad/v00.01/RF300-Eingang`):
+12 V → **R1 220 Ω, 2 W** → RF+ → Geber → RF− → Masse. R1 speist den Geber, begrenzt bei Kurzschluss (höchstens
~58 mA) und macht die Stromsprünge als Spannungssprünge sichtbar. **C1 100 nF + BC337** werten nur die Sprünge aus
(Grundspannung abgetrennt): Die unbekannten Stromstufen und ihre Drift spielen keine Rolle. An der Klemme 10 nF gegen
Masse; keine eigene TVS-Diode, weil das Kabel an Bord höchstens 3 m lang, geschirmt (Schirm an Masse) und fern von
Lichtmaschine und Starter verlegt ist (Betreiber) und Bordnetzspitzen schon die 1.5KE20A am Geräteeingang abfängt
(Abschnitt 7). Versorgung über eigene Anschlüsse am Blatt (+12 V geschützter Zweig, +3,3 V, Masse).
Alles Drahtbauteile, zusammen unter 2 €. Gerechnet bei 12,73 V und 14 mA:
Geber ~9,6 V (heute 6,89 V gemessen, Robertson 10,8 V); im Dauerkurzschluss ~0,9 W in R1 (bei 14,4 V), daher 2 W.
**Fehlererkennung über die Frequenz:** kein Takt oder außerhalb 1600–5200 Hz = Störung (S2). Welcher Fehler
(Bruch, Kurzschluss) vorliegt, klärt im Fehlerfall ein Multimeter. Eine Mindestspannung des Gebers ist nirgends
angegeben; mit 6,89 V arbeitet er.
Industriepraxis bestätigt den Aufbau: NAMUR-Eingänge (EN 60947-5-6) speisen über einen festen Widerstand (1 kΩ an
8,2 V), der zugleich der Kurzschlussschutz ist.
**Offen:** Reicht der Sprung bei 220 Ω (heute ~360–410 Ω)? Versuch an der alten Platine.

## 5. Rechner — **festgelegt 04.10.2026**

**ESP32-DevKitC-32E** (WROOM-32E, Antenne als Leiterbahn auf dem Modul,
<https://www.mouser.de/ProductDetail/356-ESP32-DEVKITC32E>), ~12 €, Industrie-Ausführung −40…+85 °C,
Stiftleisten, zwei Rechenkerne.
- **Zähler in Hardware** (PCNT): Er zählt die RF300-Impulse ohne Zutun des Rechenwerks; die Frequenz steht nach
  jedem Messfenster sofort bereit, ohne Mittelung über 30 Messungen wie heute. Das ist F4.
- **Zwei Rechenkerne:** einer misst, der andere regelt und redet — die Messung stockt nicht, während Daten
  übertragen werden.
- **Anschlüsse mit Reserve:** gebraucht werden rund 19 (Wandler 4, Display 2, zwei serielle Strecken 3,
  Endstufe 4, Frequenzeingang 1, Gegenprobe 1, drei Leuchtdioden, ein Taster), vorhanden sind etwa 30.
- **WLAN für die Fernprogrammierung** (F12). Zwei Auflagen an den Platinenentwurf, damit die Antenne auf dem
  Modul genügt: Das Modul sitzt **an der Kante unserer Platine, die Antenne ragt darüber hinaus**; darunter und
  daneben kein Kupfer, keine Bauteile. Alles Metallische (Leistungsmodul, Kühlwinkel, Klemmen, dicke Kabel)
  kommt ans andere Ende. Der Kunststoff des Gehäuses stört den Funk nicht, nahes Metall dagegen sehr.
- **Rückweg, falls der Funk im Motorraum nicht reicht:** Die Ausführung **-32UE**
  (<https://www.digikey.de/de/products/detail/espressif-systems/ESP32-DEVKITC-32UE/12091813>) hat dieselbe
  Platine und Anschlussbelegung, aber statt der Leiterbahn eine Buchse für eine äußere Antenne. Weil das Modul
  in einer Buchsenleiste steckt, ist der Wechsel Steckarbeit — die Platine bleibt unverändert.
- Versorgung aus unserem eigenen Regler statt über USB. **Seine 3,3-V-Logik bestimmt die Betriebsspannung des
  Wandlers** (Abschnitt 3).

*Verworfen:* Arduino Nano (zu langsam, zu wenige Schnittstellen),
Teensy 4.1 (mehr als nötig).

## 6. Datenverbindung — **festgelegt 04.10.2026**

**MAX488E / MAX3488E (DIP-8)** — Datenblatt <https://www.analog.com/en/products/max3488e.html>, Bezug z. B.
<https://de.farnell.com/analog-devices/max488cpa/transceiver-rs-485-422-dip8-488/dp/2519464>.
Die Familie steckt bereits zweimal auf der vorhandenen Platine
`1-tinypilot/autopilot/hardware/kicad/PyPilot_Main_RS422`: U6 für die Strecke zum Motor-Controller, U7 für die Ruderlage, beide an
3,3 V, je ein Abschlusswiderstand am Empfangspaar — an Bord erprobt und beschaffbar. Eigenschaften: Vollduplex
(getrennte Sende- und Empfangsadern, keine Umschaltung in Software), 250 kbit/s bei weichen Flanken (wenig
Störstrahlung), Treiber kurzschluss- und übertemperaturfest, Empfänger mit Fail-Safe (Kabelbruch ergibt sicheren
Ruhepegel statt Zeichensalat), ±15 kV Schutz gegen statische Entladung.
**Die Ruderlage läuft schon heute differentiell über RS422** (Stecker J3, Pins 5–8), nicht einadrig.

**Galvanisch getrennt, aber nur auf unserer Seite** — der TinyPilot bleibt unverändert. Motorströme bis 40 A auf
gemeinsamer Masse erzeugen über 10–15 m Kabel Spannungsunterschiede zwischen Motorraum und Steuerhaus; ein
Ausgleichsstrom auf der Datenmasse zerstört Treiber, und die Ursache findet man hinterher nie.
Je Strecke: **zwei Optokoppler 6N137 (DIP-8, <https://de.rs-online.com/web/p/optokoppler/2799622>) + isolierter
DC/DC-Wandler Traco TMA 0505S (SIP, 1 kV Trennung, ~3,70 €,
<https://de.rs-online.com/web/p/dcdc-wandler/1914922>) + MAX488E** auf der getrennten Seite, etwa 12–18 €. Dort das 5-V-Modell, weil schnelle Optokoppler in Drahtform erst ab 4,5 V
arbeiten; der 3,3-V-Typ MAX3488E bleibt richtig für jede Strecke, die nicht getrennt wird.
**Zwei getrennte Strecken:** eine zum TinyPilot, eine für die Ruderlage. Nur so hält F5 — die Anzeige am
Steuerstand läuft weiter, wenn die Verbindung zum TinyPilot ausfällt.

*Verworfen:* isolierte Fertigbausteine wie ADM2483 — nur in SMD erhältlich.

## 7. Versorgung und Schutz — **festgelegt 04.10.2026**

- **Zwei getrennte Regler, beide Recom R-78B5.0-2.0** (F13): SIP-3, 5 V / 2 A, Eingang **6,5–32 V**, kurzschlussfest, −40…+70 °C ohne Abschlag, verträgt keine
  Verpolung (Datenblatt REV 1/2017, <https://www.recom-power.com/pdf/Innoline/R-78B-2.0.pdf>). Gleicher Typ in beiden
  Zweigen: ein Ersatzteil passt überall, ein Schaltplanblatt (`kicad/v00.01/5V-Zweig`, zweimal eingesetzt), Reserve
  für Sendespitzen des ESP32. 3,3 V liefert das ESP32-Modul selbst.
  **Teile je 5-V-Zweig** (Drahtbauteile): Regler R-78B5.0-2.0; Sicherung 2 A träge, 5 × 20 mm im Halter; rote
  Leuchtdiode 3 mm mit 4,7 kΩ parallel zur Sicherung; Eingangsfilter nach Herstellervorschlag: 10 µF 50 V keramisch,
  Drossel 10 µH (mindestens 2 A), 4,7 µF 50 V keramisch. Typen von Halter, Drossel und Kondensatoren noch zu wählen. *Verworfen:* Traco TSR 1-2450 für die
  Elektronik (billiger, aber zweiter Typ und zweites Schaltplanblatt, nur 1 A).
  Der Eingangsbereich entscheidet, nicht die Stromstärke: Beim Anlassen des Diesels bricht die Bordspannung
  kurz ein — ein Regler, der erst ab 10 V arbeitet (z. B. Traco TSR 3-2450 mit 3 A), ließe den Pi neu starten.
  Getrennte Regler heißen auch: Ein Kurzschluss im Steuerhaus nimmt die Ruderlagen-Ausgabe nicht mit (F5, S6).
  Zum Steuerstand gehen 5 V über das **vorhandene Kabel** (Festlegung des Betreibers 07.10.2026); im Steuerstand
  ist kein Platz für einen eigenen Regler. Der Zweig versorgt in Phase 3 auch den SuAnPilot.
- **Schutz gegen Überspannung aus dem Bordnetz: Schutzdiode 1.5KE20A**, unidirektional, 1500 W, DO-201,
  Drahtform, unter 1 € (<https://www.digikey.de/de/products/detail/littelfuse-inc/1-5KE20A/688017>), direkt
  hinter der Sicherung; dazu Drossel und Kondensator am Eingang.
  **Die Spannungsklasse ist durch zwei Grenzen eingeklemmt, 20 V ist die einzige dazwischen:** Nach unten darf
  sie im Betrieb nicht leiten — die Lichtmaschine lädt bis 15 V, diese Diode sperrt bis **17,1 V**. Nach oben
  muss sie unter der Grenze der Endstufe klemmen — der G2 verträgt **30 V**, diese Diode klemmt bei **27,7 V**.
  Die einfache Ausführung genügt; im Gleichspannungsnetz klemmt sie schärfer als eine bidirektionale.
  **Wogegen sie schützt:** Im Alltag gegen Schaltspitzen anderer Verbraucher (Ankerwinde, Bugstrahlruder,
  Kompressor, eigene Pumpe) — die hält sie mühelos aus. Im seltenen Fall gegen den **Lastabwurf**: Reißt bei
  laufendem Motor die Verbindung zur Batterie, liefert die Lichtmaschine noch 100–400 ms weiter, weil ihr
  Erregerfeld nicht schlagartig zusammenbricht; die Spannung steigt auf etwa 35 V, bei Maschinen ohne eigene
  Begrenzung auf über 100 V. **Ehrlich dazu:** Für ein so langes Ereignis ist die Diode nicht ausgelegt. Sie
  stirbt dann, fast immer als Kurzschluss — und die Sicherung fällt. Das ist ihr Wert: Sie macht aus einem
  Totalschaden einen Wechsel von Diode und Sicherung für zwei Euro.
- **Verpolschutz nur für den Elektronikzweig: Schottky-Diode in Reihe** (festgelegt 07.10.2026, Typ noch zu wählen,
  etwa 3 A / 40 V). Ein Bauteil; Verlust typisch 0,4–0,5 V, die Regler arbeiten damit bis etwa 7 V Bordspannung.
  Beleg: Mit der Silizium-Diode der alten Interfaceplatine ist der TinyPilot in allen Feldversuchen nie neu gestartet
  (Betreiber, 07.10.2026); die Schottky-Diode verliert weniger. *Verworfen:* P-Kanal-MOSFET (nicht nötig). Der G2 bringt
  seinen eigenen Verpolschutz mit — damit entfällt ein Bauteil im Hochstrompfad.
- **Drei Sicherungen, aufeinander abgestimmt:** Leistung **20 A** träge (KFZ-Flachsicherung im Halter, Leitung
  2,5 mm²) — dazu passend wird die **Strombegrenzung der Endstufe auf 15 A** gesetzt, damit zuerst die
  Elektronik begrenzt und erst danach die Sicherung fällt. Elektronik 2 A, TinyPilot-Zweig 2 A (F13).
- **Rote Leuchtdiode „Sicherung durch"**, mit Widerstand **parallel zur Sicherung**: Ist die Sicherung heil,
  liegt über ihr keine Spannung und die Diode bleibt dunkel; ist sie durch, fließt ein kleiner Strom über die
  Diode zur Last und sie leuchtet. Zwei Bauteile, und man sucht nicht stundenlang.

## 8. Anzeige und Leuchtdioden — Vorschlag

**OLED 0,96" SSD1306, I²C**, ~8 € (<https://www.az-delivery.de/products/0-96zolldisplay>), −30…+70 °C,
steckbar, ohne Hintergrundlicht; Anzeige nach einer Minute
abschalten, damit kein Bild einbrennt. **Pflicht sind vier Leuchtdioden** (Betrieb, Pumpe läuft, Störung, blau für
aktives WLAN nach F12) — sie fallen nicht aus wie ein Display. Dazu die **rote Leuchtdiode „Sicherung durch"**
aus Abschnitt 7, die nicht am Rechner hängt und auch bei totem Gerät noch anzeigt.
**Ein Taster mit zwei Aufgaben:** Anzeige wecken und WLAN wieder einschalten (F12). Er muss von außen
bedienbar sein, ohne das Gehäuse zu öffnen.
*Verworfen:* Zeichen-LCD 16×2 mit I²C — Hintergrundlicht nötig, engerer Temperaturbereich, größer.

## 9. Leiterplatte, Klemmen, Gehäuse — Vorschlag

- **Hohe Ströme gehören nicht auf eine selbst entworfene Leiterbahn** (Praxiswert: 20 mm breite Außenbahn mit
  105 µm Kupfer wird bei etwa 70 A um 58 K wärmer). Leistungspfad als aufgelötete Kupferschiene oder dicker
  blanker Draht, Weg Klemme → Modul → Klemme so kurz wie möglich.
- **Alle Klemmen wie auf der RF300-Interfaceplatine: Phoenix Contact MSTBA 2,5/…-G-5,08** (festgelegt 07.10.2026):
  Stiftleiste liegend auf der Platine, dazu steckbarer Schraubstecker MSTB 2,5/…-ST-5,08; Raster 5,08 mm, 12 A je
  Kontakt, 320 V, Leiter bis 2,5 mm² (z. B. 2-polig: Stiftleiste 1757242, Stecker 1757019). Gilt auch für Pumpe und
  12-V-Zuleitung: Im Normalbetrieb bleibt der Strom darunter (gemessen 4–6 A, Spitze 8,3 A); Dauerblockieren
  verhindert F6. *Verworfen:* eigene Leistungsklemmen 7,62 mm (zweiter Typ, im Normalbetrieb nicht nötig).
- **Gehäuse 3D-Druck: ASA**, ersatzweise Polycarbonat; **PLA scheidet aus** (erweicht bei 55–60 °C), PETG ist
  grenzwertig. O-Ring in Nut, Verschraubungen M16/M20, Ziel IP 54 (die Pumpe selbst ist IP 44).
- **Wärmeabfuhr:** Leistungsmodul auf einen Aluminiumwinkel durch die Gehäusewand nach außen; dort sitzt auch
  der Temperatursensor (F11).
- **Durchführungen in der Gehäusewand**, alle dicht: Taster, vier Leuchtdioden plus die rote für die Sicherung,
  Kühlwinkel, Kabelverschraubungen. Für eine spätere Antennenbuchse wird eine Stelle **vorbereitet, aber nicht
  gebohrt** — jedes Loch ist eine mögliche Undichtigkeit, und gebraucht wird sie nur, falls der Funk aus dem
  Motorraum nicht reicht.
- **Anschlüsse nach außen:** 12 V Leistung (2,5 mm², eigene Sicherung) und Motor A/B; RF300 zweiadrig geschirmt;
  zum Steuerhaus **das vorhandene Kabel, unverändert** (8 Adern: grün Stellbefehle, orange Meldungen, braun
  NMEA-Ruderlage, weiß Minus, blau frei; dazu rot/schwarz für 5 V, F13). **Stecker und Belegung wie an der
  RF300-Interfaceplatine:** MSTBA 2,5/8 wie dort J9 (1–4 RS422 zum Motor-Controller A+, B−, Z−, Y+; 5–8 RS422
  Ruderlage A+, B−, Z−, Y+), 5 V über MSTBA 2,5/2.

## 10. Offen — vor dem Kauf zu messen oder zu klären
1. *(erledigt 05.10.2026 – Arbeitspunkt des RF300 gemessen, Auslegung steht in Abschnitt 4.)*
2. RPU160: Anlauf- und Blockierstrom messen, und ob die Pumpe ein Überdruckventil hat. Beides entscheidet über
   Sicherung, Kupferquerschnitt, Kühlfläche — und darüber, wie sich ein Anschlag überhaupt bemerkbar macht.
3. Widerstandswert für die Strombegrenzung des G2 bei Pololu erfragen (Ziel 15 A).
4. Temperaturklasse der RS422-Treiber festlegen: 0…+70 °C oder −40…+85 °C. Für den Motorraum die Industrie-
   Ausführung. Welche heute im TinyPilot sitzt, steht im Schaltplan nicht.
5. Genauigkeitsklasse der Referenz wählen: ±1 % (LM4040**D**IZ-2.5) reicht, ±0,1 % (LM4040**A**IZ-2.5) kostet
   kaum mehr. Die Klasse bestimmt den Fehler aller Spannungs- und Strommessungen gleichermaßen.
6. Wann darf der Selbsttest (S10) laufen? Am Steg bewegt sich das Ruder gefahrlos, im engen Fahrwasser nicht.
7. **Funkprobe vor dem Platinenentwurf:** ein Handy oder anderes WLAN-Gerät an die künftige Einbaustelle im
   Motorraum legen und prüfen, ob es den Master erreicht und wie stark. Entscheidet über -32E oder -32UE.

## Quellen
**Die Bezugsquelle jedes Bauteils steht im jeweiligen Abschnitt.** Hier nur, was nicht an einem Bauteil hängt:
- Ladungspumpe, Strombegrenzung und Stromrückmeldung des G2: <https://www.pololu.com/product/2994/faqs>
- RS422-Treiber im Schiff verbaut: `1-tinypilot/autopilot/hardware/kicad/PyPilot_Main_RS422/PyPilot_Main.net` (U6, U7)
- Leiterbahnbreite hoher Ströme: <https://courses.fedevel.com/forum/other/high-current-tracepour>
- Neuer pypilot-Controller (4,5 oz Kupfer, Sicherungs-LED): <https://forum.openmarine.net/printthread.php?tid=2248>
- Heutiges Protokoll und Verkabelung: `1-tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md`
