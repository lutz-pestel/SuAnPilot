# Aufgabenliste TinyPilot (aktuelles Projekt)

Stand: 10.10.2026. Erledigtes wird gelöscht, nicht abgehakt; Lehren gehen in `0-gesamtprojekt/CHRONIK.md`.
Jeder Schritt wird dem Betreiber einzeln vorgelegt (Regel 3). Zukunftsprojekt: `3-suanpilot/docs/gesamt.md`.
Ort je Aufgabe: [H] Hafen, [U] unterwegs, [M] auch unter Motor möglich. Fork: `1-tinypilot/regler/verbesserungen.md`.
**Erst der Kern; alles unter „Später“ wartet, bis adaptive auf See gezeigt hat, ob er besser ist als basic.**

## Kern (jetzt)
1. **adaptive in Betrieb nehmen** (Werte: `1-tinypilot/regler/parameter/`, Entwurf `1-tinypilot/regler/entwurf.md`):
   a) [H] nach einem Rückfall beim nächsten Start wieder adaptive wählen; Regler auf Anzeige 1 (Fehlersystematik 3, 5).
   b) [U, M] Vergleich adaptive / basic unter gleichen Bedingungen (Gütemaß Trend und Pumpe); Feinabstimmung (Entwurf 5.5).
2. [H] **Hörbarer Alarm:** Summer im Leitstand zuschalten (Master GPIO 24, Plotter GPIO 23, Konflikt mit NMEA_Monitor/ePaper
   prüfen); ob der Summer der Hauptplatine bestückt ist und geht: offene Frage 4.

## Später
1. [H] Ausfall des Autopiloten beim Signal-K-Neustart (30.09.) nachstellen; Signal-K-Client in pypilot beteiligt?
   Bis dahin: Signal K nie bei eingeschaltetem Autopiloten neu starten.
2. [U, M] **Betrieb ohne WLAN testen:** WLAN aus, Autopilot muss weiter steuern (ohne GPS/Wind).
3. [H] **Prüfung „Ruder folgt nicht“** (Fehlersystematik, Abschnitt 2): Stromgrenzen niedrig/normal/hoch aus den Aufzeichnungen
   bestimmen (bekannt: Fehlerfall 1,0–1,5 A) und Fensterlänge festlegen; danach Spalte „Bereich“ in die Tabelle.
4. [H] **Fehler 6 „Strom hoch“:** Strom an der Endlage je Richtung messen (Handsteuerung, Stoß 1,4 s, aufzeichnen); ergibt
   Grenze und Fensterlänge (bekannt: Betrieb 4–6 A, Spitzen 8,3 A, Anlauf unter 15 A).
5. [H] **Fehler 3 „Messwert springt“:** Wie oft überschreitet der Normalbetrieb (06.–09.10.) die Grenzen 5° je 0,2 s,
   zurück binnen 1 s, zweiter Sprung binnen 5 min? Bewegt eine Hand das Ruder schneller?
6. [H] **Pumpe rückwärts** (Testbericht 08.10.; an Bord fest 80 %): Erkennung für kurze Stöße
   (`1-tinypilot/regler/entwurf_pumpenleistung.md`) und Bewertung kurzer Stöße (< 1,2 s); Fehlalarm „Pumpe steht“ abstellen.
7. [U, M] **Fehler 7 Ersatzsteuerung:** zweiter Kompass im NMEA? Nimmt pypilot 0.24 ihn an, nur nach Kreisel steuern?
   Betriebsart „gps“ und Standby, wenn nichts geht; danach bauen.
8. [H] **Anzeige 1:** unterste Zeile bei Warnung/Alarm invertiert (Fehlersystematik, Abschnitt 5).
9. [H] Ruder-Kalibrierung genau (Endpunkte am 01.10. nicht am Anschlag, Grad ~20 % zu groß); [U, M] Nullpunkt bei
   Geradeausfahrt ohne Krängung (offene Frage 14).
