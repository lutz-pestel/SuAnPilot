# Gehaeuse Robnet-Analyse (SMD-Platine). Version 00.01, Stand 07.11.2026 (keine Kabelzungen, Betreiber).
# Anforderungen: ../../konzeption/Gehaeuse_Anforderungen.md
# Aufruf: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" gehaeuse_v00.01.py  (Umgebung PLATINE_STEP = Platine aus kicad-cli
#         "pcb export step --subst-models --user-origin 0x0mm", AUSGABE_NETZ = Ordner fuer die Bilddaten)
# Lage wie der KiCad-Export: x nach rechts, y nach oben (y = -KiCad-y), z = 0 Unterseite Platine, z = 1,6 Oberseite.
# Masse in mm. Alles hier aendern, nichts von Hand im Modell.
import math, os
import FreeCAD as App, Part
from FreeCAD import Vector as V

HIER = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
HIER = os.environ.get('GEHAEUSE_ORDNER', HIER)
PLATINE = os.environ.get('PLATINE_STEP', '')
NETZ = os.environ.get('AUSGABE_NETZ', '')

M = dict(
    Wand=2.5, Boden=2.5, Dach=2.0,
    Spalt_rechts_oben_unten=0.5,   # Platine 100 x 100, Toleranz JLC3DP +-0,2
    Spalt_links=1.5,               # USB-Buchsen des Raspberry ragen 1,2 ueber die Platine
    Frei_unter_Platine=4.0,        # Loetstellen enden 2,41 unter der Platine (Modell)
    z_Rand=17.2,                   # Stecker enden bei 16,73, Spalt zum Deckel 0,47
    z_Dach_innen=21.6,             # Raspberry-Schrauben enden bei 20,59
    Stift_D=2.7, Stift_ueber=2.6,  # Loch in der Platine 3,2
    Saeule_D=7.0,
    Rast_Winkel=60.0,              # Schraege beider Nasenseiten gegen die Waagerechte: kraftschluessig, kein Riegel
    PCB_Haken_B=5.0, PCB_Haken_Dicke=2.5, PCB_Haken_Fuss=15.7, PCB_Eingriff=0.6,
    Deckel_Arm_B=10.0, Deckel_Arm_Dicke=1.6, Deckel_Eingriff=0.6,
    Lippe_Tiefe=3.0, Lippe_Dicke=1.3,
    Rippe_Hoehe=3.6, Rippe_Dicke=1.6,   # unter dem Dach; Raspberry-Platte endet bei 17,6, Rippe beginnt bei 18,0
    Lasche_Dicke=5.0, Lasche_Loch=4.5,
    Gravur=0.8,
)
W = M['Wand']
xi0, xi1 = -M['Spalt_links'], 100 + M['Spalt_rechts_oben_unten']
yi0, yi1 = -100 - M['Spalt_rechts_oben_unten'], M['Spalt_rechts_oben_unten']
xo0, xo1, yo0, yo1 = xi0 - W, xi1 + W, yi0 - W, yi1 + W
zf1 = -M['Frei_unter_Platine']
zf0 = zf1 - M['Boden']
zr = M['z_Rand']
zdi = M['z_Dach_innen']
zdo = zdi + M['Dach']
LOECHER = [(3.8, -3.8), (96.2, -3.8), (3.8, -96.2), (96.2, -96.2)]


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def zyl(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0))


def zyl_x(d, x0, x1, y, z):
    return Part.makeCylinder(d / 2, x1 - x0, V(x0, y, z), V(1, 0, 0))


def zyl_y(d, y0, y1, x, z):
    return Part.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def rund(x0, x1, y0, y1, z0, z1, r):
    """Quader mit senkrechten Eckradien."""
    k = box(x0, x1, y0, y1, z0, z1)
    return k.makeFillet(r, [e for e in k.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])


def prisma_xz(punkte, y0, y1):
    p = [V(x, y0, z) for x, z in punkte]
    return Part.Face(Part.makePolygon(p + [p[0]])).extrude(V(0, y1 - y0, 0))


def prisma_yz(punkte, x0, x1):
    p = [V(x0, y, z) for y, z in punkte]
    return Part.Face(Part.makePolygon(p + [p[0]])).extrude(V(x1 - x0, 0, 0))


SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', 'J': 'bcde', 'P': 'abfge', 'v': 'cde'}


