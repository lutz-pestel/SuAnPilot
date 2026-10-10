#!/bin/sh
# Einspielen Paket ap-v00.06 auf dem TinyPilot (Version 00.01, Stand 10.10.2026). Laeuft auf dem TinyPilot als tc.
# Aenderungen gegen ap-v00.05: adaptive.py 00.07 (kein Rueckfall bei ausgeschaltetem Autopiloten), autopilot.py
# (nach dem Start einmal adaptive waehlen), hat/page.py (Regler links unten, Rueckfall als Alarm-Balken).
# Vorher vom PC nach /home/tc/ap-v00.06/ kopieren: dieses Skript und die drei Dateien (Namen siehe unten).
# Aufruf: sh /home/tc/ap-v00.06/einspielen_ap-v00.06.sh   -- startet NICHT neu; Neustart und Rueckweg siehe Ende.
set -e
QUELLE=${QUELLE:-/home/tc/ap-v00.06}
TCE=${TCE:-/mnt/mmcblk0p2/tce/optional}
ARBEIT=${ARBEIT:-/home/tc/paket-ap-v00.06}   # Pfade nur fuer den Probelauf am PC aenderbar
P=usr/local/lib/python3.6/site-packages/pypilot
ALT_TCZ=1e4b6c85d98ae1fc3674af6ce2f1c2fe          # ap-v00.05, an Bord seit 08.10.2026
SICHERUNG=pypilot.tcz.bak-2026-10-10-vor-ap-v00.06
# Datei im Quellordner | Ziel im Paket | md5 alt (ap-v00.05) | md5 neu (ap-v00.06)
LISTE="autopilot.py $P/autopilot.py 9996d65503f0c1e0a6da25a4dd8f418a 860cb20abe699561a08f00c1163328cf
adaptive.py $P/pilots/adaptive.py f392f027769306aa2f840fce7a947284 619bc8f41eebf5ab2366617c0482d595
page.py $P/hat/page.py c626d59bd4c9b86588fd640699eead5f 59f314384ba4e659b7229806288a00e7"

stopp() { echo "ABBRUCH: $*"; exit 1; }
md5() { md5sum "$1" | cut -c1-32; }

echo "1. Paket an Bord pruefen"
[ "$(md5 $TCE/pypilot.tcz)" = "$ALT_TCZ" ] || stopp "pypilot.tcz ist nicht ap-v00.05"
[ ! -e "$TCE/$SICHERUNG" ] || stopp "Sicherung $SICHERUNG gibt es schon (schon eingespielt?)"

echo "2. Neue Dateien pruefen"
echo "$LISTE" | while read f ziel alt neu; do
    [ "$(md5 $QUELLE/$f)" = "$neu" ] || stopp "$f falsch oder unvollstaendig kopiert"
done

echo "3. Paket auspacken nach $ARBEIT"
rm -rf "$ARBEIT"; mkdir -p "$ARBEIT"
unsquashfs -d "$ARBEIT/root" "$TCE/pypilot.tcz" > /dev/null
echo "$LISTE" | while read f ziel alt neu; do
    [ "$(md5 $ARBEIT/root/$ziel)" = "$alt" ] || stopp "$ziel im Paket ist nicht der Stand ap-v00.05"
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
cp -p "$TCE/pypilot.tcz.md5.txt" "$TCE/pypilot.tcz.md5.txt.bak-2026-10-10-vor-ap-v00.06"
cp "$ARBEIT/pypilot.tcz" "$TCE/pypilot.tcz.neu"
mv "$TCE/pypilot.tcz.neu" "$TCE/pypilot.tcz"     # umbenennen: das eingehaengte alte Paket bleibt bis zum Neustart heil
(cd "$TCE" && md5sum pypilot.tcz > pypilot.tcz.md5.txt)
sync
NEU_TCZ=$(md5 $TCE/pypilot.tcz)
[ "$(cut -c1-32 $TCE/pypilot.tcz.md5.txt)" = "$NEU_TCZ" ] || stopp "md5.txt passt nicht"

echo "Fertig: pypilot.tcz ap-v00.06, md5 $NEU_TCZ (fuer das Git-Etikett notieren)."
echo "Neustart (Autopilot vorher AUS): sudo reboot"
echo "Rueckweg: cp $TCE/$SICHERUNG $TCE/pypilot.tcz.neu; mv $TCE/pypilot.tcz.neu $TCE/pypilot.tcz; cp $TCE/pypilot.tcz.md5.txt.bak-2026-10-10-vor-ap-v00.06 $TCE/pypilot.tcz.md5.txt; sync; sudo reboot"
