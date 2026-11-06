#!/usr/bin/env python3
# Robnet-Analyse: Speicheroszilloskop im Browser. Version 00.01, Stand 06.11.2026.
# Anforderungen: anforderungen_oszilloskop.md. Nur lesen: Sendet nichts auf den Robnet-Bus.
# Messschleife: messkern_v00.01.c. Laeuft als Dienst robnet-oszilloskop, Port 8080.
import bisect
import csv
import io
import json
import os
import re
import shutil
import struct
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pigpio

VERSION = "00.01"
HIER = os.path.dirname(os.path.abspath(__file__))
MESSKERN = os.path.join(HIER, "messkern")
SEITE = os.path.join(HIER, "oszilloskop_v00.01.html")
ZIEL = "/home/pi/aufzeichnungen"
PORT = 8080
VREF = 2.5
F13 = (100 + 13) / 13
F82 = (100 + 8.2) / 8.2
# Kanal: (Klemme, Name, Wandlerkanal, Faktor); alle am oberen Sockel U2
KANAL = {1: (1, "Bus−", 1, F13), 2: (2, "Bus+", 0, F13), 3: (3, "Vsys+", 2, F82), 4: (5, "On-Off", 3, F13), 5: (6, "Alarm", 4, F13)}
# Geschwindigkeit: Teiler -> (Name, Nullpunkt in Stufen, am Pi gemessen 06.11.2026)
TEMPO = {56: ("Maximum", 14.0), 100: ("Schnell", 8.7), 200: ("Mittel", 1.6), 800: ("Genau", 0.0)}
GPIO_BUS, GPIO_ALARM = 23, 27
BELEGT = "/tmp/robnet_aufzeichnung.pid"
KOPF = "<4sIIIIIQQIfffff"
KOPF_GR = struct.calcsize(KOPF)


def spannung(rohwert, faktor, kern):
    return (rohwert - kern["null"]) * kern["gain"] * VREF / 4096 * faktor


