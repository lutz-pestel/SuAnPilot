#!/usr/bin/env python3
# Umschalttest adaptive -> basic (Version 00.01, 10.10.2026): pypilot-Anbindung von adaptive.py am PC mit
# nachgebildeten pypilot-Werten. Prueft: bei ausgeschaltetem Autopiloten kein Rueckfall (Fall 10.10.2026 11:53),
# bei eingeschaltetem weiterhin Rueckfall auf basic.
import sys, types, time, importlib

class Wert(object):
    def __init__(self, v=None): self.value = v
    def set(self, v): self.value = v

class Pilot(object):                                   # Ersatz fuer pilot.AutopilotPilot
    def __init__(self, name, ap): self.name, self.ap = name, ap
    def register(self, typ, name, *a): return typ(name, *a)
class Gain(Wert):
    def __init__(self, name, d, lo, hi): Wert.__init__(self, d)
class Sensor(Wert):
    def __init__(self, name): Wert.__init__(self, False)
class Text(Wert):
    def __init__(self, name, d): Wert.__init__(self, d)

m = types.ModuleType('pilot'); m.AutopilotPilot, m.AutopilotGain = Pilot, Gain; sys.modules['pilot'] = m
pv = types.ModuleType('pypilot.values'); pv.SensorValue, pv.StringValue = Sensor, Text
sys.modules['pypilot'] = types.ModuleType('pypilot'); sys.modules['pypilot.values'] = pv
adaptive = importlib.import_module('adaptive')

def ap_neu():
    ns = types.SimpleNamespace
    ap = ns(enabled=Wert(False), pilot=Wert('adaptive'), mode=Wert('compass'), heading=Wert(100.0),
            heading_command=Wert(100.0), servo=ns(command=Wert(0)),
            sensors=ns(rudder=ns(angle=Wert(0.0), range=Wert(30.0)), gps=ns(speed=Wert(5.0))),
            boatimu=ns(SensorValues={'headingrate_lowpass': Wert(0.0)}))
    p = adaptive.AdaptivePilot(ap)
    for n, v in (('k_ref', 1.0), ('Tg', 2.0), ('rate_up', 6.5), ('rate_down', 3.7)):
        p.vals[n].set(v)
    return ap, p

t = [1000.0]
adaptive.time.monotonic = lambda: t[0]                 # Uhr der Simulation

def laufen(ap, p, s, ruder):
    for i in range(int(s * 10)):
        if ap.pilot.value != 'adaptive':                # pypilot ruft dann basic statt adaptive auf
            return
        ap.sensors.rudder.angle.set(ruder)
        t[0] += 0.1
        p.process(False)

ok = True
def pruefe(name, bed):
    global ok
    ok &= bed
    print('%-62s %s' % (name, 'OK' if bed else 'FEHLER'))

# Fall 1 wie 10.10. 11:53: Autopilot aus, Anzeige erst -52 Grad, dann 60 s weg
ap, p = ap_neu()
laufen(ap, p, 5, -52.37); laufen(ap, p, 60, False)
pruefe('1 aus, Anzeige 60 s weg: Regler bleibt adaptive', ap.pilot.value == 'adaptive')
pruefe('1 aus: Zustand nennt Grund ohne Rueckfall (%s)' % p.status.value, p.status.value.startswith('aus: Ruderanzeige fehlt'))
# Fall 2: dann einschalten, Anzeige fehlt weiter -> Rueckfall auf basic
ap.enabled.set(True); laufen(ap, p, 1, False)
pruefe('2 ein, Anzeige fehlt: Rueckfall auf basic', ap.pilot.value == 'basic')
pruefe('2 Zustand (%s)' % p.status.value, p.status.value.startswith('Rueckfall: Ruderanzeige fehlt'))
# Fall 3: eingeschaltet, Anzeige faellt 30 s aus -> Rueckfall (nach t_blind 10 s), wie bisher
ap, p = ap_neu(); ap.enabled.set(True)
laufen(ap, p, 10, 0.0); laufen(ap, p, 30, False)
pruefe('3 ein, Anzeige 30 s weg: Rueckfall auf basic', ap.pilot.value == 'basic')
# Fall 4: aus, Pflichtwert fehlt -> kein Rueckfall; ein -> Rueckfall
ap, p = ap_neu(); p.vals['k_ref'].set(0.0)
laufen(ap, p, 5, 0.0)
pruefe('4 aus, Pflichtwert fehlt: bleibt adaptive (%s)' % p.status.value, ap.pilot.value == 'adaptive')
ap.enabled.set(True); laufen(ap, p, 1, 0.0)
pruefe('4 ein, Pflichtwert fehlt: Rueckfall auf basic', ap.pilot.value == 'basic')
# Fall 5: aus, Ausnahme im Programm -> kein Rueckfall; ein -> Rueckfall
ap, p = ap_neu(); p._process = lambda reset: 1 / 0
p.process(False)
pruefe('5 aus, Ausnahme im Programm: bleibt adaptive', ap.pilot.value == 'adaptive')
ap.enabled.set(True); p.process(False)
pruefe('5 ein, Ausnahme im Programm: Rueckfall auf basic', ap.pilot.value == 'basic')
# Fall 6: aus, alles in Ordnung -> Zustand "aus"
ap, p = ap_neu(); laufen(ap, p, 5, 2.0)
pruefe('6 aus, alles da: Zustand aus (%s)' % p.status.value, p.status.value == 'aus' and ap.pilot.value == 'adaptive')
print('Version adaptive', adaptive.VERSION, '- alle Faelle bestanden' if ok else '- FEHLER')
sys.exit(0 if ok else 1)
