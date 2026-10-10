#!/usr/bin/env python3
# Optimierung adaptive (Version 00.01, 10.10.2026): Modell der SuAn aus einer Aufzeichnung, dann Parametersuche
# in der Simulation. Nur am PC.
#   python optimierung.py modell SIGNALS.csv VON BIS [VON BIS ...]   (hh:mm:ss) -> K, T, Verzoegerung, Rudergeschw.
#   python optimierung.py pruefen  -> Modell mit den Werten an Bord: bildet es das Pendeln vom 10.10. 13:42 nach?
#   python optimierung.py suche    -> Rangliste der Parameter-Kombinationen
# Modell: T*dr/dt + r = K*(Ruder(t-delay_wirk) - d0); Drehrate r vom Kreisel (imu.headingrate_lowpass).
import csv, sys, time, math, itertools

def lesen(datei, fenster):
    R = []
    for x in csv.DictReader(open(datei)):
        try:
            t = float(x['time']); hms = time.strftime('%H:%M:%S', time.localtime(t))
            if any(a <= hms <= b for a, b in fenster):
                R.append(dict(t=t, r=float(x['imu.headingrate_lowpass']), d=float(x['rudder.angle']),
                              u=float(x['servo.command'] or 0), on=x['ap.enabled'] == 'True' or x['ap.enabled'] == 'true',
                              v=float(x['gps.speed'] or 0)))
        except (ValueError, KeyError):
            pass
    return R

def interp(R, key, t):
    lo, hi = 0, len(R) - 1
    if t <= R[0]['t']: return R[0][key]
    if t >= R[-1]['t']: return R[-1][key]
    while hi - lo > 1:
        m = (lo + hi) // 2
        if R[m]['t'] <= t: lo = m
        else: hi = m
    a, b = R[lo], R[hi]
    return a[key] + (b[key] - a[key]) * (t - a['t']) / (b['t'] - a['t'])

def fit(R, dt=0.1):
    """Gitter ueber T und Verschiebung s (Anzeige spaeter als Wirkung: Ruder(t+s)); K, d0 linear. Abschnittsweise
    (Luecken > 2 s trennen), Start jedes Abschnitts mit gemessener Drehrate."""
    abschn, cur = [], [R[0]]
    for a, b in zip(R, R[1:]):
        if b['t'] - a['t'] > 2.0: abschn.append(cur); cur = []
        cur.append(b)
    abschn.append(cur)
    best = None
    for s10 in range(0, 16):
        s = s10 / 10.0
        for T10 in range(5, 201, 5):
            T = T10 / 10.0
            A = []; B = []; Y = []
            for S in abschn:
                if S[-1]['t'] - S[0]['t'] < 10: continue
                t = S[0]['t']; a = b = 0.0; c = S[0]['r']
                while t < S[-1]['t'] - s:
                    d = interp(S, 'd', t + s)
                    a += (d - a) / T * dt; b += (1 - b) / T * dt; c += (0 - c) / T * dt
                    t += dt
                    A.append(a); B.append(b); Y.append(interp(S, 'r', t) - c)
            # Y = K*A - K*d0*B  -> lineare Regression auf A, B
            saa = sum(x * x for x in A); sbb = sum(x * x for x in B); sab = sum(x * y for x, y in zip(A, B))
            say = sum(x * y for x, y in zip(A, Y)); sby = sum(x * y for x, y in zip(B, Y))
            det = saa * sbb - sab * sab
            if abs(det) < 1e-9: continue
            p = (say * sbb - sby * sab) / det; q = (saa * sby - sab * say) / det
            res = sum((y - p * x - q * z) ** 2 for x, z, y in zip(A, B, Y)) / len(Y)
            if best is None or res < best[0]:
                var = sum((y - sum(Y) / len(Y)) ** 2 for y in Y) / len(Y)
                best = (res, T, s, p, -q / p if p else 0.0, 1 - res / var, len(Y) * dt)
    return best

