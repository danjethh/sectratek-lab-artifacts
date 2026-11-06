"""Read-only streaming ZIP reader (ZIP64 aware) for very large archives.

`scan` walks the central directory in chunks and keeps only the entries whose name passes a filter, so an
archive of hundreds of gigabytes is indexed without unpacking it and without building a ZipInfo for every member.
`extract` and `read_head` read single members (stored or deflated) through the local header.
Each entry is a dict: name, csize, usize, off, method, mtime (epoch seconds or None), mtime_src ("UT" or "NTFS").
"""
import os
import struct
import zlib

_EOCD = b"PK\x05\x06"
_EOCD64_LOC = b"PK\x06\x07"
_CDH = b"PK\x01\x02"
_NTFS_TO_UNIX = 369 * 365 * 86400 + 89 * 86400  # seconds from 1601-01-01 to 1970-01-01 (369 years, 89 leap days)


def _find_eocd(f, size):
    tail = min(size, 70000)
    f.seek(size - tail)
    buf = f.read(tail)
    i = buf.rfind(_EOCD)
    if i < 0:
        raise ValueError("no end-of-central-directory record")
    (_, _disk, _cd_disk, _n_disk, n_total, cd_size, cd_off, _clen) = struct.unpack("<4sHHHHIIH", buf[i:i + 22])
    if cd_off == 0xFFFFFFFF or n_total == 0xFFFF or cd_size == 0xFFFFFFFF:
        loc = buf[i - 20:i]
        if loc[:4] != _EOCD64_LOC:
            raise ValueError("zip64 locator missing")
        _, _, eocd64_off, _ = struct.unpack("<4sIQI", loc)
        f.seek(eocd64_off)
        e64 = f.read(56)
        (_sig, _, _, _, _, _, _nd, n_total64, cd_size64, cd_off64) = struct.unpack("<4sQHHIIQQQQ", e64)
        return cd_off64, cd_size64, n_total64
    return cd_off, cd_size, n_total


def _parse_extra(extra, csize, usize, off):
    """Return (csize, usize, off, mtime or None, source) from the extra field."""
    i = 0
    mt = None
    src = None
    while i + 4 <= len(extra):
        hid, hl = struct.unpack("<HH", extra[i:i + 4])
        body = extra[i + 4:i + 4 + hl]
        if hid == 0x0001:  # zip64 extended information
            j = 0
            if usize == 0xFFFFFFFF and j + 8 <= len(body):
                usize = struct.unpack("<Q", body[j:j + 8])[0]
                j += 8
            if csize == 0xFFFFFFFF and j + 8 <= len(body):
                csize = struct.unpack("<Q", body[j:j + 8])[0]
                j += 8
            if off == 0xFFFFFFFF and j + 8 <= len(body):
                off = struct.unpack("<Q", body[j:j + 8])[0]
                j += 8
        elif hid == 0x5455 and len(body) >= 5:  # extended timestamp
            if body[0] & 1:
                mt = struct.unpack("<i", body[1:5])[0]
                src = "UT"
        elif hid == 0x000A and len(body) >= 32 and mt is None:  # NTFS times
            tag, sz = struct.unpack("<HH", body[4:8])
            if tag == 1 and sz >= 24:
                ft = struct.unpack("<Q", body[8:16])[0]
                if ft:
                    mt = ft / 1e7 - _NTFS_TO_UNIX
                    src = "NTFS"
        i += 4 + hl
    return csize, usize, off, mt, src


def scan(path, name_filter, chunk=1 << 24):
    """Yield an entry dict for every central-directory entry whose name passes name_filter(name) -> bool."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        cd_off, cd_size, _n_total = _find_eocd(f, size)
        f.seek(cd_off)
        remaining = cd_size
        buf = b""
        pos = 0
        while True:
            if len(buf) - pos < 46 + 65535 * 3 and remaining > 0:
                take = min(chunk, remaining)
                buf = buf[pos:] + f.read(take)
                remaining -= take
                pos = 0
            if len(buf) - pos < 46:
                break
            if buf[pos:pos + 4] != _CDH:
                break
            (_, _vm, _vn, flag, meth, _t, _d, _crc, csize, usize, nl, el, cl, _dsk, _ia, _ea, off) = struct.unpack(
                "<4sHHHHHHIIIHHHHHII", buf[pos:pos + 46])
            name_b = buf[pos + 46:pos + 46 + nl]
            name = name_b.decode("utf-8", "replace") if flag & 0x800 else name_b.decode("cp437", "replace")
            if name_filter(name):
                extra = buf[pos + 46 + nl:pos + 46 + nl + el]
                csize2, usize2, off2, mt, src = _parse_extra(extra, csize, usize, off)
                yield {"name": name, "csize": csize2, "usize": usize2, "off": off2, "method": meth,
                       "mtime": mt, "mtime_src": src}
            pos += 46 + nl + el + cl


def _data_start(f, ent):
    f.seek(ent["off"])
    lh = f.read(30)
    if lh[:4] != b"PK\x03\x04":
        raise ValueError("bad local header")
    nl, el = struct.unpack("<HH", lh[26:30])
    f.seek(ent["off"] + 30 + nl + el)


def extract(path, ent, out_path, max_bytes=4 << 30):
    """Copy one member (stored or deflated) to out_path. The archive is only read."""
    with open(path, "rb") as f:
        _data_start(f, ent)
        left = ent["csize"]
        if left > max_bytes:
            raise ValueError("member too large")
        with open(out_path, "wb") as o:
            if ent["method"] == 0:
                while left > 0:
                    b = f.read(min(1 << 22, left))
                    left -= len(b)
                    if not b:
                        break
                    o.write(b)
            elif ent["method"] == 8:
                dz = zlib.decompressobj(-15)
                while left > 0:
                    b = f.read(min(1 << 22, left))
                    left -= len(b)
                    if not b:
                        break
                    o.write(dz.decompress(b))
                o.write(dz.flush())
            else:
                raise ValueError("unsupported compression method %d" % ent["method"])


def read_head(path, ent, n):
    """Return the first n uncompressed bytes of a member."""
    with open(path, "rb") as f:
        _data_start(f, ent)
        if ent["method"] == 0:
            return f.read(min(n, ent["csize"]))
        if ent["method"] != 8:
            raise ValueError("unsupported compression method %d" % ent["method"])
        dz = zlib.decompressobj(-15)
        out = b""
        left = ent["csize"]
        while len(out) < n and left > 0:
            b = f.read(min(65536, left))
            left -= len(b)
            out += dz.decompress(b, n - len(out))
            if dz.unconsumed_tail:
                break
        return out[:n]
