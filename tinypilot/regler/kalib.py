#!/usr/bin/env python3
# Wellengieren der Simulation an SuANs Messung anpassen (PyPilot-AI, 03.10.2026).
# Ziel (gemessen 03.10. 10:10-10:21, suan db 2,5, ~5 kn, fast vor dem Wind): Drehrate-Streuung 0,41 Grad/s,
# Pumpenlaeufe 12,5/min, Umkehr < 0,7 s 0,27/min.
import sys
from sim import Schiff, lauf, guete
K, T = 0.28, 6.5                      # SuAn bei ~5 kn (gemessen 4,4 und 6,5 kn, dazwischen)
P = dict(k_ref=1.0, Tg=2, v_ref=6.5, n_v=1, K_ref=0.42, T_I=60, r_max_stb=1.5, r_max_bb=1.5, T_ramp=5.3,
         rate_up=6.5, rate_down=3.7, delay=1.0, db=2.5, T_D=0, t_rev=0, T_acc=0)
ZIEL = dict(rstd=0.41, laeufe=12.5, umkehr=0.27)
def kalibrieren():
    best = []
    for tau in (0.5, 0.8, 1.2, 2.0):
        for welle in (0.5, 0.8, 1.2, 1.8, 2.5):
            gs = [guete(lauf(P, Schiff(K, T, 6.5, 3.7, 1.0, luv=10.0, welle=welle, seed=sd, tau_w=tau), dauer=400)) for sd in (21, 22)]
            g = {k: sum(x[k] for x in gs) / len(gs) for k in ('rstd', 'laeufe', 'umkehr', 'trend', 'pumpe')}
            fehler = abs(g['rstd'] - ZIEL['rstd']) / ZIEL['rstd'] + abs(g['laeufe'] - ZIEL['laeufe']) / ZIEL['laeufe']
            best.append((fehler, tau, welle, g))
    best.sort(key=lambda x: x[0])
    for f, tau, welle, g in best[:5]:
        print('tau_w %.1f s  welle %.1f  -> Drehrate %.2f  Laeufe %.1f/min  Umkehr %.2f/min  Trend %.2f  (Abweichung %.2f)' % (
            tau, welle, g['rstd'], g['laeufe'], g['umkehr'], g['trend'], f))

def kw(q, K, T, sog, d):
    import math
    log = lauf(q, Schiff(K, T, 6.5, 3.7, 1.0, luv=10.0, welle=WELLE, seed=31, tau_w=TAU), dauer=100, ereignisse=[(30, 'kurs', d)], sog=sog)
    nach = [x for x in log if x[0] > 30.5]
    tz = next((x[0] - 30 for x in nach if abs(x[1]) < 2), 70.0)
    ue = max(0.0, max((math.copysign(1, d) * x[1] for x in nach if x[0] - 30 >= tz), default=0))
    g = guete(log, ab=30)
    return tz, ue, g['umkehr']

def werte():
    """Gittersuche mit gemessenem Wellengieren; Kurshalten bei 5 und 6,5 kn, 10-Grad-Wechsel beide Seiten."""
    res = {}
    for k in KS:
        for Tg in TGS:
            for T_D in TDS:
                for db in DBS:
                    q = dict(P); q.update(k_ref=k, Tg=Tg, T_D=T_D, db=db, t_rev=1.0)
                    h5 = guete(lauf(q, Schiff(0.28, 6.5, 6.5, 3.7, 1.0, luv=10.0, welle=WELLE, seed=23, tau_w=TAU), dauer=400, sog=5.0))
                    h6 = guete(lauf(q, Schiff(0.42, 5.3, 6.5, 3.7, 1.0, luv=10.0, welle=WELLE, seed=24, tau_w=TAU), dauer=400, sog=6.5))
                    c = [kw(q, 0.28, 6.5, 5.0, d) for d in (10, -10)]
                    tr = (h5['trend'] + h6['trend']) / 2; au = (h5['aus'] + h6['aus']) / 2
                    pu = (h5['pumpe'] + h6['pumpe']) / 2; la = (h5['laeufe'] + h6['laeufe']) / 2
                    um = (h5['umkehr'] + h6['umkehr']) / 2 + sum(x[2] for x in c) / 2
                    tz = max(x[0] for x in c); ue = max(x[1] for x in c)
                    kosten = {'ruhig':   tr + au / 2 + 0.02 * pu + 0.05 * la + 2 * um + 0.3 * ue + 0.03 * tz,
                              'sparsam': tr / 2 + au / 4 + 0.1 * pu + 0.15 * la + 2 * um + 0.2 * ue + 0.02 * tz}
                    for satz, kc in kosten.items():
                        if satz not in res or kc < res[satz][0]:
                            res[satz] = (kc, q, tr, pu, la, um, tz, ue)
    for satz, (kc, q, tr, pu, la, um, tz, ue) in res.items():
        print('%-8s k_ref %.1f Tg %.0f T_D %.0f db %.1f | Trend %.2f° Pumpe %.0f%% Laeufe %.1f/min Umkehr %.2f/min | 10°: %.0f s, Überschw. %.1f°' % (
            satz, q['k_ref'], q['Tg'], q['T_D'], q['db'], tr, pu, la, um, tz, ue))

TAU, WELLE = 1.2, 0.5
KS, TGS, TDS, DBS = (1.4, 2.0, 2.8, 4.0), (3.0, 4.0, 6.0), (0.0, 1.0, 2.0), (3.5, 4.5, 6.0)   # Suchgitter (erweitert)
if __name__ == '__main__':
    werte() if len(sys.argv) > 1 and sys.argv[1] == 'werte' else kalibrieren()
