# Erzeugt die Platine Robnet-Analyse v00.01: Umriss, Bauteile mit Netzen, Befestigungsloecher, 3D-Modelle (keine Leiterbahnen). Version 00.02, Stand 16.10.2026.
# Aufruf mit dem Python von KiCad (KiCad geschlossen):
#   "C:/Program Files/KiCad/10.0/bin/python.exe" robnet_platine.py <netzliste.xml> <ziel.kicad_pcb>
# Netzliste vorher: kicad-cli sch export netlist --format kicadxml -o <netzliste.xml> ../Robnet-Analyse.kicad_sch
# Masse in mm, Ursprung oben links, y nach unten. Drehung in Grad gegen den Uhrzeigersinn (wie KiCad).
# Ein vorhandenes Board mit Leiterbahnen wird nicht ueberschrieben (Schutz der gezeichneten Bahnen).
import sys, os, json, xml.etree.ElementTree as ET
import pcbnew

NETZ, ZIEL = sys.argv[1], sys.argv[2]
if os.path.exists(ZIEL):
    alt = pcbnew.LoadBoard(ZIEL)
    assert len(alt.GetTracks()) == 0, 'Board hat Leiterbahnen - nicht ueberschreiben'
KI = 'C:/Program Files/KiCad/10.0/share/kicad/footprints/'
PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Robnet-Analyse.pretty')
if len(sys.argv) > 3:
    PROJ = sys.argv[3]

B, H = 100.0, 110.0                     # Platinengroesse

# ---------------------------------------------------------------- Lage der Bauteile: Ref -> (x, y, Drehung)
P = {}
# Steckverbinder an der oberen Kante, Oeffnung nach aussen (Drehung 180: Pin 1 rechts)
P['J1'] = (36.83, 10.16, 180)           # Kabel zum J300
P['J3'] = (71.12, 10.16, 180)           # Stecker der Bedieneinheit
P['J2'] = (87.63, 10.16, 180)           # +12 V Versorgung
# Trenn-Jumper unter den Steckern, Reihenfolge wie die Adern an J1/J3 (Alarm, On-Off, Vsys+, Bus+, Bus-)
JPX = 31.75                             # erster Jumper; Abstand 6,35 mm, damit Finger und Beschriftung Platz haben
ADERN = (('JP7', 'Alarm'), ('JP6', 'On-Off'), ('JP5', 'Vsys+'), ('JP3', 'Bus+'), ('JP4', 'Bus−'))
for i, (r, _) in enumerate(ADERN):
    P[r] = (JPX + 6.35 * i, 19.05, 0)
P['J4'] = (62.23, 19.05, 0)             # Messpunkte Bus+, Bus-, Masse
# Bus-Empfaenger oben links (ueber dem Zero)
P['JP2'] = (24.13, 19.05, 0)            # Seitenwahl
P['R1'] = (20.32, 19.05, 180)
P['R2'] = (20.32, 22.86, 180)
P['JP1'] = (3.81, 19.05, 0)             # gerade / gekreuzt
P['U1'] = (3.81, 30.48, 0)
P['C1'] = (16.51, 30.48, 0)
# Zero 2 W kopfueber, Ecke unten links: USB zur linken Kante, SD-Karte zur unteren Kante
P['J5'] = (25.83, H - 8.97, 180)
# Wandler: Kanaele rechts (zu den Teilern), SPI links (zum Zero)
P['U2'] = (43.18, 55.88, 180)
P['U6'] = (43.18, 97.79, 180)
P['C2'] = (34.29, 60.33, 0)
P['U4'] = (35.56, 66.04, 0)
P['R4'] = (43.18, 60.96, 270)
P['C3'] = (34.29, 102.87, 0)
# Versorgung, Spalte am rechten Rand, von oben (J2) nach unten
P['F1'] = (87.63, 17.78, 270)
P['R3'] = (80.01, 17.78, 270)
P['D3'] = (80.01, 33.02, 270)
P['D1'] = (88.90, 62.23, 90)
P['D2'] = (96.52, 46.99, 270)
P['L1'] = (80.01, 71.12, 0)
P['C4'] = (90.17, 67.31, 0)
P['C5'] = (90.17, 72.39, 0)
P['C6'] = (90.17, 77.47, 0)
P['U3'] = (83.82, 83.82, 0)

