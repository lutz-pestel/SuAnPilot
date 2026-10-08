# Aufgabenliste TinyPilot (aktuelles Projekt)

Stand: 08.10.2026. Erledigtes wird gelöscht, nicht abgehakt; Lehren gehen in `0-gesamtprojekt/CHRONIK.md`.
Jeder Schritt wird dem Betreiber einzeln vorgelegt (Regel 3). Zukunftsprojekt: `3-suanpilot/docs/gesamt.md`.
Einteilung nach Ort: **Im Hafen** (entwickeln, einrichten) und **Unterwegs** (messen, testen); Reihenfolge
innerhalb des Abschnitts nach Sicherheit → Nutzen/Aufwand → Abhängigkeiten. Fork: `1-tinypilot/regler/verbesserungen.md`.

## Im Hafen
1. **Leitstand erweitern** (Seiten 1–4 laufen am Master, `leitstand.py`): auf den Cockpit-Kartenplotter bringen
   (dort live vom TinyPilot, höchstens 1 Abfrage/s, Desktop-Symbol); Summer zuschalten (Master GPIO 24, Plotter
   GPIO 23, Konflikt mit NMEA_Monitor/ePaper prüfen); weitere Prüfungen ergänzen; Diagramme in Seite 1 nur bei Änderung neu zeichnen.
2. **Ruderlage in Signal K:** Signal K liest die NMEA-Ausgabe des TinyPilot (TCP 10.10.10.163:20220, sendet
   `$APRSA` 4/s, dazu Kurs, Roll, Stampf) als Datenquelle → `steering.rudderAngle`. Vorzeichen prüfen.
   Signal K dafür nur bei ausgeschaltetem Autopiloten neu starten. Alternative: pypilot-eigener
   Signal-K-Client (`signalk.py`, braucht Zugriffsfreigabe im Signal-K-Admin).
3. **Kurze Pumpenstöße bewerten** (< 1,2 s) in Überwachung und Selbsthilfe; Test unterwegs.
4. **Fork:** Einträge aus `Verbesserungen.md` nach deren Priorität einbauen; Test unterwegs.
5. **Profile** als Behelf auf dem Master: Bedingung (Kurs zum Wind, Krängung, Seegang) × Ziel
   („bestes Kurshalten“, „minimaler Strom“); ein Befehl schaltet um und markiert. Werte unterwegs messen.
6. **Datensicherung** Master → `1-tinypilot/daten/aplog/` regelmäßig; automatische Erkennung von Kurs- und
   Bedingungswechseln, damit Abschnitte ohne Markierung auswertbar sind.
7. Ausfall des Autopiloten beim Signal-K-Neustart (30.09.) und Hartruder beim Einschalten nachstellen;
   Verdacht prüfen, ob der Signal-K-Client in pypilot beteiligt ist. Bis dahin: Signal K nie bei
   eingeschaltetem Autopiloten neu starten.
8. Ruder-Kalibrierung genau (Endpunkte am 01.10. nicht am Anschlag, Grad ~20 % zu groß).
9. AIS-Positionsmeldungen mit Datum 2007 abstellen; Signal-K-Passwort zurücksetzen;
   Aufzeichnungsprogramm: Takt nach nicht springendem Zähler.
10. **Pumpe rückwärts** (Testbericht 08.10.): an Bord feste Höchstdrehzahl 80 %. Offen: Erkennung für kurze Stöße des Autopiloten
    (`1-tinypilot/regler/entwurf_pumpenleistung.md`); Fehlalarm „Pumpe steht“ der alten Selbsthilfe bei halber Geschwindigkeit abstellen.
11. **Master-Netz:** Autostart des Leitstands (`Leitstand-Autostart.desktop`) nach einem Neustart des Masters prüfen (eingerichtet,
    ungeprüft); die Geräte `30:83:98` (10.10.10.159/.160, Espressif, ohne offene Ports) zuordnen: an Bord nachsehen
    oder nacheinander ausschalten.
12. **WLAN des Masters beobachten** (06.10.: PC konnte sich 40 min nicht anmelden, Neustart half): Seite 4 eine Stunde offen
    lassen, melden sich Geräte ab? Master an der Drosselgrenze (60 °C), Dateimanager `pcmanfm` 87 % Last prüfen.

