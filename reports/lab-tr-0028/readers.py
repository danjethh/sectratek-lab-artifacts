"""Readers for LAB-TR-0028: indicator values from extraction archives, bug reports and an iOS probe.

All readers are read-only. They take the path of an archive from a configuration (see run_corpus.py); no
path is built in. They return plain dictionaries of integers, booleans and lists of integers: no names,
no content. Package names, account names and message text are never copied into the result. Databases are
copied to a scratch directory that is removed afterwards.

Archive layout assumed: a ZIP file whose member names are the paths of the device file system
(for example "data/system/packages.xml"), with the original file times in the extended-timestamp field.
A bug report is a ZIP file with one large text member (the dump), or such a ZIP inside another.
Standard library only.
"""
import collections
import datetime
import io
import os
import re
import shutil
import sqlite3
import struct
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import abx
import zipscan

UTC = datetime.timezone.utc
COCOA = 978307200  # seconds from 1970 to 2001-01-01
DATA = r"data/(?:user_de/0|user/0|data)"

ANDROID_PATTERNS = [
    ("packages", r"(?:^|/)data/system/packages\.xml$"),
    ("pkgrestr", r"(?:^|/)data/system/users/0/package-restrictions\.xml$"),
    ("user0", r"(?:^|/)data/system/users/0\.xml$"),
    ("set_secure", r"(?:^|/)data/system/users/0/settings_secure\.xml$"),
    ("set_global", r"(?:^|/)data/system/users/0/settings_global\.xml$"),
    ("acc_de", r"(?:^|/)data/system_de/0/accounts_de\.db(?:-wal)?$"),
    ("acc_old", r"(?:^|/)data/system/users/0/accounts\.db(?:-wal)?$"),
    ("ancestral", r"(?:^|/)data/backup/ancestral$"),
    ("setup_ts", r"(?:^|/)data/backup/initialSetupTimestamp\.txt$"),
    ("tele", r"(?:^|/)" + DATA + r"/com\.android\.providers\.telephony/databases/mmssms\.db(?:-wal)?$"),
    ("calllog", r"(?:^|/)" + DATA + r"/com\.android\.providers\.contacts/databases/calllog\.db(?:-wal)?$"),
    ("external", r"(?:^|/)" + DATA + r"/com\.android\.providers\.media(?:\.module)?/databases/external\.db(?:-wal)?$"),
    ("bootstat", r"(?:^|/)data/misc/bootstat/factory_reset$"),
    ("usage", r"(?:^|/)data/system/usagestats/0/daily/\d+$"),
]
_ANDROID = [(k, re.compile(p)) for k, p in ANDROID_PATTERNS]
_ANDROID_ANY = re.compile("|".join("(?:%s)" % p for _, p in ANDROID_PATTERNS))
# directory prefixes of the system image; a package whose code path starts with one is a system package
SYSTEM_DIRS = ("/system/", "/product/", "/vendor/", "/system_ext/", "/apex/", "/odm/", "/oem/")
FLAG_SYSTEM = 1  # ApplicationInfo.FLAG_SYSTEM


def _classify(name, table):
    for key, rx in table:
        if rx.search(name):
            return key
    return None


def _as_int(v):
    if isinstance(v, int):
        return v
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _hex_int(v):
    if isinstance(v, int):
        return v
    try:
        return int(v, 16)
    except (TypeError, ValueError):
        return None


def _start_tags(data):
    """Yield (tag, attributes) for every start tag of an ABX or plain XML document."""
    if abx.is_abx(data):
        for ev in abx.parse(data):
            if ev[0] == "start":
                yield ev[1], ev[2]
    else:
        for el in ET.fromstring(data).iter():
            yield el.tag, dict(el.attrib)


def _copy_db(archive, entries, scratch, base):
    """Copy the largest database member (and its write-ahead log) to scratch; return the path."""
    dbs = [e for e in entries if not e["name"].endswith("-wal")]
    if not dbs:
        return None
    db = max(dbs, key=lambda e: e["usize"])
    path = os.path.join(scratch, base)
    zipscan.extract(archive, db, path)
    for e in entries:
        if e["name"] == db["name"] + "-wal":
            zipscan.extract(archive, e, path + "-wal")
    return path


