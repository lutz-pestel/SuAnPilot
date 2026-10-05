#!/usr/bin/env python3
# Ueberwacht jeden Pumpenlauf anhand der Aufzeichnung von aplog.py (signals_*.csv).
# pumpruns_*.csv: eine Zeile je Lauf (>= 0,6 s) mit Strom, Ruderweg, Geschwindigkeit und Befund.
# Kurze Stoesse (< 1,2 s) lassen sich nicht sicher bewerten: der Strom wird verzoegert gemeldet.
# Ihr mittlerer Strom je Richtung steht nur zur Beobachtung in pumpstatus.txt (kein Befund).
# pumpstatus.txt: Zusammenfassung der letzten 10 Minuten, jede Minute neu geschrieben.
# Zusätzlich: guete_<Datum>.csv (Gütemaß je Minute, guete.py) und Speichergrenze des Datenordners (stündlich).
# Aufruf: pumpwatch.py            (laufend, folgt der neuesten signals-Datei)
#         pumpwatch.py DATEI      (einmal auswerten, zum Testen; Ausgabe auf den Bildschirm)
import csv, glob, os, statistics, sys, time
import guete            # Gütemaß je Minute → data/guete_<Datum>.csv, Speichergrenze

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
MIN_RUN = 0.6          # kuerzere Laeufe werden nicht bewertet
LOW_CURRENT = 2.0      # A, darunter laeuft die Pumpe nicht richtig (30.09.: tot 1,3-1,5 A, gut 4-6 A)
HIGH_CURRENT = 15.0    # A
LAG = 1.0              # s, so spaet kommt die Ruderlage an
MIN_MOVE = 1.0         # Grad Ruderweg, den ein Lauf >= 1,5 s mindestens bringen muss
SLOW = 0.4             # Anteil der ueblichen Geschwindigkeit, darunter "langsam" (Laeufe >= 2 s)

def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

class Watch:
    def __init__(self, out):
        self.out = out            # Funktion fuer eine Ergebniszeile
        self.rows = []            # letzte ~15 s Zeilen fuer die Ruderlage nach dem Lauf
        self.run = None
        self.pending = []         # Laeufe, die noch auf die Ruderlage +LAG warten
        self.speeds = {'forward': [], 'reverse': []}
        self.history = []         # (zeit, richtung, dauer, befund)
        self.samples = []         # (zeit, laeuft) fuer die Einschaltdauer
        self.minute = []          # (zeit, richtung, strom) der laufenden Minute
        self.minute_start = None
        self.minutes = []         # (zeit, {richtung: (mittelstrom, n)}) der letzten 10 Minuten

    def add(self, r):
        t = fl(r.get('time'))
        if t is None:
            return
        state = r.get('servo.state', '')
        running = state in ('forward', 'reverse')
        self.samples.append((t, running))
        if self.minute_start is None:
            self.minute_start = t
        if running and fl(r.get('servo.current')) is not None:
            self.minute.append((t, state, fl(r.get('servo.current'))))
        if t - self.minute_start >= 60:
            self.check_minute(self.minute_start)
            self.minute, self.minute_start = [], t
        self.rows.append((t, fl(r.get('rudder.angle'))))
        self.rows = [x for x in self.rows if x[0] > t - 15]
        if self.run and (state != self.run['dir'] or t - self.run['last'] > 0.5):
            self.run['end'] = self.run['last']
            self.pending.append(self.run)
            self.run = None
        if running:
            if not self.run:
                self.run = {'dir': state, 'start': t, 'last': t, 'cur': [],
                            'r0': fl(r.get('rudder.angle')), 'ap': r.get('ap.enabled')}
            self.run['last'] = t
            c = fl(r.get('servo.current'))
            if c is not None:
                self.run['cur'].append(c)
        for p in list(self.pending):
            if t >= p['end'] + LAG:
                self.finish(p, self.rudder_at(p['end'] + LAG))
                self.pending.remove(p)

    def check_minute(self, t0):
        # Strom eine Messung nach Stossbeginn ist aussagekraeftiger; alle Messungen waehrend Laufs mitteln
        res = {}
        for d in ('forward', 'reverse'):
            c = [x[2] for x in self.minute if x[1] == d]
            if len(c) >= 5:
                res[d] = (statistics.mean(c), len(c))
        self.minutes.append((t0, res))
        del self.minutes[:-10]

    def rudder_at(self, t):
        best = None
        for x in self.rows:
            if x[1] is not None and (best is None or abs(x[0] - t) < abs(best[0] - t)):
                best = x
        return best[1] if best else None

    def finish(self, p, r1):
        d = p['end'] - p['start'] + 0.2
        if d < MIN_RUN:
            return
        cur = p['cur'][1:] or p['cur']
        cm = statistics.mean(cur) if cur else 0
        cx = max(p['cur']) if p['cur'] else 0
        move = (r1 - p['r0']) if (r1 is not None and p['r0'] is not None) else None
        sgn = 1 if p['dir'] == 'forward' else -1          # vorwaerts = Ruder Richtung plus
        speed = sgn * move / d if move is not None else None
        notes = []
        if d >= 1.2 and cm < LOW_CURRENT:
            notes.append('Strom niedrig - Pumpe steht?')
        if cx > HIGH_CURRENT:
            notes.append('Strom hoch')
        if d >= 1.5 and speed is not None and speed * d < MIN_MOVE:
            notes.append('Ruder bewegt sich nicht' if speed * d > -MIN_MOVE else 'Ruder laeuft falsch')
        usual = self.speeds[p['dir']]
        if d >= 2.0 and speed is not None and len(usual) >= 20 and speed < SLOW * statistics.median(usual):
            notes.append('langsam')
        if d >= 1.5 and speed is not None and not notes:
            usual.append(speed)
            del usual[:-30]
        self.history.append((p['start'], p['dir'], d, bool(notes)))
        self.out([time.strftime('%H:%M:%S', time.localtime(p['start'])), p['dir'], '%.1f' % d,
                  '%.1f' % cm, '%.1f' % cx, '' if p['r0'] is None else '%.1f' % p['r0'],
                  '' if move is None else '%.1f' % move, '' if speed is None else '%.1f' % speed,
                  p['ap'], '; '.join(notes)])

    def status(self, now):
        self.history = [x for x in self.history if x[0] > now - 3600]
        h = [x for x in self.history if x[0] > now - 600]
        s = [x for x in self.samples if x[0] > now - 600]
        self.samples = s
        lines = ['Stand %s, letzte 10 min' % time.strftime('%H:%M:%S', time.localtime(now))]
        for d in ('forward', 'reverse'):
            c = [m[1][d][0] for m in self.minutes if d in m[1]]
            lines.append('%-8s mittlerer Strom aller Stoesse je Minute: %s A' % (d, ' '.join('%.1f' % x for x in c) or '-'))
        if s:
            lines.append('Pumpe laeuft %.0f %% der Zeit, %d Laeufe' % (100 * sum(1 for x in s if x[1]) / len(s), len(h)))
        for d in ('forward', 'reverse'):
            u = self.speeds[d]
            lines.append('%-8s Laeufe %3d, auffaellig %2d, uebliche Geschwindigkeit %s Grad/s' % (
                d, sum(1 for x in h if x[1] == d), sum(1 for x in h if x[1] == d and x[3]),
                '%.1f' % statistics.median(u) if u else '-'))
        return '\n'.join(lines) + '\n'

