#!/usr/bin/env python3
# Robnet-Analyse: Erzeugt das Handbuch. Version 00.01, Stand 07.11.2026.
# Eingabe: handbuch_quelle_v00.01.html mit Platzhaltern <!--skizze:X-->. Ausgabe: ../handbuch_v00.01.html.
# Die Skizzen zeigen die Platine von oben; alle Lagen stammen aus smd/kicad/v00.01/Robnet-Analyse.kicad_pcb.
import os
import re

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "handbuch_quelle_v00.01.html")
ZIEL = os.path.join(HIER, "..", "handbuch_v00.01.html")

M = 7.0        # Bildpunkte je Millimeter
RAND_O = 18.0  # Platz oberhalb der Platine in mm, fuer die Beschriftung der Kabel
RAND_U = 15.0
RAND_S = 2.0
J1_X = {1: 87.4, 2: 82.32, 3: 77.24, 4: 72.16, 5: 67.08, 6: 62.0}
J3_X = {1: 62.0, 2: 67.08, 3: 72.16, 4: 77.24, 5: 82.32, 6: 87.4}
NAME = {1: "Bus−", 2: "Bus+", 3: "Vsys+", 4: "Masse", 5: "On-Off", 6: "Alarm"}
TRENN = {"JP3": 82.32, "JP4": 87.4, "JP5": 77.24, "JP6": 67.08, "JP7": 62.0}
ALLE = ("JP3", "JP4", "JP5", "JP6", "JP7")

GOLD = "#f2b632"
ROT = "#ff5a4f"
SILK = "#f4f7f2"
PIN = "#d7dde0"
PLATTE = "#1d4a35"
GRAU = "#c9cfcb"
DUNKEL = "#262b2a"


def x(mm):
    return round((mm + RAND_S) * M, 1)


def y(mm):
    return round((mm + RAND_O) * M, 1)


def l(mm):
    return round(mm * M, 1)


def text(xm, ym, t, gr=2.0, anker="middle", farbe=SILK, fett=False):
    t = t.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x(xm)}" y="{y(ym)}" font-size="{l(gr)}" text-anchor="{anker}" fill="{farbe}"{" font-weight=\"700\"" if fett else ""}>{t}</text>'


def rechteck(x1, y1, x2, y2, fuell, rand="none", r=0.4, breite=1):
    return f'<rect x="{x(x1)}" y="{y(y1)}" width="{l(x2 - x1)}" height="{l(y2 - y1)}" rx="{l(r)}" fill="{fuell}" stroke="{rand}" stroke-width="{breite}"/>'


def stift(xm, ym):
    return rechteck(xm - 0.55, ym - 0.55, xm + 0.55, ym + 0.55, PIN, r=0.1)


def bruecke(x1, y1, x2, y2):
    return rechteck(min(x1, x2) - 1.05, min(y1, y2) - 1.05, max(x1, x2) + 1.05, max(y1, y2) + 1.05, GOLD, "#7a5500", r=0.5)


def ring(xm, ym, rx=2.2, ry=3.5, farbe=ROT):
    return f'<ellipse cx="{x(xm)}" cy="{y(ym)}" rx="{l(rx)}" ry="{l(ry)}" fill="none" stroke="{farbe}" stroke-width="3"/>'


