# Erzeugt die Platine Robnet-Analyse Linie B (SMD) v00.01: Umriss, Bauteile mit Netzen, Befestigungsloecher, 3D-Modelle
# (keine Leiterbahnen). Version 00.05, Stand 16.10.2026. Grundlage: Linie A (tht/kicad/v00.01/platine_erzeugen).
# Gegen Linie A: 100 x 100 mm (guenstigste Leiterplattenstufe bei JLCPCB), J1 genau ueber J3 an der Unterkante, Jumper senkrecht
# unter ihren Klemmen an J1, M3-Loecher in allen vier Ecken (Betreiber 16.10.2026),
# alle SMD-Teile oben und mindestens 2,5 mm vom Rand (Regel fuer von JLCPCB bestueckte Teile).
# Aufruf mit dem Python von KiCad (KiCad geschlossen), Ziel ist die Zwischendatei ohne Bahnen:
#   "C:/Program Files/KiCad/10.0/bin/python.exe" robnet_platine.py <netzliste.xml> Robnet-Analyse_platziert.kicad_pcb
# Die Leiterbahnen ergaenzt danach ../bahnen_erzeugen/robnet_bahnen.py und schreibt ../Robnet-Analyse.kicad_pcb.
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

B, H = 100.0, 100.0                     # Platinengroesse
RAND_SMD = 2.5                          # Bauteilkoerper SMD bis Kante (JLCPCB-Bestueckungsregeln, Abschnitt 3)

# ---------------------------------------------------------------- Lage der Bauteile: Ref -> (x, y, Drehung)
P = {}
# Stecker (Betreiber, 16.10.2026): J1 oben rechts genau ueber J3 unten rechts; J2 oben links. Beide Phoenix zeigen nach aussen,
# deshalb ist ihre Klemmenfolge von oben gesehen gespiegelt (J1: 6..1 von links, J3: 1..6 von links).
XS = 62.0                               # linke Klemme von J1 und J3
P['J1'] = (XS + 5 * 5.08, 10.16, 180)   # Kabel zum J300, Klemme 1 (Bus-) rechts
P['J3'] = (XS, H - 10.16, 0)            # Stecker der Bedieneinheit, Klemme 1 (Bus-) links
P['J2'] = (20.0, 10.16, 180)            # +12 V Versorgung, oben links
def klemme(ref, k):                     # x der Klemme k (1..6)
    return P['J1'][0] - 5.08 * (k - 1) if ref == 'J1' else P['J3'][0] + 5.08 * (k - 1)
# Trenn-Jumper direkt unter J1 (Seite J300), jeder senkrecht unter seiner Klemme; Masse (Klemme 4) ohne Jumper
JPY = 19.5
ADERN = (('JP4', 'Bus−', 1), ('JP3', 'Bus+', 2), ('JP5', 'Vsys+', 3), ('JP6', 'On-Off', 5), ('JP7', 'Alarm', 6))
for r, _, k in ADERN:
    P[r] = (klemme('J1', k), JPY, 0)
