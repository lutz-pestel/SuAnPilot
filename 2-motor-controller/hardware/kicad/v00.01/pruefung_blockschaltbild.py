# Prueft jeden Pfeil des Blockschaltbilds gegen die Netzliste von KiCad. Version 00.01, Stand 09.10.2026.
# Aufruf (KiCad geschlossen): kicad-cli sch export netlist --format kicadxml -o mc.xml Motor-Controller.kicad_sch
#                            python pruefung_blockschaltbild.py mc.xml   -> erwartet: 80 erfuellt, 0 nicht erfuellt
# Bauteilnamen (U601, R610 ...) gelten fuer den Plan v00.01; neue Verbindungen hier als Pruefpunkt ergaenzen.
import sys, xml.etree.ElementTree as E
sys.stdout.reconfigure(encoding='utf-8')
r = E.parse(sys.argv[1]).getroot()
net_of = {}
members = {}
for n in r.iter('net'):
    name = n.get('name')
    for x in n.iter('node'):
        key = x.get('ref') + '.' + x.get('pin')
        net_of[key] = name
        members.setdefault(name, set()).add(key)

ok = fail = 0


def same(text, *pins):
    global ok, fail
    nets = {net_of.get(p, '-') for p in pins}
    good = len(nets) == 1 and '-' not in nets
    ok += good; fail += not good
    print(('OK  ' if good else 'FEHLT') + '  ' + text + ('' if good else '   ' + str({p: net_of.get(p, '-') for p in pins})))


def apart(text, a, b):
    global ok, fail
    good = net_of.get(a) != net_of.get(b)
    ok += good; fail += not good
    print(('OK  ' if good else 'FEHLT') + '  ' + text)


print('--- Bordnetz-Eingang')
same('J2.1 12 V an Schutzdiode D1 (Kathode) und Verpolschutz D2 (Anode) = +12V_LEISTUNG', 'J2.1', 'D1.1', 'D2.2')
same('J2.2 Minus an Masse, Anode D1', 'J2.2', 'D1.2', 'U601.14')
same('+12V hinter D2 an beide 5-V-Zweige, RF300-Speisung, Selbsttest', 'D2.1', 'F101.1', 'F201.1', 'R1.1', 'R301.1')
print('--- Endstufe (Pololu)')
same('+12V_LEISTUNG über J3/W1 an Pololu VIN', 'J3.1', 'W1.1', 'J2.1'); same('W1 an VIN', 'W1.2', 'U1.13')
same('Pololu GND über W2/J3 an Masse', 'U1.14', 'W2.2'); same('W2 an Masse', 'W2.1', 'J3.2', 'U601.14')
same('Elko C3 am Pololu-„+“ (VM hinter Verpolschutz)', 'C3.1', 'U1.11'); same('Elko an „−“', 'C3.2', 'U1.12')
apart('Pololu-„+“ nicht mit +12V verbunden', 'U1.11', 'D2.1')
same('Strombegrenzung R10 an VREF', 'R10.1', 'U1.10')
print('--- Pumpe (OUTA, OUTB, Hall-Sensor, Klemme J5)')
same('OUTA über W3 an J4.2', 'U1.15', 'W3.1'); same('J4.2 an Hall-Sensor IP+', 'W3.2', 'J4.2', 'U2.4')
same('Hall-Sensor IP− an Pumpenklemme J5.1 (KLEMME_A)', 'U2.5', 'J5.1')
same('OUTB über W4/J4.1 an Pumpenklemme J5.2 (KLEMME_B)', 'U1.16', 'W4.1'); same('W4 an J5.2', 'W4.2', 'J4.1', 'J5.2')
same('Hall-Sensor Versorgung +5V', 'U2.1', 'U601.19')
same('Gelbe LEDs: R12 an KLEMME_A', 'R12.1', 'J5.1'); same('Gelbe LEDs an KLEMME_B', 'D3.1', 'D4.2', 'J5.2')
print('--- Versorgung')
same('+5V Elektronik: Regler U101 an ESP32 5V, Hall-Sensor, LED-Zweige', 'U101.3', 'U601.19', 'U2.1', 'R603.1')
same('+5V_PYPILOT: Regler U201 an Klemme J8.1', 'U201.3', 'J8.1'); same('J8.2 Masse', 'J8.2', 'U601.14')
apart('+5V_PYPILOT getrennt von +5V Elektronik', 'U201.3', 'U101.3')
same('+3V3 vom ESP32 an Wandler, Referenz, RS422, RF300-Eingang, Display, FLT-Widerstand',
     'U601.1', 'U301.16', 'R311.1', 'U401.1', 'U501.1', 'R6.1', 'DS601.2', 'R11.1')
