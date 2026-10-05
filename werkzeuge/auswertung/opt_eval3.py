# Auswertung je Zeitabschnitt (Unix-Zeit). Auf dem Master nach /tmp kopieren; opt_eval3 braucht /tmp/opt_eval2.py.
# Aufruf: python3 /tmp/opt_eval3.py START [ENDE]   – Glob der signals-Datei bei Bedarf anpassen.
import csv, glob, statistics as st, sys, time
exec(open('/tmp/opt_eval2.py').read())
# Boeen-Anluven: Kraengung (imu.heel) nimmt in 5 s um > 2 Grad zu -> max. Kursfehler nach Luv in den 15 s danach
hl = [fl(r['imu.heel']) for r in s]; sg = -1 if st.mean([x for x in hl if x is not None]) > 0 else 1
ev = []; i = 0
while i < n - 25:
    j = i + 25
    if hl[i] is not None and hl[j] is not None and abs(hl[j]) - abs(hl[i]) > 2:
        w = [sg * e[k] for k in range(j, min(n, j + 75))]
        ev.append(max(w)); i = j + 75
    else:
        i += 1
hg = [fl(r.get('ap.pilot.basic.Hgain', '')) for r in s]
print('   Boeen %d, Anluven danach im Mittel %.1f Grad, max %.1f' % (len(ev), st.mean(ev) if ev else 0, max(ev) if ev else 0))
