# Unterblaetter Robnet-Analyse v00.01: Versorgung, Bus-Empfaenger, Rechner, Messung. Version 00.02, Stand 15.10.2026.
from kgen import Sheet

FP_R = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
FP_BAT = 'Diode_THT:D_DO-34_SOD68_P7.62mm_Horizontal'
FP_C100N = 'Robnet-Analyse:C_KEMET_C320_L5.1mm_W4.1mm_P2.54mm'
FP_C4U7 = 'Robnet-Analyse:C_TDK_FG16_L5.5mm_W3.5mm_P2.50mm'
_flg = [1]


def flag(s, x, y, rot=0):
    _flg[0] += 1
    return s.sym('power:PWR_FLAG', '#FLG%02d' % _flg[0], 'PWR_FLAG', x, y, rot, hide_value=True)


def res_h(s, ref, val, x, y):
    # Widerstand waagrecht, Pin 1 links (x-3,81), Pin 2 rechts
    return s.sym('Device:R', ref, val, x, y, 90, fp=FP_R, fields={'Reference': (x, y - 2.54, None), 'Value': (x, y + 2.54, None)})


def res_v(s, ref, val, x, y, side='right'):
    # Widerstand senkrecht, Pin 1 oben (y-3,81)
    dx, j = (2.54, 'left') if side == 'right' else (-2.54, 'right')
    return s.sym('Device:R', ref, val, x, y, 0, fp=FP_R, fields={'Reference': (x + dx, y - 1.27, j), 'Value': (x + dx, y + 1.27, j)})


def dio_v(s, lib, ref, val, x, y, fp, side='right'):
    # Diode senkrecht, Kathode (Pin 1) oben
    dx, j = (2.54, 'left') if side == 'right' else (-2.54, 'right')
    return s.sym(lib, ref, val, x, y, 270, fp=fp, fields={'Reference': (x + dx, y - 1.27, j), 'Value': (x + dx, y + 1.27, j)})


def cap_v(s, ref, val, x, y, fp, side='right'):
    dx, j = (2.54, 'left') if side == 'right' else (-2.54, 'right')
    return s.sym('Device:C', ref, val, x, y, 0, fp=fp, fields={'Reference': (x + dx, y - 1.27, j), 'Value': (x + dx, y + 1.27, j)})