10. [H] **Leitstand** auf den Cockpit-Kartenplotter (live vom TinyPilot, höchstens 1 Abfrage/s, Desktop-Symbol); weitere
   Prüfungen; Diagramme in Seite 1 nur bei Änderung neu zeichnen.
11. [H] **Fork:** Einträge aus `Verbesserungen.md` nach deren Priorität einbauen; Test unterwegs.
12. [U] **Krängungs-Glied H vor dem Wind:** löst Rollen (bis ±30°) es falsch aus? Wechseltest H 0 / 0,5 ab 5° Krängung.
13. [U] **Werte auf anderen Kursen** (raumschots, vor dem Wind); Windgeber (hart am Wind nur 12–17° scheinbar,
    Wendewinkel); [U, M] Kompass: Abweichung zum GPS-Kurs je Kurs.
14. [H] **Datensicherung** Master → `1-tinypilot/daten/aplog/` regelmäßig; Kurs- und Bedingungswechsel automatisch erkennen.
15. [H] **Master-Netz:** Autostart des Leitstands nach Neustart prüfen (eingerichtet, ungeprüft); Geräte `30:83:98`
    (10.10.10.159/.160, Espressif) zuordnen. WLAN beobachten (06.10.: 40 min keine Anmeldung; Drosselgrenze 60 °C, `pcmanfm` 87 %).
16. [H] **Profile** auf dem Master: Bedingung (Kurs zum Wind, Krängung, Seegang) × Ziel („bestes Kurshalten“,
    „minimaler Strom“); ein Befehl schaltet um und markiert; [U] Werte je Profil messen.
17. [H] **Ruderlage in Signal K:** NMEA-Ausgabe des TinyPilot (TCP 10.10.10.163:20220, `$APRSA` 4/s) als Datenquelle →
    `steering.rudderAngle`, Vorzeichen prüfen; Signal K nur bei ausgeschaltetem Autopiloten neu starten.
    Alternative: pypilot-eigener Signal-K-Client (`signalk.py`, Zugriffsfreigabe im Signal-K-Admin).
18. [H] AIS-Meldungen mit Datum 2007 abstellen; Signal-K-Passwort zurücksetzen; Aufzeichnung: Takt nach nicht springendem Zähler.
19. [H] **Messgerät** (`99-tools/messgeraet/`, Idee): Strom und Spannung per Netz; nächster Schritt `99-tools/docs/messgeraet.md`, Abschnitt 3.

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
13. Ruder von Anschlag zu Anschlag: Zeit? pypilot nimmt 2,14 s an. (M)
14. Anzeige-Fehler +2,9° bei Ruder mittig: Einbau RF300, Kalibrierung Interface oder pypilot? (N, M)
15. Verzögerung der Ruderlage ~1 s: welcher Teil wie viel (Mittelwert, Glättung, Controller, pypilot)? Für SuAnPilot. (M)
16. Einbauort der PyPilot-Einheit (Kompass): Abstand zu Eisen und Stromkabeln? (N)
17. Unterlagen: Motor_Controller_Fakten nennt 0,25 s Verzögerung (geschätzt), gemessen ~1 s – berichtigen.
18. Verdrahtungsplan: orange Ader und Masse am Wandler fehlen, blaues Paar falsch – Plan berichtigen oder Kabelliste gilt? (F)
19. **RF300-Versuch für den Neubau:** R1 der Interfaceplatine (gemessen ~360–410 Ω, R1 nicht auf 100 Ω tauschen) probeweise
    auf 220 Ω: zählt die Platine noch sauber? Dazu Frequenz mittschiffs an der Platine (6,89 V) und am Robertson (10,8 V)
    vergleichen: beeinflusst die Sensorspannung die Messung? (M)
20. **Robnet On-Off** (gelb; gemessen 13,5 V bei eingeschaltetem Robertson): Ist es eine Schaltleitung? Spannung messen bei
    Robertson aus und während STBY 3–5 s gedrückt wird (`99-tools/docs/Robnet.md`, H6). (M)
