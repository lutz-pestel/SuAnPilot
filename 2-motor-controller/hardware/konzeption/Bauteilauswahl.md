# Bauteilauswahl Motor-Controller V2.0

Version 00.21, Stand 09.10.2026, Obergrenze 350 Zeilen. Grundlage: `Projektdokument.md` Abschnitt 3,
`Blockschaltbild_Controller-V2.0.html`.
Abschnitte 1 bis 8 sind **festgelegt**; 9 ist Vorschlag und wird noch besprochen.
Preise sind Einzelpreise aus Händlerlisten, nur zur Größenordnung. Verworfene Wege stehen in je einem Satz;
wird eine Festlegung unbeschaffbar, wird neu gesucht, nicht in alten Listen nachgeschlagen.

## 0. Vorgaben, an denen jede Wahl gemessen wird
- Pumpe **Robertson RPU160**, Typenschild: 12 V DC, **7,5 A**, 3500 min⁻¹, 1,6 l/min, IP 44, Bj. 1995.
  Gemessen: Betrieb 4–6 A, Spitzen 8,3 A ohne Last. Endstufe soll 40 A Spitze vertragen (Reserve, Blockierfall).
- **Linie A (THT):** kein SMD-Löten auf unserer Platine: Einzelteile in Drahtform (DIP, TO-220) oder Module mit
  Stiftleiste. Je Teil SMD-Gegenstück prüfen, Abweichung begründen (`0-gesamtprojekt/fertigung/fertigungsstrategie-platinen.md`).
- Vor Preis gehen **Robustheit** und **Diagnosefähigkeit** (Strom *und* Klemmenspannung zurücklesen).
- Motorraum: warm, Vibration. Bauteile möglichst −40…+85 °C. Das Gehäuse dient nur dem mechanischen Schutz (Betreiber).

## 1. Endstufe (Leistungstreiber) — **festgelegt 04.10.2026**

