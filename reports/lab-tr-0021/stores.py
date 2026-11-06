"""Store registry (report Table 2) and the read-only readers that date each store.

A reader returns, per store, the times of its records or files (seconds since 1970, UTC) summarised as
n_records / oldest / newest / first percentile, with records that cannot be right (before 2007, or later than
acquisition + 1 h) counted and left out of the oldest record (report Listing 1).

Readers: read_ios (archive of an iOS file system), read_android (archive of an Android /data tree),
read_bugreport (bug report text, inside a zip or a nested zip). All of them only read the archive.
"""
import contextlib
import datetime
import io
import os
import re
import shutil
import sqlite3
import struct
import tempfile
import zipfile

import ziputil

UTC = datetime.timezone.utc
COCOA = int((datetime.datetime(2001, 1, 1, tzinfo=UTC) - datetime.datetime(1970, 1, 1, tzinfo=UTC)).total_seconds())
MIN_PLAUSIBLE = datetime.datetime(2007, 1, 1, tzinfo=UTC).timestamp()
DAY = 86400.0
HOUR = 3600.0

# Clock rule (report Listing 1): a device is clock-checked if  T - 72 h <= D <= T + 1 h,
# D = newest device-clock time over the measured stores, T = acquisition time.
CLOCK_MAX_LAG_H = 72
CLOCK_MAX_AHEAD_H = 1

# Body of a bug-report log section (report Section 3.1)
BODY_GAP_S = 600.0
BODY_STRAY_FRACTION = 0.005

# ---------------------------------------------------------------- registry (report Table 2)
LABELS = {
    "ul_persist": "Unified log, Persist",
    "ul_signpost": "Unified log, Signpost",
    "ul_special": "Unified log, Special",
    "ul_highvolume": "Unified log, HighVolume",
    "powerlog_archives": "Powerlog archives",
    "biome_appinfocus": "Biome App.InFocus",
    "knowledgec": "knowledgeC, all records",
    "knowledgec_other": "knowledgeC, other streams",
    "interactionc": "interactionC",
    "usage_daily": "Usage statistics, daily",
    "usage_any": "Usage statistics, any interval",
    "notif_history": "Notification history",
    "dropbox": "DropBox entries",
    "netstats": "Network statistics",
    "procstats": "Process statistics",
    "vendor_battery_hist": "Battery history (vendor files)",
    "logcat_system": "Bug report, system log (body)",
    "logcat_events": "Bug report, event log (body)",
}

TABLE2 = [
    ("iOS full file system", [
        ("Unified log: Persist, Special, Signpost, HighVolume", "db/diagnostics/<stream>/*.tracev3",
         "File header start time, UTC [14]", "Hours to about 10 days [4]; a few days [11]"),
        ("knowledgeC", "CoreDuet/Knowledge/knowledgeC.db", "ZOBJECT.ZSTARTDATE, seconds since 2001",
         "About 4 weeks [10]; 28 to 30 days [13]"),
        ("interactionC", "CoreDuet/People/interactionC.db", "ZINTERACTIONS.ZSTARTDATE", "None found"),
        ("Biome App.InFocus", "Biome/streams/restricted/App.InFocus/local/",
         "Segment name, microseconds since 2001", "28 to 30 days (Biome data) [13]"),
        ("Powerlog archives", "BatteryLife/Archives/powerlog_<date>_*", "Calendar date in name (day, +-1 d)",
         "None found"),
    ]),
    ("Android full file system (user 0)", [
        ("Usage statistics", "usagestats/{daily, weekly, monthly, yearly}/", "Name, epoch ms",
         "Source: daily 10 d, weekly 4 wk, monthly 6 mo, yearly 2 y [9]"),
        ("Notification history", "notification_history/history/", "Name, epoch ms", "Source: 1 d [7]"),
        ("DropBox entries", "system/dropbox/<tag>@<ms>.*", "Name, epoch ms",
         "Source default: 3 d, 1,000 files, a size quota [5]"),
        ("Network statistics", "netstats/{xt, uid, uid_tag}.<start>-<end>", "Name (start), epoch ms",
         "Source: files of 15 d, deleted after 90 d (device and per-app) [6]"),
        ("Process statistics", "procstats/state-v2-<date>.bin", "Name, device local time (+-14 h)",
         "Source: 8 files [8]"),
        ("Battery history (vendor files)", "data/log/batterystats/", "Name, device local time (+-14 h)",
         "None found"),
    ]),
    ("Android bug report", [
        ("System log, event log", "SYSTEM LOG, EVENT LOG sections",
         "Line time, counted from the start of the body of the section (Section 3.1), against the report's header "
         "time; one device clock", "None found"),
    ]),
]


