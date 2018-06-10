import re
from io import StringIO


class Struct:
    pass


def isint(s):
    try:
        int(s)
        return True
    except:
        return False


def sanitise(string):
    if isint(string[0]):
        string = '_' + string
    return re.sub('\W', '_', string)


def to_struct(string):
    in_paren = False
    struct = Struct()
    ii = 0
    for i, char in enumerate(string):
        if i == len(string) - 1:
            k, v = string[ii:].strip().split('=', 1)
            setattr(struct, sanitise(k), v)
            continue
        if char == ',' and not in_paren:
            k, v = string[ii:i].strip().split('=', 1)
            setattr(struct, sanitise(k), v)
            ii = i + 1
            continue
        if char == '(':
            in_paren = True
            continue
        if char == ')':
            assert in_paren, 'Attempted to close parenthesis without opening'
            in_paren = False
    return struct


class Genkey:
    def __init__(self, filename):
        self.filename = filename
        buf = StringIO()
        with open(filename) as f_in:
            buf.write(re.sub(r'\\\n\s*', '', f_in.read()))

        buf.seek(0)
        for line in buf.readlines():
            if line[0] == '!' or line[:3] == 'END' or len(line) < 2:
                continue

            if not line[0] == ' ':
                parent = self
                c, data = line.split(' ', 1)
            else:
                assert data, 'Attempted to nest with no parent'
                if parent is self:
                    parent = data
                c, data = line[1:].split(' ', 1)

            c = sanitise(c)
            data = to_struct(data)

            if hasattr(parent, c):
                if not isinstance(getattr(parent, c), (tuple, list)):
                    setattr(parent, c, [getattr(parent, c)])
                getattr(parent, c).append(data)
            else:
                setattr(parent, c, data)
        buf.close()
