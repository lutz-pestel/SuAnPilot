#!/usr/bin/env python3
# SuAn-Regler, erste Fassung (PyPilot-AI, 02.10.2026). Entwurf: Software/SuAn_Regler/Entwurf.md
# Regelt die Ruderlage:  Soll = Trimm + k(Fahrt) x (Kursfehler + Tg x (Drehrate - Soll-Drehrate)) + Drehruder
# Die Pumpe wird ueber eine geschaetzte Ruderlage gefuehrt (Laufzeit x Rudergeschwindigkeit), die mit der um
# 'delay' verspaeteten Ruderanzeige abgeglichen wird. Alle Schiffswerte kommen aus SuAns Vermessung; solange
# Pflichtwerte fehlen (0), schaltet der Regler sofort auf 'basic' zurueck.
# Im TinyPilot: Datei nach pypilot/pilots/suan.py; am PC: SuanCore direkt (sim.py). Python 3.6.
import math, time

def resolv(a):
    """Winkel auf -180..180."""
    return (a + 180.0) % 360.0 - 180.0

def clip(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

# Name, Vorgabe, Minimum, Maximum, Bedeutung. Vorgabe 0 bei Schiffswerten = noch nicht vermessen.
PARAMS = [
    ('k_ref',      0.0, 0.0, 5.0,  'Grad Ruder je Grad Kursfehler bei v_ref (Pflicht)'),
    ('Tg',         0.0, 0.0, 20.0, 's, Gegenruder: Drehrate x Tg wirkt wie Kursfehler'),
    ('T_D',        0.0, 0.0, 10.0, 's, Glaettung der Drehrate fuers Gegenruder (Wellengieren; 0 = aus)'),
    ('v_ref',      5.0, 1.0, 12.0, 'kn, Bezugsfahrt fuer k_ref und K_ref'),
    ('n_v',        0.0, 0.0, 3.0,  'Exponent der Fahrtanpassung (0 = keine)'),
    ('v_min',      2.0, 0.5, 6.0,  'kn, kleinste Fahrt fuer die Anpassung'),
    ('fk_min',     0.5, 0.1, 1.0,  'k hoechstens so weit verkleinern (Faktor)'),
    ('fk_max',     3.0, 1.0, 6.0,  'k hoechstens so weit vergroessern (Faktor)'),
    ('K_ref',      0.0, 0.0, 3.0,  'Grad/s Drehung je Grad Ruder bei v_ref (Drehruder; 0 = aus)'),
    ('T_I',        0.0, 0.0, 900.0,'s, Zeitkonstante Rest-Trimm (0 = aus)'),
    ('T_S',        0.0, 0.0, 30.0, 's, Glaettung Kursfehler (Seegang)'),
    ('r_max_stb',  0.0, 0.0, 10.0, 'Grad/s, Kurswechsel nach Steuerbord (0 = Sprung)'),
    ('r_max_bb',   0.0, 0.0, 10.0, 'Grad/s, Kurswechsel nach Backbord (0 = Sprung)'),
    ('T_ramp',     0.0, 0.0, 30.0, 's, Soll-Drehung nimmt zum Ziel hin ab: Rest/T_ramp (0 = aus)'),
    ('T_acc',      0.0, 0.0, 30.0, 's, Soll-Drehung setzt weich ein und klingt weich aus (0 = Sprung)'),
    ('t_rev',      1.0, 0.0, 5.0,  's, Pumpenschutz: Mindestpause vor Richtungsumkehr'),
    ('rate_up',    0.0, 0.0, 30.0, 'Grad/s Ruder bei Pumpe + (Pflicht)'),
    ('rate_down',  0.0, 0.0, 30.0, 'Grad/s Ruder bei Pumpe - (Pflicht)'),
    ('delay',      1.0, 0.0, 3.0,  's, Verzoegerung der Ruderanzeige (gemessen 29.09.)'),
    ('db',         1.0, 0.2, 6.0,  'Grad, Totband der Pumpe um das Soll'),
    ('T_corr',     3.0, 0.5, 30.0, 's, Abgleich Schaetzung -> Anzeige'),
    ('hub',       30.0, 2.0, 60.0, 'Grad, groesster Ausschlag um den Trimm'),
    ('e_freeze',  15.0, 2.0, 60.0, 'Grad, ab diesem Kursfehler lernt der Trimm nicht'),
    ('t_blind',   10.0, 0.0, 60.0, 's, so lange ohne Ruderanzeige weiter mit Schaetzung'),
    ('jump_lim',   8.0, 2.0, 30.0, 'Grad, Abweichung Anzeige/Schaetzung gilt als unplausibel'),
    ('t_bad',      3.0, 0.5, 30.0, 's, (nicht mehr benutzt: Abweichung wird abgeglichen, nicht abgebrochen)'),
    ('lern',       0.4, 0.0, 1.0,  'Lernrate Rudergeschwindigkeit je Lauf (0 = fest)'),
    ('schwach',    0.5, 0.1, 0.9,  'Anteil der Soll-Rudergeschwindigkeit, unter dem Pumpe schwach gemeldet wird'),
    ('n_tot',      3.0, 1.0, 10.0, 'so viele Laeufe einer Richtung ohne Ruderbewegung -> Ruder folgt nicht'),
    ('speed',      1.0, 0.2, 1.0,  'Pumpengeschwindigkeit (Anteil)'),
    ('sparsam',    0.0, 0.0, 1.0,  '0 = Satz ruhig, 1 = Satz sparsam'),
    ('db_sparsam', 2.0, 0.2, 6.0,  'Grad, Totband im Satz sparsam'),
    ('TS_sparsam', 0.0, 0.0, 30.0, 's, Glaettung Kursfehler im Satz sparsam'),
]
DEFAULTS = {n: d for n, d, lo, hi, txt in PARAMS}
REQUIRED = ('k_ref', 'rate_up', 'rate_down')

class SuanCore(object):
    """Reiner Regler ohne pypilot; step() liefert den Pumpenbefehl -1..1."""
    def __init__(self, params=None):
        self.p = dict(DEFAULTS)
        if params:
            self.p.update(params)
        self.t = None
        self.reset(None, None)

    def reset(self, t, rudder, heading=None):
        self.t = t
        self.trim = rudder if rudder is not None else 0.0
        self.est_raw = rudder if rudder is not None else 0.0
        self.off = 0.0
        self.hist = []                   # (t, est_raw) fuer den Abgleich mit der verspaeteten Anzeige
        self.u = 0
        self.last_dir = 0                # Richtung des letzten Pumpenlaufs (Pumpenschutz)
        self.t_stop = -1e9
        self.rf = 0.0                    # gefilterte Soll-Kursaenderung (Grad/s Kompasskurs)
        self.rate_f = None               # geglaettete Drehrate fuers Gegenruder
        self.ef = 0.0
        self.ref = heading
        self.blind = 0.0
        self.bad = 0.0
        self.anz = []                    # (t, Anzeige) der letzten Sekunden, fuers Lernen der Rudergeschwindigkeit
        self.lauf = None                 # laufender Pumpenlauf (Richtung, Start)
        self.offen = []                  # beendete Laeufe, deren Wirkung noch nicht sichtbar ist (r, t0, t1)
        if not hasattr(self, 'v_up'):
            self.v_up = self.v_down = None   # gelernte Rudergeschwindigkeit (bleibt ueber reset erhalten)
            self.tot = {1: 0, -1: 0}
        self.n_abgl = 0
        self.info = {}

    def missing(self):
        return [n for n in REQUIRED if not self.p.get(n)]

    def _est_at(self, t):
        """Geschaetzte Ruderlage (ohne Abgleich) zum Zeitpunkt t aus dem Verlauf."""
        h = self.hist
        if not h or t <= h[0][0]:
            return h[0][1] if h else self.est_raw
        for (t0, e0), (t1, e1) in zip(h[-2::-1], h[:0:-1]):     # von hinten suchen
            if t0 <= t <= t1:
                return e0 + (e1 - e0) * (t - t0) / (t1 - t0) if t1 > t0 else e1
        return h[-1][1]

    def _anz_at(self, t):
        """Mittlere Ruderanzeige im Fenster t +- 0,2 s (Ausreisser der Anzeige daempfen)."""
        v = [a for ta, a in self.anz if abs(ta - t) <= 0.21]
        return sum(v) / len(v) if v else None

    def _lernen(self, t):
        """Rudergeschwindigkeit je Richtung aus beendeten Laeufen lernen (Anzeige um delay versetzt)."""
        p, rest = self.p, []
        for (r, t0, t1, t2) in self.offen:
            t_end = min(t1 + 0.3, t2) if t2 else t1 + 0.3   # naechster Lauf darf die Messung nicht verfaelschen
            if t < t_end + p['delay'] + 0.25:
                rest.append((r, t0, t1, t2)); continue
            a0, a1 = self._anz_at(t0 + p['delay']), self._anz_at(t_end + p['delay'])
            if a0 is None or a1 is None or t1 - t0 < 0.4:
                continue
            v = max(0.0, (a1 - a0) * r) / (t1 - t0)       # Grad/s in Befehlsrichtung
            soll = p['rate_up'] if r > 0 else p['rate_down']
            v = clip(v, 0.0, 1.5 * soll)
            self.tot[r] = self.tot[r] + 1 if v < 0.3 else 0
            if p['lern'] > 0:
                alt = self.v_up if r > 0 else self.v_down
                neu = clip(alt + (v - alt) * p['lern'], 0.3, 1.5 * soll)
                if r > 0: self.v_up = neu
                else: self.v_down = neu
        self.offen = rest

    def step(self, t, enabled, heading, command, rate, rudder, sog=None, windmode=False):
        p = self.p
        if self.t is None:
            self.reset(t, rudder, heading)
        dt = clip(t - self.t, 0.0, 0.5)
        self.t = t
        miss = self.missing()
        if miss:
            return 0, self._out('Rueckfall: Werte fehlen (%s)' % ','.join(miss))
        sparsam = p['sparsam'] >= 0.5
        db = p['db_sparsam'] if sparsam else p['db']
        T_S = p['TS_sparsam'] if sparsam else p['T_S']
        s = -1.0 if windmode else 1.0      # im Windmodus ist der Fehler umgekehrt (wie pypilot)

        # --- Ruderlage schaetzen (gelernte Rudergeschwindigkeit je Richtung) ---
        if self.v_up is None:
            self.v_up, self.v_down = p['rate_up'], p['rate_down']
        if self.u > 0:
            self.est_raw += self.v_up * dt
        elif self.u < 0:
            self.est_raw -= self.v_down * dt
        self.hist.append((t, self.est_raw))
        horizon = p['delay'] + 2.0
        while len(self.hist) > 2 and self.hist[1][0] < t - horizon:
            self.hist.pop(0)
        state = 'ok'
        if rudder is None:
            self.blind += dt
            if self.blind > p['t_blind']:
                return 0, self._out('Rueckfall: Ruderanzeige fehlt')
            state = 'blind'
        else:
            self.blind = 0.0
            self.anz.append((t, rudder))
            while self.anz and self.anz[0][0] < t - 20.0:
                self.anz.pop(0)
            self._lernen(t)
            past = self._est_at(t - p['delay']) + self.off
            diff = rudder - past
            if abs(diff) > p['jump_lim']:
                self.bad += dt
                if self.bad > 0.6:                      # anhaltend, kein Ausreisser: Schaetzung an Anzeige angleichen
                    self.off += diff
                    self.n_abgl += 1
                    self.bad = 0.0
                state = 'abgleich'
            else:
                self.bad = 0.0
                self.off += diff * min(1.0, dt / p['T_corr'])
        est = self.est_raw + self.off
        if self.lauf and rudder is not None:            # laufender langer Lauf: bewegt sich das Ruder ueberhaupt?
            r0, t0 = self.lauf
            eff = t - p['delay'] - t0                   # so lange wirkt der Lauf schon in der Anzeige
            if eff > 1.5:
                a0 = self._anz_at(t0 + p['delay'])
                a1 = sum(a for ta, a in self.anz if ta > t - 0.4) / max(1, len([1 for ta, a in self.anz if ta > t - 0.4]))
                if a0 is not None:
                    v_live = max(0.0, (a1 - a0) * r0) / eff
                    if eff > 2.5 and v_live < 0.3:
                        self._stop(t)
                        return 0, self._out('Rueckfall: Ruder folgt nicht (%s)' % ('vorw' if r0 > 0 else 'rueckw'))
                    if r0 > 0: self.v_up = clip(min(self.v_up, 1.2 * v_live), 0.3, 1.5 * p['rate_up'])
                    else: self.v_down = clip(min(self.v_down, 1.2 * v_live), 0.3, 1.5 * p['rate_down'])
        for r in (1, -1):                               # Ruder bewegt sich trotz Pumpe nicht: an basic uebergeben
            if self.tot[r] >= p['n_tot']:
                self.tot[r] = 0
                return 0, self._out('Rueckfall: Ruder folgt nicht (%s)' % ('vorw' if r > 0 else 'rueckw'))
        for r, v, sp in ((1, self.v_up, p['rate_up']), (-1, self.v_down, p['rate_down'])):
            if v < p['schwach'] * sp and state == 'ok':
                state = 'Pumpe %s schwach %.1f' % ('vorw' if r > 0 else 'rueckw', v)

        if not enabled:
            self._stop(t)
            self.rf = 0.0
            self.ref = heading
            self.trim = est
            self.ef = 0.0
            return 0, self._out('aus', est=est)

        # --- Sollkurs als Rampe (Kurswechsel mit begrenzter Drehrate, je Seite) ---
        if self.ref is None:
            self.ref = heading
        d = resolv(command - self.ref)
        turn = s * d                                   # >0: Kompasskurs waechst = Drehung nach Steuerbord
        rmax = p['r_max_stb'] if turn > 0 else p['r_max_bb']
        if rmax > 0:
            target = 0.0
            if abs(d) > 0.5:
                target = rmax if p['T_ramp'] <= 0 else min(rmax, abs(d) / p['T_ramp'])   # zum Ziel hin langsamer
                target = math.copysign(target, d)
            if p['T_acc'] > 0:                         # weich einsetzen und ausklingen, kein Sprung im Soll-Ruder
                self.rf += (target - self.rf) * min(1.0, dt / p['T_acc'])
            else:
                self.rf = target
            step = self.rf * dt
            if abs(d) <= max(abs(step), 0.5) or step * d <= 0:
                self.ref = command
            else:
                self.ref = resolv(self.ref + step)
        else:
            self.rf = 0.0
            self.ref = command
        r_ref = s * self.rf                            # >0: Soll-Drehung nach Steuerbord
        ramping = abs(resolv(command - self.ref)) > 0.5 or abs(self.rf) > 0.1

        # --- Kursfehler, Fahrt, Verstaerkung ---
        e = clip(s * resolv(heading - self.ref), -60.0, 60.0)
        if T_S > 0:
            self.ef += (e - self.ef) * min(1.0, dt / T_S)
        else:
            self.ef = e
        f = 1.0
        if p['n_v'] > 0 and sog is not None and sog is not False:
            v = max(float(sog), p['v_min'])
            f = clip((p['v_ref'] / v) ** p['n_v'], p['fk_min'], p['fk_max'])
        k = p['k_ref'] * f
        dff = 0.0
        if p['K_ref'] > 0 and r_ref:
            dff = -r_ref / (p['K_ref'] / f)            # Ruder, das die Soll-Drehung erzeugt (r = -K x Ruder)

        # --- Drehrate fuers Gegenruder glaetten (Wellengieren nicht nachsteuern) ---
        if self.rate_f is None or p['T_D'] <= 0:
            self.rate_f = rate
        else:
            self.rate_f += (rate - self.rate_f) * min(1.0, dt / p['T_D'])

        # --- Soll-Ruderlage ---
        raw = self.trim + k * (self.ef + p['Tg'] * (self.rate_f - r_ref)) + dff
        lim = float(p.get('limit', 30.0))
        soll = clip(clip(raw, self.trim - p['hub'], self.trim + p['hub']), -lim, lim)
        saturated = abs(soll - raw) > 0.01

        # --- Rest-Trimm: langsam, eingefroren bei Kurswechsel, Anschlag und grossem Fehler ---
        if p['T_I'] > 0 and not ramping and not saturated and abs(e) < p['e_freeze']:
            self.trim = clip(self.trim + k * self.ef * dt / p['T_I'], -lim, lim)

        # --- Pumpe: bis die geschaetzte Lage im Totband liegt ---
        diff = soll - est
        if self.u != 0:
            if diff * self.u <= 0 or abs(diff) < db / 2:
                self._stop(t)
        if self.u == 0 and abs(diff) > db:
            want = 1 if diff > 0 else -1
            if not (want == -self.last_dir and t - self.t_stop < p['t_rev']):   # Pumpenschutz
                self.u = want
                if self.offen and self.offen[-1][3] is None:
                    r0, a, b, _ = self.offen[-1]; self.offen[-1] = (r0, a, b, t)
                self.lauf = (want, t)
        return self.u * p['speed'], self._out(state, est=est, soll=soll, k=k, e=e, ramp=ramping)

    def _stop(self, t):
        if self.u and self.lauf:
            self.offen.append((self.lauf[0], self.lauf[1], t, None))
        self.last_dir, self.t_stop, self.u, self.lauf = self.u, t, 0, None

    def _out(self, state, **kw):
        self.info = dict(state=state, trim=self.trim, v_up=self.v_up, v_down=self.v_down, n_abgl=self.n_abgl, **kw)
        if state.startswith('Rueckfall') or state == 'aus':
            self._stop(self.t if self.t is not None else 0.0)
        return self.info

# ---------------------------------------------------------------- Anbindung an pypilot 0.24
try:
    from pilot import AutopilotPilot, AutopilotGain
    from pypilot.values import SensorValue, StringValue
except ImportError:                     # am PC ohne pypilot
    AutopilotPilot = None

if AutopilotPilot:
    class SuanPilot(AutopilotPilot):
        def __init__(self, ap):
            super(SuanPilot, self).__init__('suan', ap)
            self.gains = {}
            self.core = SuanCore()
            self.vals = {n: self.register(AutopilotGain, n, d, lo, hi) for n, d, lo, hi, txt in PARAMS}
            self.out = {n: self.register(SensorValue, n) for n in ('soll', 'est', 'trim', 'k', 'fehler', 'v_up', 'v_down')}
            self.status = self.register(StringValue, 'status', '')
            self.last_t = None

        def process(self, reset):
            try:
                self._process(reset)
            except Exception as e:                      # nie den Autopiloten anhalten: zurueck auf basic
                try:
                    self.ap.servo.command.set(0)
                    self.ap.pilot.set('basic')
                    print('suan: Rueckfall, Fehler', repr(e))
                except Exception:
                    pass

        def _process(self, reset):
            ap = self.ap
            t = time.monotonic()
            rudder = ap.sensors.rudder.angle.value
            rudder = None if type(rudder) == bool else rudder
            sog = ap.sensors.gps.speed.value
            sog = None if type(sog) == bool else sog
            heading, command = ap.heading.value, ap.heading_command.value
            rate = ap.boatimu.SensorValues['headingrate_lowpass'].value
            if type(heading) == bool or type(rate) == bool:
                return
            # Autopilot eben eingeschaltet oder Regler eben gewaehlt (Luecke > 1 s): jetzige Lage = Trimm
            if reset or self.last_t is None or t - self.last_t > 1.0:
                self.core.reset(t, rudder, heading)
            self.last_t = t
            try:
                for n, v in self.vals.items():
                    self.core.p[n] = v.value
                self.core.p['limit'] = ap.sensors.rudder.range.value
                u, info = self.core.step(t, ap.enabled.value, heading, command, rate, rudder, sog,
                                         'wind' in ap.mode.value)
            except Exception as e:
                u, info = 0, {'state': 'Rueckfall: Fehler %s' % e}
            if self.status.value != info['state']:
                self.status.set(info['state'])
            if info['state'].startswith('Rueckfall'):
                try:
                    print('suan:', info['state'])
                except Exception:
                    pass
                ap.pilot.set('basic')                   # sicherer Rueckweg
                return
            for n, key in (('soll', 'soll'), ('est', 'est'), ('trim', 'trim'), ('k', 'k'), ('fehler', 'e'),
                           ('v_up', 'v_up'), ('v_down', 'v_down')):
                if info.get(key) is not None:
                    self.out[n].set(round(info[key], 2))
            if ap.enabled.value:
                ap.servo.command.set(u)

    pilot = SuanPilot
