# Ergaenzt die Leiterbahnen der Platine Robnet-Analyse Linie B (SMD) v00.01. Version 00.04, Stand 16.10.2026.
# Liest die platzierte Platine (ohne Bahnen, aus ../platine_erzeugen/robnet_platine.py) und schreibt die fertige Platine.
# Aufruf mit dem Python von KiCad (KiCad geschlossen):
#   "C:/Program Files/KiCad/10.0/bin/python.exe" robnet_bahnen.py ../platine_erzeugen/Robnet-Analyse_platziert.kicad_pcb ../Robnet-Analyse.kicad_pcb
# Schutz: Liegt ein Bauteil im Ziel anders als in der platzierten Platine (in KiCad verschoben), bricht das Skript ab;
# die neue Lage erst ins Platzierungsskript uebernehmen. Bahnen, die nur im Ziel stehen (in KiCad gezeichnet), ebenso;
# Ueberschreiben nur mit --ueberschreiben; neue Lage aus dem Platzierungsskript mit --neue-lage.
# Gruppen nacheinander, je Gruppe vom Betreiber freigegeben: 1 Versorgung und Masse, 2 Adern J1 -> Jumper -> J3,
# 3 Teiler -> Wandler mit Referenz und Alarm zum Zero, 4 SPI zum Zero (16.10.2026).
# Masse in mm, Ursprung oben links, y nach unten. Lagen: O = Oberseite (F.Cu), U = Unterseite (B.Cu, Massefläche).
import sys, os
import pcbnew

QUELLE, ZIEL = sys.argv[1], sys.argv[2]
UEBERSCHREIBEN = '--ueberschreiben' in sys.argv
NEUE_LAGE = '--neue-lage' in sys.argv      # Lage im Platzierungsskript absichtlich geaendert (vorher pruefen: nichts in KiCad verschoben)
B, H = 100.0, 100.0

def mm(v):
    return pcbnew.FromMM(v)

board = pcbnew.LoadBoard(QUELLE)
assert len(board.GetTracks()) == 0, 'Quelle hat schon Bahnen'
NETZ = {}
for name, n in board.GetNetsByName().items():
    NETZ[str(name).split('/')[-1]] = n
O, U = pcbnew.F_Cu, pcbnew.B_Cu

def bahn(netz, breite, lage, *punkte):
    for (xa, ya), (xb, yb) in zip(punkte, punkte[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(xa), mm(ya)))
        t.SetEnd(pcbnew.VECTOR2I(mm(xb), mm(yb)))
        t.SetWidth(mm(breite))
        t.SetLayer(lage)
        t.SetNet(NETZ[netz])
        board.Add(t)

def via(netz, x, y, d=0.6, bohrung=0.3):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(d))
    v.SetDrill(mm(bohrung))
    v.SetNet(NETZ[netz])
    board.Add(v)

# ---------------------------------------------------------------- Gruppe 1: Versorgung und Masse
# 12 V: J2 -> D1 (Verpolschutz) -> D2 (Ueberspannung), C4 -> R5 || R6 -> L1 (Drahtbruecke) -> C5, C6 -> U3, 1,0 mm oben
bahn('+12V_EIN', 1.0, O, (20.0, 10.16), (20.0, 13.5), (28.5, 13.5), (28.5, 17.0))
bahn('+12V_F', 1.0, O, (24.5, 17.0), (24.5, 20.9), (39.0, 20.9), (39.0, 19.5), (42.04, 19.5), (42.04, 16.0))
bahn('Net-(L1-Pad1)', 1.0, O, (44.96, 16.0), (44.96, 19.5))
bahn('Net-(L1-Pad1)', 1.0, O, (44.96, 18.0), (49.5, 18.0))
bahn('Net-(U3-IN)', 1.0, O, (54.5, 18.0), (54.5, 14.0), (47.0, 14.0), (47.0, 5.5))
bahn('Net-(U3-IN)', 1.0, O, (47.0, 8.47), (37.5, 8.47))

# 5 V: U3 -> Zero Pin 2 und 4, 1,5 mm oben, aussen herum (oben an der Kante, links unter dem Zero), damit die Mitte
# zwischen Zero und Wandlern fuer SPI frei bleibt
bahn('+5V', 1.5, O, (52.08, 5.5), (52.08, 2.6), (9.0, 2.6), (9.0, 85.2), (28.37, 85.2), (28.37, 83.03), (28.37, 80.49))

