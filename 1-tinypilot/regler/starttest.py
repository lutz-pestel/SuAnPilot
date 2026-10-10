#!/usr/bin/env python3
# Starttest (Version 00.01, 10.10.2026): Reglerwahl in pypilot/autopilot.py (Block "SuAn: nach dem Start ...")
# am PC. Der Block wird aus der Datei gelesen und mit nachgebildeten Werten ausgefuehrt.
import os, types

DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'autopilot', 'software', 'RPI', 'kern', 'usr',
                     'local', 'lib', 'python3.6', 'site-packages', 'pypilot', 'autopilot.py')
zeilen = open(DATEI).read().split('\n')
a = next(i for i, z in enumerate(zeilen) if 'SuAn: nach dem Start' in z)
b = next(i for i, z in enumerate(zeilen) if i > a and 'pilot = self.pilots[self.pilot.value]' in z)
block = compile('\n'.join(z[8:] for z in zeilen[a:b]), 'autopilot.py-Block', 'exec')   # Einrueckung der Methode weg

class Wert(object):
    def __init__(self, v): self.value = v
    def set(self, v): self.value = v

def ap(pilot, enabled=False, lastenabled=False, start_t=100.0):
    return types.SimpleNamespace(pilot=Wert(pilot), enabled=Wert(enabled), lastenabled=lastenabled,
                                 start_pilot_t=start_t, pilots={'adaptive': 1, 'basic': 2})

def schritt(s, t0):
    exec(block, {'print': lambda *x: None}, {'self': s, 't0': t0})
    s.lastenabled = s.enabled.value                     # wie spaeter in iteration()

ok = True
def pruefe(name, bed):
    global ok
    ok &= bed
    print('%-66s %s' % (name, 'OK' if bed else 'FEHLER'))

s = ap('basic'); schritt(s, 99.0)
pruefe('1 vor Ablauf der 15 s: noch basic', s.pilot.value == 'basic')
schritt(s, 101.0)
pruefe('2 nach 15 s, Autopilot aus: adaptive', s.pilot.value == 'adaptive' and s.start_pilot_t is False)
s.pilot.set('basic'); schritt(s, 200.0)
pruefe('3 danach von Hand basic (Autopilot aus): bleibt basic', s.pilot.value == 'basic')
s.enabled.set(True); schritt(s, 201.0)
pruefe('4 Einschalten: adaptive', s.pilot.value == 'adaptive')
s.pilot.set('basic'); schritt(s, 202.0)
pruefe('5 Rueckfall/Wahl basic bei eingeschaltetem Autopiloten: bleibt basic', s.pilot.value == 'basic')
s.enabled.set(False); schritt(s, 203.0); s.enabled.set(True); schritt(s, 204.0)
pruefe('6 Aus und wieder Ein: adaptive', s.pilot.value == 'adaptive')
s = ap('basic', enabled=True, lastenabled=True); schritt(s, 101.0)
pruefe('7 nach 15 s, Autopilot schon ein: Start-Regel greift nicht', s.pilot.value == 'basic')
s = ap('basic', enabled=True, lastenabled=False); schritt(s, 50.0)
pruefe('8 Einschalten vor Ablauf der 15 s: adaptive', s.pilot.value == 'adaptive')
s = ap('basic', enabled=True); s.pilots = {'basic': 2}; schritt(s, 101.0)
pruefe('9 ohne adaptive im Paket: bleibt basic', s.pilot.value == 'basic')
# OFF COURSE (check_offcourse aus autopilot.py): Grenze 20 Grad, 30 s
import ast
baum = ast.parse(open(DATEI).read())
fn = next(n for n in ast.walk(baum) if isinstance(n, ast.FunctionDef) and n.name == 'check_offcourse')
ns = {'print': lambda *x: None}
exec(compile(ast.Module(body=[fn], type_ignores=[]), 'check_offcourse', 'exec'), ns)
def oc(ein=True, cmd=100.0):
    return types.SimpleNamespace(enabled=Wert(ein), heading_error=Wert(0.0), heading_command=Wert(cmd), offcourse=Wert(False),
                                 offcourse_limit=Wert(20.0), offcourse_delay=Wert(30.0), offcourse_t=None, offcourse_cmd=None)
def fahre(s, t0, t1, e, cmd=None):
    t = t0
    while t <= t1 + 1e-9:
        s.heading_error.value = e
        if cmd is not None: s.heading_command.value = cmd
        ns['check_offcourse'](s, t); t += 0.1
s = oc(); fahre(s, 0, 29, 25.0)
pruefe('O1 25 Grad seit 29 s: noch kein Alarm', s.offcourse.value is False)
fahre(s, 29.1, 31, 25.0)
pruefe('O2 25 Grad seit 31 s: OFF COURSE', s.offcourse.value is True)
fahre(s, 31.1, 32, 15.0)
pruefe('O3 wieder innerhalb 20 Grad: Alarm aus', s.offcourse.value is False)
s = oc(); fahre(s, 0, 20, 25.0); fahre(s, 20.1, 21, 10.0); fahre(s, 21.1, 45, 25.0)
pruefe('O4 kurz innerhalb, dann wieder draussen: zaehlt neu (24 s)', s.offcourse.value is False)
s = oc(ein=False); fahre(s, 0, 60, 40.0)
pruefe('O5 Autopilot aus: nie Alarm', s.offcourse.value is False)
s = oc(); fahre(s, 0, 25, 25.0); fahre(s, 25.1, 50, 25.0, cmd=130.0)
pruefe('O6 Kurswechsel nach 25 s: zaehlt neu, kein Alarm', s.offcourse.value is False)
s = oc(); fahre(s, 0, 35, 25.0); fahre(s, 35.1, 36, 25.0, cmd=130.0)
pruefe('O7 Alarm steht, Kurswechsel: Alarm bleibt', s.offcourse.value is True)
s = oc(); fahre(s, 0, 35, -25.0)
pruefe('O8 andere Seite (-25 Grad): OFF COURSE', s.offcourse.value is True)
print('alle Faelle bestanden' if ok else 'FEHLER')
raise SystemExit(0 if ok else 1)
