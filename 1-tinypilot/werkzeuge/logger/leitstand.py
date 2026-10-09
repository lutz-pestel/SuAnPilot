#!/usr/bin/env python3
# Leitstand Autopilot (PyPilot-AI, 01.–03.10.2026): Seite 1 „Lage“ (Lage, Ruder, Verlauf), Seite 2 „Güte“ (Kästen
# AP-Health, Umwelt, Ruder-Trimm aus guete_<Datum>.csv; Gesamtampel 60 min), Seite 3 „Einstellungen & Meldungen“
# (Regler/Satz umschalten, bestehende Probleme, Meldungsprotokoll). Seiten: Knöpfe oder Taste 1/2/3. Oben auf jeder
# Seite die Statuszeile; eine neue rote Meldung faerbt den Knopf 3 rot, bis Seite 3 angesehen wurde.
# Liest die Aufzeichnung von aplog.py / pumpwatch.py in data/. Einzige Eingriffe (03.10.2026, Betreiber: Leitstand zeigt
# vorrangig die Leistung, dazu ausgewaehlte Einstellungen redundant zur Weboberflaeche): Regler basic/adaptive und Satz
# ruhig/sparsam umschalten - mit Rueckfrage, Rueckmeldung aus dem TinyPilot und Markierung in marks.csv.
# Python 3.7, nur Tkinter. Aufruf: python3 leitstand.py   (Desktop-Symbol: Leitstand.desktop)
import csv, glob, io, json, os, socket, subprocess, threading, time, tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox

VERSION = '00.03'      # Version des Leitstands (Format NN.NN, jede Aenderung zaehlt hoch)
GUETE_ALT = 180        # s nach Ende der letzten Minute: Seite „Güte“ gilt als veraltet
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
STATUS = os.path.join(DATA, 'verbindung.json')       # schreibt aplog.py jede Sekunde
GERAETE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geraete.csv')   # bekannte Geraete: ip,name,funktion
NETZ = '10.10.10.'     # Master-Netz (/24)
DATEN_ALT = 10         # s: aelter als das = nicht verbunden
HISTORY = 600          # s Verlauf in den Grafiken
TREND = 20             # s Mittel fuer den Trend des Kursfehlers
RUDDER_LIMIT = 30
FAULTS = ('FAULT', 'OVERCURRENT', 'OVERTEMP', 'BADVOLTAGE', 'INVALID', 'DRIVER_TIMEOUT', 'RUDDER_FAULT', 'PIN_FAULT')
BG, FG, DIM, GRID = '#101418', '#e8e8e8', '#8a929a', '#2a3036'
RED, YEL, GRN, BLU = '#ff4d4d', '#ffcc33', '#44dd66', '#4da6ff'
RUDER_MITTE = 2.9      # °: Ruderanzeige bei Ruder mittig (gemessen 02.10.2026 unter Motor)
# Farbschwellen (Betrag): gelb = auffaellig, rot = Fehler, sonst gruen
LIMITS = {'trend': (2, 5), 'rudder.angle': (25, RUDDER_LIMIT - 1), 'imu.heel': (20, 28), 'servo.current': (10, 15)}
DEAD_CURRENT = 2.0     # A: Pumpe laeuft >= 1,2 s mit weniger Strom = steht (rot)
AMPEL = {'trend': (2, 4), 'wh_h': (10, 25), 'wechsel': (8, 20), 'ausreisser': (2, 10)}   # wie guete.py
ANZEIGE = {}  # Pilotname im Geraet -> Anzeigename, falls abweichend
GERAET = {v: k for k, v in ANZEIGE.items()}

def tinypilot_address():
    try:
        for line in open('/var/lib/misc/dnsmasq.leases'):
            f = line.split()
            if len(f) > 3 and f[3] == 'box':
                return f[2]
    except OSError:
        pass
    return '10.10.10.164'

def pypilot_setzen(name, wert):
    """Wert im TinyPilot setzen und zuruecklesen (Goldene Regel). Liefert den gelesenen Wert oder None."""
    s = socket.create_connection((tinypilot_address(), 23322), timeout=3)
    try:
        s.sendall(('%s=%s\n' % (name, json.dumps(wert))).encode())
        time.sleep(0.7)
        s.sendall(('watch={"%s":true}\n' % name).encode())
        s.settimeout(0.5); buf, ende = '', time.time() + 2.5
        while time.time() < ende:
            try:
                buf += s.recv(65536).decode(errors='replace')
            except socket.timeout:
                continue
            for z in buf.split('\n'):
                if z.startswith(name + '='):
                    return json.loads(z.split('=', 1)[1])
    finally:
        s.close()
    return None

def ping(ip, warte=1):
    """(antwortet, Ausgabe) eines einzelnen Pings."""
    try:
        r = subprocess.run(['ping', '-c', '1', '-n', '-W', str(warte), ip], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=warte + 4)
        return r.returncode == 0, r.stdout.decode(errors='replace')
    except Exception as e:
        return False, str(e)

def pypilot_probe(host):
    """(ok, Grund): nimmt der pypilot-Server an und sendet er Messwerte?"""
    try:
        s = socket.create_connection((host, 23322), timeout=3)
    except ConnectionRefusedError:
        return False, 'der pypilot-Dienst nimmt keine Verbindung an (abgestürzt oder startet noch).'
    except socket.timeout:
        return False, 'der pypilot-Dienst antwortet nicht (hängt oder startet noch).'
    except OSError as e:
        return False, 'Verbindung zum pypilot-Dienst nicht möglich (%s).' % e
    try:
        s.sendall(b'watch={"ap.heading":0.2,"imu.heading":0.2,"rudder.angle":0.2}\n')
        s.settimeout(0.5); buf, ende = '', time.time() + 3.5
        while time.time() < ende:
            try:
                data = s.recv(65536)
            except socket.timeout:
                continue
            if not data:
                return False, 'der pypilot-Dienst hat die Verbindung sofort geschlossen.'
            buf += data.decode(errors='replace')
            if any('=' in z and not z.startswith('watch') for z in buf.split('\n')):
                return True, ''
        return False, 'der pypilot-Dienst nimmt die Verbindung an, sendet aber keine Messwerte (Sensoren oder Dienst gestört).'
    except OSError as e:
        return False, 'der pypilot-Dienst bricht die Verbindung ab (%s).' % e
    finally:
        s.close()

class Verbindung:
    """Prueft im Hintergrund, ob die Aufzeichnung frische Daten vom TinyPilot hat; wenn nicht, wird die Ursache
    stufenweise ermittelt: Master-Netz -> TinyPilot im Netz -> pypilot-Dienst -> Aufzeichnung (aplog)."""
    def __init__(self):
        self.ok, self.text = False, 'wird geprüft …'
        threading.Thread(target=self.lauf, daemon=True).start()

    def lauf(self):
        while True:
            try:
                self.pruefen()
            except Exception as e:
                self.ok, self.text = False, 'Verbindungsprüfung selbst fehlgeschlagen: %s' % e
            time.sleep(2)

    def pruefen(self):
        try:
            d = json.load(open(STATUS))
        except (OSError, ValueError):
            d = None
        now = time.time()
        aplog_da = d is not None and abs(now - d.get('zeit', 0)) <= 5
        if aplog_da and d.get('zustand') == 'verbunden' and now - d.get('letzte_daten', 0) <= DATEN_ALT:
            self.ok, self.text = True, ''
            return
        host = tinypilot_address()
        antwortet, aus = ping(host)
        if not antwortet:
            if 'unreachable' in aus.lower():
                t = 'Der Master hat kein Netz zum TinyPilot (%s) – Netzwerk (br0) des Masters prüfen.' % host
            else:
                t = 'Der TinyPilot (%s) antwortet nicht im Netz – ausgeschaltet, startet noch oder Kabel/WLAN gestört.' % host
        else:
            ok, grund = pypilot_probe(host)
            if not ok:
                t = 'Der TinyPilot (%s) ist im Netz, aber %s' % (host, grund)
            elif not aplog_da:
                t = 'TinyPilot und pypilot sind in Ordnung. Die Aufzeichnung (aplog) am Master läuft nicht – „aplog.sh start“.'
            elif d.get('zustand') != 'verbunden':
                t = 'TinyPilot und pypilot sind in Ordnung. Die Aufzeichnung verbindet sich gerade neu (%s).' % (d.get('ursache') or '–')
            else:
                t = ('TinyPilot und pypilot sind in Ordnung. Die Aufzeichnung bekommt seit %.0f s nichts und verbindet sich neu.'
                     % (now - d.get('letzte_daten', now)))
        if not aplog_da and not t.endswith('„aplog.sh start“.'):
            t += ' Außerdem läuft die Aufzeichnung (aplog) nicht.'
        self.ok, self.text = False, t

