# SuAn-Autopilot-Projekt

Version 00.01, Stand 07.10.2026, Obergrenze 80 Zeilen.
Entwicklung und Bau eines neuen Autopilot-Systems für die SuAn. Dieses Dokument erklärt das Gesamtprojekt;
Einzelheiten stehen in den Dokumenten der Phasen (Abschnitt 6).

## 1. Anlass
- An Bord ist ein **Robertson AP300CX** mit Verteilereinheit J300. Er steuert nach wie vor, aber das Display der
  Bedieneinheit ist kaum noch zu erkennen, und einige Bedientasten funktionieren nicht mehr.
- Der Robertson bleibt bis zum Ende des Projekts angeschlossen und als Rückfall nutzbar. Ob er danach
  ausgebaut wird, wird dann entschieden.
- Er ist der **Maßstab**: Das neue System muss mindestens so gut und so zuverlässig steuern.

## 2. Ziel
Ein Autopilot für die SuAn (15 t, Hydrauliksteuerung mit Pumpe RPU160, Ruderlagengeber RF300), der das Schiff
unter allen Bedingungen, auf allen Kursen und bei jeder Wellengröße sicher steuert.

## 3. Heutiges Ersatzsystem
- **TinyPilot** (pypilot 0.24) am Steuerstand, anstelle der Robertson-Bedieneinheit. Die Hardware ist selbst
  entwickelt; Kursregler und Lagesensor sitzen hier.
- **Gekaufter pypilot-Motor-Controller** im Motorraum: steuert die Pumpe. Er ist für einen Ruderlagengeber
  gebaut, der eine Spannung von 0–5 V ausgibt.
- **RF300-Interfaceplatine** (selbst entwickelt): wandelt die Frequenz des RF300 in diese Spannung um und gibt
  die Ruderlage für die Anzeige am Steuerstand aus. Sie soll im weiteren Projekt **ganz entfallen**.

## 4. Phasen
Die Phasen werden nacheinander realisiert; Phase 1 und 2 laufen derzeit nebeneinander.

**Phase 1 – Ersatzsystem testen (läuft).** Ausführliche Tests von TinyPilot, Motor-Controller und
Interfaceplatine: Worin liegen die Schwächen des heutigen Ersatzsystems? Jede gefundene Schwäche wird als
Anforderung für Phase 2 oder 3 aufgenommen.

**Phase 2 – neuer Motor-Controller (begonnen).** Anlass: gravierende Schwächen des gekauften Controllers,
gefunden in Phase 1. Der neue Controller
- ersetzt den gekauften Controller und die Interfaceplatine gemeinsam,
- liest den RF300 direkt und gibt die Ruderlage für die Anzeige am Steuerstand selbst aus,
- ist voll verträglich mit dem TinyPilot, der dafür unverändert bleibt.

**Phase 3 – SuAnPilot (noch nicht begonnen).** Ersetzt den TinyPilot; wird erst in dieser Phase konzipiert,
entworfen und gebaut. Unterschiede zum TinyPilot:
- kein Arduino als Coprozessor, überhaupt kein Coprozessor,
- nur noch ein einziges LCD-Display.
Weitere Ideen stehen als Ideensammlung im Dokument der Phase 3.

## 5. Übergang von Phase 2 zu Phase 3
Phase 3 beginnt erst, wenn der neue Motor-Controller mit dem TinyPilot zur vollen Zufriedenheit
zusammenarbeitet und die SuAn sicher steuert. Nachweis durch **Seetests** nach einem Bedingungsraster
(Kurs zum Wind, Wellengröße, Krängung); Maßstab ist der Robertson. Termine gibt es keine.

## 6. Wo was steht
| Thema | Ort |
|---|---|
| Phase 1: Aufbau und Werte | `1-tinypilot/docs/system/Systembeschreibung.md` |
| Phase 1: Testablauf, Testberichte | `1-tinypilot/docs/system/Testplan_Autopilot.md`, `1-tinypilot/docs/tests/` |
| Phase 1: Hardware TinyPilot (KiCad) | `1-tinypilot/autopilot/hardware/kicad/` |
| Phase 1: gekaufter Motor-Controller | `1-tinypilot/motor-controller/hardware/` |
| Phase 1: RF300-Interfaceplatine | `1-tinypilot/rf300-interface/` |
| Eigener Kursregler | `1-tinypilot/regler/` |
| Phase 2: Anforderungen, Bauteile | `2-motor-controller/hardware/konzeption/motorcontroller.md`, `Bauteilauswahl.md` |
| Phase 3: Gesamtbeschreibung | `3-suanpilot/docs/gesamt.md` |
| Robertson-Handbücher, Pumpe | `0-gesamtprojekt/handbuecher/Robertson/` |
| Aufgaben, Lehren | `0-gesamtprojekt/TODO.md`, `0-gesamtprojekt/CHRONIK.md` |