# ======================================================================= Versorgung (A4)
def versorgung(path):
    s = Sheet('Versorgung', 'Versorgung.kicad_sch', 'Robnet-Analyse – Versorgung', paper='A4', path=path)
    Y, G = 76.2, 101.6
    s.frame(15.24, 40.64, 182.88, 111.76, 'Versorgung: Robertson-Bordnetz 12 V → Sicherung → Verpolschutz → Filter → 5 V für den Zero')
    s.hlabel('+12V_EIN', 30.48, Y, 'input', 180)
    f1 = s.sym('Device:Fuse', 'F1', '1A T', 44.45, Y, 90, fp='Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open',
               fields={'Reference': (44.45, Y + 2.54, None), 'Value': (44.45, Y + 5.08, None)})
    s.wire((30.48, Y), (35.56, Y), f1.pin(1)); s.junction(35.56, Y)
    # Sicherungs-LED: R3 und D3 parallel zur Sicherung, leuchtet, wenn F1 durch ist
    r3 = res_h(s, 'R3', '4k7 1%', 41.91, 63.5)
    d3 = s.sym('Device:LED', 'D3', 'rot 3 mm', 52.07, 63.5, 180, fp='LED_THT:LED_D3.0mm',
               fields={'Reference': (52.07, 60.96, None), 'Value': (52.07, 58.42, None)})
    s.wire((35.56, Y), (35.56, 63.5), r3.pin(1)); s.wire(r3.pin(2), d3.pin(2))
    s.wire(d3.pin(1), (55.88, 63.5), (55.88, Y)); s.junction(55.88, Y)
    d1 = s.sym('Device:D_Schottky', 'D1', 'SB540', 64.77, Y, 180, fp='Diode_THT:D_DO-201AD_P15.24mm_Horizontal',
               fields={'Reference': (64.77, Y - 3.81, None), 'Value': (64.77, Y + 3.81, None)})
    s.wire(f1.pin(2), (55.88, Y), d1.pin(2))
    # +12V_F: hinter dem Verpolschutz, Messkanal Bordspannung
    s.wire(d1.pin(1), (73.66, Y)); s.junction(73.66, Y)
    s.wire((73.66, Y), (73.66, 55.88)); s.hlabel('+12V_F', 73.66, 55.88, 'output', 90)
    d2 = dio_v(s, 'Diode:1.5KExxA', 'D2', '1.5KE20A', 78.74, 87.63, 'Diode_THT:D_DO-201AE_P15.24mm_Horizontal', 'left')
    c4 = cap_v(s, 'C4', '4u7 50V', 91.44, 87.63, FP_C4U7)
    c5 = cap_v(s, 'C5', '4u7 50V', 104.14, 87.63, FP_C4U7)
    l1 = s.sym('Device:L', 'L1', '10uH', 118.11, Y, 90, fp='Inductor_THT:L_Radial_D10.0mm_P5.00mm_Fastron_07P',
               fields={'Reference': (118.11, Y - 2.54, None), 'Value': (118.11, Y + 2.54, None)})
    c6 = cap_v(s, 'C6', '4u7 50V', 129.54, 87.63, FP_C4U7)
    u3 = s.sym('Converter_DCDC:R-78B5.0-2.0', 'U3', 'R-78B5.0-2.0', 147.32, Y, fp='Converter_DCDC:Converter_DCDC_RECOM_R-78B-2.0_THT',
               fields={'Reference': (147.32, Y - 7.62, None), 'Value': (147.32, Y - 5.08, None)})
    s.wire((73.66, Y), (78.74, Y), (91.44, Y), (104.14, Y), l1.pin(1))
    for x in (78.74, 91.44, 104.14):
        s.junction(x, Y)
    s.wire((78.74, Y), d2.pin(1)); s.wire((91.44, Y), c4.pin(1)); s.wire((104.14, Y), c5.pin(1))
    s.wire(l1.pin(2), (129.54, Y), (134.62, Y), u3.pin(1)); s.junction(129.54, Y); s.wire((129.54, Y), c6.pin(1))
    flag(s, 134.62, Y)          # Regler-Eingang: Netz wird nur ueber L1 gespeist
    # Masse-Schiene
    for p in (d2.pin(2), c4.pin(2), c5.pin(2), c6.pin(2)):
        s.wire(p, (p[0], G))
        if p[0] != 78.74:
            s.junction(p[0], G)
    s.wire((78.74, G), (91.44, G), (104.14, G), (129.54, G), (147.32, G))
    s.wire(u3.pin(2), (147.32, G)); s.junction(147.32, G)
    s.wire((147.32, G), (162.56, G)); s.hlabel('GND', 162.56, G, 'passive', 0)
    s.wire(u3.pin(3), (162.56, Y)); s.hlabel('+5V', 162.56, Y, 'output', 0)
    s.text('F1: Sicherung 1 A träge, 5 × 20 mm, Halter Schurter OGN 0031.8201. D3 mit R3 leuchtet, wenn F1 durch ist.\n'
           'D1: Verpolschutz SB540 (Schottky 40 V / 5 A). D2: Schutzdiode 1.5KE20A gegen Spannungsspitzen.\n'
           'Filter wie Motor-Controller: 2 × 4,7 µF – 10 µH (Bourns RLB0914-100KL) – 4,7 µF (TDK FG16X7R1H475KRT06, 50 V X7R).\n'
           'U3: Recom R-78B5.0-2.0, Eingang 6,5–32 V, 5 V / 2 A für den Zero (Pin 2/4). Nicht aus Vsys versorgen.\n'
           'Blattanschlüsse: +12V_EIN von J2, +12V_F zur Messung (Bordspannung), +5V zum Zero, GND.',
           17.78, 127.0)
    return s


# ======================================================================= Bus-Empfaenger (A4)
def power_entry(s, x, y, kinds):
    # Versorgung des Blatts: je Netz ein Blattanschluss, dahinter das blattlokale Versorgungszeichen
    for i, kind in enumerate(kinds):
        yy = y + 5.08 * i
        s.hlabel(kind, x, yy, 'input' if kind != 'GND' else 'passive', 180)
        s.wire((x, yy), (x + 7.62, yy)); s.lpower(kind, x + 7.62, yy)