P['J4'] = (B - 5.0, 57.0, 0)            # Messpunkte Bus+, Bus-, Masse (Seite J300), am rechten Rand
# Zero 2 W kopfueber, links; um 8 mm nach oben geschoben, damit unten links ein M3-Loch Platz hat (Betreiber, 16.10.2026)
P['J5'] = (25.83, H - 16.97, 180)
# Versorgung oben links: J2 -> D1 -> D2, C4 -> R5 || R6 -> L1 -> C5, C6 -> U3
P['D1'] = (26.5, 17.0, 0)               # SS54
P['D2'] = (33.5, 17.5, 90)              # SMCJ18CA
P['C4'] = (39.0, 18.0, 90)
P['R5'] = (43.5, 16.0, 0)
P['R6'] = (43.5, 19.5, 0)
P['L1'] = (49.5, 18.0, 0)               # Platz Drossel, bestueckt mit Drahtbruecke
P['C5'] = (37.5, 7.0, 90)
P['C6'] = (41.0, 7.0, 90)
P['U3'] = (47.0, 5.5, 0)                # R-78B
# Wandler: Kanaele rechts (Pins 1-8), SPI, Referenz und Versorgung links zum Zero (Drehung 180)
P['U2'] = (44.45, 50.0, 180)
P['U6'] = (44.45, 84.0, 180)
P['C2'] = (33.0, 49.0, 90)
P['C3'] = (33.0, 83.0, 90)
P['U4'] = (33.0, 57.5, 0)               # Referenz TO-92 zwischen den Wandlern
P['R4'] = (34.5, 62.0, 90)
# Bus-Empfaenger: JP2 und JP1 rechts unter der Jumperreihe mit Funktionstext daneben; U1 und C1 unter dem Alarmkanal
# (U1, C1 vom Betreiber in KiCad verschoben, 16.10.2026)
P['JP2'] = (68.0, 37.0, 0)              # Seitenwahl
P['R1'] = (68.5, 45.3, 0)
P['R2'] = (77.5, 45.3, 0)
P['JP1'] = (68.0, 48.5, 0)              # gerade / gekreuzt
P['U1'] = (65.19, 69.19, 0)
P['C1'] = (70.5, 65.5, 0)

# Teiler: je Kanal eine Zeile aus R oben (zur Ader), BAT54S (Mitte am Messpunkt), R unten (zur Masse)
KANAL_J = [('R11', 'R12', 'D11'), ('R13', 'R14', 'D12'), ('R15', 'R16', 'D13'), ('R17', 'R18', 'D14'),
           ('R19', 'R20', 'D15'), ('R21', 'R22', 'D16')]
KANAL_B = [('R31', 'R32', 'D31'), ('R33', 'R34', 'D32'), ('R35', 'R36', 'D33'), ('R37', 'R38', 'D34'), ('R39', 'R40', 'D35')]
KX, KDY = 50.5, 4.8                     # linke Spalte der Kanaele, Zeilenabstand
def zelle(t, x0, y0, dreh=0):
    rt, rb, d = t
    P[rt] = (x0, y0, dreh)              # Ader links, Mitte rechts (Seite Bedieneinheit: Ader an Pin 2, deshalb 180 Grad)
    P[d] = (x0 + 4.4, y0, 180)          # Pin 3 (Mitte) links, Pin 1 (Masse) unten rechts, Pin 2 (+3V3) oben rechts
    P[rb] = (x0 + 9.4, y0, 0)           # Pin 1 (Mitte) links, Pin 2 (Masse) rechts
# Zeilen von unten nach oben in Kanalfolge (Betreiber, 16.10.2026): CH0 der Wandler liegt unten (Drehung 180),
# so laufen die Messleitungen ohne Kreuzung zu U2/U6
for i, t in enumerate(reversed(KANAL_J)):
    zelle(t, KX, 32.5 + KDY * i)
for i, t in enumerate(reversed(KANAL_B)):
    zelle(t, KX, 61.5 + KDY * i, 180)
zelle(('R23', 'R24', 'D23'), KX + 15.0, 62.0)   # Alarm an den Zero (Seite J300)

LOECHER = [(3.8, 3.8), (B - 3.8, 3.8), (3.8, H - 3.8), (B - 3.8, H - 3.8)]   # alle vier Ecken (Betreiber, 16.10.2026)

# ---------------------------------------------------------------- Netzliste lesen
root = ET.parse(NETZ).getroot()
comps = {}
for c in root.iter('comp'):
    sp = c.find('sheetpath')
    felder = {f.get('name'): (f.text or '') for f in c.iter('field') if f.get('name') not in ('Footprint',)}
    comps[c.get('ref')] = dict(value=c.findtext('value'), fp=c.findtext('footprint'), felder=felder,
                               path=sp.get('tstamps') + c.findtext('tstamps'), sheet=sp.get('names'))
def netzname(n):
    return n.replace('/', '{slash}') if n.startswith(('unconnected-(', 'Net-(')) else n

pinnet = {}
netnames = []
for n in root.iter('net'):
    netnames.append(netzname(n.get('name')))
    for nd in n.iter('node'):
        pinnet[(nd.get('ref'), nd.get('pin'))] = netzname(n.get('name'))

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

