#!/usr/bin/env python3
# Robnet-Analyse: Haelt den Raspberry im Netz erreichbar. Version 00.01, Stand 07.11.2026.
# Anforderungen: anforderungen_oszilloskop.md, Abschnitt 7. Dienst robnet-netz, laeuft getrennt von der
# Oberflaeche, damit ein Fehler dort die Erreichbarkeit nicht kostet. Das Einbuchen beim Start und nach
# einem Ausfall erledigt der NetworkManager selbst (autoconnect, zuletzt erfolgreiches Netz zuerst).
# Dieser Dienst startet den eigenen Zugangspunkt und fuehrt die Wechsel aus, die der Nutzer anordnet.
# Passwoerter stehen nur in den Profilen des NetworkManager und in AP_PASSWORT, nie im Quelltext.
import json
import os
import re
import secrets
import subprocess
import time
import uuid

ORDNER = "/run/robnet-netz"
STATUS = ORDNER + "/status.json"
BEFEHLE = ORDNER + "/befehle"
SPEICHER = "/var/lib/robnet/netze.json"
AP_PASSWORT = "/var/lib/robnet/ap_passwort"
PROFILE = "/etc/NetworkManager/system-connections"
AP_PROFIL = "robnet-ap"
AP_NAME = "robnet"
AP_IP = "192.168.4.1"
WARTEN = 60    # Sekunden ohne Netz bis zum eigenen Zugangspunkt, beim Start und nach einem Ausfall
VERSUCH = 45   # Sekunden je Verbindungsversuch
WLAN = "802-11-wireless"

speicher = {"letzte_gute": None, "netze": {}}
sicht = []
meldung = ""


def nm(*args, zeit=20):
    try:
        r = subprocess.run(["nmcli", *args], capture_output=True, text=True, timeout=zeit)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return 1, ""


def felder(zeile):
    return [x.replace("\\:", ":") for x in re.split(r"(?<!\\):", zeile)]


def laden():
    global speicher
    try:
        with open(SPEICHER) as f:
            speicher = json.load(f)
    except (OSError, ValueError):
        pass


def sichern():
    with open(SPEICHER + ".neu", "w") as f:
        json.dump(speicher, f, indent=1)
    os.replace(SPEICHER + ".neu", SPEICHER)


def profile():
    """Alle gespeicherten WLAN-Profile ausser dem eigenen Zugangspunkt: Profilname -> Netzname."""
    aus = {}
    for z in nm("-t", "-f", "NAME,TYPE", "con", "show")[1].splitlines():
        f = felder(z)
        if len(f) == 2 and f[1] == WLAN and f[0] != AP_PROFIL:
            aus[f[0]] = nm("-g", WLAN + ".ssid", "con", "show", "id", f[0])[1].strip().replace("\\:", ":")
    return aus


def aktiv():
    """(Profil, Geraet) der aktiven WLAN-Verbindung oder (None, None)."""
    for z in nm("-t", "-f", "NAME,TYPE,DEVICE,STATE", "con", "show", "--active")[1].splitlines():
        f = felder(z)
        if len(f) == 4 and f[1] == WLAN and f[3] == "activated":
            return f[0], f[2]
    return None, None


def adressen(geraet):
    """(eigene Adresse, Adresse des Zugangspunkts)."""
    ip = gw = ""
    for z in nm("-t", "-f", "IP4.ADDRESS,IP4.GATEWAY", "device", "show", geraet)[1].splitlines():
        f = felder(z)
        if f[0].startswith("IP4.ADDRESS") and not ip:
            ip = f[1].split("/")[0]
        elif f[0] == "IP4.GATEWAY":
            gw = f[1]
    return ip, gw


def funkgeraet():
    """Steckt ein WLAN-Stick, wird er genommen, sonst das eingebaute WLAN."""
    alle = [felder(z)[0] for z in nm("-t", "-f", "DEVICE,TYPE", "device")[1].splitlines() if felder(z)[1:] == ["wifi"]]
    stick = [g for g in alle if g != "wlan0"]
    return stick[0] if stick else (alle[0] if alle else "wlan0")


def status(modus=None):
    p, g = aktiv()
    ip, gw = adressen(g) if g else ("", "")
    if modus is None:
        modus = "eigener_ap" if p == AP_PROFIL else "verbunden" if p else "sucht"
    alle = profile()
    netze = [{"profil": n, "ssid": s, "aktiv": n == p,
              "zuletzt_ok": speicher["netze"].get(n, {}).get("zuletzt_ok"),
              "vorgemerkt": speicher["netze"].get(n, {}).get("vorgemerkt", False)} for n, s in alle.items()]
    netze.sort(key=lambda x: -(x["zuletzt_ok"] or 0))
    d = {"modus": modus, "ssid": AP_NAME if p == AP_PROFIL else alle.get(p, ""), "pi_adresse": ip, "ap_adresse": gw,
         "ap_name": AP_NAME, "ap_ip": AP_IP, "geraet": g or funkgeraet(), "meldung": meldung, "netze": netze, "sicht": sicht, "zeit": time.time()}
    with open(STATUS + ".neu", "w") as f:
        json.dump(d, f)
    os.replace(STATUS + ".neu", STATUS)
    return p


