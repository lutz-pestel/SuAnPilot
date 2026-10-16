# Eigene 3D-Modelle (STEP) fuer Teile ohne frei ladbares Herstellermodell. Version 00.01, Stand 16.10.2026.
# Aufruf: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" eigene_modelle.py   (schreibt die STEP-Dateien in diesen Ordner)
# Masse in mm. Ursprung: Pin 1 bzw. Mitte Unterkante; z = 0 ist die Platinenoberseite (Sitzflaeche).
# Quelle je Mass im Kommentar; "ANNAHME" = nicht belegt, vor der Gehaeusekonstruktion am echten Teil messen.
import os, Part, FreeCAD as App
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__))


def box(l, b, h, x=0, y=0, z=0):
    return Part.makeBox(l, b, h, V(x, y, z))


def zyl(r, h, x=0, y=0, z=0, richtung=V(0, 0, 1)):
    return Part.makeCylinder(r, h, V(x, y, z), richtung)


def speichern(name, *teile):
    form = teile[0]
    for t in teile[1:]:
        form = form.fuse(t)
    form = form.removeSplitter()
    pfad = os.path.join(OUT, name + '.step')
    form.exportStep(pfad)
    bb = form.BoundBox
    print('%-55s %6.2f x %6.2f x %6.2f' % (name, bb.XLength, bb.YLength, bb.ZLength))


def radial_kondensator(name, l, t, h, raster, draht, unten=3.0):
    """Bedrahteter Keramik-Vielschichtkondensator: Koerper ueber den Draehten, Draehte bis 'unten' unter die Platine."""
    koerper = box(l, t, h - 1.5, -l / 2 + raster / 2, -t / 2, 1.5)
    koerper = koerper.makeFillet(min(t, l) / 2 - 0.05, koerper.Edges)
    d1 = zyl(draht / 2, 1.5 + unten + 0.5, 0, 0, -unten)
    d2 = zyl(draht / 2, 1.5 + unten + 0.5, raster, 0, -unten)
    speichern(name, koerper, d1, d2)


# TDK FG16X7R1H475KRT06: Koerper 5,5 x 3,5 mm, Hoehe 6,0 mm, Raster 2,5 mm, Draht 0,5 mm (TDK-Katalog FG 11/2024, S. 39 und 42)
radial_kondensator('TDK_FG16X7R1H475KRT06_eigen', 5.5, 3.5, 6.0, 2.5, 0.5)
# KEMET C320C104K5R5TA: L 5,08, T 3,18, H 5,84 (je max.), Raster 2,54, Draht 0,51 (KEMET C1053 GoldMax 300, 08/2025)
radial_kondensator('KEMET_C320C104K5R5TA_eigen', 5.08, 3.18, 5.84, 2.54, 0.51)

# Harwin M7566-05: 5,00 x 2,30 x 6,30 mm (Harwin-Produktseite, Abschnitt Dimensions), offen oben; sitzt auf der
# Stiftleiste (Kunststoff 2,5 mm hoch, KiCad PinHeader) -> Unterkante z = 2,5. Kontaktoeffnungen 1,0 x 1,0 ANNAHME.
j = box(5.0, 2.3, 6.3, -1.27, -1.15, 2.5)
for x in (0.0, 2.54):
    j = j.cut(box(1.0, 1.0, 6.4, x - 0.5, -0.5, 2.4))
speichern('Harwin_M7566-05_eigen', j)

# Feinsicherung 5 x 20 mm (Schurter 0034.3117, 1 A T): Normmass IEC 60127-2: Kappen Durchmesser 5,2, Laenge 20,0;
# Kappenlaenge 5,0 und Glasrohr Durchmesser 4,8 ANNAHME. Achse in x, Mitte im Ursprung (liegt im Halter).
glas = zyl(2.4, 20.0, -10.0, 0, 0, V(1, 0, 0))
kappe1 = zyl(2.6, 5.0, -10.0, 0, 0, V(1, 0, 0))
kappe2 = zyl(2.6, 5.0, 5.0, 0, 0, V(1, 0, 0))
speichern('Schurter_0034.3117_Sicherung_5x20_eigen', glas, kappe1, kappe2)