def _columns(con, table):
    return [r[1] for r in con.execute('PRAGMA table_info("%s")' % table)]


def _tables(con):
    return [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]


def _ints(v):
    return v if isinstance(v, (int, float)) else None


def read_android(path, creator_prefixes=()):
    """Indicator values of one Android file system archive. creator_prefixes: package-name prefixes of the
    message creators to be treated as a migration tool (from the configuration; none are built in)."""
    found = collections.defaultdict(list)
    for e in zipscan.scan(path, lambda n: bool(_ANDROID_ANY.search(n))):
        key = _classify(e["name"], _ANDROID)
        if key:
            found[key].append(e)
    res = {"kind": "android", "errors": []}

    def one(key):
        return [e for e in found.get(key, []) if not e["name"].endswith("/")]

    scratch = tempfile.mkdtemp(prefix="ind_")
    try:
        # first boot record: file time of the factory-reset event
        fr = one("bootstat")
        res["W"] = fr[0]["mtime"] if fr else None
        usage = []
        for e in one("usage"):
            try:
                usage.append(int(e["name"].rsplit("/", 1)[1]) / 1000.0)
            except ValueError:
                pass
        res["usage_daily_s"] = sorted(usage)
        # packages: system flag from packages.xml, install time and reason from package-restrictions.xml
        res["packages"] = []
        res["restrictions_present"] = False
        try:
            pk = [e for e in one("packages") if e["name"].endswith("packages.xml")]
            if pk:
                data = zipscan.read_member(path, pk[0])
                names = collections.OrderedDict()
                for tag, a in _start_tags(data):
                    if tag == "package" and "name" in a:
                        code_path = a.get("codePath", "") or ""
                        flags = _as_int(a.get("publicFlags") if a.get("publicFlags") is not None else a.get("flags"))
                        names[a["name"]] = bool(code_path.startswith(SYSTEM_DIRS) or ((flags or 0) & FLAG_SYSTEM))
                restr = {}
                pr = one("pkgrestr")
                if pr:
                    res["restrictions_present"] = True
                    for tag, a in _start_tags(zipscan.read_member(path, pr[0])):
                        if tag == "pkg" and "name" in a:
                            restr[a["name"]] = (_hex_int(a.get("first-install-time")), _as_int(a.get("install-reason")))
                for name, system in names.items():
                    fit, ir = restr.get(name, (None, None))
                    res["packages"].append({"system": system, "fit_ms": fit, "ir": ir})
        except Exception as ex:  # a store that fails to parse is reported, not read as empty
            res["errors"].append("packages: " + type(ex).__name__)
        # user record and setup flags
        res["user_created"] = None
        try:
            u0 = one("user0")
            if u0:
                for tag, a in _start_tags(zipscan.read_member(path, u0[0])):
                    if tag == "user":
                        res["user_created"] = str(a.get("created"))
                        break
        except Exception as ex:
            res["errors"].append("user0: " + type(ex).__name__)
        res["setup_flags"] = [None, None]
        try:
            for slot, (key, name) in enumerate((("set_secure", "user_setup_complete"), ("set_global", "device_provisioned"))):
                for e in one(key)[:1]:
                    for tag, a in _start_tags(zipscan.read_member(path, e)):
                        if tag == "setting" and a.get("name") == name:
                            res["setup_flags"][slot] = str(a.get("value"))
                            break
        except Exception as ex:
            res["errors"].append("settings: " + type(ex).__name__)
        # accounts: last password entry time of each account, time of each add action in the debug log
        res["acc_pw_ms"], res["acc_add_s"] = [], []
        try:
            for key in ("acc_de", "acc_old"):
                if found.get(key):
                    db = _copy_db(path, found[key], scratch, key + ".db")
                    con = sqlite3.connect(db)
                    con.execute("PRAGMA query_only=1")
                    tb = _tables(con)
                    if "accounts" in tb and "last_password_entry_time_millis_epoch" in _columns(con, "accounts"):
                        res["acc_pw_ms"] = [r[0] for r in con.execute(
                            "SELECT last_password_entry_time_millis_epoch FROM accounts "
                            "WHERE last_password_entry_time_millis_epoch>0 ORDER BY _id")]
                    if "debug_table" in tb:
                        res["acc_add_s"] = [int(r[0]) for r in con.execute(
                            "SELECT strftime('%s', time) FROM debug_table WHERE action_type='action_account_add' "
                            "AND time IS NOT NULL ORDER BY rowid") if r[0]]
                    con.close()
                    break
        except Exception as ex:
            res["errors"].append("accounts: " + type(ex).__name__)
        # backup record: header of the ancestral file; setup timestamp file
        res["ancestral"] = None
        res["setup_ts_s"] = None
        try:
            anc = one("ancestral")
            if anc:
                b = zipscan.read_member(path, anc[0])
                if len(b) >= 24:
                    version, ancestral, current, count = struct.unpack(">iqqi", b[:24])
                    res["ancestral"] = {"ancestral_nonzero": ancestral != 0, "current_nonzero": current != 0, "count": count}
            ts = one("setup_ts")
            if ts:
                txt = zipscan.read_member(path, ts[0])[:40].decode("ascii", "replace").strip()
                if txt.isdigit():
                    res["setup_ts_s"] = int(txt) / 1000.0
        except Exception as ex:
            res["errors"].append("backup: " + type(ex).__name__)
        # message and call tables: identifier, date, creator class
        res["sms"] = {"id": [], "date_ms": [], "tool": []}
        res["sms_has_creator"] = False
        try:
            if found.get("tele"):
                con = sqlite3.connect(_copy_db(path, found["tele"], scratch, "tele.db"))
                con.execute("PRAGMA query_only=1")
                if "sms" in _tables(con):
                    cols = _columns(con, "sms")
                    res["sms_has_creator"] = "creator" in cols
                    sel = "_id, date, creator" if "creator" in cols else "_id, date, NULL"
                    for i, d, c in con.execute("SELECT %s FROM sms ORDER BY _id" % sel):
                        res["sms"]["id"].append(i)
                        res["sms"]["date_ms"].append(_ints(d))
                        res["sms"]["tool"].append(int(bool(c) and any(str(c).startswith(p) for p in creator_prefixes)))
                con.close()
        except Exception as ex:
            res["errors"].append("messages: " + type(ex).__name__)
        res["calls"] = {"id": [], "date_ms": []}
        try:
            if found.get("calllog"):
                con = sqlite3.connect(_copy_db(path, found["calllog"], scratch, "calls.db"))
                con.execute("PRAGMA query_only=1")
                if "calls" in _tables(con):
                    for i, d in con.execute("SELECT _id, date FROM calls ORDER BY _id"):
                        res["calls"]["id"].append(i)
                        res["calls"]["date_ms"].append(_ints(d))
                con.close()
        except Exception as ex:
            res["errors"].append("calls: " + type(ex).__name__)
        # media index: time added (s), time taken (ms), type code
        res["media"] = {"added_s": [], "taken_ms": [], "type": []}
        try:
            if found.get("external"):
                con = sqlite3.connect(_copy_db(path, found["external"], scratch, "media.db"))
                con.execute("PRAGMA query_only=1")
                if "files" in _tables(con):
                    cols = _columns(con, "files")
                    taken = "datetaken" if "datetaken" in cols else "NULL"
                    for a, t, m in con.execute("SELECT date_added, %s, media_type FROM files ORDER BY _id" % taken):
                        res["media"]["added_s"].append(_ints(a))
                        res["media"]["taken_ms"].append(_ints(t))
                        res["media"]["type"].append(m)
                con.close()
        except Exception as ex:
            res["errors"].append("media: " + type(ex).__name__)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return res