class Kern:
    """Spricht mit dem C-Programm der Messschleife."""

    def __init__(self):
        self.proz = None
        self.sperre = threading.RLock()
        self.konfig = None
        self.rate = 0.0
        self.gain = 1.0
        self.null = 0.0
        self.letzte = 0.0

    def laeuft(self):
        return self.proz is not None and self.proz.poll() is None

    def starten(self):
        if not self.laeuft():
            self.proz = subprocess.Popen([MESSKERN], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            self.konfig = None

    def stoppen(self):
        with self.sperre:
            if self.laeuft():
                try:
                    self.proz.stdin.write(b"E\n")
                    self.proz.stdin.flush()
                    self.proz.wait(timeout=3)
                except Exception:
                    self.proz.kill()
            self.proz = None
            self.konfig = None

    def _senden(self, s):
        self.proz.stdin.write((s + "\n").encode())
        self.proz.stdin.flush()

    def _kopf(self):
        d = self.proz.stdout.read(KOPF_GR)
        if len(d) != KOPF_GR:
            raise RuntimeError("Messschleife antwortet nicht")
        f = struct.unpack(KOPF, d)
        return dict(art=f[1], n=f[2], breite=f[3], ausgeloest=f[4], teiler=f[5], scans=f[6], trigger_scan=f[7],
                    tick_start=f[8], rate=f[9], min=f[10], max=f[11], kalib=f[12], ref=f[13])

    def _kalib_setzen(self, teiler, k):
        b = TEMPO.get(teiler, ("", 0.0))[1]
        ref = k["ref"]
        roh = ref / k["kalib"] if k["kalib"] else ref
        self.null = b
        self.gain = ref / (roh - b) if roh - b > 1 else 1.0

    def konfigurieren(self, teiler, codes):
        wunsch = (teiler, tuple(codes))
        if self.konfig == wunsch:
            return
        self.starten()
        self._senden(f"K {teiler} {len(codes)} " + " ".join(map(str, codes)))
        k = self._kopf()
        self._kalib_setzen(teiler, k)
        self.konfig = wunsch
        self.rate = {56: 236000.0, 100: 139000.0, 200: 72000.0, 800: 18400.0}[teiler] / len(codes)

    def frame(self, vor, nach, art, quelle, pegel, steigend, warte, breite):
        self._senden(f"F {vor} {nach} {art} {quelle} {pegel} {steigend} {warte} {breite}")
        k = self._kopf()
        d = self.proz.stdout.read(k["n"] * k["breite"] * 4)
        if k["rate"] > 0:
            self.rate = k["rate"]
        werte = struct.unpack("<%dH" % (len(d) // 2), d)
        return k, werte

    def aufzeichnen(self, pfad, dauer):
        self._senden(f"R {pfad} {dauer}")
        return self._kopf()

    def abbrechen(self):
        if self.laeuft():
            try:
                self._senden("X")
            except Exception:
                pass


kern = Kern()


class Digital:
    """Merkt sich die Pegelwechsel von Bus-Empfaenger und Alarm (pigpio, 2 us)."""

    def __init__(self):
        self.sperre = threading.Lock()
        self.ticks, self.pegel = [], []
        self.pi = None
        self.griff = None
        self.datei = None
        self.fehler = ""

    def starten(self):
        if subprocess.run(["pgrep", "-x", "pigpiod"], capture_output=True).returncode != 0:
            subprocess.run(["pigpiod", "-s", "2"], check=False)
            time.sleep(1.0)
        self.pi = pigpio.pi()
        if not self.pi.connected:
            self.fehler = "pigpiod antwortet nicht"
            return
        for g in (GPIO_BUS, GPIO_ALARM):
            self.pi.set_pull_up_down(g, pigpio.PUD_OFF)
        self.griff = self.pi.notify_open()
        self.pi.notify_begin(self.griff, (1 << GPIO_BUS) | (1 << GPIO_ALARM))
        threading.Thread(target=self._lesen, daemon=True).start()

    def _lesen(self):
        with open(f"/dev/pigpio{self.griff}", "rb", buffering=0) as rohr:
            rest = b""
            while True:
                daten = rest + rohr.read(65536)
                n = len(daten) // 12
                rest = daten[n * 12:]
                neu_t, neu_p = [], []
                for i in range(n):
                    _, flags, tick, lev = struct.unpack_from("<HHII", daten, i * 12)
                    if flags:
                        continue
                    neu_t.append(tick)
                    neu_p.append((lev >> GPIO_BUS & 1) | (lev >> GPIO_ALARM & 1) << 1)
                with self.sperre:
                    self.ticks += neu_t
                    self.pegel += neu_p
                    if len(self.ticks) > 400000:
                        del self.ticks[:200000]
                        del self.pegel[:200000]
                    if self.datei:
                        for t, p in zip(neu_t, neu_p):
                            self.datei.write(struct.pack("<IB", t, p))

    def fenster(self, tick_start, dauer_us):
        """Pegelwechsel im Fenster, Zeiten in us ab Fensterbeginn."""
        with self.sperre:
            t = list(self.ticks[-200000:])
            p = list(self.pegel[-200000:])
        if not t:
            lev = self.pi.read(GPIO_BUS) | self.pi.read(GPIO_ALARM) << 1 if self.pi else 1
            return lev, []
        ende = (tick_start + int(dauer_us)) & 0xFFFFFFFF
        # 32-Bit-Zeit, relativ zum Start rechnen
        rel = [((x - tick_start + 0x80000000) & 0xFFFFFFFF) - 0x80000000 for x in t]
        a = bisect.bisect_left(rel, 0)
        b = bisect.bisect_right(rel, int(dauer_us))
        start_p = p[a - 1] if a > 0 else (p[0] if p else 1)
        return start_p, list(zip(rel[a:b], p[a:b]))


digital = Digital()


def spur(start, wechsel, bit):
    """Eine digitale Spur als (t, pegel), nur echte Wechsel."""
    aus, alt = [], (start >> bit) & 1
    for t, p in wechsel:
        w = (p >> bit) & 1
        if w != alt:
            aus.append((t, w))
            alt = w
    return (start >> bit) & 1, aus


def bytes_zerlegen(start_pegel, wechsel, baud, dauer_us):
    """Serielle Bytes aus Pegelwechseln: 8 Datenbits, keine Paritaet, 1 Stopbit."""
    if baud <= 0:
        return []
    bit = 1e6 / baud
    n = len(wechsel)

    def lauf(ab, grenze=None):
        ergebnis, falsch = [], 0
        i = ab
        while i < n and (grenze is None or len(ergebnis) + falsch < grenze):
            t0, w = wechsel[i]
            if w != 0:
                i += 1
                continue
            j = i
            wert = 0
            pegel = 0

            def pegel_bei(t, j):
                while j + 1 < n and wechsel[j + 1][0] <= t:
                    j += 1
                return wechsel[j][1], j
            for b in range(8):
                pegel, j = pegel_bei(t0 + bit * (1.5 + b), j)
                wert |= pegel << b
            stop, j = pegel_bei(t0 + bit * 9.5, j)
            if t0 + bit * 9.5 > dauer_us:
                break
            if stop == 1:
                ergebnis.append((t0, wert))
            else:
                falsch += 1
            ende = t0 + bit * 9.5
            i = j
            while i < n and not (wechsel[i][1] == 0 and wechsel[i][0] > ende):
                i += 1
        return ergebnis, falsch

    beste, wenig, geprueft = 0, None, 0
    for i, (_, w) in enumerate(wechsel):
        if w != 0:
            continue
        _, f = lauf(i, 60)
        if wenig is None or f < wenig:
            beste, wenig = i, f
        geprueft += 1
        if f == 0 or geprueft >= 20:
            break
    return lauf(beste)[0][:800]


def planen(q):
    """Aus der Anfrage: Messliste und was daraus berechnet wird."""
    teiler = int(q.get("tempo", "56"))
    if teiler not in TEMPO:
        teiler = 56
    aktiv = [int(x) for x in q.get("k", "1").split(",") if x.strip().isdigit() and int(x) in KANAL][:5]
    d12 = q.get("d12", "aus")
    d56 = q.get("d56", "aus")
    codes, plaetze = [], {}

    def mess(k):
        if k not in plaetze:
            plaetze[k] = len(codes)
            codes.append(KANAL[k][2])
    for k in aktiv:
        mess(k)
    chip12 = None
    if d12 == "software":
        mess(1)
        mess(2)
    elif d12 == "chip":
        chip12 = len(codes)
        codes.append(8 + 1)  # im Chip: CH1 minus CH0, also Klemme 1 minus Klemme 2, nur positiv
    if d56 == "software":
        mess(4)
        mess(5)
    if not codes:
        mess(1)
    return teiler, aktiv, d12, d56, codes, plaetze, chip12


def in_mv(w):
    return [int(round(x * 1000)) for x in w]


def kurven(k, werte, aktiv, d12, d56, plaetze, chip12, gain, null_):
    """Rohspalten in Millivolt je angezeigter Kurve."""
    br = k["breite"]
    kern_d = {"null": null_, "gain": gain}
    aus = {}

    def spalten(platz):
        return werte[platz * br * 2:(platz + 1) * br * 2]

    def volt(platz, faktor):
        s = spalten(platz)
        return [spannung(x, faktor, kern_d) for x in s]
    for ka in aktiv:
        aus[f"K{ka}"] = in_mv(volt(plaetze[ka], KANAL[ka][3]))

    def differenz(a, b):
        va, vb = volt(plaetze[a], KANAL[a][3]), volt(plaetze[b], KANAL[b][3])
        return in_mv([x - y for x, y in zip(va, vb)])
    if d12 == "software":
        aus["D12"] = differenz(1, 2)
    elif d12 == "chip" and chip12 is not None:
        aus["D12"] = in_mv(volt(chip12, F13))
    if d56 == "software":
        aus["D56"] = differenz(4, 5)
    return aus


zustand = {"aufnahme": None, "fremd": False}
zustand_sperre = threading.Lock()


def fremde_aufzeichnung():
    # Die Bus-Aufzeichnung meldet sich ueber eine Datei und wartet, bis die Messschleife beendet ist
    try:
        pid = int(open(BELEGT).read().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def waechter():
    # Gibt den Wandler frei, wenn die Bus-Aufzeichnung ihn braucht oder niemand mehr zusieht
    while True:
        time.sleep(0.5)
        fremd = fremde_aufzeichnung()
        ruhe = time.time() - kern.letzte > 15 and not zustand["aufnahme"]
        if kern.laeuft() and (fremd or ruhe):
            kern.stoppen()


def status():
    r = {"version": VERSION, "fremd": False, "aufnahme": zustand["aufnahme"], "fehler": digital.fehler}
    r["frei_mb"] = shutil.disk_usage("/").free // (1024 * 1024)
    try:
        r["temp"] = round(int(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000, 1)
    except Exception:
        r["temp"] = None
    if fremde_aufzeichnung():
        r["fremd"] = True
        d = neueste_aufnahme()
        if d:
            r["fremd_ordner"] = os.path.basename(d)
            r["fremd_byte"] = sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d))
            r["fremd_seit_s"] = round(time.time() - os.path.getmtime(os.path.join(d, "kopf.json")))
    zustand["fremd"] = r["fremd"]
    return r


def neueste_aufnahme():
    if not os.path.isdir(ZIEL):
        return None
    alle = [os.path.join(ZIEL, x) for x in os.listdir(ZIEL) if os.path.isdir(os.path.join(ZIEL, x))]
    return max(alle, key=os.path.getmtime) if alle else None


def frame_liefern(q):
    if fremde_aufzeichnung():
        return {"belegt": "Bus-Aufzeichnung läuft, das Oszilloskop misst nicht."}
    if zustand["aufnahme"]:
        return {"belegt": "Oszilloskop-Aufzeichnung läuft."}
    teiler, aktiv, d12, d56, codes, plaetze, chip12 = planen(q)
    tdiv = float(q.get("tdiv", "0.001"))
    vor_ant = max(0.0, min(1.0, float(q.get("vor", "10")) / 100))
    breite = max(50, min(4000, int(q.get("breite", "1000"))))
    baud = int(q.get("baud", "0") or 0)
    modus = q.get("modus", "auto")
    with kern.sperre:
        kern.letzte = time.time()
        kern.konfigurieren(teiler, codes)
        fenster = tdiv * 10
        scans = max(4, int(fenster * kern.rate))
        vor = int(scans * vor_ant)
        nach = scans - vor
        quelle = q.get("trig", "keine")
        pegel_v = float(q.get("pegel", "1"))
        steigend = 1 if q.get("flanke", "1") == "1" else 0
        code = -1
        pegel_roh = 0
        if quelle == "bus":
            code = 100
        elif quelle == "alarm":
            code = 101
        elif re.fullmatch(r"k[1-5]", quelle):
            ka = int(quelle[1:])
            if ka in plaetze:
                code = plaetze[ka]
                pegel_roh = int(pegel_v / KANAL[ka][3] * 4096 / VREF / kern.gain + kern.null)
        art = 0 if modus == "auto" else 1
        warte = 200 if art == 0 else 250
        k, werte = kern.frame(vor, nach, art, code, pegel_roh, steigend, warte, breite)
        kern.letzte = time.time()
        rate = k["rate"] or kern.rate
        gain, null_ = kern.gain, kern.null
    dauer_us = k["scans"] / rate * 1e6
    antwort = {"t_us": dauer_us, "n_spalten": k["breite"], "ausgeloest": k["ausgeloest"], "scans": k["scans"],
               "trigger_us": k["trigger_scan"] / rate * 1e6, "rate_scan": rate, "messungen": k["n"],
               "rate_gesamt": rate * k["n"], "abstand_min": k["min"] if k["max"] else None, "abstand_max": k["max"] if k["max"] else None, "kalib": round(gain, 4),
               "null": null_, "tempo": TEMPO[teiler][0], "takt_mhz": 400.0 / teiler, "kurven": kurven(k, werte, aktiv, d12, d56, plaetze, chip12, gain, null_)}
    start, wechsel = digital.fenster(k["tick_start"], dauer_us)
    if q.get("bus", "1") == "1":
        s, w = spur(start, wechsel, 0)
        antwort["bus"] = {"start": s, "w": w[:6000]}
        if baud:
            antwort["bytes"] = [[round(t), v] for t, v in bytes_zerlegen(s, w, baud, dauer_us)]
    if q.get("alarm", "0") == "1":
        s, w = spur(start, wechsel, 1)
        antwort["alarm"] = {"start": s, "w": w[:6000]}
    return antwort


def aufnahme_starten(q):
    if fremde_aufzeichnung():
        return {"fehler": "Bus-Aufzeichnung läuft."}
    if zustand["aufnahme"]:
        return {"fehler": "Es läuft schon eine Aufzeichnung."}
    teiler, aktiv, d12, d56, codes, plaetze, chip12 = planen(q)
    dauer = max(0.2, min(3600.0, float(q.get("dauer", "5"))))
    name = re.sub(r"[^A-Za-z0-9_-]", "_", q.get("name", "") or "")[:40] or "aufnahme"
    ordner = os.path.join(ZIEL, time.strftime("%Y-%m-%d_%H-%M-%S_") + name)
    os.makedirs(ordner, exist_ok=True)
    kopf = {"art": "oszilloskop", "version": VERSION, "start": time.strftime("%Y-%m-%d %H:%M:%S %z"), "name": name, "dauer_s": dauer, "tempo": TEMPO[teiler][0],
            "teiler": teiler, "codes": codes, "aktiv": aktiv, "d12": d12, "d56": d56, "plaetze": plaetze, "chip12": chip12, "baud": int(q.get("baud", "0") or 0)}

    def lauf():
        z = zustand["aufnahme"] = {"name": name, "ordner": os.path.basename(ordner), "ende": time.time() + dauer + 1}
        try:
            with kern.sperre:
                kern.konfigurieren(teiler, codes)
                kopf["gain"], kopf["null"] = kern.gain, kern.null
                time.sleep(0.05)
                kopf["tick_start"] = digital.pi.get_current_tick() if digital.pi else 0
                datei = open(os.path.join(ordner, "digital.bin"), "wb")
                with digital.sperre:
                    digital.datei = datei
                k = kern.aufzeichnen(os.path.join(ordner, "analog.bin"), dauer)
                with digital.sperre:
                    digital.datei = None
                datei.close()
            kopf.update(scans=k["scans"], rate=k["rate"], messungen=k["n"], abstand_min=k["min"], abstand_max=k["max"], tick_ende=k["tick_start"], fertig=True)
            kopf["rate_scan"] = k["scans"] / dauer if dauer else k["rate"]
        except Exception as e:
            kopf["fehler"] = str(e)
        with open(os.path.join(ordner, "kopf.json"), "w") as f:
            json.dump(kopf, f, indent=1)
        for x in os.listdir(ordner):
            os.chown(os.path.join(ordner, x), 1000, 1000)
        os.chown(ordner, 1000, 1000)
        zustand["aufnahme"] = None
    threading.Thread(target=lauf, daemon=True).start()
    return {"ok": True, "ordner": os.path.basename(ordner)}


def aufnahmen():
    aus = []
    if os.path.isdir(ZIEL):
        for x in sorted(os.listdir(ZIEL), reverse=True):
            d = os.path.join(ZIEL, x)
            f = os.path.join(d, "kopf.json")
            if not os.path.isfile(f):
                continue
            try:
                k = json.load(open(f))
            except Exception:
                continue
            aus.append({"ordner": x, "art": k.get("art", "bus"), "dauer": k.get("dauer_s"), "rate": k.get("rate"), "tempo": k.get("tempo", "–"),
                        "groesse_kb": sum(os.path.getsize(os.path.join(d, y)) for y in os.listdir(d)) // 1024})
    return aus


def ordner_sicher(name):
    name = os.path.basename(name or "")
    d = os.path.join(ZIEL, name)
    if not name or not os.path.isdir(d):
        raise ValueError("Ordner nicht gefunden")
    return d


def aufnahme_ansehen(q):
    d = ordner_sicher(q.get("ordner"))
    k = json.load(open(os.path.join(d, "kopf.json")))
    breite = max(50, min(4000, int(q.get("breite", "1000"))))
    von, bis = float(q.get("von", "0")), float(q.get("bis", "0"))
    gesamt = k.get("dauer_s") or 0
    if bis <= von:
        bis = gesamt or von + 1
    antwort = {"gesamt_s": gesamt, "von": von, "bis": bis, "kopf": {x: k.get(x) for x in ("name", "start", "tempo", "rate", "abstand_min", "abstand_max", "messungen", "baud")}}
    baud = int(q.get("baud", k.get("baud", 0)) or 0)
    if k.get("art") == "oszilloskop":
        n = k["messungen"]
        rate = k["scans"] / gesamt if gesamt else 1
        a, e = int(von * rate), max(int(von * rate) + 1, int(bis * rate))
        r = subprocess.run([MESSKERN, "A", os.path.join(d, "analog.bin"), str(n), str(a), str(e), str(breite)], capture_output=True)
        n2, br, _ = struct.unpack("<iii", r.stdout[:12])
        werte = struct.unpack("<%dH" % (n2 * br * 2), r.stdout[12:12 + n2 * br * 4])
        plaetze = {int(x): y for x, y in k["plaetze"].items()}
        antwort["kurven"] = kurven({"breite": br}, werte, k["aktiv"], k["d12"], k["d56"], plaetze, k.get("chip12"), k.get("gain", 1.0), k.get("null", 0.0))
        antwort["n_spalten"] = br
        tick0 = k.get("tick_start", 0)
        ereignisse = []
        with open(os.path.join(d, "digital.bin"), "rb") as f:
            daten = f.read()
        for i in range(0, len(daten) - 4, 5):
            t, p = struct.unpack_from("<IB", daten, i)
            ereignisse.append((((t - tick0 + 0x80000000) & 0xFFFFFFFF) - 0x80000000, p))
    else:
        # Aufnahme der Bus-Aufzeichnung: Spannungen zehnmal je Sekunde, Pegelwechsel aus pigpio
        spalten = {"K1": "J_Bus-", "K2": "J_Bus+", "K3": "J_Vsys+", "K4": "J_OnOff", "K5": "J_Alarm"}
        zeit, werte = [], {x: [] for x in spalten}
        with open(os.path.join(d, "spannung.csv")) as f:
            for z in csv.DictReader(f, delimiter=";"):
                t = float(z["zeit_s"])
                if von <= t <= bis:
                    zeit.append(t)
                    for x, y in spalten.items():
                        werte[x].append(float(z[y]))
        antwort["kurven"] = {x: in_mv([v for w in werte[x] for v in (w, w)]) for x in spalten} if zeit else {}
        antwort["n_spalten"] = len(zeit)
        tick0 = k.get("tick_start", 0)
        ereignisse = []
        with open(os.path.join(d, "flanken.bin"), "rb") as f:
            daten = f.read()
        for i in range(0, len(daten) - 11, 12):
            _, flags, t, lev = struct.unpack_from("<HHII", daten, i)
            if not flags:
                ereignisse.append((((t - tick0 + 0x80000000) & 0xFFFFFFFF) - 0x80000000, (lev >> GPIO_BUS & 1) | (lev >> GPIO_ALARM & 1) << 1))
        baud = baud or k.get("baud", 0)
    t_a, t_e = von * 1e6, bis * 1e6
    frueher = [p for t, p in ereignisse if t < t_a]
    start = frueher[-1] if frueher else (ereignisse[0][1] ^ 3 if ereignisse else 1)
    im = [(t - t_a, p) for t, p in ereignisse if t_a <= t <= t_e]
    s, w = spur(start, im, 0)
    antwort["bus"] = {"start": s, "w": w[:12000]}
    s2, w2 = spur(start, im, 1)
    antwort["alarm"] = {"start": s2, "w": w2[:6000]}
    if baud:
        antwort["bytes"] = [[round(t), v] for t, v in bytes_zerlegen(s, w, baud, t_e - t_a)]
    return antwort


def csv_ausgeben(handler, q):
    d = ordner_sicher(q.get("ordner"))
    k = json.load(open(os.path.join(d, "kopf.json")))
    handler.send_response(200)
    handler.send_header("Content-Type", "text/csv; charset=utf-8")
    handler.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(d)}.csv"')
    handler.end_headers()
    aus = handler.wfile
    if k.get("art") != "oszilloskop":
        with open(os.path.join(d, "spannung.csv"), "rb") as f:
            shutil.copyfileobj(f, aus)
        return
    n = k["messungen"]
    plaetze = {int(x): y for x, y in k["plaetze"].items()}
    kern_d = {"null": k.get("null", 0.0), "gain": k.get("gain", 1.0)}
    faktoren = [F13] * n
    namen = [f"Messung{i+1}" for i in range(n)]
    for ka, pl in plaetze.items():
        faktoren[pl] = KANAL[ka][3]
        namen[pl] = f"Kanal{ka}_{KANAL[ka][1]}"
    if k.get("chip12") is not None:
        namen[k["chip12"]] = "Klemme1_minus_Klemme2_Chip"
    aus.write(("zeit_s;" + ";".join(namen) + "\n").encode())
    rate = k["scans"] / k["dauer_s"] if k.get("dauer_s") else 1
    with open(os.path.join(d, "analog.bin"), "rb") as f:
        i = 0
        while True:
            b = f.read(2 * n * 4096)
            if not b:
                break
            w = struct.unpack("<%dH" % (len(b) // 2), b)
            zeilen = io.StringIO()
            for s in range(len(w) // n):
                zeilen.write(f"{i / rate:.6f}".replace(".", ","))
                for j in range(n):
                    zeilen.write(f";{spannung(w[s * n + j], faktoren[j], kern_d):.3f}".replace(".", ","))
                zeilen.write("\n")
                i += 1
            aus.write(zeilen.getvalue().encode())


def system_aktion(aktion):
    if aktion not in ("herunterfahren", "neustart"):
        return {"fehler": "unbekannt"}
    with kern.sperre:
        kern.stoppen()

    def spaeter():
        time.sleep(1.0)
        subprocess.run(["systemctl", "poweroff" if aktion == "herunterfahren" else "reboot"])
    threading.Thread(target=spaeter, daemon=True).start()
    return {"ok": True, "aktion": aktion}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def json_senden(self, obj, code=200):
        d = json.dumps(obj, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(d)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(d)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = {k: v[-1] for k, v in urllib.parse.parse_qs(url.query, keep_blank_values=True).items()}
        try:
            if url.path in ("/", "/index.html"):
                d = open(SEITE, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(d)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(d)
            elif url.path == "/api/status":
                self.json_senden(status())
            elif url.path == "/api/frame":
                self.json_senden(frame_liefern(q))
            elif url.path == "/api/aufnahmen":
                self.json_senden(aufnahmen())
            elif url.path == "/api/ansehen":
                self.json_senden(aufnahme_ansehen(q))
            elif url.path == "/api/csv":
                csv_ausgeben(self, q)
            else:
                self.send_error(404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            try:
                self.json_senden({"fehler": str(e)}, 500)
            except Exception:
                pass

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        q = {k: v[-1] for k, v in urllib.parse.parse_qs(url.query).items()}
        try:
            if url.path == "/api/aufnahme":
                self.json_senden(aufnahme_starten(q))
            elif url.path == "/api/system":
                self.json_senden(system_aktion(q.get("aktion", "")))
            else:
                self.send_error(404)
        except Exception as e:
            self.json_senden({"fehler": str(e)}, 500)


def main():
    os.makedirs(ZIEL, exist_ok=True)
    os.chown(ZIEL, 1000, 1000)
    digital.starten()
    threading.Thread(target=waechter, daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
