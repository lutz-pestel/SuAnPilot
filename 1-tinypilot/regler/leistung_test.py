#!/usr/bin/env python3
# Pruefung der adaptiven Pumpenleistung (leistung.py) am PC, Version 00.02, Stand 08.10.2026 (PyPilot-AI).
# Nachbildung nach Testbericht 08.10.2026: rueckwaerts versagt ab Befehl 0,90, wenn die Ruhespannung unter 13,3 V liegt
# (12,65 V gestoert, 14,0 V normal); Servo-Kalibrierung 0,2 + 0,8 x Geschwindigkeit wie an Bord.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'autopilot', 'software', 'RPI', 'kern',
                                'usr', 'local', 'lib', 'python3.6', 'site-packages', 'pypilot'))
import leistung
from leistung import Leistungsgrenze

class Wert(object):
    def __init__(self, v): self.value = v
    def set(self, v): self.value = v

class Boot(object):
    def __init__(self):
        self.grenze = {1: Wert(100.0), -1: Wert(100.0)}
        self.uref = {1: Wert(0.0), -1: Wert(0.0)}
        self.meldungen = []
        self.lg = Leistungsgrenze(self.grenze, self.uref, lambda s: self.meldungen.append('%6.1f s  %s' % (self.t, s)))
        self.t, self.ruder, self.anz, self.u0 = 0.0, 15.0, [], 12.65
        self.kriech = 0.3          # Grad/s, mit denen das gestoerte Ruder noch kriecht (Hafen 08.10.: 0,3-0,7)
    def schritt(self, soll, dt=0.1, anzeige=True):
        """soll: -1..1 wie der Regler; liefert (Befehl, Strom)."""
        speed = min(max(soll, -self.lg.faktor(-1)), self.lg.faktor(1))
        befehl = 0.0 if speed == 0 else (0.2 + 0.8 * abs(speed)) * (1 if speed > 0 else -1)
        gestoert = befehl <= -0.90 and self.u0 < 13.3
        if befehl == 0:
            strom = 0.0
        elif gestoert:
            strom, self.ruder = 1.1, self.ruder - self.kriech * dt
        else:
            strom = max(0.5, 6.4 * abs(befehl) - 1.6)   # passt zu 08.10.: Befehl 0,68 -> 2,7 A, 0,88 -> 4,0 A
            self.ruder += (4.3 if befehl < 0 else 5.5) * abs(befehl) * dt * (1 if befehl > 0 else -1)
        spannung = self.u0 - 0.3 * strom
        self.anz.append((self.t, self.ruder))
        a = [r for t, r in self.anz if t <= self.t - leistung.VERZ]
        self.lg.update(self.t, befehl, strom, spannung, (a[-1] if a else self.anz[0][1]) if anzeige else False)
        self.t += dt
        return befehl, strom
    def laufe(self, soll, dauer, **kw):
        out = [self.schritt(soll, **kw) for _ in range(int(round(dauer / 0.1)))]
        return out

def pruefe(name, ok, info=''):
    print('%-62s %s  %s' % (name, 'OK  ' if ok else 'FEHLER', info))
    return ok

alle = True
b = Boot()
b.laufe(0, 3)                                         # Ruhe 12,65 V messen
r = b.laufe(-1, 8)                                    # Autopilot will voll rueckwaerts
alle &= pruefe('A Batterie 12,65 V: rueckwaerts gestoert -> Absenkung bis 85 %', b.grenze[-1].value == 85.0,
               'Grenze %.0f %%, Strom am Ende %.1f A' % (b.grenze[-1].value, r[-1][1]))