def empfaenger(path):
    s = Sheet('Empfaenger', 'Bus-Empfaenger.kicad_sch', 'Robnet-Analyse – Bus-Empfänger', paper='A4', path=path)
    Y = 76.2
    s.frame(12.7, 45.72, 195.58, 142.24, 'Bus-Empfänger: liest nur, sendet nie')
    jp2 = s.sym('Robnet-Analyse:Jumper_2x3_Seitenwahl', 'JP2', 'Seitenwahl', 50.8, Y, fp='Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical',
                fields={'Reference': (50.8, Y - 10.16, None), 'Value': (50.8, Y + 10.16, None)})
    for name, n in (('BUSP_J', 1), ('BUSN_J', 2), ('BUSP_B', 5), ('BUSN_B', 6)):
        p = jp2.pin(n); s.hlabel(name, 25.4, p[1], 'input', 180); s.wire((25.4, p[1]), p)
    r1 = res_h(s, 'R1', '1k 1%', 72.39, jp2.pin(3)[1])
    r2 = res_h(s, 'R2', '1k 1%', 72.39, jp2.pin(4)[1])
    s.wire(jp2.pin(3), r1.pin(1)); s.wire(jp2.pin(4), r2.pin(1))
    jp1 = s.sym('Robnet-Analyse:Jumper_2x3_Kreuzung', 'JP1', 'Kreuzung', 96.52, Y, fp='Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical',
                fields={'Reference': (96.52, Y - 12.7, None), 'Value': (96.52, Y + 12.7, None)})
    # Bus+ an JP1.6 und JP1.1, Bus- an JP1.2 und JP1.5
    s.wire(r1.pin(2), (81.28, r1.pin(2)[1]), jp1.pin(6)); s.junction(81.28, jp1.pin(6)[1])
    s.wire((81.28, jp1.pin(6)[1]), (81.28, jp1.pin(1)[1]), jp1.pin(1))
    s.wire(r2.pin(2), (81.28, r2.pin(2)[1]), jp1.pin(2)); s.junction(81.28, jp1.pin(2)[1])
    s.wire((81.28, jp1.pin(2)[1]), (81.28, jp1.pin(5)[1]), jp1.pin(5))
    u1 = s.sym('Interface_UART:MAX3488xPA', 'U1', 'MAX3488EEPA', 129.54, Y + 2.54, mirror='y', fp='Package_DIP:DIP-8_W7.62mm_Socket',
               fields={'Reference': (121.92, Y - 12.7, None), 'Value': (119.38, Y + 20.32, None)})
    s.wire(jp1.pin(3), u1.pin(8))                                              # A
    s.wire(jp1.pin(4), (114.3, jp1.pin(4)[1]), (114.3, u1.pin(7)[1]), u1.pin(7))  # B
    s.no_connect(*u1.pin(5)); s.no_connect(*u1.pin(6))                         # Y, Z offen
    # Versorgung U1 mit 100 nF
    vcc = u1.pin(1)
    s.wire(vcc, (vcc[0], vcc[1] - 7.62)); s.lpower('+3V3', vcc[0], vcc[1] - 7.62)
    s.junction(vcc[0], vcc[1] - 5.08)
    c1 = cap_v(s, 'C1', '100n', 142.24, vcc[1] - 1.27, FP_C100N)
    s.wire((vcc[0], vcc[1] - 5.08), c1.pin(1)); s.lpower('GND', *c1.pin(2))
    s.wire(u1.pin(4), (u1.pin(4)[0], u1.pin(4)[1] + 2.54)); s.lpower('GND', u1.pin(4)[0], u1.pin(4)[1] + 2.54)
    di = u1.pin(3)
    s.wire(di, (di[0] + 7.62, di[1]), (di[0] + 7.62, di[1] - 2.54)); s.lpower('+3V3', di[0] + 7.62, di[1] - 2.54)
    ro = u1.pin(2)
    s.wire(ro, (160.02, ro[1])); s.hlabel('BUS_RX', 160.02, ro[1], 'output', 0)
    power_entry(s, 25.4, 127.0, ('+3V3', 'GND'))
    s.text('Versorgung vom Hauptblatt (3,3 V vom Zero)', 43.18, 129.54)
    s.text('JP2 Seitenwahl: 1-3 und 2-4 gesteckt = Seite J300 (_J),\n3-5 und 4-6 gesteckt = Seite Bedieneinheit (_B).', 15.24, 99.06)
    s.text('JP1: 1-3 und 2-4 = gerade (A = Bus+),\n3-5 und 4-6 = gekreuzt (A = Bus−).', 15.24, 106.68)
    s.text('U1 MAX3488 im Sockel, nur Empfänger: Y, Z offen,\nDI an 3,3 V. R1/R2 1 kΩ schützen die Eingänge.', 15.24, 114.3)
    s.text('empfangene Daten zum Zero\n(RXD und GPIO23)', 152.4, 80.01)
    return s