def grund():
    a = [rechteck(0, 0, 100, 100, PLATTE, r=0.8)]
    for hx, hy in ((3.8, 3.8), (96.2, 3.8), (3.8, 96.2), (96.2, 96.2)):
        a.append(f'<circle cx="{x(hx)}" cy="{y(hy)}" r="{l(1.6)}" fill="#e8eaf2"/>')
    # Raspberry, Fassungen, Regler
    a.append(rechteck(0.6, 26.5, 30.6, 92.5, GRAU, "#8d9490", r=2.5))
    a.append(text(15.6, 57, "Raspberry Pi", 3.0, farbe="#1a1d21", fett=True))
    a.append(text(15.6, 61, "Zero 2 W (J5)", 2.4, farbe="#1a1d21"))
    a.append(text(15.6, 65, "kopfüber", 2.2, farbe="#1a1d21"))
    for name, x1, y1, x2, y2 in (("U2", 35.9, 31.3, 45.4, 50.9), ("U6", 35.9, 65.3, 45.4, 84.9), ("U1", 64.3, 68.3, 73.7, 77.7)):
        a.append(rechteck(x1, y1, x2, y2, "#14351f", SILK))
        a.append(rechteck(x1 + 1.9, y1 + 0.9, x2 - 1.9, y2 - 0.9, DUNKEL))
        a.append(text((x1 + x2) / 2, (y1 + y2) / 2 + 0.8, name, 2.3))
    a.append(rechteck(43.6, 3.4, 55.0, 12.2, DUNKEL))
    a.append(text(49.3, 8.6, "U3 5 V", 2.2))
    a.append(text(39.4, 53.0, "Wandler", 1.9))
    a.append(text(39.4, 87.0, "Wandler", 1.9))
    a.append(text(69, 80.0, "Empfänger", 1.9))
    # Klemmleisten
    a.append(rechteck(58.2, 0, 91.2, 12.4, GRAU, "#8d9490"))
    a.append(rechteck(58.2, 87.6, 91.2, 100, GRAU, "#8d9490"))
    a.append(rechteck(11.2, 0, 23.7, 12.4, GRAU, "#8d9490"))
    for n in range(1, 7):
        a.append(text(J1_X[n], 8, str(n), 3.1, farbe="#1a1d21", fett=True))
        a.append(text(J3_X[n], 96, str(n), 3.1, farbe="#1a1d21", fett=True))
        a.append(text(J1_X[n], 14.4 if n % 2 else 16.6, NAME[n], 1.9))
        a.append(text(J3_X[n], 83.6 if n % 2 else 85.8, NAME[n], 1.9))
    a.append(text(20, 8, "+", 3.4, farbe="#1a1d21", fett=True))
    a.append(text(14.92, 8, "−", 3.4, farbe="#1a1d21", fett=True))
    a.append(text(17.46, 15.0, "J2 12 V", 2.1))
    a.append(text(52.5, 15.0, "J1", 2.8, fett=True))
    a.append(text(52.5, 92, "J3", 2.8, fett=True))
    # Stiftleiste J4
    for i in range(3):
        a.append(stift(95, 57 + i * 2.54))
    a.append(text(95, 54.6, "J4", 2.1))
    return a


def jumper_bild(gesteckt, jp2, jp1, markiert):
    """gesteckt: Trenn-Jumper mit Bruecke; jp2/jp1: 'oben', 'unten' oder None."""
    a = []
    for name, xm in TRENN.items():
        a.append(stift(xm, 19.5))
        a.append(stift(xm, 22.04))
        if name in gesteckt:
            a.append(bruecke(xm, 19.5, xm, 22.04))
        a.append(text(xm, 26.2, name, 1.9))
        if name in markiert:
            a.append(ring(xm, 20.77))
    for name, y0, stand in (("JP2", 37.0, jp2), ("JP1", 48.5, jp1)):
        for s in (68.0, 70.54):
            for r in range(3):
                a.append(stift(s, y0 + r * 2.54))
            if stand == "oben":
                a.append(bruecke(s, y0, s, y0 + 2.54))
            elif stand == "unten":
                a.append(bruecke(s, y0 + 2.54, s, y0 + 5.08))
        a.append(text(64.2, y0 + 3.3, name, 2.1, "end", fett=True))
        if name in markiert:
            a.append(ring(69.27, y0 + 2.54, 3.6, 4.9))
    a.append(text(73.1, 37.7, "J1", 1.7, "start"))
    a.append(text(73.1, 42.8, "J3", 1.7, "start"))
    a.append(text(73.1, 49.2, "normal", 1.7, "start"))
    a.append(text(73.1, 54.3, "getauscht", 1.7, "start"))
    return a


def kabel(xm, oben, zeile, farbe="#7fd1ff", anker="middle"):
    """Beschriftung ausserhalb der Platine mit Pfeil zur Klemmleiste."""
    ya, yb = (-3.2, -0.1) if oben else (103.2, 100.1)
    yt = -5.0 if oben else 106.5
    a = [f'<line x1="{x(xm)}" y1="{y(ya)}" x2="{x(xm)}" y2="{y(yb)}" stroke="{farbe}" stroke-width="3"/>']
    zeilen = zeile.split("|")
    for i, t in enumerate(zeilen):
        ys = yt - (len(zeilen) - 1 - i) * 3.0 if oben else yt + i * 3.0
        a.append(text(xm, ys, t, 2.3, anker, farbe, True))
    return a


def bild(teile, titel):
    b, h = l(100 + 2 * RAND_S), l(100 + RAND_O + RAND_U)
    inhalt = "".join(teile)
    return (f'<svg class="skizze" viewBox="0 0 {b} {h}" role="img" aria-label="{titel}" font-family="Segoe UI, Arial, sans-serif">'
            f'<rect width="{b}" height="{h}" fill="#101412" rx="8"/>{inhalt}</svg>')


