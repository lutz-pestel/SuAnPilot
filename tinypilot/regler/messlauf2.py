#!/usr/bin/env python3
# Messung an der Klemmleiste des Controllers (Motor A/B gegen Masse), PyPilot-AI 04.10.2026. NUR IM HAFEN.
# Ruder einmal auf +18 Grad, dann 6 Rueckwaertslaeufe zu je 15 s mit 10 s Pause, ohne Vorwaertslauf dazwischen
# (der Fehler tritt eher auf, wenn kein Vorwaertslauf vorausging). Nur wenn das Ruder unter 0 Grad kommt, wird
# zurueckgefahren. Start 30 s nach Aufruf.
import os, sys, time
import diagnose
host = sys.argv[1] if len(sys.argv) > 1 else diagnose.finde_tinypilot()
ordner = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Daten', 'diagnose')
roh = open(os.path.join(ordner, 'messlauf2_%s_roh.csv' % time.strftime('%Y-%m-%d_%H%M%S')), 'w', newline='')
p = diagnose.Pumpe(host, roh)
laeufe = []
try:
    for _ in range(30):
        if isinstance(p.ruder(), (int, float)): break
        time.sleep(0.2)
    if p.v.get('ap.enabled') is True:
        sys.exit('Autopilot eingeschaltet – Abbruch')
    diagnose.fahre_auf(p, 18.0, [])
    rest = 30 - 0
    time.sleep(20)
    for n in range(1, 7):
        r = p.ruder()
        if isinstance(r, (int, float)) and r < 0:
            print('  Ruder %.1f – zurueck auf +18' % r); diagnose.fahre_auf(p, 18.0, []); time.sleep(5)
        print(time.strftime('%H:%M:%S'), 'Lauf %d rueckwaerts 15 s' % n, flush=True)
        diagnose.lauf(p, -1, 15.0, laeufe, 'Lauf %d' % n, nachlauf=10.0)
except KeyboardInterrupt:
    print('ABBRUCH')
finally:
    p.stop(); p.aus = True; roh.close()
