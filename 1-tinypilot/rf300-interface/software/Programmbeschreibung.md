# RF300-Interface – Programmbeschreibung

Bauen und Hochladen mit der Arduino-IDE, benötigte Bibliothek: U8g2 (Nokia-5110-Display).
Vor dem Hochladen den Jumper an RX entfernen (Hinweis im Code).

## Ablauf
Die Hauptschleife in `RF300_Interface.ino` ruft nacheinander auf:
1. `read_RF300()` (`RF300.h`): misst die Frequenz mit `pulseIn`, glättet sie über 30 Werte (`average.cpp`),
   rechnet sie in den Ruderwinkel um und gibt sie als PWM an Pin 3 aus (auf der Platine mit R6/C6 geglättet).
2. `test_max_rudder()`: lässt die Status-LED blinken, wenn die Frequenz außerhalb des kalibrierten Bereichs liegt.
3. `send_RSA_sentence()` (`nmea.h`): sendet `$GPRSA` mit 4800 Baud, zeitgesteuert statt bei jedem Durchlauf.
4. `state_machine()` (`state_machine.h`): wertet die Tasten aus und wechselt den Menüzustand.
5. `sprungverteiler()`: zeichnet die Display-Seite des aktuellen Zustands (`states.h`).

Die Kalibrierwerte (Winkel min/max, Frequenz min/mitte/max) werden im Menü gesetzt und im EEPROM
(Adressen 10–18) gespeichert. Beim Start werden sie aus dem EEPROM geladen.

## Stolpersteine
- Die `.h`-Dateien und `average.cpp` sind keine eigenständigen Module. Sie enthalten Funktionen, benutzen
  globale Variablen aus der `.ino` und werden dort in fester Reihenfolge per `#include` eingefügt.
- Die Zustände sind `#define`-Zahlen in der `.ino` (in `state_machine.h` nur als Kommentar wiederholt).
  Ein neuer Zustand braucht Einträge in `state_machine()` **und** in `sprungverteiler()`.
  Einer der Zustände heißt `main`: Jede spätere Verwendung des Namens `main` wird ersetzt.
- Die Tasten hängen alle an einem Analogeingang (A1). Die Grenzwerte in `check_keys.h` beruhen
  auf gemessenen Spannungen. Ein langer Tastendruck liefert den zehnfachen Tastencode.
- Ohne RF300-Signal wartet `pulseIn` bis zu seiner Zeitgrenze, und die ganze Schleife stockt.
- `HallSensor_PIN` wird zwar eingerichtet, aber nie gelesen.
- Der Mittelwert über 30 Messungen trägt zur gemessenen Verzögerung der Ruderlage von etwa 1 s bei
  (siehe `0-gesamtprojekt/CHRONIK.md`). Am heutigen System wird daran bewusst nichts geändert (`1-tinypilot/docs/anforderungen/notloesung-A2.md`, B1).