def melden(text, modus=None):
    global meldung
    meldung = text
    print(text, flush=True)
    status(modus)


def suchen():
    global sicht
    beste = {}
    for z in nm("-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "yes", zeit=30)[1].splitlines():
        f = felder(z)
        if len(f) == 3 and f[0] and (f[0] not in beste or int(f[1] or 0) > beste[f[0]]["signal"]):
            beste[f[0]] = {"ssid": f[0], "signal": int(f[1] or 0), "geschuetzt": f[2] not in ("", "--")}
    if beste:
        sicht = sorted(beste.values(), key=lambda x: -x["signal"])


def datei_schreiben(name, text):
    pfad = os.path.join(PROFILE, name + ".nmconnection")
    fd = os.open(pfad, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(text)
    nm("con", "load", pfad)


def psk_text(passwort):
    psk = passwort.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
    return "\\s" + psk[1:] if psk.startswith(" ") else psk


def passwort_sichern(passwort):
    fd = os.open(AP_PASSWORT + ".neu", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(passwort)
    os.replace(AP_PASSWORT + ".neu", AP_PASSWORT)


def ap_profil_sicher():
    if not os.path.exists(os.path.join(PROFILE, AP_PROFIL + ".nmconnection")):
        ap_profil_schreiben(str(uuid.uuid4()))


def ap_profil_schreiben(kennung):
    if not os.path.exists(AP_PASSWORT):
        passwort_sichern(secrets.token_urlsafe(9))
    psk = psk_text(open(AP_PASSWORT).read())
    # pmf=1 (aus): Mit Schutz der Verwaltungsrahmen melden sich Geraete am eingebauten WLAN oft nicht an
    datei_schreiben(AP_PROFIL, f"""[connection]
id={AP_PROFIL}
uuid={kennung}
type=wifi
autoconnect=false

[wifi]
mode=ap
ssid={AP_NAME}
band=bg
channel=6

[wifi-security]
key-mgmt=wpa-psk
pairwise=ccmp;
group=ccmp;
proto=rsn;
pmf=1
psk={psk}

[ipv4]
method=shared
address1={AP_IP}/24

[ipv6]
method=disabled
""")


def ap_passwort(passwort):
    if not 8 <= len(passwort) <= 63:
        melden("Nicht geändert: Das Passwort muss 8 bis 63 Zeichen haben.")
        return
    passwort_sichern(passwort)
    # Gleiche Kennung: Das Profil wird ersetzt, nicht neu angelegt
    m = re.search(r"^uuid=(.+)$", open(os.path.join(PROFILE, AP_PROFIL + ".nmconnection")).read(), re.M)
    ap_profil_schreiben(m.group(1) if m else str(uuid.uuid4()))
    if aktiv()[0] != AP_PROFIL:
        melden("Das Passwort des eigenen Zugangspunkts ist geändert.")
        return
    melden("Das Passwort des eigenen Zugangspunkts ist geändert, er startet neu.", "verbindet")
    time.sleep(3)  # damit die Seite die Antwort noch bekommt
    rc, _ = nm("--wait", str(VERSUCH), "con", "up", "id", AP_PROFIL, "ifname", funkgeraet(), zeit=VERSUCH + 10)
    melden("Das Passwort des eigenen Zugangspunkts ist geändert" + (", er läuft wieder." if rc == 0 else ", der Neustart des Zugangspunkts schlug fehl."))


def eigener_ap(grund):
    suchen()
    ap_profil_sicher()
    melden(grund + " Eigener Zugangspunkt startet.", "verbindet")
    rc, _ = nm("--wait", str(VERSUCH), "con", "up", "id", AP_PROFIL, "ifname", funkgeraet(), zeit=VERSUCH + 10)
    melden(grund + (f" Eigener Zugangspunkt „{AP_NAME}“ läuft." if rc == 0 else " Eigener Zugangspunkt ließ sich nicht starten, neuer Versuch folgt."))
    return rc == 0


def versuch(profil):
    rc, _ = nm("--wait", str(VERSUCH), "con", "up", "id", profil, zeit=VERSUCH + 10)
    if rc != 0:
        return False
    for _ in range(5):
        p, g = aktiv()
        if p == profil and g and adressen(g)[0]:
            return True
        time.sleep(1)
    return False


def erfolg(profil):
    """Merkt das Netz; beim naechsten Start kommt es zuerst an die Reihe."""
    if speicher["letzte_gute"] != profil:
        for n in profile():
            nm("con", "modify", "id", n, "connection.autoconnect-priority", "10" if n == profil else "0")
    speicher["letzte_gute"] = profil
    speicher["netze"][profil] = {"zuletzt_ok": time.time(), "vorgemerkt": False}
    sichern()


def profil_schreiben(ssid, passwort):
    """Neues Profil. Das Passwort landet so nie in einer Befehlszeile."""
    name = "robnet-" + re.sub(r"[^A-Za-z0-9_-]", "_", ssid)[:24] + "-" + secrets.token_hex(2)
    bytes_ssid = ";".join(str(b) for b in ssid.encode()) + ";"
    teil = ""
    if passwort:
        teil = f"\n[wifi-security]\nkey-mgmt=wpa-psk\npsk={psk_text(passwort)}\n"
    datei_schreiben(name, f"""[connection]
id={name}
uuid={uuid.uuid4()}
type=wifi
autoconnect=true

[wifi]
mode=infrastructure
ssid={bytes_ssid}
{teil}
[ipv4]
method=auto

[ipv6]
method=auto
""")
    return name


def profil_zu(ssid):
    for n, s in profile().items():
        if s == ssid:
            return n
    return None


def passwort_falsch(passwort):
    return passwort and not 8 <= len(passwort) <= 63


def verbinden(ssid, passwort):
    if passwort_falsch(passwort):
        melden(f"Nicht gewechselt: Das Passwort für {ssid} muss 8 bis 63 Zeichen haben.")
        return
    p, _ = aktiv()
    vorher = p if p and p != AP_PROFIL else speicher["letzte_gute"]
    alt = profil_zu(ssid)
    ziel = profil_schreiben(ssid, passwort) if passwort or not alt else alt
    melden(f"Wechselt zu {ssid} …", "verbindet")
    time.sleep(3)  # damit die Seite die Antwort noch bekommt
    if versuch(ziel):
        if ziel != alt and alt:
            nm("con", "delete", "id", alt)
            speicher["netze"].pop(alt, None)
        erfolg(ziel)
        melden(f"Verbunden mit {ssid}.")
        return
    if ziel != alt:
        nm("con", "delete", "id", ziel)
    text = f"Verbindung zu {ssid} ist fehlgeschlagen."
    if vorher and vorher != ziel and vorher in profile():
        melden(text + " Kehrt zum vorigen Netz zurück …", "verbindet")
        if versuch(vorher):
            melden(text + f" Wieder verbunden mit {profile().get(vorher, vorher)}.")
            return
    eigener_ap(text + " Auch das vorige Netz ist nicht erreichbar.")


def merken(ssid, passwort):
    if passwort_falsch(passwort):
        melden(f"Nicht gespeichert: Das Passwort für {ssid} muss 8 bis 63 Zeichen haben.")
        return
    alt = profil_zu(ssid)
    if alt and alt == aktiv()[0]:
        melden(f"{ssid} ist gerade verbunden und schon gespeichert.")
        return
    neu = profil_schreiben(ssid, passwort)
    if alt:
        nm("con", "delete", "id", alt)
        speicher["netze"].pop(alt, None)
    speicher["netze"][neu] = {"zuletzt_ok": None, "vorgemerkt": True}
    sichern()
    melden(f"{ssid} ist gespeichert und wird versucht, sobald es in Reichweite ist.")


def vergessen(profil):
    if profil == aktiv()[0]:
        melden("Das verbundene Netz kann nicht entfernt werden.")
        return
    if profil in profile():
        nm("con", "delete", "id", profil)
    speicher["netze"].pop(profil, None)
    if speicher["letzte_gute"] == profil:
        speicher["letzte_gute"] = None
    sichern()
    melden("Netz entfernt.")


def befehle():
    for name in sorted(os.listdir(BEFEHLE)):
        pfad = os.path.join(BEFEHLE, name)
        try:
            with open(pfad) as f:
                b = json.load(f)
        except (OSError, ValueError):
            b = {}
        os.remove(pfad)  # enthaelt vielleicht ein Passwort
        a = b.get("aktion")
        if a == "verbinden" and b.get("ssid"):
            verbinden(b["ssid"], b.get("passwort") or "")
        elif a == "merken" and b.get("ssid"):
            merken(b["ssid"], b.get("passwort") or "")
        elif a == "vergessen" and b.get("profil"):
            vergessen(b["profil"])
        elif a == "ap_passwort":
            ap_passwort(b.get("passwort") or "")
        elif a == "eigener_ap":
            eigener_ap("Auf Anweisung.")
        elif a == "suchen" and aktiv()[0] != AP_PROFIL:
            suchen()


def main():
    global meldung
    os.makedirs(BEFEHLE, mode=0o700, exist_ok=True)
    os.makedirs(os.path.dirname(SPEICHER), exist_ok=True)
    laden()
    ap_profil_sicher()
    ohne_netz = time.monotonic()
    while True:
        befehle()
        p = status()
        if p:
            ohne_netz = time.monotonic()
            if p != AP_PROFIL and p != speicher["letzte_gute"]:
                erfolg(p)
        elif time.monotonic() - ohne_netz <= WARTEN:
            meldung = ""  # die alte Meldung passt nicht mehr, die Seite nennt den Zustand selbst
        else:
            if not eigener_ap(f"{WARTEN} s ohne bekanntes Netz."):
                ohne_netz = time.monotonic() - WARTEN + 30
            else:
                ohne_netz = time.monotonic()
        time.sleep(2)


if __name__ == "__main__":
    main()