# 3,3 V vom Zero (Pin 1 und 17). Die Messleitung jedes Kanals laeuft oben quer unter ihrer BAT54S durch, deshalb
# fuehrt die 3,3 V unten (Sammelleitung x = 57,3 rechts der Dioden, je Diode eine Durchkontaktierung).
bahn('+3V3', 0.4, O, (25.83, 62.71), (23.6, 62.71), (23.6, 83.03), (25.83, 83.03))      # Pin 17 - Pin 1, links unter dem Zero
bahn('+3V3', 0.4, O, (34.5, 62.91), (35.8, 64.0))                                        # R4 (Referenz); Durchkontaktierung
via('+3V3', 35.8, 64.0)                                  # rechts, damit die Masseflaeche zwischen ihr und der Referenz durchkommt
bahn('+3V3', 0.4, U, (35.8, 64.0), (37.9, 64.0), (37.9, 51.2), (36.83, 50.0))            # U2 VDD (Abstand zu U4 Pin 3: Masse)
bahn('+3V3', 0.4, U, (37.9, 59.5), (57.3, 59.5))        # zwischen den Kanalbloecken: kreuzt keine Messleitung (Gruppe 3)
bahn('+3V3', 0.4, O, (33.0, 50.48), (36.83, 50.48))                                      # C2
bahn('+3V3', 0.4, U, (25.83, 83.03), (27.2, 84.4), (36.83, 84.4))                        # U6 VDD
bahn('+3V3', 0.4, O, (33.0, 84.47), (36.83, 84.47))                                      # C3
bahn('+3V3', 0.4, U, (36.83, 84.0), (36.83, 86.3), (57.3, 86.3), (57.3, 79.6))            # U6 und Zero an die Sammelleitung
ZEILEN_J = [32.5, 37.3, 42.1, 46.9, 51.7, 56.5]          # Kanalzeilen (y der Widerstaende), Seite J300 und Bedieneinheit
ZEILEN_B = [61.5, 66.3, 71.1, 75.9, 80.7]
ZEILEN = ZEILEN_J + ZEILEN_B
bahn('+3V3', 0.4, U, (57.3, ZEILEN[0] - 1.1), (57.3, ZEILEN[-1] - 1.1))
for y in ZEILEN:                                          # BAT54S Pin 2 (oben rechts) zur Sammelleitung
    bahn('+3V3', 0.3, O, (55.84, y - 0.95), (57.3, y - 1.1))
    via('+3V3', 57.3, y - 1.1)
bahn('+3V3', 0.4, U, (57.3, 68.3), (64.3, 68.3), (65.19, 69.19))                         # U1 Pin 1 (VCC)
bahn('+3V3', 0.4, U, (65.19, 69.19), (66.6, 70.6), (66.6, 72.86), (65.19, 74.27))         # U1 Pin 3 (DI fest high)
bahn('+3V3', 0.4, U, (65.19, 69.19), (66.4, 67.98), (68.05, 67.98), (69.03, 67.0))        # C1
via('+3V3', 69.03, 67.0)
bahn('+3V3', 0.4, O, (69.03, 65.5), (69.03, 67.0))
bahn('+3V3', 0.4, U, (69.03, 67.0), (69.03, 61.7), (70.84, 59.9))                         # D23 (Alarm zum Zero)
via('+3V3', 70.84, 59.9)
bahn('+3V3', 0.4, O, (70.84, 61.05), (70.84, 59.9))

# ---------------------------------------------------------------- Gruppe 2: Adern J1 -> Jumper -> J3
# Klemmen x (J1 von links 6..1, J3 von links 1..6), Jumper Pin 1 (Seite J300) y 19,5, Pin 2 (Seite Bedieneinheit) y 22,04
J1X = {'ALARM': 62.0, 'ONOFF': 67.08, 'VSYS': 77.24, 'BUSP': 82.32, 'BUSN': 87.4}
J3X = {'BUSN': 62.0, 'BUSP': 67.08, 'VSYS': 72.16, 'ONOFF': 82.32, 'ALARM': 87.4}
ZEILE = {'+12V_F': 32.5, 'ALARM_J': 37.3, 'ONOFF_J': 42.1, 'VSYS_J': 46.9, 'BUSN_J': 51.7, 'BUSP_J': 56.5,
         'BUSN_B': 61.5, 'BUSP_B': 66.3, 'ALARM_B': 71.1, 'ONOFF_B': 75.9, 'VSYS_B': 80.7}   # Aderpad x 49,59
