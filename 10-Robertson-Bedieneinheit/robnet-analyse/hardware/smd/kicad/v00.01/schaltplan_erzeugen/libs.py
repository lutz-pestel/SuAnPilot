# Projektbibliotheken Robnet-Analyse: eigene Schaltzeichen und Bauformen. Version 00.05, Stand 16.10.2026.
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import parse, dump, find, Q

# Quelle der LM4040- und KEMET-Vorlagen: Motor-Controller v00.01 (gleiche Teile)
MC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../../../..',
                                   '2-motor-controller/hardware/kicad/v00.01')) + '/'


def prop(name, val, x, y, hide=False, justify=None):
    e = ['effects', ['font', ['size', '1.27', '1.27']]]
    if justify:
        e.append(['justify', justify])
    p = ['property', Q(name), Q(val), ['at', x, y, '0'], e]
    if hide:
        p.append(['hide', 'yes'])
    return p


def pin(num, name, x, y, ang):
    f = ['effects', ['font', ['size', '1.27', '1.27']]]
    return ['pin', 'passive', 'line', ['at', x, y, ang], ['length', '2.54'], ['name', Q(name), f], ['number', Q(num), f]]


def jumper(name, desc, left, right, height):
    # left/right: Liste (nummer, name, y); Koerper 20,32 mm breit
    h = str(height)
    pins = [pin(n, t, '-12.7', y, '0') for n, t, y in left] + [pin(n, t, '12.7', y, '180') for n, t, y in right]
    return ['symbol', Q(name), ['pin_names', ['offset', '1.016']], ['exclude_from_sim', 'no'], ['in_bom', 'yes'], ['on_board', 'yes'],
            prop('Reference', 'JP', '0', str(height + 1.27)),
            prop('Value', name, '0', str(-height - 1.27)),
            prop('Footprint', 'Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical', '0', str(-height - 3.81), True),
            prop('Datasheet', '', '0', '0', True),
            prop('Description', desc, '0', '0', True),
            ['symbol', Q(name + '_0_1'), ['rectangle', ['start', '-10.16', h], ['end', '10.16', '-' + h],
                                          ['stroke', ['width', '0.254'], ['type', 'default']], ['fill', ['type', 'background']]]],
            ['symbol', Q(name + '_1_1')] + pins]


