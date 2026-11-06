#!/usr/bin/env python3
# Robnet-Analyse: Aufzeichnung auf dem Raspberry. Version 00.01, Stand 06.11.2026.
# Speichert Pegelwechsel (Bus-Empfaenger, Alarm), Bytes der seriellen Schnittstelle und die
# Spannungen aller Adern in einen neuen Ordner. Nur lesen: Das Programm sendet nichts.
# Aufruf: python3 aufzeichnung_v00.01.py --baud 9600 --dauer 60 --stellung A
import argparse
import json
import os
import select
import signal
import struct
import subprocess
import termios
import threading
import time

import pigpio
import spidev

VERSION = "00.01"
GPIO_BUS = 23       # Raspberry-Pin 16, Ausgang des Bus-Empfaengers
GPIO_ALARM = 27     # Raspberry-Pin 13, Alarm Seite Hauptgeraet
VREF = 2.5
TEILER_13K = (100 + 13) / 13
TEILER_VSYS = (100 + 8.2) / 8.2
# (Spi-Weg, Kanal, Name, Faktor); Konzept, Abschnitt 2, Block 4
KANAELE = [
    (0, 0, "J_Bus+", TEILER_13K), (0, 1, "J_Bus-", TEILER_13K), (0, 2, "J_Vsys+", TEILER_VSYS),
    (0, 3, "J_OnOff", TEILER_13K), (0, 4, "J_Alarm", TEILER_13K), (0, 5, "Bordspannung", TEILER_13K),
    (1, 0, "B_Vsys+", TEILER_VSYS), (1, 1, "B_OnOff", TEILER_13K), (1, 2, "B_Alarm", TEILER_13K),
    (1, 3, "B_Bus+", TEILER_13K), (1, 4, "B_Bus-", TEILER_13K),
]
ANALOG_TAKT = 0.1   # Sekunden je Durchlauf
SICHERN_TAKT = 2.0  # Sekunden bis zum Sichern auf die Karte
BAUD = {1200: termios.B1200, 2400: termios.B2400, 4800: termios.B4800, 9600: termios.B9600,
        19200: termios.B19200, 38400: termios.B38400, 57600: termios.B57600,
        115200: termios.B115200, 230400: termios.B230400}

stopp = threading.Event()
fehler = []


def sichern(datei):
    datei.flush()
    os.fsync(datei.fileno())


def pigpiod_starten():
    # Laeuft der Dienst nicht, mit Abtastung alle 2 us starten
    if subprocess.run(["pgrep", "-x", "pigpiod"], capture_output=True).returncode != 0:
        subprocess.run(["sudo", "pigpiod", "-s", "2"], check=True)
    for _ in range(50):
        time.sleep(0.1)
        if subprocess.run(["sh", "-c", "ss -tln | grep -q :8888"]).returncode == 0:
            break
    probe = pigpio.pi()
    if not probe.connected:
        raise RuntimeError("pigpiod antwortet nicht")
    return probe


def flanken_lesen(pi, ordner, zaehler):
    griff = pi.notify_open()
    maske = (1 << GPIO_BUS) | (1 << GPIO_ALARM)
    with open(f"/dev/pigpio{griff}", "rb", buffering=0) as rohr, open(f"{ordner}/flanken.bin", "wb") as ziel:
        pi.notify_begin(griff, maske)
        letztes = time.monotonic()
        while not stopp.is_set():
            bereit, _, _ = select.select([rohr], [], [], 0.2)
            if bereit:
                daten = rohr.read(65536)
                ziel.write(daten)
                zaehler["flanken_byte"] += len(daten)
            if time.monotonic() - letztes > SICHERN_TAKT:
                sichern(ziel)
                letztes = time.monotonic()
        pi.notify_close(griff)
        sichern(ziel)