HEADER = ['start', 'richtung', 'dauer_s', 'strom_mittel_A', 'strom_max_A', 'ruder_start',
          'ruderweg', 'grad_pro_s', 'ap', 'befund']

def once(path):
    w = Watch(lambda row: print(','.join(row)) if row[-1] else None)
    for r in csv.DictReader(open(path)):
        w.add(r)
    print(w.status(max(x[0] for x in w.samples)))

def follow():
    stamp = time.strftime('%Y-%m-%d_%H%M%S')
    out_f = open(os.path.join(DATA, 'pumpruns_%s.csv' % stamp), 'w', newline='')
    out_w = csv.writer(out_f)
    out_w.writerow(HEADER)
    out_f.flush()
    def out(row):
        out_w.writerow(row)
        out_f.flush()
    w = Watch(out)
    g = guete.Minuten(guete.Writer(DATA), DATA)
    path, f, reader_fields, last_status, last_trim = None, None, None, 0, 0
    buf = ''
    while True:
        newest = max(glob.glob(os.path.join(DATA, 'signals_*.csv')) or [''], key=lambda p: os.path.getmtime(p) if p else 0)
        if newest and newest != path:
            path, f = newest, open(newest)
            reader_fields = next(csv.reader([f.readline()]))
            f.seek(0, 2)                     # nur neue Zeilen
            buf = ''
        if f:
            buf += f.read()
            lines = buf.split('\n')
            buf = lines.pop()
            for row in csv.reader(lines):
                if len(row) == len(reader_fields):
                    r = dict(zip(reader_fields, row))
                    w.add(r)
                    try:
                        g.add(r)
                    except Exception as e:
                        print('guete:', e, flush=True)
        now = time.time()
        if now - last_status > 60:
            last_status = now
            tmp = os.path.join(DATA, 'pumpstatus.txt.tmp')
            open(tmp, 'w').write(w.status(now))
            os.replace(tmp, os.path.join(DATA, 'pumpstatus.txt'))
        if now - last_trim > 3600:
            last_trim = now
            try:
                gone = guete.trim(DATA, keep=(os.path.abspath(path or ''),))
                if gone:
                    print(time.strftime('%H:%M:%S'), 'Speichergrenze: gelöscht', ' '.join(gone), flush=True)
            except OSError as e:
                print('trim:', e, flush=True)
        time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        once(sys.argv[1])
    else:
        follow()