# Teiler: je Kanal vier Teile senkrecht nebeneinander (R zur Ader, R zur Masse, Diode nach 3,3 V, Diode nach Masse),
# der Mittelpunkt (Wandlereingang) liegt bei allen unten auf einer Linie.
KANAL = {  # Platz (Zeile, Spalte): (R_hoch, R_tief, D_hoch, D_tief)
    (0, 0): ('R21', 'R22', 'D21', 'D22'),   # U2 CH5 Bordspannung
    (0, 1): ('R19', 'R20', 'D19', 'D20'),   # U2 CH4 Alarm J300
    (1, 0): ('R17', 'R18', 'D17', 'D18'),   # U2 CH3 On-Off J300
    (1, 1): ('R15', 'R16', 'D15', 'D16'),   # U2 CH2 Vsys+ J300
    (2, 0): ('R13', 'R14', 'D13', 'D14'),   # U2 CH1 Bus- J300
    (2, 1): ('R11', 'R12', 'D11', 'D12'),   # U2 CH0 Bus+ J300
    (3, 0): ('R23', 'R24', 'D23', None),    # Alarm an den Zero
    (3, 1): ('R31', 'R32', 'D31', 'D32'),   # U6 CH0 Vsys+ Bedieneinheit
    (4, 0): ('R33', 'R34', 'D33', 'D34'),   # U6 CH1 On-Off
    (4, 1): ('R35', 'R36', 'D35', 'D36'),   # U6 CH2 Alarm
    (5, 0): ('R37', 'R38', 'D37', 'D38'),   # U6 CH3 Bus+
    (5, 1): ('R39', 'R40', 'D39', 'D40'),   # U6 CH4 Bus-
}
ZEILE_Y = [38.0 + 14.0 * z for z in range(6)]   # Unterkante (Mittelpunkt-Linie) je Zeile
SPALTE_X = [48.26, 63.50]
DX = (0.0, 3.81, 7.62, 11.43)                   # Abstand der vier Teile im Kanal
LOECHER = [(3.8, 3.8), (B - 3.8, 3.8), (B - 3.8, H - 3.8)]

# ---------------------------------------------------------------- Netzliste lesen
root = ET.parse(NETZ).getroot()
comps = {}
for c in root.iter('comp'):
    sp = c.find('sheetpath')
    felder = {f.get('name'): (f.text or '') for f in c.iter('field') if f.get('name') not in ('Footprint',)}
    comps[c.get('ref')] = dict(value=c.findtext('value'), fp=c.findtext('footprint'), felder=felder,
                               path=sp.get('tstamps') + c.findtext('tstamps'), sheet=sp.get('names'))
def netzname(n):
    # Schraegstriche in Pinnamen (z. B. SDA/GPIO2) fuehrt KiCad intern als {slash}; Blattpfade behalten '/'
    return n.replace('/', '{slash}') if n.startswith(('unconnected-(', 'Net-(')) else n

pinnet = {}
netnames = []
for n in root.iter('net'):
    netnames.append(netzname(n.get('name')))
    for nd in n.iter('node'):
        pinnet[(nd.get('ref'), nd.get('pin'))] = netzname(n.get('name'))

def knoten(ref):
    """Pin-Nummer, die am Teiler-Mittelpunkt haengt (Netz 'Net-(Dxx-A)' oder ALARM_ZERO)."""
    for pin in ('1', '2'):
        n = pinnet[(ref, pin)]
        if n.startswith('Net-(D') and n.endswith('-A)') or n.endswith('ALARM_ZERO'):
            return pin
    raise ValueError(ref)

