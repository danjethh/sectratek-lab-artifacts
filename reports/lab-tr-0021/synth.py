"""Generator of small invented archives in the layout the readers expect.

The archives show the pipeline, not the findings of the report. Every device is invented: horizons are drawn from
simple distributions with round parameters (age-bounded stores sit near the limits published in the platform
sources; size-bounded stores get wide ranges). No value comes from a real device. Seeded: random.Random(seed),
fixed base dates, no wall clock, no system randomness.

Layouts (public file system layouts of the two platforms):
  iOS archive      root/private/var/...  members with extended-timestamp extra field
  Android archive  root/data/...         members with extended-timestamp extra field
  bug report       zip with one text member in dumpstate format (one of the reports is a zip inside a zip)
"""
import datetime
import io
import json
import os
import random
import shutil
import sqlite3
import struct
import tempfile
import zipfile

UTC = datetime.timezone.utc
DAY = 86400.0
HOUR = 3600.0
COCOA = int((datetime.datetime(2001, 1, 1, tzinfo=UTC) - datetime.datetime(1970, 1, 1, tzinfo=UTC)).total_seconds())
BASE = datetime.datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC).timestamp()   # invented acquisition date


# ---------------------------------------------------------------- archive writer
def write_zip(path, members):
    """members: list of (name, bytes, mtime or None). Extended-timestamp field (0x5455) carries the mtime."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data, mt in sorted(members, key=lambda m: m[0]):
            zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            if mt is not None:
                zi.extra = struct.pack("<HHBi", 0x5455, 5, 1, int(mt))
            z.writestr(zi, data)


# ---------------------------------------------------------------- SQLite with an hand-built write-ahead log
def _wal_checksum(data, s0, s1):
    words = struct.unpack("<%dI" % (len(data) // 4), data)
    for i in range(0, len(words), 2):
        s0 = (s0 + words[i] + s1) & 0xFFFFFFFF
        s1 = (s1 + words[i + 1] + s0) & 0xFFFFFFFF
    return s0, s1


def build_wal(old_db, new_db, page_size=4096, salt=(0x21212121, 0x12121212)):
    """Write-ahead log (file format of sqlite.org/walformat.html) that turns old_db into new_db: one frame per page
    that differs, the last frame a commit frame. Fixed salts make the bytes reproducible."""
    n_old, n_new = len(old_db) // page_size, len(new_db) // page_size
    magic = 0x377F0682  # checksums in little-endian word order
    hdr = struct.pack(">IIIIII", magic, 3007000, page_size, 0, salt[0], salt[1])
    s0, s1 = _wal_checksum(hdr, 0, 0)
    out = [hdr + struct.pack(">II", s0, s1)]
    changed = [p for p in range(1, n_new + 1)
               if p > n_old or old_db[(p - 1) * page_size:p * page_size] != new_db[(p - 1) * page_size:p * page_size]]
    for i, p in enumerate(changed):
        page = new_db[(p - 1) * page_size:p * page_size]
        commit = n_new if i == len(changed) - 1 else 0
        fh = struct.pack(">IIII", p, commit, salt[0], salt[1])
        s0, s1 = _wal_checksum(fh[:8] + page, s0, s1)
        out.append(fh + struct.pack(">II", s0, s1) + page)
    return b"".join(out)


def make_db(tmp, name, table, schema, rows_old, rows_new, insert_sql, wal_hides_old):
    """Return (db bytes, wal bytes or None). rows_old are rows a log can delete again: if wal_hides_old, the main file
    holds rows_old + rows_new and the log deletes rows_old; otherwise the main file holds rows_new only."""
    def build(path, rows):
        for ext in ("", "-wal", "-shm"):
            if os.path.exists(path + ext):
                os.remove(path + ext)
        con = sqlite3.connect(path)
        con.execute("PRAGMA page_size=4096")
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(schema)
        con.executemany(insert_sql, rows)
        con.commit()
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        con.close()
    pa = os.path.join(tmp, name + "_a.db")
    pb = os.path.join(tmp, name + "_b.db")
    if not wal_hides_old:
        build(pb, rows_new)
        return open(pb, "rb").read(), None
    build(pa, rows_old + rows_new)
    for ext in ("", "-wal", "-shm"):
        if os.path.exists(pb + ext):
            os.remove(pb + ext)
    shutil.copyfile(pa, pb)
    con = sqlite3.connect(pb)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("DELETE FROM %s WHERE Z_PK IN (%s)" % (table, ",".join(str(r[0]) for r in rows_old)))
    con.commit()
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    con.close()
    a, b = open(pa, "rb").read(), open(pb, "rb").read()
    return a, build_wal(a, b)


# ---------------------------------------------------------------- iOS
def _spread(rng, oldest, newest, n):
    """n times from oldest to newest, the first and the last exactly at the ends."""
    mid = sorted(rng.uniform(oldest, newest) for _ in range(n - 2))
    return [oldest] + mid + [newest]


def gen_ios(rng, tmp, tacq, lag_h, fail_clock=False, highvolume=False):
    """Return (members, truth) of one invented iOS archive; truth holds the horizons (days) the reader should find."""
    lag = (20 * 24 if fail_clock else lag_h) * HOUR
    newest = tacq - lag
    H = {"persist": rng.uniform(0.5, 10), "signpost": rng.uniform(2, 10), "special": rng.uniform(5, 30),
         "powerlog": rng.uniform(6, 8), "biome": rng.uniform(30, 60), "other": rng.uniform(20, 30),
         "signals": rng.uniform(100, 700) if rng.random() < 0.85 else rng.uniform(5, 20),
         "ic": 168 - rng.uniform(0, 1.5)}
    m = []
    truth = {}
    root = "root/private/var/"

    def old(hdays):  # oldest record: hdays before the acquisition (a device with a wrong clock ends earlier)
        return min(tacq - hdays * DAY, newest - 0.5 * DAY)

    def tracev3(sub, hdays, n):
        truth["ul_" + sub.lower()] = (tacq - int(old(hdays))) / DAY
        for i, t in enumerate(_spread(rng, old(hdays), newest, n)):
            body = bytes(rng.randrange(256) for _ in range(rng.randrange(200, 1200)))
            hdr = struct.pack("<I", 0x1000) + bytes(28) + struct.pack("<Q", int(t)) + bytes(8)
            m.append((root + "db/diagnostics/%s/%016x.tracev3" % (sub, rng.getrandbits(64)), hdr + body,
                      t + rng.uniform(0, 2 * HOUR) if i < n - 1 else t))
    tracev3("Persist", H["persist"], 5)
    tracev3("Special", H["special"], 4)
    if rng.random() < 0.6:
        tracev3("Signpost", H["signpost"], 3)
    if highvolume:
        tracev3("HighVolume", 1.0, 2)
    # knowledgeC: three streams; one long-lived stream sets the oldest record
    k_rows, pk = [], 0
    for stream, h, n in (("/app/inFocus", H["other"], 60), ("/device/isPluggedIn", H["other"] * 0.9, 25),
                         ("/discoverability/signals", H["signals"], 8), ("/knowledge-sync/deletion", H["other"] * 0.8, 3)):
        for t in _spread(rng, old(h), newest, n):
            pk += 1
            k_rows.append((pk, stream, t - COCOA))
    oldest_k = {}
    for _pk, stream, t in k_rows:
        oldest_k[stream] = min(oldest_k.get(stream, t), t)
    truth["knowledgec"] = (tacq - (min(oldest_k.values()) + COCOA)) / DAY
    truth["knowledgec_other"] = max((tacq - (t + COCOA)) / DAY for st, t in oldest_k.items()
                                    if st != "/discoverability/signals" and not st.startswith("/knowledge-sync"))
    db, _ = make_db(tmp, "k", "ZOBJECT", "CREATE TABLE ZOBJECT (Z_PK INTEGER PRIMARY KEY, ZSTREAMNAME TEXT, ZSTARTDATE REAL)",
                    [], k_rows, "INSERT INTO ZOBJECT VALUES (?,?,?)", False)
    m.append((root + "mobile/Library/CoreDuet/Knowledge/knowledgeC.db", db, newest))
    # interactionC: age-bounded at 24 weeks; in some devices the main file still holds rows the log has deleted
    hides = rng.random() < 0.65
    new_rows = [(i + 1000, t - COCOA) for i, t in enumerate(_spread(rng, old(H["ic"]), newest, 120))]
    old_rows = [(i + 1, t - COCOA) for i, t in enumerate(_spread(rng, old(H["ic"] + rng.uniform(2, 30)),
                                                                  old(H["ic"] + 1.5), 12))]
    truth["interactionc"] = (tacq - (min(r[1] for r in new_rows) + COCOA)) / DAY
    truth["interactionc_nowal"] = (tacq - (min(r[1] for r in (old_rows if hides else new_rows)) + COCOA)) / DAY
    db, wal = make_db(tmp, "i", "ZINTERACTIONS", "CREATE TABLE ZINTERACTIONS (Z_PK INTEGER PRIMARY KEY, ZSTARTDATE REAL)",
                      old_rows, new_rows, "INSERT INTO ZINTERACTIONS VALUES (?,?)", hides)
    m.append((root + "mobile/Library/CoreDuet/People/interactionC.db", db, newest))
    if wal:
        m.append((root + "mobile/Library/CoreDuet/People/interactionC.db-wal", wal, newest))
    # Biome segments: the name is the creation time in microseconds since 2001
    truth["biome_appinfocus"] = (tacq - old(H["biome"])) / DAY
    for t in _spread(rng, old(H["biome"]), min(newest, tacq - 9 * DAY), 8):
        m.append((root + "mobile/Library/Biome/streams/restricted/App.InFocus/local/%d" % int((t - COCOA) * 1e6),
                  bytes(rng.randrange(256) for _ in range(300)), t + rng.uniform(0, HOUR)))
    # powerlog archives: calendar date in the name
    d0 = datetime.datetime.fromtimestamp(tacq - H["powerlog"] * DAY, UTC).date()
    truth["powerlog_archives"] = (tacq - datetime.datetime(d0.year, d0.month, d0.day, 12, tzinfo=UTC).timestamp()) / DAY
    for i in range(int(H["powerlog"])):
        d = d0 + datetime.timedelta(days=i)
        m.append((root + "mobile/Library/BatteryLife/Archives/powerlog_%s_12:00:00_%04x.PLSQL.gz" % (d.isoformat(), i),
                  bytes(rng.randrange(256) for _ in range(120)), datetime.datetime(d.year, d.month, d.day, 23, tzinfo=UTC).timestamp()))
    return m, truth


# ---------------------------------------------------------------- Android
def gen_android(rng, tacq, lag_h, young=False, name_exception=False):
    lag = lag_h * HOUR
    newest = tacq - lag
    H = {"daily": rng.uniform(9, 10.2) if not young else rng.uniform(1, 3), "notif": rng.uniform(0.5, 1.5),
         "dropbox": rng.uniform(1, 3.1), "net": rng.uniform(75, 105), "proc": rng.uniform(1.5, 40),
         "battery": rng.uniform(5, 60), "any": rng.uniform(200, 700)}
    root = "root/data/"
    m = []

    def old(hdays):  # oldest record: hdays before the acquisition, but before the newest record
        return min(tacq - hdays * DAY, newest - 0.25 * DAY)

    truth = {k: (tacq - old(H[h])) / DAY for k, h in (("usage_daily", "daily"), ("usage_any", "any"),
                                                       ("notif_history", "notif"), ("dropbox", "dropbox"),
                                                       ("netstats", "net"))}

    def add(path, t, size=60):
        mt = min(t + rng.uniform(0.1, 3) * HOUR, newest)
        m.append((path, bytes(rng.randrange(256) for _ in range(size)), mt))

    ms = lambda t: int(t * 1000)
    day0 = old(H["daily"])
    for i in range(int(H["daily"]) + 1):
        add(root + "system_ce/0/usagestats/daily/%d" % ms(day0 + i * DAY), day0 + i * DAY)
    for k, span in (("weekly", 28), ("monthly", 180)):
        add(root + "system_ce/0/usagestats/%s/%d" % (k, ms(newest - span * DAY)), newest - span * DAY)
    add(root + "system_ce/0/usagestats/yearly/%d" % ms(old(H["any"])), old(H["any"]))
    for t in _spread(rng, old(H["notif"]), newest, 3):
        add(root + "system_ce/0/notification_history/history/%d" % ms(t), t)
    for i, t in enumerate(_spread(rng, old(H["dropbox"]), newest, 4)):
        add(root + "system/dropbox/system_app_crash@%d.txt.gz" % ms(t), t)
    for i, t in enumerate(_spread(rng, old(H["net"]), newest - 15 * DAY, 5)):
        add(root + "system/netstats/xt.%d-%d" % (ms(t), ms(t + 15 * DAY)), t)
    truth["procstats"] = (tacq - int(old(H["proc"]))) / DAY
    for i, t in enumerate(_spread(rng, old(H["proc"]), newest, 8)):
        d = datetime.datetime.fromtimestamp(t, UTC)
        add(root + "system/procstats/state-v2-%s.bin" % d.strftime("%Y-%m-%d-%H-%M-%S"), t)
    if rng.random() < 0.85:
        truth["vendor_battery_hist"] = (tacq - int(old(H["battery"]))) / DAY
        for t in _spread(rng, old(H["battery"]), newest, 4):
            d = datetime.datetime.fromtimestamp(t, UTC)
            add(root + "log/batterystats/newbatterystats%s" % d.strftime("%y%m%d%H%M%S"), t)
    if name_exception:  # one usage file whose name lies two hours after its modification time
        t = newest - 3 * DAY
        m.append((root + "system_ce/0/usagestats/daily/%d" % ms(t), bytes(40), t - 2 * HOUR))
    return m, truth


# ---------------------------------------------------------------- bug reports
def _fmt_line(t, tag, n):
    d = datetime.datetime.fromtimestamp(t, UTC)
    return "%02d-%02d %02d:%02d:%02d.%03d  1000  1001 I %s: message %d\n" % (
        d.month, d.day, d.hour, d.minute, d.second, d.microsecond // 1000, tag, n)


def gen_bugreport(rng, tacq, strays, body_hours, lines):
    d = datetime.datetime.fromtimestamp(tacq, UTC)
    out = ["== dumpstate: %s\n" % d.strftime("%Y-%m-%d %H:%M:%S"), "\n"]
    body_start = tacq - body_hours * HOUR
    syst = sorted(body_start - rng.uniform(2, 15) * DAY for _ in range(strays))
    syst += sorted(rng.uniform(body_start, tacq - 20) for _ in range(lines))
    out.append("------ SYSTEM LOG (logcat -v threadtime) ------\n")
    out += [_fmt_line(t, "SampleTag%d" % (i % 5), i) for i, t in enumerate(syst)]
    out.append("------ 0.060s was the duration of 'SYSTEM LOG' ------\n")
    ev_hours = rng.uniform(0.5, 2.9)
    ev = sorted(rng.uniform(tacq - ev_hours * HOUR, tacq - 20) for _ in range(max(50, lines // 4)))
    out.append("------ EVENT LOG (logcat -b events -v threadtime) ------\n")
    out += [_fmt_line(t, "event", i) for i, t in enumerate(ev)]
    out.append("------ 0.010s was the duration of 'EVENT LOG' ------\n")
    text = "".join(out).encode()
    name = "bugreport-invented-%s.txt" % d.strftime("%Y-%m-%d-%H-%M-%S")
    first_body = int(min(syst[strays:]))
    truth = {"logcat_system": (tacq - first_body) / DAY, "head_strays": strays,
             "logcat_system_oldest_line": (tacq - int(min(syst))) / DAY}
    return text, name, truth


# ---------------------------------------------------------------- corpus
def make_corpus(outdir, seed=21):
    """Write archives under outdir/archives and return the configuration (paths relative to outdir)."""
    rng = random.Random(seed)
    arch = os.path.join(outdir, "archives")
    os.makedirs(arch, exist_ok=True)
    devices = []
    tmp = tempfile.mkdtemp(prefix="tr21synth")
    try:
        # iOS: 15 invented devices (9 on a recent release, 6 on earlier ones); two tablets, one failing clock,
        # one extraction taken twice, four whose acquisition time is taken from the archive file time
        for i in range(15):
            tacq = BASE + i * DAY
            lag = rng.uniform(0.3, 40)
            fail = (i == 12)
            m, truth = gen_ios(rng, tmp, tacq, lag, fail_clock=fail, highvolume=(i in (3, 8)))
            name = "ios%02d.zip" % (i + 1)
            write_zip(os.path.join(arch, name), m)
            dev = {"id": "ios%02d" % (i + 1), "kind": "ios_ffs", "path": "archives/" + name,
                   "os_major": 26 if i < 9 else 17, "device_class": "tablet" if i in (4, 9) else "phone",
                   "vendor_group": "group1", "truth": truth}
            if i % 4 != 3:
                dev["acq_time"] = tacq
                dev["acq_source"] = "record"
            else:
                os.utime(os.path.join(arch, name), (tacq, tacq))
            if i == 1:
                dev["same_device_group"] = "pair1"
            devices.append(dev)
        # the second extraction of device ios02, six hours later
        tacq = BASE + DAY + 6 * HOUR
        m, truth = gen_ios(rng, tmp, tacq, 2.0)
        write_zip(os.path.join(arch, "ios02b.zip"), m)
        devices.append({"id": "ios02b", "kind": "ios_ffs", "path": "archives/ios02b.zip", "os_major": 26,
                        "device_class": "phone", "vendor_group": "group1", "acq_time": tacq, "acq_source": "record",
                        "same_device_group": "pair1", "truth": truth})
        # Android: 10 invented devices (7 on a recent release), one young device, one name exception
        for i in range(10):
            tacq = BASE + (20 + i) * DAY
            m, truth = gen_android(rng, tacq, rng.uniform(0.3, 30), young=(i == 7), name_exception=(i == 5))
            name = "and%02d.zip" % (i + 1)
            write_zip(os.path.join(arch, name), m)
            dev = {"id": "and%02d" % (i + 1), "kind": "android_ffs", "path": "archives/" + name,
                   "os_major": 16 if i < 7 else 13, "device_class": "phone", "vendor_group": "group1" if i < 8 else "group2",
                   "truth": truth}
            if i % 3 != 2:
                dev["acq_time"] = tacq
                dev["acq_source"] = "record"
            else:
                os.utime(os.path.join(arch, name), (tacq, tacq))
            devices.append(dev)
        # bug reports: six invented reports; three begin with head strays, one nested zip, one crosses a year end
        for i, (strays, hours, lines) in enumerate([(0, 0.5, 900), (1, 1.0, 1500), (3, 3.0, 2400), (0, 2.0, 1200),
                                                    (4, 0.8, 1000), (2, 1.5, 1800)]):
            tacq = BASE + (40 + i) * DAY if i != 5 else datetime.datetime(2027, 1, 4, 10, 0, tzinfo=UTC).timestamp()
            text, tname, truth = gen_bugreport(rng, tacq, strays, hours, lines)
            name = "br%02d.zip" % (i + 1)
            if i == 3:
                inner = io.BytesIO()
                write_zip(inner, [(tname, text, None)])
                write_zip(os.path.join(arch, name), [("bugreport-invented.zip", inner.getvalue(), None)])
            else:
                write_zip(os.path.join(arch, name), [(tname, text, None), ("version.txt", b"invented\n", None)])
            devices.append({"id": "br%02d" % (i + 1), "kind": "bugreport", "path": "archives/" + name,
                            "os_major": 16 if i < 4 else 14, "device_class": "phone", "vendor_group": "group1",
                            "truth": truth})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"note": "Invented devices; paths are relative to this file.", "devices": devices}


if __name__ == "__main__":
    import sys
    cfg = make_corpus(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 21)
    with open(os.path.join(sys.argv[1], "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1)