# ------------------------------------------------------------------ bug report
_DT = re.compile(r"(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)")


def _dt(s):
    m = _DT.search(s)
    if not m:
        return None
    return datetime.datetime(*map(int, m.groups()), tzinfo=UTC).timestamp()


def _bugreport_text(path):
    z = zipfile.ZipFile(path)
    rx = re.compile(r"(^|/)(bugreport[^/]*|dumpstate[^/]*)\.txt$")
    txt = [n for n in z.namelist() if rx.search(n) and "dumpstate_log" not in n]
    if txt:
        return z.read(max(txt, key=lambda n: z.getinfo(n).file_size))
    inner = [n for n in z.namelist() if re.search(r"bugreport[^/]*\.zip$", n)]
    zi = zipfile.ZipFile(io.BytesIO(z.read(inner[0])))
    t2 = [n for n in zi.namelist() if rx.search(n) and "dumpstate_log" not in n]
    return zi.read(max(t2, key=lambda n: zi.getinfo(n).file_size))


def read_bugreport(path):
    """Package install times and reasons and the backup token of one bug report (no names kept)."""
    text = _bugreport_text(path).decode("utf-8", "replace")
    res = {"kind": "bugreport", "packages": [], "ancestral_token": None}
    cur = None
    in_pkg = False
    in_user0 = False
    for line in text.splitlines():
        if line.startswith("Ancestral:"):
            res["ancestral_token"] = line.split(":", 1)[1].strip()
        if line.startswith("DUMP OF SERVICE package:"):
            in_pkg = True
        elif line.startswith("DUMP OF SERVICE ") and in_pkg:
            in_pkg = False
        if not in_pkg:
            continue
        if re.match(r"^  Package \[[^\]]+\]", line):
            cur = {"system": False, "fit": None, "ir": None}
            res["packages"].append(cur)
            in_user0 = False
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith("flags=["):
            cur["system"] = " SYSTEM " in s
        elif s.startswith("User "):
            in_user0 = s.startswith("User 0:")
        elif in_user0 and s.startswith("installReason="):
            cur["ir"] = _as_int(s.split("=", 1)[1])
        elif s.startswith("firstInstallTime=") and cur["fit"] is None:
            cur["fit"] = _dt(s)
    return res