STANDARD = {"j1": "Hauptgerät J300", "j3": "Bedieneinheit", "j2": "+12 V Bord"}


def fall(titel, gesteckt=ALLE, jp2="oben", jp1="oben", markiert=(), j1=STANDARD["j1"], j3=STANDARD["j3"], j2=STANDARD["j2"]):
    t = grund() + jumper_bild(gesteckt, jp2, jp1, markiert)
    t.append(text(0.5, -13.0, titel.replace("Skizze ", "").replace(":", " ", 1), 3.6, "start", "#ffffff", True))
    t += kabel(74.7, True, j1)
    t += kabel(17.46, True, j2, "#ffb36b")
    if j3:
        t += kabel(74.7, False, j3)
    return bild(t, titel)


def uebersicht():
    t = grund() + jumper_bild(ALLE, "oben", "oben", ())
    t.append(text(0.5, -13.0, "P  Platine, Grundstellung", 3.6, "start", "#ffffff", True))
    gelb = "#ffe27a"
    for xt, yt, s in ((35.6, 21.0, "Trenn-Jumper JP3–JP7"), ):
        t.append(text(xt, yt, s, 2.2, "middle", gelb, True))
    t.append(text(95, 69.0, "Messpunkte", 1.9, farbe=gelb))
    t.append(text(95, 71.6, "Bus+ Bus− Masse", 1.5, farbe=gelb))
    t.append(text(82, 44, "Stellungs-", 1.9, "start", gelb))
    t.append(text(82, 46.5, "Tabelle A–E", 1.9, "start", gelb))
    t.append(text(82, 49, "ist aufgedruckt", 1.9, "start", gelb))
    t += kabel(74.7, True, "J1: Kabel zum Hauptgerät J300")
    t += kabel(17.46, True, "J2: Versorgung 12 V", "#ffb36b")
    t += kabel(74.7, False, "J3: Bedieneinheit AP300CX")
    return bild(t, "Platine von oben, Grundstellung")


SKIZZEN = {
    "P": uebersicht,
    "A": lambda: fall("Skizze A: Bus mithören"),
    "B": lambda: fall("Skizze B: Bus, Adern getauscht", jp1="unten", markiert=("JP1",)),
    "C": lambda: fall("Skizze C: Bedieneinheit allein", gesteckt=("JP5", "JP6", "JP7"), jp2="unten", markiert=("JP2", "JP3", "JP4")),
    "D": lambda: fall("Skizze D: Bedieneinheit allein, getauscht", gesteckt=("JP5", "JP6", "JP7"), jp2="unten", jp1="unten", markiert=("JP1", "JP2", "JP3", "JP4")),
    "E": lambda: fall("Skizze E: Empfänger getrennt", jp2=None, markiert=("JP2",)),
    "F": lambda: fall("Skizze F: Hauptgerät allein", gesteckt=("JP5", "JP6", "JP7"), markiert=("JP3", "JP4")),
    "G": lambda: fall("Skizze G: Trennversuch Vsys+", gesteckt=("JP3", "JP4", "JP6", "JP7"), markiert=("JP5",)),
    "H": lambda: fall("Skizze H: Trennversuch On-Off", gesteckt=("JP3", "JP4", "JP5", "JP7"), markiert=("JP6",)),
    "I": lambda: fall("Skizze I: Trennversuch Alarm", gesteckt=("JP3", "JP4", "JP5", "JP6"), markiert=("JP7",)),
    "K": lambda: fall("Skizze K: Spannung messen", gesteckt=(), jp2=None, markiert=("JP2",) + ALLE, j1="Messleitungen an 1, 2, 3, 5, 6|Masse der Quelle an 4", j3="J3 frei lassen", j2="+12 V"),
    "L": lambda: fall("Skizze L: Serielles Signal", gesteckt=(), markiert=ALLE, j1="Klemme 2 = Plus, Klemme 1 = Minus|Masse der Quelle an 4", j3="J3 frei lassen", j2="+12 V"),
    "M": lambda: fall("Skizze M: NMEA 0183 lesen", gesteckt=(), markiert=ALLE, j1="NMEA A(+) an 2, NMEA B(−) an 1|Masse der Quelle an 4", j3="J3 frei lassen", j2="+12 V"),
    "S": lambda: open(os.path.join(HIER, "..", "adern_v00.01.svg"), encoding="utf-8").read().replace('xmlns="http://www.w3.org/2000/svg" ', ""),
    "N": lambda: fall("Skizze N: Testsender", gesteckt=(), markiert=ALLE, j1="YL-12B: Y an 2, Z an 1|GND an 4 (nötig!)", j3="J3 frei lassen", j2="+12 V"),
}


