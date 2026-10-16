# Prueft jede Verbindung des Blockschaltbilds 00.15 gegen die Netzliste von KiCad. Linie B (SMD). Version 00.04, Stand 16.10.2026.
# Gegen Linie A (smd/konzeption/Bauteilauswahl.md Regel 11): Klemmdioden BAT54S (Pin 1 A an Masse, Pin 3 Mitte am Messpunkt,
#   Pin 2 K an +3V3) statt 2 x BAT85; keine Sicherung F1 und keine Sicherungs-LED; Schutzdiode SMCJ18CA;
#   Filter 4,7 uF - R5 || R6 (je 1 Ohm) - L1 (Drahtbruecke) - 2 x 10 uF; Teiler 100 k / 13 k statt 18 k (bis ~21,7 V).
# Aufruf (KiCad geschlossen): kicad-cli sch export netlist --format kicadxml -o ra.xml Robnet-Analyse.kicad_sch
#                            python pruefung_blockschaltbild.py ra.xml   -> erwartet: 86 erfuellt, 0 nicht erfuellt
# Blaetter: Hauptblatt, Bus-Empfaenger, Rechner, Messung, Versorgung; Versorgung nur ueber Leitungen im Hauptblatt.
# Namen aus dem Blockschaltbild: J1 (J300), J2 (Versorgung), J3 (Bedieneinheit), J4, JP1-JP7, U1-U4, U6, R1, R2, F1, D1.
# Hier festgelegt (Blockschaltbild nennt sie nicht): J5 = Buchsenleiste des Zero (Pin = Zero-Pin);
#   JP2: 1 BUSP_J, 2 BUSN_J, 3 Bus+ gewaehlt, 4 Bus- gewaehlt, 5 BUSP_B, 6 BUSN_B (Jumper 1-3/2-4 = J300, 3-5/4-6 = Bedieneinheit);
#   JP1: 1 und 6 von R1, 2 und 5 von R2, 3 an A, 4 an B (Jumper 1-3/2-4 = gerade, 3-5/4-6 = gekreuzt).
# Teiler, Dioden und Kondensatoren werden ueber Netz und Wert gefunden, nicht ueber ihren Namen.
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
value = {c.get('ref'): (c.findtext('value') or '') for c in r.iter('comp')}

ok = fail = 0
GND, V33, V5 = 'J1.4', 'J5.1', 'J5.2'          # Bezugspins: Masse (Vsys-), +3V3 und +5V vom Zero
V12F = 'D1.1'                                    # Kathode Verpolschutz = +12V_F


def report(good, text, detail=''):
    global ok, fail
    ok += good; fail += not good
    print(('OK  ' if good else 'FEHLT') + '  ' + text + ('' if good else '   ' + detail))


def ohm(v):
    # '100k 1%' -> 100000, '8k2' -> 8200, '4u7 50V' -> 4.7e-6
    s = v.split()[0].replace(',', '.') if v.split() else ''
    mult = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, 'k': 1e3, 'K': 1e3, 'M': 1e6, 'R': 1}
    for ch, f in mult.items():
        if ch in s:
            a, _, b = s.partition(ch)
            b = ''.join(x for x in b if x.isdigit())       # '10uH' -> b = ''
            try:
                return float((a or '0') + '.' + b if b else a) * f
            except ValueError:
                return None
    try:
        return float(s)
    except ValueError:
        return None


def parts(prefix, a, b, val=None):
    # Zweipolige Teile mit Namensanfang prefix zwischen den Netzen von a und b; bei Dioden/LED: Pin 1 (K) an a
    na, nb = net_of.get(a), net_of.get(b)
    found = []
    for ref, v in value.items():
        if not ref.startswith(prefix) or not ref[len(prefix):].isdigit():
            continue
        p1, p2 = net_of.get(ref + '.1'), net_of.get(ref + '.2')
        if prefix == 'D':
            hit = (p1, p2) == (na, nb)
        else:
            hit = {p1, p2} == {na, nb} and na != nb
        if isinstance(val, str):
            hit = hit and val in v
        elif val is not None:
            hit = hit and ohm(v) is not None and abs(ohm(v) - val) <= val * 1e-6
        if hit:
            found.append(ref)
    return found