def table2_markdown():
    out = ["| Store | Where kept | Dating field and clock | Stated retention |", "|---|---|---|---|"]
    for grp, rows in TABLE2:
        out.append("| **%s** | | | |" % grp)
        for r in rows:
            out.append("| %s | %s | %s | %s |" % r)
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- helpers
def valid_mtime(e):
    mt = e.get("mtime")
    return mt if (mt is not None and e.get("mtime_src") and mt > MIN_PLAUSIBLE) else None


def summarise_times(ts, tacq, kind):
    """ts: record times (device clock). Drop impossible values; return the summary of the rest."""
    bad_low = [t for t in ts if t < MIN_PLAUSIBLE]
    bad_high = [t for t in ts if tacq is not None and t > tacq + HOUR]
    ok = sorted(t for t in ts if t >= MIN_PLAUSIBLE and (tacq is None or t <= tacq + HOUR))
    r = {"kind": kind, "n_records": len(ts), "n_clock_err_low": len(bad_low), "n_clock_err_high": len(bad_high)}
    if ok:
        r["oldest"] = ok[0]
        r["newest"] = ok[-1]
        if len(ok) >= 20:
            r["p01"] = ok[int(0.01 * (len(ok) - 1))]
    return r


def clock_rule(newest_device, tacq):
    """Return (verdict, lag in hours). Verdict is 'pass', 'fail' or 'no-anchor'."""
    if newest_device is None:
        return "no-anchor", None
    lag = tacq - newest_device
    ok = -CLOCK_MAX_AHEAD_H * HOUR <= lag <= CLOCK_MAX_LAG_H * HOUR
    return ("pass" if ok else "fail"), lag / HOUR


def body_start(times, gap=BODY_GAP_S, frac=BODY_STRAY_FRACTION):
    """Start of the body of a log section: after the last gap of >= gap seconds that is preceded by at most
    frac of the lines (and at least one line). Returns (time of the first body line, number of head strays)."""
    s = sorted(times)
    n = len(s)
    cap = max(1, int(frac * n))
    starts = [i + 1 for i in range(n - 1) if s[i + 1] - s[i] >= gap and (i + 1) <= cap]
    if starts:
        return s[starts[-1]], starts[-1]
    return s[0], 0


GRID_GAPS_MIN = (5, 10, 30, 60)
GRID_FRACTIONS = (0.001, 0.005, 0.01, 0.02, 0.05)


def body_grid(times):
    """Sensitivity of the body start to its two constants (report Section 5.4): how many of the gap and stray-fraction
    pairs give the same body start as the default pair, and whether all pairs up to a stray fraction of 2% do."""
    default = body_start(times)[0]
    same, upto2 = 0, []
    for g in GRID_GAPS_MIN:
        for fr in GRID_FRACTIONS:
            eq = body_start(times, g * 60.0, fr)[0] == default
            same += eq
            if fr <= 0.02:
                upto2.append(eq)
    return {"pairs": len(GRID_GAPS_MIN) * len(GRID_FRACTIONS), "same_as_default": same, "same_up_to_2pct": all(upto2)}


