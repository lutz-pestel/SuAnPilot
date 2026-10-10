#!/usr/bin/env python3
# Displaytest (Version 00.01, 10.10.2026): Steuerseite von hat/page.py am PC auf nachgebildetem Display
# (JLX12864 hochkant, 64 x 128 Punkte). Schrift nur als Rahmen (am PC keine Schriftbibliothek): geprueft werden
# Lage der Texte, Regleranzeige links unten (gross), WIFI rechts unten (klein), Alarmzeile invertiert. Bilder: displaytest_<fall>.png (4-fach).
# Aufruf: python displaytest.py [Ausgabeordner]
import sys, os, types, struct, zlib

HAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'autopilot', 'software', 'RPI', 'plattform',
                   'paket', 'usr', 'local', 'lib', 'python3.6', 'site-packages', 'pypilot', 'hat')
W, H = 64, 128
texte = []

class Flaeche(object):
    def __init__(self): self.width, self.height, self.bypp, self.p = W, H, 1, [[0] * W for y in range(H)]
    def fill(self, c): self.p = [[1 if c else 0] * W for y in range(H)]
    def box(self, x1, y1, x2, y2, c):
        for y in range(max(0, y1), min(H, y2 + 1)):
            for x in range(max(0, x1), min(W, x2 + 1)): self.p[y][x] = 1 if c else 0
    def invert(self, x1, y1, x2, y2):
        for y in range(max(0, y1), min(H, y2 + 1)):
            for x in range(max(0, x1), min(W, x2 + 1)): self.p[y][x] = 1 - (self.p[y][x] & 1) if self.p[y][x] < 2 else 5 - self.p[y][x]
    def png(self, name, s=4):
        farbe = {0: (0, 0, 0), 1: (255, 255, 255), 2: (90, 200, 90), 3: (40, 110, 40)}   # 2/3 = Text auf schwarz/weiss
        roh = b''
        for y in range(H * s):
            roh += b'\0' + b''.join(bytes(farbe[self.p[y // s][x // s]]) for x in range(W * s))
        def block(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        open(name, 'wb').write(b'\x89PNG\r\n\x1a\n' + block(b'IHDR', struct.pack('>IIBBBBB', W * s, H * s, 8, 2, 0, 0, 0))
                               + block(b'IDAT', zlib.compress(roh)) + block(b'IEND', b''))

def zeichne(surface, pos, text, size, bw, crop=False):          # Ersatz fuer font.draw: Text als Flaeche
    w, h = max(1, int(len(text) * size * 0.6)), max(1, int(size))
    if '\n' in text:
        z = text.split('\n'); w, h = int(max(len(l) for l in z) * size * 0.6), int(size * len(z))
    if pos:
        x0, y0 = pos
        texte.append((text, x0, y0, x0 + w - 1, y0 + h - 1))
        for y in range(max(0, y0), min(H, y0 + h)):
            for x in range(max(0, x0), min(W, x0 + w)):
                surface.p[y][x] = 2 if surface.p[y][x] == 0 else 3
    return w, h

font = types.ModuleType('font'); font.draw = zeichne; sys.modules['font'] = font
sys.path.insert(0, HAT)
import page
page.test_wifi = lambda: True                  # am PC kein WLAN-Status: WIFI immer zeigen

class Lcd(object):
    def __init__(self, werte):
        self.surface, self.bw, self.battery_voltage, self.hat = Flaeche(), 1, False, None
        self.last_msg, self.config = werte, {'smallstep': 1, 'bigstep': 10}
        self.client = types.SimpleNamespace(connection=True, reset_timeout=lambda: None)
    def receive(self): pass

GRUND = {'ap.mode': 'compass', 'ap.heading': 123.0, 'ap.heading_command': 125.0, 'ap.enabled': True,
         'servo.flags': '', 'servo.controller': 'arduino', 'imu.frequency': 20, 'gps.source': 'gpsd',
         'wind.source': 'none', 'imu.compass.calibration': [[0, 0, 0, 0], [1.0, 0]]}
faelle = [('adaptive', {'ap.pilot': 'adaptive', 'ap.pilot.adaptive.status': 'ok'}, 'ADAPTIV', False),
          ('basic_gewaehlt', {'ap.pilot': 'basic', 'ap.pilot.adaptive.status': 'aus'}, 'BASIC', False),
          ('rueckfall', {'ap.pilot': 'basic', 'ap.pilot.adaptive.status': 'Rueckfall: Ruder folgt nicht (rueckw)'}, 'BASIC', True),
          ('offcourse', {'ap.pilot': 'basic', 'ap.pilot.adaptive.status': 'Rueckfall: Ruder folgt nicht (rueckw)',
                         'ap.offcourse': True}, 'BASIC', True),
          ('rueckfall_standby', {'ap.pilot': 'basic', 'ap.pilot.adaptive.status': 'Rueckfall: Ruderanzeige fehlt',
                                 'ap.enabled': False}, 'BASIC', True)]
ordner = sys.argv[1] if len(sys.argv) > 1 else '.'
ok = True
for name, werte, regler, alarm in faelle:
    texte.clear()
    lcd = Lcd(dict(GRUND, **werte))
    seite = page.control(lcd); seite.lcd = lcd
    seite.display(True); seite.display(False)
    s = lcd.surface
    unten = [t for t in texte if t[2] >= int(.92 * (H - 1)) - 1]
    r_ok = any(t[0] == regler and t[3] <= int(.7 * (W - 1)) for t in unten)
    zeile = [s.p[y][x] for y in range(int(.75 * (H - 1)), int(.9 * (H - 1)) + 1) for x in range(W)]
    hell = sum(1 for v in zeile if v in (1, 3)) / float(len(zeile))      # Anteil hell (invertiert)
    wifi = [t for t in unten if t[0].startswith('WIFI')]
    reg = [t for t in unten if t[0] == regler]
    w_ok = bool(wifi) and bool(reg) and wifi[0][1] > reg[0][3] and (wifi[0][4] - wifi[0][2]) < (reg[0][4] - reg[0][2])
    r_ok = r_ok and w_ok
    a_ok = (hell > 0.5) == alarm and (any(t[0] in ('ALARM basic', 'OFF COURSE') for t in texte) == alarm)
    ok &= r_ok and a_ok
    s.png(os.path.join(ordner, 'displaytest_%s.png' % name))
    print('%-18s Regler links unten "%s", WIFI kleiner rechts: %-6s Alarmzeile %s (hell %3.0f %%): %s' % (
        name, regler, 'OK' if r_ok else 'FEHLER', 'ja  ' if alarm else 'nein', 100 * hell, 'OK' if a_ok else 'FEHLER'))
    if name == 'offcourse': ok &= any(t[0] == 'OFF COURSE' for t in texte) and not any(t[0] == 'ALARM basic' for t in texte)
    print('   Texte:', ', '.join('%s @(%d,%d)-(%d,%d)' % t for t in texte if t[0].strip()))
print('alle Faelle bestanden' if ok else 'FEHLER')
sys.exit(0 if ok else 1)