def same(text, *pins):
    nets = {net_of.get(p, '-') for p in pins}
    report(len(nets) == 1 and '-' not in nets, text, str({p: net_of.get(p, '-') for p in pins}))


def apart(text, a, b):
    report(a in net_of and b in net_of and net_of[a] != net_of[b], text)


def free(text, *pins):
    bad = [p for p in pins if p not in net_of or len(members[net_of[p]]) != 1]
    report(not bad, text, 'verbunden oder fehlt: ' + ', '.join(bad))


def between(text, prefix, a, b, val=None, count=1):
    f = parts(prefix, a, b, val)
    report(len(f) >= count, text, 'gefunden: %s' % f)


def bat54s(node):
    # BAT54S mit Pin 3 am Messpunkt, Pin 1 an Masse, Pin 2 an +3V3
    n = net_of.get(node)
    return [d for d, v in value.items() if d.startswith('D') and 'BAT54S' in v and net_of.get(d + '.3') == n
            and net_of.get(d + '.1') == net_of.get(GND) and net_of.get(d + '.2') == net_of.get(V33)]


def teiler(text, src, adc, top, bottom, smooth_ok=True):
    # Teiler src -> top -> ADC-Eingang -> bottom -> GND, BAT85 nach +3V3 und nach GND; Bus ohne Kondensator
    miss = []
    if not parts('R', src, adc, top): miss.append('R oben %g' % top)
    if not parts('R', adc, GND, bottom): miss.append('R unten %g' % bottom)
    if not bat54s(adc): miss.append('BAT54S (Masse - Messpunkt - +3V3)')
    if not smooth_ok and parts('C', adc, GND): miss.append('Kondensator vorhanden (Bus ohne Glättung)')
    report(not miss, text, ', '.join(miss))


print('--- Zwischenstecker und Jumper (J1 = Kabel zum J300, J3 = Buchse Bedieneinheit)')
for pin, ader, jp in (('2', 'Bus+', 'JP3'), ('1', 'Bus−', 'JP4'), ('3', 'Vsys+', 'JP5'), ('5', 'On-Off', 'JP6'), ('6', 'Alarm', 'JP7')):
    same('%s: J1.%s an %s Pin 1' % (ader, pin, jp), 'J1.' + pin, jp + '.1')
    same('%s: %s Pin 2 an J3.%s' % (ader, jp, pin), jp + '.2', 'J3.' + pin)
    apart('%s: ohne Jumper getrennt (J1.%s nicht an J3.%s)' % (ader, pin, pin), 'J1.' + pin, 'J3.' + pin)
