#!/usr/bin/env python3
# Auswertung der Rudersprünge von Hand (PyPilot-AI, 02.10.2026). Entwurf.md, Abschnitt 5.2.
# Aufruf:  python sprung.py SIGNALS.csv [VON_UHRZEIT BIS_UHRZEIT]      (Uhrzeit hh:mm, Ortszeit)
# Sucht im Standby (Autopilot aus) Rudersprünge (Taste oder Steuerrad) an der Ruderanzeige mit ruhiger Zeit davor/danach und
# passt je Sprung das Modell  T*dr/dt + r = K*(Ruder - Ruder_vorher) + r_vorher  an.
#   K  = Drehung (Grad/s) je Grad Ruder  (negativ: Ruder + dreht nach Backbord)
#   T  = Anlaufzeit (s)
# Das wahre Ruder ist die Anzeige, um DELAY (1 s) vorgezogen. Dazu Rudergeschwindigkeit je Richtung.
import csv, sys, time, statistics as st

VOR, NACH, MIN_LAUF, MAX_LAUF = 8.0, 15.0, 0.5, 4.5     # s ruhig davor / Auswertung danach / Laufdauer
DELAY = 1.0                                              # s Verzögerung der Ruderanzeige (gemessen 29.09.)
TASTE = 1.4                                              # s Pumpe je Tastendruck im Standby (Systembeschreibung)

