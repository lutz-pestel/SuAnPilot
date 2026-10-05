#!/usr/bin/env python3
# Lange Laeufe fuer Messung mit Multimeter an den Motorklemmen (PyPilot-AI 04.10.2026). NUR IM HAFEN.
# Folge: rueckw 8 s, vorw (bis Grenze), rueckw 8 s, vorw, rueckw 8 s; je 6 s Pause. Startet nach START s.
import sys, time
import diagnose
START = 20
host = sys.argv[1] if len(sys.argv) > 1 else diagnose.finde_tinypilot()
roh = open(diagnose.os.path.join(diagnose.os.path.dirname(diagnose.os.path.abspath(__file__)), '..', '..', 'Daten', 'diagnose',
                                 'messlauf_%s_roh.csv' % time.strftime('%Y-%m-%d_%H%M%S')), 'w', newline='')
p = diagnose.Pumpe(host, roh)
laeufe = []
try:
    for _ in range(30):
        if isinstance(p.ruder(), (int, float)): break
        time.sleep(0.2)
    if p.v.get('ap.enabled') is True:
        sys.exit('Autopilot eingeschaltet – Abbruch')
    diagnose.fahre_auf(p, 15.0, [])
    print('Start in %d s' % START); time.sleep(START)
    for richtung, dauer in ((-1, 8.0), (1, 8.0), (-1, 8.0), (1, 8.0), (-1, 8.0)):
        if richtung > 0:
            diagnose.fahre_auf(p, -18.0, [])
        print(time.strftime('%H:%M:%S'), 'Lauf', 'rueckw' if richtung < 0 else 'vorw', flush=True)
        diagnose.lauf(p, richtung, dauer, laeufe, 'Messung', nachlauf=6.0)
        if richtung < 0:
            diagnose.fahre_auf(p, 15.0, [])
except KeyboardInterrupt:
    print('ABBRUCH')
finally:
    p.stop(); p.aus = True; roh.close()
