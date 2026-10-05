#!/bin/sh
# Version 0.1 (05.10.2026)
# Setzt den Paketbaum von pypilot aus kern/ und plattform/tinypilot/paket/ zusammen.
# Aufruf: sh bauen.sh ZIELORDNER   (Zielordner darf nicht existieren oder muss leer sein)
# Das Paket selbst (mksquashfs) wird auf dem TinyPilot gebaut, siehe CLAUDE.md, Abschnitt TinyPilot.
set -e
ziel="$1"
[ -n "$ziel" ] || { echo "Aufruf: sh bauen.sh ZIELORDNER"; exit 1; }
hier="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ziel"
[ -z "$(ls -A "$ziel")" ] || { echo "Zielordner nicht leer: $ziel"; exit 1; }
cp -R "$hier/kern/." "$ziel/"
cp -R "$hier/plattform/tinypilot/paket/." "$ziel/"
echo "Paketbaum gebaut in $ziel"
