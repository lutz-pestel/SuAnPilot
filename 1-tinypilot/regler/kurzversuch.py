#!/usr/bin/env python3
# Kurzversuch Unterspannung im Dialog, Version 00.01, Stand 07.10.2026 (PyPilot-AI). NUR IM HAFEN: Autopilot aus,
# Ruder frei, niemand am Steuerrad. Jeder Aufruf = eine Folge: Wartezeit (Weg zum Controller), Ruder +ZIEL -> -ZIEL
# (rueckwaerts), Pause (Ruhespannung ablesen), -ZIEL -> +ZIEL (vorwaerts). Danach Strom, Spannung, Ausfall je Lauf.
#   python kurzversuch.py --position            -> Ruder auf +15 Grad bringen (kurze Stoesse)
#   python kurzversuch.py "Batterie"            -> eine Folge, Bedingung "Batterie"
#   python kurzversuch.py --notiz "Batterie 1: Ruhe 12,6 / rueckw 11,3 / vorw 11,6"   -> Messwerte des Betreibers eintragen
#   Optionen: --warten 30 (s bis Start), --pause 10 (s bei -ZIEL), --ziel 15, --host 127.0.0.1 (diag_mock.py), --ordner X
# Ergebnis: 1-tinypilot/daten/diagnose/kurzversuch_<Datum>.csv (eine Zeile je Lauf bzw. Notiz) und Rohdaten je Folge.
import csv, os, sys, time
import diagnose
from unterspannung import ruhespannung, spannung_im_lauf, datenluecke

VERSION = '00.01'
FELDER = ['zeit', 'bedingung', 'folge', 'name', 'richtung', 'ist_s', 'ruder_start', 'ruderweg', 'grad_s', 'i_mittel', 'i_max',
          'u_ruhe', 'u_lauf', 'u_min', 'befund', 'notiz']

def optionen(args):
    o = dict(host=None, warten=30.0, pause=10.0, ziel=15.0, position=False, notiz=None,
             ordner=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daten', 'diagnose'))
    for opt in ('--host', '--warten', '--pause', '--ziel', '--ordner', '--notiz'):
        if opt in args:
            i = args.index(opt); wert = args[i + 1]; del args[i:i + 2]
            o[opt[2:]] = float(wert) if opt in ('--warten', '--pause', '--ziel') else wert
    if '--position' in args:
        args.remove('--position'); o['position'] = True
    o['bedingung'] = ' '.join(args) or 'ohne Angabe'
    return o

def anhaengen(pfad, zeilen):
    neu = not os.path.exists(pfad)
    with open(pfad, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FELDER, extrasaction='ignore')
        if neu: w.writeheader()
        w.writerows(zeilen)

def main():
    o = optionen(sys.argv[1:])
    tagesdatei = os.path.join(o['ordner'], 'kurzversuch_%s.csv' % time.strftime('%Y-%m-%d'))
    if o['notiz']:
        anhaengen(tagesdatei, [dict(zeit=time.strftime('%H:%M:%S'), notiz=o['notiz'])])
        print('Notiz eingetragen:', o['notiz']); return
    if o['ziel'] > 21:
        sys.exit('Ziel hoechstens 21 Grad (Schutzgrenze 25 Grad)')
    # diagnose.lauf() stoppt bei Anzeige > GRENZE - 6: so bei ZIEL - 2, denn das Ruder laeuft waehrend der Anzeigeverzoegerung weiter
    diagnose.GRENZE = o['ziel'] + 4.0
    folge = 1
    if os.path.exists(tagesdatei):
        folge += len({r['folge'] for r in csv.DictReader(open(tagesdatei)) if r.get('folge')})
    host = o['host'] or diagnose.finde_tinypilot()
    stamm = os.path.join(o['ordner'], 'kurzversuch_%s' % time.strftime('%Y-%m-%d_%H%M%S'))
    roh = open(stamm + '_roh.csv', 'w', newline='')
    p = diagnose.Pumpe(host, roh)
    laeufe = []
    try:
        for _ in range(30):
            if isinstance(p.ruder(), (int, float)): break
            time.sleep(0.2)
        if p.v.get('ap.enabled') is True:
            sys.exit('Autopilot eingeschaltet – Abbruch')
        r = p.ruder()
        if not isinstance(r, (int, float)):
            sys.exit('Keine Ruderanzeige – Abbruch')
        if o['position'] or abs(r - o['ziel']) > 4.0:
            print('Ruder bei %.1f Grad, bringe es auf +%.0f Grad ...' % (r, o['ziel']), flush=True)
            diagnose.fahre_auf(p, o['ziel'], [])
            print('Ruder jetzt bei %.1f Grad' % p.ruder(), flush=True)
            if o['position']: return
        print('Folge %d, %s (Kurzversuch %s, TinyPilot %s)' % (folge, o['bedingung'], VERSION, host), flush=True)
        t_los = time.time() + o['warten']
        print('  Start in %.0f s, um %s' % (o['warten'], time.strftime('%H:%M:%S', time.localtime(t_los))), flush=True)
        while time.time() < t_los - 0.05:
            rest = t_los - time.time()
            time.sleep(min(1.0, rest))
            rest = t_los - time.time()
            if 0.5 < rest <= 5.5 or (rest > 5.5 and round(rest) % 10 == 0):
                print('  Start in %2.0f s' % rest, flush=True)
        nachl = diagnose.DELAY + 1.5                        # so lange braucht lauf() fuer die Endlage (Anzeige verzoegert)
        for richtung, name in ((-1, 'rueckw'), (1, 'vorw')):
            print('\a' + time.strftime('%H:%M:%S'), '%s laeuft (nach %+.0f Grad) – jetzt ablesen' % (
                'RUECKWAERTS' if richtung < 0 else 'VORWAERTS', richtung * o['ziel']), flush=True)
            t0 = time.time()
            u_ruhe = ruhespannung(p, t0)
            e = diagnose.lauf(p, richtung, 15.0, laeufe, name, nachlauf=nachl)
            if richtung < 0:
                print('  PAUSE – Ruhespannung jetzt ablesen (noch %.0f s)' % max(0.0, o['pause'] - nachl), flush=True)
                time.sleep(max(0.0, o['pause'] - nachl))
            if e is None:
                continue
            e.update(zeit=time.strftime('%H:%M:%S', time.localtime(t0)), bedingung=o['bedingung'], folge=folge,
                     u_ruhe=u_ruhe, u_lauf=spannung_im_lauf(p, t0, e['ist_s']))
            if datenluecke(p, t0, e['ist_s']) > 1.0:
                e['befund'] = 'ungueltig: Datenluecke'
    except KeyboardInterrupt:
        print('ABBRUCH')
    finally:
        p.stop(); p.aus = True; time.sleep(0.5); roh.close()
        ok = [e for e in laeufe if 'zeit' in e]
        if ok:
            anhaengen(tagesdatei, ok)
            print('\nFolge %d, %s' % (folge, o['bedingung']))
            for e in ok:
                print('  %-6s %4.1f s  Ruder %5s -> Weg %6s  %5s Grad/s | Strom %5s A (Spitze %5s) | Spannung Ruhe %5s V, '
                      'im Lauf %5s V (tiefster %5s V) | %s' % (e['name'], e['ist_s'], e['ruder_start'], e['ruderweg'], e['grad_s'],
                      e['i_mittel'], e['i_max'], e['u_ruhe'], e['u_lauf'], e['u_min'], e['befund'] or 'normal'))

if __name__ == '__main__':
    main()
