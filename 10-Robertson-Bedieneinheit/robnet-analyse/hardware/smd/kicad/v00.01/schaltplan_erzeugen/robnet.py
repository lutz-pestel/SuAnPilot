# Erzeugt den Schaltplan Robnet-Analyse Linie B (SMD) v00.01 (Hauptblatt, Unterblaetter, Projektbibliotheken). Version 00.04, Stand 16.10.2026.
# Kopie von Linie A (tht/kicad/v00.01/schaltplan_erzeugen), Aenderungen: smd/konzeption/Bauteilauswahl.md Regel 11.
# Aufruf (KiCad geschlossen), im Ordner schaltplan_erzeugen:  python robnet.py ..
# Danach: kicad-cli sch erc, Netzliste exportieren, python ../pruefung_blockschaltbild.py <netzliste.xml>.
# Aenderungen am Schaltplan hier vornehmen und neu erzeugen, nicht in KiCad (sonst gehen sie beim naechsten Lauf verloren).
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kgen, libs
kgen.LCSC.update({'100k 1%': 'C149504', '18k 1%': 'C17506', '8k2 1%': 'C17828', '180k 1%': 'C17501', '1k 1%': 'C17513',
                  '100n': 'C24497', 'BAT54S': 'C7420333', 'SS54': 'C22452', 'SMCJ18CA': 'C41411753', '4u7 50V': 'C29823',
                  '1R 1%': 'C17928', '10u 50V': 'C13585'})   # JLCPCB-Katalog 16.10.2026, smd/bom/bom.csv
from kgen import Sheet, uid, Q

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
libs.write(OUT)
kgen.PROJLIB['Robnet-Analyse'] = os.path.join(OUT, 'Robnet-Analyse.kicad_sym')
ROOT = uid('root')
main = Sheet('main', 'Robnet-Analyse.kicad_sch', 'Robnet-Analyse – Hauptblatt', root_uuid=ROOT, path='/' + ROOT)

FP6 = 'Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_6-G-5,08_1x06_P5.08mm_Horizontal'
FP2 = 'Connector_Phoenix_MSTB:PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal'
FPJ = 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'

# ---- Zeilen der sechs Adern (Reihenfolge wie Klemme 1-6)
ROWS = [60.96, 71.12, 81.28, 91.44, 101.6, 111.76]
NAMES = ['Bus−', 'Bus+', 'Vsys+', 'Vsys− (Masse)', 'On-Off', 'Alarm']
NET = ['BUSN', 'BUSP', 'VSYS', None, 'ONOFF', 'ALARM']
JP = {0: 'JP4', 1: 'JP3', 2: 'JP5', 4: 'JP6', 5: 'JP7'}
XM = 210.82                     # Mitte (Jumper)
XL_END, XR_END = 30.48, 421.64 - 30.48

main.frame(17.78, 40.64, 403.86, 139.7, 'Zwischenstecker: sechs Adern 1:1 durchgeschleift, fünf davon per Jumper trennbar')
main.text('Seite J300', 50.8, 50.8, 1.524, True)
main.text('Seite Bedieneinheit', 355.6, 50.8, 1.524, True)
main.text('Jumper gesteckt = 1:1 verbunden, gezogen = getrennt\n(nur im Hafen, nur durch den Betreiber)', 198.12, 50.8)

j1 = main.sym('Connector:Screw_Terminal_01x06', 'J1', 'MSTBA 6-pol.', 30.48, 85.09, mirror='y', fp=FP6,
              fields={'Reference': (30.48, 77.47, None), 'Value': (30.48, 97.79, None)})
j3 = main.sym('Connector:Screw_Terminal_01x06', 'J3', 'MSTBA 6-pol.', XR_END, 85.09, fp=FP6,
              fields={'Reference': (XR_END, 77.47, None), 'Value': (XR_END, 97.79, None)})
main.text('J1: Kabel mit\nStecker zum\nJ300', 20.32, 73.66, justify='left bottom')
main.text('J3: Buchse für\nden Stecker der\nBedieneinheit', 401.32, 73.66, justify='right bottom')