print('--- RF300 (Ruderlage)')
same('J1.1 RF+ an Vorwiderstand R1', 'J1.1', 'R1.2'); same('J1.2 RF− an Masse', 'J1.2', 'U601.14')
same('RF_TAKT vom Transistor Q3 an ESP32 IO35 (Zähler)', 'Q3.1', 'U601.6')
print('--- Ansteuerung Endstufe')
same('DIR: ESP32 IO25 an Pololu DIR', 'U601.9', 'U1.2'); same('PWM: ESP32 IO26 an Pololu PWM, R601 nach Masse', 'U601.10', 'U1.3', 'R601.1')
same('SLP: ESP32 IO27 an Pololu SLP', 'U601.11', 'U1.4'); same('FLT: Pololu an ESP32 IO34, R11 nach +3V3', 'U1.5', 'U601.5', 'R11.2')
print('--- Messwerterfassung')
same('Klemme A über Teiler an Wandler CH0', 'R302.1', 'J5.1'); same('CH0', 'R302.2', 'U301.1')
same('Klemme B über Teiler an Wandler CH1', 'R304.1', 'J5.2'); same('CH1', 'R304.2', 'U301.2')
same('Bordspannung (+12V_LEISTUNG) über Teiler an CH2', 'R306.1', 'J2.1'); same('CH2', 'R306.2', 'U301.3')
same('CS des Pololu an CH3', 'U1.6', 'U301.4')
same('Hall-Ausgang über Teiler an CH4', 'U2.3', 'R308.1'); same('CH4', 'R308.2', 'U301.5')
same('Temperaturfühler J6 an CH5', 'J6.1', 'U301.6', 'R310.2')
same('Selbsttest-Widerstand R301 an Klemme A', 'R301.2', 'J5.1')
same('Bezugsspannung LM4040 an Vref', 'U302.2', 'U301.15')
same('SPI Takt IO18', 'U601.28', 'U301.13'); same('SPI Daten vom Wandler IO19', 'U601.27', 'U301.12')
same('SPI Daten zum Wandler IO23', 'U601.21', 'U301.11'); same('SPI Auswahl IO5', 'U601.29', 'U301.10')
print('--- Verbindung zum Steuerhaus')
same('TinyPilot senden: ESP32 IO17 an U401 DI', 'U601.30', 'U401.3'); same('TinyPilot empfangen: U401 RO an IO16', 'U401.2', 'U601.31')
same('J7.1 A+', 'J7.1', 'U401.8'); same('J7.2 B−', 'J7.2', 'U401.7'); same('J7.3 Z−', 'J7.3', 'U401.6'); same('J7.4 Y+', 'J7.4', 'U401.5')
same('Abschluss 120 Ω TinyPilot', 'R401.1', 'U401.8'); same('Abschluss', 'R401.2', 'U401.7')
same('NMEA-Ruderlage: ESP32 IO32 an U501 DI', 'U601.7', 'U501.3')
same('J7.5 A+', 'J7.5', 'U501.8'); same('J7.6 B−', 'J7.6', 'U501.7'); same('J7.7 Z−', 'J7.7', 'U501.6'); same('J7.8 Y+', 'J7.8', 'U501.5')
apart('Ruderlage-Strecke unabhängig von der TinyPilot-Strecke', 'U501.5', 'U401.5')
print('--- Rechner und Bedienung')
same('Display Auswahl IO15', 'U601.35', 'DS601.4'); same('Display Daten IO13', 'U601.15', 'DS601.5'); same('Display Takt IO14', 'U601.12', 'DS601.6')
same('Display seriell: PSB an Masse', 'DS601.15', 'U601.14')
same('Beleuchtung: IO4 über R602 an Q601', 'U601.32', 'R602.1'); same('Q601 schaltet BLK', 'Q601.1', 'DS601.20')
same('Beleuchtung BLA über R610 220 Ω an +5V Elektronik', 'R610.1', 'U101.3'); same('R610 an BLA', 'R610.2', 'DS601.19')
same('grün Betrieb: IO21', 'U601.25', 'R604.1'); same('rot Störung: IO22', 'U601.22', 'R606.1'); same('blau WLAN: IO33', 'U601.8', 'R608.1')
same('LED grün am Transistor', 'D601.1', 'Q602.1'); same('LED rot am Transistor', 'D602.1', 'Q603.1'); same('LED blau am Transistor', 'D603.1', 'Q604.1')
same('Taster an IO36 mit 10k nach +3V3', 'SW601.2', 'U601.3', 'R609.2')
print('--- Sicherungs-LEDs der 5-V-Zweige')
same('LED D101 mit R101 parallel zur Sicherung F101', 'R101.1', 'F101.1'); same('D101 an Sicherungsausgang', 'D101.1', 'F101.2')
same('LED D201 mit R201 parallel zur Sicherung F201', 'R201.1', 'F201.1'); same('D201 an Sicherungsausgang', 'D201.1', 'F201.2')
print()
print('Prüfpunkte erfüllt: %d, nicht erfüllt: %d' % (ok, fail))
