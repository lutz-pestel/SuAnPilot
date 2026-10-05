#!/usr/bin/env python3
# Rueckwaertslaeufe wiederholen (Pumpenfehler rueckwaerts, PyPilot-AI 04.10.2026). NUR IM HAFEN, Ruder frei.
# Je Lauf: Ruder auf etwa +15 Grad, dann rueckwaerts 0,8 / 1,6 / 3 s. Aufruf: python rueckw_test.py ETIKETT [HOST]
import csv, os, sys, time
import diagnose

etikett = sys.argv[1] if len(sys.argv) > 1 else 'test'
host = sys.argv[2] if len(sys.argv) > 2 else diagnose.finde_tinypilot()
ordner = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Daten', 'diagnose')
os.makedirs(ordner, exist_ok=True)
stamm = os.path.join(os.path.abspath(ordner), 'rueckw_%s_%s' % (etikett, time.strftime('%Y-%m-%d_%H%M%S')))
roh = open(stamm + '_roh.csv', 'w', newline='')
p = diagnose.Pumpe(host, roh)
laeufe = []
try:
    for _ in range(30):
        if isinstance(p.ruder(), (int, float)): break
        time.sleep(0.2)
    else:
        sys.exit('keine Werte vom TinyPilot')
    if p.v.get('ap.enabled') is True:
        sys.exit('Autopilot eingeschaltet – Abbruch')
    print('Rampe max_slew_speed %s, Ruder %s' % (p.v.get('servo.max_slew_speed'), p.ruder()))
    for dauer in (0.8, 1.6, 0.8, 1.6, 3.0, 0.8, 1.6, 0.8, 1.6, 3.0, 0.8, 1.6, 3.0):
        diagnose.fahre_auf(p, 15.0, [])
        diagnose.lauf(p, -1, dauer, laeufe, 'R %.1fs' % dauer)
except KeyboardInterrupt:
    print('ABBRUCH')
finally:
    p.stop(); p.aus = True; roh.close()
    if laeufe:
        w = csv.DictWriter(open(stamm + '_laeufe.csv', 'w', newline=''), sorted({k for x in laeufe for k in x}))
        w.writeheader(); w.writerows(laeufe)
    gestoert = [x for x in laeufe if x['befund']]
    print('%s: %d Laeufe, gestoert (Strom < %.1f A, >= 0,8 s): %d' % (etikett, len(laeufe), diagnose.I_TOT, len(gestoert)))
