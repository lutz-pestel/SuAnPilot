# Wache: liest die laufende Aufzeichnung mit; meldet und endet bei Böe, Flaute, großer Abweichung oder AP aus.
# Nach einem Auslöser werden noch NACH s aufgezeichnet, dann Zusammenfassung je 10 s.
import csv, glob, os, sys, time, statistics as st
NACH = int(sys.argv[1]) if len(sys.argv) > 1 else 90
p = max(glob.glob('/home/pi/aplog/data/signals_*.csv'), key=os.path.getmtime)
h = open(p).readline().strip().split(',')
f = open(p); f.seek(0, 2)
hist, trig, t_trig, err_since, war_an = [], None, None, None, False
def fl(x):
    try: return float(x)
    except: return None
while True:
    line = f.readline()
    if not line:
        time.sleep(0.2); continue
    r = dict(zip(h, line.strip().split(',')))
    t = fl(r.get('time'))
    if t is None: continue
    r['t'] = t; hist.append(r)
    hist = [x for x in hist if x['t'] > t - 400]
    if trig is None:
        w30 = [fl(x['wind.speed']) for x in hist if x['t'] > t - 30 and fl(x['wind.speed']) is not None]
        w120 = [fl(x['wind.speed']) for x in hist if x['t'] > t - 120 and fl(x['wind.speed']) is not None]
        he10 = [abs(fl(x['imu.heel'])) for x in hist if x['t'] > t - 10 and fl(x['imu.heel']) is not None]
        e = fl(r.get('ap.heading_error'))
        err_since = (err_since or t) if (e is not None and abs(e) > 15 and r.get('ap.enabled') == 'True') else None
        if r.get('ap.enabled') == 'True':
            war_an = True
        if r.get('ap.enabled') != 'True':
            if war_an:
                trig, t_trig, NACH = 'Autopilot aus', t, 5
            continue
        elif len(he10) > 30 and st.mean(he10) > 17:
            trig = 'Böe: Krängung 10 s Ø %.1f°, Wind %.1f kn' % (st.mean(he10), st.mean(w30) if w30 else 0)
        elif hist[0]['t'] < t - 115 and len(w120) > 400 and st.mean(w120) < 10:
            trig = 'Flaute: Wind 2 min Ø %.1f kn' % st.mean(w120)
        elif err_since and t - err_since > 10:
            trig = 'Kursabweichung > 15° seit 10 s'
        if trig:
            t_trig = t
            if trig == 'Autopilot aus': NACH = 5
    elif t > t_trig + NACH:
        break
print('AUSLÖSER %s um %s' % (trig, time.strftime('%H:%M:%S', time.localtime(t_trig))))
for a in range(int(t_trig - 120), int(t + 1), 10):
    seg = [x for x in hist if a <= x['t'] < a + 10]
    if not seg: continue
    g = lambda k: [fl(x[k]) for x in seg if fl(x[k]) is not None]
    e, ru, he, w = g('ap.heading_error'), g('rudder.angle'), g('imu.heel'), g('wind.speed')
    print('%s Fehl %+5.1f (%+4.0f..%+4.0f) Ruder %4.0f..%4.0f Kräng %4.1f Wind %4.1f AP %s' % (
        time.strftime('%H:%M:%S', time.localtime(a)), st.mean(e), min(e), max(e), min(ru), max(ru),
        st.mean(he), st.mean(w) if w else 0, seg[-1].get('ap.enabled')))