# 3D-Modelle: THT-Teile wie Linie A aus hardware/tht/3d-modelle, SMD-Teile mit dem Modell der
# KiCad-Bibliothek (bleibt in der Bauform stehen).
M3D = '${KIPRJMOD}/../../../tht/3d-modelle/'
MODELLE = {
    'DIP-8_W7.62mm_Socket': [('KiCad_DIP-8_W7.62mm_Socket.step', 0), ('KiCad_DIP-8_W7.62mm.step', 4.0)],
    'DIP-16_W7.62mm_Socket': [('KiCad_DIP-16_W7.62mm_Socket.step', 0), ('KiCad_DIP-16_W7.62mm.step', 4.0)],
    'TO-92_Inline': [('KiCad_TO-92_Inline.step', 0)],
    'Converter_DCDC_RECOM_R-78B-2.0_THT': [('KiCad_Converter_DCDC_RECOM_R-78B-2.0_THT.step', 0)],
    'L_Radial_D10.0mm_P5.00mm_Fastron_07P': [('kicad-lage/Bourns_RLB0914-100KL.step', 0)],
    'PinHeader_1x02_P2.54mm_Vertical': [('KiCad_PinHeader_1x02_P2.54mm_Vertical.step', 0), ('kicad-lage/Harwin_M7566-05_auf_1x02.step', 0)],
    'PinHeader_1x03_P2.54mm_Vertical': [('KiCad_PinHeader_1x03_P2.54mm_Vertical.step', 0)],
    'PinHeader_2x03_P2.54mm_Vertical': [('KiCad_PinHeader_2x03_P2.54mm_Vertical.step', 0), ('kicad-lage/Harwin_M7566-05_2x_auf_2x03_oben.step', 0)],
    'PhoenixContact_MSTBA_2,5_6-G-5,08_1x06_P5.08mm_Horizontal': [('kicad-lage/J_MSTBA-6-G_mit_MSTB-6-ST.step', 0)],
    'PhoenixContact_MSTBA_2,5_2-G-5,08_1x02_P5.08mm_Horizontal': [('kicad-lage/J_MSTBA-2-G_mit_MSTB-2-ST.step', 0)],
    'Raspberry_Pi_Zero_kopfueber': [('KiCad_PinSocket_2x20_P2.54mm_Vertical.step', 0), ('kicad-lage/Zero2W_Baugruppe_kopfueber.step', 0)],
}

def modelle(f):
    name = f.GetFPID().GetLibItemName().wx_str()
    if name not in MODELLE:
        return f.Models().size() > 0            # SMD: Modell der KiCad-Bibliothek behalten
    f.Models().clear()
    for datei, dz in MODELLE[name]:
        m = pcbnew.FP_3DMODEL()
        m.m_Filename = M3D + datei
        m.m_Offset = pcbnew.VECTOR3D(0, 0, dz)
        m.m_Show = True
        f.Models().push_back(m)
    return True

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
    f.Models().clear()
    f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    board.Add(f)

# ---------------------------------------------------------------- Beschriftung (Aufdruck oben)
def text(s, x, y, groesse=1.0, winkel=0, links=False, dicke=0.15, rechts=False):
    tx = pcbnew.PCB_TEXT(board)
    tx.SetText(s)
    tx.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    tx.SetLayer(pcbnew.F_SilkS)
    tx.SetTextSize(pcbnew.VECTOR2I(mm(groesse * 0.8), mm(groesse)))
    tx.SetTextThickness(mm(dicke))
    tx.SetTextAngleDegrees(winkel)
    if links:
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    if rechts:
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    board.Add(tx)

def feld(f, x, y, winkel=0, groesse=1.0, breite=0.8):
    r = f.Reference()
    r.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    r.SetTextAngleDegrees(winkel)
    r.SetTextSize(pcbnew.VECTOR2I(mm(groesse * breite), mm(groesse)))
    r.SetTextThickness(mm(0.15))

