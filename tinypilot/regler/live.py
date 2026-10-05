# Live-Beobachtung suan; schaltet bei Abbruchgrund selbst auf basic zurueck
import socket, time, sys, json
DAUER = float(sys.argv[1]) if len(sys.argv) > 1 else 180
SCHALT = len(sys.argv) > 2 and sys.argv[2] == 'ein'
s = socket.create_connection(('10.10.10.164', 23322), timeout=5)
if SCHALT:
    s.sendall(b'ap.pilot="suan"\n'); time.sleep(0.5)
keys = ['ap.enabled','ap.pilot','ap.heading_error','rudder.angle','servo.command','gps.speed','ap.heading_command',
        'ap.pilot.suan.status','ap.pilot.suan.soll','ap.pilot.suan.est','ap.pilot.suan.trim','ap.pilot.suan.k','imu.heel']
s.sendall(('watch={' + ','.join('"%s":0.2' % k for k in keys) + '}\n').encode())
s.settimeout(0.3); buf = ''; v = {}; t0 = time.time(); last = t0; win = []; over = None
def zur(grund):
    s.sendall(b'ap.pilot="basic"\n'); print('*** ZURUECK AUF BASIC:', grund, flush=True)
while time.time() - t0 < DAUER:
    try: buf += s.recv(65536).decode(errors='replace')
    except Exception: pass
    lines = buf.split('\n'); buf = lines.pop()
    for l in lines:
        if '=' in l:
            k, x = l.split('=', 1)
            try: v[k] = json.loads(x)
            except Exception: v[k] = x
    if 'ap.heading_error' in v and isinstance(v.get('ap.heading_error'), (int, float)):
        win.append((v['ap.heading_error'], v.get('rudder.angle'), v.get('servo.command')))
        e = v['ap.heading_error']
        if v.get('ap.pilot') == 'suan' and v.get('ap.enabled') is True:
            if abs(e) > 15:
                over = over or time.time()
                if time.time() - over > 10: zur('Kursfehler > 15 Grad seit 10 s'); break
            else: over = None
    if time.time() - last >= 10:
        last = time.time()
        es = [abs(w[0]) for w in win]; rs = [w[1] for w in win if isinstance(w[1], (int, float))]
        pu = [w[2] for w in win if isinstance(w[2], (int, float))]
        print('%3.0fs %s AP %s  Fehler Ø %4.1f max %4.1f  Ruder %5.1f..%5.1f  Pumpe an %3.0f%%  Soll %s Est %s Trim %s k %s SOG %s  %s' % (
            time.time() - t0, v.get('ap.pilot'), v.get('ap.enabled'), sum(es)/len(es) if es else -1, max(es) if es else -1,
            min(rs) if rs else 0, max(rs) if rs else 0, 100.0*sum(1 for p in pu if p)/len(pu) if pu else 0,
            v.get('ap.pilot.suan.soll'), v.get('ap.pilot.suan.est'), v.get('ap.pilot.suan.trim'), v.get('ap.pilot.suan.k'),
            v.get('gps.speed'), v.get('ap.pilot.suan.status')), flush=True)
        win = []
        if v.get('ap.pilot') != 'suan': print('Regler ist', v.get('ap.pilot'), flush=True)