# ======================================================================= Rechner (A4)
def rechner(path):
    s = Sheet('Rechner', 'Rechner.kicad_sch', 'Robnet-Analyse – Rechner', paper='A4', path=path)
    px, py = 148.59, 101.6
    s.frame(78.74, 45.72, 215.9, 152.4, 'Rechner: Raspberry Pi Zero 2 W (aufgesteckt)')
    j5 = s.sym('Connector:Raspberry_Pi_2_3', 'J5', 'Raspberry Pi Zero 2 W', px, py,
               fp='Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical',
               fields={'Reference': (px, py - 36.83, None), 'Value': (px + 12.7, py + 35.56, None)})
    rx, ts = j5.pin(10), j5.pin(16)
    s.hlabel('BUS_RX', 101.6, rx[1], 'input', 180)
    s.wire((101.6, rx[1]), (111.76, rx[1]), rx); s.junction(111.76, rx[1])
    s.wire((111.76, rx[1]), (111.76, ts[1]), ts)
    a = j5.pin(13)
    s.hlabel('ALARM_ZERO', 101.6, a[1], 'input', 180); s.wire((101.6, a[1]), a)
    for name, n, shape in (('CE1', 26, 'output'), ('CE0', 24, 'output'), ('MISO', 21, 'input'), ('MOSI', 19, 'output'), ('SCLK', 23, 'output')):
        p = j5.pin(n)
        # Richtung aus Sicht des Blatts: der Zero treibt SCLK, MOSI, CE0, CE1 hinaus, MISO kommt herein
        s.hlabel(name, p[0] + 7.62, p[1], shape, 0); s.wire(p, (p[0] + 7.62, p[1]))
    t3, t5, gnd = j5.pin(1), j5.pin(2), j5.pin(6)
    s.wire(t5, (t5[0], t5[1] - 5.08)); s.hlabel('+5V', t5[0], t5[1] - 5.08, 'input', 90)
    s.wire(t3, (t3[0], t3[1] - 2.54), (t3[0], t3[1] - 5.08)); s.hlabel('+3V3', t3[0], t3[1] - 5.08, 'output', 90)
    s.junction(t3[0], t3[1] - 2.54)
    s.wire((t3[0], t3[1] - 2.54), (t3[0] + 5.08, t3[1] - 2.54)); flag(s, t3[0] + 5.08, t3[1] - 2.54)
    s.wire(gnd, (gnd[0], gnd[1] + 5.08)); s.hlabel('GND', gnd[0], gnd[1] + 5.08, 'passive', 270)
    used = {1, 2, 6, 10, 13, 16, 19, 21, 23, 24, 26}
    done = {j5.pin(n) for n in used}
    for n in range(1, 41):
        p = j5.pin(n)
        if n not in used and p not in done:
            s.no_connect(*p); done.add(p)
    s.text('+5V vom Regler (Blatt Versorgung) an Pin 2/4; +3V3 vom Zero (Pin 1/17) für Bus-Empfänger und Messung.\n'
           'BUS_RX an RXD (GPIO15, Telegramme) und GPIO23 (Zeitstempel, pigpio). GPIO27: Alarm.\n'
           'Netz über den Daten-USB des Zero. Nie zusätzlich über USB versorgen.', 81.28, 162.56)
    return s


# ======================================================================= Messung (A3)
LEFT = [('BUSP_J', '18k 1%', False), ('BUSN_J', '18k 1%', False), ('VSYS_J', '8k2 1%', True), ('ONOFF_J', '18k 1%', True),
        ('ALARM_J', '18k 1%', True), ('+12V_F', '18k 1%', True)]
RIGHT = [('VSYS_B', '8k2 1%', True), ('ONOFF_B', '18k 1%', True), ('ALARM_B', '18k 1%', True), ('BUSP_B', '18k 1%', False),
         ('BUSN_B', '18k 1%', False)]