def schrift(text, h, x, y, z, tiefe, unten=False):
    """Gravur aus geraden Balken (Stiftbreite 1,0, Luecken ueber 0,8: JLC3DP-Regel). Mitte auf x, Unterkante auf y.
    unten=True: von unten lesbar."""
    s_, b_, luecke = 1.0, 0.6 * h, 1.4
    balken = {'a': (0, b_, h - s_, h), 'd': (0, b_, 0, s_), 'g': (0, b_, (h - s_) / 2, (h + s_) / 2),
              'b': (b_ - s_, b_, h / 2, h), 'c': (b_ - s_, b_, 0, h / 2), 'e': (0, s_, 0, h / 2), 'f': (0, s_, h / 2, h)}
    k, cx = None, 0.0
    for ch in text:
        if ch == '.':
            teile = [box(cx, cx + s_, 0, s_, 0, tiefe)]
            cx += s_ + luecke
        else:
            teile = [box(cx + b[0], cx + b[1], b[2], b[3], 0, tiefe) for b in (balken[q] for q in SEG[ch])]
            cx += b_ + luecke
        for t in teile:
            k = t if k is None else k.fuse(t)
    k = k.removeSplitter()
    k.translate(V(-(cx - luecke) / 2, 0, 0))
    if unten:
        k.rotate(V(0, 0, 0), V(0, 1, 0), 180)
        k.translate(V(0, 0, tiefe))
    k.translate(V(x, y, z))
    return k


# ---------- Wanne ----------
wanne = rund(xo0, xo1, yo0, yo1, zf0, zr, 3.0)
wanne = wanne.cut(rund(xi0, xi1, yi0, yi1, zf1, zr + 1, 1.5))

# Eckensaeulen mit Stift (Kraft vom Stecker: Stift -> Saeule -> Wand und Boden)
for x, y in LOECHER:
    ex = xi0 if x < 50 else xi1
    ey = yi0 if y < -50 else yi1
    s = zyl(M['Saeule_D'], zf1, 0, x, y)
    s = s.fuse(box(min(ex, x), max(ex, x), y - 3.5, y + 3.5, zf1, 0))
    s = s.fuse(box(x - 3.5, x + 3.5, min(ey, y), max(ey, y), zf1, 0))
    s = s.fuse(box(min(ex, x), max(ex, x), min(ey, y), max(ey, y), zf1, 0))
    stift = zyl(M['Stift_D'], 0, M['Stift_ueber'] - 0.6, x, y)
    spitze = Part.makeCone(M['Stift_D'] / 2, M['Stift_D'] / 2 - 0.6, 0.6, V(x, y, M['Stift_ueber'] - 0.6))
    wanne = wanne.fuse(s).fuse(stift).fuse(spitze)

# Zwei Federarme fuer die Platine (links, rechts mittig): Nase beidseitig schraeg, haelt durch Kraftschluss.
# Beim Anheben schiebt die Platinenkante die Nase selbst nach aussen; Druecken mit dem Finger hilft nur.
HAKEN = (('links', -25.0), ('rechts', -50.0))
hb, hd, hf, he = M['PCB_Haken_B'], M['PCB_Haken_Dicke'], M['PCB_Haken_Fuss'], M['PCB_Eingriff']
st = math.tan(math.radians(M['Rast_Winkel']))
zk = 1.7                            # Beruehrpunkt der Schraege an der Platinenkante (0,1 ueber der Oberseite)
hu = zk - 0.5 * st                  # Unterkante der Nase
for seite, yc in HAKEN:
    if seite == 'links':
        w0, w1 = xo0 - 0.1, xi0 + 0.1
        z_sp = zk + he * st
        nase = prisma_xz([(xi0 - 0.05, hu), (-0.5, hu), (he, z_sp), (he, z_sp + 0.9), (xi0 - 0.05, z_sp + 0.9 + (he - xi0) * st)], yc - hb / 2, yc + hb / 2)
        auflage = box(xi0, 1.5, yc - hb / 2, yc + hb / 2, zf1, 0)
    else:
        w0, w1 = xi1 - 0.1, xo1 + 0.1
        z_sp = zk + he * st
        nase = prisma_xz([(xi1 + 0.05, hu), (100.0 - he, z_sp), (100.0 - he, z_sp + 0.9), (xi1 + 0.05, z_sp + 0.9 + (xi1 - 100.0 + he) * st)], yc - hb / 2, yc + hb / 2)
        auflage = box(98.5, xi1, yc - hb / 2, yc + hb / 2, zf1, 0)
    for sy in (-1, 1):
        ym = yc + sy * (hb / 2 + 0.5)
        wanne = wanne.cut(box(w0, w1, ym - 0.5, ym + 0.5, 0.0, hf))
        wanne = wanne.cut(zyl_x(1.0, w0, w1, ym, hf))
    wanne = wanne.cut(box(w0, w1, yc - hb / 2 - 0.1, yc + hb / 2 + 0.1, 0.0, hu))
    wanne = wanne.fuse(nase).fuse(auflage)

