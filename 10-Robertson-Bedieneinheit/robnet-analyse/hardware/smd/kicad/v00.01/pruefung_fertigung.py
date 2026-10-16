# Prueft die Fertigungsdateien in production/ (Fabrication Toolkit) gegen Platine und Stueckliste. Linie B (SMD).
# Version 00.01, Stand 16.10.2026. Ablauf: 0-gesamtprojekt/fertigung/ablauf-smd-bestueckung.md, Schritt 4, Punkt 5.
# Aufruf (KiCad geschlossen), im Ordner kicad/v00.01:
#   "C:/Program Files/KiCad/10.0/bin/python.exe" pruefung_fertigung.py
# Prueft: jedes Teil mit LCSC-Nummer in Stueckliste und Positionsliste, kein selbst geloetetes Teil darin, gleiche
# LCSC-Nummern wie Platine und ../../bom/bom.csv, keine doppelten Bezeichner, hoechstens 200 Bezeichner je Zeile,
# Bezeichner in beiden Listen gleich geschrieben, alle Teile oben, Gerber und Bohrdaten im Archiv.
import csv, os, re, sys, zipfile
import pcbnew

HIER = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.join(HIER, 'production')
fehler = []

def lies(name):
    with open(os.path.join(PROD, name), encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

board = pcbnew.LoadBoard(os.path.join(HIER, 'Robnet-Analyse.kicad_pcb'))
platine = {}                                   # Bezeichner -> LCSC (leer = selbst geloetet)
for fp in board.GetFootprints():
    felder = {x.GetName(): x.GetText() for x in fp.GetFields()}
    platine[fp.GetReference()] = felder.get('LCSC Part #', '')
jlc = {r for r, l in platine.items() if l}

# Stueckliste
bom = {}
for z in lies('bom.csv'):
    refs = [r.strip() for r in z['Designator'].split(',')]
    if len(refs) > 200:
        fehler.append('mehr als 200 Bezeichner in einer Zeile: %s' % z['Value'])
    for r in refs:
        if r in bom:
            fehler.append('doppelter Bezeichner in der Stueckliste: %s' % r)
        bom[r] = z['LCSC Part #'].strip()
# Positionsliste
pos = {}
for z in lies('positions.csv'):
    r = z['Designator'].strip()
    if r in pos:
        fehler.append('doppelter Bezeichner in der Positionsliste: %s' % r)
    pos[r] = z
    if z['Layer'].strip().lower() != 'top':
        fehler.append('%s nicht oben' % r)

for r in sorted(jlc - set(bom)):
    fehler.append('JLCPCB-Teil fehlt in der Stueckliste: %s' % r)
for r in sorted(jlc - set(pos)):
    fehler.append('JLCPCB-Teil fehlt in der Positionsliste: %s' % r)
for r in sorted((set(bom) | set(pos)) - jlc):
    fehler.append('selbst geloetetes oder unbekanntes Teil in den Listen: %s' % r)
for r in sorted(set(bom) & jlc):
    if bom[r] != platine[r]:
        fehler.append('%s: LCSC %s in der Stueckliste, %s auf der Platine' % (r, bom[r], platine[r]))
if set(bom) != set(pos):
    fehler.append('Bezeichner in Stueckliste und Positionsliste verschieden: %s' % sorted(set(bom) ^ set(pos)))

# Eigene Stueckliste ../../bom/bom.csv (Spalte LCSC SMD)
eigene = set()
with open(os.path.join(HIER, '..', '..', 'bom', 'bom.csv'), encoding='utf-8') as f:
    zeilen = [z for z in f if not z.startswith('#')]
for z in csv.DictReader(zeilen, delimiter=';'):
    if re.fullmatch(r'C\d+', (z.get('LCSC SMD') or '').strip()):
        eigene.add(z['LCSC SMD'].strip())
for l in sorted(set(bom.values()) - eigene):
    fehler.append('LCSC %s steht nicht in bom/bom.csv' % l)
for l in sorted(eigene - set(bom.values())):
    fehler.append('LCSC %s aus bom/bom.csv fehlt in der Stueckliste' % l)

# Gerber und Bohrdaten
archiv = [n for n in os.listdir(PROD) if n.endswith('.zip')]
if len(archiv) != 1:
    fehler.append('nicht genau ein Gerber-Archiv in production/: %s' % archiv)
else:
    namen = zipfile.ZipFile(os.path.join(PROD, archiv[0])).namelist()
    for endung in ('F_Cu.gtl', 'B_Cu.gbl', 'F_Mask.gts', 'B_Mask.gbs', 'F_Silkscreen.gto', 'F_Paste.gtp', 'Edge_Cuts.gm1', 'PTH.drl'):
        if not any(n.endswith(endung) for n in namen):
            fehler.append('im Gerber-Archiv fehlt *%s' % endung)

print('JLCPCB-Teile: %d, Zeilen Stueckliste: %d, Positionen: %d, selbst geloetet: %d'
      % (len(jlc), len(lies('bom.csv')), len(pos), len(platine) - len(jlc)))
for f in fehler:
    print('FEHLER:', f)
print('Fehler: %d' % len(fehler))
sys.exit(1 if fehler else 0)