RX = 49.59
def sprung(netz, a, b, breite=0.25):                       # kurz auf die Unterseite (Kreuzung)
    via(netz, *a)
    via(netz, *b)
    bahn(netz, breite, U, a, b)

# Seite J300: Klemme -> Jumper Pin 1 oben; Vsys 1,5 mm
for n, x in J1X.items():
    bahn(n + '_J', 1.5 if n == 'VSYS' else 0.5, O, (x, 10.16), (x, 19.5))
# Seite J300 zu den Teilern: ueber J1 hinweg nach links (rechte Klemme am hoechsten), im Schacht x 57-59,4 hinunter,
# auf y 24-27 nach links in die Gasse x 46-48,6 zwischen U2 und den Teilern (Reihenfolge Zeile von oben = rechts)
OBEN = {'BUSN': 1.0, 'BUSP': 1.6, 'VSYS': 2.2, 'ONOFF': 2.8, 'ALARM': 3.4}
SCHACHT = {'BUSN': 57.0, 'BUSP': 57.6, 'VSYS': 58.2, 'ONOFF': 58.8, 'ALARM': 59.4}
QUER = {'BUSN': 24.2, 'BUSP': 25.2, 'VSYS': 25.8, 'ONOFF': 26.4, 'ALARM': 27.0}
GASSE = {'BUSN': 46.65, 'BUSP': 46.0, 'VSYS': 47.45, 'ONOFF': 48.1, 'ALARM': 48.7}   # Vsys: 0,3 mm Abstand (Klasse Strom_3A)
for n in J1X:
    netz = n + '_J'
    if n == 'BUSN':                                         # Bus- kreuzt Bus+ (Zeilenfolge Bus-, Bus+ wie CH1, CH0)
        bahn(netz, 0.25, O, (J1X[n], 10.16), (J1X[n], OBEN[n]), (SCHACHT[n], OBEN[n]), (SCHACHT[n], QUER[n]), (GASSE[n], QUER[n]))
        sprung(netz, (GASSE[n], QUER[n]), (GASSE[n], 26.2))
        bahn(netz, 0.25, O, (GASSE[n], 26.2), (GASSE[n], ZEILE[netz]), (RX, ZEILE[netz]))
    else:
        bahn(netz, 0.25, O, (J1X[n], 10.16), (J1X[n], OBEN[n]), (SCHACHT[n], OBEN[n]), (SCHACHT[n], QUER[n]),
             (GASSE[n], QUER[n]), (GASSE[n], ZEILE[netz]), (RX, ZEILE[netz]))
# Bordspannung zu R21: unten, unter der Gasse durch
bahn('+12V_F', 0.5, O, (39.0, 20.9), (39.0, 22.3))
via('+12V_F', 39.0, 22.3)
bahn('+12V_F', 0.25, U, (39.0, 22.3), (47.9, 31.0), (RX, 31.0))
via('+12V_F', RX, 31.0)
bahn('+12V_F', 0.25, O, (RX, 31.0), (RX, 32.5))
# Seite J300 unten: Bus+/Bus- zu JP2 (obere Reihe) und zu den Messpunkten J4; Alarm zum Teiler R23 (Zero)
bahn('BUSP_J', 0.25, U, (82.32, 19.5), (68.0, 37.0), (66.4, 37.0), (66.4, 45.0), (93.5, 45.0), (93.5, 57.0), (95.0, 57.0))
bahn('BUSN_J', 0.25, U, (87.4, 19.5), (70.54, 37.0))
bahn('BUSN_J', 0.25, U, (87.4, 19.5), (97.3, 19.5), (97.3, 59.54), (95.0, 59.54))
bahn('ALARM_J', 0.25, U, (62.0, 19.5), (63.5, 21.0), (63.5, 61.0))
via('ALARM_J', 63.5, 61.0)
bahn('ALARM_J', 0.25, O, (63.5, 61.0), (64.59, 62.0))

