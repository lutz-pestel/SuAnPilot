#!/usr/bin/env python3
# Eingrifftest (Version 00.01, 10.10.2026): "Ruder folgt nicht" bei Hand am Steuer und bei eingefrorenem Geber.
# Simulation (TESTSCHIFF, keine SuAn-Werte). Vorbild: Eingriff an Bord 10.10.2026 13:26 (Hand ~3 s auf +21 Grad);
# die Aufzeichnung selbst taugt nicht zur Wiedergabe (Pumpe des Reglers wirkt dort nicht).
# Aufruf: python eingrifftest.py [adaptive.py einer anderen Fassung, zum Vergleich]
import importlib.util, sys
from sim import Schiff, lauf, guete, TESTSCHIFF
from adaptive import AdaptiveCore
import optimierung as o
KERN = AdaptiveCore
if len(sys.argv) > 1:
    spec = importlib.util.spec_from_file_location('alt', sys.argv[1]); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); KERN = m.AdaptiveCore

P = dict(k_ref=1.0, Tg=2, v_ref=6.5, n_v=1, K_ref=0.42, T_I=60, r_max_stb=1.5, r_max_bb=1.5, T_ramp=5.3,
         rate_up=6.5, rate_down=3.7, delay=1.0, db=2.5, t_rev=1.0)

class HandSchiff(Schiff):
    """Hand am Steuer: Ruder in 2 s auf 'ziel' und dort 'dauer' s gehalten (Pumpe wirkt nicht). Geber eingefroren ab 'frz'."""
    def __init__(self, hand=(), frz=None, **kw):
        Schiff.__init__(self, TESTSCHIFF['K'], TESTSCHIFF['T'], 6.5, 3.7, 1.0, **kw)
        self.hand, self.frz, self.frz_wert = hand, frz, None
    def schritt(self, u, dt):
        for a, dauer, ziel in self.hand:
            if a <= self.t < a + 2 + dauer:
                alt = self.rud
                Schiff.schritt(self, 0, dt)
                self.rud = alt + max(-8 * dt, min(8 * dt, ziel - alt))
                return
        Schiff.schritt(self, u, dt)
    def anzeige(self):
        if self.frz is not None and self.t >= self.frz:
            if self.frz_wert is None: self.frz_wert = round(Schiff.anzeige(self), 2)
            return self.frz_wert                        # Interface gibt den letzten Wert weiter aus (Fehler 2)
        return Schiff.anzeige(self)

ok = True
def pruefe(name, bed, extra=''):
    global ok
    ok &= bed
    print('%-58s %-7s %s' % (name, 'OK' if bed else 'FEHLER', extra))

def zust(log): return [x[4] for x in log]
for name, hand in (('Hand 3 s auf +20 Grad', [(60, 3, 20.0)]), ('Hand 10 s auf -20 Grad', [(60, 10, -20.0)]),
                   ('Hand 30 s auf +15 Grad', [(60, 30, 15.0)]), ('dreimal Hand 4 s', [(60, 4, 20), (90, 4, -20), (120, 4, 20)])):
    log = lauf(P, HandSchiff(hand=hand, luv=8.0, welle=0.5, seed=7), dauer=200, kern=KERN)
    z = zust(log); spaet = [x for x in log if x[0] > 160]; g = guete(spaet, ab=0) if spaet else {'trend': float('nan')}
    pruefe('Sim  %s: kein Rueckfall' % name, not z[-1].startswith('Rueckfall') and log[-1][0] > 199,
           'Warnung %s, nach 160 s Trend %.1f' % ('ja' if any('Hand' in s for s in z) else 'nein', g['trend']))
log = lauf(P, HandSchiff(frz=60, luv=8.0, welle=0.5, seed=7), dauer=200, ereignisse=[(65, 'kurs', 20)], kern=KERN)
pruefe('Sim  Geber eingefroren ab 60 s, Kurswechsel: Rueckfall', zust(log)[-1].startswith('Rueckfall'),
       '%s nach %.0f s' % (zust(log)[-1], log[-1][0]))
log = lauf(P, HandSchiff(luv=8.0, welle=0.5, seed=7), dauer=200, ereignisse=[(60, 'kurs', 30), (120, 'kurs', -30)], kern=KERN)
pruefe('Sim  ohne Stoerung: nie Warnung oder Rueckfall', all(s in ('ok', 'abgleich') for s in zust(log)))

# Rudergeschwindigkeit nach Handeingriffen (Modell SuAn 10.10.2026, Werte an Bord, Lernen aus): darf sich nicht aendern
# (an Bord fiel sie am 10.10. nach einem Griff ins Ruder von 4,4 auf 0,99 Grad/s, der Kurs schaukelte sich auf).
kerne = []
class Rec(KERN):
    def __init__(self, *a, **k):
        KERN.__init__(self, *a, **k); kerne.append(self)
PB = dict(o.BORD, lern=0, rate_up=4.4, rate_down=4.2)
for hand in ([(20, -20.0, 2.0)], [(20, 22.0, 1.5)], [(20, -20.0, 0.5)], [(20, 20.0, 0.3)], [(20, -20.0, 0.5), (50, 20.0, 0.5)]):
    kerne.clear()
    log = lauf(PB, o.SuAn(o.WELLE, 3, hand), dauer=120, sog=5.7, kern=Rec)
    c = kerne[0]
    pruefe('Modell Hand %s: Rudergeschw. bleibt 4,4/4,2' % ' '.join('%+.0f/%.1fs' % (z, h) for a, z, h in hand),
           abs(c.v_up - 4.4) < 1e-6 and abs(c.v_down - 4.2) < 1e-6 and not log[-1][4].startswith('Rueckfall'),
           'v_up %.2f v_down %.2f, nach 60 s max %.1f Grad' % (c.v_up, c.v_down, max(abs(x[1]) for x in log if x[0] > 60)))
c = Rec(dict(PB)); c.p['rate_up'] = 3.0; c.step(0.0, True, 0.0, 0.0, 0.0, 3.0); c.p['rate_up'] = 5.0; c.step(0.1, True, 0.0, 0.0, 0.0, 3.0)
pruefe('Lernen aus: geaenderte Rudergeschw. gilt sofort', abs(c.v_up - 5.0) < 1e-6)
print('Version adaptive', (m if len(sys.argv) > 1 else sys.modules['adaptive']).VERSION, '- alle Faelle bestanden' if ok else '- FEHLER')
sys.exit(0 if ok else 1)
