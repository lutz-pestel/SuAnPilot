#!/usr/bin/env python3
# Werte des SuAn-Reglers im TinyPilot setzen und zurücklesen (Goldene Regel). PyPilot-AI, 02.10.2026.
#   python setzen.py                      -> alle ap.pilot.suan.* anzeigen
#   python setzen.py k_ref=1.2 Tg=3 ...   -> setzen, danach jeden Wert prüfen
import socket, sys, time

def tinypilot():
    "Adresse des TinyPilot (Name box) aus den DHCP-Eintraegen des Masters; sonst letzte bekannte."
    import subprocess
    try:
        out = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', 'pi@10.10.10.1',
                              'cat /var/lib/misc/dnsmasq.leases'], capture_output=True, text=True, timeout=15).stdout
        for line in out.splitlines():
            f = line.split()
            if len(f) > 3 and f[3] == 'box':
                return f[2]
    except Exception:
        pass
    return '10.10.10.164'

HOST = tinypilot()

def lesen(namen, warte=2.0):
    s = socket.create_connection((HOST, 23322), timeout=5)
    s.sendall(('watch={' + ','.join('"%s":true' % n for n in namen) + '}\n').encode())
    end, buf = time.time() + warte, b''
    s.settimeout(0.5)
    while time.time() < end:
        try: buf += s.recv(65536)
        except Exception: pass
    s.close()
    v = {}
    for l in buf.decode(errors='replace').splitlines():
        if '=' in l:
            k, x = l.split('=', 1); v[k] = x
    return v

if __name__ == '__main__':
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from suan import PARAMS
    namen = ['ap.pilot.suan.' + n for n, *_ in PARAMS] + ['ap.pilot', 'ap.pilot.suan.status']
    neu = dict(a.split('=', 1) for a in sys.argv[1:])
    if neu:
        s = socket.create_connection((HOST, 23322), timeout=5)
        for n, x in neu.items():
            s.sendall(('ap.pilot.suan.%s=%s\n' % (n, float(x))).encode())
        time.sleep(1); s.close()
    v = lesen(namen)
    fehler = 0
    for n, *_ in PARAMS:
        ist = v.get('ap.pilot.suan.' + n)
        mark = ''
        if n in neu:
            ok = ist is not None and abs(float(ist) - float(neu[n])) < 1e-3
            mark = 'gesetzt OK' if ok else 'FEHLER: soll %s' % neu[n]
            fehler += not ok
        print('%-11s %10s  %s' % (n, ist, mark))
    print('Regler:', v.get('ap.pilot'), ' Zustand:', v.get('ap.pilot.suan.status'))
    if neu: print('ALLE WERTE GEPRÜFT' if not fehler else '%d WERT(E) FALSCH' % fehler)