# Teiler-Lagen aus dem Raster berechnen: Mittelpunkt-Pin unten
for (z, s), teile in KANAL.items():
    yb = ZEILE_Y[z]
    for k, ref in enumerate(teile):
        if ref is None:
            continue
        laenge = 10.16 if ref.startswith('R') else 7.62
        x = SPALTE_X[s] + DX[k]
        if knoten(ref) == '2':          # Pin 2 nach unten: Drehung 270, Pin 1 oben
            P[ref] = (x, yb - laenge, 270)
        else:                           # Pin 1 nach unten: Drehung 90, Pin 1 unten
            P[ref] = (x, yb, 90)

fehlt = sorted(set(comps) - set(P))
zuviel = sorted(set(P) - set(comps))
assert not fehlt and not zuviel, (fehlt, zuviel)

# ---------------------------------------------------------------- Platine aufbauen
board = pcbnew.BOARD()
board.SetCopperLayerCount(2)
nets = {}
for name in netnames:
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    nets[name] = ni

def mm(v):
    return pcbnew.FromMM(v)

def lade(fp):
    lib, name = fp.split(':')
    path = PROJ if lib == 'Robnet-Analyse' else KI + lib + '.pretty'
    f = pcbnew.FootprintLoad(path, name)
    assert f is not None, fp
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    return f

# 3D-Modelle aus hardware/3d-modelle (Liste und Herkunft: konzeption/Bauteilauswahl.md, Abschnitt 6). Gedrehte oder
# zusammengesetzte Teile liegen vorab in kicad-lage/ (erzeugt mit 3d-modelle/kicad_lage.py) und brauchen keine Drehung.
M3D = '${KIPRJMOD}/../../3d-modelle/'
MODELLE = {  # Bauform -> [(Datei, z-Versatz)]
    'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal': [('KiCad_R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.step', 0)],
    'D_DO-35_SOD27_P7.62mm_Horizontal': [('KiCad_D_DO-35_SOD27_P7.62mm_Horizontal.step', 0)],
    'D_DO-201AD_P15.24mm_Horizontal': [('KiCad_D_DO-201AD_P15.24mm_Horizontal.step', 0)],
    'D_DO-201_P15.24mm_Horizontal': [('KiCad_D_DO-201_P15.24mm_Horizontal.step', 0)],
    # IC im Sockel: Sockeloberkante 4,0 mm (KiCad-Sockelmodell 4,01; Mill-Max 4,19 ueber Platine)
    'DIP-8_W7.62mm_Socket': [('KiCad_DIP-8_W7.62mm_Socket.step', 0), ('KiCad_DIP-8_W7.62mm.step', 4.0)],
    'DIP-16_W7.62mm_Socket': [('KiCad_DIP-16_W7.62mm_Socket.step', 0), ('KiCad_DIP-16_W7.62mm.step', 4.0)],
    'TO-92_Inline': [('KiCad_TO-92_Inline.step', 0)],
    'Converter_DCDC_RECOM_R-78B-2.0_THT': [('KiCad_Converter_DCDC_RECOM_R-78B-2.0_THT.step', 0)],
    'Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open': [
        ('KiCad_Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open.step', 0), ('kicad-lage/Schurter_0034.3117_im_Halter.step', 0)],
    'L_Radial_D10.0mm_P5.00mm_Fastron_07P': [('kicad-lage/Bourns_RLB0914-100KL.step', 0)],
    'LED_D3.0mm': [('KiCad_LED_D3.0mm.step', 0)],
    'PinHeader_1x02_P2.54mm_Vertical': [('KiCad_PinHeader_1x02_P2.54mm_Vertical.step', 0), ('kicad-lage/Harwin_M7566-05_auf_1x02.step', 0)],
    'PinHeader_1x03_P2.54mm_Vertical': [('KiCad_PinHeader_1x03_P2.54mm_Vertical.step', 0)],
    'PinHeader_2x03_P2.54mm_Vertical': [('KiCad_PinHeader_2x03_P2.54mm_Vertical.step', 0), ('kicad-lage/Harwin_M7566-05_2x_auf_2x03_oben.step', 0)],
    'PhoenixContact_MSTBA_2,5_6-G-5,08_1x06_P5.08mm_Horizontal': [('kicad-lage/J_MSTBA-6-G_mit_MSTB-6-ST.step', 0)],
    'PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal': [('kicad-lage/J_MSTBA-2-G_mit_MSTB-2-ST.step', 0)],
    'C_KEMET_C320_L5.1mm_W4.1mm_P2.54mm': [('KEMET_C320C104K5R5TA_eigen.step', 0)],
    'C_TDK_FG16_L5.5mm_W3.5mm_P2.50mm': [('TDK_FG16X7R1H475KRT06_eigen.step', 0)],
    'Raspberry_Pi_Zero_kopfueber': [('KiCad_PinSocket_2x20_P2.54mm_Vertical.step', 0), ('kicad-lage/Zero2W_Baugruppe_kopfueber.step', 0)],
}