# Seite Bedieneinheit: Jumper Pin 2 hinunter, Treppe nach rechts (rechter Jumper am hoechsten), rechts am Rand hinunter,
# in ineinanderliegenden Boegen unter J3 durch und von unten in die Klemme: so kreuzt sich trotz gespiegelter Folge nichts
STUFE = {'BUSN': 23.8, 'BUSP': 24.4, 'VSYS': 25.6, 'ONOFF': 26.9, 'ALARM': 27.5}
RAND = {'ALARM': 88.9, 'ONOFF': 89.6, 'VSYS': 90.9, 'BUSP': 92.3, 'BUSN': 93.0}
BOGEN = {'ONOFF': 92.6, 'VSYS': 93.9, 'BUSP': 95.3, 'BUSN': 96.0}
for n, x in J1X.items():
    netz, b = n + '_B', 1.5 if n == 'VSYS' else 0.25
    weg = [(x, 22.04), (x, STUFE[n]), (RAND[n], STUFE[n])]
    if n == 'ALARM':                                        # Klemme 6 liegt direkt links neben dem Rand
        weg += [(RAND[n], 89.84), (J3X[n], 89.84)]
    else:
        weg += [(RAND[n], BOGEN[n]), (J3X[n], BOGEN[n]), (J3X[n], 89.84)]
    bahn(netz, b, O, *weg)
# Bus+/Bus- der Bedieneinheit zu JP2 (untere Reihe): vom Rand unten hinueber
via('BUSN_B', 93.0, 42.08)
bahn('BUSN_B', 0.25, U, (93.0, 42.08), (70.54, 42.08))
via('BUSP_B', 92.3, 43.6)
bahn('BUSP_B', 0.25, U, (92.3, 43.6), (68.0, 43.6), (68.0, 42.08))
# zu den Teilern: von J3 oben nach links (rechte Klemme am hoechsten) in die Gasse; Alarm und Ein/Aus springen unter Vsys durch
EBENE = {'ALARM': 84.6, 'ONOFF': 85.4, 'VSYS': 86.2, 'BUSP': 86.85, 'BUSN': 87.45}
GASSE_B = {'VSYS': 48.7, 'ONOFF': 47.9, 'ALARM': 47.25, 'BUSP': 46.55, 'BUSN': 45.95}
for n in J3X:
    netz = n + '_B'
    if n in ('ALARM', 'ONOFF'):
        xs = 49.5 if n == 'ALARM' else 50.2
        bahn(netz, 0.25, O, (J3X[n], 89.84), (J3X[n], EBENE[n]), (xs, EBENE[n]))
        sprung(netz, (xs, EBENE[n]), (GASSE_B[n], EBENE[n]))
        bahn(netz, 0.25, O, (GASSE_B[n], EBENE[n]), (GASSE_B[n], ZEILE[netz]), (RX, ZEILE[netz]))
    else:
        bahn(netz, 0.25, O, (J3X[n], 89.84), (J3X[n], EBENE[n]), (GASSE_B[n], EBENE[n]), (GASSE_B[n], ZEILE[netz]), (RX, ZEILE[netz]))

# ---------------------------------------------------------------- Gruppe 3: Teiler -> Wandler, Referenz, Alarm zum Zero
# Messleitung je Zeile oben: R zur Ader (Pin rechts) -> BAT54S Pin 3 -> unter der Diode zwischen Pin 1 und 2 durch ->
# R zur Masse; dann unten zum Wandlerpin (Zeilen in Kanalfolge, deshalb ohne Kreuzung)
MITTE = [('Net-(D16-COM)', 32.5, 37.3), ('Net-(D15-COM)', 37.3, 39.84), ('Net-(D14-COM)', 42.1, 42.38),
         ('Net-(D13-COM)', 46.9, 44.92), ('Net-(D12-COM)', 51.7, 47.46), ('Net-(D11-COM)', 56.5, 50.0),
         ('Net-(D35-COM)', 61.5, 73.84), ('Net-(D34-COM)', 66.3, 76.38), ('Net-(D33-COM)', 71.1, 78.92),
         ('Net-(D32-COM)', 75.9, 81.46), ('Net-(D31-COM)', 80.7, 84.0)]          # Netz, Zeile, Pin y an U2/U6 (x 44,45)
for netz, y, py in MITTE:
    bahn(netz, 0.25, O, (51.41, y), (58.99, y))
    bahn(netz, 0.25, O, (52.6, y), (52.6, y + 1.0))
    via(netz, 52.6, y + 1.0)
    bahn(netz, 0.25, U, (52.6, y + 1.0), (46.5, py), (44.45, py))
