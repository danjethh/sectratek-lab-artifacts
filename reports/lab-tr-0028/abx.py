"""Reader and writer for Android Binary XML (ABX), standard library only.

Format as in the AOSP classes BinaryXmlSerializer and BinaryXmlPullParser: magic "ABX\\0", then tokens;
the low nibble of a token byte is the token, the high nibble the value type. Names are interned in a
table that grows as new names are written.

parse(bytes) -> list of events ['start', name, {attr: value}], ['end', name], ['text', str]
dump(events) -> bytes   (used by the invented-archive generator)
"""
import struct

START_DOC, END_DOC, START_TAG, END_TAG, TEXT, CDSECT, ENTITY_REF, IGN_WS, PI, COMMENT, DOCDECL = range(11)
ATTRIBUTE = 15
(T_NULL, T_STRING, T_STRING_INTERNED, T_BYTES_HEX, T_BYTES_BASE64, T_INT, T_INT_HEX, T_LONG, T_LONG_HEX,
 T_FLOAT, T_DOUBLE, T_TRUE, T_FALSE) = range(1, 14)
MAGIC = b"ABX\x00"


def is_abx(data):
    return data[:4] == MAGIC


def parse(data):
    if not is_abx(data):
        raise ValueError("not ABX")
    p = 4
    interned = []
    events = []
    stack = []

    def u16():
        nonlocal p
        v = struct.unpack(">H", data[p:p + 2])[0]
        p += 2
        return v

    def utf():
        nonlocal p
        n = u16()
        s = data[p:p + n].decode("utf-8", "replace")
        p += n
        return s

    def interned_string():
        idx = u16()
        if idx == 0xFFFF:
            s = utf()
            interned.append(s)
            return s
        return interned[idx]

    while p < len(data):
        byte = data[p]
        p += 1
        token, vtype = byte & 0x0F, byte >> 4
        if token == START_DOC:
            continue
        if token == END_DOC:
            break
        if token == START_TAG:
            name = interned_string()
            stack.append((name, {}))
            events.append(["start", name, stack[-1][1]])
        elif token == END_TAG:
            name = interned_string()
            stack.pop()
            events.append(["end", name])
        elif token == ATTRIBUTE:
            name = interned_string()
            if vtype == T_STRING:
                v = utf()
            elif vtype == T_STRING_INTERNED:
                v = interned_string()
            elif vtype in (T_INT, T_INT_HEX):
                v = struct.unpack(">i", data[p:p + 4])[0]
                p += 4
            elif vtype in (T_LONG, T_LONG_HEX):
                v = struct.unpack(">q", data[p:p + 8])[0]
                p += 8
            elif vtype == T_FLOAT:
                v = struct.unpack(">f", data[p:p + 4])[0]
                p += 4
            elif vtype == T_DOUBLE:
                v = struct.unpack(">d", data[p:p + 8])[0]
                p += 8
            elif vtype == T_TRUE:
                v = True
            elif vtype == T_FALSE:
                v = False
            elif vtype in (T_BYTES_HEX, T_BYTES_BASE64):
                n = u16()
                v = data[p:p + n]
                p += n
            elif vtype == T_NULL:
                v = None
            else:
                raise ValueError("attribute type %d" % vtype)
            stack[-1][1][name] = v
        elif token in (TEXT, CDSECT, COMMENT, IGN_WS, PI, DOCDECL, ENTITY_REF):
            events.append(["text", utf() if vtype == T_STRING else ""])
        else:
            raise ValueError("token %d at offset %d" % (token, p))
    return events


def dump(events):
    """Serialise events as produced by parse(); integers are written as 32 bit ints when they fit,
    otherwise as 64 bit longs; strings as plain strings."""
    out = bytearray(MAGIC)
    table = {}

    def u16(v):
        out.extend(struct.pack(">H", v))

    def utf(s):
        b = s.encode("utf-8")
        u16(len(b))
        out.extend(b)

    def name(s):
        if s in table:
            u16(table[s])
        else:
            u16(0xFFFF)
            utf(s)
            table[s] = len(table)

    out.append(START_DOC | (T_NULL << 4))
    for ev in events:
        if ev[0] == "start":
            out.append(START_TAG | (T_STRING_INTERNED << 4))
            name(ev[1])
            for k, v in ev[2].items():
                if isinstance(v, bool):
                    out.append(ATTRIBUTE | ((T_TRUE if v else T_FALSE) << 4))
                    name(k)
                elif isinstance(v, int):
                    if -2 ** 31 <= v < 2 ** 31:
                        out.append(ATTRIBUTE | (T_INT << 4))
                        name(k)
                        out.extend(struct.pack(">i", v))
                    else:
                        out.append(ATTRIBUTE | (T_LONG << 4))
                        name(k)
                        out.extend(struct.pack(">q", v))
                else:
                    out.append(ATTRIBUTE | (T_STRING << 4))
                    name(k)
                    utf(str(v))
        elif ev[0] == "end":
            out.append(END_TAG | (T_STRING_INTERNED << 4))
            name(ev[1])
        else:
            out.append(TEXT | (T_STRING << 4))
            utf(ev[1])
    out.append(END_DOC | (T_NULL << 4))
    return bytes(out)