def modelle(f):
    name = f.GetFPID().GetLibItemName().wx_str()
    f.Models().clear()
    for datei, dz in MODELLE.get(name, []):
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = M3D + datei
        m.m_Offset = pcbnew.VECTOR3D(0, 0, dz)
        m.m_Show = True
        f.Models().push_back(m)
    return name in MODELLE

ohne_modell = []
for ref, c in sorted(comps.items()):
    f = lade(c['fp'])
    if not modelle(f):
        ohne_modell.append(ref)
    f.SetReference(ref)
    f.SetValue(c['value'])
    for name, wert in c['felder'].items():
        if name not in ('Value',):
            f.SetField(name, wert)
            f.GetField(name).SetVisible(False)
    f.SetPath(pcbnew.KIID_PATH(c['path']))
    f.SetSheetname(c['sheet'])
    x, y, rot = P[ref]
    f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    f.SetOrientationDegrees(rot)
    for pad in f.Pads():
        n = pinnet.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(nets[n])
    board.Add(f)

for i, (x, y) in enumerate(LOECHER, 1):
    f = lade('MountingHole:MountingHole_3.2mm_M3')
    f.SetReference('H%d' % i)
    f.SetValue('M3')
    f.SetBoardOnly(True)
    f.Models().clear()                          # Loch ohne Modell
    f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    board.Add(f)

# ---------------------------------------------------------------- Beschriftung (Aufdruck oben)
def text(s, x, y, groesse=1.0, winkel=0, links=False):
    tx = pcbnew.PCB_TEXT(board)
    tx.SetText(s)
    tx.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    tx.SetLayer(pcbnew.F_SilkS)
    tx.SetTextSize(pcbnew.VECTOR2I(mm(groesse * 0.8), mm(groesse)))
    tx.SetTextThickness(mm(0.15))
    tx.SetTextAngleDegrees(winkel)
    if links:
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(tx)

def feld(f, x, y, winkel=0, groesse=1.0, breite=0.8):
    r = f.Reference()
    r.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    r.SetTextAngleDegrees(winkel)
    r.SetTextSize(pcbnew.VECTOR2I(mm(groesse * breite), mm(groesse)))
    r.SetTextThickness(mm(0.15))

ADERNAME = ('Bus−', 'Bus+', 'Vsys+', 'Masse', 'On-Off', 'Alarm')        # Klemme 1-6 an J1 und J3
ZEILE_A, ZEILE_B, ZEILE_C = 14.2, 15.9, 24.9
for ref in ('J1', 'J3'):
    x1 = P[ref][0]
    for k, nm in enumerate(ADERNAME):
        text(nm, x1 - 5.08 * k, ZEILE_A)
text('+12 V', P['J2'][0], ZEILE_A)
text('Masse', P['J2'][0] - 5.08, ZEILE_A)
text('J1: zum J300', 9.0, ZEILE_B, links=True)
text('J3: Bedieneinheit', 64.5, ZEILE_B, links=True)
text('J2', P['J2'][0] + 3.0, ZEILE_B)
for r, nm in ADERN:
    text(nm, P[r][0], ZEILE_C)
