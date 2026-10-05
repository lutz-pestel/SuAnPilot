#!/usr/bin/env python3
# Pumpen-Diagnose (PyPilot-AI, 03.10.2026). NUR IM HAFEN: Autopilot aus, Ruder frei, niemand am Steuerrad.
# Faehrt die Autopilot-Pumpe ueber den TinyPilot (servo.command) nach festem Plan, misst je Lauf Strom, Spannung,
# Rudergeschwindigkeit (Anzeige um DELAY versetzt), Temperatur, Fehlermeldungen und fragt Beobachtungen ab
# (Geraeusch, Klopftest, Multimeter an den Motorklemmen). Ergebnis: Rohdaten-CSV, Lauf-Tabelle, Befund.
#   python diagnose.py                 -> alle Pruefungen nacheinander (jeweils mit Rueckfrage)
#   python diagnose.py A C             -> nur Pruefungen A und C
#   python diagnose.py --host 127.0.0.1 ...   (Test gegen diag_mock.py)
# Abbruch jederzeit mit Strg+C: die Pumpe wird sofort angehalten.
import csv, json, os, socket, statistics as st, sys, threading, time

DELAY = 1.0          # s, Verzoegerung der Ruderanzeige (gemessen 29.09.)
GRENZE = 25.0        # Grad, das Ruder wird nie weiter gefahren
I_TOT = 2.5          # A, Laeufe darunter gelten als 'Pumpe steht?' (wie Selbsthilfe/pumpwatch)
KEYS = ['servo.command', 'servo.speed', 'servo.raw_command', 'servo.current', 'servo.voltage', 'servo.controller_temp',
        'servo.flags', 'servo.state', 'rudder.angle', 'ap.enabled', 'servo.max_slew_speed', 'servo.max_slew_slow']

def finde_tinypilot():
    import subprocess
    try:
        out = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', 'pi@10.10.10.1',
                              'cat /var/lib/misc/dnsmasq.leases'], capture_output=True, text=True, timeout=15).stdout
        for line in out.splitlines():
            f = line.split()
            if len(f) > 3 and f[3] == 'box':
                return f[2]
    except Exception:
        pass
    return '10.10.10.164'

class Pumpe(object):
    """Verbindung zum TinyPilot: liest laufend mit und haelt den Pumpenbefehl am Leben (laeuft sonst nach 1 s aus)."""
    def __init__(self, host, roh):
        self.s = socket.create_connection((host, 23322), timeout=5)
        self.s.sendall(('watch={' + ','.join('"%s":0.05' % k for k in KEYS) + '}\n').encode())
        self.v, self.cmd, self.lock, self.aus = {}, 0.0, threading.Lock(), False
        self.roh = csv.writer(roh); self.roh.writerow(['t', 'cmd'] + KEYS); self.rohf = roh
        self.hist = []                                   # (t, Ruderanzeige, Strom, Spannung)
        threading.Thread(target=self._lesen, daemon=True).start()
        threading.Thread(target=self._halten, daemon=True).start()
        time.sleep(1.0)

    def _lesen(self):
        buf = ''
        self.s.settimeout(0.2)
        while not self.aus:
            try:
                buf += self.s.recv(65536).decode(errors='replace')
            except socket.timeout:
                continue
            except OSError:
                break
            zeilen = buf.split('\n'); buf = zeilen.pop()
            for z in zeilen:
                if '=' in z:
                    k, x = z.split('=', 1)
                    try: self.v[k] = json.loads(x)
                    except ValueError: self.v[k] = x
            t = time.time()
            r, i, u = self.v.get('rudder.angle'), self.v.get('servo.current'), self.v.get('servo.voltage')
            if isinstance(r, (int, float)):
                self.hist.append((t, r, i if isinstance(i, (int, float)) else 0.0, u if isinstance(u, (int, float)) else 0.0))
                self.hist = self.hist[-4000:]
            self.roh.writerow(['%.3f' % t, self.cmd] + [self.v.get(k, '') for k in KEYS])

    def _halten(self):
        while not self.aus:
            with self.lock:
                c = self.cmd
            try:
                self.s.sendall(('servo.command=%s\n' % c).encode())
            except OSError:
                break
            time.sleep(0.15)

    def befehl(self, c):
        with self.lock:
            self.cmd = float(c)
        self.s.sendall(('servo.command=%s\n' % c).encode())

    def stop(self):
        for _ in range(5):
            try:
                self.befehl(0)
            except OSError:
                pass
            time.sleep(0.05)

    def ruder(self):
        return self.v.get('rudder.angle')

    def anz_mittel(self, t0, t1):
        x = [r for t, r, i, u in self.hist if t0 <= t <= t1]
        return st.mean(x) if x else None

    def fenster(self, t0, t1):
        return [(t, r, i, u) for t, r, i, u in self.hist if t0 <= t <= t1]

