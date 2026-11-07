# Baugruppe Gehaeuse + Platine. Version 00.01, Stand 07.11.2026.
# Im laufenden FreeCAD ausfuehren (braucht die Oberflaeche wegen der Farben); PLATINE = KiCad-Export
# ("pcb export step --subst-models --user-origin 0x0mm"). Alle Teile liegen schon in derselben Lage wie der Export,
# die Wanne ist festgesetzt; Verbindungen zwischen den Teilen gibt es nicht.
import os
import FreeCAD as App, FreeCADGui as Gui, Part, ImportGui

ORDNER = os.environ.get('GEHAEUSE_ORDNER', globals().get('ORDNER', ''))
PLATINE = os.environ.get('PLATINE_STEP', globals().get('PLATINE', ''))

doc = App.newDocument('Baugruppe_Robnet_v00_01')
bg = doc.addObject('Assembly::AssemblyObject', 'Baugruppe')
bg.Type = 'Assembly'
gelenke = bg.newObject('Assembly::JointGroup', 'Verbindungen')

teile = {}
for name, farbe, durch in (('Wanne', (0.92, 0.84, 0.59), 0), ('Deckel', (0.67, 0.82, 0.92), 55)):
    o = bg.newObject('Part::Feature', name)
    o.Shape = Part.read(os.path.join(ORDNER, name + '_v00.01.step'))
    o.ViewObject.ShapeColor = farbe
    o.ViewObject.Transparency = durch
    teile[name] = o

vorher = set(x.Name for x in doc.Objects)
ImportGui.insert(PLATINE, doc.Name)
neu = [x for x in doc.Objects if x.Name not in vorher]
oberste = [x for x in neu if not any(p in neu for p in x.InList)]
pl = doc.addObject('App::Part', 'Platine')
bg.addObject(pl)
for x in oberste:
    pl.addObject(x)
doc.recompute()
try:
    import JointObject
    fest = gelenke.newObject('App::FeaturePython', 'Wanne_fest')
    JointObject.GroundedJoint(fest, teile['Wanne'])
    JointObject.ViewProviderGroundedJoint(fest.ViewObject)
    print('Wanne festgesetzt')
except Exception as ex:
    print('Festsetzen nicht moeglich:', ex)
doc.recompute()
Gui.ActiveDocument.ActiveView.viewIsometric()
Gui.SendMsgToActiveView('ViewFit')
doc.saveAs(os.path.join(ORDNER, 'Baugruppe_Robnet_v00.01.FCStd'))
print('Teile', len(doc.Objects), 'neu aus STEP', len(neu), 'oberste', [x.Name for x in oberste][:5])
print('Datei', doc.FileName, 'Groesse MB', round(os.path.getsize(doc.FileName) / 1e6, 1))