# Oeffnungen fuer Stecker und USB, nach oben offen
SP = 0.5
for x0, x1 in ((59.4, 90.0), (12.3, 22.6)):            # J1, J2 oben
    wanne = wanne.cut(box(x0 - SP, x1 + SP, yi1 - 0.1, yo1 + 0.1, 1.2, zr + 1))
wanne = wanne.cut(box(59.4 - SP, 90.0 + SP, yo0 - 0.1, yi0 + 0.1, 1.2, zr + 1))   # J3 unten
wanne = wanne.cut(box(xo0 - 0.1, xi0 + 0.1, -55.2 - SP, -44.7 + SP, 7.14, zr + 1))  # USB links
# HDMI des Raspberry (Buchse bei y -79, Mitte 11,0 ueber der Unterseite); Annahme Stecker bis 17 breit, 10 hoch, nach oben offen
wanne = wanne.cut(box(xo0 - 0.1, xi0 + 0.1, -87.5, -70.5, 5.5, zr + 1))
# Griffraum Speicherkarte, untere Wand
wanne = wanne.cut(box(7.0, 24.0, yo0 - 0.1, yi0 + 0.1, 9.0, zr + 1))
# Rastfenster fuer den Deckel, obere und untere Wand
FX0, FX1 = 35.5, 46.5    # Nase 10 breit, je 0,5 Luft
FZ0, FZ1 = 6.5, 11.0     # Nase beginnt bei 7,06
wanne = wanne.cut(box(FX0, FX1, yi1 - 0.1, yo1 + 0.1, FZ0, FZ1))
wanne = wanne.cut(box(FX0, FX1, yo0 - 0.1, yi0 + 0.1, FZ0, FZ1))
# Lueftung rechte Wand, je drei Schlitze ober- und unterhalb des Federarms
for yv in (-26.0, -32.0, -38.0, -62.0, -68.0, -74.0):
    wanne = wanne.cut(box(xi1 - 0.1, xo1 + 0.1, yv - 1.0, yv + 1.0, 5.0, 13.0))

# Laschen fuer Holzschrauben
LASCHE = [(-11.0, -8.0), (-11.0, -92.0), (110.0, -8.0), (110.0, -92.0)]
for x, y in LASCHE:
    if x < 50:
        l = rund(x - 6.0, xo0 + 1.0, y - 7.0, y + 7.0, zf0, zf0 + M['Lasche_Dicke'], 2.5)
    else:
        l = rund(xo1 - 1.0, x + 6.0, y - 7.0, y + 7.0, zf0, zf0 + M['Lasche_Dicke'], 2.5)
    wanne = wanne.fuse(l).cut(zyl(M['Lasche_Loch'], zf0 - 1, zf0 + M['Lasche_Dicke'] + 1, x, y))

# Beschriftung Unterseite
wanne = wanne.cut(schrift('v00.01', 6.0, 50.0, -53.0, zf0 - 0.01, M['Gravur'] + 0.01, unten=True))
wanne = wanne.removeSplitter()

# ---------- Deckel ----------
deckel = rund(xo0, xo1, yo0, yo1, zr, zdo, 3.0)
deckel = deckel.cut(rund(xi0, xi1, yi0, yi1, zr - 1, zdi, 1.5))
try:
    kanten = [e for e in deckel.Edges if abs(e.Vertexes[0].Z - zdo) < 1e-6 and abs(e.Vertexes[-1].Z - zdo) < 1e-6]
    deckel = deckel.makeFillet(1.5, kanten)
except Exception as ex:
    print('Deckelkante nicht gerundet:', ex)

