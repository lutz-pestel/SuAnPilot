#!/usr/bin/env python3
# Robnet-Analyse: Wertet einen Aufzeichnungsordner aus. Version 00.01, Stand 06.11.2026.
# Bestimmt aus den Pegelwechseln die Bitdauer, zerlegt die Bytes (8 Datenbits, ohne Paritaet, 1 Stopbit)
# und vergleicht sie mit der seriellen Schnittstelle. Aufruf: python3 auswertung_v00.01.py <Ordner>
import collections
import json
import os
import struct
import sys

STANDARD = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400]


def flanken_laden(ordner, gpio):
    kopf = json.load(open(os.path.join(ordner, "kopf.json")))
    daten = open(os.path.join(ordner, "flanken.bin"), "rb").read()
    wechsel, luecken, letzte_seq, letzter = [], 0, None, kopf["pegel_bus_start"]
    tick_alt, hoch = None, 0
    for i in range(0, len(daten) - 11, 12):
        seq, flags, tick, pegel = struct.unpack_from("<HHII", daten, i)
        if letzte_seq is not None and seq != (letzte_seq + 1) & 0xFFFF:
            luecken += 1
        letzte_seq = seq
        if flags:
            continue
        if tick_alt is not None and tick < tick_alt:
            hoch += 1
        tick_alt = tick
        wert = (pegel >> gpio) & 1
        if wert != letzter:
            wechsel.append((tick + (hoch << 32), wert))
            letzter = wert
    return kopf, wechsel, luecken


def bitdauer(wechsel):
    laengen = [b[0] - a[0] for a, b in zip(wechsel, wechsel[1:]) if b[0] > a[0]]
    if not laengen:
        return None, None
    haeufig = collections.Counter(round(x) for x in laengen)
    kurz = min(k for k, v in haeufig.items() if v >= max(2, len(laengen) // 1000))
    baud = 1e6 / kurz
    return kurz, min(STANDARD, key=lambda s: abs(s - baud))


def zerlegen(wechsel, baud):
    # Ruhepegel hoch, Start niedrig; Abtastung in Bitmitte
    bit = 1e6 / baud
    ergebnis, falsch = bytearray(), 0
    i, n = 0, len(wechsel)

    def pegel_zu(t, von):
        j = von
        while j + 1 < n and wechsel[j + 1][0] <= t:
            j += 1
        return wechsel[j][1], j

    while i < n:
        t0, wert = wechsel[i]
        if wert != 0:
            i += 1
            continue
        byte, j = 0, i
        for b in range(8):
            w, j = pegel_zu(t0 + bit * (1.5 + b), j)
            byte |= w << b
        stop, j = pegel_zu(t0 + bit * 9.5, j)
        if stop == 1:
            ergebnis.append(byte)
        else:
            falsch += 1
        ende = t0 + bit * 9.5
        i = j
        while i < n and not (wechsel[i][1] == 0 and wechsel[i][0] > ende):
            i += 1
    return bytes(ergebnis), falsch


def seriell_laden(ordner):
    daten = open(os.path.join(ordner, "bytes.bin"), "rb").read()
    ziel, i = bytearray(), 0
    while i + 12 <= len(daten):
        _, laenge = struct.unpack_from("<QI", daten, i)
        ziel += daten[i + 12:i + 12 + laenge]
        i += 12 + laenge
    return bytes(ziel)


def main():
    ordner = sys.argv[1]
    kopf, wechsel, luecken = flanken_laden(ordner, kopf_gpio(ordner))
    seriell = seriell_laden(ordner)
    kurz, baud = bitdauer(wechsel)
    print(f"Ordner: {ordner}")
    print(f"Dauer {kopf.get('dauer_s')} s, Baud eingestellt {kopf['baud']}, Stellung {kopf['stellung']}, Fehler {kopf.get('fehler')}")
    print(f"Pegelwechsel: {len(wechsel)}, verlorene Meldungen: {luecken}")
    print(f"Serielle Bytes: {len(seriell)}")
    if baud:
        roh, falsch = zerlegen(wechsel, baud)
        print(f"Kuerzester Puls: {kurz} us, also etwa {baud} Baud")
        print(f"Aus Pegelwechseln zerlegt: {len(roh)} Byte, ohne gueltiges Stopbit: {falsch}")
        print(f"Stimmt mit seriell ueberein: {roh == seriell}")
        print(f"Anfang (hex): {roh[:32].hex(' ')}")
    return 0


def kopf_gpio(ordner):
    return json.load(open(os.path.join(ordner, "kopf.json")))["gpio_bus"]


if __name__ == "__main__":
    raise SystemExit(main())
