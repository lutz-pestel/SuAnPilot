# Erzeugt KiCad-10-Schaltplanblaetter aus Python-Beschreibungen. Linie B (SMD). Version 00.03, Stand 16.10.2026.
# Neu gegen Linie A: Feld "LCSC Part #" je Bauteil aus LCSC (Wert -> JLCPCB-Teilenummer).
import copy, math, uuid, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import parse, dump, find, first, Q

LIBDIR = 'C:/Program Files/KiCad/10.0/share/kicad/symbols/'
PROJECT = 'Robnet-Analyse'
NS = uuid.UUID('6a1f3c2e-0000-4000-8000-526f626e6574')
_libcache = {}
_pwr = [0]


def uid(*key):
    return Q(str(uuid.uuid5(NS, '/'.join(str(k) for k in key))))


def r(v):
    return ('%.4f' % v).rstrip('0').rstrip('.') if v != int(v) else str(int(v))


PROJLIB = {}          # Bibliotheksname -> Pfad der .kicad_sym (Projektbibliothek)
LCSC = {}             # Wert -> JLCPCB-Teilenummer (nur Teile, die JLCPCB bestueckt)


def _flat(syms, name):
    s = copy.deepcopy(syms[name])
    ext = first(s, 'extends')
    if not ext:
        return s
    parent = _flat(syms, ext[1])
    own = {p[1]: p for p in find(s, 'property')}
    pprops = find(parent, 'property')
    props = [own.get(p[1], p) for p in pprops] + [p for p in find(s, 'property') if p[1] not in {q[1] for q in pprops}]
    head = [x for x in parent[2:] if not (isinstance(x, list) and x[0] in ('property', 'symbol', 'embedded_fonts', 'extends'))]
    units = []
    for u in find(parent, 'symbol'):
        u = copy.deepcopy(u); u[1] = Q(name + u[1][len(parent[1]):]); units.append(u)
    return ['symbol', Q(name)] + head + props + units + find(parent, 'embedded_fonts')


def lib_symbol(lib_id):
    if lib_id in _libcache:
        return _libcache[lib_id]
    lib, name = lib_id.split(':')
    path = PROJLIB.get(lib, LIBDIR + lib + '.kicad_sym')
    root = parse(open(path, encoding='utf-8').read())[0]
    syms = {x[1]: x for x in find(root, 'symbol')}
    s = _flat(syms, name)
    s[1] = Q(lib_id)
    _libcache[lib_id] = s
    return s


def pins_of(lib_id):
    s = lib_symbol(lib_id)
    res = {}
    for u in find(s, 'symbol'):
        for p in find(u, 'pin'):
            a = first(p, 'at')
            res[first(p, 'number')[1]] = (float(a[1]), float(a[2]))
    return res


def xf(px, py, rot, mirror):
    if mirror == 'y':
        px = -px
    elif mirror == 'x':
        py = -py
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return px * c - py * s, px * s + py * c


def font(size=1.27, bold=False, justify=None, hide=False):
    f = ['font', ['size', r(size), r(size)]]
    if bold:
        f.append(['bold', 'yes'])
    e = ['effects', f]
    if justify:
        e.append(['justify'] + justify.split())
    if hide:
        e.append(['hide', 'yes'])
    return e


