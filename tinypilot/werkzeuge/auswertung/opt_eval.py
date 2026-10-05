# Auswertung je Zeitabschnitt (Unix-Zeit). Auf dem Master nach /tmp kopieren; opt_eval3 braucht /tmp/opt_eval2.py.
# Aufruf: python3 /tmp/opt_eval.py START [ENDE]   – Glob der signals-Datei bei Bedarf anpassen.
import csv, glob, statistics as st, sys, time
# Aufruf: opt_eval.py <start_unix> [<ende_unix>]   (wertet nur AP-an-Zeilen ohne Sollkurswechsel-Anlauf)
a = float(sys.argv[1]); b = float(sys.argv[2]) if len(sys.argv) > 2 else 1e12
f = sorted(glob.glob('/home/pi/aplog/data/signals_2026-10-01_*.csv'))[-1]
def fl(x):
    try: return float(x)
    except: return None
s = [r for r in csv.DictReader(open(f)) if fl(r['time']) and a <= fl(r['time']) < b
     and r['ap.enabled'] == 'True' and fl(r['rudder.angle']) is not None and fl(r['ap.heading_error']) is not None]
if len(s) < 100:
    print('zu wenig Daten', len(s)); sys.exit()
dmin = (fl(s[-1]['time']) - fl(s[0]['time'])) / 60
g = lambda k: [v for v in (fl(r[k]) for r in s) if v is not None]
e = g('ap.heading_error'); ae = sorted(map(abs, e)); n = len(ae)
runs = []; cur = []
for x, y in zip(s, s[1:]):
    if y['servo.state'] == x['servo.state'] and y['servo.state'] in ('forward', 'reverse') and fl(y['time']) - fl(x['time']) < 0.5:
        if not cur: cur = [x]
        cur.append(y)
    else:
        if cur: runs.append(cur); cur = []
dirs = [r[0]['servo.state'] for r in runs]
wech = sum(1 for p, q in zip(dirs, dirs[1:]) if p != q)
ru = g('rudder.angle'); weg = sum(abs(q - p) for p, q in zip(ru, ru[1:]))
duty = 100 * sum(1 for r in s if r['servo.state'] in ('forward', 'reverse')) / len(s)
tot = 0
for r in runs:
    d = fl(r[-1]['time']) - fl(r[0]['time'])
    if d >= 0.8 and st.mean(fl(x['servo.current']) or 0 for x in r[1:]) < 2.5: tot += 1
print('%s-%s %.1fmin | Wind %.1f(B%.1f) Einf %.0f Kr %.1f Roll %.2f Stampf %.2f | Fehler %.2f 95%% %.1f >10 %.1f%% VZ %.1f | Laeufe %.1f/min Wechsel %.1f/min Pumpe %.0f%% Weg %.0f/min Strom %.2fA | Ruder %.1f max %.1f | tot %d' % (
    time.strftime('%H:%M', time.gmtime(fl(s[0]['time']) + 7200)), time.strftime('%H:%M', time.gmtime(fl(s[-1]['time']) + 7200)), dmin,
    st.mean(g('wind.speed')), max(g('wind.speed')), st.mean(g('wind.direction')), st.mean(g('imu.roll')), st.pstdev(g('imu.roll')), st.pstdev(g('imu.pitch')),
    st.mean(ae), ae[int(.95 * n)], 100 * sum(1 for x in ae if x > 10) / n, st.mean(e),
    len(runs) / dmin, wech / dmin, duty, weg / dmin, st.mean(g('servo.current')), st.mean(ru), max(map(abs, ru)), tot))