# Referenz 2,5 V (U4, R4) unten zu U2 und U6 Pin 15, links an R4 vorbei (rechts liegt die 3,3 V von R4)
REF = 'Net-(U2-Vref)'
bahn(REF, 0.25, O, (34.5, 61.09), (35.9, 61.09))          # Durchkontaktierung rechts von R4: links laufen die SPI-Leitungen
via(REF, 35.9, 61.09)
bahn(REF, 0.25, U, (35.9, 61.09), (34.27, 60.0))
bahn(REF, 0.25, U, (34.27, 57.5), (34.27, 60.0), (33.8, 60.5), (33.8, 80.5), (34.76, 81.46), (36.83, 81.46))
bahn(REF, 0.25, U, (34.27, 57.5), (34.27, 55.0), (35.6, 53.7), (35.6, 48.4), (36.83, 47.46))
# Alarm zum Zero (Pin 13): Teiler R23 - D23 - R24 oben, dann unten rechts an U1 vorbei, unter U6 nach links (y 87,6),
# links oben hinauf und zwischen den Stiftreihen in Pin 13. Daneben bleibt Platz fuer die Empfaengerleitung (Gruppe 5):
# unten y 86,9, oben x 30,2 zu Pin 10.
bahn('ALARM_ZERO', 0.25, O, (66.41, 62.0), (73.99, 62.0))
bahn('ALARM_ZERO', 0.25, O, (73.99, 62.0), (73.99, 63.3))
via('ALARM_ZERO', 73.99, 63.3)
bahn('ALARM_ZERO', 0.25, U, (73.99, 63.3), (74.7, 64.0), (74.7, 87.6), (30.8, 87.6))
via('ALARM_ZERO', 30.8, 87.6)
bahn('ALARM_ZERO', 0.25, O, (30.8, 87.6), (30.8, 66.52), (27.1, 66.52), (25.83, 67.79))

# ---------------------------------------------------------------- Gruppe 4: SPI vom Zero zu U2 und U6
# Am Zero liegen die Pins umgekehrt zu den Wandlerpins. Deshalb: unten waagerecht aus der Stiftleiste (je Netz eine Hoehe),
# dann je Ast eine Durchkontaktierung; oben zu U2 hinauf (links = oberer Pin) und zu U6 hinunter (rechts = oberer Pin).
# Gasse oben: x 29,7-31,95 an der Stiftleiste, unterhalb y 62 nach rechts versetzt (links laufen Alarm und Empfaenger).
SPI_AUS = {'CE1': ((28.37, 52.55), 52.55), 'CE0': ((28.37, 55.09), 55.09), 'SCLK': ((25.83, 55.09), 56.36),
           'MISO': ((25.83, 57.63), 58.9), 'MOSI': ((25.83, 60.17), 61.44)}    # Pin, Hoehe der Bahn unten
# Ast nach oben: Durchkontaktierung x, Pin y an U2. Ast nach unten: Durchkontaktierung x (None = dieselbe wie oben),
# Gasse oben, Versatzhoehe, Gasse danach (rechts von Alarm x 30,8), Pin y an U6. Durchkontaktierung 0,5 mm (Gasse eng).
HOCH = {'CE0': (29.65, 34.76), 'MOSI': (30.225, 37.3), 'MISO': (30.8, 39.84), 'SCLK': (31.375, 42.38)}
RUNTER = {'SCLK': (29.65, 29.65, 63.4, 31.3, 76.38), 'MISO': (None, 31.375, 62.8, 31.75, 73.84),
          'MOSI': (32.0, 32.0, 62.2, 32.25, 71.3), 'CE1': (32.0, 32.0, 60.0, 32.75, 68.76)}
UX = 36.83
for n, (pin, y) in SPI_AUS.items():
    vias = [HOCH[n][0]] if n in HOCH else []
    if n in RUNTER and RUNTER[n][0] is not None:
        vias.append(RUNTER[n][0])
    weg = [pin] if pin[1] == y else [pin, (27.1, y)]          # linke Reihe: schraeg zwischen die Stifte
    bahn(n, 0.25, U, *(weg + [(max(vias), y)]))
    for x in vias:
        via(n, x, y, 0.5, 0.3)
    if n in HOCH:
        x, py = HOCH[n]
        bahn(n, 0.25, O, (x, y), (x, py), (UX, py))
    if n in RUNTER:
        xv, x, yv, x2, py = RUNTER[n]
        start = [(HOCH[n][0], y)] if xv is None else []      # MISO: oben von der gemeinsamen Durchkontaktierung hinueber
        bahn(n, 0.25, O, *(start + [(x, y), (x, yv), (x2, yv + 0.45), (x2, py), (UX, py)]))

