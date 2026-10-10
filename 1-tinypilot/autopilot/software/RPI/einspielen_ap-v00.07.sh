#!/bin/sh
# Einspielen Paket ap-v00.07 auf dem TinyPilot (Version 00.01, Stand 10.10.2026). Laeuft auf dem TinyPilot als tc.
# Aenderungen gegen ap-v00.06: autopilot.py waehlt adaptive auch bei jedem Einschalten des Autopiloten; adaptive.py 00.08
# (Ruder folgt nicht: basic nur bei eingefrorener Anzeige, sonst Warnung); hat/page.py (Regler gross, WIFI klein).
# Vorher vom PC nach /home/tc/ap-v00.07/ kopieren: dieses Skript, autopilot.py, adaptive.py, page.py.
# Aufruf: sh /home/tc/ap-v00.07/einspielen_ap-v00.07.sh   -- startet NICHT neu; Neustart und Rueckweg siehe Ende.
set -e
QUELLE=${QUELLE:-/home/tc/ap-v00.07}
TCE=${TCE:-/mnt/mmcblk0p2/tce/optional}
ARBEIT=${ARBEIT:-/home/tc/paket-ap-v00.07}   # Pfade nur fuer den Probelauf am PC aenderbar
P=usr/local/lib/python3.6/site-packages/pypilot
ALT_TCZ=ad9d304d8374ad30c0baf95b04e34979          # ap-v00.06, an Bord seit 10.10.2026
SICHERUNG=pypilot.tcz.bak-2026-10-10-vor-ap-v00.07
# Datei im Quellordner | Ziel im Paket | md5 alt (ap-v00.06) | md5 neu (ap-v00.07)
LISTE="autopilot.py $P/autopilot.py 860cb20abe699561a08f00c1163328cf 94431e191ca2e2c39bd03f7d517976d2
adaptive.py $P/pilots/adaptive.py 619bc8f41eebf5ab2366617c0482d595 35b8b3c7fe6e19917e11e7141a2d1ea0
page.py $P/hat/page.py 59f314384ba4e659b7229806288a00e7 a2d6684501530aef1375c56234546970"

stopp() { echo "ABBRUCH: $*"; exit 1; }
md5() { md5sum "$1" | cut -c1-32; }

echo "1. Paket an Bord pruefen"
[ "$(md5 $TCE/pypilot.tcz)" = "$ALT_TCZ" ] || stopp "pypilot.tcz ist nicht ap-v00.06"
[ ! -e "$TCE/$SICHERUNG" ] || stopp "Sicherung $SICHERUNG gibt es schon (schon eingespielt?)"

echo "2. Neue Dateien pruefen"
echo "$LISTE" | while read f ziel alt neu; do
    [ "$(md5 $QUELLE/$f)" = "$neu" ] || stopp "$f falsch oder unvollstaendig kopiert"
done

echo "3. Paket auspacken nach $ARBEIT"
rm -rf "$ARBEIT"; mkdir -p "$ARBEIT"
unsquashfs -d "$ARBEIT/root" "$TCE/pypilot.tcz" > /dev/null
echo "$LISTE" | while read f ziel alt neu; do
    [ "$(md5 $ARBEIT/root/$ziel)" = "$alt" ] || stopp "$ziel im Paket ist nicht der Stand ap-v00.06"
    cp "$QUELLE/$f" "$ARBEIT/root/$ziel"
    python3 -c "import py_compile, sys; py_compile.compile(sys.argv[1], cfile='/tmp/probe.pyc', doraise=True)" \
        "$ARBEIT/root/$ziel" || stopp "$ziel laesst sich nicht uebersetzen"
    [ "$(md5 $ARBEIT/root/$ziel)" = "$neu" ] || stopp "$ziel nach dem Kopieren falsch"
done

echo "4. Neues Paket packen"
mksquashfs "$ARBEIT/root" "$ARBEIT/pypilot.tcz" -comp gzip -b 131072 -noappend > /dev/null
unsquashfs -lls "$ARBEIT/pypilot.tcz" > /dev/null || stopp "neues Paket nicht lesbar"

echo "5. Sichern und austauschen"
cp -p "$TCE/pypilot.tcz" "$TCE/$SICHERUNG"
cp -p "$TCE/pypilot.tcz.md5.txt" "$TCE/pypilot.tcz.md5.txt.bak-2026-10-10-vor-ap-v00.07"
cp "$ARBEIT/pypilot.tcz" "$TCE/pypilot.tcz.neu"
mv "$TCE/pypilot.tcz.neu" "$TCE/pypilot.tcz"     # umbenennen: das eingehaengte alte Paket bleibt bis zum Neustart heil
(cd "$TCE" && md5sum pypilot.tcz > pypilot.tcz.md5.txt)
sync
NEU_TCZ=$(md5 $TCE/pypilot.tcz)
[ "$(cut -c1-32 $TCE/pypilot.tcz.md5.txt)" = "$NEU_TCZ" ] || stopp "md5.txt passt nicht"

echo "Fertig: pypilot.tcz ap-v00.07, md5 $NEU_TCZ (fuer das Git-Etikett notieren)."
echo "Neustart (Autopilot vorher AUS): sudo reboot"
echo "Rueckweg: cp $TCE/$SICHERUNG $TCE/pypilot.tcz.neu; mv $TCE/pypilot.tcz.neu $TCE/pypilot.tcz; cp $TCE/pypilot.tcz.md5.txt.bak-2026-10-10-vor-ap-v00.07 $TCE/pypilot.tcz.md5.txt; sync; sudo reboot"
