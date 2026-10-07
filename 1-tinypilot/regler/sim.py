#!/usr/bin/env python3
# Simulation fuer den Regler adaptive (PyPilot-AI, 02.10.2026). Nur am PC.
#   python sim.py test               -> Programmpruefung mit TESTSCHIFF (keine SuAn-Werte!)
#   python sim.py tune K T up down   -> Startwerte fuer ruhig/sparsam aus SuAns vermessenem K, T, Rudergeschw.
#   python sim.py sprungdaten DATEI  -> erzeugt Rudersprung-Daten zum Pruefen von sprung.py
# Schiffsmodell: Nomoto 1. Ordnung  T*dr/dt + r = -K*(Ruder + Luvgierigkeit) + Wellen;  Ruder per Pumpe mit
# Geschwindigkeit je Richtung, Anzeige um 'delay' verspaetet. Alle Groessen in Grad, Grad/s, s.
import csv, math, random, sys
from adaptive import AdaptiveCore, resolv

# Nur zur Pruefung des Programms. NICHT als Werte fuer SuAn verwenden (CLAUDE: nur eigene Messungen).
TESTSCHIFF = dict(K=0.3, T=6.0, rate_up=6.0, rate_down=3.5, delay=1.0)

class Schiff(object):
    def __init__(self, K, T, rate_up, rate_down, delay, luv=8.0, welle=1.0, seed=1, tau_w=1.5):
        self.K, self.T, self.up, self.down, self.delay = K, T, rate_up, rate_down, delay
        self.luv = luv                  # Luvgierigkeit als gleichwertige Ruderlage (+ = luvt nach BB an)
        self.welle = welle              # Staerke des Wellengierens (Grad/s)
        self.tau_w = tau_w              # Zeitkonstante des Wellengierens (s)
        self.r = 0.0; self.psi = 0.0; self.rud = -luv; self.t = 0.0
        self.hist = []; self.rng = random.Random(seed); self.w = 0.0
        self.fehler = []                # Pumpenfehler: Liste (von_s, bis_s, Faktor rueckwaerts), z. B. (60, 180, 0.25)

    def schritt(self, u, dt):
        f = 1.0
        for a, b, fak in self.fehler:
            if a <= self.t < b: f = fak
        if u > 0: self.rud += self.up * dt
        elif u < 0: self.rud -= self.down * f * dt
        self.rud = max(-35.0, min(35.0, self.rud))
        self.w += (-self.w / self.tau_w + self.rng.gauss(0, 1) * self.welle * 1.2 / math.sqrt(dt) * 0.316) * dt
        self.r += (-self.K * (self.rud + self.luv) - self.r) / self.T * dt + self.w * dt
        self.psi = resolv(self.psi + self.r * dt)
        self.t += dt
        self.hist.append((self.t, self.rud))
        while self.hist and self.hist[0][0] < self.t - self.delay - 1: self.hist.pop(0)

    def anzeige(self):
        ta = self.t - self.delay
        for t, r in self.hist:
            if t >= ta: return r + self.rng.gauss(0, 0.2)
        return self.hist[0][1] if self.hist else self.rud

def lauf(params, schiff, dauer=300.0, ereignisse=(), dt=0.1, start_ruder=None, sog=5.0, kern=AdaptiveCore):
    """ereignisse: Liste (Zeit, Art, Wert): 'kurs' (+/- Grad), 'luv' (neuer Wert), 'anzeige_aus' (Dauer s)."""
    c = kern(params)
    if start_ruder is not None: schiff.rud = start_ruder
    cmd = 0.0; ev = sorted(ereignisse); aus_bis = -1
    log = []
    c.reset(0.0, schiff.anzeige(), schiff.psi)
    while schiff.t < dauer:
        while ev and ev[0][0] <= schiff.t:
            _, art, wert = ev.pop(0)
            if art == 'kurs': cmd = resolv(cmd + wert)
            elif art == 'luv': schiff.luv = wert
            elif art == 'anzeige_aus': aus_bis = schiff.t + wert
        anz = None if schiff.t < aus_bis else schiff.anzeige()
        u, info = c.step(schiff.t, True, schiff.psi, cmd, schiff.r + random.gauss(0, 0.05), anz, sog)
        if info['state'].startswith('Rueckfall'):
            log.append((schiff.t, resolv(schiff.psi - cmd), 0, schiff.rud, info['state'])); break
        schiff.schritt(u, dt)
        log.append((schiff.t, resolv(schiff.psi - cmd), u, schiff.rud, info['state'], schiff.r))
    return log