alle &= pruefe('  danach laeuft die Pumpe (Befehl 0,88, Strom > 4 A)', abs(r[-1][0]) < 0.90 and r[-1][1] > 4.0)
alle &= pruefe('  vorwaerts unveraendert 100 %', b.grenze[1].value == 100.0)
alle &= pruefe('  Bezugsspannung = Ruhespannung', abs(b.uref[-1].value - 12.65) < 0.05, '%.2f V' % b.uref[-1].value)
b.laufe(0, 40)
alle &= pruefe('B Ruhe 12,65 V 40 s: keine Freigabe', b.grenze[-1].value == 85.0)
b.u0 = 13.5; b.laufe(0, 90)
alle &= pruefe('C Ruhe 13,5 V (+0,85 V) 90 s: keine Freigabe', b.grenze[-1].value == 85.0)
b.u0 = 14.0; b.laufe(0, 30)
alle &= pruefe('D Ruhe 14,0 V (+1,35 V) nach 30 s: noch keine Freigabe', b.grenze[-1].value == 85.0)
b.laufe(0, 35)
alle &= pruefe('  nach 65 s: Freigabe auf 100 %', b.grenze[-1].value == 100.0)
r = b.laufe(-1, 4)
alle &= pruefe('  bei 14 V rueckwaerts mit 100 % normal, keine Absenkung', b.grenze[-1].value == 100.0 and r[-1][1] > 4)
b.u0 = 14.0; b.laufe(0, 3); b.laufe(-1, 1); b.laufe(0, 2); b.laufe(-1, 1)     # Unterbrechung durch Pumpenlauf
b2 = Boot(); b2.laufe(0, 3); b2.laufe(1, 8)
alle &= pruefe('E vorwaerts voll bei 12,65 V: keine Absenkung', b2.grenze[1].value == 100.0 and b2.grenze[-1].value == 100.0)
b3 = Boot(); b3.grenze[-1].set(20.0); b3.laufe(0, 3); r = b3.laufe(-1, 6)
alle &= pruefe('F Grenze 20 %%, Strom klein (%.1f A) aber Ruder laeuft: keine Absenkung' % r[-1][1], b3.grenze[-1].value == 20.0)
b4 = Boot(); b4.laufe(0, 3); b4.laufe(-1, 8, anzeige=False)
alle &= pruefe('G ohne Ruderanzeige: keine Absenkung', b4.grenze[-1].value == 100.0)
b5 = Boot(); b5.laufe(-1, 8)
alle &= pruefe('H Lauf gleich nach dem Start (keine Ruhespannung): Absenkung, Bezug gesetzt',
               b5.grenze[-1].value == 85.0 and b5.uref[-1].value > 0, 'Bezug %.2f V' % b5.uref[-1].value)
b6 = Boot(); b6.kriech = 0.7; b6.laufe(0, 3); b6.laufe(-1, 8)
alle &= pruefe('I gestoertes Ruder kriecht mit 0,7 Grad/s: trotzdem Absenkung bis 85 %', b6.grenze[-1].value == 85.0,
               b6.meldungen[0][:8].strip() if b6.meldungen else 'keine Absenkung')
erste = float(b.meldungen[0][:6])
alle &= pruefe('J erste Absenkung spaetestens 2,5 s nach Laufbeginn (Start bei 3,0 s)', erste <= 5.5, '%.1f s' % erste)
b7 = Boot(); b7.laufe(0, 3); b7.laufe(-1, 8); b7.lg.reset('Autopilot eingeschaltet')
alle &= pruefe('K Einschalten des Autopiloten: beide Richtungen 100 %, Bezug geloescht',
               b7.grenze[-1].value == 100.0 and b7.uref[-1].value == 0.0)
b8 = Boot(); b8.grenze[-1].set(40.0); b8.laufe(0, 3); r = b8.laufe(-1, 6)
alle &= pruefe('L Grenze 40 %%, Strom %.1f A, Ruder laeuft langsam: keine Absenkung' % r[-1][1], b8.grenze[-1].value == 40.0)
print('\nMeldungen Fall A-D:'); print('\n'.join(b.meldungen))
print('\nALLE PRUEFUNGEN OK' if alle else '\nPRUEFUNG FEHLGESCHLAGEN')