def messung(path):
    s = Sheet('Messung', 'Messung.kicad_sch', 'Robnet-Analyse – Messung (Teiler, Wandler)', paper='A3', path=path)
    W = 421.64
    rows_l = [50.8, 81.28, 111.76, 142.24, 172.72, 233.68]
    rows_r = [50.8, 81.28, 111.76, 142.24, 172.72]
    YC = 127.0
    bend_l = [106.68, 101.6, 96.52, 96.52, 101.6, 106.68]
    bend_r = [106.68, 101.6, 96.52, 101.6, 106.68]
    s.frame(15.24, 27.94, 160.02, 254.0, 'Seite J300: Teiler und Wandler U2 (CE0)')
    s.frame(261.62, 27.94, 406.4, 190.5, 'Seite Bedieneinheit: Teiler und Wandler U6 (CE1)')
    s.frame(165.1, 71.12, 256.54, 157.48, 'Referenz 2,5 V und SPI')

    def mx(x, mirror):
        return W - x if mirror else x

    def channel(mirror, k, y, src, rb, smooth_ok, refs, adc_pin, bend):
        rt, rbo, du, dd = refs
        side_l = 'left' if not mirror else 'right'
        lx = mx(30.48, mirror)
        s.hlabel(src, lx, y, 'input', 180 if not mirror else 0)
        r_t = res_h(s, rt, '100k 1%', mx(50.8, mirror), y)
        pin_in, pin_out = (r_t.pin(1), r_t.pin(2)) if not mirror else (r_t.pin(2), r_t.pin(1))
        s.wire((lx, y), pin_in)
        xd, xr = mx(66.04, mirror), mx(76.2, mirror)
        d_up = dio_v(s, 'Diode:BAT85', du, 'BAT85', xd, y - 6.35, FP_BAT, 'left' if not mirror else 'right')
        d_dn = dio_v(s, 'Diode:BAT85', dd, 'BAT85', xd, y + 6.35, FP_BAT, 'left' if not mirror else 'right')
        r_b = res_v(s, rbo, rb, xr, y + 6.35, 'right' if not mirror else 'left')
        s.lpower('+3V3', *d_up.pin(1))
        s.wire(d_up.pin(2), (xd, y)); s.wire(d_dn.pin(1), (xd, y)); s.wire(r_b.pin(1), (xr, y))
        s.junction(xd, y); s.junction(xr, y)
        s.wire(d_dn.pin(2), r_b.pin(2)); s.lpower('GND', *r_b.pin(2))
        bx = mx(bend, mirror)
        s.wire(pin_out, (bx, y), (bx, adc_pin[1]), adc_pin)

    u2 = s.sym('Robnet-Analyse:MCP3208', 'U2', 'MCP3208-CI/P', 129.54, YC, fp='Package_DIP:DIP-16_W7.62mm_Socket',
               fields={'Reference': (119.38, YC - 16.51, None), 'Value': (119.38, YC - 13.97, None)})
    u6 = s.sym('Robnet-Analyse:MCP3208', 'U6', 'MCP3208-CI/P', W - 129.54, YC, mirror='y', fp='Package_DIP:DIP-16_W7.62mm_Socket',
               fields={'Reference': (W - 119.38, YC - 16.51, None), 'Value': (W - 119.38, YC - 13.97, None)})
    for k, (src, rb, sm) in enumerate(LEFT):
        channel(False, k, rows_l[k], src, rb, sm, ('R%d' % (11 + 2 * k), 'R%d' % (12 + 2 * k), 'D%d' % (11 + 2 * k), 'D%d' % (12 + 2 * k)),
                u2.pin(k + 1), bend_l[k])
    for k, (src, rb, sm) in enumerate(RIGHT):
        channel(True, k, rows_r[k], src, rb, sm, ('R%d' % (31 + 2 * k), 'R%d' % (32 + 2 * k), 'D%d' % (31 + 2 * k), 'D%d' % (32 + 2 * k)),
                u6.pin(k + 1), bend_r[k])
    for n in (7, 8):
        s.no_connect(*u2.pin(n))
    for n in (6, 7, 8):
        s.no_connect(*u6.pin(n))
    # Alarm an den Zero: ALARM_J -> 100k -> Knoten -> 180k -> GND, BAT85 nach +3V3
    ya, y4 = 203.2, rows_l[4]
    s.junction(38.1, y4); s.wire((38.1, y4), (38.1, ya))
    r23 = res_h(s, 'R23', '100k 1%', 50.8, ya)
    s.wire((38.1, ya), r23.pin(1))
    d23 = dio_v(s, 'Diode:BAT85', 'D23', 'BAT85', 66.04, ya - 6.35, FP_BAT, 'left')
    r24 = res_v(s, 'R24', '180k 1%', 76.2, ya + 6.35)
    s.lpower('+3V3', *d23.pin(1)); s.wire(d23.pin(2), (66.04, ya)); s.wire(r24.pin(1), (76.2, ya))
    s.junction(66.04, ya); s.junction(76.2, ya); s.lpower('GND', *r24.pin(2))
    s.wire(r23.pin(2), (83.82, ya)); s.hlabel('ALARM_ZERO', 83.82, ya, 'output', 0)
    # Versorgung der Wandler
    for u, xc, side in ((u2, 147.32, 'right'), (u6, W - 147.32, 'left')):
        vdd = u.pin(16)
        s.wire(vdd, (vdd[0], 104.14)); s.lpower('+3V3', vdd[0], 104.14)
        s.junction(vdd[0], 109.22)
        c = cap_v(s, 'C2' if u is u2 else 'C3', '100n', xc, 113.03, FP_C100N, side)
        s.wire((vdd[0], 109.22), c.pin(1)); s.lpower('GND', *c.pin(2))
        for n in (9, 14):
            p = u.pin(n); s.wire(p, (p[0], p[1] + 2.54)); s.lpower('GND', p[0], p[1] + 2.54)
    # Referenz VREF fuer beide Wandler
    v2, v6 = u2.pin(15), u6.pin(15)
    VR = 93.98
    u4 = s.sym('Robnet-Analyse:LM4040LP-2.5_3pin', 'U4', 'LM4040AIZ-2.5', 210.82, VR + 3.81, fp='Package_TO_SOT_THT:TO-92_Inline',
               fields={'Reference': (208.28, VR + 3.81, 'right'), 'Value': (208.28, VR + 6.35, 'right')})
    rr = res_v(s, 'R4', '1k 1%', 220.98, VR - 6.35)
    s.wire(v2, (v2[0], VR), (172.72, VR), (210.82, VR), (220.98, VR), (v6[0], VR), v6)
    for x in (210.82, 220.98):
        s.junction(x, VR)
    flag(s, 172.72, VR)
    s.wire(u4.pin(2), (210.82, VR)); s.wire(rr.pin(2), (220.98, VR))
    s.lpower('+3V3', *rr.pin(1)); s.lpower('GND', *u4.pin(3)); s.no_connect(*u4.pin(1))
    s.text('VREF 2,5 V', 175.26, VR - 1.27)
    power_entry(s, 226.06, 142.24, ('+3V3', 'GND'))
    s.text('Versorgung vom\nHauptblatt', 238.76, 146.05)
    # SPI: Takt, Daten in beide Richtungen von U2 nach U6 durchgehend
    clk, dout, din = u2.pin(13), u2.pin(12), u2.pin(11)
    s.wire(clk, (182.88, clk[1]), u6.pin(13)); s.junction(182.88, clk[1])
    s.wire(dout, (193.04, dout[1]), u6.pin(12)); s.junction(193.04, dout[1])
    s.wire(din, (203.2, din[1]), u6.pin(11)); s.junction(203.2, din[1])
    s.wire((182.88, clk[1]), (182.88, 116.84)); s.hlabel('SCLK', 182.88, 116.84, 'input', 90)
    s.wire((193.04, dout[1]), (193.04, 116.84)); s.hlabel('MISO', 193.04, 116.84, 'output', 90)
    s.wire((203.2, din[1]), (203.2, 142.24)); s.hlabel('MOSI', 203.2, 142.24, 'input', 270)
    cs2, cs6 = u2.pin(10), u6.pin(10)
    s.wire(cs2, (149.86, cs2[1]), (149.86, 142.24)); s.hlabel('CE0', 149.86, 142.24, 'input', 270)
    s.wire(cs6, (W - 149.86, cs6[1]), (W - 149.86, 142.24)); s.hlabel('CE1', W - 149.86, 142.24, 'input', 270)
    s.text('Teiler 100 k / 18 k (bis ~16 V), Vsys+ 100 k / 8,2 k (bis ~33 V), alle 1 % (Vishay MBB0207).\n'
           'Je Kanal zwei BAT85 nach +3,3 V und Masse. Bus-Kanäle ohne Glättung. Last je Ader ~118 kΩ.\n'
           'U2, U6 MCP3208 (12 Bit, Sockel), Referenz U4 LM4040 2,5 V für beide.\n'
           'Alarm an den Zero (GPIO27): ALARM_J über 100 k / 180 k, 4,8 V → ~3,1 V, BAT85 nach +3,3 V.', 165.1, 205.74)
    return s
