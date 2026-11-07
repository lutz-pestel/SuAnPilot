#!/usr/bin/env python3
# Robnet-Analyse: Nimmt die Werte fuer die Kalibrierung auf. Version 00.01, Stand 07.11.2026.
# Laeuft auf dem Raspberry neben der Oberflaeche und fragt sie ab, bis die Zeit um ist oder die Datei STOPP existiert.
# Misst auf jeder Geschwindigkeit alle 5 Kanaele; die Auswertung erkennt selbst, welche Klemme auf 12 V lag.
# Allein oder zu fuenft gemessen lag Kanal 1 hoechstens 5 mV auseinander (07.11.2026).
# Aufnehmen: python3 kalibrieren_v00.01.py <Sekunden>. Ergebnis: ~/kalibrierung/messung.jsonl
# Dabei je Klemme von J1 das Kabel 20 s an die Bezugsspannung halten, dann 20 s an GND; JP2 ohne Bruecken.
# Auswerten: sudo python3 kalibrieren_v00.01.py auswerten <Bezugsspannung in V>. Schreibt ZIEL; danach Dienst neu starten.
import json
import os
import statistics
import sys
import time
import urllib.request

ORT = os.path.expanduser("~/kalibrierung")
STOPP = os.path.join(ORT, "STOPP")
ZIEL = "/var/lib/robnet/kalibrierung.json"
QUELLE = "/home/pi/kalibrierung"
TEILER = (800, 200, 100, 56)
AUSWAHL = "1,2,3,4,5"


def bild(teiler):
    u = (f"http://localhost/api/frame?tempo={teiler}&k={AUSWAHL}&d12=aus&d56=aus&baud=0&tdiv=0.002&vor=0&breite=200"
         "&trig=keine&flanke=1&pegel=1&modus=auto&bus=0&alarm=0")
    return json.load(urllib.request.urlopen(u, timeout=20))


def auswerten(bezug):
    """Sucht je Kanal den letzten Abschnitt mit Bezugsspannung und die Zeit danach an GND."""
    z = []
    for n in sorted(os.listdir(QUELLE)):
        if n.endswith(".jsonl"):
            with open(os.path.join(QUELLE, n)) as f:
                z += [json.loads(x) for x in f]
    z = sorted((a for a in z if a["auswahl"] == AUSWAHL), key=lambda a: a["t"])
    kanaele = {}
    for ka in ("K1", "K2", "K3", "K4", "K5"):
        hoch = [a["t"] for a in z if a[ka][1] > 9000]
        if not hoch:
            print(ka, "keine Bezugsspannung gefunden")
            continue
        t2 = t1 = hoch[-1]
        for t in reversed(hoch):
            if t1 - t > 3:
                break
            t1 = t
        kanaele[ka] = {}
        for teiler in TEILER:
            h = [a[ka][0] for a in z if a["teiler"] == teiler and t1 + 0.5 < a["t"] < t2 - 0.5 and a[ka][1] > 9000]
            g = [a[ka][0] for a in z if a["teiler"] == teiler and t2 + 3 < a["t"] < t2 + 15 and a[ka][2] < 1500]
            if h and g:
                kanaele[ka][str(teiler)] = [round(statistics.median(h)), round(statistics.median(g))]
    ergebnis = {"version": "00.01", "datum": time.strftime("%d.%m.%Y"), "bezug_v": bezug, "werte": "Kanal, Teiler: Anzeige in mV an Bezugsspannung und an GND", "kanaele": kanaele}
    with open(ZIEL, "w") as f:
        json.dump(ergebnis, f, indent=1)
    print(json.dumps(ergebnis))


def main():
    if sys.argv[1] == "auswerten":
        auswerten(float(sys.argv[2]))
        return
    dauer = float(sys.argv[1])
    os.makedirs(ORT, exist_ok=True)
    if os.path.exists(STOPP):
        os.remove(STOPP)
    ende = time.time() + dauer
    with open(os.path.join(ORT, "messung.jsonl"), "a") as f:
        while time.time() < ende and not os.path.exists(STOPP):
            for teiler in TEILER:
                d = bild(teiler)
                z = {"t": round(time.time(), 2), "teiler": teiler, "auswahl": AUSWAHL, "rate": round(d.get("rate_gesamt", 0))}
                for k, w in d.get("kurven", {}).items():
                    z[k] = [round(sum(w) / len(w)), min(w), max(w)]  # Mittel, kleinster, groesster Wert in mV
                f.write(json.dumps(z) + "\n")
                f.flush()
    print("fertig")


if __name__ == "__main__":
    main()
