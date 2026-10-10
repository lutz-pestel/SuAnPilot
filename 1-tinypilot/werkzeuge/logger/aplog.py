#!/usr/bin/env python3
# Records autopilot data from the TinyPilot pypilot server (port 23322) to CSV files.
# signals_*.csv: one row per sample period (latest value of every signal)
# events_*.csv:  settings, written whenever one of them changes
import csv, json, os, socket, sys, time

VERSION = '00.02'      # Version der Aufzeichnung (Format NN.NN, jede Aenderung zaehlt hoch)
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PERIOD = float(os.environ.get('APLOG_PERIOD', '0.2'))

SIGNALS = ['ap.enabled', 'ap.mode', 'ap.heading', 'ap.heading_command', 'ap.heading_error',
           'ap.heading_error_int', 'imu.heading', 'imu.headingrate_lowpass',
           'imu.headingraterate_lowpass', 'imu.roll', 'imu.pitch', 'imu.heel',
           'rudder.angle', 'servo.command', 'servo.speed', 'servo.raw_command', 'servo.current',
           'servo.voltage', 'servo.state', 'servo.flags', 'servo.duty',
           'gps.speed', 'gps.track', 'wind.direction', 'wind.speed',
           'ap.pilot.basic.Pgain', 'ap.pilot.basic.Igain', 'ap.pilot.basic.Dgain',
           'ap.pilot.basic.DDgain', 'ap.pilot.basic.PRgain', 'ap.pilot.basic.FFgain',
           'ap.pilot.basic.Hgain', 'ap.pilot.basic.heelrate', 'servo.controller_temp', 'servo.recovery',
           'ap.pilot.adaptive.soll', 'ap.pilot.adaptive.est', 'ap.pilot.adaptive.trim', 'ap.pilot.adaptive.k',
           'ap.pilot.adaptive.fehler', 'ap.pilot.adaptive.status', 'ap.pilot.adaptive.v_up', 'ap.pilot.adaptive.v_down',
           'ap.offcourse']
SETTINGS = ['ap.pilot', 'ap.pilot.basic.P', 'ap.pilot.basic.I', 'ap.pilot.basic.D',
            'ap.pilot.basic.DD', 'ap.pilot.basic.PR', 'ap.pilot.basic.FF', 'ap.pilot.basic.R',
            'servo.period', 'servo.gain', 'servo.speed.min', 'servo.speed.max',
            'servo.max_current', 'servo.faults', 'servo.hardover_time', 'imu.heading_offset',
            'rudder.offset', 'rudder.scale', 'rudder.range',
            'servo.controller', 'nmea.client', 'ap.pilot.basic.H', 'imu.heading_lowpass_constant',
            'imu.headingrate_lowpass_constant', 'imu.headingraterate_lowpass_constant',
            'ap.pilot.adaptive.k_ref', 'ap.pilot.adaptive.Tg', 'ap.pilot.adaptive.v_ref', 'ap.pilot.adaptive.n_v',
            'ap.pilot.adaptive.v_min', 'ap.pilot.adaptive.fk_min', 'ap.pilot.adaptive.fk_max', 'ap.pilot.adaptive.K_ref',
            'ap.pilot.adaptive.T_I', 'ap.pilot.adaptive.T_S', 'ap.pilot.adaptive.r_max_stb', 'ap.pilot.adaptive.r_max_bb',
            'ap.pilot.adaptive.T_ramp', 'ap.pilot.adaptive.rate_up', 'ap.pilot.adaptive.rate_down', 'ap.pilot.adaptive.delay',
            'ap.pilot.adaptive.db', 'ap.pilot.adaptive.T_corr', 'ap.pilot.adaptive.hub', 'ap.pilot.adaptive.e_freeze',
            'ap.pilot.adaptive.t_blind', 'ap.pilot.adaptive.jump_lim', 'ap.pilot.adaptive.t_bad', 'ap.pilot.adaptive.speed',
            'ap.pilot.adaptive.sparsam', 'ap.pilot.adaptive.db_sparsam', 'ap.pilot.adaptive.TS_sparsam',
            'ap.pilot.adaptive.T_D', 'ap.pilot.adaptive.T_acc', 'ap.pilot.adaptive.t_rev',
            'ap.pilot.adaptive.lern', 'ap.pilot.adaptive.schwach', 'ap.pilot.adaptive.n_tot']

STALE = 6.0            # s ohne jede Zeile vom TinyPilot: Verbindung gilt als tot, neu verbinden
STATUS = os.path.join(DATA, 'verbindung.json')