def guete(log, ab=30.0):
    """Gütemaß wie an Bord: Trend (20-s-Mittel), Ausreißer > 10°, Pumpe an (%), Richtungswechsel/min."""
    L = [x for x in log if x[0] >= ab]
    if not L: return {}
    n = int(20 / 0.1); fe = [x[1] for x in L]
    trend = [abs(sum(fe[max(0, i - n):i + 1]) / len(fe[max(0, i - n):i + 1])) for i in range(len(fe))]
    us = [x[2] for x in L if x[2] != 0]
    laeufe, umkehr, last, t_end = 0, 0, 0, -9.0
    for a, b in zip(L, L[1:]):
        if a[2] != 0 and b[2] == 0: last, t_end = a[2], b[0]
        if a[2] == 0 and b[2] != 0:
            laeufe += 1
            if b[2] == -last and b[0] - t_end < 0.7: umkehr += 1
    wechsel = sum(1 for a, b in zip(us, us[1:]) if a * b < 0)
    minuten = (L[-1][0] - L[0][0]) / 60.0
    return dict(trend=sum(trend) / len(trend), aus=100.0 * sum(1 for e in fe if abs(e) > 10) / len(fe),
                pumpe=100.0 * len(us) / len(L), wechsel=wechsel / max(minuten, 0.1), max=max(abs(e) for e in fe),
                laeufe=laeufe / max(minuten, 0.1), umkehr=umkehr / max(minuten, 0.1),
                rstd=(lambda r: (sum((x - sum(r) / len(r)) ** 2 for x in r) / len(r)) ** 0.5)([x[5] for x in L if len(x) > 5] or [0.0]))

def zeile(name, g, extra=''):
    print('%-34s Trend %4.2f°  >10° %4.1f%%  Pumpe %4.1f%%  Wechsel %4.1f/min  max %5.1f°  %s' % (
        name, g['trend'], g['aus'], g['pumpe'], g['wechsel'], g['max'], extra))

def test():
    s = TESTSCHIFF
    p = dict(k_ref=1.0, Tg=4.0, K_ref=s['K'], T_I=120.0, T_S=0.0, r_max_stb=3.0, r_max_bb=3.0, T_ramp=s['T'],
             rate_up=s['rate_up'], rate_down=s['rate_down'], delay=s['delay'], db=1.0)
    print('Programmpruefung mit TESTSCHIFF (keine SuAn-Werte):', s)
    sch = lambda **kw: Schiff(s['K'], s['T'], s['rate_up'], s['rate_down'], s['delay'], **kw)
    zeile('1 Kurshalten, Wellen', guete(lauf(p, sch())))
    zeile('2 Start mit Ruder 0 (Trimm fehlt)', guete(lauf(p, sch(), start_ruder=0.0), ab=0))
    log = lauf(p, sch(), ereignisse=[(100, 'luv', 14.0), (130, 'luv', 8.0)])
    zeile('3 Böe: Luvgierigkeit 8 -> 14 -> 8', guete(log, ab=90))
    for d in (10, 30, -10, -30):
        log = lauf(p, sch(welle=0.0), dauer=150, ereignisse=[(40, 'kurs', d)])
        nach = [x for x in log if x[0] > 40.5]
        ue = max((math.copysign(1, d) * x[1] for x in nach), default=0)
        t_ziel = next((x[0] - 40 for x in nach if abs(x[1]) < 2), float('nan'))
        print('4 Kurswechsel %+3d°: Ziel ±2° nach %5.1f s, Überschwingen %4.1f°' % (d, t_ziel, max(0.0, ue)))
    log = lauf(p, sch(), ereignisse=[(100, 'anzeige_aus', 5)])
    print('5 Anzeige 5 s weg:  Zustand am Ende:', log[-1][4], ' max Fehler %.1f°' % guete(log)['max'])
    log = lauf(p, sch(), ereignisse=[(100, 'anzeige_aus', 30)])
    print('6 Anzeige 30 s weg: Zustand am Ende:', log[-1][4], 'nach %.0f s' % log[-1][0])
    p2 = dict(p); p2['k_ref'] = 0
    print('7 Pflichtwert fehlt:', lauf(p2, sch(), dauer=1)[-1][4])

