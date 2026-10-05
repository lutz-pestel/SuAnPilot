#!/usr/bin/env python3
# Übersicht Ruder-Trimm (PyPilot-AI, 02.10.2026): Geradeaus-Ruder aus guete_*.csv je Bug, Windklasse und Krängungsstufe.
# Ruder-Trimm = Ruderanzeige minus RUDER_MITTE (Anzeige bei Ruder mittig). Aufruf: ruder.py [DATUM, z. B. 2026-10-02]
import csv, glob, os, statistics, sys

RUDER_MITTE = 2.9      # °, gemessen 02.10.2026 unter Motor ohne Segel
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

day = sys.argv[1] if len(sys.argv) > 1 else ''
files = sorted(glob.glob(os.path.join(DATA, 'guete_%s*.csv' % day)))
groups, n = {}, 0
for p in files:
    for r in csv.DictReader(open(p, newline='')):
        g, kr, bug = fl(r.get('geradeaus_ruder')), fl(r.get('kraengung')), r.get('bug', '')
        if g is None or kr is None or bug not in ('BB', 'StB'):
            continue
        n += 1
        groups.setdefault((r.get('wind_klasse', ''), bug, int(kr // 2) * 2), []).append(g - RUDER_MITTE)
print('Ruder-Trimm (Anzeige - %.1f°) %s: %d Minuten aus %d Datei(en)' % (RUDER_MITTE, day or 'alle Tage', n, len(files)))
print('%-8s %-12s %-14s %-14s' % ('Wind', 'Krängung', 'Wind von BB', 'Wind von StB'))
for wk in ('leicht', 'mittel', 'stark', ''):
    stufen = sorted(set(k for w, b, k in groups if w == wk))
    for k in stufen:
        cell = []
        for b in ('BB', 'StB'):
            v = groups.get((wk, b, k), [])
            cell.append('%+6.1f° (%3d)' % (statistics.mean(v), len(v)) if len(v) >= 3 else '      –' if not v else '  (%d Min.)' % len(v))
        print('%-8s %2d–%2d°       %-14s %-14s' % (wk or '?', k, k + 2, cell[0], cell[1]))
print('In Klammern: Minuten. Werte erst ab etwa 10 Minuten belastbar.')