def write(out):
    mc = parse(open(MC + 'Motor-Controller.kicad_sym', encoding='utf-8').read())[0]
    lm = [s for s in find(mc, 'symbol') if s[1] == 'LM4040LP-2.5_3pin'][0]
    sel = jumper('Jumper_2x3_Seitenwahl',
                 'Stiftleiste 2 x 3 mit zwei Jumpern: 1-3 und 2-4 gesteckt = Seite J300, 3-5 und 4-6 gesteckt = Seite Bedieneinheit',
                 [('1', 'Bus+(J300)', '5.08'), ('2', 'Bus−(J300)', '2.54'), ('5', 'Bus+(Bed.)', '-2.54'), ('6', 'Bus−(Bed.)', '-5.08')],
                 [('3', 'Bus+', '5.08'), ('4', 'Bus−', '-5.08')], 7.62)
    kr = jumper('Jumper_2x3_Kreuzung',
                'Stiftleiste 2 x 3 mit zwei Jumpern: 1-3 und 2-4 gesteckt = gerade (A = Bus+), 3-5 und 4-6 gesteckt = gekreuzt (A = Bus−)',
                [('1', 'Bus+', '7.62'), ('6', 'Bus+', '5.08'), ('2', 'Bus−', '-5.08'), ('5', 'Bus−', '-7.62')],
                [('3', 'A', '5.08'), ('4', 'B', '-5.08')], 10.16)
    # MCP3208 mit Dout als abschaltbarem Ausgang (hochohmig bei CS hoch, Microchip DS21298E Bild 5-1): zwei Wandler an MISO
    import copy
    adc_lib = parse(open('C:/Program Files/KiCad/10.0/share/kicad/symbols/Analog_ADC.kicad_sym', encoding='utf-8').read())[0]
    adc = copy.deepcopy([x for x in find(adc_lib, 'symbol') if x[1] == 'MCP3208'][0])
    for u in find(adc, 'symbol'):
        for pn in find(u, 'pin'):
            if find(pn, 'number')[0][1] == '12':
                pn[1] = 'tri_state'
    for pr in find(adc, 'property'):
        if pr[1] == 'Description':
            pr[2] = Q(pr[2] + '; Dout als tri_state (hochohmig bei CS hoch, DS21298E Bild 5-1)')
    # Blattlokale Versorgungszeichen: verbinden nur innerhalb ihres Blatts; zwischen den Blaettern laeuft die
    # Versorgung ueber Blattanschluesse und Leitungen im Hauptblatt (dort sichtbar)
    pw_lib = parse(open('C:/Program Files/KiCad/10.0/share/kicad/symbols/power.kicad_sym', encoding='utf-8').read())[0]
    local = []
    for name in ('GND', '+3V3'):
        pw = copy.deepcopy([x for x in find(pw_lib, 'symbol') if x[1] == name][0])
        for i, x in enumerate(pw):
            if isinstance(x, list) and x[0] == 'power':
                pw[i] = ['power', 'local']
        for pr in find(pw, 'property'):
            if pr[1] == 'Description':
                pr[2] = Q(pr[2] + ' (nur innerhalb des Blatts)')
        local.append(pw)
    lib = ['kicad_symbol_lib', ['version', '20251024'], ['generator', Q('kicad_symbol_editor')], ['generator_version', Q('10.0')], lm, sel, kr, adc] + local
    open(os.path.join(out, 'Robnet-Analyse.kicad_sym'), 'w', encoding='utf-8', newline='\n').write(dump(lib) + '\n')
    pretty = os.path.join(out, 'Robnet-Analyse.pretty')
    os.makedirs(pretty, exist_ok=True)
    shutil.copy(MC + 'Motor-Controller.pretty/C_KEMET_C320_L5.1mm_W4.1mm_P2.54mm.kicad_mod', pretty)
    open(os.path.join(pretty, 'C_TDK_FG16_L5.5mm_W3.5mm_P2.50mm.kicad_mod'), 'w', encoding='utf-8', newline='\n').write(TDK)
    open(os.path.join(pretty, ZERO_NAME + '.kicad_mod'), 'w', encoding='utf-8', newline='\n').write(zero())
    open(os.path.join(out, 'sym-lib-table'), 'w', encoding='utf-8', newline='\n').write(
        '(sym_lib_table\n  (version 7)\n  (lib (name "Robnet-Analyse")(type "KiCad")(uri "${KIPRJMOD}/Robnet-Analyse.kicad_sym")'
        '(options "")(descr "Eigene Schaltzeichen Robnet-Analyse"))\n)\n')
    open(os.path.join(out, 'fp-lib-table'), 'w', encoding='utf-8', newline='\n').write(
        '(fp_lib_table\n  (version 7)\n  (lib (name "Robnet-Analyse")(type "KiCad")(uri "${KIPRJMOD}/Robnet-Analyse.pretty")'
        '(options "")(descr "Eigene Bauformen Robnet-Analyse"))\n)\n')


def line(x1, y1, x2, y2, w, layer):
    return '\t(fp_line\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width %s)\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "%s")\n\t)\n' % (
        x1, y1, x2, y2, w, layer)


def rect(x1, y1, x2, y2, w, layer):
    return '\t(fp_rect\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width %s)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "%s")\n\t)\n' % (
        x1, y1, x2, y2, w, layer)


def pad(n, x):
    return ('\t(pad "%s" thru_hole circle\n\t\t(at %s 0)\n\t\t(size 1.6 1.6)\n\t\t(drill 0.8)\n\t\t(layers "*.Cu" "*.Mask")\n'
            '\t\t(remove_unused_layers no)\n\t)\n') % (n, x)


