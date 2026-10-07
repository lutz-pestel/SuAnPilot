#!/usr/bin/env python3
# Nachbildung TinyPilot-Pumpe fuer diagnose.py am PC (PyPilot-AI, 03.10.2026). Port 23322 auf 127.0.0.1.
# Ruder 6,5 Grad/s vorwaerts, 3,7 rueckwaerts, Anzeige 1 s verzoegert; Fehler: jeder 2. Rueckwaertslauf ab 0,8 s
# mit 25 % Foerderung und 1,4 A (wie 03.10. gemessen). Befehl verfaellt nach 1 s (wie pypilot).
import json, random, socket, threading, time
lock = threading.Lock()
z = dict(rud=0.0, cmd=0.0, t_cmd=0.0, n_rueck=0, fehler=False, t_start=0.0, last=0)
hist = []
def physik():
    while True:
        time.sleep(0.02); t = time.time()
        with lock:
            c = z['cmd'] if t - z['t_cmd'] < 1.0 else 0.0
            if c != 0 and z['last'] == 0:
                z['t_start'] = t
                if c < 0:
                    z['n_rueck'] += 1; z['fehler'] = (z['n_rueck'] % 2 == 0)
            z['last'] = c
            v = 6.5 if c > 0 else -3.7 if c < 0 else 0.0
            if c < 0 and z['fehler'] and t - z['t_start'] > 0.8: v *= 0.25
            z['rud'] = max(-35, min(35, z['rud'] + v * 0.02))
            hist.append((t, z['rud'])); del hist[:-200]
def werte():
    t = time.time()
    with lock:
        anz = next((r for ts, r in hist if ts >= t - 1.0), z['rud'])
        c = z['cmd'] if t - z['t_cmd'] < 1.0 else 0.0
        stoer = c < 0 and z['fehler'] and t - z['t_start'] > 0.8
        i = 0.0 if c == 0 else (1.4 if stoer else 4.2) + random.gauss(0, 0.2)
    return {'servo.command': c, 'servo.speed': c, 'servo.raw_command': c, 'servo.current': round(i, 2),
            'servo.voltage': round(12.9 - 0.2 * i, 2), 'servo.controller_temp': 27.0, 'servo.flags': 'SYNC',
            'servo.state': 'forward' if c > 0 else 'reverse' if c < 0 else 'idle', 'rudder.angle': round(anz + random.gauss(0, 0.15), 2),
            'ap.enabled': False, 'servo.max_slew_speed': 29.92, 'servo.max_slew_slow': 50.0}
def kunde(k):
    k.settimeout(0.05); buf = ''
    while True:
        try:
            d = k.recv(4096)
            if not d: return
            buf += d.decode()
        except socket.timeout:
            pass
        except OSError:
            return
        zl = buf.split('\n'); buf = zl.pop()
        for l in zl:
            if l.startswith('servo.command='):
                with lock: z['cmd'] = float(l.split('=', 1)[1]); z['t_cmd'] = time.time()
        try:
            k.sendall(''.join('%s=%s\n' % (n, json.dumps(x)) for n, x in werte().items()).encode())
        except OSError:
            return
        time.sleep(0.05)
threading.Thread(target=physik, daemon=True).start()
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1', 23322)); s.listen(2)
print('Nachbildung laeuft auf 127.0.0.1:23322')
while True:
    k, _ = s.accept(); threading.Thread(target=kunde, args=(k,), daemon=True).start()
