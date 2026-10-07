#!/usr/bin/env python3
# Fehlertoleranz pruefen: Pumpe rueckwaerts zeitweise schwach oder tot (wie 03.10.2026 gemessen: 0,5-1,4 statt ~4 Grad/s).
import importlib.util, sys
from sim import Schiff, lauf, guete
from adaptive import AdaptiveCore
def lade(pfad):
    spec = importlib.util.spec_from_file_location('alt', pfad); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.AdaptiveCore
K, T = 0.28, 6.5
P = dict(k_ref=1.0, Tg=2, v_ref=6.5, n_v=1, K_ref=0.42, T_I=60, r_max_stb=1.5, r_max_bb=1.5, T_ramp=5.3,
         rate_up=6.5, rate_down=3.7, delay=1.0, db=2.5, t_rev=1.0)
kerne = [('neu (tolerant)', AdaptiveCore)] + ([('alt (v2)', lade(sys.argv[1]))] if len(sys.argv) > 1 else [])
faelle = [('Pumpe gesund', []), ('rueckw. 25 % ab 60 s', [(60, 400, 0.25)]), ('rueckw. 25 % 60-180 s', [(60, 180, 0.25)]),
          ('rueckw. tot ab 60 s', [(60, 400, 0.0)])]
for name, kern in kerne:
    for fn, fe in faelle:
        sch = Schiff(K, T, 6.5, 3.7, 1.0, luv=10.0, welle=0.5, seed=41, tau_w=1.2); sch.fehler = fe
        log = lauf(P, sch, dauer=300, ereignisse=[(100, 'kurs', 10), (160, 'kurs', -10), (220, 'kurs', 10)], kern=kern)
        g = guete(log, ab=30)
        zust = sorted(set(x[4] for x in log if x[4] not in ('ok', 'abgleich')))
        ende = log[-1][4]
        print('%-15s %-22s Trend %4.2f  max %5.1f  Ende nach %3.0f s: %-34s weitere Zustaende: %s' % (
            name, fn, g['trend'], g['max'], log[-1][0], ende, ', '.join(z for z in zust if z != ende)[:70]))