def warte(sek):
    time.sleep(sek)

def lauf(p, richtung, dauer, laeufe, name, nachlauf=DELAY + 1.5):
    """Ein Pumpenlauf mit Schutz: stoppt, sobald die Anzeige (+ Weg waehrend der Verzoegerung) die Grenze erreicht."""
    r0 = p.ruder()
    if not isinstance(r0, (int, float)):
        print('  keine Ruderanzeige – Lauf ausgelassen'); return None
    t0 = time.time(); p.befehl(richtung)
    while time.time() - t0 < dauer:
        r = p.ruder()
        if isinstance(r, (int, float)) and r * richtung > GRENZE - 6.0 * DELAY:   # 6 Grad/s Reserve fuer 1 s Verzoegerung
            break
        time.sleep(0.02)
    t1 = time.time(); p.befehl(0)
    warte(nachlauf)
    a0, a1 = p.anz_mittel(t0 + DELAY - 0.2, t0 + DELAY + 0.1), p.anz_mittel(t1 + DELAY + 0.2, t1 + DELAY + 0.5)
    w = p.fenster(t0 + 0.25, t1)                        # Strom/Spannung waehrend des Laufs, ohne Einschaltspitze
    ws = p.fenster(t0, t1 + 0.2)
    erg = dict(name=name, richtung='vorw' if richtung > 0 else 'rueckw', soll_s=round(dauer, 2), ist_s=round(t1 - t0, 2),
               ruder_start=round(a0, 1) if a0 is not None else '', ruderweg=round(a1 - a0, 1) if a0 is not None and a1 is not None else '',
               i_mittel=round(st.mean(x[2] for x in w), 2) if w else '', i_max=round(max(x[2] for x in ws), 2) if ws else '',
               u_min=round(min(x[3] for x in ws if x[3] > 0), 2) if [x for x in ws if x[3] > 0] else '',
               temp=p.v.get('servo.controller_temp', ''), flags=p.v.get('servo.flags', ''))
    if erg['ruderweg'] != '' and t1 - t0 > 0.15:
        erg['grad_s'] = round(erg['ruderweg'] * richtung / (t1 - t0), 2)
    else:
        erg['grad_s'] = ''
    erg['befund'] = 'Pumpe steht?' if (erg['i_mittel'] != '' and erg['i_mittel'] < I_TOT and t1 - t0 >= 0.8) else ''
    laeufe.append(erg)
    print('  %-14s %-6s %4.1fs  Weg %6s  %6s Grad/s  I %5s/%5s A  U %5s V  %s' % (
        name, erg['richtung'], t1 - t0, erg['ruderweg'], erg['grad_s'], erg['i_mittel'], erg['i_max'], erg['u_min'], erg['befund']))
    return erg

def fahre_auf(p, ziel, laeufe):
    """Ruder mit kurzen Stoessen auf etwa ziel bringen (Anzeige verzoegert -> Stoss, warten, nachsehen)."""
    for _ in range(25):
        r = p.ruder()
        if not isinstance(r, (int, float)): return
        d = ziel - r
        if abs(d) < 2.5: return
        richtung = 1 if d > 0 else -1
        lauf(p, richtung, min(1.5, abs(d) / 6.0), [], 'positionieren', nachlauf=DELAY + 0.4)