same('Vsys− durchgehend: J1.4 an J3.4 = Masse', 'J1.4', 'J3.4')
print('--- Messpunkte J4')
same('J4.1 an BUSP_J', 'J4.1', 'J1.2'); same('J4.2 an BUSN_J', 'J4.2', 'J1.1'); same('J4.3 an Masse', 'J4.3', GND)
print('--- Bus-Empfänger U1 MAX3488 mit Seitenwahl JP2 und Kreuzung JP1')
same('JP2.1 an BUSP_J', 'JP2.1', 'J1.2'); same('JP2.2 an BUSN_J', 'JP2.2', 'J1.1')
same('JP2.5 an BUSP_B', 'JP2.5', 'J3.2'); same('JP2.6 an BUSN_B', 'JP2.6', 'J3.1')
between('R1 1 kΩ von JP2.3 (Bus+ gewählt) an JP1.1', 'R', 'JP2.3', 'JP1.1', 1e3)
between('R2 1 kΩ von JP2.4 (Bus− gewählt) an JP1.2', 'R', 'JP2.4', 'JP1.2', 1e3)
same('JP1.6 = JP1.1 (Bus+ für die Kreuzung)', 'JP1.6', 'JP1.1'); same('JP1.5 = JP1.2 (Bus− für die Kreuzung)', 'JP1.5', 'JP1.2')
same('JP1.3 an U1.8 (A)', 'JP1.3', 'U1.8'); same('JP1.4 an U1.7 (B)', 'JP1.4', 'U1.7')
apart('A und B nicht verbunden', 'U1.8', 'U1.7')
same('U1.1 VCC und U1.3 DI an +3V3', 'U1.1', 'U1.3', V33); same('U1.4 GND', 'U1.4', GND)
free('Sendeausgänge U1.5 Y und U1.6 Z offen (sonst sendet er)', 'U1.5', 'U1.6')
same('U1.2 RO an Zero Pin 10 (GPIO15 RXD) und Pin 16 (GPIO23)', 'U1.2', 'J5.10', 'J5.16')
free('Zero Pin 8 (GPIO14 TXD) frei', 'J5.8')
print('--- Wandler U2 (CE0), Seite J300')
teiler('CH0 ← BUSP_J 100k/13k, ohne Glättung', 'J1.2', 'U2.1', 100e3, 13e3, False)
teiler('CH1 ← BUSN_J 100k/13k, ohne Glättung', 'J1.1', 'U2.2', 100e3, 13e3, False)
teiler('CH2 ← VSYS_J 100k/8,2k', 'J1.3', 'U2.3', 100e3, 8.2e3)
teiler('CH3 ← ONOFF_J 100k/13k', 'J1.5', 'U2.4', 100e3, 13e3)
teiler('CH4 ← ALARM_J 100k/13k', 'J1.6', 'U2.5', 100e3, 13e3)
teiler('CH5 ← +12V_F 100k/13k (Bordspannung)', V12F, 'U2.6', 100e3, 13e3)
free('CH6, CH7 frei', 'U2.7', 'U2.8')
print('--- Wandler U6 (CE1), Seite Bedieneinheit')
teiler('CH0 ← VSYS_B 100k/8,2k', 'J3.3', 'U6.1', 100e3, 8.2e3)
teiler('CH1 ← ONOFF_B 100k/13k', 'J3.5', 'U6.2', 100e3, 13e3)
teiler('CH2 ← ALARM_B 100k/13k', 'J3.6', 'U6.3', 100e3, 13e3)
teiler('CH3 ← BUSP_B 100k/13k, ohne Glättung', 'J3.2', 'U6.4', 100e3, 13e3, False)
teiler('CH4 ← BUSN_B 100k/13k, ohne Glättung', 'J3.1', 'U6.5', 100e3, 13e3, False)
free('CH5–CH7 frei', 'U6.6', 'U6.7', 'U6.8')
print('--- Wandler gemeinsam: Versorgung, Referenz U4, SPI 0')
same('VDD U2.16, U6.16 an +3V3', 'U2.16', 'U6.16', V33)
same('DGND/AGND U2.9, U2.14, U6.9, U6.14 an Masse', 'U2.9', 'U2.14', 'U6.9', 'U6.14', GND)
same('VREF U2.15 = U6.15 = LM4040 U4.2 (K)', 'U2.15', 'U6.15', 'U4.2'); same('U4.3 (A) an Masse', 'U4.3', GND)
between('Vorwiderstand der Referenz von +3V3 an VREF', 'R', V33, 'U4.2')
apart('VREF nicht an +3V3', 'U4.2', V33)
same('SCLK Zero Pin 23 an CLK U2.13, U6.13', 'J5.23', 'U2.13', 'U6.13')
same('MOSI Zero Pin 19 an Din U2.11, U6.11', 'J5.19', 'U2.11', 'U6.11')
same('MISO Zero Pin 21 an Dout U2.12, U6.12', 'J5.21', 'U2.12', 'U6.12')
same('CE0 Zero Pin 24 an CS U2.10', 'J5.24', 'U2.10'); same('CE1 Zero Pin 26 an CS U6.10', 'J5.26', 'U6.10')
apart('CS der beiden Wandler getrennt', 'U2.10', 'U6.10')
between('100 nF an +3V3 (U1, U2, U6): mindestens 3', 'C', V33, GND, 100e-9, 3)
print('--- Alarm an den Zero')
between('ALARM_J über 100k an Zero Pin 13 (GPIO27)', 'R', 'J1.6', 'J5.13', 100e3)
between('Pin 13 über 180k an Masse', 'R', 'J5.13', GND, 180e3)
report(bool(bat54s('J5.13')), 'BAT54S an Pin 13 (nach +3V3 und Masse)')
print('--- Versorgung')
same('J2.1 +12 V direkt an Anode Verpolschutz D1 (keine Sicherung)', 'J2.1', 'D1.2'); same('J2.2 an Masse', 'J2.2', GND)
report(not [x for x in value if x.startswith('F') and x[1:].isdigit()], 'keine Sicherung auf der Platine')
between('Schutzdiode SMCJ18CA an +12V_F gegen Masse', 'D', V12F, GND, 'SMCJ18CA')
between('Filter: 4,7 µF an +12V_F', 'C', V12F, GND, 4.7e-6)
between('Filter: 2 × 1 Ω parallel von +12V_F an L1', 'R', V12F, 'L1.1', 1.0, 2)
same('L1 (Drahtbrücke, Platz für Drossel) an Regler-Eingang U3.1', 'L1.2', 'U3.1')
between('Filter: 2 × 10 µF am Regler-Eingang', 'C', 'U3.1', GND, 10e-6, 2)
same('U3.2 an Masse', 'U3.2', GND); same('U3.3 +5V an Zero Pin 2 und 4', 'U3.3', 'J5.2', 'J5.4')
same('+3V3 vom Zero: Pin 1 und 17', 'J5.1', 'J5.17')
same('Zero-Masse Pin 6, 9, 14, 20, 25, 30, 34, 39', 'J5.6', 'J5.9', 'J5.14', 'J5.20', 'J5.25', 'J5.30', 'J5.34', 'J5.39', GND)
apart('+5V nicht an +3V3', V5, V33)
report(not [x for x in value if x.startswith('D') and 'LED' in value[x].upper() or value[x].startswith('rot')],
       'keine Sicherungs-LED (entfällt mit der Sicherung)')