ADERNAME = ('Bus−', 'Bus+', 'Vsys+', 'Masse', 'On-Off', 'Alarm')        # Klemme 1-6 an J1 und J3
# J1: Nummer und Name je Klemme (zwei Zeilen), darunter die Jumper; Titel unter der Jumperreihe
for k, nm in enumerate(ADERNAME, 1):
    x = klemme('J1', k)
    text(str(k), x, 14.4, groesse=1.2, dicke=0.2)
    text(nm, x, 16.5)                    # Name der Klemme zwischen Nummer und Jumper
    if k == 4:
        text('fest', x, 21.0)            # Masse: kein Jumper, nie getrennt
text('J1: HAUPTGERÄT J300', klemme('J1', 3.5), 30.3, groesse=1.6, dicke=0.3)
for r, nm, k in ADERN:                  # Jumpername unter dem Jumper: Ader und Klemme (gleiche Nummer an J1 und J3)
    text(nm, P[r][0], JPY + 6.6, groesse=1.2, dicke=0.2)
    text('Kl. %d' % k, P[r][0], JPY + 8.5, groesse=1.0)
text('JP3–JP7: gesteckt = verbunden', klemme('J1', 3.5), 32.6)
# J2
text('+12 V', P['J2'][0], 14.2)
text('Masse', P['J2'][0] - 5.08, 14.2)
text('J2: +12 V', P['J2'][0] - 2.54, 17.6, groesse=1.6, dicke=0.3)
# J3: Name und Nummer je Klemme ueber dem Stecker, Titel darueber
for k, nm in enumerate(ADERNAME, 1):
    x = klemme('J3', k)
    text(nm, x, H - 16.4)
    text(str(k), x, H - 14.4, groesse=1.2, dicke=0.2)
text('J3: BEDIENEINHEIT', klemme('J3', 3.5), H - 19.0, groesse=1.6, dicke=0.3)
for k, nm in enumerate(('Bus+', 'Bus−', 'Masse')):
    text(nm, P['J4'][0] - 1.9, P['J4'][1] + 2.54 * k, rechts=True)
text('Messpunkte', P['J4'][0], P['J4'][1] + 9.0)
# JP2 und JP1: je Reihe der Stifte ihre Bedeutung rechts daneben; Ueberschrift ueber JP2 bzw. unter JP1.
# Stellungen A-E als Bildtabelle rechts (wie smd/konzeption/Jumper_JP1_JP2.html): oben = Bruecken 1-3 und 2-4, unten = 3-5 und 4-6
XT = P['JP2'][0] + 5.0
for ref, zeilen in (('JP2', ('J1 (J300)', 'U1', 'J3 (Bedien.)')), ('JP1', ('normal', 'U1', 'getauscht'))):
    for i, s in enumerate(zeilen):
        text(s, XT, P[ref][1] + 2.54 * i, links=True)
text('JP2: SEITE', XT, P['JP2'][1] - 2.1, groesse=1.2, links=True, dicke=0.2)
text('JP1: ADERN TAUSCHEN', P['JP1'][0] - 1.8, P['JP1'][1] + 8.1, groesse=1.2, links=True, dicke=0.2)

def flaeche(xa, ya, xb, yb):            # gefuelltes Rechteck im Aufdruck
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
    s.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
    s.SetLayer(pcbnew.F_SilkS)
    s.SetWidth(mm(0.15))
    s.SetFilled(True)
    board.Add(s)

def strich(xa, ya, xb, yb):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
    s.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
    s.SetLayer(pcbnew.F_SilkS)
    s.SetWidth(mm(0.2))
    board.Add(s)

ST = 1.1                                 # Stiftabstand im Bildchen
def bildchen(x, y, bruecken, quer=None):  # 2 x 3 Stifte, linke obere Ecke; bruecken: 'oben', 'unten' oder ''
    for sp in (0, 1):
        for r in (0, 1, 2):
            if not (bruecken == 'oben' and r < 2 or bruecken == 'unten' and r > 0) and r != quer:
                flaeche(x + sp * ST - 0.2, y + r * ST - 0.2, x + sp * ST + 0.2, y + r * ST + 0.2)
        if bruecken:
            r0 = 0 if bruecken == 'oben' else 1
            flaeche(x + sp * ST - 0.35, y + r0 * ST - 0.35, x + sp * ST + 0.35, y + (r0 + 1) * ST + 0.35)
    if quer is not None:
        flaeche(x - 0.35, y + quer * ST - 0.35, x + ST + 0.35, y + quer * ST + 0.35)