text('gesteckt = verbunden', JPX - 1.8, 26.4, groesse=1.0, links=True)
for k, nm in enumerate(('Bus+', 'Bus−', 'Masse')):
    text(nm, P['J4'][0] + 1.9, P['J4'][1] + 2.54 * k, groesse=1.0, links=True)
for i, s in enumerate(('JP1 oben: gerade', 'JP1 unten: gekreuzt', 'JP2 oben: J300', 'JP2 unten: Bedieneinh.')):
    text(s, 14.0, 34.4 + 1.8 * i, groesse=1.0, links=True)
text('Robnet-Analyse v00.01', 89.0, 94.0)

for f in board.GetFootprints():
    ref = f.GetReference()
    if ref in dict(ADERN) or ref == 'J4':       # senkrecht links neben dem Jumper, getrennt von den Pinnamen der Stecker
        feld(f, P[ref][0] - 2.4, P[ref][1] + 1.27, 90)
    elif ref in ('J1', 'J3', 'J2'):
        f.Reference().SetVisible(False)          # Name steht in der Beschriftung
    elif ref[0] == 'H':
        f.Reference().SetVisible(False)
    elif ref in ('C2', 'C3', 'U4'):              # links neben dem Teil, zwischen Zero und Wandler
        feld(f, 32.0, P[ref][1], 90)
    elif ref in ('C4', 'C5', 'C6'):
        feld(f, P[ref][0] + 6.0, P[ref][1])
    elif ref == 'D3':
        feld(f, P[ref][0], 39.0)
    elif ref in ('R1', 'R2', 'R3', 'R4', 'D1', 'D2') or (ref[0] in 'RD' and ref[1:].isdigit() and int(ref[1:]) >= 11):
        pads = list(f.Pads())
        x = sum(pcbnew.ToMM(p.GetPosition().x) for p in pads) / 2
        y = sum(pcbnew.ToMM(p.GetPosition().y) for p in pads) / 2
        w = 90 if abs(f.GetOrientationDegrees()) % 180 == 90 else 0
        if ref.startswith('D') and f.GetFPIDAsString().endswith('DO-35_SOD27_P7.62mm_Horizontal'):
            # Diode: Name zwischen Kathodenring und Anodenende, schmalere Schrift
            a, k = [p for p in pads if p.GetNumber() == '2'][0], [p for p in pads if p.GetNumber() == '1'][0]
            dx = pcbnew.ToMM(a.GetPosition().x - k.GetPosition().x) / 7.62
            dy = pcbnew.ToMM(a.GetPosition().y - k.GetPosition().y) / 7.62
            feld(f, x + 0.55 * dx, y + 0.55 * dy, w, breite=0.65)
        else:
            feld(f, x, y, w)                     # Name mitten im Koerper

# Umriss
for (x1, y1, x2, y2) in ((0, 0, B, 0), (B, 0, B, H), (B, H, 0, H), (0, H, 0, 0)):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    board.Add(s)

board.BuildConnectivity()
pcbnew.SaveBoard(ZIEL, board)

# ---------------------------------------------------------------- Fertigungsregeln in die Projektdatei
# JLCPCB, 2 Lagen FR-4, 1 oz, Seite jlcpcb.com/capabilities/pcb-capabilities, gelesen 15.10.2026:
# Bahn/Abstand min. 0,10 mm, Bohrung min. 0,15 mm, Via-Durchmesser min. 0,25 mm, Loch-Loch 0,45 mm (Pads),
# Loch-Bahn 0,28 mm, Kupfer-Kante 0,2 mm, Aufdruck: Linie 0,15 mm, Schrift 1,0 mm hoch, Pad-Aufdruck 0,15 mm.
# Hier mit Reserve gesetzt (Handloeten, Motorraum).
REGELN = {'min_clearance': 0.15, 'min_track_width': 0.15, 'min_via_diameter': 0.5, 'min_via_annular_width': 0.1,
          'min_through_hole_diameter': 0.3, 'min_hole_to_hole': 0.5, 'min_hole_clearance': 0.3,
          'min_copper_edge_clearance': 0.3, 'min_silk_clearance': 0.15, 'min_text_height': 1.0, 'min_text_thickness': 0.15}
