# Auswertung je Zeitabschnitt (Unix-Zeit). Auf dem Master nach /tmp kopieren; opt_eval3 braucht /tmp/opt_eval2.py.
# Aufruf: python3 /tmp/opt_eval2.py START [ENDE]   – Glob der signals-Datei bei Bedarf anpassen.
import csv, glob, statistics as st, sys, time
a = float(sys.argv[1]); b = float(sys.argv[2]) if len(sys.argv) > 2 else 1e12
f = sorted(glob.glob('/home/pi/aplog/data/signals_2026-10-01_*.csv'))[-1]
def fl(x):
    try: return float(x)
    except: return None
s = [r for r in csv.DictReader(open(f)) if fl(r['time']) and a <= fl(r['time']) < b
     and r['ap.enabled'] == 'True' and fl(r['rudder.angle']) is not None and fl(r['ap.heading_error']) is not None]
if len(s) < 150: print('zu wenig Daten', len(s)); sys.exit()
cmds = set(r['ap.heading_command'] for r in s)
t = [fl(r['time']) for r in s]; e = [fl(r['ap.heading_error']) for r in s]; n = len(e); W = 50
tr = [st.mean(e[max(0, i-W):min(n, i+W)]) for i in range(n)]
atr = list(map(abs, tr))
# laengste Strecke Trend > 5 Grad
lng = 0; cur = 0; 
for i in range(1, n):
    cur = cur + (t[i]-t[i-1]) if atr[i] > 5 else 0; lng = max(lng, cur)
dmin = (t[-1]-t[0]) / 60
runs = []; cr = []
for x, y in zip(s, s[1:]):
    if y['servo.state'] == x['servo.state'] and y['servo.state'] in ('forward', 'reverse') and fl(y['time']) - fl(x['time']) < 0.5:
        if not cr: cr = [x]
        cr.append(y)
    else:
        if cr: runs.append(cr); cr = []
dirs = [r[0]['servo.state'] for r in runs]; wech = sum(1 for p, q in zip(dirs, dirs[1:]) if p != q)
duty = 100 * sum(1 for r in s if r['servo.state'] in ('forward', 'reverse')) / n
g = lambda k: [v for v in (fl(r[k]) for r in s) if v is not None]
print('%s-%s %.1fmin Soll%s | Wind %.1f(B%.1f) Einf %.0f Kr %.1f Stampf %.2f | TREND |.| %.2f 95%% %.1f >5:%.1f%% laengste>5 %.0fs | Augenbl |.| %.1f | Laeufe %.1f/min Wechsel %.1f/min Pumpe %.0f%% Strom %.2fA | Ruder %.1f' % (
    time.strftime('%H:%M', time.gmtime(t[0]+7200)), time.strftime('%H:%M', time.gmtime(t[-1]+7200)), dmin, '' if len(cmds) == 1 else '(WECHSEL %d)' % len(cmds),
    st.mean(g('wind.speed')), max(g('wind.speed')), st.mean(g('wind.direction')), st.mean(g('imu.roll')), st.pstdev(g('imu.pitch')),
    st.mean(atr), sorted(atr)[int(.95*n)], 100*sum(1 for x in atr if x > 5)/n, lng, st.mean(map(abs, e)),
    len(runs)/dmin, wech/dmin, duty, st.mean(g('servo.current')), st.mean(g('rudder.angle'))))