bend = [40.64, 43.18, 45.72, 45.72, 43.18, 40.64]
for k in range(6):
    pl, pr = j1.pin(k + 1), j3.pin(k + 1)
    xl, xr = bend[k], 421.64 - bend[k]
    main.wire(pl, (xl, pl[1]), (xl, ROWS[k]))
    main.wire(pr, (xr, pr[1]), (xr, ROWS[k]))
    main.text(NAMES[k], 48.26, ROWS[k] - 0.635)
    main.text(NAMES[k], 373.38, ROWS[k] - 0.635, justify='right bottom')
    if k in JP:
        jp = main.sym('Jumper:Jumper_2_Bridged', JP[k], 'Jumper', XM, ROWS[k], fp=FPJ, hide_value=True,
                      fields={'Reference': (XM, ROWS[k] - 2.54, None)})
        main.wire((xl, ROWS[k]), jp.pin(1)); main.wire(jp.pin(2), (xr, ROWS[k]))
    else:
        main.wire((xl, ROWS[k]), (xr, ROWS[k]))
# Masse: Vsys− durchgehend, an GND
main.wire((60.96, ROWS[3]), (60.96, 119.38)); main.junction(60.96, ROWS[3])
main.power('GND', 60.96, 119.38)
main.text('nie getrennt', 62.23, 118.11)

# ---- Abgriffe vor (J) und hinter (B) den Jumpern: senkrechte Leitungen nach unten
COLJ = {'BUSN': 96.52, 'BUSP': 91.44, 'VSYS': 86.36, 'ONOFF': 81.28, 'ALARM': 76.2}
ROWOF = {n: ROWS[i] for i, n in enumerate(NET) if n}

# ---- Unterblaetter: von oben nach unten Bus-Empfaenger, Rechner, Messung; Versorgung unten links bei J2
SX, SW = 116.84, 187.96
EMP_Y, RE_X, RE_Y, RE_W, RE_H, ME_Y, ME_H = 146.05, 160.02, 171.45, 101.6, 25.4, 207.01, 38.1
X3V3 = 271.78                   # 3,3-V-Leitung rechts neben dem Rechner: hoch zum Empfaenger, runter zur Messung
ORDER = ['BUSN', 'BUSP', 'VSYS', 'ONOFF', 'ALARM']
MESS_Y = [212.09, 217.17, 222.25, 227.33, 232.41]
SPI = [('SCLK', 180.34), ('MOSI', 190.5), ('MISO', 200.66), ('CE0', 210.82), ('CE1', 220.98), ('ALARM_ZERO', 231.14)]
X_RX = 190.5
emp_pins = [('BUSN_J', 'input', 'L', 5.08), ('BUSP_J', 'input', 'L', 10.16), ('BUSN_B', 'input', 'R', 5.08), ('BUSP_B', 'input', 'R', 10.16),
            ('BUS_RX', 'output', 'B', X_RX - SX), ('+3V3', 'input', 'B', X3V3 - SX), ('GND', 'passive', 'B', 124.46)]
ep, esu = main.subsheet('Bus-Empfänger', 'Bus-Empfaenger.kicad_sch', SX, EMP_Y, SW, 15.24, emp_pins)
rech_pins = [('BUS_RX', 'input', 'T', X_RX - RE_X), ('+5V', 'input', 'L', 7.62), ('GND', 'passive', 'L', 17.78),
             ('+3V3', 'output', 'R', 12.7)]
rech_pins += [(n, 'input' if n in ('MISO', 'ALARM_ZERO') else 'output', 'B', x - RE_X) for n, x in SPI]
rp, rsu = main.subsheet('Rechner', 'Rechner.kicad_sch', RE_X, RE_Y, RE_W, RE_H, rech_pins)
mess_pins = [(n + '_J', 'input', 'L', y - ME_Y) for n, y in zip(ORDER, MESS_Y)]
mess_pins += [(n + '_B', 'input', 'R', y - ME_Y) for n, y in zip(ORDER, MESS_Y)]
mess_pins += [('+12V_F', 'input', 'L', 33.02), ('GND', 'passive', 'B', 12.7), ('+3V3', 'input', 'T', X3V3 - SX)]
mess_pins += [(n, 'output' if n in ('MISO', 'ALARM_ZERO') else 'input', 'T', x - SX) for n, x in SPI]
mp, msu = main.subsheet('Messung (Teiler, Wandler)', 'Messung.kicad_sch', SX, ME_Y, SW, ME_H, mess_pins)
vp, vsu = main.subsheet('Versorgung', 'Versorgung.kicad_sch', 48.26, 228.6, 25.4, 20.32,
                        [('+12V_EIN', 'input', 'L', 5.08), ('+12V_F', 'output', 'R', 11.43), ('+5V', 'output', 'T', 12.7),
                         ('GND', 'passive', 'B', 12.7)])