def tune(K, T, up, down, delay=1.0):
    """Gittersuche am Modell aus SuAns Vermessung: beste k_ref, Tg, T_I, db je Satz."""
    best = {}
    for k in (0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0):
        for Tg in (0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0):
            for T_I in (60.0, 120.0, 240.0):
                for db in (0.5, 1.0, 2.0, 3.0, 4.5):
                    p = dict(k_ref=k, Tg=Tg, T_I=T_I, db=db, K_ref=K, rate_up=up, rate_down=down, delay=delay,
                             r_max_stb=2.0, r_max_bb=2.0, T_ramp=T)
                    g1 = guete(lauf(p, Schiff(K, T, up, down, delay, welle=1.0, seed=3)))
                    g2 = guete(lauf(p, Schiff(K, T, up, down, delay, welle=1.0, seed=4),
                                    ereignisse=[(100, 'luv', 14.0), (140, 'luv', 8.0)]), ab=90)
                    if not g1 or not g2: continue
                    tr = (g1['trend'] + g2['trend']) / 2; au = (g1['aus'] + g2['aus']) / 2
                    pu = (g1['pumpe'] + g2['pumpe']) / 2
                    kosten = {'ruhig': tr + au / 2 + 0.02 * pu, 'sparsam': tr / 2 + au / 4 + 0.1 * pu}
                    for satz, c in kosten.items():
                        if satz not in best or c < best[satz][0]:
                            best[satz] = (c, p, g1, g2)
    print('Grenzen der Suche: k_ref 0,3-4, Tg 0-8 s, T_I 60-240 s, db 0,5-4,5° – liegt ein Ergebnis am Rand, Suche erweitern.')
    for satz, (c, p, g1, g2) in best.items():
        print('%-8s k_ref %.1f  Tg %.0f s  T_I %.0f s  db %.1f°  (Kosten %.2f)' % (satz, p['k_ref'], p['Tg'], p['T_I'], p['db'], c))
        zeile('   Wellen', g1); zeile('   Böe', g2)

def sprungdaten(datei, K=TESTSCHIFF['K'], T=TESTSCHIFF['T']):
    """Handbetrieb mit Tastendrücken 1,4 s (wie an Bord) -> CSV im Format der Aufzeichnung."""
    s = Schiff(K, T, TESTSCHIFF['rate_up'], TESTSCHIFF['rate_down'], 1.0, welle=0.3, seed=7)
    s.rud = -s.luv                                   # im Trimm
    druecke = [(30, 1), (60, -1), (90, -1), (120, 1), (150, 1), (151.6, 1), (180, -1), (181.6, -1)]
    w = csv.writer(open(datei, 'w', newline=''))
    w.writerow(['time', 'ap.enabled', 'ap.heading', 'imu.headingrate_lowpass', 'rudder.angle', 'servo.speed', 'gps.speed'])
    t0 = 1.79e9
    while s.t < 220:
        u = 0
        for td, rich in druecke:
            if td <= s.t < td + 1.4: u = rich
        s.schritt(u, 0.2)
        w.writerow(['%.2f' % (t0 + s.t), 'False', '%.2f' % s.psi, '%.3f' % s.r, '%.2f' % s.anzeige(), u, 5.0])
    print('geschrieben:', datei, ' (TESTSCHIFF K=%.2f T=%.1f)' % (K, T))

if __name__ == '__main__':
    a = sys.argv[1:] or ['test']
    if a[0] == 'test': test()
    elif a[0] == 'tune': tune(*[float(x) for x in a[1:5]])
    elif a[0] == 'sprungdaten': sprungdaten(a[1])
