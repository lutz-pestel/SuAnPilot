# Minimaler S-Ausdruck-Leser/-Schreiber fuer KiCad-Dateien. Version 00.01, Stand 15.10.2026.
import re
TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
BS = chr(92)


class Q(str):   # gequoteter String
    pass


def unesc(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == BS and i + 1 < len(s):
            c = s[i + 1]
            out.append({'n': '\n', 't': '\t'}.get(c, c)); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


def parse(text):
    stack = [[]]
    for m in TOK.finditer(text):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        elif t[0] == '"':
            stack[-1].append(Q(unesc(t[1:-1])))
        else:
            stack[-1].append(t)
    return stack[0]


def esc(s):
    return '"' + s.replace(BS, BS + BS).replace('"', BS + '"').replace('\n', BS + 'n') + '"'


def dump(x, ind=0):
    if not isinstance(x, list):
        return esc(x) if isinstance(x, Q) else str(x)
    if all(not isinstance(e, list) for e in x):
        return '(' + ' '.join(dump(e) for e in x) + ')'
    out = '(' + ' '.join(dump(e) for e in x if not isinstance(e, list))
    for e in x:
        if isinstance(e, list):
            out += '\n' + '\t' * (ind + 1) + dump(e, ind + 1)
    return out + '\n' + '\t' * ind + ')'


def find(x, key):
    return [e for e in x if isinstance(e, list) and e and e[0] == key]


def first(x, key):
    f = find(x, key)
    return f[0] if f else None
