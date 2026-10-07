#!/usr/bin/env python3
# Hafenversuch Unterspannung, Version 00.01, Stand 07.10.2026 (PyPilot-AI). NUR IM HAFEN: Autopilot aus, Ruder frei,
# niemand am Steuerrad. Ablauf und Deutung: 1-tinypilot/docs/system/Testplan_Autopilot.md, "Hafenversuch Unterspannung".
# Lange Laeufe Backbord -> Steuerbord (rueckwaerts) und zurueck (vorwaerts); vor jedem Rueckwaertslauf 1, 10 oder 30 s
# Pause seit dem letzten Pumpenlauf (gemischt). Jeder Rueckwaertslauf wird angesagt (Multimeter 2-3 s nach Start ablesen).
#   python unterspannung.py "Stufe 2 ohne Ladung"         -> je Pause 10 Laeufe (etwa 20 min)
#   python unterspannung.py --n 3 "Probe"                 -> je Pause 3 Laeufe
#   python unterspannung.py --host 127.0.0.1 --ordner X "Probe"   (Test gegen diag_mock.py)
# Ergebnis in 1-tinypilot/daten/diagnose/: Rohdaten, Lauftabelle, Zusammenfassung. Strg+C haelt die Pumpe sofort an.
import csv, os, random, statistics as st, sys, time
import diagnose

VERSION = '00.01'
PAUSEN = (1.0, 10.0, 30.0)  # s vor jedem Rueckwaertslauf
DAUER = 15.0                # s, laengster Lauf; diagnose.lauf stoppt vorher am Ruderschutz (25 Grad)
T_MAX, T_OK = 55.0, 50.0    # Grad C Controller: darueber Pause, bis T_OK erreicht

def ruhespannung(p, t):
    """Bordspannung in den 1,5 s vor t, nur Werte bei stehender Pumpe."""
    u = [x[3] for x in p.fenster(t - 1.5, t) if x[2] < 0.5 and x[3] > 0]
    return round(st.mean(u), 2) if u else ''

def spannung_im_lauf(p, t0, dauer):
    u = [x[3] for x in p.fenster(t0 + 0.25, t0 + dauer) if x[3] > 0]
    return round(st.mean(u), 2) if u else ''

def datenluecke(p, t0, dauer):
    """Laengste Luecke der Messwerte im Lauf (s). Friert der PC ein, waere der Lauf sonst falsch bewertet (07.10.2026)."""
    t = [x[0] for x in p.fenster(t0 - 0.5, t0 + dauer + 0.5)]
    return max((b - a for a, b in zip(t, t[1:])), default=99.0)

def pruefen(p):
    if p.v.get('ap.enabled') is True:
        raise SystemExit('Autopilot eingeschaltet – Abbruch')
    flags = str(p.v.get('servo.flags', ''))
    if any(k in flags for k in ('OVERCURRENT', 'OVERTEMP', 'BADVOLTAGE')):
        raise SystemExit('Controller meldet %s – Abbruch' % flags)
    tc = p.v.get('servo.controller_temp')
    if isinstance(tc, (int, float)) and tc > T_MAX:
        print(time.strftime('%H:%M:%S'), 'Controller %.0f °C – Pause bis %.0f °C' % (tc, T_OK), flush=True)
        while isinstance(p.v.get('servo.controller_temp'), (int, float)) and p.v['servo.controller_temp'] > T_OK:
            time.sleep(10)