# Rippen unter dem Dach in beiden Achsen, Lage so, dass sie nicht ueber den Jumpern liegen und die Schrauben des Raspberry frei bleiben
zrb = zdi - M['Rippe_Hoehe']
rd = M['Rippe_Dicke']
for y in (-14.0, -44.0, -72.0):
    deckel = deckel.fuse(box(xi0 - 0.01, xi1 + 0.01, y - rd / 2, y + rd / 2, zrb, zdi + 0.01))
for x in (31.5, 58.0, 92.0):
    deckel = deckel.fuse(box(x - rd / 2, x + rd / 2, yi0 - 0.01, yi1 + 0.01, zrb, zdi + 0.01))

# Schnapparme oben und unten, Fuss am Dach; Nase beidseitig schraeg, Fenster der Wanne nimmt sie auf
ab, ad, ae = M['Deckel_Arm_B'], M['Deckel_Arm_Dicke'], M['Deckel_Eingriff']
ax0 = (FX0 + FX1) / 2 - ab / 2
ax1 = ax0 + ab
z_oben_sp = (FZ1 - 0.1) - ae * st   # Schraege beruehrt die Fensteroberkante an der Wandinnenseite mit 0,1 Luft
z_unten_sp = z_oben_sp - 0.9
az0 = z_unten_sp - (ae + 0.5) * st
for oben in (True, False):
    if oben:
        y_a, y_i, spitze, sgn = yi1 - 0.5, yi1 - 0.5 - ad, yi1 + ae, 1
    else:
        y_a, y_i, spitze, sgn = yi0 + 0.5, yi0 + 0.5 + ad, yi0 - ae, -1
    arm = box(ax0, ax1, min(y_a, y_i), max(y_a, y_i), az0, zdi + 0.01)
    nase = prisma_yz([(y_a - sgn * 0.05, az0), (spitze, z_unten_sp), (spitze, z_oben_sp), (y_a - sgn * 0.05, z_oben_sp + (ae + 0.5) * st)], ax0, ax1)
    deckel = deckel.fuse(arm).fuse(nase)

# Fuehrung: umlaufende Lippe, greift 3 mm in die Wanne; am Dach angebunden. Unterbrochen an J1, J2, J3, USB, HDMI und den Schnapparmen.
lt, ls = M['Lippe_Tiefe'], 0.2      # ls = Spalt zur Wanneninnenwand
ld = M['Lippe_Dicke']
ring_z = rund(xi0 - 0.01, xi1 + 0.01, yi0 - 0.01, yi1 + 0.01, zr, zdi + 0.01, 1.5)
ring_z = ring_z.cut(rund(xi0 + ls + ld, xi1 - ls - ld, yi0 + ls + ld, yi1 - ls - ld, zr - 1, zdi + 1, 1.0))
lippe = rund(xi0 + ls, xi1 - ls, yi0 + ls, yi1 - ls, zr - lt, zr + 0.01, 1.3)
lippe = lippe.cut(rund(xi0 + ls + ld, xi1 - ls - ld, yi0 + ls + ld, yi1 - ls - ld, zr - lt - 1, zr + 1, 1.0))
for x0, x1 in ((59.4 - SP, 90.0 + SP), (12.3 - SP, 22.6 + SP)):
    lippe = lippe.cut(box(x0, x1, -5.0, yi1 + 1, zr - lt - 1, zr + 1))         # J1, J2
lippe = lippe.cut(box(59.4 - SP, 90.0 + SP, yi0 - 1, -95.0, zr - lt - 1, zr + 1))  # J3
lippe = lippe.cut(box(xi0 - 1, 5.0, -87.5, -70.5, zr - lt - 1, zr + 1))        # HDMI
lippe = lippe.cut(box(xi0 - 1, 5.0, -55.2 - SP, -44.7 + SP, zr - lt - 1, zr + 1))  # USB
for y0, y1 in ((-5.0, yi1 + 1), (yi0 - 1, -95.0)):                             # Schnapparme frei
    frei = box(ax0 - 0.5, ax1 + 0.5, y0, y1, zr - lt - 1, zdi + 0.02)
    lippe = lippe.cut(frei)
    ring_z = ring_z.cut(frei)
deckel = deckel.fuse(ring_z).fuse(lippe)

deckel = deckel.removeSplitter()

