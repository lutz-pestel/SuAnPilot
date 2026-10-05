# Schiffsmodell aus beliebigen Ruderbewegungen (Hand oder Autopilot), je 60 s: T*dr/dt + r = K*(Ruder(t+delay) - Ruder0).
# Aufruf: python3 ident.py SIGNALS.csv VON BIS [DELAY]   (Uhrzeiten hh:mm). PyPilot-AI, 03.10.2026.
# Modell aus beliebigen Daten: T*dr/dt + r = K*(ruder(t+delay) - d0); je 60-s-Abschnitt K, T, d0
import csv, sys, time, statistics as st
f, von, bis = sys.argv[1], sys.argv[2], sys.argv[3]
DELAY = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
R = []
for r in csv.DictReader(open(f)):
    try:
        t = float(r['time']); hm = time.strftime('%H:%M', time.localtime(t))
        if von <= hm <= bis:
            R.append((t, float(r['imu.headingrate_lowpass']), float(r['rudder.angle']), r['ap.enabled'], float(r['gps.speed'] or 0)))
    except: pass
def rud(t):
    for x in R:
        if x[0] >= t: return x[2]
    return R[-1][2]
def fit(S):
    best = None
    ts = [x[0] for x in S]; rs = [x[1] for x in S]; ds = [rud(x[0] + DELAY) for x in S]
    for T10 in range(5, 151, 5):
        T = T10 / 10.0
        # Antwort auf Ruder (K=1) und auf Konstante (Bias) simulieren, Start mit gemessener Drehrate
        a = b = 0.0; A = []; B = []; C = []; c = rs[0]
        for k in range(len(ts)):
            if k:
                dt = ts[k] - ts[k-1]
                a += (ds[k-1] - a) / T * dt; b += (1 - b) / T * dt; c += (0 - c) / T * dt
            A.append(a); B.append(b); C.append(c)
        y = [r - cc for r, cc in zip(rs, C)]
        # y = K*A + m*B  (m = -K*d0)
        saa = sum(x*x for x in A); sbb = sum(x*x for x in B); sab = sum(x*z for x, z in zip(A, B))
        say = sum(x*z for x, z in zip(A, y)); sby = sum(x*z for x, z in zip(B, y))
        det = saa*sbb - sab*sab
        if abs(det) < 1e-9: continue
        K = (say*sbb - sby*sab)/det; m = (saa*sby - sab*say)/det
        err = sum((K*x + m*z - w)**2 for x, z, w in zip(A, B, y))
        if best is None or err < best[0]: best = (err, K, T, -m/K if K else 0)
    err, K, T, d0 = best
    sy = sum((v - st.mean(rs))**2 for v in rs)
    return K, T, d0, 1 - err/sy if sy else 0, st.pstdev(ds)
i = 0
print('Abschnitt  AP   SOG    K(°/s/°)   T(s)  Ruder0  Güte  Ruder-Streuung')
while i < len(R):
    S = [x for x in R[i:] if x[0] < R[i][0] + 60]
    if len(S) > 200:
        K, T, d0, g, sd = fit(S)
        print('%s  %s  %4.1f   %+7.3f   %5.1f  %+6.1f  %4.2f  %4.1f' % (time.strftime('%H:%M:%S', time.localtime(S[0][0])),
              'an ' if sum(x[3] == 'True' for x in S) > len(S)/2 else 'aus', st.mean(x[4] for x in S), K, T, d0, g, sd))
    i += len(S)