## Unterwegs
1. **Betrieb ohne WLAN testen:** WLAN aus, Autopilot muss weiter steuern (ohne GPS/Wind).
2. **Krängungs-Glied H vor dem Wind prüfen:** löst Rollen (bis ±30°) es falsch aus? Wechseltest H 0 / 0,5
   ab 5° Krängung. (Am Wind halbiert H das Anluven, Testbericht 01.10.)
3. **Neue Werte auf anderen Kursen prüfen** (raumschots, vor dem Wind; Gütemaß Trend und Pumpe).
4. Werte je Profil messen; Fork-Einbauten testen (siehe Im Hafen 4, 5).
5. Windgeber prüfen (hart am Wind nur 12–17° scheinbar; Wendewinkel vergleichen); Kompass: Abweichung
   zum GPS-Kurs je Kurs.

## Offene Fragen Hardware (gemeinsam klären; geklärt → in die Systembeschreibung, hier löschen)
Klären durch: N = nachsehen, M = messen, F = Betreiber fragen. Quelle: Unterlagen und KiCad-Pläne (03.10.2026).
1. 5-V-Wandler der PyPilot-Einheit: Ort und Typ? Pläne: eigenes Modul an der 12-V-Klemme des Interface; Betreiber:
   auf der Interface-Platine. (N; Spannung an Klemme „12V out“ M)
2. Interface: welche Widerstände eingelötet? Plan/Platine: Vorwiderstand RF300 360/100 Ω, 8 weitere 2k2/2k, 4k7/4k. (N)
3. Robertson J300 noch an Klemme „RF300 to J300“? Weitergabe über Kondensator ok (Frage im Plan seit 2021)? (N)
4. Hauptplatine: Infrarot-Empfänger und Summer bestückt? Summer funktioniert (Plan: Plus an Masse, beide Platinen)? (N, M)
5. Tasten der PyPilot-Einheit: Folientasten oder Berührungssensoren (Plan-Notiz, 6-poliger Stecker)? (N)
6. Platinen nachträglich geändert (Drahtbrücken, Tausch)? Schaltplan Hauptplatine 11/2022, Platine 08/2021. (N, F)
7. Tasten-Arduino: aufgespielter Code auf anderem Rechner? Programmieradapter beschaffen. (F)
8. Blaues Adernpaar im 8-adrigen Kabel an beiden Enden frei? Verdrahtungsplan zeichnet es verbunden. (N)
9. Motor-Controller: Programmstand, Ladeprogramm, USB-Buchse ohne Öffnen erreichbar? (N)
10. Endlagenschalter am Motor-Controller angeschlossen? Kabel vorhanden, in keinem Plan. (N)
11. Ursache der 57 Servo-Störungen? (Aufzeichnung auswerten)
12. Altes Gerät (Ausfall vorwärts): welches Bauteil? Als Reserve reparieren? (M, F)
13. Pumpendaten: Typ, Nennspannung, Lauf- und Anlaufstrom, Fördermenge. (N Typenschild)
14. Ruder von Anschlag zu Anschlag: Zeit? pypilot nimmt 2,14 s an. (M)
15. Anzeige-Fehler +2,9° bei Ruder mittig: Einbau RF300, Kalibrierung Interface oder pypilot? (N, M)
16. Verzögerung der Ruderlage ~1 s: welcher Teil wie viel (Mittelwert, Glättung, Controller, pypilot)? Für SuAnPilot. (M)
17. Einbauort der PyPilot-Einheit (Kompass): Abstand zu Eisen und Stromkabeln? (N)
18. Unterlagen: Motor_Controller_Fakten nennt 0,25 s Verzögerung (geschätzt), gemessen ~1 s – berichtigen.
19. Verdrahtungsplan: orange Ader und Masse am Wandler fehlen, blaues Paar falsch – Plan berichtigen oder Kabelliste gilt? (F)
20. **RF300-Versuch für den Neubau:** R1 der Interfaceplatine (gemessen ~360–410 Ω, R1 nicht auf 100 Ω tauschen) probeweise
    auf 220 Ω: zählt die Platine noch sauber? Dazu Frequenz mittschiffs an der Platine (6,89 V) und am Robertson (10,8 V)
    vergleichen: beeinflusst die Sensorspannung die Messung? (M)
Ebenfalls offen, steht oben: Ruder-Kalibrierung (Hafen 8), Hartruder (Hafen 7), AIS (Hafen 9), Kompass, Windgeber (Unterwegs 5).