# Leiterbahnbreite nach IPC-2221, Aussenlage, 35 um Kupfer, 10 K Erwaermung: A[mil2] = (I / (0,048 * 10^0,44))^(1/0,725), b = A / 1,378:
#   3 A -> 1,37 mm (Vsys+: Grenze der Jumper, Strom der Bedieneinheit nicht gemessen) -> 1,5 mm
#   2 A -> 0,78 mm (+5 V: Grenze R-78B5.0-2.0) -> 1,0 mm;  1 A -> 0,30 mm (+12 V hinter Sicherung 1 A T) -> 1,0 mm
KLASSEN = [('Default', 0.25, 0.2, []),
           ('Strom_3A', 1.5, 0.3, ['*VSYS_J', '*VSYS_B']),
           ('Versorgung', 1.0, 0.2, ['*+12V_EIN', '*+12V_F', 'Net-(D1-A)', 'Net-(U3-IN)', '*+5V', 'GND'])]
pro_pfad = os.path.splitext(ZIEL)[0] + '.kicad_pro'
pro = json.load(open(pro_pfad, encoding='utf-8')) if os.path.exists(pro_pfad) else {'meta': {'filename': os.path.basename(pro_pfad), 'version': 3}}
ds = pro.setdefault('board', {}).setdefault('design_settings', {})
ds.setdefault('rules', {}).update(REGELN)
ds['track_widths'] = [0.0, 0.25, 0.5, 1.0, 1.5]
ds['via_dimensions'] = [{'diameter': 0.0, 'drill': 0.0}, {'diameter': 0.6, 'drill': 0.3}, {'diameter': 0.8, 'drill': 0.4}]
ns = pro.setdefault('net_settings', {'meta': {'version': 5}})
vorlage = (ns.get('classes') or [{}])[0]
klassen, muster = [], []
for i, (name, breite, abstand, pat) in enumerate(KLASSEN):
    k = dict(vorlage)
    k.update({'name': name, 'track_width': breite, 'clearance': abstand, 'via_diameter': 0.8 if breite >= 1.0 else 0.6,
              'via_drill': 0.4 if breite >= 1.0 else 0.3, 'priority': 2147483647 if name == 'Default' else i})
    klassen.append(k)
    muster += [{'netclass': name, 'pattern': m} for m in pat]
ns['classes'] = klassen
ns['netclass_patterns'] = muster
json.dump(pro, open(pro_pfad, 'w', encoding='utf-8'), indent=2)

# ---------------------------------------------------------------- Selbstpruefung
fehler = 0
for f in board.GetFootprints():
    ref = f.GetReference()
    if ref[0] in 'RD' and ref[1:].isdigit() and int(ref[1:]) >= 11:
        ys = {p.GetNumber(): pcbnew.ToMM(p.GetPosition().y) for p in f.Pads()}
        k = knoten(ref)
        andere = '1' if k == '2' else '2'
        if not ys[k] > ys[andere]:
            print('Mittelpunkt nicht unten:', ref); fehler += 1
    bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    l, r, o, u = (pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetRight(), bb.GetTop(), bb.GetBottom()))
    if l < -0.6 or o < -0.6 or r > B + 0.6 or u > H + 0.6:
        print('Hof ausserhalb der Platine: %s (%.2f %.2f %.2f %.2f)' % (ref, l, o, r, u)); fehler += 1
print('Ohne 3D-Modell:', ohne_modell or 'keins')
print('Bauteile: %d, Netze: %d, Selbstpruefung Fehler: %d' % (len(board.GetFootprints()), len(nets), fehler))