def internet_pruefen():
    """(ja/nein, Text): erreicht der Master das Internet, und wenn nicht, woran liegt es?"""
    best = None
    try:
        for z in subprocess.run(['ip', '-4', 'route', 'show', 'default'], stdout=subprocess.PIPE, timeout=3).stdout.decode().splitlines():
            f = z.split()
            metric = int(f[f.index('metric') + 1]) if 'metric' in f else 0
            via = f[f.index('via') + 1] if 'via' in f else ''
            dev = f[f.index('dev') + 1] if 'dev' in f else ''
            if best is None or metric < best[0]:
                best = (metric, via, dev)
    except Exception:
        pass
    if best is None:
        return False, 'NEIN – kein Weg nach außen eingerichtet (Handy-Tethering am USB-Anschluss prüfen)'
    _, via, dev = best
    weg = '%s%s' % ('USB-Handy' if dev == 'usb0' else dev, ' – Gateway %s' % via if via else '')
    for host, port in (('1.1.1.1', 443), ('8.8.8.8', 53)):
        try:
            socket.create_connection((host, port), timeout=2).close()
            return True, 'ja – über %s' % weg
        except OSError:
            pass
    if via and not ping(via)[0]:
        return False, 'NEIN – das Gateway (%s) antwortet nicht (Handy aus, Tethering beendet oder Kabel)' % weg
    return False, 'NEIN – das Gateway (%s) antwortet, aber dahinter kein Internet (Handy ohne Mobilfunk oder Datenvolumen?)' % weg

def bekannte_geraete():
    """Zeilen aus geraete.csv (kennung,ip,name,funktion). Kennung = MAC-Adresse oder ihr Anfang (Hersteller/Geraet),
    wirkt auf jedes Geraet mit dieser Kennung; ohne Kennung zaehlt die IP. Die IP dient sonst nur zur Anzeige,
    wenn das Geraet nicht da ist."""
    out = []
    try:
        for r in csv.DictReader(open(GERAETE, newline='', encoding='utf-8')):
            z = dict((k, (r.get(k) or '').strip()) for k in ('kennung', 'ip', 'name', 'funktion'))
            z['kennung'] = z['kennung'].lower()
            if z['kennung'] or z['ip']:
                out.append(z)
    except OSError:
        pass
    return out

class Geraete:
    """Drei Hintergrundlaeufe: Internet alle 3 s; bekannte Geraete direkt anpingen (alle 5 s, solange Bild 4 offen ist,
    sonst alle 30 s); volle Suche im ganzen /24 (254 Rundrufe, findet neue Geraete) nur bei offenem Bild 4: einmal im Stoss beim Oeffnen, dann alle 60 s verteilt.
    Grund: Die Rundrufe belasten den eingebauten WLAN-Chip des Masters (06.10.2026 Anmeldungen am Zugangspunkt ausgefallen)."""
    def __init__(self):
        self.zeilen = [dict(ip=b['ip'], name=b['name'], funktion=b['funktion'], online=False, neu=False)
                       for b in bekannte_geraete() if b['ip']]
        self.stand, self.voll, self.fehler, self.version, self.aktiv = None, None, '', 0, False
        self.internet = (None, 'wird geprüft …', None)       # (ja/nein/None, Text, Zeit)
        for ziel in (self.lauf_suche, self.lauf_schnell, self.lauf_internet):
            threading.Thread(target=ziel, daemon=True).start()

    def lauf_suche(self):
        zuletzt = 0
        while True:
            if not self.aktiv:
                zuletzt = 0                                  # beim naechsten Oeffnen sofort suchen
            elif time.time() - zuletzt >= 60:
                beginn = time.time()
                try:
                    self.suchen(zuletzt == 0); self.fehler = ''    # erste Suche nach dem Oeffnen im Stoss, danach verteilt
                except Exception as e:
                    self.fehler = str(e)
                zuletzt = beginn
            time.sleep(1)

    def lauf_schnell(self):
        while True:
            try:
                self.auffrischen()
            except Exception as e:
                self.fehler = str(e)
            warte, aktiv = 0, self.aktiv
            while warte < (5 if aktiv else 30) and self.aktiv == aktiv:   # Wechsel des Bildes beendet das Warten
                time.sleep(1); warte += 1

    def lauf_internet(self):
        while True:
            try:
                ok, text = internet_pruefen()
            except Exception as e:
                ok, text = None, 'Prüfung fehlgeschlagen: %s' % e
            self.internet = (ok, text, time.time())
            self.version += 1
            time.sleep(3)

    @staticmethod
    def nachbarn():
        """(MAC-Adressen, Adressen mit ARP-Zustand REACHABLE) aus der Nachbartabelle des Masters."""
        mac, da = {}, set()
        try:
            for z in subprocess.run(['ip', 'neigh', 'show'], stdout=subprocess.PIPE, timeout=5).stdout.decode().splitlines():
                f = z.split()
                if f and f[0].startswith(NETZ):
                    if 'lladdr' in f:
                        mac[f[0]] = f[f.index('lladdr') + 1].lower()
                    if 'REACHABLE' in f:
                        da.add(f[0])
        except Exception:
            pass
        return mac, da

    @staticmethod
    def zuordnen(bekannt, ip, mac):
        """Passende Zeile der Liste: laengste passende Kennung, sonst gleiche IP ohne Kennung."""
        best = None
        for b in bekannt:
            if b['kennung'] and mac.startswith(b['kennung']) and (best is None or len(b['kennung']) > len(best['kennung'])):
                best = b
        if best is None:
            best = next((b for b in bekannt if not b['kennung'] and b['ip'] == ip), None)
        return best

    def auffrischen(self):
        """Nur die Zeilen der letzten Suche neu anpingen (schnell); neue Geraete findet erst die volle Suche."""
        basis = self.zeilen
        if not basis:
            return
        with ThreadPoolExecutor(16) as pool:
            antwort = list(pool.map(lambda r: ping(r['ip'])[0], basis))
        _, da = self.nachbarn()
        neu = [dict(r, online=a or r['ip'] in da) for r, a in zip(basis, antwort)]
        if self.zeilen is basis:                            # nicht, wenn die volle Suche inzwischen neu geliefert hat
            self.zeilen, self.stand = neu, time.time()
            self.version += 1

    def suchen(self, stoss=False):
        """Ping ueber das ganze /24. stoss: alle fast gleichzeitig (schnell, einmal beim Oeffnen); sonst mit 5 Pings
        gleichzeitig, das verteilt die Rundrufe ueber knapp eine Minute und schont den WLAN-Chip."""
        bekannt = bekannte_geraete()
        ips = [NETZ + str(i) for i in range(1, 255)]
        with ThreadPoolExecutor(48 if stoss else 5) as pool:
            antwort = dict(zip(ips, pool.map(lambda ip: ping(ip)[0], ips)))
        mac, arp = self.nachbarn()
        namen = {}
        try:
            for z in open('/var/lib/misc/dnsmasq.leases'):
                f = z.split()
                if len(f) > 3:
                    namen[f[2]] = f[3] if f[3] != '*' else ''
        except OSError:
            pass
        zeilen, gefunden = [], set()
        for ip in ips:
            if not (antwort[ip] or ip in arp):
                continue
            b = self.zuordnen(bekannt, ip, mac.get(ip, ''))
            if b:
                gefunden.add(id(b))
                zeilen.append(dict(ip=ip, name=b['name'], funktion=b['funktion'], online=True, neu=False))
            else:
                zeilen.append(dict(ip=ip, name=namen.get(ip) or '?', funktion='nicht in der Liste (Kennung %s)' % (mac.get(ip) or '?'),
                                   online=True, neu=True))
        for b in bekannt:                                  # in der Liste, aber nicht da: offline (nur mit IP darstellbar)
            if id(b) not in gefunden and b['ip']:
                ausserhalb = not b['ip'].startswith(NETZ)  # andere Netze (z. B. Handy am USB) werden gezielt angepingt
                zeilen.append(dict(ip=b['ip'], name=b['name'], funktion=b['funktion'],
                                   online=ausserhalb and ping(b['ip'])[0], neu=False))
        zeilen.sort(key=lambda r: (r['neu'], [int(x) if x.isdigit() else 0 for x in r['ip'].split('.')]))
        self.zeilen, self.stand, self.voll = zeilen, time.time(), time.time()
        self.version += 1