print('--- Versorgungswege über das Hauptblatt (Unterblätter nur mit blattlokalen Versorgungszeichen)')
same('+12V_F: Verpolschutz D1 an Filter R5, R6 und Messkanal CH5 (R21)', 'D1.1', 'R5.1', 'R6.1', 'R21.1')
same('+3V3 vom Zero an Empfänger U1, beide Wandler und Referenz-Vorwiderstand', 'J5.1', 'U1.1', 'U2.16', 'U6.16', 'R4.1')
same('Masse aller Blätter: J1, J2, Regler, Empfänger, Zero, Wandler, Referenz', 'J1.4', 'J2.2', 'U3.2', 'U1.4', 'J5.6', 'U2.9', 'U6.9', 'U4.3')
apart('+5V nicht an +12V gesichert', 'U3.3', 'D1.1')
print('--- Nicht aus Vsys versorgen, Robnet nicht belasten')
apart('Platinenversorgung nicht an Vsys+ (J300)', 'J2.1', 'J1.3'); apart('+12V_F nicht an Vsys+ (J300)', V12F, 'J1.3')
apart('+12V_F nicht an Vsys+ (Bedieneinheit)', V12F, 'J3.3')
for p, ader in (('2', 'Bus+'), ('1', 'Bus−')):
    refs = {m.split('.')[0] for m in members.get(net_of.get('J1.' + p), ())}
    stray = [x for x in refs if x[0] in 'RC' and x[1:].isdigit() and ohm(value.get(x, '')) != 100e3]
    report('J1.' + p in net_of and not stray, '%s Seite J300: kein Abschluss- oder Glättungsteil' % ader, 'zusätzlich: %s' % stray)
print()
print('Prüfpunkte erfüllt: %d, nicht erfüllt: %d' % (ok, fail))
