# Anforderungen

## A2 – Übergangslösung „Pumpenstoß je Tastendruck“ (Notlösung, umgesetzt 29.09.2026)
- **Nur aus der Not gewählt:** Es gibt derzeit kein Programmiergerät für den Arduino, und der
  aufgespielte Code ist verschollen. Der Code in `tinypilot/autopilot/software/Arduino/TinyPilot_Coprocessor` ist veraltet
  (Ruhepegel der Tastenleitungen: gemessen HIGH, laut diesem Code LOW).
- Verhalten: Bei ausgeschaltetem Autopiloten lässt jeder Tastendruck einer Steuertaste (kurz
  oder lang) die Pumpe 1,4 s mit voller Drehzahl in die gewählte Richtung laufen.
  Gemessen: 6–7° Ruderweg je Druck, in beide Richtungen gleich.
- Eine Positionsregelung („fahre 2°“) scheidet aus: Die Ruderlage kommt etwa 1 s verzögert an,
  das Ruder überschoss dadurch um 3–6° und ungleich je Richtung (gemessen 29.09.2026).
- Umsetzung in der Tastensoftware des TinyPilot (pypilot 0.24, `hat/page.py`).
- **Wird entfernt, sobald eine richtige Handsteuerung per Taste möglich ist** (Ziel siehe SuAnPilot, B3).

## Künftige Systeme
- Anforderungen (Ideen) stehen in `docs/anforderungen/` (Einstieg: `gesamt.md`).
