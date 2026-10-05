#!/usr/bin/env python3
# Gütemaß und Bedingungen je Minute (PyPilot-AI, 02.10.2026). Definitionen: Doc/Testplan_Autopilot.md, „Auswertung“.
# Wird von pumpwatch.py laufend gefüttert (schreibt data/guete_<Datum>.csv) und vom Leitstand (Seite „Güte“) gelesen.
# Test: python3 guete.py SIGNALS.csv   → schreibt die Minutenzeilen auf den Bildschirm.
import csv, glob, math, os, statistics, sys, time

TREND = 20             # s, gleitendes Mittel des Kursfehlers
# Ampel-Grenzen (gut bis erster Wert, akzeptabel bis zweiter, darüber schlecht) – vorläufig
AMPEL = {'trend': (2, 4), 'wh_h': (10, 25), 'wechsel': (8, 20), 'ausreisser': (2, 10)}
SETTLE = 60            # s ohne Bewertung nach Start der Auswertung (Minute unvollständig, Trend ohne Vorlauf)
MAX_MB = 2000          # Obergrenze Datenordner; älteste Dateien werden gelöscht (Rohdaten zuerst)

FIELDS = ['zeit', 'n', 'ap_anteil', 'manoever', 'trend', 'ausreisser', 'wh_h', 'wechsel',
          'ampel_trend', 'ampel_wh_h', 'ampel_wechsel', 'ampel_ausreisser',
          'sog', 'wind', 'boeen', 'boeigkeit', 'kurs_zum_wind', 'kurs_klasse', 'wind_klasse',
          'stampfen', 'seegang', 'kraengung', 'kraeng_aenderung', 'kraeng_ursache',
          'bug', 'geradeaus_ruder', 'drehung',
          'P', 'I', 'D', 'DD', 'PR', 'H', 'gain', 'filter', 'pilot', 'satz']
SETTING_KEYS = {'P': 'ap.pilot.basic.P', 'I': 'ap.pilot.basic.I', 'D': 'ap.pilot.basic.D', 'DD': 'ap.pilot.basic.DD',
                'PR': 'ap.pilot.basic.PR', 'H': 'ap.pilot.basic.H', 'gain': 'servo.gain',
                'filter': 'imu.headingrate_lowpass_constant', 'pilot': 'ap.pilot', 'satz': 'ap.pilot.suan.sparsam'}

def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def ampel(key, v):
    if v is None:
        return ''
    a, b = AMPEL[key]
    return 'gut' if v < a else 'akzeptabel' if v <= b else 'schlecht'

def kurs_klasse(a):
    return '' if a is None else 'am Wind' if a < 60 else 'halber Wind' if a <= 110 else 'raumschots' if a <= 150 else 'vor dem Wind'

def wind_klasse(w):
    return '' if w is None else 'leicht' if w < 10 else 'mittel' if w <= 18 else 'stark'

def seegang(s):
    return '' if s is None else 0 if s < 0.3 else 1 if s < 0.8 else 2 if s <= 1.5 else 3

def mean(v):
    v = [x for x in v if x is not None]
    return statistics.mean(v) if v else None

def corr(a, b):
    p = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(p) < 10:
        return 0
    ma, mb = statistics.mean(x for x, _ in p), statistics.mean(y for _, y in p)
    sa = math.sqrt(sum((x - ma) ** 2 for x, _ in p)); sb = math.sqrt(sum((y - mb) ** 2 for _, y in p))
    return sum((x - ma) * (y - mb) for x, y in p) / (sa * sb) if sa and sb else 0

def latest_settings(data_dir):
    vals = {}
    files = glob.glob(os.path.join(data_dir, 'events_*.csv'))
    if files:
        for r in csv.reader(open(max(files, key=os.path.getmtime), newline='')):
            if len(r) == 3:
                vals[r[1]] = r[2]
    return vals

