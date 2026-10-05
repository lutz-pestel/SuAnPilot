#!/bin/sh
# aplog.sh start | stop | status | pumpe [n] | mark "Text" | ruder [Datum]
D=$(dirname "$(readlink -f "$0")")
case "$1" in
  start)
    if pgrep -f "$D/aplog.py" >/dev/null; then echo "laeuft bereits"; exit 0; fi
    mkdir -p "$D/data"
    nohup python3 "$D/aplog.py" >> "$D/data/aplog.log" 2>&1 &
    pgrep -f "$D/pumpwatch.py" >/dev/null || nohup python3 "$D/pumpwatch.py" >> "$D/data/aplog.log" 2>&1 &
    sleep 2; "$0" status ;;
  stop)
    pkill -f "$D/pumpwatch.py"
    pkill -f "$D/aplog.py" && echo "gestoppt" || echo "lief nicht" ;;
  status)
    if pgrep -f "$D/aplog.py" >/dev/null; then echo "laeuft"; else echo "laeuft nicht"; fi
    pgrep -f "$D/pumpwatch.py" >/dev/null && echo "Pumpenueberwachung laeuft" || echo "Pumpenueberwachung laeuft nicht"
    cat "$D/data/pumpstatus.txt" 2>/dev/null
    ls -t "$D"/data/signals_*.csv 2>/dev/null | head -1 | xargs -r ls -l
    tail -2 "$D/data/aplog.log" 2>/dev/null ;;
  pumpe)
    cat "$D/data/pumpstatus.txt" 2>/dev/null
    f=$(ls -t "$D"/data/pumpruns_*.csv 2>/dev/null | head -1); [ -n "$f" ] && awk -F, 'NR>1 && $10!=""' "$f" | tail -${2:-10} ;;
  mark)
    shift
    echo "$(date +%Y-%m-%dT%H:%M:%S),$(date +%s.%N | cut -c1-13),\"$*\"" >> "$D/data/marks.csv"
    echo "Markierung: $*" ;;
  ruder)
    python3 "$D/ruder.py" $2 ;;
  *) echo "aufruf: $0 start|stop|status|pumpe [n]|mark \"Text\"|ruder [Datum]" ;;
esac
