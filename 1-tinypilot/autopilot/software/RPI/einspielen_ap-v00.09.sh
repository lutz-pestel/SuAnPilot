#!/bin/sh
# Einspielen Paket ap-v00.09 auf dem TinyPilot (Version 00.01, Stand 10.10.2026). Laeuft auf dem TinyPilot als tc.
# Aenderungen gegen ap-v00.08: adaptive.py 00.10 (Vorsteuerung aus der Kraengung, Werte kh und T_H; kh = 0 aus);
# autopilot.py und hat/page.py: Alarm OFF COURSE (wie Robertson: 20 Grad, hier 30 s; Werte ap.offcourse_limit/_delay).
# Vorher vom PC nach /home/tc/ap-v00.09/ kopieren: dieses Skript, autopilot.py, adaptive.py, page.py.
# Aufruf: sh /home/tc/ap-v00.09/einspielen_ap-v00.09.sh   -- startet NICHT neu; Neustart und Rueckweg siehe Ende.
set -e
QUELLE=${QUELLE:-/home/tc/ap-v00.09}
TCE=${TCE:-/mnt/mmcblk0p2/tce/optional}
ARBEIT=${ARBEIT:-/home/tc/paket-ap-v00.09}   # Pfade nur fuer den Probelauf am PC aenderbar
P=usr/local/lib/python3.6/site-packages/pypilot
ALT_TCZ=1b3b8ce84aa6c1930b8ccd0bfac8ff54          # ap-v00.08, an Bord seit 10.10.2026
SICHERUNG=pypilot.tcz.bak-2026-10-10-vor-ap-v00.09
# Datei im Quellordner | Ziel im Paket | md5 alt (ap-v00.08) | md5 neu (ap-v00.09)
LISTE="autopilot.py $P/autopilot.py 94431e191ca2e2c39bd03f7d517976d2 5eb9607c5780ef700765e50bd8e66ab6
adaptive.py $P/pilots/adaptive.py 9d48bd6b7afe2d921a8b7099640836c4 7c6c5a88b97feb4b982a8314bbdfab7e
page.py $P/hat/page.py a2d6684501530aef1375c56234546970 3355342018420f98c801ca2d901c5130"

stopp() { echo "ABBRUCH: $*"; exit 1; }
md5() { md5sum "$1" | cut -c1-32; }

echo "1. Paket an Bord pruefen"
[ "$(md5 $TCE/pypilot.tcz)" = "$ALT_TCZ" ] || stopp "pypilot.tcz ist nicht ap-v00.08"
[ ! -e "$TCE/$SICHERUNG" ] || stopp "Sicherung $SICHERUNG gibt es schon (schon eingespielt?)"

echo "2. Neue Dateien pruefen"
echo "$LISTE" | while read f ziel alt neu; do
    [ "$(md5 $QUELLE/$f)" = "$neu" ] || stopp "$f falsch oder unvollstaendig kopiert"
done

echo "3. Paket auspacken nach $ARBEIT"
rm -rf "$ARBEIT"; mkdir -p "$ARBEIT"
unsquashfs -d "$ARBEIT/root" "$TCE/pypilot.tcz" > /dev/null
echo "$LISTE" | while read f ziel alt neu; do
    [ "$(md5 $ARBEIT/root/$ziel)" = "$alt" ] || stopp "$ziel im Paket ist nicht der Stand ap-v00.08"
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
cp -p "$TCE/pypilot.tcz.md5.txt" "$TCE/pypilot.tcz.md5.txt.bak-2026-10-10-vor-ap-v00.09"
cp "$ARBEIT/pypilot.tcz" "$TCE/pypilot.tcz.neu"
mv "$TCE/pypilot.tcz.neu" "$TCE/pypilot.tcz"     # umbenennen: das eingehaengte alte Paket bleibt bis zum Neustart heil
(cd "$TCE" && md5sum pypilot.tcz > pypilot.tcz.md5.txt)
sync
NEU_TCZ=$(md5 $TCE/pypilot.tcz)
[ "$(cut -c1-32 $TCE/pypilot.tcz.md5.txt)" = "$NEU_TCZ" ] || stopp "md5.txt passt nicht"

echo "Fertig: pypilot.tcz ap-v00.09, md5 $NEU_TCZ (fuer das Git-Etikett notieren)."
echo "Neustart (Autopilot vorher AUS): sudo reboot"
echo "Rueckweg: cp $TCE/$SICHERUNG $TCE/pypilot.tcz.neu; mv $TCE/pypilot.tcz.neu $TCE/pypilot.tcz; cp $TCE/pypilot.tcz.md5.txt.bak-2026-10-10-vor-ap-v00.09 $TCE/pypilot.tcz.md5.txt; sync; sudo reboot"
