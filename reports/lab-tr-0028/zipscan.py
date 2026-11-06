"""Read-only streaming reader for the central directory of a ZIP archive (ZIP64 aware).

Keeps only the entries whose name passes a filter, so a very large archive of a file system can be
listed without building one object per member. File times are taken from the extended-timestamp or the
NTFS extra field when present (these are the times of the original files), not from the DOS fields.
Standard library only.
"""
import datetime
import os
import struct
import zlib

EOCD = b"PK\x05\x06"
EOCD64_LOC = b"PK\x06\x07"
CDH = b"PK\x01\x02"


def _find_eocd(f, size):
    tail = min(size, 70000)
    f.seek(size - tail)
    buf = f.read(tail)
    i = buf.rfind(EOCD)
    if i < 0:
        raise ValueError("no end-of-central-directory record")
    (_, _disk, _cd_disk, _n_disk, n_total, cd_size, cd_off, _clen) = struct.unpack("<4sHHHHIIH", buf[i:i + 22])
    if cd_off == 0xFFFFFFFF or n_total == 0xFFFF or cd_size == 0xFFFFFFFF:
        loc = buf[i - 20:i]
        if loc[:4] != EOCD64_LOC:
            raise ValueError("zip64 locator missing")
        _, _, eocd64_off, _ = struct.unpack("<4sIQI", loc)
        f.seek(eocd64_off)
        e64 = f.read(56)
        (_sig, _, _, _, _, _, _n_disk64, n_total64, cd_size64, cd_off64) = struct.unpack("<4sQHHIIQQQQ", e64)
        return cd_off64, cd_size64, n_total64
    return cd_off, cd_size, n_total


def _dos_datetime(d, t):
    try:
        return datetime.datetime(1980 + (d >> 9), (d >> 5) & 15, d & 31, t >> 11, (t >> 5) & 63, (t & 31) * 2)
    except ValueError:
        return None


def _parse_extra(extra, csize, usize, off):
    """Return (csize, usize, off, mtime as UTC epoch seconds or None, source of the time)."""
    i = 0
    mtime = None
    src = None
    while i + 4 <= len(extra):
        hid, hl = struct.unpack("<HH", extra[i:i + 4])
        body = extra[i + 4:i + 4 + hl]
        if hid == 0x0001:  # zip64 sizes and offset
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
                mtime = struct.unpack("<i", body[1:5])[0]
                src = "UT"
        elif hid == 0x000A and len(body) >= 32 and mtime is None:  # NTFS times
            tag, size = struct.unpack("<HH", body[4:8])
            if tag == 1 and size >= 24:
                ft = struct.unpack("<Q", body[8:16])[0]
                if ft:
                    mtime = ft / 1e7 - 11644473600
                    src = "NTFS"
        i += 4 + hl
    return csize, usize, off, mtime, src


def scan(path, name_filter, chunk=1 << 24):
    """Yield one dict per member whose name passes name_filter(name) -> bool."""
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
            if len(buf) - pos < 46 or buf[pos:pos + 4] != CDH:
                break
            (_, _vm, _vn, flag, method, t, d, _crc, csize, usize, nl, el, cl, _dsk, _ia, _ea, off) = struct.unpack(
                "<4sHHHHHHIIIHHHHHII", buf[pos:pos + 46])
            name_b = buf[pos + 46:pos + 46 + nl]
            name = name_b.decode("utf-8", "replace") if flag & 0x800 else name_b.decode("cp437", "replace")
            if name_filter(name):
                extra = buf[pos + 46 + nl:pos + 46 + nl + el]
                csize2, usize2, off2, mtime, src = _parse_extra(extra, csize, usize, off)
                dt = _dos_datetime(d, t)
                yield {"name": name, "csize": csize2, "usize": usize2, "off": off2, "method": method,
                       "mtime": mtime, "mtime_src": src, "dos": dt.isoformat() if dt else None}
            pos += 46 + nl + el + cl


def _data_start(f, ent):
    f.seek(ent["off"])
    lh = f.read(30)
    if lh[:4] != b"PK\x03\x04":
        raise ValueError("bad local header")
    nl, el = struct.unpack("<HH", lh[26:30])
    f.seek(ent["off"] + 30 + nl + el)


def read_member(path, ent, max_bytes=64 << 20):
    """Return the uncompressed bytes of a member (stored or deflated), up to max_bytes."""
    if ent["usize"] > max_bytes:
        raise ValueError("member too large")
    with open(path, "rb") as f:
        _data_start(f, ent)
        raw = f.read(ent["csize"])
    if ent["method"] == 0:
        return raw
    if ent["method"] == 8:
        return zlib.decompress(raw, -15)
    raise ValueError("unsupported compression method %d" % ent["method"])


def extract(path, ent, out_path, max_bytes=4 << 30):
    """Copy one member to out_path (used for SQLite files, which must be opened from a real file)."""
    data = read_member(path, ent, max_bytes)
    with open(out_path, "wb") as o:
        o.write(data)
