#!/usr/bin/env python3
# Fehler rueckwaerts provozieren und messen (PyPilot-AI 04.10.2026). NUR IM HAFEN.
# Ruder auf +18, 20 s warten, dann kurze Rueckwaertsstoesse (1,2 s, 8 s Pause). Sobald ein Stoss gestoert ist,
# folgt sofort ein langer Rueckwaertslauf von 15 s zum Messen. Hoechstens 8 Stoesse, unter 3 min.
import os, sys, time
import diagnose
host = sys.argv[1] if len(sys.argv) > 1 else diagnose.finde_tinypilot()
ordner = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Daten', 'diagnose')
roh = open(os.path.join(ordner, 'messlauf3_%s_roh.csv' % time.strftime('%Y-%m-%d_%H%M%S')), 'w', newline='')
p = diagnose.Pumpe(host, roh)
laeufe = []
try:
    for _ in range(30):
        if isinstance(p.ruder(), (int, float)): break
        time.sleep(0.2)
    if p.v.get('ap.enabled') is True:
        sys.exit('Autopilot eingeschaltet – Abbruch')
    diagnose.fahre_auf(p, 18.0, [])
    time.sleep(20)
    for n in range(1, 9):
        print(time.strftime('%H:%M:%S'), 'Stoss %d rueckwaerts 1,2 s' % n, flush=True)
        e = diagnose.lauf(p, -1, 1.2, laeufe, 'Stoss %d' % n, nachlauf=8.0)
        if e and e['befund']:
            print(time.strftime('%H:%M:%S'), 'FEHLER da – langer Lauf rueckwaerts 15 s, JETZT MESSEN', flush=True)
            diagnose.lauf(p, -1, 15.0, laeufe, 'Messlauf', nachlauf=3.0)
            break
        r = p.ruder()
        if isinstance(r, (int, float)) and r < -12:
            print('  Ruder %.1f – Ende (kein weiterer Platz ohne Vorwaertslauf)' % r); break
except KeyboardInterrupt:
    print('ABBRUCH')
finally:
    p.stop(); p.aus = True; roh.close()
