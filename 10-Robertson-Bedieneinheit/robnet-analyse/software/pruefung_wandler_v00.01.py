#!/usr/bin/env python3
# Robnet-Analyse, Linie B: Prueft beide MCP3208. Version 00.01, Stand 06.11.2026.
# Liest jeden Kanal mehrfach und zeigt Rohwert, Spannung am Wandler und Spannung an der Ader.
# Nur lesen: Das Programm sendet nichts auf den Robnet-Bus.
import spidev

VREF = 2.5
MITTELN = 32
TEILER_13K = (100 + 13) / 13
TEILER_VSYS = (100 + 8.2) / 8.2

# (Name, Faktor von der Spannung am Wandler zur Spannung an der Ader); Konzept, Abschnitt 2, Block 4
KANAELE = {
    0: ("Oberer Sockel (U2, Seite J300)", [
        ("Bus+", TEILER_13K), ("Bus-", TEILER_13K), ("Vsys+", TEILER_VSYS), ("On-Off", TEILER_13K),
        ("Alarm", TEILER_13K), ("Bordspannung", TEILER_13K), ("frei", None), ("frei", None)]),
    1: ("Unterer Sockel (U6, Seite Bedieneinheit)", [
        ("Vsys+", TEILER_VSYS), ("On-Off", TEILER_13K), ("Alarm", TEILER_13K), ("Bus+", TEILER_13K),
        ("Bus-", TEILER_13K), ("frei", None), ("frei", None), ("frei", None)]),
}


def lesen(spi, kanal):
    # MCP3208: Startbit, Einzelkanal, drei Kanalbits; Antwort 12 Bit
    antwort = spi.xfer2([0x06 | (kanal >> 2), (kanal & 3) << 6, 0])
    return ((antwort[1] & 0x0F) << 8) | antwort[2]


def main():
    for ce, (titel, kanaele) in KANAELE.items():
        spi = spidev.SpiDev()
        spi.open(0, ce)
        spi.mode = 0
        spi.max_speed_hz = 500000
        print(titel)
        print("  CH  Rohwert  am Wandler  an der Ader  Name")
        for kanal, (name, faktor) in enumerate(kanaele):
            werte = [lesen(spi, kanal) for _ in range(MITTELN)]
            roh = sum(werte) / MITTELN
            volt = roh * VREF / 4096
            ader = f"{volt * faktor:8.2f} V" if faktor else "        -"
            print(f"  {kanal}  {roh:7.1f}  {volt:8.3f} V  {ader}   {name}"
                  f"  (Streuung {max(werte) - min(werte)})")
        spi.close()
        print()


if __name__ == "__main__":
    main()