AUTO = False      # --auto: keine Rueckfragen (Bedingungen im Gespraech bestaetigt), Beobachtungen bleiben leer

def frage(text, erlaubt=None):
    if AUTO:
        a = 'ja' if erlaubt and 'ja' in erlaubt else 'j' if erlaubt and 'j' in erlaubt else 'x' if erlaubt and 'x' in erlaubt else ''
        print('  > %s %s (automatisch)' % (text, a)); return a
    while True:
        a = input('  > %s ' % text).strip().lower()
        if not erlaubt or a in erlaubt: return a

def beobachtung(laeufe, text='Geraeusch? h=hell surrend, d=dunkel brummend, n=nichts gehoert, x=uebergehen'):
    if laeufe:
        laeufe[-1]['geraeusch'] = frage(text, ('h', 'd', 'n', 'x', ''))

def pruefung_A(p, laeufe):
    print('A  Stoesse je Richtung: 0,2 / 0,4 / 0,8 / 1,6 / 3 s, je 3 mal')
    for richtung in (1, -1):
        for dauer in (0.2, 0.4, 0.8, 1.6, 3.0):
            for n in range(3):
                fahre_auf(p, -15.0 * richtung, laeufe)
                lauf(p, richtung, dauer, laeufe, 'A %.1fs' % dauer)
                if dauer >= 1.6: beobachtung(laeufe)

def pruefung_B(p, laeufe):
    print('B  Lange Laeufe von Seite zu Seite (bis +-%d Grad), je 3 mal' % GRENZE)
    for n in range(3):
        fahre_auf(p, -18.0, laeufe)
        lauf(p, 1, 12.0, laeufe, 'B lang'); beobachtung(laeufe)
        lauf(p, -1, 12.0, laeufe, 'B lang'); beobachtung(laeufe)

def pruefung_C(p, laeufe):
    print('C  Richtungsumkehr nach 0 / 0,3 / 1 / 3 s Pause, je Richtung')
    for erste in (1, -1):
        for pause in (0.0, 0.3, 1.0, 3.0):
            fahre_auf(p, -8.0 * erste, laeufe)
            lauf(p, erste, 1.0, laeufe, 'C hin', nachlauf=pause)
            lauf(p, -erste, 1.0, laeufe, 'C Umkehr %.1fs' % pause)   # Weg von 'C hin' bei Pause < 1 s nicht messbar

def pruefung_D(p, laeufe):
    print('D  Dauerbelastung 2 min: abwechselnd 2-s-Laeufe zwischen +-15 Grad')
    t_ende = time.time() + 120
    richtung = 1
    while time.time() < t_ende:
        lauf(p, richtung, 2.0, laeufe, 'D dauer', nachlauf=0.5)
        r = p.ruder()
        if isinstance(r, (int, float)) and r * richtung > 12: richtung = -richtung
    print('  Controller-Temperatur jetzt: %s' % p.v.get('servo.controller_temp'))

def pruefung_E(p, laeufe):
    print('E  Messung mit Multimeter an den Motorklemmen (Gleichspannung, Messbereich 20 V)')
    for richtung in (-1, 1):
        fahre_auf(p, -18.0 * richtung, laeufe)
        frage('Multimeter angeschlossen? Enter = Lauf starten (%s, bis 8 s)' % ('rueckw' if richtung < 0 else 'vorw'))
        print('  JETZT ABLESEN (Spannung am Motor waehrend des Laufs)')
        erg = lauf(p, richtung, 8.0, laeufe, 'E Messung')
        if erg is not None:
            erg['u_motor'] = frage('abgelesene Motorspannung in V (leer = keine):')
            erg['klopf'] = frage('Klopftest gemacht? j=lief danach an, n=keine Wirkung, x=nicht gemacht', ('j', 'n', 'x', ''))
            beobachtung(laeufe)

PRUEFUNGEN = {'A': pruefung_A, 'B': pruefung_B, 'C': pruefung_C, 'D': pruefung_D, 'E': pruefung_E}

