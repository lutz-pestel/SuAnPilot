# Schnitte als echte 3D-Koerper in einer eigenen FreeCAD-Datei. Version 00.01, Stand 07.11.2026.
# Im laufenden FreeCAD ausfuehren (ORDNER, PLATINE wie baugruppe_v00.01.py). Je Schnitt zwei Gruppen (beide Seiten); Schnittflaechen rot.
import os
import FreeCAD as App, FreeCADGui as Gui, Part
from FreeCAD import Vector as V

ORDNER = globals().get('ORDNER', '')
PLATINE = globals().get('PLATINE', '')
ROT = (0.80, 0.12, 0.12, 1.0)
FARBE = {'Wanne': (0.92, 0.84, 0.59, 1.0), 'Deckel': (0.55, 0.75, 0.92, 1.0), 'Platine': (0.35, 0.65, 0.42, 1.0)}
GROSS = (-60.0, 130.0, -130.0, 20.0, -20.0, 40.0)


def halb(achse, wert, gegen=False):
    """Quader um den behaltenen Teil: y >= wert, x >= wert oder z <= wert; gegen=True: die andere Seite."""
    x0, x1, y0, y1, z0, z1 = GROSS
    if achse == 'y':
        y0, y1 = (y0, wert) if gegen else (wert, y1)
    elif achse == 'x':
        x0, x1 = (x0, wert) if gegen else (wert, x1)
    else:
        z0, z1 = (wert, z1) if gegen else (z0, wert)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def schneide(form, b):
    """Schnitt je Koerper; Koerper ausserhalb bleiben weg, ganz innen liegende bleiben unberuehrt."""
    teile = []
    for sol in form.Solids:
        if not sol.BoundBox.intersect(b.BoundBox):
            continue
        c = sol.common(b)
        if c.Solids:
            teile.extend(c.Solids)
    return Part.makeCompound(teile)


def faerben(obj, farbe, achse, wert):
    n = {'x': V(1, 0, 0), 'y': V(0, 1, 0), 'z': V(0, 0, 1)}[achse]
    werte = []
    for f in obj.Shape.Faces:
        rot = False
        if f.Surface.TypeId == 'Part::GeomPlane':
            u0, u1, v0, v1 = f.ParameterRange
            if abs(abs(f.normalAt(u0, v0).dot(n)) - 1) < 1e-6 and abs(f.valueAt(u0, v0).dot(n) - wert) < 1e-3:
                rot = True
        werte.append(ROT if rot else farbe)
    obj.ViewObject.ShapeColor = farbe[:3]
    obj.ViewObject.DiffuseColor = werte


SCHNITTE = (
    ('A_Jumperreihe', 'y', -20.5, 'Front'), ('B_Rast_links', 'y', -25.0, 'Front'),
    ('C_Rast_rechts_USB_JP1', 'y', -50.0, 'Front'), ('D_Rippe_Raspberry', 'y', -72.0, 'Front'),
    ('I_HDMI', 'y', -79.0, 'Front'),
    ('E_Deckelrasten', 'x', 41.0, 'Left'), ('F_J1_JP3_J3', 'x', 82.32, 'Left'),
    ('G_J2_Raspberry_Karte', 'x', 15.0, 'Left'), ('H_waagerecht_Stifte_Nasen', 'z', 3.0, 'Top'),
)

formen = {'Wanne': Part.read(os.path.join(ORDNER, 'Wanne_v00.01.step')),
          'Deckel': Part.read(os.path.join(ORDNER, 'Deckel_v00.01.step')),
          'Platine': Part.read(PLATINE)}
doc = App.newDocument('Schnitte_Robnet_v00_01')
for name, achse, wert, sicht in SCHNITTE:
    for gegen in (False, True):
        gruppe = doc.addObject('App::DocumentObjectGroup', 'Schnitt_' + name + ('_Gegenseite' if gegen else ''))
        b = halb(achse, wert, gegen)
        for teil, form in formen.items():
            c = schneide(form, b)
            if not c.Solids:
                continue
            o = doc.addObject('Part::Feature', name[0] + ('g_' if gegen else '_') + teil)
            o.Shape = c
            gruppe.addObject(o)
            faerben(o, FARBE[teil], achse, wert)
        sichtbar = name.startswith('A_') and gegen
        gruppe.ViewObject.Visibility = sichtbar
        for o in gruppe.Group:
            o.ViewObject.Visibility = sichtbar
        print(gruppe.Name, [(o.Label, len(o.Shape.Solids)) for o in gruppe.Group])
doc.recompute()
Gui.ActiveDocument.ActiveView.viewRear()
Gui.SendMsgToActiveView('ViewFit')
doc.saveAs(os.path.join(ORDNER, 'Schnitte_Robnet_v00.01.FCStd'))
print('Datei', doc.FileName, 'MB', round(os.path.getsize(doc.FileName) / 1e6, 1))