# ---------------------------------------------------------------- SQLite stores (copies, with and without the log)
def sqlite_span(zpath, ents, work, table, col, tacq, deep=False):
    """Copy the database (and its -wal) out of the archive and read the start dates twice: with the log applied
    and from the main file alone. With deep=True also per stream (knowledgeC)."""
    dbs = [e for e in ents if not e["name"].endswith(("-wal", "-shm"))]
    if not dbs:
        return None
    db = max(dbs, key=lambda e: e["usize"])
    wal = [e for e in ents if e["name"] == db["name"] + "-wal"]
    out = {}
    tmp = tempfile.mkdtemp(dir=work)
    try:
        for mode in ("wal", "nowal"):
            d = os.path.join(tmp, mode)
            os.makedirs(d)
            fp = os.path.join(d, "s.db")
            ziputil.extract(zpath, db, fp)
            if mode == "wal" and wal:
                ziputil.extract(zpath, wal[0], fp + "-wal")
            con = sqlite3.connect(fp)
            try:
                q = "SELECT %s FROM %s WHERE %s IS NOT NULL AND %s > 0" % (col, table, col, col)
                vals = sorted(v[0] + COCOA for v in con.execute(q) if isinstance(v[0], (int, float)))
                r = {"n": len(vals), "vals": vals}
                if mode == "wal" and deep:
                    sv = [v[0] + COCOA for v in con.execute(
                        "SELECT ZSTARTDATE FROM ZOBJECT WHERE ZSTREAMNAME='/app/inFocus' AND ZSTARTDATE>0")
                        if isinstance(v[0], (int, float))]
                    r["infocus_min"] = min(sv) if sv else None
                    r["streams"] = _stream_profile(con, tacq)
            finally:
                con.close()
            out[mode] = r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def _stream_profile(con, tacq):
    """Per-stream oldest record of knowledgeC (report Section 5.7, post hoc). Stream names have identifiers masked."""
    rows = con.execute("SELECT ZSTREAMNAME, MIN(ZSTARTDATE), COUNT(*) FROM ZOBJECT "
                       "WHERE ZSTARTDATE>0 AND ZSTARTDATE < ? GROUP BY ZSTREAMNAME", (tacq + HOUR - COCOA,)).fetchall()
    old30 = con.execute("SELECT COUNT(*) FROM ZOBJECT WHERE ZSTARTDATE>0 AND ZSTARTDATE < ?",
                        ((tacq - 30 * DAY) - COCOA,)).fetchone()[0]
    rs = sorted(((_UUID.sub("<id>", n or ""), (tacq - (m + COCOA)) / DAY, c) for n, m, c in rows),
                key=lambda x: (-x[1], x[0]))
    tot = sum(c for _, _, c in rs)
    if not rs:
        return {"streams": 0, "records": 0}
    hs = sorted(h for _, h, _ in rs)
    excl = [h for n, h, _ in rs if n != "/discoverability/signals" and not n.startswith("/knowledge-sync")]
    return {"streams": len(rs), "records": tot, "share_older_than_30_days": round(old30 / tot, 3) if tot else None,
            "oldest_stream_name": rs[0][0], "median_stream_horizon_d": round(hs[len(hs) // 2], 1),
            "horizon_excl_signals_sync_d": round(max(excl), 2) if excl else None,
            "signals_horizon_d": round(max([h for n, h, _ in rs if n == "/discoverability/signals"], default=-1), 2)}


# ---------------------------------------------------------------- iOS
IOS_RE = re.compile(
    r"(db/diagnostics/(Persist|Special|Signpost|HighVolume)/[0-9a-fA-F]+\.tracev3$)"
    r"|(mobile/Library/CoreDuet/Knowledge/knowledgeC\.db(-wal)?$)"
    r"|(mobile/Library/CoreDuet/People/interactionC\.db(-wal)?$)"
    r"|(mobile/Library/Biome/streams/restricted/App\.InFocus/local/\d{9,}$)"
    r"|(BatteryLife/Archives/powerlog_\d{4}-\d\d-\d\d[^/]*$)")


def read_ios(zpath, tacq, work):
    ents = sorted(ziputil.scan(zpath, lambda n: bool(IOS_RE.search(n))), key=lambda e: e["name"])
    res = {"stores": {}, "checks": {}}
    newest_device = []
    # unified log: wall-clock start time of every tracev3 file, header chunk tag 0x1000, seconds at offset 32
    for sub in ("Persist", "Special", "Signpost", "HighVolume"):
        es = [e for e in ents if "db/diagnostics/%s/" % sub in e["name"] and e["name"].endswith(".tracev3")]
        if not es:
            continue
        ts, size_total, chk_ok, chk_n, bad_hdr = [], 0, 0, 0, 0
        for e in es:
            size_total += e["usize"] or 0
            try:
                h = ziputil.read_head(zpath, e, 48)
            except (ValueError, OSError):
                bad_hdr += 1
                continue
            if len(h) < 40 or struct.unpack("<I", h[:4])[0] != 0x1000:
                bad_hdr += 1
                continue
            wt = struct.unpack("<Q", h[32:40])[0]
            ts.append(float(wt))
            mt = valid_mtime(e)
            if mt and MIN_PLAUSIBLE < wt:
                chk_n += 1
                chk_ok += 1 if wt <= mt + HOUR else 0
        s = summarise_times(ts, tacq, "header start time")
        s.update(files=len(es), bytes=size_total, bad_header=bad_hdr)
        res["stores"]["ul_" + sub.lower()] = s
        res["checks"]["ul_%s_hdr_le_mtime" % sub.lower()] = [chk_ok, chk_n]
        if "newest" in s:
            newest_device.append(s["newest"])
    # CoreDuet databases
    for key, pat, table, col, deep in (("knowledgec", "knowledgeC.db", "ZOBJECT", "ZSTARTDATE", True),
                                       ("interactionc", "interactionC.db", "ZINTERACTIONS", "ZSTARTDATE", False)):
        es = [e for e in ents if pat in e["name"]]
        if not es:
            continue
        try:
            r = sqlite_span(zpath, es, work, table, col, tacq, deep)
        except (sqlite3.Error, ValueError, OSError) as ex:
            res["stores"][key] = {"error": type(ex).__name__}
            continue
        if r is None:
            continue
        s = summarise_times(r["wal"]["vals"], tacq, "sqlite")
        nw = r["nowal"]["vals"]
        s["nowal_min"] = nw[0] if nw else None
        s["nowal_n"] = r["nowal"]["n"]
        if deep:
            s["infocus_min"] = r["wal"].get("infocus_min")
            res["deep_knowledgec"] = r["wal"]["streams"]
        res["stores"][key] = s
        if "newest" in s:
            newest_device.append(s["newest"])
    # Biome segments: the numeric name is the creation time in microseconds since 2001
    es = [e for e in ents if "Biome/streams/restricted/App.InFocus/local/" in e["name"]]
    if es:
        ts, ok, n = [], 0, 0
        for e in es:
            t = int(e["name"].rsplit("/", 1)[1]) / 1e6 + COCOA
            ts.append(t)
            mt = valid_mtime(e)
            if mt:
                n += 1
                ok += 1 if t <= mt + HOUR else 0
        s = summarise_times(ts, tacq, "biome-segment-name")
        s["files"] = len(es)
        res["stores"]["biome_appinfocus"] = s
        res["checks"]["biome_name_le_mtime"] = [ok, n]
        mts = [valid_mtime(e) for e in es if valid_mtime(e)]
        if mts:
            newest_device.append(max(mts))
    # powerlog archives: calendar date in the name, taken as noon UTC
    es = [e for e in ents if "BatteryLife/Archives/powerlog_" in e["name"]]
    if es:
        ts = []
        for e in es:
            m = re.search(r"powerlog_(\d{4})-(\d\d)-(\d\d)", e["name"])
            try:
                ts.append(datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 12,
                                            tzinfo=UTC).timestamp())
            except ValueError:
                pass
        s = summarise_times(ts, tacq, "powerlog-archive-date")
        s["files"] = len(es)
        res["stores"]["powerlog_archives"] = s
    res["device_newest"] = max(newest_device) if newest_device else None
    return res


# ---------------------------------------------------------------- Android
ANDROID_RE = re.compile(
    r"(data/system_ce/0/usagestats/(daily|weekly|monthly|yearly)/\d{10,}$)"
    r"|(data/system/usagestats/0/(daily|weekly|monthly|yearly)/\d{10,}$)"
    r"|(data/system_ce/0/notification_history/history/\d{10,}$)"
    r"|(data/system/dropbox/[^/]+@\d{10,}\.[^/]+$)"
    r"|((data/system/netstats|tethering/netstats)/(xt|uid|uid_tag|dev)\.\d{10,}-\d*$)"
    r"|(data/system/procstats/state-(v2-)?\d{4}-\d\d-\d\d-\d\d-\d\d-\d\d\.bin$)"
    r"|(data/log/batterystats/[a-z]+\d{12}$)")


def read_android(zpath, tacq):
    ents = sorted(ziputil.scan(zpath, lambda n: bool(ANDROID_RE.search(n))), key=lambda e: e["name"])
    groups = {"usage_daily": [], "usage_any": [], "notif_history": [], "dropbox": [], "netstats": [],
              "procstats": [], "vendor_battery_hist": []}
    chk = {}
    newest = []
    for e in ents:
        n = e["name"]
        base = n.rsplit("/", 1)[1]
        mt = valid_mtime(e)
        key, t, local = None, None, False
        if "/usagestats/" in n:
            t = int(base) / 1000.0
            groups["usage_any"].append(t)
            if "/daily/" in n:
                groups["usage_daily"].append(t)
            key = "usage"
        elif "notification_history/history/" in n:
            t = int(base) / 1000.0
            key = "notif_history"
            groups[key].append(t)
        elif "/dropbox/" in n:
            t = int(re.search(r"@(\d{10,})\.", base).group(1)) / 1000.0
            key = "dropbox"
            groups[key].append(t)
        elif "netstats/" in n:
            t = int(re.search(r"\.(\d{10,})-", base).group(1)) / 1000.0
            key = "netstats"
            groups[key].append(t)
        elif "/procstats/" in n:
            m = re.search(r"(\d{4})-(\d\d)-(\d\d)-(\d\d)-(\d\d)-(\d\d)", base)
            t = datetime.datetime(*map(int, m.groups()), tzinfo=UTC).timestamp()
            key, local = "procstats", True
            groups[key].append(t)
        elif "/batterystats/" in n:
            m = re.search(r"(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$", base)
            try:
                t = datetime.datetime(2000 + int(m.group(1)), *map(int, m.groups()[1:]), tzinfo=UTC).timestamp()
            except ValueError:
                t = None
            key, local = "vendor_battery_hist", True
            if t:
                groups[key].append(t)
        if key and t and mt:
            c = chk.setdefault(key + "_name_le_mtime", [0, 0])
            c[1] += 1
            tol = HOUR + (14 * HOUR if local else 0)
            c[0] += 1 if t <= mt + tol else 0
        if mt:
            newest.append(mt)
    res = {"stores": {}, "checks": chk}
    for k, ts in groups.items():
        if ts:
            s = summarise_times(ts, tacq, "file-name-time")
            s["files"] = len(ts)
            res["stores"][k] = s
    res["device_newest"] = max(newest) if newest else None
    return res


# ---------------------------------------------------------------- bug report
_LINE = re.compile(rb"^(?:(\d{4})-)?(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)\.\d{3}")
_TEXT = re.compile(r"(^|/)(bugreport[^/]*|dumpstate[^/]*)\.txt$")


@contextlib.contextmanager
def _bugreport_stream(path):
    """Open the text of the report: the largest bugreport/dumpstate text of the zip, or of a zip inside it."""
    z = zipfile.ZipFile(path)
    try:
        def pick(zz):
            c = [n for n in zz.namelist() if _TEXT.search(n) and "dumpstate_log" not in n and "dumpstate_board" not in n]
            return max(c, key=lambda n: zz.getinfo(n).file_size) if c else None
        name = pick(z)
        if name:
            with z.open(name) as f:
                yield f
            return
        inner = [n for n in z.namelist() if re.search(r"bugreport[^/]*\.zip$", n)]
        if inner:
            zi = zipfile.ZipFile(io.BytesIO(z.read(inner[0])))
            name = pick(zi)
            if name:
                with zi.open(name) as f:
                    yield f
                return
        raise ValueError("no bug report text")
    finally:
        z.close()


def _bugreport_sections(path):
    """Header time and the line times of the SYSTEM LOG and EVENT LOG sections (in line order), plus the number
    of backward steps of more than one hour per section."""
    hdr = None
    sec = None
    secs = {}
    steps = {}
    last = {}
    with _bugreport_stream(path) as f:
        for raw in f:
            if hdr is None:
                m = re.match(rb"== dumpstate: (\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)", raw)
                if m:
                    hdr = datetime.datetime(*map(int, m.groups()), tzinfo=UTC)
                    continue
            if raw.startswith(b"------ "):
                if b"was the duration of" in raw:
                    sec = None
                    continue
                m = re.match(rb"------ (SYSTEM LOG|EVENT LOG)", raw)
                sec = m.group(1).decode() if m else None
                continue
            if sec and hdr:
                m = _LINE.match(raw)
                if not m:
                    continue
                y, mo, d, H, M, S = m.groups()
                yr = int(y) if y else hdr.year
                try:
                    t = datetime.datetime(yr, int(mo), int(d), int(H), int(M), int(S), tzinfo=UTC)
                except ValueError:
                    continue
                if not y and t > hdr + datetime.timedelta(days=1):  # lines carry no year
                    t = t.replace(year=yr - 1)
                ts = t.timestamp()
                secs.setdefault(sec, []).append(ts)
                if sec in last and ts < last[sec] - HOUR:
                    steps[sec] = steps.get(sec, 0) + 1
                last[sec] = ts
    if hdr is None:
        raise ValueError("no dumpstate header")
    return hdr.timestamp(), secs, steps


def read_bugreport(path):
    """Read the SYSTEM LOG and EVENT LOG sections. The acquisition time is the dumpstate header time (one device
    clock for both, so a constant offset cancels)."""
    tacq, secs, steps = _bugreport_sections(path)
    res = {"tacq": tacq, "stores": {}, "checks": {}}
    for sec, key in (("SYSTEM LOG", "logcat_system"), ("EVENT LOG", "logcat_events")):
        if sec not in secs:
            continue
        ts = secs[sec]
        b, strays = body_start(ts)
        res["stores"][key] = {"kind": "logcat", "n_records": len(ts), "oldest": min(ts), "newest": max(ts),
                              "body_start": b, "head_strays": strays,
                              "body_grid": body_grid(ts) if key == "logcat_system" else None,
                              "n_clock_err_low": 0, "n_clock_err_high": 1 if max(ts) > tacq + HOUR else 0}
        res["checks"][key + "_backward_steps_over_hour"] = steps.get(sec, 0)
    res["device_newest"] = max((s["newest"] for s in res["stores"].values()), default=None)
    return res