# Masse: Flaeche auf der ganzen Unterseite; jedes SMD-Massepad oben mit kurzer Bahn an eine Durchkontaktierung 0,8/0,4 mm
def masse(pad, ziel):
    bahn('GND', 0.5, O, pad, ziel)
    via('GND', ziel[0], ziel[1], 0.8, 0.4)
for y in ZEILEN:
    masse((55.84, y + 0.95), (55.84, y + 1.9))            # BAT54S Pin 1
    masse((60.81, y), (62.1, y))                          # Widerstand zur Masse
masse((75.81, 62.0), (77.1, 62.0))                        # R24
masse((70.84, 62.95), (70.84, 63.9))                      # D23
masse((71.97, 65.5), (73.6, 65.5))                        # C1
masse((33.0, 47.52), (34.6, 47.52))                       # C2
masse((33.0, 81.53), (33.0, 79.8))                        # C3 (rechts daneben laeuft die Referenz)
masse((39.0, 16.52), (39.0, 14.9))                        # C4
masse((37.5, 5.53), (35.9, 5.53))                         # C5
masse((41.0, 5.53), (42.6, 5.53))                         # C6
masse((33.5, 14.1), (31.2, 13.4))                         # D2 (Ueberspannungsschutz): zwei Durchkontaktierungen
masse((33.5, 14.1), (31.2, 14.8))

z = pcbnew.ZONE(board)
z.SetLayer(U)
z.SetNet(NETZ['GND'])
z.SetZoneName('Masse unten')
ol = z.Outline()
ol.NewOutline()
for x, y in ((0, 0), (B, 0), (B, H), (0, H)):
    ol.Append(mm(x), mm(y))
z.SetLocalClearance(mm(0.2))                      # 0,2 mm: auch zwischen den Stiften des Zero
z.SetMinThickness(mm(0.25))
z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
z.SetThermalReliefGap(mm(0.3))
z.SetThermalReliefSpokeWidth(mm(0.4))
board.Add(z)
for f in board.GetFootprints():                         # Stiftleiste des Zero: Stege gerade statt schraeg (zwischen den
    if f.GetReference() == 'J5':                         # Stiften ist fuer schraege Stege kein Platz)
        for p in f.Pads():
            p.SetThermalSpokeAngleDegrees(90)

# ---------------------------------------------------------------- Schutz und Speichern
if os.path.exists(ZIEL):
    alt = pcbnew.LoadBoard(ZIEL)
    lage = {f.GetReference(): (f.GetPosition(), f.GetOrientationDegrees(), f.GetLayer()) for f in board.GetFootprints()}
    verschoben = [f.GetReference() for f in alt.GetFootprints()
                  if lage.get(f.GetReference()) != (f.GetPosition(), f.GetOrientationDegrees(), f.GetLayer())]
    if verschoben and not NEUE_LAGE:
        sys.exit('Bauteile im Ziel anders als platziert (erst ins Platzierungsskript uebernehmen): ' + ', '.join(sorted(verschoben)))
    def schluessel(t):
        return (t.GetClass(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetLayer(), t.GetNetname())
    neu = {schluessel(t) for t in board.GetTracks()}
    fremd = [t for t in alt.GetTracks() if schluessel(t) not in neu]
    if fremd and not UEBERSCHREIBEN:
        sys.exit('%d Bahnen/Durchkontaktierungen nur im Ziel (in KiCad gezeichnet?) - erst ins Skript uebernehmen '
                 'oder mit --ueberschreiben verwerfen' % len(fremd))

board.BuildConnectivity()
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pro_ziel = os.path.splitext(ZIEL)[0] + '.kicad_pro'      # Projektdatei gehoert dem Platzierungsskript: SaveBoard
pro_alt = open(pro_ziel, encoding='utf-8').read() if os.path.exists(pro_ziel) else None   # schreibt sie neu, deshalb zurueck
pcbnew.SaveBoard(ZIEL, board)
if pro_alt is not None:
    open(pro_ziel, 'w', encoding='utf-8').write(pro_alt)
bahnen = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK']
print('Bahnen: %d, Durchkontaktierungen: %d' % (len(bahnen), len(board.GetTracks()) - len(bahnen)))