TX, TY, TZ = 87.0, 35.6, 3.8             # Tabelle: linke Spalte, erste Zeile, Zeilenabstand
text('JP2', TX + 3.3, TY - 1.6, links=False)
text('JP1', TX + 7.0, TY - 1.6, links=False)
for i, (bst, jp2, jp1) in enumerate((('A', 'oben', 'oben'), ('B', 'oben', 'unten'), ('C', 'unten', 'oben'),
                                     ('D', 'unten', 'unten'), ('E', '', 'oben'))):
    y = TY + i * TZ
    text(bst, TX, y + ST, groesse=1.4, dicke=0.25)
    bildchen(TX + 2.75, y, jp2)
    bildchen(TX + 6.45, y, jp1)
# nie quer: Bruecke quer, durchgekreuzt
text('nie', TX + 11.0, TY - 1.6)
text('quer!', TX + 11.0, TY + 4.2)
bildchen(TX + 10.45, TY, '', quer=0)
strich(TX + 9.6, TY - 0.7, TX + 12.4, TY + 2.9)
strich(TX + 12.4, TY - 0.7, TX + 9.6, TY + 2.9)
text('Robnet-Analyse B v00.01', 88.0, 74.0)
text('SuAn electronic', 88.0, 76.0)
text('Lutz Pestel, 2026', 88.0, 77.8)

SUPPLY_FELD = {'D1': (26.5, 14.0), 'D2': (33.5, 24.0), 'C4': (39.0, 22.0), 'R5': (43.5, 14.2), 'R6': (43.5, 21.6),
               'L1': (49.5, 24.6), 'C5': (37.5, 11.0), 'C6': (41.0, 11.0), 'C1': (74.8, 65.5)}
for f in board.GetFootprints():
    ref = f.GetReference()
    if ref in [a[0] for a in ADERN]:
        feld(f, P[ref][0] - 2.5, P[ref][1] + 1.27, 90)
    elif ref == 'J4':
        feld(f, P[ref][0] + 2.5, P[ref][1] + 2.54, 90)
    elif ref in ('J1', 'J2', 'J3') or ref[0] == 'H':
        f.Reference().SetVisible(False)
    elif any(ref in z for z in KANAL_J + KANAL_B + [('R23', 'R24', 'D23')]):
        feld(f, P[ref][0], P[ref][1] - 2.3)       # Name ueber dem Teil, Kanalzeilen 5 mm
    elif ref in ('C2', 'C3'):
        feld(f, P[ref][0], P[ref][1] - 3.8)       # ueber dem Teil, nicht im Umriss des Zero
    elif ref == 'J5':
        f.Reference().SetVisible(False)           # der Zero ist gross beschriftet
    elif ref in ('U3',):
        feld(f, P[ref][0] + 10.0, P[ref][1] + 1.3)
    elif ref in ('R1', 'R2'):
        feld(f, P[ref][0] + 3.6, P[ref][1])       # rechts neben dem Teil
    elif ref == 'U1':
        feld(f, P[ref][0] + 10.6, P[ref][1] + 3.81, 90)   # rechts neben der Fassung (innen verdeckt der Chip)
    elif ref in ('JP1', 'JP2'):
        feld(f, P[ref][0] - 2.6, P[ref][1] + 2.54, 90)
    elif ref in SUPPLY_FELD:
        feld(f, *SUPPLY_FELD[ref])

# Umriss
for (xa, ya, xb, yb) in ((0, 0, B, 0), (B, 0, B, H), (B, H, 0, H), (0, H, 0, 0)):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
    s.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    board.Add(s)