# Raspberry Pi Zero 2 W, Lage wie geliefert (Bauteilseite oben, z = 0 = Unterseite der Leiterplatte).
# Umriss 65 x 30, Loecher 2,75 mm bei 3,5 mm vom Rand, Abstand 58 x 23; Stiftleiste Mitte 32,5 mm von links, 3,5 mm von
# der oberen Kante; HDMI 12,4 / USB 41,4 / USB 54 mm von links (Raspberry-Pi-Zeichnung 2021-10, datenblaetter/).
# Breite und Ueberstand der Buchsen aus der KiCad-Bauform (Fertigungsebene): HDMI 11,3 breit, 0,7 ueber; USB je 8,0 breit,
# 1,8 ueber; Kamerabuchse 17,0 breit, 1,2 ueber. ANNAHME: Leiterplatte 1,0 dick, Eckradius 3,0, Hoehen HDMI 3,2, USB 2,9,
# Kamera 1,3, SD-Halter 12 x 11,5 x 1,4, Stiftleiste Kunststoff 2,5 hoch, Stifte 0,64 quadratisch, 6,0 ueber Kunststoff, 3,0 unter der Platte.
DICKE = 1.0
plf = Part.Face(Part.Wire(Part.makePolygon([V(3, 0, 0), V(62, 0, 0), V(65, 3, 0), V(65, 27, 0), V(62, 30, 0), V(3, 30, 0), V(0, 27, 0), V(0, 3, 0), V(3, 0, 0)])))
platte = plf.extrude(V(0, 0, DICKE))
for (x, y) in ((3.5, 3.5), (61.5, 3.5), (3.5, 26.5), (61.5, 26.5)):
    platte = platte.cut(zyl(1.375, DICKE + 1, x, y, -0.5))
teile = [platte]
teile.append(box(11.3, 7.5 + 0.7, 3.2, 12.4 - 5.65, -0.7, DICKE))           # Mini-HDMI
for xm in (41.4, 54.0):
    teile.append(box(8.0, 5.6 + 1.8, 2.9, xm - 4.0, -1.8, DICKE))           # Micro-USB
teile.append(box(1.2 + 3.0, 17.0, 1.3, 65 - 3.0, 6.5, DICKE))               # Kamerabuchse (rechtes Ende)
teile.append(box(12.0, 11.5, 1.4, -0.5, 9.0, DICKE))                       # SD-Halter (linkes Ende)
teile.append(box(50.8, 5.08, 2.5, 32.5 - 25.4, 26.5 - 2.54, DICKE))         # Stiftleiste Kunststoff
for k in range(20):
    for zeile in (0, 1):
        x = 32.5 - 24.13 + 2.54 * k
        y = 26.5 - 1.27 + 2.54 * zeile
        teile.append(box(0.64, 0.64, 3.0 + DICKE + 2.5 + 6.0, x - 0.32, y - 0.32, -3.0))
speichern('RaspberryPi_Zero2W_eigen', *teile)

# OTG-Adapter LogiLink AA0035 (Micro-B-Stecker an 0,2-m-Kabel auf A-Buchse; Reichelt-Daten): nur das Steckerende.
# Steckteil 6,85 x 1,8 (USB-Micro-Norm), Laenge 6,0 ANNAHME; Umspritzung 10,5 x 7,0 x 18,0 ANNAHME; Kabel Durchmesser 3,5,
# 30 mm Stueck ANNAHME. Steckrichtung -y, Ursprung Mitte Steckerspitze.
stecker = box(6.85, 6.0, 1.8, -3.425, 0, -0.9)
umsp = box(10.5, 18.0, 7.0, -5.25, 6.0, -3.5)
kabel = zyl(1.75, 30.0, 0, 24.0, 0, V(0, 1, 0))
speichern('LogiLink_AA0035_OTG-Stecker_eigen', stecker, umsp, kabel)

# Steuerleitung BKL Li12Y11Y 6 x 0,5 mm2 (Reichelt PUR 6X0,50 5): Aussendurchmesser 5,8 mm (Reichelt-Daten); 50-mm-Stueck.
speichern('BKL_Li12Y11Y_6x0,5_Steuerleitung_eigen', zyl(2.9, 50.0, 0, 0, 0, V(0, 1, 0)))