LAGEN = {
    "T": (ALLE, (56.5, 0, 93.0, 28.0), "Die Trenn-Jumper <b>JP3 bis JP7</b> unter der Klemmleiste J1 (rot umkreist)."),
    "2": (("JP2",), (59.0, 33.0, 85.0, 57.0), "<b>JP2</b>, die obere der beiden Stiftgruppen in der Mitte rechts (rot umkreist)."),
    "1": (("JP1",), (59.0, 33.0, 85.0, 57.0), "<b>JP1</b>, die untere der beiden Stiftgruppen in der Mitte rechts (rot umkreist)."),
    "W": (("JP1", "JP2"), (59.0, 33.0, 85.0, 57.0), "<b>JP2</b> (oben) und <b>JP1</b> (unten) in der Mitte rechts (rot umkreist)."),
}
ZIEL_LAGE = {"T": "jp-trenn", "2": "jp2", "1": "jp1", "W": "jumper"}


def lage(art):
    """Ausschnitt der Platine in Grundstellung mit markierten Jumpern, dazu Links in den Hardware-Teil."""
    markiert, (x1, y1, x2, y2), satz = LAGEN[art]
    inhalt = "".join(grund() + jumper_bild(ALLE, "oben", "oben", markiert))
    svg = (f'<svg class="skizze" viewBox="{x(x1)} {y(y1)} {l(x2 - x1)} {l(y2 - y1)}" role="img" aria-label="Lage der Jumper" '
           f'font-family="Segoe UI, Arial, sans-serif">{inhalt}</svg>')
    return (f'<figure class="lage">{svg}<figcaption>{satz} <a href="#{ZIEL_LAGE[art]}">Erklärung</a>, '
            f'<a href="#skizze-P">ganze Platine</a></figcaption></figure>')


def jumper_verlinken(t):
    """Macht in Fliesstext und Tabellen aus jeder Erwaehnung eines Jumpers einen Link in den Hardware-Teil."""
    aus, tiefe = [], {"a": 0, "svg": 0, "style": 0, "title": 0, "h1": 0, "h2": 0, "h3": 0, "h4": 0, "th": 0, "code": 0, "figcaption": 0}

    def ziel(n):
        return {"1": "jp1", "2": "jp2"}.get(n, "jp-trenn")

    def text_ersetzen(s):
        s = re.sub(r"JP3 bis JP7", '<a href="#jp-trenn">JP3 bis JP7</a>', s)
        s = re.sub(r"Trenn-Jumper", '<a href="#jp-trenn">Trenn-Jumper</a>', s)
        teile = re.split(r"(<a href=[^>]*>.*?</a>)", s)
        for i in range(0, len(teile), 2):
            teile[i] = re.sub(r"\bJP([1-7])\b", lambda m: f'<a href="#{ziel(m.group(1))}">JP{m.group(1)}</a>', teile[i])
            teile[i] = re.sub(r"\bJumper\b(?! auf 5 V)", '<a href="#jumper">Jumper</a>', teile[i])
        return "".join(teile)

    for stueck in re.split(r"(<[^>]+>)", t):
        m = re.fullmatch(r"<(/?)(\w+)[^>]*?(/?)>", stueck)
        if m:
            name = m.group(2).lower()
            if name in tiefe and not m.group(3):
                tiefe[name] += -1 if m.group(1) else 1
            aus.append(stueck)
        elif stueck.startswith("<") or any(tiefe.values()):
            aus.append(stueck)
        else:
            aus.append(text_ersetzen(stueck))
    return "".join(aus)


def main():
    t = open(QUELLE, encoding="utf-8").read()
    t = re.sub(r"<!--lage:(\w)-->", lambda m: lage(m.group(1)), t)
    t = jumper_verlinken(t)
    genutzt = set(re.findall(r"<!--skizze:(\w)-->", t))
    assert genutzt == set(SKIZZEN), genutzt ^ set(SKIZZEN)
    t = re.sub(r"<!--skizze:(\w)-->", lambda m: SKIZZEN[m.group(1)](), t)
    open(ZIEL, "w", encoding="utf-8", newline="\n").write(t)
    print("erzeugt", os.path.normpath(ZIEL), t.count("\n") + 1, "Zeilen", len(t) // 1024, "kB")


if __name__ == "__main__":
    main()