def main():
    args = sys.argv[1:]
    host, n, ordner = None, 10, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daten', 'diagnose')
    for opt in ('--host', '--n', '--ordner'):
        if opt in args:
            i = args.index(opt); wert = args[i + 1]; del args[i:i + 2]
            if opt == '--host': host = wert
            elif opt == '--n': n = int(wert)
            else: ordner = wert
    stufe = ' '.join(args) or 'ohne Angabe'
    host = host or diagnose.finde_tinypilot()
    plan = []
    for k in range(n):                                  # je Dreiergruppe jede Pause einmal, Reihenfolge fest gemischt
        drei = list(PAUSEN); random.Random(k).shuffle(drei); plan += drei
    stamm = os.path.join(ordner, 'unterspannung_%s' % time.strftime('%Y-%m-%d_%H%M%S'))
    print('Hafenversuch Unterspannung %s, TinyPilot %s, %s. NUR IM HAFEN, Ruder frei, niemand am Rad.' % (VERSION, host, stufe))
    print('%d Rueckwaertslaeufe, Dauer etwa %.0f min. Abbruch mit Strg+C.' % (len(plan), len(plan) * 40 / 60.0), flush=True)
    roh = open(stamm + '_roh.csv', 'w', newline='')
    p = diagnose.Pumpe(host, roh)
    laeufe = []
    try:
        for _ in range(30):
            if isinstance(p.ruder(), (int, float)): break
            time.sleep(0.2)
        pruefen(p)
        print('Ruder nach Backbord (etwa +18 Grad) ...', flush=True)
        diagnose.fahre_auf(p, 18.0, [])
        t_ende = time.time()                            # Ende des letzten Pumpenlaufs
        for k, pause in enumerate(plan):
            pruefen(p)
            t_los = max(time.time(), t_ende + pause)
            print('\a' + time.strftime('%H:%M:%S'), 'Lauf %d/%d RUECKWAERTS startet um %s (Pause %.0f s) – Multimeter '
                  '2-3 s nach Start ablesen' % (k + 1, len(plan), time.strftime('%H:%M:%S', time.localtime(t_los)), pause), flush=True)
            while time.time() < t_los:
                time.sleep(0.05)
            for richtung in (-1, 1):
                naechste = plan[k + 1] if k + 1 < len(plan) else 10.0
                # Nachlauf vorwaerts hoechstens so lang wie die naechste Pause (bei 1 s fehlt dann der Ruderweg vorwaerts)
                nachlauf = diagnose.DELAY + 1.5 if richtung < 0 else min(naechste, diagnose.DELAY + 1.5)
                t0 = time.time()
                u_ruhe = ruhespannung(p, t0)
                e = diagnose.lauf(p, richtung, DAUER, laeufe, '%s%d' % ('R' if richtung < 0 else 'V', k + 1), nachlauf=nachlauf)
                if e is None:
                    t_ende = time.time(); continue
                e.update(zeit=time.strftime('%H:%M:%S', time.localtime(t0)), stufe=stufe, pause_s=pause if richtung < 0 else '',
                         u_ruhe=u_ruhe, u_lauf=spannung_im_lauf(p, t0, e['ist_s']))
                if datenluecke(p, t0, e['ist_s']) > 1.0:
                    e['befund'] = 'ungueltig: Datenluecke'
                    print('  ungueltig: Messwerte fehlten waehrend des Laufs', flush=True)
                t_ende = t0 + e['ist_s']
    except KeyboardInterrupt:
        print('ABBRUCH')
    finally:
        p.stop(); p.aus = True; time.sleep(0.5); roh.close()     # Lese-Teil erst beenden, dann Datei schliessen
        felder = ['zeit', 'stufe', 'name', 'richtung', 'pause_s', 'ist_s', 'ruder_start', 'ruderweg', 'grad_s', 'i_mittel',
                  'i_max', 'u_ruhe', 'u_lauf', 'u_min', 'temp', 'flags', 'befund']
        with open(stamm + '_laeufe.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=felder, extrasaction='ignore'); w.writeheader(); w.writerows(laeufe)
        zusammenfassung(laeufe, stufe, stamm + '_zusammenfassung.txt')

def zusammenfassung(laeufe, stufe, pfad):
    def med(x, k):
        v = [e[k] for e in x if isinstance(e.get(k), (int, float))]
        return '%.2f' % st.median(v) if v else '-'
    zeilen = ['Hafenversuch Unterspannung %s, %s, %s' % (VERSION, stufe, time.strftime('%d.%m.%Y %H:%M')),
              'Richtung  Pause  Laeufe  gestoert  Ruhespannung  Spannung im Lauf  Strom  (Mediane; gestoert = unter %.1f A)' % diagnose.I_TOT]
    for richtung, pausen in (('rueckw', PAUSEN), ('vorw', (None,))):
        for pause in pausen:
            x = [e for e in laeufe if e.get('richtung') == richtung and 'zeit' in e and (pause is None or e.get('pause_s') == pause)
                 and not str(e.get('befund', '')).startswith('ungueltig')]
            if not x: continue
            zeilen.append('%-8s  %5s  %6d  %8d  %10s V  %14s V  %5s A' % (
                richtung, '%.0f s' % pause if pause else 'alle', len(x), sum(1 for e in x if e.get('befund')),
                med(x, 'u_ruhe'), med(x, 'u_lauf'), med(x, 'i_mittel')))
    n_ung = sum(1 for e in laeufe if str(e.get('befund', '')).startswith('ungueltig'))
    if n_ung:
        zeilen.append('%d Laeufe wegen Datenluecke nicht gewertet' % n_ung)
    text = '\n'.join(zeilen)
    print('\n' + text)
    open(pfad, 'w', encoding='utf-8').write(text + '\n')

if __name__ == '__main__':
    main()