def seriell_lesen(ordner, baud, zaehler):
    fd = os.open("/dev/serial0", os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = 0
    a[1] = 0
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    a[3] = 0
    a[4] = a[5] = BAUD[baud]
    termios.tcsetattr(fd, termios.TCSANOW, a)
    termios.tcflush(fd, termios.TCIFLUSH)
    # Satzaufbau: Zeit in us seit Start (Q), Laenge (I), danach die Bytes
    with open(f"{ordner}/bytes.bin", "wb") as ziel:
        start = time.monotonic()
        letztes = start
        while not stopp.is_set():
            bereit, _, _ = select.select([fd], [], [], 0.2)
            if bereit:
                daten = os.read(fd, 4096)
                t = int((time.monotonic() - start) * 1e6)
                ziel.write(struct.pack("<QI", t, len(daten)) + daten)
                zaehler["seriell_byte"] += len(daten)
            if time.monotonic() - letztes > SICHERN_TAKT:
                sichern(ziel)
                letztes = time.monotonic()
        sichern(ziel)
    os.close(fd)


def analog_lesen(ordner, zaehler):
    spis = []
    for ce in (0, 1):
        s = spidev.SpiDev()
        s.open(0, ce)
        s.mode = 0
        s.max_speed_hz = 500000
        spis.append(s)
    with open(f"{ordner}/spannung.csv", "w") as ziel:
        ziel.write("zeit_s;" + ";".join(k[2] for k in KANAELE) + "\n")
        start = time.monotonic()
        naechste = start
        letztes = start
        while not stopp.is_set():
            werte = []
            for ce, kanal, _, faktor in KANAELE:
                a = spis[ce].xfer2([0x06 | (kanal >> 2), (kanal & 3) << 6, 0])
                werte.append(f"{((a[1] & 0x0F) << 8 | a[2]) * VREF / 4096 * faktor:.3f}")
            ziel.write(f"{time.monotonic() - start:.3f};" + ";".join(werte) + "\n")
            zaehler["analog_zeilen"] += 1
            if time.monotonic() - letztes > SICHERN_TAKT:
                sichern(ziel)
                letztes = time.monotonic()
            naechste += ANALOG_TAKT
            stopp.wait(max(0, naechste - time.monotonic()))
        sichern(ziel)
    for s in spis:
        s.close()


def absichern(ziel, *args):
    def lauf():
        try:
            ziel(*args)
        except Exception as e:
            fehler.append(f"{ziel.__name__}: {e}")
            stopp.set()
    return lauf


def main():
    p = argparse.ArgumentParser(description="Robnet-Aufzeichnung, sendet nichts")
    p.add_argument("--baud", type=int, default=9600, choices=sorted(BAUD))
    p.add_argument("--dauer", type=float, default=0, help="Sekunden, 0 = bis zum Abbruch")
    p.add_argument("--stellung", default="A", help="Stellung JP1/JP2, nur als Notiz")
    p.add_argument("--notiz", default="")
    p.add_argument("--ziel", default=os.path.expanduser("~/aufzeichnungen"))
    a = p.parse_args()
    ordner = os.path.join(a.ziel, time.strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(ordner)
    signal.signal(signal.SIGTERM, lambda *_: stopp.set())
    signal.signal(signal.SIGINT, lambda *_: stopp.set())

    pi = pigpiod_starten()
    for g in (GPIO_BUS, GPIO_ALARM):
        pi.set_pull_up_down(g, pigpio.PUD_OFF)
    zaehler = {"flanken_byte": 0, "seriell_byte": 0, "analog_zeilen": 0}
    start = {"version": VERSION, "start": time.strftime("%Y-%m-%d %H:%M:%S %z"), "baud": a.baud,
             "stellung": a.stellung, "notiz": a.notiz, "gpio_bus": GPIO_BUS, "gpio_alarm": GPIO_ALARM,
             "tick_start": pi.get_current_tick(), "pegel_bus_start": pi.read(GPIO_BUS)}
    with open(f"{ordner}/kopf.json", "w") as f:
        json.dump(start, f, indent=1)

    faeden = [threading.Thread(target=absichern(flanken_lesen, pi, ordner, zaehler)),
              threading.Thread(target=absichern(seriell_lesen, ordner, a.baud, zaehler)),
              threading.Thread(target=absichern(analog_lesen, ordner, zaehler))]
    for t in faeden:
        t.start()
    beginn = time.monotonic()
    print(f"Aufzeichnung laeuft: {ordner}", flush=True)
    while not stopp.is_set():
        if a.dauer and time.monotonic() - beginn >= a.dauer:
            stopp.set()
        stopp.wait(0.2)
    for t in faeden:
        t.join()
    pi.stop()
    start["dauer_s"] = round(time.monotonic() - beginn, 3)
    start.update(zaehler)
    start["fehler"] = fehler
    with open(f"{ordner}/kopf.json", "w") as f:
        json.dump(start, f, indent=1)
    print(json.dumps(start, indent=1))
    raise SystemExit(1 if fehler else 0)


if __name__ == "__main__":
    main()
