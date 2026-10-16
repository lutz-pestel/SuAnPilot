# Legt 3D-Modelle in die Lage der KiCad-Bauformen (Unterordner kicad-lage/), damit KiCad sie ohne Drehung einbindet.
# Version 00.01, Stand 16.10.2026. Aufruf: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" kicad_lage.py
# Koordinaten wie KiCad-3D: Ursprung = Pin 1 der Bauform, x nach rechts, y nach OBEN (= -y der Bauform), z = Platinenoberseite.
# Platinendicke 1,6 mm (KiCad-Standard). ANNAHME = nicht belegt, am echten Teil pruefen.
import os, Part, FreeCAD as App
from FreeCAD import Vector as V, Matrix

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'kicad-lage')
os.makedirs(OUT, exist_ok=True)


def lade(name):
    s = Part.Shape()
    s.read(os.path.join(D, name))
    return s


def zus(*formen):
    return Part.makeCompound([f for f in formen])


def schreibe(name, form):
    form.exportStep(os.path.join(OUT, name + '.step'))
    b = form.optimalBoundingBox() if hasattr(form, 'optimalBoundingBox') else form.BoundBox
    print('%-48s x %7.2f..%7.2f  y %7.2f..%7.2f  z %7.2f..%7.2f' % (name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))


def verschoben(s, x, y, z):
    s = s.copy(); s.translate(V(x, y, z)); return s


def gedreht(s, grad, achse=V(0, 0, 1), punkt=V(0, 0, 0)):
    s = s.copy(); s.rotate(punkt, achse, grad); return s


# --- Phoenix-Leisten mit gestecktem Kabelstecker (J1, J3: 6-polig; J2: 2-polig)
# Leiste: senkrechte Pins bei x = 3,54 + 5,08 k, y = 10,0 im Modell -> verschieben um (-3,54; -10,0).
# Waagrechter Stift: Mitte z = 3,87, Spitze bei Leisten-y 1,2 (-> -8,8). Stecker: Federkontakte beginnen bei
# Stecker-y 10,82 (6-polig) bzw. 10,59 (2-polig), Mitte z 3,73; Kontaktmitte x 2,57 bzw. 2,54.
# Steckerlage: Federanfang an der Stiftspitze (ANNAHME: Stecker ganz eingesteckt).
leiste6 = verschoben(lade('PhoenixContact_1757284_MSTBA-2,5-6-G-5,08.step'), -3.54, -10.0, 0)
stecker6 = verschoben(lade('PhoenixContact_1757051_MSTB-2,5-6-ST-5,08.step'), -2.57, -8.8 - 10.82, 3.87 - 3.73)
schreibe('J_MSTBA-6-G_mit_MSTB-6-ST', zus(leiste6, stecker6))
leiste2 = verschoben(lade('PhoenixContact_1757242_MSTBA-2,5-2-G-5,08.step'), -3.54, -10.0, 0)
stecker2 = verschoben(lade('PhoenixContact_1757019_MSTB-2,5-2-ST-5,08.step'), -2.54, -8.8 - 10.59, 3.87 - 3.73)
schreibe('J_MSTBA-2-G_mit_MSTB-2-ST', zus(leiste2, stecker2))

# --- Bourns RLB0914: Draehte im Modell in y-Richtung, Koerper oben bei z 0 -> 90 Grad drehen, Draht 1 auf (0,0),
# Draht 2 auf (5,0), Koerperunterkante auf z = 0.
rlb = gedreht(lade('Bourns_RLB0914-100KL.step'), -90)
draehte = sorted([so for so in rlb.Solids if so.BoundBox.ZMin < -20], key=lambda q: q.BoundBox.Center.x)
m1 = draehte[0].BoundBox.Center
koerper_unten = min(so.optimalBoundingBox().ZMin for so in rlb.Solids if so.BoundBox.ZMin > -20)
rlb = verschoben(rlb, -m1.x, -m1.y, -koerper_unten)
schreibe('Bourns_RLB0914-100KL', rlb)