print('Wanne gueltig', wanne.isValid(), 'Volumen cm3 %.1f' % (wanne.Volume / 1000), 'Masse', wanne.BoundBox)
print('Deckel gueltig', deckel.isValid(), 'Volumen cm3 %.1f' % (deckel.Volume / 1000), 'Masse', deckel.BoundBox)
print('Koerper Wanne', len(wanne.Solids), 'Deckel', len(deckel.Solids))

# ---------- Masstabelle mit abgeleiteten Waenden und Dehnung ----------
def dehnung(delta, dicke, laenge):
    return 3 * delta * dicke / (2 * laenge ** 2) * 100


def haltekraft(e_mod, breite, dicke, laenge, delta, reib=17.0):
    # Federkraft des Arms mal Keilwirkung der Schraege (Reibwinkel angenommen)
    i_ = breite * dicke ** 3 / 12
    k_ = 3 * e_mod * i_ / laenge ** 3
    return k_ * delta * math.tan(math.radians(90 - M['Rast_Winkel'] + reib))


L_pcb = hf - 3.0
L_dk = zdi - (z_oben_sp + z_unten_sp) / 2
abg = dict(
    Wand_Arm_Platine=hd,
    Wand_hinter_Deckelnase=W - ae,
    Wand_Boden_ueber_Gravur=M['Boden'] - M['Gravur'],
    Dehnung_Platinenarm_Prozent=dehnung(he + 0.4, hd, L_pcb),
    Dehnung_Deckelarm_Prozent=dehnung(ae + 0.4, ad, L_dk),
    Haltekraft_Platinenarm_N=haltekraft(2800, hb, hd, L_pcb, he),   # Wanne Grey, Biegemodul 2705-2875
    Haltekraft_Deckelarm_N=haltekraft(2100, ab, ad, L_dk, ae),
)
for k, v in abg.items():
    print('%s = %.2f' % (k, v))

doc = App.newDocument('Gehaeuse_Robnet')
tab = doc.addObject('Spreadsheet::Sheet', 'Masse')
for i, (k, v) in enumerate(list(M.items()) + list(abg.items()), start=1):
    tab.set('A%d' % i, k)
    tab.set('B%d' % i, str(round(v, 3)))
for name, form in (('Wanne', wanne), ('Deckel', deckel)):
    o = doc.addObject('Part::Feature', name)
    o.Shape = form
    o.Visibility = True      # ohne Bildschirm gespeichert waere es sonst beim Oeffnen ausgeblendet
doc.recompute()
doc.saveAs(os.path.join(HIER, 'Gehaeuse_Robnet_v00.01.FCStd'))
wanne.exportStep(os.path.join(HIER, 'Wanne_v00.01.step'))
deckel.exportStep(os.path.join(HIER, 'Deckel_v00.01.step'))

# ---------- Pruefung gegen die Platine ----------
if PLATINE:
    platine = Part.read(PLATINE)
    print('Platine', platine.BoundBox, len(platine.Solids))
    def kollision(name, teil):
        n = 0
        tb = teil.BoundBox
        for i, sol in enumerate(platine.Solids):
            if not tb.intersect(sol.BoundBox):
                continue
            v = teil.common(sol).Volume
            if v > 1e-3:
                n += 1
                b = sol.BoundBox
                print('  KOLLISION %s mit Koerper #%d: %.2f mm3, x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (name, i, v, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
        print('%s: %d Kollisionen' % (name, n))
    kollision('Wanne', wanne)
    kollision('Deckel', deckel)
    v = wanne.common(deckel).Volume
    print('Wanne gegen Deckel: %.3f mm3' % v)
    # Weg des Deckelarms beim Ausfedern und der Platinenhaken-Nasen
    weg = box(ax0, ax1, yi1 - 0.5 - ad - 1.6, yi1 - 0.5, az0, zdi - 0.5).fuse(box(ax0, ax1, yi0 + 0.5, yi0 + 0.5 + ad + 1.6, az0, zdi - 0.5))
    kollision('Federweg Deckelarme', weg)

if NETZ:
    import numpy as np
    def netz(form, name, abw=0.05):
        pts, tris = form.tessellate(abw)
        np.savez_compressed(os.path.join(NETZ, name + '.npz'), p=np.array([[q.x, q.y, q.z] for q in pts], dtype=np.float32), t=np.array(tris, dtype=np.int32))
    netz(wanne, 'wanne')
    netz(deckel, 'deckel')
    if PLATINE:
        netz(platine, 'platine', 0.1)
print('FERTIG')