# Abgriffe der Adern: senkrecht nach unten zur Messung, Bus-Adern zusaetzlich zum Empfaenger
for side in ('J', 'B'):
    for n in ORDER:
        x = COLJ[n] if side == 'J' else 421.64 - COLJ[n]
        ym = mp[n + '_' + side]
        main.wire((x, ROWOF[n]), (x, ym[1]), ym); main.junction(x, ROWOF[n])
        if n in ('BUSN', 'BUSP'):
            p = ep[n + '_' + side]
            main.wire((x, p[1]), p); main.junction(x, p[1])
# Daten: Empfaenger -> Rechner -> Messung
main.wire(ep['BUS_RX'], rp['BUS_RX'])
for n, _ in SPI:
    main.wire(rp[n], mp[n])

# ---- Messpunkte J4 (Bus+, Bus−, Masse), Seite J300
j4 = main.sym('Connector_Generic:Conn_01x03', 'J4', 'Messpunkte', 109.22, 124.46, fp='Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
              fields={'Reference': (106.68, 118.11, 'left'), 'Value': (106.68, 130.81, 'left')})
main.wire((COLJ['BUSP'], j4.pin(1)[1]), j4.pin(1)); main.junction(COLJ['BUSP'], j4.pin(1)[1])
main.wire((COLJ['BUSN'], j4.pin(2)[1]), j4.pin(2)); main.junction(COLJ['BUSN'], j4.pin(2)[1])
main.wire(j4.pin(3), (101.6, j4.pin(3)[1]), (101.6, 132.08)); main.power('GND', 101.6, 132.08)
main.text('Oszilloskop oder\nLogikanalysator', 114.3, 124.46, justify='left')

# ---- Versorgung: J2 -> Versorgung -> 12 V gesichert zur Messung, 5 V zum Rechner -> 3,3 V zu Empfaenger und Messung
j2 = main.sym('Connector:Screw_Terminal_01x02', 'J2', 'MSTBA 2-pol.', 30.48, 233.68, mirror='y', fp=FP2,
              fields={'Reference': (30.48, 229.87, None), 'Value': (30.48, 240.03, None)})
main.text('J2: Robertson-\nVersorgung +12 V', 20.32, 224.79)
main.wire(j2.pin(1), vp['+12V_EIN'])
main.wire(j2.pin(2), (38.1, j2.pin(2)[1]), (38.1, 243.84)); main.power('GND', 38.1, 243.84)
main.sym('power:PWR_FLAG', '#FLG01', 'PWR_FLAG', 38.1, j2.pin(2)[1], hide_value=True)
main.wire(vp['+12V_F'], mp['+12V_F'])
main.text('+12 V nach Verpolschutz', 78.74, mp['+12V_F'][1] - 1.27)
v5, r5 = vp['+5V'], rp['+5V']
main.wire(v5, (v5[0], r5[1]), r5)
main.text('+5 V', 104.14, r5[1] - 1.27)
r33, e33, m33 = rp['+3V3'], ep['+3V3'], mp['+3V3']
main.wire(r33, (X3V3, r33[1])); main.junction(X3V3, r33[1])
main.wire(e33, (X3V3, r33[1]), m33)
main.text('+3,3 V\nvom Zero', X3V3 + 1.27, r33[1] + 3.81)
for p in (vp['GND'], mp['GND'], ep['GND']):
    main.wire(p, (p[0], p[1] + 2.54)); main.power('GND', p[0], p[1] + 2.54)
g = rp['GND']
main.wire(g, (g[0] - 5.08, g[1]), (g[0] - 5.08, g[1] + 2.54)); main.power('GND', g[0] - 5.08, g[1] + 2.54)

# ---- Unterblaetter
import sheets
subs = [sheets.empfaenger('/' + ROOT + '/' + esu), sheets.rechner('/' + ROOT + '/' + rsu), sheets.messung('/' + ROOT + '/' + msu),
        sheets.versorgung('/' + ROOT + '/' + vsu)]
SHEETS = [[str(ROOT), 'Robnet-Analyse'], [str(esu), 'Bus-Empfänger'], [str(rsu), 'Rechner'], [str(msu), 'Messung (Teiler, Wandler)'],
          [str(vsu), 'Versorgung']]

os.makedirs(OUT, exist_ok=True)
main.write(OUT)
for s in subs:
    s.write(OUT)
pp = os.path.join(OUT, 'Robnet-Analyse.kicad_pro')
pro = json.load(open(pp, encoding='utf-8')) if os.path.exists(pp) else {'meta': {'filename': 'Robnet-Analyse.kicad_pro', 'version': 3}}
pro['sheets'] = SHEETS
json.dump(pro, open(pp, 'w', encoding='utf-8'), indent=2)
print('geschrieben nach', OUT)