**Pololu G2 High-Power Motor Driver 18v25**, Nr. 2994, 57 $ — <https://www.pololu.com/product/2994>.
Deutsche Händler laut Pololu: **Eckstein GmbH** (<https://eckstein-shop.de/pololu>), **TME Germany**
(<https://www.tme.eu/de/>), RobotShop; über DigiKey nur als „Marketplace", Versand aus den USA.
6,5–30 V, 25 A dauernd ohne Kühlkörper, Strombegrenzung, Verpolschutz, Stromrückmeldung 10 mV/A, Fehlerausgang.
Entscheidend für F9: Pololu benennt unser Schadensbild selbst — diskrete Brücken vertragen oft kein dauerhaftes
Durchschalten, weil die Bootstrap-Kondensatoren keine Ladezeit bekommen — und baut dagegen eine **zusätzliche
Ladungspumpe** ein, mit der die oberen Transistoren unbegrenzt eingeschaltet bleiben. Fehler verriegeln nicht:
Nach Wegfall der Ursache läuft das Modul selbst wieder an (S5).

**Einbau: gesteckt und verschraubt** (Betreiber, 08.10.2026). Modul **umgedreht** auf **zwei Messing-Stehbolzen** über unserer
Platine: Kondensatoren zur Platine, Transistoren oben in freier Luft; Stiftleiste auf der Kondensatorseite eingelötet,
**Buchsenleiste so hoch, dass Kondensatoren (8,0 mm) und Pololu-Klemmen (10,0 mm) darunter Platz haben**; die Fläche
darunter ist für Bauteile gesperrt.
**Am Pololu wird nur gesteckt und geschraubt, nie gelötet** (Betreiber, 08.10.2026); Leisten, Stifte und Klemmen sind
vorher eingelötet, beim Ersatzmodul ebenso. An den **mitgelieferten Pololu-Schraubklemmen** hängen nur vier kurze Leitungen
zu fest eingelöteten Klemmen auf unserer Platine (Degson DG301, Abschnitt 9): VIN und GND von unserer Eingangsseite,
OUTA und OUTB zurück. **Die Pumpe wird an unserer Platine angeschlossen:** Dort misst sie die Klemmenspannung A/B
(Abschnitt 3; gelbe Leuchtdioden, Abschnitt 8), Ader A läuft über den Hall-Sensor (Abschnitt 2). In keine Klemme kommt mehr
als eine Ader. Zusätzlich je ein Stift in den Pololu-Lötpunkten **„+" (VM, hinter dem Verpolschutz des Pololu) und „−"**,
gesteckt in Einzelbuchsen: Darüber hängt unser Elko (Abschnitt 7). „+" nie mit +12V verbinden, sonst ist der Verpolschutz
umgangen. **Die Pololu-Klemmen sitzen auf der Kondensatorseite, also nach unten**; die vier Leitungen (mindestens 20 mm)
treten an der Klemmenkante unter dem Pololu heraus, unsere zwei Klemmen sitzen direkt daneben. **Tausch:** die vier
Schrauben an unserer Platine lösen, Stehbolzen lösen, Pololu samt Leitungen abziehen; das Ersatzmodul liegt fertig verdrahtet an Bord.
Im Schaltplan: Pololu-Klemmen als Hilfslötaugen auf der Unterseite, die vier Leitungen als Brücken W1–W4 (nicht auf der Platine, in der Stückliste).
**Der Widerstand für die Strombegrenzung sitzt auf unserer Platine, nicht auf dem Modul**: Ein Ersatzmodul ist
dann ohne Nacharbeit einsatzbereit und bringt keine eigenen Werte mit (S7) — anders als der gekaufte Controller
am 01.10. Ein Ersatzmodul gehört trocken verpackt an Bord.

**Blockiertes Ruder meldet das Modul nicht.** Öffnet das Überdruckventil, steigt der Strom nur mäßig: nichts
greift, nichts wird gemeldet, das Ruder steht trotzdem. Steht der Motor still, springt der Strom (Faustregel
3–5× Nennstrom, grob 22–37 A — **nicht gemessen**); die Begrenzung steht ab Werk bei etwa 60 A und greift gar
nicht, ihr Ansprechen wäre auch kein Fehlerzustand. **Die Blockade erkennt nur die Software** aus Befehl +
Strom + stehender Ruderlage (S1, F6). Die Endstufe ist die letzte Verteidigungslinie, nicht die erste.

**Zwei Auflagen:** (1) Strombegrenzung über einen Widerstand zwischen VREF und Masse auf **15 A** senken, unter
den Wert der 20-A-Sicherung im Schiff (Pololu nennt 100 kΩ → ca. 41 A; der Widerstand für 15 A ist zu erfragen). (2) **Fehlerausgang (FLT) an
den ESP32** (F11): Er meldet Kurzschluss, Unterspannung und Übertemperatur; das Modul schaltet bei Übertemperatur
nicht selbst ab (Pololu), deshalb stoppt der ESP32 die Pumpe. Kein Kühlkörper. Zur Vorwarnung ein **NTC-Fühler mit
Ringöse unter der Befestigungsschraube, die den Transistoren am nächsten liegt** (festgelegt 07.10.2026): nichts
geklebt, beim Modultausch nur umsetzen; Anschluss über MSTBA 2,5/2, Spannungsteiler an einem freien Eingang des
Messwandlers (Abschnitt 3). **Typ: TDK B57703M0103A017** (10 kΩ ±2 %, B 3988 K, −55…+125 °C, 115 mm PTFE-Litze AWG 26;
DigiKey.de 3,29 €, Datenblatt Oktober 2025). Teiler: 12 kΩ 1 % von +3,3 V, Fühler nach Masse (0 °C → 2,44 V, 100 °C →
0,18 V, gerechnet). Pololu-Löcher 2,18 mm für M2 (zwei Stück); Öse vermutlich M3, dann mit M2-Unterlegscheibe klemmen.
Noch zu prüfen: Ösenmaß in der Maßzeichnung, welche Schraube den Transistoren am nächsten liegt.

*Verworfen:* RoboClaw (teuer, Firmware verschlossen); VNH5019 (100 % nicht zugesichert); IBT-2/BTS7960 trotz
Vorhandensein (belegte Entwurfs- und Fertigungsmängel); eigene Brücke (heikelste Baugruppe, ohne Vorteil).

## 2. Strommessung — **festgelegt 08.10.2026: eingebaute Messung des G2 und Hall-Sensor**

Der G2 meldet den Strom selbst: **10 mV je Ampere plus etwa 50 mV Versatz** am Ausgang CS, gelesen über den MCP3208
(Abschnitt 3). **An diesen Pin kein Kondensator** — der Treiber benutzt ihn selbst für seine Strombegrenzung.
Er misst nur, solange die Brücke treibt; bei zerhackter Ansteuerung zeigt er in den Bremspausen null. Wesentliches
geht dabei nicht verloren: Bei voller Ansteuerung treibt die Brücke ständig, in der Rampe teilt das Programm den
Mittelwert durch den Tastgrad, die Richtung steht im Befehl. Förderausfall (1,5 statt 5 A, also etwa 15 statt 50 mV
über dem Versatz; ein Wandlerschritt ist 0,61 mV) und Blockade (Begrenzung 15 A plus stehendes Ruder) bleiben erkennbar.
**Beleg:** Am 04.10. hat die eingebaute Messung des gekauften Controllers den Fehler gezeigt (1,1–1,9 A statt 5–6 A);
gefehlt haben die Klemmenspannung und eine Auswertung, nicht ein zweiter Sensor.
**Am echten Modul einmal messen:** Ist der Versatz stabil? Wie schnell folgt die Messung einer Anlaufspitze?

**Zusätzlich auf unserer Platine** (Betreiber, 08.10.2026): Hall-Sensor **ACS758LCB-050B-PFF-T** (±50 A, 40 mV/A
bei 5 V, Farnell 1791392) im Weg der Pumpenader A (Pololu OUTA → Klemme → Sensor → Pumpenklemme; in beiden Adern fließt
derselbe Strom). Beide Pumpenadern laufen ohnehin über unsere Platine (Abschnitt 1), der Sensor bringt keine zusätzliche
Klemme. **Er wird gleich bestückt** (Betreiber, 08.10.2026): Ein späterer Einbau hieße Löten an der Leistungsstrecke. Versorgung aus **5 V** (Elektronikzweig), weil der Hersteller ihn bei 5 V abgleicht
(Datenblatt: 3,0–5,5 V zulässig, abseits von 5 V zusätzlicher Fehler ohne Zahlenangabe); Ausgang über einen
Spannungsteiler 1:2 (2 × 10 kΩ, 1 %; ±50 A ergeben 0,25–2,25 V, gerechnet) auf Wandlerkanal CH4 (Abschnitt 3).

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
- **Acht Eingänge, fünf Messstellen:** Klemme A, Klemme B, Bordspannung, Stromrückmeldung der Endstufe
  (Abschnitt 2) und Temperatur der Endstufe (NTC, F11); ein Kanal für den Hall-Sensor (Abschnitt 2).
  Zwei Eingänge sind frei.
- **Steckbar im Sockel**, ohne Lötkolben tauschbar.
**Anschluss über Hardware-SPI, nicht nachgebildet in Software.** Der Wandler hält die Messspannung in einem
Kondensator von 20 pF, der während der Wandlung Ladung verliert; unter 10 000 Takten je Sekunde leidet die
Genauigkeit, **bei Wärme besonders**. Software-SPI stünde bei jeder Unterbrechung still — mit eingeschaltetem
WLAN ständig — und lieferte dann Werte, die nicht falsch aussehen, aber falsch sind.
Auflösung: ein Schritt ist 0,61 mV, also 61 mA an der Stromrückmeldung und 4 mV an den Klemmen — feiner als die
Unterschiede, um die es geht (1,3 A statt 5 A; 1,9 V statt 11 V).

**Messstellen:** je Stelle ein Spannungsteiler 100 kΩ / 18 kΩ, 1 % (16 V Bordspannung ergeben 2,44 V, unterhalb
der Referenz), dazu zwei Klemmdioden **BAT85** (Schottky, 30 V, 200 mA, DO-34; RS 0300978, Distrelec 30152079) nach
+3,3 V und Masse, je an Klemme A, B und Bordspannung (6 Stück); sie leiten ab etwa 3,6 V, der Wandler verträgt 3,9 V.
Bei einem Spannungsstoß von 100 V fließt durch den Vorwiderstand nur 1 mA. Sperrstrom wächst mit der Wärme: kleiner
Fehler der Bordspannung, notfalls im Programm ausgleichen. **Die Glättung ist je Kanal verschieden:** Klemmenspannungen mit ~10 ms, damit bei zerhackter Ansteuerung
der Mittelwert herauskommt (der Fall vom 04.10. — 1,9 V statt 11 V — wäre so sofort sichtbar); der Stromkanal
**ohne** diese Glättung, sonst verschenkt man die Spitzen.

*Verworfen:* ADS1115-Modul (nur 4 Eingänge und fest 860 Messungen je Sekunde — eine 2 ms kurze Spitze wird
verfehlt oder zufällig getroffen, und ein zufälliger Wert ist schlimmer als keiner, weil man ihn für den
Höchstwert hält); der Wandler im ESP32 (misst nicht geradlinig, nur 10–11 nutzbare Bit).

**Ein Widerstand mehr für den Selbsttest (S10):** 100 kΩ von einer Motorklemme nach Plus. Ohne ihn ziehen die
Messteiler die freien Klemmen in Ruhe nach Masse — „alles 0 V" wäre dann sowohl der gesunde Ruhezustand als auch
ein durchgebrannter unterer Schalter, ununterscheidbar. Mit dem Widerstand stellt sich in Ruhe eine mittlere,
berechenbare Spannung ein; 0 V oder volle Bordspannung heißt dann eindeutig: ein Schalter ist dauerhaft leitend.

## 4. RF300-Eingang (Zweidraht-Stromschnittstelle) — **festgelegt 07.10.2026, Versuch steht aus**

**Prinzip der alten RF300-Interfaceplatine, mit kleinerem Vorwiderstand** (Schaltplan `kicad/v00.01/RF300-Eingang`):
+12 V → **R1 220 Ω, 2 W** → RF+ → Geber → RF− → Masse. R1 speist den Geber, begrenzt bei Kurzschluss (~58 mA) und
macht die Stromsprünge sichtbar; **C1 100 nF + BC337** werten nur die Sprünge aus, die unbekannten Stromstufen spielen
keine Rolle. An der Klemme 10 nF; keine eigene TVS-Diode (Kabel höchstens 3 m, geschirmt, fern von Lichtmaschine und
Starter; Bordnetzspitzen fängt die 1.5KE20A ab). Gerechnet bei 12,73 V und 14 mA: Geber ~9,6 V (heute 6,89 V gemessen,
Robertson 10,8 V; eine Mindestspannung nennt kein Datenblatt); Dauerkurzschluss ~0,9 W in R1, daher 2 W.
**Fehlererkennung über die Frequenz:** kein Takt oder außerhalb 1600–5200 Hz = Störung (S2); welcher Fehler, klärt ein
Multimeter. Industriepraxis (NAMUR, EN 60947-5-6): Speisung über festen Widerstand, der zugleich schützt.
**Offen:** Reicht der Sprung bei 220 Ω (heute ~360–410 Ω)? Versuch an der alten Platine.

## 5. Rechner — **festgelegt 04.10.2026**

**ESP32-DevKitC-32E** (WROOM-32E, Antenne als Leiterbahn auf dem Modul,
<https://www.mouser.de/ProductDetail/356-ESP32-DEVKITC32E>), ~12 €, Industrie-Ausführung −40…+85 °C,
Stiftleisten, zwei Rechenkerne.
- **Zähler in Hardware** (PCNT): Er zählt die RF300-Impulse ohne Zutun des Rechenwerks; die Frequenz steht nach
  jedem Messfenster sofort bereit, ohne Mittelung über 30 Messungen wie heute. Das ist F4.
- **Zwei Rechenkerne:** einer misst, der andere regelt und redet — die Messung stockt nicht, während Daten
  übertragen werden.
- **Anschlüsse mit Reserve:** gebraucht werden rund 20 (Wandler 4, Display 3 und Beleuchtung 1, zwei serielle
  Strecken 3, Endstufe 4, Frequenzeingang 1, drei Leuchtdioden, ein Taster), vorhanden sind etwa 30. Belegung im
  Schaltplanblatt `Rechner`, geprüft gegen Espressif (keine Startanschlüsse an der Pumpe, Taster nur abfragen).
- **WLAN für die Fernprogrammierung** (F12). Zwei Auflagen an den Platinenentwurf, damit die Antenne auf dem
  Modul genügt: Das Modul sitzt **an der Kante unserer Platine, die Antenne ragt darüber hinaus**; darunter und
  daneben kein Kupfer, keine Bauteile. Alles Metallische (Leistungsmodul, Klemmen, dicke Kabel)
  kommt ans andere Ende. Der Kunststoff des Gehäuses stört den Funk nicht, nahes Metall dagegen sehr.
- **Rückweg, falls der Funk im Motorraum nicht reicht:** Die Ausführung **-32UE**
  (<https://www.digikey.de/de/products/detail/espressif-systems/ESP32-DEVKITC-32UE/12091813>) hat dieselbe
  Platine und Anschlussbelegung, aber statt der Leiterbahn eine Buchse für eine äußere Antenne. Weil das Modul
  in einer Buchsenleiste steckt, ist der Wechsel Steckarbeit — die Platine bleibt unverändert.
- Versorgung aus unserem eigenen Regler statt über USB. **Seine 3,3-V-Logik bestimmt die Betriebsspannung des
  Wandlers** (Abschnitt 3).

*Verworfen:* Arduino Nano (zu langsam, zu wenige Schnittstellen),
Teensy 4.1 (mehr als nötig).

## 6. Datenverbindung — **festgelegt 08.10.2026**

**MAX3488E (3,3 V, DIP-8), je Strecke einer, direkt am Rechner** — Datenblatt <https://www.analog.com/en/products/max3488e.html>.
Die Familie (MAX488E/MAX3488E) steckt bereits zweimal auf der vorhandenen Platine
`1-tinypilot/autopilot/hardware/kicad/PyPilot_Main_RS422`: U6 für die Strecke zum Motor-Controller, U7 für die Ruderlage, beide an
3,3 V, je ein Abschlusswiderstand am Empfangspaar (bei uns 2 × 120 Ω, 1 %, 0,25 W, wie R25/R26 der
RF300-Interfaceplatine) — an Bord erprobt und beschaffbar. Eigenschaften: Vollduplex
(getrennte Sende- und Empfangsadern, keine Umschaltung in Software), 250 kbit/s bei weichen Flanken (wenig
Störstrahlung), Treiber kurzschluss- und übertemperaturfest, Empfänger mit Fail-Safe (Kabelbruch ergibt sicheren
Ruhepegel statt Zeichensalat), ±15 kV Schutz gegen statische Entladung.
**Die Ruderlage läuft schon heute differentiell über RS422** (Stecker J3, Pins 5–8), nicht einadrig.

**Zwei getrennte Strecken:** eine zum TinyPilot, eine für die Ruderlage. Nur so hält F5 — die Anzeige am
Steuerstand läuft weiter, wenn die Verbindung zum TinyPilot ausfällt. Ein Schaltplanblatt (`kicad/v00.01/RS422-Strecke`),
zweimal eingesetzt; bei der Ruderlage bleibt der Empfänger frei.

*Verworfen:* galvanische Trennung (Lichtkoppler 6N137 und Trennwandler TMA 0505S) — der TinyPilot hängt nur am
Motor-Controller und bekommt von ihm auch die 5 V; die Massen sind über das Kabel ohnehin verbunden (Betreiber, 08.10.2026).

## 7. Versorgung und Schutz — **festgelegt 04.10.2026**

- **Zwei getrennte Regler, beide Recom R-78B5.0-2.0** (F13): SIP-3, 5 V / 2 A, Eingang **6,5–32 V**, kurzschlussfest, −40…+70 °C ohne Abschlag, verträgt keine
  Verpolung (Datenblatt REV 5/2021, <https://www.recom-power.com/pdf/Innoline/R-78B-2.0.pdf>). Gleicher Typ in beiden
  Zweigen: ein Ersatzteil passt überall, ein Schaltplanblatt (`kicad/v00.01/5V-Zweig`, zweimal eingesetzt), Reserve
  für Sendespitzen des ESP32. 3,3 V liefert das ESP32-Modul selbst.
  **Teile je 5-V-Zweig** (Drahtbauteile): Regler R-78B5.0-2.0; Sicherung 2 A träge 5 × 20 mm im Schurter-Halter OG/OGN
  (Händler noch prüfen); rote Leuchtdiode 3 mm mit 4,7 kΩ parallel zur Sicherung; Filter nach Herstellervorschlag:
  10 µF (2 × KEMET C320C475K5R5TA, 4,7 µF 50 V X7R) – Drossel **Bourns RLB0914-100KL** (10 µH, 2,7 A, RS 8118799;
  Zweig zieht am Eingang höchstens ~1,6 A bei 7 V, gerechnet) – 4,7 µF (C320C475K5R5TA). *Verworfen:* Traco TSR 1-2450 für die
  Elektronik (billiger, aber zweiter Typ und zweites Schaltplanblatt, nur 1 A).
  Der Eingangsbereich entscheidet, nicht die Stromstärke: Beim Anlassen des Diesels bricht die Bordspannung
  kurz ein — ein Regler, der erst ab 10 V arbeitet (z. B. Traco TSR 3-2450 mit 3 A), ließe den Pi neu starten.
  Getrennte Regler heißen auch: Ein Kurzschluss im Steuerhaus nimmt die Ruderlagen-Ausgabe nicht mit (F5, S6).
  Zum Steuerstand gehen 5 V über das **vorhandene Kabel** (Festlegung des Betreibers 07.10.2026); im Steuerstand
  ist kein Platz für einen eigenen Regler. Der Zweig versorgt in Phase 3 auch den SuAnPilot.
- **Schutz gegen Überspannung aus dem Bordnetz: Schutzdiode 1.5KE20A**, unidirektional, 1500 W, DO-201,
  Drahtform, unter 1 € (<https://www.digikey.de/de/products/detail/littelfuse-inc/1-5KE20A/688017>), direkt
  an der Eingangsklemme. Keine Drossel am Geräteeingang (müsste 15 A tragen; die 5-V-Zweige filtern selbst). An der
  Endstufe Elko **Panasonic EEU-FR1V102** (1000 µF, 35 V, 105 °C, 10 000 h, Ø 12,5 × 20 mm; Farnell 2508152) auf
  unserer Platine, nicht auf dem Modul, angeschlossen über zwei Stifte an den Pololu-Lötpunkten „+" (VM) und „−"
  (Abschnitt 1): hinter dem Verpolschutz des Pololu. Pololu: „at least a few hundred µF", auf dem Modul nur 3 × 150 µF.
  **Die Spannungsklasse ist durch zwei Grenzen eingeklemmt, 20 V ist die einzige dazwischen:** Nach unten darf
  sie im Betrieb nicht leiten — die Lichtmaschine lädt bis 15 V, diese Diode sperrt bis **17,1 V**. Nach oben
  muss sie unter der Grenze der Endstufe klemmen — der G2 verträgt **30 V**, diese Diode klemmt bei **27,7 V**.
  Die einfache Ausführung genügt; im Gleichspannungsnetz klemmt sie schärfer als eine bidirektionale.
  **Wogegen sie schützt:** Im Alltag gegen Schaltspitzen anderer Verbraucher (Ankerwinde, Bugstrahlruder,
  Kompressor, eigene Pumpe) — die hält sie mühelos aus. Im seltenen Fall gegen den **Lastabwurf**: Reißt bei
  laufendem Motor die Verbindung zur Batterie, liefert die Lichtmaschine noch 100–400 ms weiter, weil ihr
  Erregerfeld nicht schlagartig zusammenbricht; die Spannung steigt auf etwa 35 V, bei Maschinen ohne eigene
  Begrenzung auf über 100 V. **Ehrlich dazu:** Für ein so langes Ereignis ist die Diode nicht ausgelegt. Sie
  stirbt dann, fast immer als Kurzschluss — und die Sicherung im Schiff fällt. Das ist ihr Wert: Sie macht aus einem
  Totalschaden einen Wechsel von Diode und Sicherung für zwei Euro.
- **Verpolschutz nur für den Elektronikzweig: Schottky-Diode Vishay SB540-E3/54 in Reihe** (5 A, 40 V, DO-201AD;
  Farnell 9550399, RS 7000915; 5 A, weil beide Zweige bei 7 V zusammen über 3 A ziehen können). Ein Bauteil; Verlust typisch 0,4–0,5 V, die Regler arbeiten damit bis etwa 7 V Bordspannung.
  Beleg: Mit der Silizium-Diode der alten Interfaceplatine ist der TinyPilot in allen Feldversuchen nie neu gestartet
  (Betreiber, 07.10.2026); die Schottky-Diode verliert weniger. *Verworfen:* P-Kanal-MOSFET (nicht nötig). Der G2 bringt
  seinen eigenen Verpolschutz mit — damit entfällt ein Bauteil im Hochstrompfad.
- **Zwei Sicherungen auf der Platine:** Elektronik 2 A, TinyPilot-Zweig 2 A (F13). Die Leistung sichert die vorhandene
  **20-A-Sicherung im Schiff** (Leitung 2,5 mm²), deshalb keine eigene (Betreiber, 08.10.2026). Die **Strombegrenzung der
  Endstufe auf 15 A** bleibt, damit zuerst die Elektronik begrenzt und erst danach diese Sicherung fällt.
- **Rote Leuchtdiode „Sicherung durch"**, mit Widerstand **parallel zur Sicherung**: Ist die Sicherung heil,
  liegt über ihr keine Spannung und die Diode bleibt dunkel; ist sie durch, fließt ein kleiner Strom über die
  Diode zur Last und sie leuchtet. Zwei Bauteile, und man sucht nicht stundenlang.

## 8. Anzeige und Leuchtdioden — **festgelegt 08.10.2026**

**Grafik-LCD 128 × 64 mit Steuerbaustein ST7920**, Modul mit Stiftleiste, 3,3 V, SPI; beim Betreiber in anderen
Projekten bewährt (Unterlagen: `E:\Users\SuAn\Cloud\My Computer\Hardware\Displays\ST7920 based 128x64 LCD`). Zeigt immer
**Ruderwinkel, Status und Fehlertext**. Beleuchtung immer an und gedimmt, bei Störung hell; der ESP32 stellt die
Helligkeit über einen Transistor. Gelb-grüne Ausführung (bei Umgebungslicht lesbar). Temperaturbereich steht in den
Unterlagen nicht — beim Kauf prüfen.
**Sieben Leuchtdioden** — sie fallen nicht aus wie ein Display:
- vom Rechner: grün „Betrieb" (blinkt im Programmtakt; Dauerlicht oder dunkel = Programm hängt), **rot „Störung"**,
  blau „WLAN an" (F12). Je ein Transistor BC337 schaltet sie aus +5 V: Grün und Blau brauchen ca. 3 V, mehr als ein
  3,3-V-Anschluss sicher liefert; Vorwiderstände für ca. 9–11 mA (gerechnet), an die gekauften Leuchtdioden anpassen;
- ohne Rechner: zwei gelbe „A" und „B", gegeneinander mit Vorwiderstand an den Pumpenklemmen auf unserer
  Platine (Abschnitt 1). Sie zeigen, was an der Pumpe ankommt, nicht was befohlen ist; schwach heißt zu wenig Spannung (Fall
  04.10.). Mit dem Selbsttest-Widerstand (Abschnitt 3) stellt sich in Ruhe A ca. 5 V, B ca. 3 V ein (gerechnet); die
  gelbe Leuchtdiode A glimmt dabei kaum sichtbar (ca. 30 µA, gerechnet);
- je 5-V-Zweig rot „Sicherung durch" (Abschnitt 7), leuchtet auch bei totem Gerät.
**Warnausgang:** rote Leuchtdiode, Fehlertext im Display, Meldung an den TinyPilot mit Anzeige dort und am Leitstand.
Kein Summer.
**Ein Taster mit zwei Aufgaben:** Beleuchtung hell und WLAN wieder einschalten (F12). **Leiterplattentaster Omron
B3F-4055** mit Kappe Typ B32 (12 × 12 mm, Drahtbauteil, 1 Mio. Schaltspiele, −25…+70 °C; Bürklin 13G7563, Mouser,
LCSC C84931), aufgelötet. Ob er von außen durch eine nachgiebige Stelle im Deckel bedient wird oder bei geöffnetem
Gehäuse, wird später entschieden (Abschnitt 10).
*Verworfen:* OLED 0,96" (zu klein für Ruderwinkel und Status, brennt bei Daueranzeige ein); blaue LCD-Ausführung
(ohne Beleuchtung unlesbar).

## 9. Leiterplatte, Klemmen, Gehäuse — Vorschlag

- **Hohe Ströme gehören nicht auf eine selbst entworfene Leiterbahn** (Praxiswert: 20 mm breite Außenbahn mit
  105 µm Kupfer wird bei etwa 70 A um 58 K wärmer). Leistungspfad als aufgelötete Kupferschiene oder dicker
  blanker Draht; Wege Eingangsklemme → Klemme zum Pololu und Klemme vom Pololu → Hall-Sensor → Pumpenklemme so kurz
  wie möglich.
- **Klemmen für die vier kurzen Leitungen zum Pololu: Degson DG301-5.0-02P** (festgelegt 08.10.2026), fest eingelötet,
  baugleich zu den Pololu-Klemmen (Pololu Nr. 2440, ohne Maße und 3D-Modell); 5,0 mm, IEC 17,5 A / 250 V, Leiter
  0,75–1,5 mm², Höhe 10,0 mm; Datenblatt und 3D-Modell über LCSC C5371917. Eine Kontaktstelle weniger als steckbar.
- **Alle Klemmen wie auf der RF300-Interfaceplatine: Phoenix Contact MSTBA 2,5/…-G-5,08** (festgelegt 07.10.2026):
  Stiftleiste liegend auf der Platine, dazu steckbarer Schraubstecker MSTB 2,5/…-ST-5,08; Raster 5,08 mm, 12 A je
  Kontakt, 320 V, Leiter bis 2,5 mm² (z. B. 2-polig: Stiftleiste 1757242, Stecker 1757019). Gilt auch für die
  12-V-Zuleitung und die Klemmen zum Pololu: 12 A sind ein Dauerwert; im Betrieb fließen 4–6 A (Spitze 8,3 A), die
  15 A der Begrenzung nur kurz bis zur Abschaltung (F6). Die Pumpe wird an unserer Platine angeschlossen (Abschnitt 1). *Verworfen:* eigene Leistungsklemmen 7,62 mm (zweiter Typ, im Normalbetrieb nicht nötig).
- **Gehäuse 3D-Druck: ASA**, ersatzweise Polycarbonat; **PLA scheidet aus** (erweicht bei 55–60 °C), PETG ist
  grenzwertig. **Nur mechanischer Schutz, nicht dicht.** Lüftungsschlitze über den Transistoren des
  Pololu (Abschnitt 1).
- **Wärmeabfuhr:** kein Kühlkörper; das Modul trägt 25 A ohne Kühlkörper, die Pumpe zieht 4–6 A. Temperaturfühler
  an der Endstufe siehe Abschnitt 1 (F11).
- **Durchführungen in der Gehäusewand:** Taster, sieben Leuchtdioden (Abschnitt 8), Display, Kabel mit
  Zugentlastung. Für eine spätere Antennenbuchse wird eine Stelle vorbereitet; gebraucht wird sie nur, falls der Funk
  aus dem Motorraum nicht reicht.
- **Anschlüsse nach außen:** 12 V (2,5 mm², Sicherung 20 A im Schiff) an unserer Platine, Pumpe A/B an unserer Platine (MSTBA 2,5/2); RF300 zweiadrig geschirmt;
  zum Steuerhaus **das vorhandene Kabel, unverändert** (8 Adern: grün Stellbefehle, orange Meldungen, braun
  NMEA-Ruderlage, weiß Minus, blau frei; dazu rot/schwarz für 5 V, F13). **Stecker und Belegung wie an der
  RF300-Interfaceplatine:** MSTBA 2,5/8 wie dort J9 (1–4 RS422 zum Motor-Controller A+, B−, Z−, Y+; 5–8 RS422
  Ruderlage A+, B−, Z−, Y+), 5 V über MSTBA 2,5/2.

## 10. Offen — vor dem Kauf zu messen oder zu klären
1. RPU160: Anlauf- und Blockierstrom messen, und ob die Pumpe ein Überdruckventil hat. Beides entscheidet über
   Sicherung, Kupferquerschnitt, Kühlfläche — und darüber, wie sich ein Anschlag überhaupt bemerkbar macht.
2. Widerstandswert für die Strombegrenzung des G2 bei Pololu erfragen (Ziel 15 A).
3. Temperaturklasse der RS422-Treiber festlegen: 0…+70 °C oder −40…+85 °C. Für den Motorraum die Industrie-
   Ausführung. Welche heute im TinyPilot sitzt, steht im Schaltplan nicht.
4. Genauigkeitsklasse der Referenz wählen: ±1 % (LM4040**D**IZ-2.5) reicht, ±0,1 % (LM4040**A**IZ-2.5) kostet
   kaum mehr. Die Klasse bestimmt den Fehler aller Spannungs- und Strommessungen gleichermaßen.
5. Wann darf der Selbsttest (S10) laufen? Am Steg bewegt sich das Ruder gefahrlos, im engen Fahrwasser nicht.
6. **Funkprobe vor dem Platinenentwurf:** ein Handy oder anderes WLAN-Gerät an die künftige Einbaustelle im
   Motorraum legen und prüfen, ob es den Master erreicht und wie stark. Entscheidet über -32E oder -32UE.
7. Taster: von außen bedienbar (nachgiebige Stelle im Deckel) oder nur bei geöffnetem Gehäuse?
8. Buchsen- und Stiftleiste für den umgedrehten Pololu wählen: Abstand der Platinen größer als die Pololu-Klemmen
   (10,0 mm laut Degson-Datenblatt) plus Luft (Abschnitt 1). Ebenso die Buchsenleisten für ESP32 (2 × 19) und Display (20).
9. Leuchtdioden wählen (Farbe, Bauform, Fassung in der Gehäusewand); danach die Vorwiderstände (Abschnitt 8) anpassen.

## Quellen
**Die Bezugsquelle jedes Bauteils steht im jeweiligen Abschnitt.** Hier nur, was nicht an einem Bauteil hängt:
- Ladungspumpe, Strombegrenzung und Stromrückmeldung des G2: <https://www.pololu.com/product/2994/faqs>
- RS422-Treiber im Schiff verbaut: `1-tinypilot/autopilot/hardware/kicad/PyPilot_Main_RS422/PyPilot_Main.net` (U6, U7)
- Leiterbahnbreite hoher Ströme: <https://courses.fedevel.com/forum/other/high-current-tracepour>
- Neuer pypilot-Controller (4,5 oz Kupfer, Sicherungs-LED): <https://forum.openmarine.net/printthread.php?tid=2248>
- Heutiges Protokoll und Verkabelung: `1-tinypilot/motor-controller/hardware/konzeption/Motor_Controller_Fakten.md`