# ------------------------------------------------------------------ iOS probe
IOS_PATTERNS = [
    ("sms", r"private/var/mobile/Library/SMS/sms\.db(?:-wal)?$"),
    ("calls", r"private/var/mobile/Library/CallHistoryDB/CallHistory\.storedata(?:-wal)?$"),
    ("photos", r"private/var/mobile/Media/PhotoData/Photos\.sqlite(?:-wal)?$"),
    ("marker_task", r"completionOfPerBackupRestoreLaunchTask_[^/]+$"),
    ("marker_lock", r"private/var/mobile/Library/Caches/Backup/RestoreFromBackupLock$"),
]
_IOS = [(k, re.compile(p)) for k, p in IOS_PATTERNS]
_IOS_ANY = re.compile("|".join("(?:%s)" % p for _, p in IOS_PATTERNS))


def _core_data_to_epoch(v):
    if v is None or v <= 0:
        return None
    if v > 1e11:  # nanoseconds
        v = v / 1e9
    return v + COCOA


def read_ios(path):
    """Marker file times and the dates of messages, calls and photograph assets of one iOS archive."""
    found = collections.defaultdict(list)
    for e in zipscan.scan(path, lambda n: bool(_IOS_ANY.search(n))):
        key = _classify(e["name"], _IOS)
        if key:
            found[key].append(e)
    res = {"kind": "ios", "errors": [],
           "marker_task_s": sorted(e["mtime"] for e in found.get("marker_task", []) if e["mtime"]),
           "marker_lock_s": [e["mtime"] for e in found.get("marker_lock", []) if e["mtime"]],
           "sms_s": [], "calls_s": [], "photos_s": []}
    scratch = tempfile.mkdtemp(prefix="ios_")
    try:
        for key, base, sql, out in (
                ("sms", "s.db", "SELECT date FROM message WHERE date>0", "sms_s"),
                ("calls", "c.db", "SELECT ZDATE FROM ZCALLRECORD WHERE ZDATE>0", "calls_s"),
                ("photos", "p.db", "SELECT ZDATECREATED FROM ZASSET WHERE ZDATECREATED IS NOT NULL", "photos_s")):
            if not found.get(key):
                continue
            try:
                con = sqlite3.connect(_copy_db(path, found[key], scratch, base))
                con.execute("PRAGMA query_only=1")
                if key == "sms":
                    res[out] = [_core_data_to_epoch(r[0]) for r in con.execute(sql)]
                else:
                    res[out] = [r[0] + COCOA for r in con.execute(sql) if r[0] is not None]
                con.close()
            except Exception as ex:
                res["errors"].append(key + ": " + type(ex).__name__)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return res