class Sym:
    def __init__(self, sheet, lib_id, ref, value, x, y, rot=0, mirror=None, fp='', fields=None, hide_value=False, dnp=False):
        self.sheet, self.lib_id, self.ref, self.value = sheet, lib_id, ref, value
        self.x, self.y, self.rot, self.mirror, self.fp = x, y, rot, mirror, fp
        self.fields = fields or {}
        self.hide_value, self.dnp = hide_value, dnp
        self._pins = pins_of(lib_id)

    def pin(self, n):
        px, py = self._pins[str(n)]
        dx, dy = xf(px, py, self.rot, self.mirror)
        return (round(self.x + dx, 4), round(self.y - dy, 4))

    def sexpr(self):
        s = lib_symbol(self.lib_id)
        props = {p[1]: p for p in find(s, 'property')}
        out = ['symbol', ['lib_id', Q(self.lib_id)], ['at', r(self.x), r(self.y), r(self.rot)]]
        if self.mirror:
            out.append(['mirror', self.mirror])
        out += [['unit', '1'], ['body_style', '1'], ['exclude_from_sim', 'no'], ['in_bom', 'no' if self.ref.startswith('#') else 'yes'],
                ['on_board', 'no' if self.ref.startswith('#') else 'yes'], ['in_pos_files', 'yes'], ['dnp', 'yes' if self.dnp else 'no'],
                ['uuid', uid(self.sheet.name, self.ref)]]
        fangle = self.rot % 180
        for key in ('Reference', 'Value', 'Footprint', 'Datasheet', 'Description'):
            p = props.get(key)
            if key in self.fields:
                fx, fy, just = self.fields[key]
            elif p is not None:
                a = first(p, 'at'); dx, dy = xf(float(a[1]), float(a[2]), self.rot, self.mirror)
                fx, fy, just = self.x + dx, self.y - dy, None
            else:
                fx, fy, just = self.x, self.y, None
            val = {'Reference': self.ref, 'Value': self.value, 'Footprint': self.fp}.get(key, p[2] if p is not None else '')
            hidden = key in ('Footprint', 'Datasheet', 'Description') or (key == 'Value' and self.hide_value) or \
                (key == 'Reference' and self.ref.startswith('#'))
            prop = ['property', Q(key), Q(val), ['at', r(fx), r(fy), r(fangle)]]
            if hidden:
                prop.append(['hide', 'yes'])
            prop += [['show_name', 'no'], ['do_not_autoplace', 'no'], font(justify=just)]
            out.append(prop)
        if self.value in LCSC and not self.ref.startswith('#'):
            out.append(['property', Q('LCSC Part #'), Q(LCSC[self.value]), ['at', r(self.x), r(self.y), '0'], ['hide', 'yes'],
                        ['show_name', 'no'], ['do_not_autoplace', 'no'], font()])
        for n in self._pins:
            out.append(['pin', Q(n), ['uuid', uid(self.sheet.name, self.ref, 'pin', n)]])
        out.append(['instances', ['project', Q(PROJECT), ['path', Q(self.sheet.path), ['reference', Q(self.ref)], ['unit', '1']]]])
        return out