def tinypilot_addresses():
    """Adressen, die der Reihe nach probiert werden: Lease am Master, feste Adresse, Name."""
    out = []
    try:
        for line in open('/var/lib/misc/dnsmasq.leases'):
            f = line.split()
            if len(f) > 3 and f[3] == 'box':
                out.append(f[2])
    except OSError:
        pass
    out.append('10.10.10.164')
    out.append('box')
    return list(dict.fromkeys(out))

def status_schreiben(zustand, host='', letzte_daten=0.0, ursache=''):
    """Zustand fuer den Leitstand (atomar ersetzen, damit er nie eine halbe Datei liest)."""
    try:
        tmp = STATUS + '.tmp'
        with open(tmp, 'w') as f:
            json.dump({'zeit': time.time(), 'zustand': zustand, 'host': host,
                       'letzte_daten': letzte_daten, 'ursache': ursache}, f)
        os.replace(tmp, STATUS)
    except OSError:
        pass

def verbinden():
    """Erste erreichbare Adresse; wirft OSError mit allen Einzelfehlern, wenn keine antwortet."""
    fehler = []
    for host in tinypilot_addresses():
        try:
            s = socket.create_connection((host, 23322), timeout=4)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            return s, host
        except OSError as e:
            fehler.append('%s: %s' % (host, e))
    raise OSError('; '.join(fehler))

def record(sig_writer, ev_writer, files):
    s, host = verbinden()
    watch = {n: PERIOD for n in SIGNALS}
    watch.update({n: 1 for n in SETTINGS})
    s.sendall(('watch=' + json.dumps(watch) + '\n').encode())
    s.settimeout(0.05)
    print(time.strftime('%H:%M:%S'), 'verbunden mit', host, flush=True)
    latest, settings, buf = {}, {}, b''
    next_row = last_rx = last_status = time.time()
    try:
        while True:
            try:
                data = s.recv(65536)
                if not data:
                    raise OSError('Verbindung vom TinyPilot geschlossen')
                buf += data
                last_rx = time.time()
            except socket.timeout:
                pass
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                text = line.decode(errors='replace')
                if '=' not in text:
                    continue
                name, value = text.split('=', 1)
                try:
                    value = json.loads(value)
                except ValueError:
                    pass
                if name in SETTINGS and settings.get(name) != value:
                    settings[name] = value
                    ev_writer.writerow([time.strftime('%Y-%m-%dT%H:%M:%S'), name, value])
                    files[1].flush()
                latest[name] = value
            now = time.time()
            if now - last_rx > STALE:
                raise OSError('seit %.0f s keine Daten vom TinyPilot (Verbindung steht, pypilot sendet nicht)' % (now - last_rx))
            if now >= next_row:
                sig_writer.writerow(['%.2f' % now] + [latest.get(n, '') for n in SIGNALS])
                next_row = max(next_row + PERIOD, now)
                files[0].flush()
            if now - last_status >= 1:
                status_schreiben('verbunden', host, last_rx)
                last_status = now
    finally:
        s.close()

def main():
    os.makedirs(DATA, exist_ok=True)
    stamp = time.strftime('%Y-%m-%d_%H%M%S')
    sig_f = open(os.path.join(DATA, 'signals_%s.csv' % stamp), 'w', newline='')
    ev_f = open(os.path.join(DATA, 'events_%s.csv' % stamp), 'w', newline='')
    sig_w, ev_w = csv.writer(sig_f), csv.writer(ev_f)
    sig_w.writerow(['time'] + SIGNALS)
    ev_w.writerow(['time', 'name', 'value'])
    print(time.strftime('%H:%M:%S'), 'aplog Version', VERSION, flush=True)
    pause = 2.0
    while True:                                   # gibt nie auf: jeder Fehler fuehrt zu neuem Versuch
        start = time.time()
        try:
            record(sig_w, ev_w, (sig_f, ev_f))
        except Exception as e:
            print(time.strftime('%H:%M:%S'), 'keine Verbindung:', e, flush=True)
            letzte = time.time()
            pause = 2.0 if letzte - start > 30 else min(pause * 1.5, 10.0)   # hielt sie lange, sofort wieder schnell
            ende = time.time() + pause
            while time.time() < ende:             # Pause, dabei weiter melden (der Leitstand prueft das Alter)
                status_schreiben('getrennt', '', 0.0, str(e))
                time.sleep(1)

if __name__ == '__main__':
    main()