class Minuten:
    """Sammelt Zeilen der Aufzeichnung und gibt je abgeschlossener Minute eine Zeile (dict) aus."""
    def __init__(self, out, data_dir=None):
        self.out, self.data_dir = out, data_dir
        self.buf, self.prev = [], []      # Zeilen der laufenden Minute, letzte TREND s davor
        self.minute = None
        self.settle_until = None

    def add(self, r):
        t = fl(r.get('time'))
        if t is None:
            return
        if self.settle_until is None:
            self.settle_until = t + SETTLE
        m = int(t // 60)
        if self.minute is None:
            self.minute = m
        if m != self.minute:
            if self.buf:
                self.out(self.summary())
            self.prev = [x for x in self.prev + self.buf if fl(x['time']) > self.minute * 60 + 60 - TREND]
            self.buf, self.minute = [], m
        self.buf.append(r)

    def summary(self):
        rows, allr = self.buf, self.prev + self.buf
        g = lambda k: [fl(x.get(k)) for x in rows]
        on = [x.get('ap.enabled') == 'True' for x in rows]
        err = [fl(x.get('ap.heading_error')) if x.get('ap.enabled') == 'True' else None for x in allr]
        t_all = [fl(x['time']) for x in allr]
        k0 = len(self.prev)
        trend = []
        for i in range(k0, len(allr)):
            if err[i] is None:
                continue
            w = [err[j] for j in range(i, -1, -1) if t_all[j] > t_all[i] - TREND and err[j] is not None]
            trend.append(abs(statistics.mean(w)))
        e_on = [abs(v) for v in err[k0:] if v is not None]
        cmds = set(x.get('ap.heading_command') for x in rows if x.get('ap.enabled') == 'True')
        manoever = len(cmds) > 1 or (any(on) and not all(on))
        einschwingen = fl(rows[0]['time']) < self.settle_until     # erste Minute der Auswertung: nicht bewerten
        watt = [(c or 0) * (v or 12.5) for c, v in zip(g('servo.current'), g('servo.voltage'))]
        dirs = [x.get('servo.state') for x in rows if x.get('servo.state') in ('forward', 'reverse')]
        wech = sum(1 for a, b in zip(dirs, dirs[1:]) if a != b)
        dur = max(1.0, (fl(rows[-1]['time']) - fl(rows[0]['time'])) / 60)
        ws = [v for v in g('wind.speed') if v is not None]
        wd = [v for v in g('wind.direction') if v is not None]
        rel = mean([abs(((d + 180) % 360) - 180) for d in wd])
        heel = g('imu.heel'); roll = g('imu.roll')
        hv = [v for v in heel if v is not None]
        pitch = [v for v in g('imu.pitch') if v is not None]
        stampf = statistics.pstdev(pitch) if len(pitch) > 5 else None
        aend = (max(hv) - min(hv)) if hv else None
        rv = [v for v in roll if v is not None]
        if manoever:
            ursache = 'Kurve'
        elif aend and aend > 3 and corr([abs(v) if v is not None else None for v in heel], g('wind.speed')) > 0.5:
            ursache = 'Böe'
        elif len(rv) > 5 and statistics.pstdev(rv) > 2:
            ursache = 'Welle'
        else:
            ursache = ''
        # Geradeaus-Ruder (Verfahren B): mittlere Ruderlage der Minute; der Autopilot hält den Kurs, die
        # Drehung (°/s) bleibt fast null und wird nur mitgeschrieben. Anzeige-Fehler ist NICHT abgezogen.
        bug = ''
        if wd and min(wd) < -10 and max(wd) < 0:
            bug = 'BB'                                 # Wind von Backbord
        elif wd and max(wd) > 10 and min(wd) > 0:
            bug = 'StB'
        gr = dreh = None
        if all(on) and not manoever:
            gr = mean(g('rudder.angle'))
            hd = [v for v in g('ap.heading') if v is not None]
            if len(hd) > 1:
                dreh = sum((b - a + 180) % 360 - 180 for a, b in zip(hd, hd[1:])) / (dur * 60)
        tr = mean(trend) if trend else None
        aus = 100.0 * sum(1 for v in e_on if v > 10) / len(e_on) if e_on else None
        whh = mean(watt)
        wpm = wech / dur
        res = {'zeit': time.strftime('%Y-%m-%d %H:%M', time.localtime(self.minute * 60)), 'n': len(rows),
               'ap_anteil': round(sum(on) / float(len(on)), 2), 'manoever': int(manoever),
               'trend': r1(tr), 'ausreisser': r1(aus), 'wh_h': r1(whh), 'wechsel': r1(wpm),
               'ampel_trend': ampel('trend', tr) if all(on) and not manoever and not einschwingen else '',
               'ampel_wh_h': ampel('wh_h', whh) if all(on) and not manoever and not einschwingen else '',
               'ampel_wechsel': ampel('wechsel', wpm) if all(on) and not manoever and not einschwingen else '',
               'ampel_ausreisser': ampel('ausreisser', aus) if all(on) and not manoever and not einschwingen else '',
               'sog': r1(mean(g('gps.speed'))), 'wind': r1(mean(ws)), 'boeen': r1(max(ws) if ws else None),
               'boeigkeit': r1(statistics.pstdev(ws) if len(ws) > 5 else None),
               'kurs_zum_wind': r1(rel), 'kurs_klasse': kurs_klasse(rel), 'wind_klasse': wind_klasse(mean(ws)),
               'stampfen': r2(stampf), 'seegang': seegang(stampf), 'kraengung': r1(abs(mean(hv)) if hv else None),
               'kraeng_aenderung': r1(aend), 'kraeng_ursache': ursache,
               'bug': bug, 'geradeaus_ruder': r1(gr), 'drehung': '' if dreh is None else round(dreh, 3)}
        s = latest_settings(self.data_dir) if self.data_dir else {}
        for k, n in SETTING_KEYS.items():
            res[k] = s.get(n, '')
        return res

def r1(v):
    return '' if v is None else round(v, 1)

def r2(v):
    return '' if v is None else round(v, 2)

class Writer:
    """Schreibt Minutenzeilen in data/guete_<Datum>.csv, je Tag eine neue Datei."""
    def __init__(self, data_dir):
        self.dir, self.day, self.f, self.w = data_dir, None, None, None

    def __call__(self, row):
        day = row['zeit'][:10]
        if day != self.day:
            p = os.path.join(self.dir, 'guete_%s.csv' % day)
            if os.path.exists(p) and open(p).readline().strip().split(',') != FIELDS:
                os.rename(p, p[:-4] + '-1.csv')     # alte Spalten: umbenennen, sortiert davor
            new = not os.path.exists(p)
            self.f = open(p, 'a', newline=''); self.w = csv.DictWriter(self.f, FIELDS)
            if new:
                self.w.writeheader()
            self.day = day
        self.w.writerow(row); self.f.flush()

def trim(data_dir, max_mb=MAX_MB, keep=()):
    """Löscht älteste Dateien, bis der Ordner unter max_mb liegt; Rohdaten zuerst, Gütedateien zuletzt."""
    def size():
        return sum(os.path.getsize(os.path.join(data_dir, f)) for f in os.listdir(data_dir)) / 1e6
    removed = []
    for pattern in ('signals_*.csv', 'pumpruns_*.csv', 'events_*.csv', 'guete_*.csv'):
        files = sorted(glob.glob(os.path.join(data_dir, pattern)), key=os.path.getmtime)
        for f in files[:-1]:                      # die jüngste Datei jeder Art bleibt immer
            if size() <= max_mb:
                return removed
            if os.path.abspath(f) not in keep:
                os.remove(f); removed.append(os.path.basename(f))
    return removed

if __name__ == '__main__':
    w = csv.DictWriter(sys.stdout, FIELDS); w.writeheader()
    m = Minuten(w.writerow, os.path.dirname(os.path.abspath(sys.argv[1])))
    for r in csv.DictReader(open(sys.argv[1], newline='')):
        m.add(r)