class Sheet:
    def __init__(self, name, filename, title, paper='A3', root_uuid=None, path=None, date='2026-10-16', rev='00.01'):
        self.name, self.filename, self.title, self.paper = name, filename, title, paper
        self.uuid = root_uuid or uid('sheetfile', filename)
        self.path = path            # Instanzpfad der Bauteile dieses Blatts
        self.date, self.rev = date, rev
        self.items, self.syms, self.wires, self.junctions = [], [], [], []
        self.subsheets = []

    def sym(self, *a, **k):
        s = Sym(self, *a, **k); self.syms.append(s); return s

    def power(self, kind, x, y, rot=0):
        _pwr[0] += 1
        return self.sym('power:' + kind, '#PWR%03d' % _pwr[0], kind, x, y, rot)

    def lpower(self, kind, x, y, rot=0):
        # blattlokales Versorgungszeichen aus der Projektbibliothek
        _pwr[0] += 1
        return self.sym('Robnet-Analyse:' + kind, '#PWR%03d' % _pwr[0], kind, x, y, rot)

    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            if a != b:
                self.wires.append((a, b))

    def junction(self, x, y):
        self.junctions.append((x, y))

    def text(self, s, x, y, size=1.27, bold=False, justify='left bottom', angle=0):
        self.items.append(['text', Q(s), ['exclude_from_sim', 'no'], ['at', r(x), r(y), r(angle)], font(size, bold, justify),
                           ['uuid', uid(self.name, 'text', s, x, y)]])

    def frame(self, x1, y1, x2, y2, title=None):
        self.items.append(['rectangle', ['start', r(x1), r(y1)], ['end', r(x2), r(y2)], ['stroke', ['width', '0'], ['type', 'dash']],
                           ['fill', ['type', 'none']], ['uuid', uid(self.name, 'rect', x1, y1)]])
        if title:
            self.text(title, x1 + 1.27, y1 + 3.81, 1.524, True)

    def hlabel(self, name, x, y, shape='input', angle=0):
        just = 'left' if angle in (0, 90) else 'right'
        self.items.append(['hierarchical_label', Q(name), ['shape', shape], ['at', r(x), r(y), r(angle)], font(justify=just),
                           ['uuid', uid(self.name, 'hl', name)]])

    def no_connect(self, x, y):
        self.items.append(['no_connect', ['at', r(x), r(y)], ['uuid', uid(self.name, 'nc', x, y)]])

    def subsheet(self, name, filename, x, y, w, h, pins):
        # pins: Liste (name, typ, seite 'L'/'R'/'T'/'B', versatz in mm vom Ecke oben/links)
        su = uid('sheet', name)
        self.subsheets.append((name, filename, su))
        pp = {}
        out = ['sheet', ['at', r(x), r(y)], ['size', r(w), r(h)], ['exclude_from_sim', 'no'], ['in_bom', 'yes'], ['on_board', 'yes'],
               ['dnp', 'no'], ['fields_autoplaced', 'yes'], ['stroke', ['width', '0.1524'], ['type', 'solid']],
               ['fill', ['color', '0', '0', '0', '0']], ['uuid', su],
               ['property', Q('Sheetname'), Q(name), ['at', r(x), r(y - 0.7112), '0'], ['show_name', 'no'], ['do_not_autoplace', 'no'],
                font(1.524, True, 'left bottom')],
               ['property', Q('Sheetfile'), Q(filename), ['at', r(x), r(y + h + 0.5842), '0'], ['show_name', 'no'], ['do_not_autoplace', 'no'],
                font(justify='left top')]]
        for pname, typ, side, off in pins:
            if side == 'L':
                at, ang, just = (x, y + off), 180, 'left'
            elif side == 'R':
                at, ang, just = (x + w, y + off), 0, 'right'
            elif side == 'T':
                at, ang, just = (x + off, y), 90, 'right'
            else:
                at, ang, just = (x + off, y + h), 270, 'left'
            out.append(['pin', Q(pname), typ, ['at', r(at[0]), r(at[1]), r(ang)], ['uuid', uid('sheetpin', name, pname)], font(justify=just)])
            pp[pname] = (round(at[0], 4), round(at[1], 4))
        out.append(['instances', ['project', Q(PROJECT), ['path', Q(self.path), ['page', Q(str(len(self.subsheets) + 1))]]]])
        self.items.append(out)
        return pp, su

    def sexpr(self):
        libs = []
        seen = set()
        for s in self.syms:
            if s.lib_id not in seen:
                seen.add(s.lib_id); libs.append(lib_symbol(s.lib_id))
        out = ['kicad_sch', ['version', '20260306'], ['generator', Q('eeschema')], ['generator_version', Q('10.0')], ['uuid', self.uuid],
               ['paper', Q(self.paper)],
               ['title_block', ['title', Q(self.title)], ['date', Q(self.date)], ['rev', Q(self.rev)], ['company', Q('SuAn-Autopilot-Projekt')]],
               ['lib_symbols'] + libs]
        for (x, y) in self.junctions:
            out.append(['junction', ['at', r(x), r(y)], ['diameter', '0'], ['color', '0', '0', '0', '0'], ['uuid', uid(self.name, 'j', x, y)]])
        for i, (a, b) in enumerate(self.wires):
            out.append(['wire', ['pts', ['xy', r(a[0]), r(a[1])], ['xy', r(b[0]), r(b[1])]], ['stroke', ['width', '0'], ['type', 'default']],
                        ['uuid', uid(self.name, 'w', a, b)]])
        out += self.items
        out += [s.sexpr() for s in self.syms]
        if self.path.count('/') == 1:
            out.append(['sheet_instances', ['path', Q('/'), ['page', Q('1')]]])
        out.append(['embedded_fonts', 'no'])
        return out

    def write(self, folder):
        with open(os.path.join(folder, self.filename), 'w', encoding='utf-8', newline='\n') as f:
            f.write(dump(self.sexpr()) + '\n')
