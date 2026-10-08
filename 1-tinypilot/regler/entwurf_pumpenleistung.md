# Entwurf: adaptive Pumpenleistung je Richtung

Version 00.03, Stand 08.10.2026. **An Bord seit 08.10.** (`pypilot/leistung.py` 00.02, Paket `ap-v00.05`; Prüfung
`1-tinypilot/regler/leistung_test.py`). **Greift im Autopilot-Betrieb nicht:** basic gibt nur Stöße von ~0,5 s, die Erkennung
braucht ≥ 2 s Dauerlauf. Nächster Schritt: Erkennung je Stoß am Strom. Bis dahin feste Höchstdrehzahl 80 % (Testbericht 08.10., 5a). Überbrückung bis zum neuen Motor-Controller (Phase 2).
Anlass und Messungen: `1-tinypilot/docs/tests/2026-10-08_Hafen_Pumpe_Drehzahl_Spannung.md`.

## 1. Ziel
Der gekaufte Controller versagt rückwärts ab Befehl 0,90 bei Bordspannung um 12,6 V; unter 0,90 läuft er, und Absenken
wirkt sofort im laufenden Pumpenlauf. Der TinyPilot erkennt den Ausfall selbst, senkt die Leistung **nur für diese
Richtung** und meldet es. Steigt die Bordspannung deutlich (Maschine, Ladegerät), gibt er die volle Leistung wieder frei.

## 2. Entscheidungen des Betreibers (08.10.2026)
- Absenken in Schritten von 5 % der Einstellung, je Richtung getrennt.
- **Keine Untergrenze.** Jeder Schritt wird gemeldet, nie gesperrt; abschalten entscheidet der Betreiber.
- Hochsetzen nur bei deutlich höherer Ruhespannung: **mindestens 1,0 V** über dem Wert bei der letzten Absenkung,
  mit Hysterese. Protokoll am Master und Anzeige im Leitstand.

## 3. Ablauf im TinyPilot (`pypilot/servo.py`)
- **Neue Werte, dauerhaft gespeichert:** `servo.limit.forward`, `servo.limit.reverse` (Prozent, Start 100) und
  `servo.limit.uref.forward`, `servo.limit.uref.reverse` (Ruhespannung bei der letzten Absenkung).
- **Anwenden:** In `do_command` wird die Höchstgeschwindigkeit je Richtung `min(speed.max, limit[Richtung])`.
  `servo.speed.min/max` bleiben 100 %. Einstellung 85 % ergibt über die Kalibrierung (0,2 + 0,8 × Drehzahl) Befehl 0,88.
- **Erkennen (beide Bedingungen):**
  - (a) Strom gleitend unter 2,0 A, ab 0,4 s nach Laufbeginn oder nach der letzten Absenkung (gestört 1,0–1,3 A, normal 2,6 A und mehr).
  - (b) Ruder bewegt sich nicht in Befehlsrichtung: unter 0,5° in 1,0 s, Anzeige um 0,5 s versetzt.
  - Bedingung (b) verhindert, dass niedriger Strom bei kleiner Leistung fälschlich weiter absenkt (Abstieg ohne Ende).
- **Absenken:** `limit -= 5`, nicht unter 5 % (0 % hieße Pumpe aus – das entscheidet der Betreiber); `uref` = Ruhespannung
  vor diesem Lauf; Meldung. Nach dem ersten bestätigten Ausfall im selben Lauf genügt oberhalb von 50 % der Strom
  (0,4 s nach der Absenkung): 100 → 85 % in 3,8 s ab Laufbeginn (Prüfung). Darunter wieder volle Prüfung mit Ruderweg.
- **Ruhespannung:** `servo.voltage` gemittelt über 2 s, nur bei stehender Pumpe (Strom unter 0,5 A).
- **Hochsetzen:** bei stehender Pumpe Ruhespannung ≥ `uref + 1,0 V` ununterbrochen **60 s** → `limit = 100`, Meldung.
  - Kehrt der Fehler zurück, wird sofort wieder abgesenkt, mit neuer `uref`.
  - Die Hysterese ergibt sich aus den 1,0 V und den 60 s: Ein kurzer Spannungsanstieg löst nichts aus.
- **Vorhandene Selbsthilfe** (`recover()`, meldet nur „Pumpe steht“): bleibt, Ereignisse gehen weiter nach `REC_LOG` und `servo.recovery`.
- **Nach Neustart:** gespeicherte Grenzen gelten weiter (Vorschlag), bis die Spannungsregel sie freigibt.

## 4. Protokoll und Leitstand (Master)
- `aplog.py`: neue Spalten `servo.limit.forward`, `servo.limit.reverse`.
- **Ereignisse** mit Uhrzeit, Richtung, neuem Wert und Spannung, zum Beispiel „rückwärts 100 → 95 % (12,6 V)“ oder
  „rückwärts wieder 100 % (13,9 V)“, über `servo.recovery`, das schon aufgezeichnet wird.
- `leitstand.py`: gelber Hinweis, solange eine Richtung begrenzt ist, etwa „Pumpe rückwärts auf 85 % begrenzt“.
  Grüne Meldung bei Freigabe. Das ist ein echtes Problem und wird deshalb gezeigt (Regel: nur echte Probleme, aber alle).

## 5. Wirkung auf die Regler
- **basic:** befiehlt Pumpengeschwindigkeit, eine Begrenzung wirkt wie eine kleinere Verstärkung in dieser Richtung.
- **adaptive:** lernt die Rudergeschwindigkeit je Richtung nach (`v_up`/`v_down`). `rate_up`/`rate_down` nach dem
  Fahrtest prüfen. Seine Meldung „Pumpe schwach“ kann bei Begrenzung ansprechen; dann den Wortlaut anpassen.

## 6. Umsetzung (je Schritt einzeln vorgelegt)
1. `servo.py` ändern, beide Kopien (`kern/…` und Paket). Test am PC: `diag_mock.py` so erweitern, dass rückwärts ab
   Befehl 0,90 bei 12,6 V versagt und bei 14 V läuft.
2. Paket bauen und im Hafen aufspielen (neue Paketnummer, `0-gesamtprojekt/VERSIONEN.md`).
3. Hafentest: Batterie allein → erster Rückwärtslauf gestört, Absenkung bis 85 % in 3 Schritten. Dann Ladegerät an →
   nach 60 s wieder 100 %.
4. `aplog.py` und `leitstand.py` erweitern.
5. Fahrtest: Wie oft wird abgesenkt, steuert der Autopilot mit der Begrenzung gut genug?

## 7. Offen
- Schwellen 2,0 A und 0,5° aus den Hafenmessungen. Bei Krängung und Ruderlast unterwegs ungeprüft.
- Ob die Firmware auf dem Gerät wirklich bei Befehl 0,90 umschaltet (passt zur Reserve, kein Beweis).
