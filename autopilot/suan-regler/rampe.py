#!/usr/bin/env python3
# Versuch Anlauf-Rampe der Pumpe (PyPilot-AI, 03.10.2026). Der Controller faehrt die Motorspannung mit
# servo.max_slew_speed (Beschleunigen) / servo.max_slew_slow (Abbremsen) hoch; Stand 03.10.: 29,9 / 50 %.
#   python rampe.py            -> Werte anzeigen
#   python rampe.py 60         -> max_slew_speed auf 60 % (Original wird beim ersten Mal in rampe_original.txt gesichert)
#   python rampe.py zurueck    -> Original wiederherstellen
# Nur mit Zustimmung des Betreibers; danach 5 min beobachten (Pumpenlaeufe, Strom, Geraeusch).
import os, socket, sys, time
from setzen import tinypilot, lesen
import setzen

ORIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rampe_original.txt')
NAMEN = ['servo.max_slew_speed', 'servo.max_slew_slow']

def schreiben(name, wert):
    s = socket.create_connection((setzen.HOST, 23322), timeout=5)
    s.sendall(('%s=%s\n' % (name, wert)).encode()); time.sleep(1); s.close()

if __name__ == '__main__':
    v = lesen(NAMEN)
    print('jetzt: max_slew_speed %s, max_slew_slow %s' % (v.get(NAMEN[0]), v.get(NAMEN[1])))
    if len(sys.argv) < 2:
        sys.exit()
    if sys.argv[1] == 'zurueck':
        if not os.path.exists(ORIG):
            sys.exit('kein gesichertes Original (rampe_original.txt)')
        ziel = float(open(ORIG).read().split()[0])
    else:
        ziel = float(sys.argv[1])
        if not 0 < ziel <= 100:
            sys.exit('Wert 1..100')
        if not os.path.exists(ORIG):
            open(ORIG, 'w').write('%s %s\n' % (v.get(NAMEN[0]), v.get(NAMEN[1])))
            print('Original gesichert:', open(ORIG).read().strip())
    schreiben(NAMEN[0], ziel)
    if sys.argv[1] == 'zurueck':      # pypilot haelt slow >= speed: slow wird beim Hochsetzen mitverstellt
        schreiben(NAMEN[1], float(open(ORIG).read().split()[1]))
    v = lesen(NAMEN)
    neu = float(v.get(NAMEN[0], 'nan'))
    print('max_slew_speed jetzt %.2f (soll %.2f): %s; max_slew_slow %s' % (
        neu, ziel, 'GEPRUEFT' if abs(neu - ziel) < 0.5 else 'FEHLER', v.get(NAMEN[1])))