def fl(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def lesen(pfad, von=None, bis=None):
    R = []
    for r in csv.DictReader(open(pfad, newline='')):
        t = fl(r.get('time'))
        if t is None: continue
        hm = time.strftime('%H:%M', time.localtime(t))
        if (von and hm < von) or (bis and hm > bis): continue
        R.append(dict(t=t, an=r.get('ap.enabled') == 'True', rate=fl(r.get('imu.headingrate_lowpass')),
                      ruder=fl(r.get('rudder.angle')), u=fl(r.get('servo.speed')) or 0.0,
                      sog=fl(r.get('gps.speed')), kurs=fl(r.get('ap.heading'))))
    return [x for x in R if x['rate'] is not None and x['ruder'] is not None]

def laeufe(R):
    out, i = [], 0
    while i < len(R):
        if R[i]['u'] != 0:
            j = i
            while j + 1 < len(R) and R[j + 1]['u'] * R[i]['u'] > 0: j += 1
            out.append((i, j)); i = j + 1
        else: i += 1
    return out

def anpassen(ts, rs, ds, r0):
    """Bestes T (Gitter) und K (lineare Ausgleichsrechnung) für T*dr/dt + r = K*d + r0."""
    best = None
    for T10 in range(5, 301, 5):
        T = T10 / 10.0
        sim, r = [], 0.0                                  # Antwort auf K = 1
        for k in range(len(ts)):
            if k: r += (ds[k - 1] - r) / T * (ts[k] - ts[k - 1])
            sim.append(r)
        y = [x - r0 for x in rs]
        nenner = sum(a * a for a in sim)
        if nenner <= 0: continue
        K = sum(a * b for a, b in zip(sim, y)) / nenner
        fehler = sum((K * a - b) ** 2 for a, b in zip(sim, y))
        if best is None or fehler < best[2]: best = (K, T, fehler)
    K, T, fehler = best
    y = [x - r0 for x in rs]; sy = sum((v - st.mean(y)) ** 2 for v in y)
    return K, T, (1 - fehler / sy) if sy > 0 else 0.0

def ruder_bei(R, t):
    """Ruderanzeige zum Zeitpunkt t (lineare Interpolation)."""
    lo, hi = 0, len(R) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if R[m]['t'] <= t: lo = m
        else: hi = m
    a, b = R[lo], R[hi]
    if b['t'] == a['t']: return a['ruder']
    return a['ruder'] + (b['ruder'] - a['ruder']) * (t - a['t']) / (b['t'] - a['t'])

def auswerten(R):
    """Sprünge an der Ruderanzeige erkennen (Taste oder Steuerrad, Autopilot aus).
    Das wahre Ruder ist die Anzeige, um DELAY vorgezogen."""
    erg, i, n = [], 0, len(R)
    while i < n:
        x = R[i]
        if x['an'] or x['t'] < R[0]['t'] + VOR:
            i += 1; continue
        vorher = [y for y in R[max(0, i - int(VOR * 6)):i] if x['t'] - VOR <= y['t'] < x['t']]
        if len(vorher) < VOR * 3 or any(y['an'] for y in vorher) or st.pstdev([y['ruder'] for y in vorher]) > 0.4:
            i += 1; continue
        d0 = st.mean(y['ruder'] for y in vorher)
        if abs(x['ruder'] - d0) < 1.0:
            i += 1; continue
        # Bewegung beginnt: Ende = Anzeige 2 s lang ruhig (Streuung < 0,3°)
        t0 = x['t']; j = i
        while j < n and R[j]['t'] < t0 + 6:
            ruhig = [y['ruder'] for y in R[j:j + 12] if y['t'] <= R[j]['t'] + 2]
            if len(ruhig) > 5 and st.pstdev(ruhig) < 0.3: break
            j += 1
        t1 = R[j]['t'] if j < n else t0
        d1 = ruder_bei(R, t1 + 1.0)
        hub = d1 - d0
        nach = [y for y in R[i:] if y['t'] <= t1 + NACH]
        rest = [y['ruder'] for y in nach if y['t'] > t1 + 1]
        if (t1 - t0 > 5 or abs(hub) < 2 or not nach or nach[-1]['t'] < t1 + NACH - 1 or any(y['an'] for y in nach)
                or len(rest) < 10 or st.pstdev(rest) > 0.5 or st.pstdev([y['rate'] for y in vorher]) > 0.5):
            i = j + 1; continue
        r0 = st.mean(y['rate'] for y in vorher)
        start = t0 - DELAY                                   # wahres Ruder begann um DELAY früher
        win = [y for y in R if start <= y['t'] <= t1 + NACH]
        ts = [y['t'] for y in win]
        ds = [ruder_bei(R, min(t + DELAY, R[-1]['t'])) - d0 for t in ts]
        K, T, guete = anpassen(ts, [y['rate'] for y in win], ds, r0)
        sog = [y['sog'] for y in win if y['sog'] is not None]
        erg.append(dict(zeit=time.strftime('%H:%M:%S', time.localtime(start)), hub=hub, dauer=t1 - t0,
                        rudergeschw=hub / max(t1 - t0, 0.2), K=K, T=T, R2=guete, sog=st.mean(sog) if sog else None))
        i = j + int(NACH * 5)
    return erg

if __name__ == '__main__':
    a = sys.argv[1:]
    R = lesen(a[0], *(a[1:3]))
    erg = auswerten(R)
    print('%-9s %7s %6s %9s %8s %6s %6s %5s' % ('Zeit', 'Ruder', 'Dauer', 'Grad/s', 'K', 'T s', 'Güte', 'SOG'))
    for e in erg:
        print('%-9s %+6.1f° %5.1fs %+8.2f %+8.3f %6.1f %6.2f %5s' % (e['zeit'], e['hub'], e['dauer'], e['rudergeschw'],
              e['K'], e['T'], e['R2'], '%.1f' % e['sog'] if e['sog'] else '–'))
    gut = [e for e in erg if e['R2'] > 0.6]
    for name, sel in (('Ruder +', lambda e: e['hub'] > 0), ('Ruder -', lambda e: e['hub'] < 0)):
        g = [e for e in gut if sel(e)]
        if g:
            ein = [abs(e['hub']) / TASTE for e in g if abs(e['hub']) < 12]      # Einzeldruck = 1,4 s Pumpe
            print('%s: n=%d  K Median %+.3f  T Median %.1f s  Rudergeschw. (Einzeldruck %.1f s) %s' % (
                name, len(g), st.median(e['K'] for e in g), st.median(e['T'] for e in g), TASTE,
                '%.2f Grad/s' % st.median(ein) if ein else '–'))
    if not gut: print('Keine auswertbaren Sprünge (Güte > 0,6) gefunden.')