def befund(laeufe, pfad):
    zeilen = ['# Pumpen-Diagnose %s' % time.strftime('%d.%m.%Y %H:%M'), '',
              '| Richtung | Laeufe >= 0,8 s | Grad/s Median | Strom Median | davon "Pumpe steht?" | dunkel gehoert |',
              '|---|---|---|---|---|---|']
    for r in ('vorw', 'rueckw'):
        L = [x for x in laeufe if x['richtung'] == r and x['ist_s'] >= 0.8 and x['grad_s'] != '']
        if not L: continue
        zeilen.append('| %s | %d | %.1f | %.1f A | %d | %d |' % (r, len(L), st.median(x['grad_s'] for x in L),
                      st.median(x['i_mittel'] for x in L if x['i_mittel'] != ''), sum(1 for x in L if x['befund']),
                      sum(1 for x in L if x.get('geraeusch') == 'd')))
    um = [x for x in laeufe if x.get('u_motor')]
    if um:
        zeilen += ['', 'Motorspannung (Multimeter):']
        for x in um:
            zeilen.append('- %s: Motor %s V, Bord min %s V, Strom %s A, %s Grad/s, Klopftest %s' % (
                x['richtung'], x['u_motor'], x['u_min'], x['i_mittel'], x['grad_s'], x.get('klopf', '')))
        zeilen.append('Deutung: Motorspannung nahe Bordspannung bei Stoerung -> Motor/Kohlen/Pumpe/Ventil; '
                      'deutlich darunter -> Controller/Kabel/Kontakte.')
    zeilen.append('Deutung Klopftest: laeuft nach Klopfen an -> Kohlen/Kollektor wahrscheinlich.')
    open(pfad, 'w', encoding='utf-8').write('\n'.join(zeilen) + '\n')
    print('\n'.join(zeilen))

def main():
    global AUTO
    args = sys.argv[1:]
    if '--auto' in args:
        AUTO = True; args.remove('--auto')
    host = None
    if '--host' in args:
        i = args.index('--host'); host = args[i + 1]; del args[i:i + 2]
    wahl = [a.upper() for a in args] or list('ABCDE')
    host = host or finde_tinypilot()
    ordner = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Daten', 'diagnose')
    os.makedirs(ordner, exist_ok=True)
    stamm = os.path.join(os.path.abspath(ordner), 'diagnose_%s' % time.strftime('%Y-%m-%d_%H%M%S'))
    print('Pumpen-Diagnose, TinyPilot %s. NUR IM HAFEN, Ruder frei, niemand am Rad.' % host)
    if frage('Bedingungen erfuellt? (ja/nein)', ('ja', 'nein')) != 'ja':
        return
    roh = open(stamm + '_roh.csv', 'w', newline='')
    p = Pumpe(host, roh)
    laeufe = []
    try:
        for _ in range(30):                              # Werte muessen ankommen, sonst nicht fahren
            if isinstance(p.ruder(), (int, float)): break
            time.sleep(0.2)
        else:
            print('Keine Werte vom TinyPilot – Abbruch.'); return
        if p.v.get('ap.enabled') is True:
            print('Autopilot ist eingeschaltet – bitte ausschalten. Abbruch.'); return
        print('Ruder jetzt %s Grad, Anlauf-Rampe max_slew_speed %s / slow %s' % (
            p.ruder(), p.v.get('servo.max_slew_speed'), p.v.get('servo.max_slew_slow')))
        for k in wahl:
            if k in PRUEFUNGEN and frage('Pruefung %s starten? (j/n)' % k, ('j', 'n')) == 'j':
                PRUEFUNGEN[k](p, laeufe)
    except KeyboardInterrupt:
        print('\nABBRUCH – Pumpe angehalten')
    finally:
        p.stop(); p.aus = True
        if laeufe:
            w = csv.DictWriter(open(stamm + '_laeufe.csv', 'w', newline=''), sorted({k for x in laeufe for k in x}))
            w.writeheader(); w.writerows(laeufe)
            befund(laeufe, stamm + '_befund.md')
        roh.close()
        print('Dateien: %s_*.csv/.md' % stamm)

if __name__ == '__main__':
    main()