# TDK FG16 (FG16X7R1H475KRT06, Gurt): Koerper 5,5 x 3,5 mm, Hoehe 6,0 mm, Raster 2,5 mm (+0,5/-0,2), Draht 0,5 mm (+0,1/-0,03)
# laut TDK-Katalog FG, Ausgabe 11/2024, S. 39 und 42 (datenblaetter/TDK_FG16X7R1H475KRT06_2024-11.pdf); Bohrung 0,8 = Draht max. 0,6 + 0,2
TDK = ('(footprint "C_TDK_FG16_L5.5mm_W3.5mm_P2.50mm"\n\t(version 20260206)\n\t(generator "pcbnew")\n\t(generator_version "10.0")\n'
       '\t(layer "F.Cu")\n\t(descr "TDK FG16 Keramikkondensator bedrahtet, Koerper 5,5 x 3,5 mm, Rastermass 2,5 mm, Draht 0,5 mm, Bohrung 0,8 mm '
       '(FG16X7R1H475KRT06; TDK-Katalog FG 11/2024)")\n\t(tags "C TDK FG16 Radial 2.50mm")\n'
       '\t(property "Reference" "REF**"\n\t\t(at 1.25 -2.9 0)\n\t\t(layer "F.SilkS")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n'
       '\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
       '\t(property "Value" "C_TDK_FG16_L5.5mm_W3.5mm_P2.50mm"\n\t\t(at 1.25 2.9 0)\n\t\t(layer "F.Fab")\n\t\t(effects\n\t\t\t(font\n'
       '\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
       '\t(attr through_hole)\n\t(duplicate_pad_numbers_are_jumpers no)\n'
       + line(-1.62, -1.87, 4.12, -1.87, 0.12, 'F.SilkS') + line(4.12, -1.87, 4.12, 1.87, 0.12, 'F.SilkS')
       + line(4.12, 1.87, -1.62, 1.87, 0.12, 'F.SilkS') + line(-1.62, 1.87, -1.62, -1.87, 0.12, 'F.SilkS')
       + rect(-1.75, -2.0, 4.25, 2.0, 0.05, 'F.CrtYd') + rect(-1.5, -1.75, 4.0, 1.75, 0.1, 'F.Fab')
       + '\t(fp_text user "${REFERENCE}"\n\t\t(at 1.25 0 0)\n\t\t(layer "F.Fab")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 0.92 0.92)\n'
       '\t\t\t\t(thickness 0.138)\n\t\t\t)\n\t\t)\n\t)\n'
       + pad('1', '0') + pad('2', '2.5') + '\t(embedded_fonts no)\n)\n')

# Zero 2 W kopfueber auf der Buchsenleiste (Betreiber, 15.10.2026): KiCad-Bauform Raspberry_Pi_Zero_Socketed_THT_FaceDown_MountingHoles
# (Umriss 30 x 65 mm, Loecher 23 x 58 mm, Pin 1 an der Seite der SD-Karte; geprueft gegen datenblaetter/RaspberryPi_Zero2W-Mechanik_2021-10.pdf),
# dazu Aufdruck, damit der Zero nur richtig herum aufgesteckt wird. Koordinaten der Bauform: Seite SD-Karte oben (y = -8,37),
# Buchsen an der Kante x = 25,23: HDMI y = 4,03, USB Daten y = 33,03, USB Strom y = 45,63 (12,4 / 41,4 / 54 mm vom Ende).
ZERO_NAME = 'Raspberry_Pi_Zero_kopfueber'
ZERO_SRC = 'C:/Program Files/KiCad/10.0/share/kicad/footprints/Module.pretty/Raspberry_Pi_Zero_Socketed_THT_FaceDown_MountingHoles.kicad_mod'


def silk(txt, x, y, rot=0, size=1.2):
    return ('\t(fp_text user "%s"\n\t\t(at %s %s %s)\n\t\t(layer "F.SilkS")\n\t\t(effects\n\t\t\t(font\n'
            '\t\t\t\t(size %s %s)\n\t\t\t\t(thickness %s)\n\t\t\t)\n\t\t)\n\t)\n') % (txt, x, y, rot, size, size, round(size * 0.15, 3))


def zero():
    t = open(ZERO_SRC, encoding='utf-8').read()
    t = t.replace('(footprint "Raspberry_Pi_Zero_Socketed_THT_FaceDown_MountingHoles"', '(footprint "%s"' % ZERO_NAME, 1)
    t = t.replace('"Raspberry_Pi_Zero_Socketed_THT_FaceDown_MountingHoles"', '"%s"' % ZERO_NAME)
    marks = (silk('SD-Karte', 10.23, -6.4) + silk('HDMI', 22.8, 4.03, 90) + silk('USB Daten', 22.8, 33.03, 90)
             + silk('USB Strom', 22.8, 45.63, 90) + silk('Pin 1', 4.4, 0) + silk('ZERO KOPFÜBER', 12.5, 24.13, 90, 2.0)
             + silk('Bauteilseite nach unten', 16.5, 24.13, 90, 1.5))
    i = t.index('\t(embedded_fonts') if '\t(embedded_fonts' in t else t.index('\t(model')
    return t[:i] + marks + t[i:]


if __name__ == '__main__':
    write(sys.argv[1])