board.BuildConnectivity()
pcbnew.SaveBoard(ZIEL, board)

# ---------------------------------------------------------------- Fertigungsregeln und Leiterbahnklassen in die Projektdatei (wie Linie A)
REGELN = {'min_clearance': 0.15, 'min_track_width': 0.15, 'min_via_diameter': 0.5, 'min_via_annular_width': 0.1,
          'min_through_hole_diameter': 0.3, 'min_hole_to_hole': 0.5, 'min_hole_clearance': 0.3,
          'min_copper_edge_clearance': 0.3, 'min_silk_clearance': 0.15, 'min_text_height': 1.0, 'min_text_thickness': 0.15}
KLASSEN = [('Default', 0.25, 0.2, []),
           ('Strom_3A', 1.5, 0.3, ['*VSYS_J', '*VSYS_B']),
           ('Versorgung', 1.0, 0.2, ['*+12V_EIN', '*+12V_F', 'Net-(L1-Pad1)', 'Net-(U3-IN)', '*+5V', 'GND'])]
pro_pfad = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Robnet-Analyse.kicad_pro')   # Projekt der fertigen Platine
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
# Aufdruck der Stecker an der Kante ist gewollt (Gehaeuse ragt ueber die Kante; JLCPCB schneidet ab; Betreiber, 16.10.2026)
STECKER = " || ".join("%s.memberOfFootprint('%s')" % (s, r) for s in 'AB' for r in ('J1', 'J2', 'J3', 'J5'))
open(os.path.splitext(pro_pfad)[0] + '.kicad_dru', 'w', encoding='utf-8').write(
    '(version 1)\n'
    '(rule "Aufdruck der Stecker an der Kante (gewollt)"\n'
    '  (condition "(%s) && (A.Layer == \'F.Silkscreen\' || B.Layer == \'F.Silkscreen\')")\n'
    '  (constraint silk_clearance (min -10mm))\n'
    '  (constraint edge_clearance (min -10mm))\n'
    '  (severity ignore))\n' % STECKER)
zwischen = os.path.splitext(os.path.abspath(ZIEL))[0] + '.kicad_pro'      # gleiche Regeln in der Zwischendatei, damit das
if os.path.normcase(zwischen) != os.path.normcase(os.path.abspath(pro_pfad)):  # Bahnenskript mit ihnen arbeitet
    kopie = json.loads(json.dumps(pro))
    kopie.setdefault('meta', {})['filename'] = os.path.basename(zwischen)
    json.dump(kopie, open(zwischen, 'w', encoding='utf-8'), indent=2)

# ---------------------------------------------------------------- Selbstpruefung: Rand und Ueberlappung der Hoefe
fehler = 0
hoefe = []
for f in board.GetFootprints():
    ref = f.GetReference()
    bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    l, r, o, u = (pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetRight(), bb.GetTop(), bb.GetBottom()))
    smd = comps.get(ref, {}).get('felder', {}).get('LCSC Part #')
    if smd and (l < RAND_SMD or o < RAND_SMD or r > B - RAND_SMD or u > H - RAND_SMD):
        print('JLCPCB-Teil naeher als %.1f mm am Rand: %s (%.2f %.2f %.2f %.2f)' % (RAND_SMD, ref, l, o, r, u)); fehler += 1
    if ref != 'J5' and (l < -0.6 or o < -0.6 or r > B + 0.6 or u > H + 0.6):   # Zero ragt wie in Linie A ueber die Kante
        print('Hof ausserhalb der Platine: %s (%.2f %.2f %.2f %.2f)' % (ref, l, o, r, u)); fehler += 1
    if ref[0] != 'H':
        hoefe.append((ref, l, o, r, u))
for i, a in enumerate(hoefe):
    for b in hoefe[i + 1:]:
        if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
            print('Hoefe ueberlappen: %s / %s' % (a[0], b[0])); fehler += 1
print('Ohne 3D-Modell:', ohne_modell or 'keins')
print('Bauteile: %d, Netze: %d, Selbstpruefung Fehler: %d' % (len(board.GetFootprints()), len(nets), fehler))
