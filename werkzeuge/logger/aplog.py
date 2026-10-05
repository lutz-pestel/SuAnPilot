#!/usr/bin/env python3
# Records autopilot data from the TinyPilot pypilot server (port 23322) to CSV files.
# signals_*.csv: one row per sample period (latest value of every signal)
# events_*.csv:  settings, written whenever one of them changes
import csv, json, os, socket, sys, time

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
           'ap.pilot.suan.soll', 'ap.pilot.suan.est', 'ap.pilot.suan.trim', 'ap.pilot.suan.k',
           'ap.pilot.suan.fehler', 'ap.pilot.suan.status', 'ap.pilot.suan.v_up', 'ap.pilot.suan.v_down']
SETTINGS = ['ap.pilot', 'ap.pilot.basic.P', 'ap.pilot.basic.I', 'ap.pilot.basic.D',
            'ap.pilot.basic.DD', 'ap.pilot.basic.PR', 'ap.pilot.basic.FF', 'ap.pilot.basic.R',
            'servo.period', 'servo.gain', 'servo.speed.min', 'servo.speed.max',
            'servo.max_current', 'servo.faults', 'servo.hardover_time', 'imu.heading_offset',
            'rudder.offset', 'rudder.scale', 'rudder.range',
            'servo.controller', 'nmea.client', 'ap.pilot.basic.H', 'imu.heading_lowpass_constant',
            'imu.headingrate_lowpass_constant', 'imu.headingraterate_lowpass_constant',
            'ap.pilot.suan.k_ref', 'ap.pilot.suan.Tg', 'ap.pilot.suan.v_ref', 'ap.pilot.suan.n_v',
            'ap.pilot.suan.v_min', 'ap.pilot.suan.fk_min', 'ap.pilot.suan.fk_max', 'ap.pilot.suan.K_ref',
            'ap.pilot.suan.T_I', 'ap.pilot.suan.T_S', 'ap.pilot.suan.r_max_stb', 'ap.pilot.suan.r_max_bb',
            'ap.pilot.suan.T_ramp', 'ap.pilot.suan.rate_up', 'ap.pilot.suan.rate_down', 'ap.pilot.suan.delay',
            'ap.pilot.suan.db', 'ap.pilot.suan.T_corr', 'ap.pilot.suan.hub', 'ap.pilot.suan.e_freeze',
            'ap.pilot.suan.t_blind', 'ap.pilot.suan.jump_lim', 'ap.pilot.suan.t_bad', 'ap.pilot.suan.speed',
            'ap.pilot.suan.sparsam', 'ap.pilot.suan.db_sparsam', 'ap.pilot.suan.TS_sparsam',
            'ap.pilot.suan.T_D', 'ap.pilot.suan.T_acc', 'ap.pilot.suan.t_rev',
            'ap.pilot.suan.lern', 'ap.pilot.suan.schwach', 'ap.pilot.suan.n_tot']

def tinypilot_address():
    try:
        for line in open('/var/lib/misc/dnsmasq.leases'):
            f = line.split()
            if len(f) > 3 and f[3] == 'box':
                return f[2]
    except OSError:
        pass
    return '10.10.10.163'

def record(sig_writer, ev_writer, files):
    host = tinypilot_address()
    s = socket.create_connection((host, 23322), timeout=5)
    watch = {n: PERIOD for n in SIGNALS}
    watch.update({n: 1 for n in SETTINGS})
    s.sendall(('watch=' + json.dumps(watch) + '\n').encode())
    s.settimeout(0.05)
    print(time.strftime('%H:%M:%S'), 'verbunden mit', host, flush=True)
    latest, settings, buf = {}, {}, b''
    next_row = time.time()
    while True:
        try:
            data = s.recv(65536)
            if not data:
                raise OSError('Verbindung geschlossen')
            buf += data
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
        if now >= next_row:
            sig_writer.writerow(['%.2f' % now] + [latest.get(n, '') for n in SIGNALS])
            next_row = max(next_row + PERIOD, now)
            files[0].flush()

def main():
    os.makedirs(DATA, exist_ok=True)
    stamp = time.strftime('%Y-%m-%d_%H%M%S')
    sig_f = open(os.path.join(DATA, 'signals_%s.csv' % stamp), 'w', newline='')
    ev_f = open(os.path.join(DATA, 'events_%s.csv' % stamp), 'w', newline='')
    sig_w, ev_w = csv.writer(sig_f), csv.writer(ev_f)
    sig_w.writerow(['time'] + SIGNALS)
    ev_w.writerow(['time', 'name', 'value'])
    while True:
        try:
            record(sig_w, ev_w, (sig_f, ev_f))
        except OSError as e:
            print(time.strftime('%H:%M:%S'), 'keine Verbindung:', e, flush=True)
            time.sleep(5)

if __name__ == '__main__':
    main()
