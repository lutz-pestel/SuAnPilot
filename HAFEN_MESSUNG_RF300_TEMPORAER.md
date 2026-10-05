# TEMPORÄR – Messung RF300 am Robertson (nach Erledigung löschen)

Ergebnisse gehen danach in `docs/anforderungen/motorcontroller.md`, Abschnitt 3.4.

**Zweck:** Mit welcher Spannung und welchem Strom versorgt Robertson selbst den RF300?
Vergleich: An der eigenen Interfaceplatine bekommt er 7,3 V bei 13,3 V Bordspannung (04.10.2026, ~17 mA gerechnet).

## Vorher
- Autopilot (TinyPilot) und Robertson **aus**. Ruder mittschiffs.
- Multimeter: Messkabel in **V-Buchse**, Einstellung **V= (Gleichspannung)**.

## Ablauf
1. RF300-Kabel von der Interfaceplatine lösen und an der Robertson-Anschlussbox an **RF+ / RF–** klemmen
   (Polung egal). Robertson einschalten.
2. **Spannung am RF300:** Messspitzen an RF+ und RF–. Etwa 10 s warten, bis die Anzeige ruhig ist.
3. **Bordspannung:** Messspitzen am Versorgungseingang der Robertson-Box (Plus/Minus).
4. *Wenn es einfach geht –* **Strom:** Robertson aus. Messkabel auf **mA-Buchse**, Einstellung **mA=**.
   Eine RF300-Ader lösen, Multimeter dazwischen schalten (in Reihe). Robertson ein, ablesen.
   ⚠️ Im Strommodus **nie** zwei Klemmen mit Spannung direkt berühren – das ist ein Kurzschluss durchs Gerät.
5. Robertson aus. Messkabel zurück auf **V-Buchse**.
6. RF300-Kabel wieder an die Interfaceplatine (wie vorher). TinyPilot ein: **Ruderanzeige prüfen**
   (Ruder mittschiffs ≈ wie vorher, Ruder drehen → Anzeige folgt).

## Ergebnisse (eintragen)
| Messung | Wert |
|---|---|
| 2. Spannung RF+ / RF– am Robertson | ____ V |
| 3. Bordspannung am Robertson | ____ V |
| 4. Strom in der RF300-Ader (falls gemessen) | ____ mA |
| Maschine lief / Laden? | ja / nein |
| Bemerkungen (Anzeige am Robertson ok? Fehlermeldung?) | |
