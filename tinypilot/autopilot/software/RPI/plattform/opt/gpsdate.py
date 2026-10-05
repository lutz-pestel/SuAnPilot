#!/usr/local/bin/python3.6
# Sets the system clock from the GPS of the master (NMEA RMC over TCP).
# Replaces the original script, which needed the python gps module that is not installed.
import os, socket, time

SOURCE = ('10.10.10.1', 10110)

def checksum_ok(line):
    if not line.startswith('$') or '*' not in line:
        return False
    data, cs = line[1:].split('*', 1)
    crc = 0
    for c in data:
        crc ^= ord(c)
    return cs[:2].upper() == '%02X' % crc

def read_time():
    s = socket.create_connection(SOURCE, timeout=10)
    try:
        buf = b''
        end = time.monotonic() + 30
        while time.monotonic() < end:
            data = s.recv(1024)
            if not data:
                return None
            buf += data
            while b'\n' in buf:
                raw, buf = buf.split(b'\n', 1)
                line = raw.decode(errors='replace').strip()
                if not checksum_ok(line):
                    continue
                f = line.split('*')[0].split(',')
                if len(f) > 9 and f[0][3:6] == 'RMC' and f[2] == 'A' \
                   and len(f[1]) >= 6 and len(f[9]) == 6:
                    t, d = f[1], f[9]
                    return '20%s-%s-%s %s:%s:%s' % (d[4:6], d[2:4], d[0:2],
                                                    t[0:2], t[2:4], t[4:6])
    finally:
        s.close()
    return None

while True:
    try:
        utc = read_time()
    except OSError:
        utc = None
    if utc:
        print('Setting date to gps time', utc, flush=True)
        os.system('date -u -s "%s"' % utc)
        time.sleep(3*24*60*60) # sync again in 3 days
    else:
        time.sleep(10)