def markieren(text):
    with open(os.path.join(DATA, 'marks.csv'), 'a') as f:
        f.write('%s,%.2f,"%s"\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), time.time(), text))

def ampel_of(key, v):
    a, b = AMPEL[key]
    return 'gut' if v < a else 'akzeptabel' if v <= b else 'schlecht'

def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def mittel(v):
    """Mittelwert fuer Gleitkommazahlen; statistics.mean rechnet exakt mit Bruechen und war auf dem Pi ein Viertel der Last."""
    return sum(v) / len(v)

_CACHE = {}
def gecacht(key, sekunden, fn):
    """Ergebnis von fn() hoechstens alle <sekunden> neu berechnen (Dateisuche und -lesen nicht jede Sekunde)."""
    t, w = _CACHE.get(key, (0, None))
    if time.time() - t >= sekunden:
        w = fn()
        _CACHE[key] = (time.time(), w)
    return w

class Source:
    """Folgt der neuesten signals-Datei und haelt die letzten HISTORY Sekunden."""
    def __init__(self):
        self.path, self.f, self.fields, self.buf = None, None, None, ''
        self.rows = []

    def newest(self):
        def suche():
            files = glob.glob(os.path.join(DATA, 'signals_*.csv'))
            return max(files, key=os.path.getmtime) if files else None
        return gecacht('signals', 10, suche)

    def update(self):
        p = self.newest()
        if p and p != self.path:
            f = open(p, newline='')
            kopf = f.readline()
            if not kopf.endswith('\n'):                    # Kopfzeile fehlt noch (aplog wartet auf den TinyPilot):
                f.close()                                  # beim naechsten Durchlauf erneut versuchen
            else:
                if self.f:
                    self.f.close()
                self.path, self.f = p, f
                self.fields = next(csv.reader([kopf]))
                size = os.path.getsize(p)
                self.f.seek(max(0, size - 900000))       # ~10 min Verlauf
                if size > 900000:
                    self.f.readline()                      # angeschnittene Zeile verwerfen
                self.buf, self.rows = '', []
        if not self.f:
            return
        self.buf += self.f.read()
        lines = self.buf.split('\n')
        self.buf = lines.pop()
        for row in csv.reader(lines):
            if len(row) == len(self.fields):
                r = dict(zip(self.fields, row))
                r['_t'] = fl(r.get('time'))                  # einmal umrechnen, nicht bei jedem Durchlauf
                if r['_t']:
                    self.rows.append(r)
        if self.rows:
            grenze, i = self.rows[-1]['_t'] - HISTORY, 0
            while i < len(self.rows) and self.rows[i]['_t'] <= grenze:   # Zeilen sind nach Zeit geordnet
                i += 1
            if i:
                del self.rows[:i]

def last_settings():
    def lesen():
        vals = {}
        files = glob.glob(os.path.join(DATA, 'events_*.csv'))
        if files:
            for r in csv.reader(open(max(files, key=os.path.getmtime), newline='')):
                if len(r) == 3:
                    vals[r[1]] = r[2]
        return vals
    return gecacht('events', 5, lesen)

def recent_findings(now):
    def lesen():
        out = []
        files = glob.glob(os.path.join(DATA, 'pumpruns_*.csv'))
        if files:
            for r in csv.DictReader(open(max(files, key=os.path.getmtime), newline='')):
                if r.get('befund'):
                    out.append('%s Pumpe %s %s s: %s' % (r['start'], r['richtung'], r['dauer_s'], r['befund']))
        return out[-5:]
    return gecacht('befunde', 10, lesen)

class Leitstand:
    def __init__(self, root):
        self.root, self.src = root, Source()
        root.title('Leitstand Autopilot %s' % VERSION)
        root.configure(bg=BG)
        root.geometry('1024x600')
        big = ('DejaVu Sans', 16, 'bold'); mid = ('DejaVu Sans', 12); small = ('DejaVu Sans', 9)
        nav = tk.Frame(root, bg=BG); nav.pack(fill='x', padx=6)
        self.btn = {}
        for key, txt in (('lage', '1  Lage'), ('guete', '2  Güte'), ('einst', '3  Einstellungen & Meldungen'),
                         ('geraete', '4  Geräte')):
            b = tk.Button(nav, text=txt, font=small, relief='flat', bd=0, padx=10,
                          command=lambda k=key: self.show(k))
            b.pack(side='left', padx=2); self.btn[key] = b
        root.bind('1', lambda e: self.show('lage')); root.bind('2', lambda e: self.show('guete'))
        root.bind('3', lambda e: self.show('einst')); root.bind('4', lambda e: self.show('geraete'))
        self.status = tk.Label(nav, text='', bg=BG, font=('DejaVu Sans', 10, 'bold'), anchor='e')
        self.status.pack(side='right', padx=6)
        self.ctl, self.settings, self.unseen = {}, {}, False
        self.kopf = tk.Frame(root, bg=BG); self.kopf.pack(fill='x', padx=6)      # Platz fuer den Hinweis „nicht verbunden“
        self.banner = tk.Label(self.kopf, text='', bg=RED, fg='#ffffff', font=('DejaVu Sans', 11, 'bold'),
                               anchor='w', justify='left', wraplength=990, padx=8, pady=3)
        self.verbunden = None
        self.pages = {'lage': tk.Frame(root, bg=BG), 'guete': tk.Frame(root, bg=BG), 'einst': tk.Frame(root, bg=BG),
                      'geraete': tk.Frame(root, bg=BG)}
        self.verb, self.net, self.net_version = Verbindung(), Geraete(), -1
        self.g2 = tk.Canvas(self.pages['guete'], width=1012, height=480, bg=BG, highlightthickness=0)
        self.g2.pack(padx=6, pady=4)
        page = self.pages['lage']
        top = tk.Frame(page, bg=BG); top.pack(fill='x', padx=6, pady=4)
        self.lbl = {}
        for key, title in [('ap', 'Autopilot'), ('regler', 'Regler'), ('soll', 'Soll'), ('ist', 'Ist'), ('fehl', 'Abweichung'),
                           ('trend', 'Trend 20 s'), ('kraeng', 'Krängung'), ('wind', 'Wind'), ('fahrt', 'Fahrt')]:
            f = tk.Frame(top, bg=BG); f.pack(side='left', expand=True, fill='x')
            tk.Label(f, text=title, fg=DIM, bg=BG, font=small).pack()
            self.lbl[key] = tk.Label(f, text='–', fg=FG, bg=BG, font=mid if key == 'regler' else big); self.lbl[key].pack()
        self.rud = tk.Canvas(page, width=1012, height=100, bg=BG, highlightthickness=0); self.rud.pack(padx=6)
        self.graphs = tk.Canvas(page, width=1012, height=376, bg=BG, highlightthickness=0)
        self.graphs.pack(padx=6, pady=4)
        self.foot = tk.Label(root, text='', fg=DIM, bg=BG, font=small, anchor='w', justify='left')
        self.foot.pack(fill='x', padx=6)
        self.seite3(self.pages['einst'], mid, small)
        self.seite4(self.pages['geraete'])
        self.mid, self.small = mid, small
        self.n = 0
        self.page = None
        self.show('lage')
        self.tick()

    def seite3(self, page, mid, small):
        gross = ('DejaVu Sans', 13, 'bold')
        def titel(text):
            tk.Label(page, text=text, fg=BLU, bg=BG, font=('DejaVu Sans', 12, 'bold'), anchor='w').pack(fill='x', padx=8, pady=(8, 2))
        titel('Steuerung (wie in der Weboberfläche; mit Rückfrage, der TinyPilot bestätigt)')
        for zeile, gruppe, wahl in (('Regler', 'pilot', ('basic', 'adaptive')), ('Satz', 'satz', ('ruhig', 'sparsam'))):
            fr = tk.Frame(page, bg=BG); fr.pack(fill='x', padx=8, pady=2)
            tk.Label(fr, text=zeile, fg=DIM, bg=BG, font=mid, width=8, anchor='w').pack(side='left')
            for w in wahl:
                b = tk.Button(fr, text=w, font=gross, relief='flat', bd=0, padx=26, pady=6,
                              command=lambda g=gruppe, x=w: self.schalten(g, x))
                b.pack(side='left', padx=4); self.ctl[(gruppe, w)] = b
            info = tk.Label(fr, text='', fg=DIM, bg=BG, font=small, anchor='w', justify='left')
            info.pack(side='left', padx=12)
            setattr(self, 'info_' + gruppe, info)
        titel('Bestehende Probleme')
        self.state = tk.Label(page, text='', bg=BG, font=mid, anchor='w', justify='left')
        self.state.pack(fill='x', padx=8)
        titel('Meldungen (neueste unten)')
        pf = tk.Frame(page, bg=BG); pf.pack(fill='both', expand=True, padx=8, pady=(0, 6))
        sb = tk.Scrollbar(pf); sb.pack(side='right', fill='y')
        self.prob = tk.Text(pf, height=14, bg='#181d22', fg=FG, font=('DejaVu Sans', 10), relief='flat',
                            yscrollcommand=sb.set, state='disabled')
        self.prob.pack(side='left', fill='both', expand=True); sb.config(command=self.prob.yview)
        for c, col in (('rot', RED), ('gelb', YEL), ('gruen', GRN)):
            self.prob.tag_configure(c, foreground=col)
        self.active = {}           # Schluessel -> (Farbe, Text) der aktuell bestehenden Probleme
        self.seen = set()          # Einzelereignisse, die schon im Protokoll stehen

    def seite4(self, page):
        self.net_kopf = tk.Label(page, text='Geräte werden gesucht …', fg=BLU, bg=BG, font=('DejaVu Sans', 12, 'bold'), anchor='w')
        self.net_kopf.pack(fill='x', padx=8, pady=(8, 2))
        self.net_text = tk.Text(page, bg='#181d22', fg=FG, font=('DejaVu Sans Mono', 11), relief='flat',
                                height=18, state='disabled')
        self.net_text.pack(fill='both', expand=True, padx=8, pady=(0, 6))
        for c, col in (('gruen', GRN), ('rot', RED), ('gelb', YEL), ('dim', DIM)):
            self.net_text.tag_configure(c, foreground=col)

    def geraete_anzeigen(self):
        n = self.net
        if n.version == self.net_version:
            return
        self.net_version = n.version
        z = n.zeilen or []
        bek = [r for r in z if not r['neu']]; neu = [r for r in z if r['neu']]
        if n.voll is None:
            self.net_kopf.config(text='Geräte im Master-Netz %s0/24 – bekannt %d (online %d) – Suche nach neuen Geräten läuft …' % (
                NETZ, len(bek), sum(1 for r in bek if r['online'])))
        else:
            self.net_kopf.config(text='Geräte im Master-Netz %s0/24 – bekannt %d (online %d), neu %d – volle Suche %s' % (
                NETZ, len(bek), sum(1 for r in bek if r['online']), len(neu), time.strftime('%H:%M:%S', time.localtime(n.voll))))
        t = self.net_text
        t.config(state='normal'); t.delete('1.0', 'end')
        ok, text, zeit = n.internet                          # erste Zeile: Internet, alle 3 s geprüft
        t.insert('end', '● Internet-Zugang des Netzes: %s%s\n\n' % (text, '   (geprüft %s)' % time.strftime('%H:%M:%S', time.localtime(zeit)) if zeit else ''),
                 'dim' if ok is None else 'gruen' if ok else 'rot')
        t.insert('end', '   %-16s %-18s %-52s %s\n' % ('IP-Adresse', 'Name', 'Funktion', 'Zustand'), 'dim')
        for r in z:
            col = 'gelb' if r['neu'] else 'gruen' if r['online'] else 'rot'
            zustand = ('NEU, ' if r['neu'] else '') + ('online' if r['online'] else 'offline')
            t.insert('end', '● %-16s %-18s %-52s %s\n' % (r['ip'], r['name'][:18], r['funktion'][:52], zustand), col)
        if n.fehler:
            t.insert('end', '\nSuche gestört: %s\n' % n.fehler, 'rot')
        t.config(state='disabled')

    def show(self, key):
        if self.page == key:
            return
        if key == 'einst':
            self.unseen = False
        for k, p in self.pages.items():
            p.pack_forget()
        self.page = key
        self.knoepfe()
        self.pages[key].pack(before=self.foot, fill='both', expand=True)
        if key == 'guete' and self.verb.ok:
            self.draw_guete()
        elif key == 'geraete':
            self.net_version = -1
            self.geraete_anzeigen()
        self.net.aktiv = key == 'geraete'                  # volle Netzsuche nur, solange Bild 4 offen ist

    def knoepfe(self):
        for k, b in self.btn.items():
            rot = k == 'einst' and self.unseen
            b.config(bg=RED if rot else BLU if k == self.page else GRID, fg=FG)

    def tick(self):
        try:
            self.src.update()
            self.draw()
            if self.page == 'geraete':
                self.geraete_anzeigen()
        except Exception as e:
            self.log(time.time(), 'rot', 'Leitstand-Fehler: %s' % e)
        self.root.after(1000, self.tick)

    def log(self, t, col, msg):
        """Neue Zeile unten anfuegen, mit Zeitstempel; rollt mit, wenn die Liste unten stand."""
        p = self.prob
        if col == 'rot' and self.page != 'einst':
            self.unseen = True
            self.knoepfe()
        at_end = p.yview()[1] > 0.99
        mark = {'rot': '⚠ ', 'gruen': '✓ '}.get(col, '• ')
        p.config(state='normal')
        p.insert('end', '%s  %s%s\n' % (time.strftime('%H:%M:%S', time.localtime(t)), mark, msg), col)
        if int(p.index('end-1c').split('.')[0]) > 500:
            p.delete('1.0', '2.0')
        p.config(state='disabled')
        if at_end:
            p.see('end')

    def draw(self):
        rows, now = self.src.rows, time.time()
        if not self.verb.ok:
            self.getrennt(now)
            return
        if self.verbunden is not True:
            self.verbunden = True
            self.banner.pack_forget()
            for lb in self.lbl.values():
                lb.config(fg=FG)
            self.foot.config(fg=DIM)
            self.n = 0                                 # Grafiken und Güte sofort neu zeichnen
        if not rows:
            self.report([('daten', 'rot', 'Keine Aufzeichnung gefunden – läuft aplog? (aplog.sh status)')], [], now)
            return
        r = rows[-1]
        g = lambda k: fl(r.get(k))
        age = now - fl(r['time'])
        on = r.get('ap.enabled') == 'True'
        self.lbl['ap'].config(text='AN' if on else 'AUS', fg=GRN if on else YEL)
        self.settings = last_settings()
        self.regler_anzeigen(r)
        self.lbl['soll'].config(text='%.0f°' % g('ap.heading_command') if g('ap.heading_command') is not None else '–')
        self.lbl['ist'].config(text='%.0f°' % g('ap.heading') if g('ap.heading') is not None else '–')
        e = [fl(x['ap.heading_error']) for x in rows
             if fl(x['time']) > fl(r['time']) - TREND and fl(x['ap.heading_error']) is not None]
        fe, tr = g('ap.heading_error'), (mittel(e) if e else None)
        if not on:                                     # Standby: es gibt keinen Kursfehler
            fe = tr = None
        self.lbl['fehl'].config(text='%+.1f°' % fe if fe is not None else '–')
        self.lbl['trend'].config(text='%+.1f°' % tr if tr is not None else '–', fg=self.col('trend', tr, FG))
        h = g('imu.heel') if g('imu.heel') is not None else g('imu.roll')
        self.lbl['kraeng'].config(text='%.0f°' % abs(h) if h is not None else '–', fg=self.col('imu.heel', h, FG))
        ws, wd = g('wind.speed'), g('wind.direction')
        self.lbl['wind'].config(text=('%.0f kn/%.0f°' % (ws, wd)) if ws is not None and wd is not None else '–')
        self.lbl['fahrt'].config(text='%.1f kn' % g('gps.speed') if g('gps.speed') is not None else '–')
        self.rudder(g('rudder.angle'), r.get('servo.state', ''), g('servo.current'))
        if self.n % 3 == 0 and self.page == 'lage':   # Grafiken alle 3 s, spart Rechenzeit
            self.plot(rows)
        if self.n % 20 == 0 and self.page == 'guete':
            self.draw_guete()
        self.n += 1
        cond, events = self.check(rows, r, age)
        self.report(cond, events, fl(r['time']))
        self.footer(self.settings)

    def getrennt(self, now):
        """Keine frischen Daten: nichts Altes anzeigen, alles grau, auf jeder Seite der Hinweis mit Ursache."""
        text = 'NICHT VERBUNDEN – ' + self.verb.text
        self.banner.config(text=text)
        if self.verbunden is not False:
            self.verbunden = False
            self.banner.pack(fill='x', pady=(2, 0))
        for lb in self.lbl.values():
            lb.config(text='–', fg=DIM)
        for k in list(self.active):                    # Zustaende aus alten Daten verwerfen, nicht als „behoben“ melden
            if k != 'verbindung':
                del self.active[k]
        for b in self.ctl.values():
            b.config(state='disabled', bg=GRID, fg=DIM)
        self.info_pilot.config(text='nicht verbunden', fg=DIM)
        self.info_satz.config(text='', fg=DIM)
        for c, h in ((self.rud, 100), (self.graphs, 376), (self.g2, 480)):
            c.delete('all')
            c.create_text(506, h / 2, text='nicht verbunden – keine aktuellen Daten', fill=DIM, font=self.mid)
        self.foot.config(text='Nicht verbunden – keine Reglerwerte', fg=DIM)
        self.report([('verbindung', 'rot', text)], [], now)
        self.status.config(text='✗ NICHT VERBUNDEN', fg=RED)

    def regler_anzeigen(self, r):
        s = self.settings
        pilot = ANZEIGE.get(s.get('ap.pilot', ''), s.get('ap.pilot', '–'))
        satz = 'sparsam' if (fl(s.get('ap.pilot.adaptive.sparsam')) or 0) >= 0.5 else 'ruhig'
        zust = r.get('ap.pilot.adaptive.status', '')
        text, farbe = pilot, FG
        if pilot == 'adaptive':
            text = 'adaptive · %s' % satz
            farbe = GRN if zust in ('ok', 'abgleich', 'blind', '') else YEL if zust.startswith('Pumpe') else RED
        self.lbl['regler'].config(text=text, fg=farbe)
        if pilot == 'adaptive':
            vu, vd = fl(r.get('ap.pilot.adaptive.v_up')), fl(r.get('ap.pilot.adaptive.v_down'))
            ruder = ('   gelernte Rudergeschwindigkeit vorw. %.1f / rückw. %.1f °/s' % (vu, vd)) if vu and vd else ''
            zt = zust.replace('Rueckfall', 'Rückfall').replace('rueckw', 'rückwärts').replace('vorw', 'vorwärts')
            if zt.startswith('Pumpe'):
                zt += ' °/s (meldet, steuert weiter)'
            self.info_pilot.config(text='Zustand: %s%s' % (zt or '–', ruder), fg=farbe)
        else:
            self.info_pilot.config(text='basic regelt die Pumpengeschwindigkeit; Werte unten in der Fußzeile', fg=DIM)
        # Satz sparsam erst waehlbar, wenn er eingestellt ist (groesseres Totband als ruhig)
        sparsam_ok = (fl(s.get('ap.pilot.adaptive.db_sparsam')) or 0) > (fl(s.get('ap.pilot.adaptive.db')) or 0)
        self.info_satz.config(text='nur bei adaptive' if pilot != 'adaptive' else '' if sparsam_ok else
                              '„sparsam“ gesperrt: Satz noch nicht eingestellt (Totband nicht größer als bei „ruhig“)', fg=DIM)
        for (g, w), b in self.ctl.items():
            aktiv = (g == 'pilot' and w == pilot) or (g == 'satz' and w == satz and pilot == 'adaptive')
            gesperrt = g == 'satz' and (pilot != 'adaptive' or (w == 'sparsam' and not sparsam_ok))
            b.config(bg=BLU if aktiv else GRID, fg=FG, state='disabled' if gesperrt else 'normal')

    def schalten(self, gruppe, wahl):
        if gruppe == 'pilot':
            name, wert, frage = 'ap.pilot', GERAET.get(wahl, wahl), 'Regler auf „%s“ umschalten?' % wahl
            if wahl != 'basic':
                frage += '\n\nNur in freiem Wasser, Steuermann bereit. Rückweg: „basic“.'
        else:
            name, wert, frage = 'ap.pilot.adaptive.sparsam', 1.0 if wahl == 'sparsam' else 0.0, 'Satz „%s“ einstellen?' % wahl
        if not messagebox.askyesno('Leitstand', frage):
            return
        try:
            ist = pypilot_setzen(name, wert)
        except OSError as e:
            ist = None
            self.log(time.time(), 'rot', 'Umschalten fehlgeschlagen: %s' % e)
        if ist == wert or (isinstance(ist, (int, float)) and isinstance(wert, float) and abs(ist - wert) < 1e-3):
            self.log(time.time(), 'gruen', 'Umgeschaltet: %s → %s (im TinyPilot geprüft)' % (gruppe, wahl))
            markieren('Leitstand: %s -> %s' % (name, wert))
        else:
            self.log(time.time(), 'rot', 'Umschalten auf %s NICHT bestätigt (gelesen: %s)' % (wahl, ist))

    @staticmethod
    def col(key, v, normal=GRN):
        if v is None:
            return normal
        yel, red = LIMITS[key]
        return RED if abs(v) >= red else YEL if abs(v) >= yel else normal

    def rudder(self, a, state, cur):
        c = self.rud; c.delete('all'); cx = 506; s = 440.0 / 35
        c.create_text(cx, 10, text='Ruder', fill=DIM, font=self.small)
        c.create_rectangle(cx - 440, 25, cx + 440, 55, outline=GRID)
        for lim in (-RUDDER_LIMIT, RUDDER_LIMIT):            # Backbord (+) links, Steuerbord (-) rechts
            x = cx - lim * s
            c.create_line(x, 20, x, 60, fill=RED, dash=(3, 2))
        c.create_line(cx, 20, cx, 60, fill=DIM)
        if a is not None:
            x = cx - max(-35, min(35, a)) * s
            c.create_rectangle(min(cx, x), 28, max(cx, x), 52, fill=self.col('rudder.angle', a), outline='')
            c.create_text(cx, 70, text='%.1f° %s' % (abs(a), 'BB' if a > 0 else 'StB' if a < 0 else ''),
                          fill=FG, font=self.mid)
        c.create_text(20, 40, text='BB', fill=DIM, font=self.small)
        c.create_text(990, 40, text='StB', fill=DIM, font=self.small)
        pumpe = {'forward': '◀ Pumpe BB', 'reverse': 'Pumpe StB ▶'}.get(state, 'Pumpe steht')
        c.create_text(cx, 92, text='%s   %.1f A' % (pumpe, cur or 0),
                      fill=GRN if state in ('forward', 'reverse') else DIM, font=self.small)

    @staticmethod
    def line(c, pts):
        """Linie aus (x, y, farbe), in Stuecken gleicher Farbe gezeichnet; None unterbricht die Linie."""
        if None in pts:
            k = pts.index(None)
            Leitstand.line(c, pts[:k]); Leitstand.line(c, pts[k + 1:])
            return
        i = 0
        while i < len(pts) - 1:
            j, col = i, pts[i][2]
            while j + 1 < len(pts) and pts[j + 1][2] == col:
                j += 1
            seg = pts[i:j + 2]
            if len(seg) >= 2:
                c.create_line(*[v for p in seg for v in p[:2]], fill=col, width=1 if col == GRN else 2)
            i = j + 1

    def plot(self, rows):
        c = self.graphs; c.delete('all')
        t0 = fl(rows[-1]['time']) - HISTORY; H = 92
        X = lambda t: 40 + (t - t0) / HISTORY * 970
        spec = [('Kursfehler °  (Farbe nach Trend 20 s; weiße Linie: Trend)', 'ap.heading_error', 15),
                ('Ruder ° (+ = BB)', 'rudder.angle', 35), ('Krängung °', 'imu.heel', 30),
                ('Strom A  (Marken: Pumpe läuft; rot = läuft ohne Strom)', 'servo.current', 12)]
        ev = [fl(x['ap.heading_error']) if x.get('ap.enabled') == 'True' else None for x in rows]
        trend, last = [], None
        for j in range(len(rows)):
            if j % 5 == 0 or j == len(rows) - 1:
                w = [v for v in ev[max(0, j - TREND * 5):j + 1] if v is not None]
                last = mittel(w) if w and ev[j] is not None else None
            trend.append(last)
        dead = self.dead_runs(rows)
        step = max(1, len(rows) // 485)
        for i, (title, key, rng) in enumerate(spec):
            y0 = i * (H + 2); ym = y0 + H / 2
            cur = key == 'servo.current'
            base, sc = (y0 + H, H / float(rng)) if cur else (ym, H / 2.0 / rng)
            c.create_rectangle(40, y0, 1010, y0 + H, outline=GRID)
            if not cur:
                c.create_line(40, ym, 1010, ym, fill=GRID)
            pts = []
            for j in range(0, len(rows), step):
                v = fl(rows[j].get(key))
                if key == 'ap.heading_error' and rows[j].get('ap.enabled') != 'True':
                    if pts and pts[-1] is not None:
                        pts.append(None)                # Standby: Linie aussetzen
                    continue
                if v is None:
                    continue
                colr = self.col('trend', trend[j]) if key == 'ap.heading_error' else self.col(key, v)
                pts.append((X(fl(rows[j]['time'])), base - max(-rng, min(rng, v)) * sc, colr))
            self.line(c, pts)
            if key == 'ap.heading_error':
                tp = []
                for j in range(0, len(rows), 25):
                    if trend[j] is None:
                        if tp and tp[-1] is not None:
                            tp.append(None)
                    else:
                        tp.append((X(fl(rows[j]['time'])), ym - max(-rng, min(rng, trend[j])) * sc, FG))
                self.line(c, tp)
            if cur:
                for j in range(0, len(rows), 2):
                    if rows[j].get('servo.state') in ('forward', 'reverse'):
                        px = X(fl(rows[j]['time']))
                        c.create_line(px, y0 + H - 5, px, y0 + H, fill=RED if j in dead else DIM)
            c.create_text(46, y0 + 8, text=title, fill=DIM, anchor='w', font=self.small)
            c.create_text(36, y0 + 6, text='%g' % rng, fill=DIM, anchor='e', font=self.small)
            c.create_text(36, y0 + H - 6, text='%g' % (0 if cur else -rng), fill=DIM, anchor='e', font=self.small)
        c.create_text(1010, 4 * (H + 2) - 2, text='letzte %d min' % (HISTORY // 60), fill=DIM, anchor='se', font=self.small)

    @staticmethod
    def dead_runs(rows):
        """Indizes von Pumpenlaeufen >= 1,2 s mit mittlerem Strom < DEAD_CURRENT (Pumpe steht)."""
        out, i = set(), 0
        while i < len(rows):
            st = rows[i].get('servo.state')
            if st in ('forward', 'reverse'):
                j = i
                while j + 1 < len(rows) and rows[j + 1].get('servo.state') == st:
                    j += 1
                d = fl(rows[j]['time']) - fl(rows[i]['time']) + 0.2
                cs = [fl(x.get('servo.current')) for x in rows[i + 1:j + 1] if fl(x.get('servo.current')) is not None]
                if d >= 1.2 and cs and mittel(cs) < DEAD_CURRENT:
                    out.update(range(i, j + 1))
                i = j + 1
            else:
                i += 1
        return out

    def check(self, rows, r, age):
        """(bestehende Zustaende [(schluessel, farbe, text)], Einzelereignisse [(zeit, farbe, text)])"""
        p, ev = [], []
        if age > 10:
            p.append(('daten', 'rot', 'Keine neuen Daten – Verbindung zum TinyPilot oder Aufzeichnung gestört'))
        bad = [f for f in r.get('servo.flags', '').replace('"', '').split() if any(k in f for k in FAULTS)]
        if bad:
            p.append(('servo', 'rot', 'Servo meldet: ' + ' '.join(bad)))
        if fl(r.get('ap.heading')) is None and r.get('ap.enabled') == 'True':
            p.append(('kompass', 'rot', 'Kein Kurs vom Kompass'))
        v = fl(r.get('servo.voltage'))
        if v is not None and not 11.5 <= v <= 15.5:
            p.append(('spannung', 'gelb', 'Bordspannung %.1f V' % v))
        ct = fl(r.get('servo.controller_temp'))
        if ct is not None and ct > 55:
            p.append(('temp', 'gelb', 'Controller-Temperatur %.0f °C' % ct))
        ra = fl(r.get('rudder.angle'))
        if ra is not None and abs(ra) >= LIMITS['rudder.angle'][1]:
            p.append(('ruder', 'gelb', 'Ruder am Bereichsende'))
        if abs(time.time() - fl(r['time'])) > 3600:
            p.append(('uhr', 'gelb', 'Uhrzeit Master und Aufzeichnung weichen ab'))
        for a, x in zip(rows, rows[1:]):
            t = fl(x['time'])
            if a.get('ap.enabled') == 'True' and x.get('ap.enabled') == 'False':
                ev.append((t, 'gelb', 'Autopilot ausgeschaltet'))
            rec = x.get('servo.recovery', '')
            if rec and rec != a.get('servo.recovery', ''):
                ev.append((t, 'rot' if ('steht' in rec or 'ohne Erfolg' in rec) else 'gelb', 'Selbsthilfe: ' + rec))
        if self.settings.get('ap.pilot') == 'adaptive':
            zust = r.get('ap.pilot.adaptive.status', '')
            if zust.startswith('Pumpe'):
                zust = zust.replace('vorw', 'vorwärts').replace('rueckw', 'rückwärts')
                p.append(('adaptive', 'gelb', 'adaptive: %s °/s – meldet und steuert weiter' % zust))
        for a, x in zip(rows, rows[1:]):
            za, zx = a.get('ap.pilot.adaptive.status', ''), x.get('ap.pilot.adaptive.status', '')
            if zx.startswith('Rueckfall') and not za.startswith('Rueckfall'):
                ev.append((fl(x['time']), 'rot', 'adaptive übergibt an basic: ' + zx.split(':', 1)[-1].strip()))
        for f in recent_findings(time.time()):
            ev.append((None, 'rot', f))
        return p, ev

    def report(self, cond, events, t):
        new = []                                       # (zeit, farbe, text), nach Zeit sortiert eintragen
        now_keys = set(k for k, _, _ in cond)
        for k, col, msg in cond:                       # neu aufgetreten
            if k not in self.active:
                new.append((t, col, msg))
            self.active[k] = (col, msg)
        for k in list(self.active):                    # behoben
            if k not in now_keys:
                new.append((t, 'gruen', 'behoben: ' + self.active.pop(k)[1]))
        for et, col, msg in events:                    # Einzelereignisse nur einmal
            if (et, msg) not in self.seen:
                self.seen.add((et, msg))
                new.append((et or t, col, msg))
        for et, col, msg in sorted(new, key=lambda x: x[0]):
            self.log(et, col, msg)
        reds = sum(1 for c, _ in self.active.values() if c == 'rot')
        yel = len(self.active) - reds
        liste = '\n'.join(('⚠ ' if c == 'rot' else '• ') + m for c, m in sorted(self.active.values(), key=lambda x: x[0] != 'rot'))
        if reds:
            kurz, farbe = '⚠ %d Fehler, %d Hinweise  → 3' % (reds, yel), RED
        elif yel:
            kurz, farbe = '• %d Hinweise  → 3' % yel, YEL
        else:
            kurz, farbe = '✓ Keine bestehenden Probleme', GRN
        self.status.config(text=kurz, fg=farbe)
        self.state.config(text=liste or '✓ Keine bestehenden Probleme', fg=farbe)

    def draw_guete(self):
        """Seite 2: AP-Health, Umwelt, Trimm als Kästen (letzte Minute, Ø 10 min, Tendenz) aus guete_<Datum>.csv;
        als einziger Verlauf die Gesamtampel der letzten 60 Minuten."""
        c = self.g2; c.delete('all')
        files = sorted(glob.glob(os.path.join(DATA, 'guete_*.csv')))[-2:]
        rows = []
        for p in files:
            rows += list(csv.DictReader(open(p, newline='')))
        rows = rows[-60:]
        if not rows:
            c.create_text(500, 200, text='Noch keine Gütedatei (guete_<Datum>.csv) – läuft pumpwatch.py?', fill=YEL, font=self.mid)
            return
        ende = time.mktime(time.strptime(rows[-1]['zeit'], '%Y-%m-%d %H:%M')) + 60   # Minute endet 60 s nach „zeit“
        if time.time() - ende > GUETE_ALT:                 # nichts Altes als aktuell zeigen
            c.create_text(506, 200, text='Gütedaten veraltet – letzte Minute %s' % rows[-1]['zeit'], fill=DIM, font=self.mid)
            c.create_text(506, 230, text='Auswertung (pumpwatch.py) liefert nichts – „aplog.sh status“ prüfen',
                          fill=DIM, font=self.small)
            return
        AMP = {'gut': GRN, 'akzeptabel': YEL, 'schlecht': RED}
        last10 = rows[-10:]
        def vals(key, rated=False, conv=fl):
            return [conv(r.get(key)) for r in last10 if conv(r.get(key)) is not None and (not rated or r.get('ampel_' + key))]
        def tendenz(v, eps):
            if len(v) < 4:
                return ''
            d = mittel(v[-3:]) - mittel(v)
            return '↗' if d > eps else '↘' if d < -eps else '→'
        def box(x, y, w, h, title, cur, curcol, sub, avg, arrow, big=26):
            c.create_rectangle(x, y, x + w, y + h, outline=GRID, width=2)
            c.create_text(x + 8, y + 6, text=title, fill=DIM, anchor='nw', font=self.mid)
            c.create_text(x + 8, y + 26, text=cur, fill=curcol, anchor='nw', font=('DejaVu Sans', big, 'bold'))
            if sub:
                c.create_text(x + w - 8, y + 34, text=sub, fill=FG, anchor='ne', font=self.mid)
            c.create_text(x + 8, y + h - 6, text='Ø 10 min %s  %s' % (avg, arrow), fill=FG, anchor='sw', font=self.mid)
        def section(y, title):
            c.create_text(6, y, text=title, fill=BLU, anchor='nw', font=('DejaVu Sans', 12, 'bold'))
        # AP-Health: Gütemaß, Farbe nach Ampel; grau = Minute nicht bewertet (Manöver, Autopilot aus)
        section(0, 'AP-Health')
        y, w, h = 22, 246, 104
        for k, (key, title, unit, fmt, eps) in enumerate((('trend', 'Kurs-Trend', '°', '%.1f', 0.3),
                                                           ('wh_h', 'Pumpe Ø', ' W', '%.1f', 1.0),
                                                           ('wechsel', 'Richtungswechsel', '/min', '%.1f', 0.5),
                                                           ('ausreisser', 'Ausreißer > 10°', ' %', '%.0f', 1.0))):
            rated = [x for x in last10 if x.get('ampel_' + key)]   # letzte bewertete Minute, sonst letzte (grau)
            r = rated[-1] if rated else rows[-1]; v = fl(r.get(key))
            cur = '–' if v is None else (fmt % v) + unit
            col = AMP.get(r.get('ampel_' + key), DIM)
            av = vals(key, rated=True)
            avs = '–' if not av else (fmt % mittel(av)) + unit
            box(6 + k * (w + 8), y, w, h, title, cur, col, '', avs, tendenz(av, eps))
        # Gesamtampel: je Minute die schlechteste der vier Farben
        X0, BW, yA = 150, 14, 136
        X = lambda i: X0 + i * BW
        c.create_text(6, yA + 4, text='Gesamtampel 60 min', fill=DIM, anchor='nw', font=self.small)
        rank = {'gut': 1, 'akzeptabel': 2, 'schlecht': 3}
        prev = None
        for i, r in enumerate(rows):
            amps = [r.get('ampel_' + k) for k in ('trend', 'wh_h', 'wechsel', 'ausreisser') if r.get('ampel_' + k)]
            col = AMP[max(amps, key=lambda a: rank[a])] if amps else GRID
            c.create_rectangle(X(i) + 1, yA, X(i) + BW - 1, yA + 22, fill=col, outline='')
            if fl(r.get('ap_anteil')) is not None and fl(r.get('ap_anteil')) < 0.5:
                c.create_text(X(i) + BW / 2, yA + 11, text='aus', fill=FG, font=('DejaVu Sans', 6))
            elif r.get('manoever') == '1':
                c.create_text(X(i) + BW / 2, yA + 11, text='M', fill=FG, font=('DejaVu Sans', 8, 'bold'))
            sv = tuple(r.get(k, '') for k in ('P', 'I', 'D', 'DD', 'PR', 'H', 'gain', 'filter', 'pilot', 'satz'))
            if prev is not None and sv != prev:
                diff = [n for n, a, b in zip(('P', 'I', 'D', 'DD', 'PR', 'H', 'gain', 'Filter', 'Regler', 'Satz'), prev, sv) if a != b]
                c.create_line(X(i), yA - 2, X(i), yA + 30, fill=BLU, width=2)
                c.create_text(X(i) + 2, yA + 24, text=','.join(diff), fill=BLU, anchor='nw', font=self.small)
            prev = sv
            if i % 10 == 0:
                c.create_text(X(i), yA + 24, text=r['zeit'][11:], fill=DIM, anchor='n', font=self.small)
        c.create_text(6, yA + 20, text='M = Manöver', fill=DIM, anchor='nw', font=self.small)
        # Umwelt
        yU = 196
        section(yU, 'Umwelt')
        r = rows[-1]; y, w, h = yU + 22, 194, 100
        def u(key, fmt):
            v = fl(r.get(key)); return '–' if v is None else fmt % v
        def ua(key, fmt):
            v = vals(key); return ('–' if not v else fmt % mittel(v)), v
        ws, wsv = ua('wind', '%.1f kn')
        kw, kwv = ua('kurs_zum_wind', '%.0f°')
        st_, stv = ua('stampfen', '%.2f')
        kr, krv = ua('kraengung', '%.1f°')
        so, sov = ua('sog', '%.1f kn')
        items = (('Wind', u('wind', '%.1f kn'), 'Böen %s' % u('boeen', '%.0f'), ws, tendenz(wsv, 1.0)),
                 ('Kurs zum Wind', u('kurs_zum_wind', '%.0f°'), r.get('kurs_klasse', ''), kw, tendenz(kwv, 5)),
                 ('Seegang', str(r.get('seegang', '–')), 'Stampfen %s' % u('stampfen', '%.2f'), st_, tendenz(stv, 0.1)),
                 ('Krängung', u('kraengung', '%.1f°'), ' '.join(x for x in (u('kraeng_aenderung', '±%.0f°'),
                                                                        r.get('kraeng_ursache', '')) if x != '–'), kr, tendenz(krv, 1.0)),
                 ('Fahrt (SOG)', u('sog', '%.1f kn'), '', so, tendenz(sov, 0.3)))
        for k, (title, cur, sub, av, ar) in enumerate(items):
            box(6 + k * (w + 6), y, w, h, title, cur, FG, sub, av, ar, big=22)
        # Trimm: Ruder-Trimm = Geradeaus-Ruder minus Anzeige-Fehler, je Bug
        yT = 334
        section(yT, 'Trimm')
        y, h = yT + 22, 110
        tr = {'BB': [], 'StB': []}
        for rr in rows:
            g, bg = fl(rr.get('geradeaus_ruder')), rr.get('bug', '')
            if g is not None and bg in tr:
                tr[bg].append(g - RUDER_MITTE)
        for k, (bg, name, col) in enumerate((('BB', 'Ruder-Trimm, Wind von BB', RED), ('StB', 'Ruder-Trimm, Wind von StB', GRN))):
            v = tr[bg][-10:]
            cur = '–' if not v else '%+.1f°' % v[-1]
            avs = '–' if not v else '%+.1f° (%d min)' % (mittel(v), len(v))
            box(6 + k * 340, y, 330, h, name, cur, FG if v else DIM, '', avs, tendenz(v, 0.5))
            c.create_rectangle(6 + k * 340 + 2, y + 2, 6 + k * 340 + 7, y + h - 2, fill=col, outline='')   # Seitenfarbe
        # Letzte Wertänderung
        x = 6 + 2 * 340
        c.create_rectangle(x, y, 1006, y + h, outline=GRID, width=2)
        c.create_text(x + 8, y + 6, text='Reglerwerte', fill=DIM, anchor='nw', font=self.mid)
        ch, prev = None, None
        for rr in rows:
            sv = tuple(rr.get(k, '') for k in ('P', 'I', 'D', 'DD', 'PR', 'H', 'gain', 'filter', 'pilot', 'satz'))
            if prev is not None and sv != prev:
                ch = (rr['zeit'][11:], [n for n, a, b in zip(('P', 'I', 'D', 'DD', 'PR', 'H', 'gain', 'Filter', 'Regler', 'Satz'), prev, sv) if a != b])
            prev = sv
        txt = 'zuletzt geändert %s: %s' % (ch[0], ', '.join(ch[1])) if ch else 'unverändert seit %s' % rows[0]['zeit'][11:]
        c.create_text(x + 8, y + 34, text=txt, fill=FG, anchor='nw', font=self.mid, width=300)
        c.create_text(x + 8, y + h - 6, text='Trimm = Anzeige − %.1f° (Anzeige bei Ruder mittig)' % RUDER_MITTE,
                      fill=DIM, anchor='sw', font=self.small)

    def footer(self, s):
        keys = [('P', 'ap.pilot.basic.P'), ('I', 'ap.pilot.basic.I'), ('D', 'ap.pilot.basic.D'), ('DD', 'ap.pilot.basic.DD'),
                ('PR', 'ap.pilot.basic.PR'), ('H', 'ap.pilot.basic.H'), ('gain', 'servo.gain'),
                ('Filter', 'imu.headingrate_lowpass_constant'), ('Störungen', 'servo.faults')]
        st = '   '.join('%s %s' % (k, s[n]) for k, n in keys if n in s)
        self.foot.config(text='Reglerwerte: ' + st + '      Datei: ' + os.path.basename(self.src.path or '–'))

if __name__ == '__main__':
    import sys
    root = tk.Tk()
    app = Leitstand(root)
    if len(sys.argv) > 1 and sys.argv[1] == '2':     # direkt mit Seite „Güte“ starten
        app.show('guete')
    root.mainloop()