def rudergeschw(R):
    """Rudergeschwindigkeit je Richtung aus Pumpenlaeufen >= 1,5 s (Anzeige um 0,5 s versetzt)."""
    laeufe, cur = [], None
    for x in R:
        sgn = 1 if x['u'] > 0.3 else -1 if x['u'] < -0.3 else 0
        if cur and (sgn != cur[0] or x['t'] - cur[2] > 1.0):
            laeufe.append(cur); cur = None
        if sgn and not cur: cur = [sgn, x['t'], x['t']]
        elif cur: cur[2] = x['t']
    out = {1: [], -1: []}
    for sgn, a, b in laeufe:
        if b - a < 1.5: continue
        d0, d1 = interp(R, 'd', a + 0.5 + 0.3), interp(R, 'd', b + 0.5)
        out[sgn].append((d1 - d0) * sgn / (b - a - 0.3))
    return {k: (sorted(v)[len(v) // 2] if v else None, len(v)) for k, v in out.items()}

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'modell':
    datei = sys.argv[2]; fenster = list(zip(sys.argv[3::2], sys.argv[4::2]))
    R = lesen(datei, fenster)
    print('Messpunkte %d, Fahrt Mittel %.1f kn' % (len(R), sum(x['v'] for x in R) / len(R)))
    for a, b in fenster:
        Ri = [x for x in R if a <= time.strftime('%H:%M:%S', time.localtime(x['t'])) <= b]
        res, T, s, K, d0, r2, dauer = fit(Ri)
        print('%s-%s: K %+.3f Grad/s je Grad, T %4.1f s, Anzeige spaeter %.1f s, Geradeaus-Ruder %+.1f, erklaert %3.0f %% (%.0f s)'
              % (a, b, K, T, s, d0, 100 * r2, dauer))
    res, T, s, K, d0, r2, dauer = fit(R)
    print('alle zusammen: K %+.3f, T %.1f s, Anzeige spaeter %.1f s, Geradeaus-Ruder %+.1f, erklaert %.0f %%' % (K, T, s, d0, 100 * r2))
    rg = rudergeschw(R)
    print('Rudergeschwindigkeit: + %.1f Grad/s (%d Laeufe), - %.1f Grad/s (%d Laeufe)' % (rg[1][0] or 0, rg[1][1], rg[-1][0] or 0, rg[-1][1]))

# ---------------------------------------------------------------- Simulation mit dem Modell vom 10.10.2026
from sim import Schiff, lauf, guete
MODELL = dict(K=0.342, T=3.5, up=4.4, down=4.2, delay=0.4, d0=3.7, sog=5.7)   # 'modell' 13:26 + 13:42, 5,7 kn
BORD = dict(K_ref=0.42, T_D=0.0, T_I=60.0, T_S=0.0, T_acc=0.0, T_corr=3.0, T_ramp=5.3, Tg=2.0, db=1.5, delay=0.4,
            e_freeze=15.0, fk_max=3.0, fk_min=0.5, hub=30.0, jump_lim=8.0, k_ref=1.0, lern=0.4, n_tot=3.0, n_v=1.0,
            r_max_bb=1.5, r_max_stb=1.5, rate_down=3.7, rate_up=6.5, t_rev=1.0, v_min=2.0, v_ref=6.5)   # an Bord 10.10.

class SuAn(Schiff):
    """Modell mit Hand am Steuer: (Beginn, Ziel, Haltezeit) - Hand legt das Ruder mit 18 Grad/s auf Ziel, haelt es
    'Haltezeit' s dort und laesst los; waehrenddessen wirkt die Pumpe nicht."""
    def __init__(self, welle, seed, hand=()):
        m = MODELL
        Schiff.__init__(self, m['K'], m['T'], m['up'], m['down'], m['delay'], luv=-m['d0'], welle=welle, seed=seed, tau_w=1.2)
        self.hand = list(hand); self.h = None          # laufender Eingriff: [Ziel, Halten bis (None = noch unterwegs)]
    def schritt(self, u, dt):
        if self.h is None and self.hand and self.t >= self.hand[0][0]:
            a, ziel, halten = self.hand.pop(0); self.h = [ziel, None, halten]
        if self.h:
            ziel, bis, halten = self.h
            alt = self.rud
            Schiff.schritt(self, 0, dt)
            self.rud = alt + max(-18 * dt, min(18 * dt, ziel - alt))
            if bis is None and abs(self.rud - ziel) < 0.01: self.h[1] = self.t + halten
            if self.h[1] is not None and self.t >= self.h[1]: self.h = None
            return
        Schiff.schritt(self, u, dt)

WELLE = 0.25          # abgeglichen auf ruhiges Kurshalten 10.10. 13:44-14:10 (Drehrate-Streuung 0,14 Grad/s)

def verlauf(log, ab, bis, ziel=0.0):
    """Kennwerte nach einer Stoerung ab 'ab': groesste Abweichung, Ueberschwingen (Gegenseite), Zeit bis dauerhaft
    innerhalb 2 Grad, Zahl der Schwingungen > 2 Grad."""
    L = [(x[0], x[1] - ziel) for x in log if ab <= x[0] <= bis]
    if not L: return dict(max=99, ueber=99, zurueck=99, schw=9)
    emax = max(L, key=lambda x: abs(x[1])); s0 = 1 if emax[1] > 0 else -1
    nach = [e for t, e in L if t >= emax[0]]
    ueber = max([0.0] + [-e * s0 for e in nach])
    zur = next((t for t, e in reversed(L) if abs(e) > 2.0), ab) - ab
    schw, seite = 0, 0
    for t, e in L:
        if abs(e) > 2.0 and (1 if e > 0 else -1) != seite:
            if seite: schw += 1
            seite = 1 if e > 0 else -1
    return dict(max=abs(emax[1]), ueber=ueber, zurueck=zur, schw=schw)

def szenarien(P, seed=3):
    P = dict(P); out = {}
    for name, hand in (('Hand -23', [(20, -20.0, 2.0)]), ('Hand +22', [(20, 22.0, 1.5)])):
        log = lauf(P, SuAn(WELLE, seed, hand), dauer=140, sog=MODELL['sog'])
        out[name] = verlauf(log, 20, 140)
    for name, dk in (('Kurs +30', 30), ('Kurs -30', -30), ('Kurs +10', 10)):
        log = lauf(P, SuAn(WELLE, seed), dauer=110, ereignisse=[(20, 'kurs', dk)], sog=MODELL['sog'])
        out[name] = verlauf(log, 20, 110)
        out[name]['zurueck'] = next((t for t, e, *r in log if t >= 20 and abs(e) <= 2.0 and
                                     all(abs(x[1]) <= 2.0 for x in log if t <= x[0] <= t + 10)), 110) - 20
    log = lauf(P, SuAn(WELLE, seed), dauer=200, sog=MODELL['sog'])
    out['ruhig'] = guete(log, ab=30)
    return out

def note(o):
    h = [o[k] for k in ('Hand -23', 'Hand +22')]; k = [o[k] for k in ('Kurs +30', 'Kurs -30', 'Kurs +10')]
    return (sum(x['zurueck'] for x in h) / 2 / 10 + sum(x['ueber'] for x in h) / 2 / 3 + sum(x['schw'] for x in h) / 2
            + sum(x['zurueck'] for x in k) / 3 / 10 + sum(x['ueber'] for x in k) / 3 / 2
            + o['ruhig']['trend'] * 2 + o['ruhig']['pumpe'] / 20)

def zeige(name, o):
    h1, h2, k1, k2, k3, r = o['Hand -23'], o['Hand +22'], o['Kurs +30'], o['Kurs -30'], o['Kurs +10'], o['ruhig']
    print('%-30s Note %5.2f | Hand: max %4.1f/%4.1f ueber %4.1f/%4.1f zurueck %3.0f/%3.0f s Schw %d/%d | '
          'Kurs +30/-30/+10: zurueck %3.0f/%3.0f/%3.0f s ueber %4.1f/%4.1f/%4.1f | ruhig: Trend %.2f Pumpe %4.1f%%'
          % (name, note(o), h1['max'], h2['max'], h1['ueber'], h2['ueber'], h1['zurueck'], h2['zurueck'], h1['schw'], h2['schw'],
             k1['zurueck'], k2['zurueck'], k3['zurueck'], k1['ueber'], k2['ueber'], k3['ueber'], r['trend'], r['pumpe']))

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'pruefen':
    log = lauf(dict(BORD), SuAn(WELLE, 3), dauer=200, sog=MODELL['sog']); g = guete(log, ab=30)
    e = [x[1] for x in log if x[0] > 30]; m = sum(e) / len(e)
    print('ruhig mit Bordwerten: Drehrate-Streuung %.2f Grad/s (gemessen 0,14), Kursfehler-Streuung %.2f (gemessen 0,79)'
          % (g['rstd'], (sum((x - m) ** 2 for x in e) / len(e)) ** 0.5))
    log = lauf(dict(BORD), SuAn(WELLE, 3, [(20, -20.0, 2.0)]), dauer=140, sog=MODELL['sog'])
    print('Eingriff wie 13:42 (Hand -23 Grad), Bordwerte - Kursfehler alle 3 s:')
    print('  ' + ' '.join('%+.0f' % x[1] for x in log if x[0] >= 20 and abs(x[0] * 10 % 30) < 0.5))
    print('  gemessen 13:42 (alle 3 s ab Eingriff): +3 +10 +16 +23 +29 +32 +29 +25 +15 +5 -2 -11 -18 -20 -18 -11 +3 +12 +9 ... -15 -15 -4 +6 +7 -4 -11 -9 +1 +7 +1 -7 -6 +1 +3')
    zeige('Bordwerte', szenarien(BORD))
    zeige('Bord + Rudergeschw. gemessen', szenarien(dict(BORD, rate_up=MODELL['up'], rate_down=MODELL['down'])))

# ---------------------------------------------------------------- Suche "zuegiger auf Sollkurs" (Betreiber 10.10.2026)
# Erlaubt: einmal hoechstens 3 Grad ueber den Sollkurs, keine zweite Schwingung; Ziel: schnell innerhalb +-2 Grad.
JETZT = dict(BORD, lern=0, rate_up=4.4, rate_down=4.2)          # an Bord seit 10.10.2026 14:11 (ap-v00.08)

def ankommen(log, ab, bis):
    """Nach Kurswechsel/Stoerung: Zeit bis dauerhaft (10 s) innerhalb 2 Grad, Ueberschwingen (Gegenseite der
    Annaeherung), zweite Schwingung (nach dem Ueberschwingen nochmals > 2 Grad auf der Ausgangsseite)."""
    L = [(x[0], x[1]) for x in log if ab <= x[0] <= bis]
    s0 = 1 if max(L, key=lambda x: abs(x[1]))[1] > 0 else -1     # Seite der grossen Abweichung
    zeit = next((t for t, e in L if abs(e) <= 2.0 and all(abs(y) <= 2.0 for u, y in L if t <= u <= t + 10)), bis) - ab
    kreuz = next((t for t, e in L if e * s0 < 0), None)
    ueber = max([0.0] + [-e * s0 for t, e in L if kreuz and t >= kreuz])
    t_ueber = next((t for t, e in L if kreuz and t >= kreuz and -e * s0 >= ueber - 1e-9), None)
    zweite = max([0.0] + [e * s0 for t, e in L if t_ueber and t > t_ueber]) if ueber > 2.0 else 0.0
    return zeit, ueber, zweite

def bewerte(P, seed=3):
    P = dict(P); z = {}
    for dk in (10, -10, 30, -30):
        log = lauf(P, SuAn(WELLE, seed), dauer=100, ereignisse=[(20, 'kurs', dk)], sog=MODELL['sog'])
        z['Kurs %+d' % dk] = ankommen(log, 20, 100)
    log = lauf(P, SuAn(WELLE, seed), dauer=130, start_ruder=7.8, sog=MODELL['sog'])      # wie 14:12: Trimm falsch
    z['Start'] = ankommen(log, 0, 130)
    log = lauf(P, SuAn(WELLE, seed, [(20, -20.0, 2.0)]), dauer=130, sog=MODELL['sog'])
    z['Hand'] = ankommen(log, 20, 130)
    g = guete(lauf(P, SuAn(WELLE, seed), dauer=200, sog=MODELL['sog']), ab=30)
    return z, g

def zeile_suche(name, z, g):
    print('%-38s ' % name + ' | '.join('%s %3.0fs %3.1f/%3.1f' % (k, *v) for k, v in z.items())
          + ' | ruhig Trend %.2f Pumpe %4.1f%%' % (g['trend'], g['pumpe']))

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'suche':
    t = time.time(); z, g = bewerte(JETZT); zeile_suche('jetzt an Bord', z, g); print('Rechenzeit je Kombination %.0f s' % (time.time() - t))

def zulaessig(z, g, basis):
    """Vorgabe Betreiber 10.10.2026 (entwurf.md, Abschnitt 1): einmal hoechstens 3 Grad ueber, keine zweite Schwingung
    ueber 2 Grad; Griff ins Ruder nicht schlechter als heute; Kurshalten und Pumpe nicht deutlich schlechter."""
    k = [z[n] for n in ('Kurs +10', 'Kurs -10', 'Kurs +30', 'Kurs -30', 'Start')]
    return (all(u <= 3.0 and w <= 2.0 for t, u, w in k) and z['Hand'][1] <= basis[0]['Hand'][1] + 0.5 and z['Hand'][2] <= 2.0
            and g['trend'] <= basis[1]['trend'] + 0.1 and g['pumpe'] <= 1.3 * basis[1]['pumpe'])

def zeit(z): return sum(z[n][0] for n in ('Kurs +10', 'Kurs -10', 'Kurs +30', 'Kurs -30', 'Start', 'Hand')) / 6

if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[1] == 'suche' and sys.argv[2] == 'gitter':
    basis = bewerte(JETZT); erg = []
    for k, tg, ti, rm, tr in itertools.product((0.8, 1.0, 1.3, 1.6, 2.0, 2.5), (1.0, 1.5, 2.0, 2.5, 3.0, 4.0),
                                               (0.0, 30.0, 60.0, 120.0), (1.5, 2.0, 2.5, 3.0), (5.3, 3.0)):
        P = dict(JETZT, k_ref=k, Tg=tg, T_I=ti, r_max_stb=rm, r_max_bb=rm, T_ramp=tr)
        z, g = bewerte(P)
        if zulaessig(z, g, basis):
            erg.append((zeit(z), k, tg, ti, rm, tr))
    erg.sort()
    print('zulaessig %d von 1152; jetzt an Bord: mittlere Zeit %.1f s' % (len(erg), zeit(basis[0])), flush=True)
    for e in erg[:15]:
        print('Zeit %4.1f s  k_ref %.1f  Tg %.1f  T_I %3.0f  Drehrate %.1f  T_ramp %.1f' % e, flush=True)

# ---------------------------------------------------------------- Wertesaetze ruhig (+-1 Grad) und sparsam (+-2,5 Grad)
import random
NEU = dict(JETZT, Tg=4.0, T_I=30.0, r_max_stb=2.0, r_max_bb=2.0, T_ramp=3.0)   # an Bord seit 10.10.2026 14:20

def ankommen_b(log, ab, bis, band):
    L = [(x[0], x[1]) for x in log if ab <= x[0] <= bis]
    s0 = 1 if max(L, key=lambda x: abs(x[1]))[1] > 0 else -1
    zeit = next((t for t, e in L if abs(e) <= band and all(abs(y) <= band for u, y in L if t <= u <= t + 10)), bis) - ab
    kreuz = next((t for t, e in L if e * s0 < 0), None)
    ueber = max([0.0] + [-e * s0 for t, e in L if kreuz and t >= kreuz])
    t_u = next((t for t, e in L if kreuz and t >= kreuz and -e * s0 >= ueber - 1e-9), None)
    zweite = max([0.0] + [e * s0 for t, e in L if t_u and t > t_u]) if ueber > 2.0 else 0.0
    return zeit, ueber, zweite

def bewerte_b(P, band, n=3):
    """Mittel (Zeit) bzw. schlechtester Fall (Ueberschwingen) ueber n verrauschte Laeufe."""
    Z = {}; G = []
    for w in range(n):
        random.seed(200 + w); P = dict(P)
        for name, kw in (('K+10', dict(ereignisse=[(20, 'kurs', 10)], dauer=110)), ('K-10', dict(ereignisse=[(20, 'kurs', -10)], dauer=110)),
                         ('K+30', dict(ereignisse=[(20, 'kurs', 30)], dauer=120)), ('K-30', dict(ereignisse=[(20, 'kurs', -30)], dauer=120)),
                         ('Start', dict(start_ruder=7.8, dauer=140)), ('Hand', dict(dauer=140))):
            hand = [(20, -20.0, 2.0)] if name == 'Hand' else ()
            log = lauf(P, SuAn(WELLE, 3 + w, hand), sog=MODELL['sog'], **kw)
            Z.setdefault(name, []).append(ankommen_b(log, 0 if name == 'Start' else 20, kw['dauer'], band))
        G.append(guete(lauf(P, SuAn(WELLE, 3 + w), dauer=300, sog=MODELL['sog']), ab=30))
    z = {k: (sum(x[0] for x in v) / n, max(x[1] for x in v), max(x[2] for x in v)) for k, v in Z.items()}
    g = {k: sum(x[k] for x in G) / n for k in ('trend', 'pumpe', 'laeufe', 'wechsel')}
    return z, g

def zeile_b(name, z, g):
    print('%-40s Zeit Mittel %5.1f s | ' % (name, sum(v[0] for v in z.values()) / len(z))
          + ' '.join('%s %3.0f/%.1f' % (k, v[0], v[1]) for k, v in z.items())
          + ' | Ueber max %.1f 2.Schw %.1f | Trend %.2f Pumpe %.1f%% Laeufe %.1f/min' % (
              max(v[1] for v in z.values()), max(v[2] for v in z.values()), g['trend'], g['pumpe'], g['laeufe']), flush=True)

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'saetze':
    z, g = bewerte_b(NEU, 1.0); zeile_b('ruhig jetzt an Bord (Ziel +-1)', z, g)
    z, g = bewerte_b(dict(NEU, sparsam=1.0), 2.5); zeile_b('sparsam jetzt (Ziel +-2,5)', z, g)
    erg = []
    for db, ti, k, tg in itertools.product((0.6, 0.8, 1.0, 1.2, 1.5), (10.0, 15.0, 20.0, 30.0), (1.0, 1.3), (3.0, 4.0, 5.0)):
        P = dict(NEU, db=db, T_I=ti, k_ref=k, Tg=tg); z, g = bewerte_b(P, 1.0)
        ok = all(v[1] <= 3.0 and v[2] <= 2.0 for v in z.values())     # Vorgabe gilt auch nach Stoerung (Hand)
        if ok: erg.append((sum(v[0] for v in z.values()) / len(z), g['laeufe'], db, ti, k, tg, z, g))
    erg.sort(key=lambda e: e[0])
    print('ruhig: zulaessig %d von 120' % len(erg), flush=True)
    for e in erg[:12]: zeile_b('ruhig db %.1f T_I %2.0f k %.1f Tg %.0f' % e[2:6], e[6], e[7])
    if len(sys.argv) > 2:
        best = dict(NEU, db=float(sys.argv[2]), T_I=float(sys.argv[3]), k_ref=float(sys.argv[4]), Tg=float(sys.argv[5]))
        erg = []
        for dbs, ts in itertools.product((1.5, 2.0, 2.5, 3.0, 4.0), (0.0, 2.0, 4.0, 8.0)):
            z, g = bewerte_b(dict(best, sparsam=1.0, db_sparsam=dbs, TS_sparsam=ts), 2.5)
            ok = all(v[1] <= 3.0 and v[2] <= 2.0 for v in z.values())
            erg.append((ok, g['laeufe'], dbs, ts, z, g))
        for e in sorted(erg, key=lambda e: (not e[0], e[1])): zeile_b('sparsam db %.1f T_S %.0f %s' % (e[2], e[3], '' if e[0] else 'VERLETZT'), e[4], e[5])

# ---------------------------------------------------------------- Kraengung (Vorsteuerung kh, 10.10.2026)
class SuAnK(SuAn):
    """Wie SuAn, dazu Kraengung: Grund 5 Grad (Wind von BB), folgt der Luvgierigkeit 1:1 (02.10.: ~1 Grad Ruder je Grad
    Kraengung) mit 1,5 s Verzoegerung, dazu Rollen in den Wellen (Streuung ~1 Grad, Periode ~4 s)."""
    def __init__(self, welle, seed, hand=(), heel0=5.0, roll=1.0):
        SuAn.__init__(self, welle, seed, hand)
        self.luv0, self.hk = self.luv, heel0; self.heel0, self.roll, self.ph = heel0, roll, 0.0
    def schritt(self, u, dt):
        SuAn.schritt(self, u, dt)
        self.hk += (self.heel0 + (self.luv - self.luv0) - self.hk) * dt / 1.5
        self.ph += dt
    def kraengung(self):
        """Wie pypilot boatimu: heel = roll*0,03 + heel*0,97 bei 20 Messungen/s (~1,7 s), hier je 0,1 s gerechnet."""
        roh = self.hk + self.roll * 1.4 * math.sin(2 * math.pi * self.ph / 4.0 + self.rng.random() * 0.3)
        self.hf = roh if not hasattr(self, 'hf') else self.hf + (roh - self.hf) * (1 - 0.97 ** 2)
        return self.hf

def boee_k(P, n=3, staerke=6.0):
    mx = ue = 0.0
    for w in range(n):
        random.seed(300 + w); s = SuAnK(WELLE, 3 + w); luv = s.luv
        log = lauf(dict(P), s, dauer=180, ereignisse=[(30, 'luv', luv + staerke), (70, 'luv', luv)], sog=MODELL['sog'])
        mx = max(mx, max(abs(x[1]) for x in log if 30 <= x[0] <= 70)); ue = max(ue, max(abs(x[1]) for x in log if x[0] >= 70))
    return mx, ue

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'kraengung':
    AKT = dict(NEU, T_I=15.0, db=1.2)                         # an Bord seit 10.10.2026 ~15:00
    for kh, th in ((0.0, 0.0), (0.1, 0.0), (0.1, 1.0), (0.1, 2.5), (0.6, 0.0), (0.6, 1.0), (0.6, 2.5), (1.0, 0.0), (1.0, 1.0)):
        P = dict(AKT, kh=kh, T_H=th)
        b1, b2 = boee_k(P), boee_k(P, staerke=-6.0)
        g = [guete(lauf(dict(P), SuAnK(WELLE, 3 + w), dauer=300, sog=MODELL['sog']), ab=30) for w in range(3)]
        print('kh %.1f T_H %.1f | Boee +6: max %4.1f danach %4.1f | Boee -6: max %4.1f danach %4.1f | ruhig mit Rollen: Trend %.2f Laeufe %.1f/min'
              % (kh, th, b1[0], b1[1], b2[0], b2[1], sum(x['trend'] for x in g) / 3, sum(x['laeufe'] for x in g) / 3), flush=True)
