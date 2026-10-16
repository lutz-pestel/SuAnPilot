# Ergaenzt die Leiterbahnen der Platine Robnet-Analyse Linie B (SMD) v00.01. Version 00.01, Stand 16.10.2026.
# Liest die platzierte Platine (ohne Bahnen, aus ../platine_erzeugen/robnet_platine.py) und schreibt die fertige Platine.
# Aufruf mit dem Python von KiCad (KiCad geschlossen):
#   "C:/Program Files/KiCad/10.0/bin/python.exe" robnet_bahnen.py ../platine_erzeugen/Robnet-Analyse_platziert.kicad_pcb ../Robnet-Analyse.kicad_pcb
# Schutz: Liegt ein Bauteil im Ziel anders als in der platzierten Platine (in KiCad verschoben), bricht das Skript ab;
# die neue Lage erst ins Platzierungsskript uebernehmen. Bahnen, die nur im Ziel stehen (in KiCad gezeichnet), ebenso;
# Ueberschreiben nur mit --ueberschreiben.
# Gruppen nacheinander, je Gruppe vom Betreiber freigegeben: 1 Versorgung und Masse (16.10.2026).
# Masse in mm, Ursprung oben links, y nach unten. Lagen: O = Oberseite (F.Cu), U = Unterseite (B.Cu, Massefläche).
import sys, os
import pcbnew

QUELLE, ZIEL = sys.argv[1], sys.argv[2]
UEBERSCHREIBEN = '--ueberschreiben' in sys.argv
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
# Noch offen: +12V_F zum Teiler R21 (Bordspannung) kommt mit Gruppe 3 (Teiler -> Wandler).

# 5 V: U3 -> Zero Pin 2 und 4, 1,5 mm oben, aussen herum (oben an der Kante, links unter dem Zero), damit die Mitte
# zwischen Zero und Wandlern fuer SPI frei bleibt
bahn('+5V', 1.5, O, (52.08, 5.5), (52.08, 2.6), (9.0, 2.6), (9.0, 85.2), (28.37, 85.2), (28.37, 83.03), (28.37, 80.49))

# 3,3 V vom Zero (Pin 1 und 17). Die Messleitung jedes Kanals laeuft oben quer unter ihrer BAT54S durch, deshalb
# fuehrt die 3,3 V unten (Sammelleitung x = 57,3 rechts der Dioden, je Diode eine Durchkontaktierung).
bahn('+3V3', 0.4, O, (25.83, 62.71), (23.6, 62.71), (23.6, 83.03), (25.83, 83.03))      # Pin 17 - Pin 1, links unter dem Zero
bahn('+3V3', 0.3, U, (25.83, 62.71), (27.1, 63.98), (29.6, 63.98), (29.92, 64.3))       # zwischen den Stiftreihen heraus
bahn('+3V3', 0.4, U, (29.92, 64.3), (57.3, 64.3))
bahn('+3V3', 0.4, O, (34.5, 62.91), (34.5, 64.3))                                        # R4 (Referenz)
via('+3V3', 34.5, 64.3)
bahn('+3V3', 0.4, U, (36.83, 64.3), (36.83, 50.0))                                       # U2 VDD
bahn('+3V3', 0.4, O, (33.0, 50.48), (36.83, 50.48))                                      # C2
bahn('+3V3', 0.4, U, (25.83, 83.03), (27.2, 84.4), (36.83, 84.4))                        # U6 VDD
bahn('+3V3', 0.4, O, (33.0, 84.47), (36.83, 84.47))                                      # C3
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
masse((33.0, 81.53), (34.6, 81.53))                       # C3
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
    if verschoben:
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