# --- Harwin-Jumper auf Stiftleiste: eigenes Modell hat die Kontakte bei (0,0) und (2,54;0) -> -90 Grad: (0,0), (0,-2,54)
j = gedreht(lade('Harwin_M7566-05_eigen.step'), -90)
schreibe('Harwin_M7566-05_auf_1x02', j)
# JP1, JP2 (2 x 3): zwei Jumper in Stellung "oben" (Pins 1-3 und 2-4)
schreibe('Harwin_M7566-05_2x_auf_2x03_oben', zus(j, verschoben(j, 2.54, 0, 0)))

# --- Sicherung 5 x 20 im Halter Schurter 0031.8201 (Pins bei x 0 und 22,5): Mitte x 11,25; Achshoehe z 8,0 ANNAHME
schreibe('Schurter_0034.3117_im_Halter', verschoben(lade('Schurter_0034.3117_Sicherung_5x20_eigen.step'), 11.25, 0, 8.0))

# --- Zero 2 W kopfueber auf der Buchsenleiste J5, mit Bolzen, Schrauben, microSD und OTG-Stecker.
# Buchsenleiste 8,5 hoch (KiCad PinSocket), darauf Kunststoff der Zero-Stiftleiste 2,5 -> Bauteilseite des Zero bei z 11,0,
# Leiterplattenrueckseite bei z 12,0. Zero-Koordinaten (eigene_modelle.py): Pin 1 bei (8,37; 25,23), SD-Ende x = 0,
# USB-Kante y = 0. Abbildung: x' = 25,23 - y, y' = 8,37 - x, z' = 12,0 - z (Drehung, keine Spiegelung).
M = Matrix(0, -1, 0, 25.23,
           -1, 0, 0, 8.37,
           0, 0, -1, 12.0,
           0, 0, 0, 1)
def auf_j5(s):
    s = s.copy(); s.transformShape(M); return s
zero = auf_j5(lade('RaspberryPi_Zero2W_eigen.step'))
# microSD: Kartenmodell 11 breit (x) x 15 lang (y); Laenge entlang Zero-x, 2,0 mm ueber das SD-Ende hinaus (ANNAHME),
# Mitte des Halters y 14,75, Hoehe z 1,15..2,25 (ANNAHME)
sd = gedreht(lade('FreeCAD-Bibliothek_microSD-Karte_generisch.step'), 90)       # -> x -15..0, y 0..11
sd = auf_j5(verschoben(sd, 13.0, 9.25, 1.15))
# OTG-Stecker in der USB-Datenbuchse (Zero-x 41,4): Spitze 6,0 tief eingesteckt ab Buchsenvorderkante y = -1,8
otg = gedreht(lade('LogiLink_AA0035_OTG-Stecker_eigen.step'), 180)              # Spitze bei y 0, Koerper nach -y
otg = auf_j5(verschoben(otg, 41.4, -1.8 + 6.0, 1.0 + 2.9 / 2))
# Bolzen M2,5 x 11 zwischen Platine (z 0) und Zero (z 11); Schrauben M2,5 x 5 von unten durch die Platine (Kopf unter
# z = -1,6) und von oben durch den Zero (Kopf auf z = 12,0)
bolzen = lade('Wuerth_970110151_WA-SSTII_M2,5x11.step')
schraube = lade('FreeCAD-Bibliothek_Schraube_M2,5x5_ISO4762.step')               # Kopf z 0..2,5, Schaft z -5..0
schraube_unten = verschoben(gedreht(schraube, 180, V(1, 0, 0)), 0, 0, -1.6)
schraube_oben = verschoben(schraube, 0, 0, 12.0)
teile = [zero, sd, otg]
for (x, y) in ((21.73, 4.87), (21.73, -53.13), (-1.27, 4.87), (-1.27, -53.13)):
    teile += [verschoben(bolzen, x, y, 5.5), verschoben(schraube_unten, x, y, 0), verschoben(schraube_oben, x, y, 0)]
schreibe('Zero2W_Baugruppe_kopfueber', zus(*teile))
