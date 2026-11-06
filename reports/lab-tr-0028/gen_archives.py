"""Generator of INVENTED extraction archives in the layout that readers.py expects.

The archives are small ZIP files of an invented file system: databases built with the table and column
names of the public Android providers (documented in AOSP), a package list, an account database, the
bootstat event file, and so on. Every name, time and count is invented from the table in DEVICES and a
seeded random generator. The output shows that the pipeline runs end to end; it does not show, and must
not be read as showing, any finding of the report.

Standard library only; no wall-clock time, no system randomness. Same seed, same bytes.
"""
import datetime
import json
import os
import random
import sqlite3
import struct
import tempfile
import zipfile

import abx

UTC = datetime.timezone.utc
DAY = 86400
START = int(datetime.datetime(2024, 1, 1, tzinfo=UTC).timestamp())  # invented first boot of device 0
TOOL_PREFIX = "com.example.migrate"  # invented message creator standing for a migration tool
DEFAULT_APP = "com.example.messages"
CARRIER_APP = "com.example.carrier"
DEFAULT_SEED = 28

# One row per invented Android device.
# gap: days from the first boot record to user setup; restore: a restored batch is written at setup;
# tool: restored messages carry the migration-tool creator; order: insertion order of the batch;
# xml: packages in plain XML (True) or Android Binary XML; fit: install times stored; token: backup token set;
# media_late: days after first boot at which the media index starts (None: at first boot).
DEVICES = [
    dict(os="16", gap=0.5, restore=True, tool=True, order="asc", xml=False, fit=True, token=True, media_late=None, ts=True),
    dict(os="16", gap=60, restore=True, tool=True, order="desc", xml=False, fit=True, token=True, media_late=None, ts=True),
    dict(os="16", gap=120, restore=False, tool=False, order="asc", xml=False, fit=True, token=False, media_late=None, ts=False),
    dict(os="14", gap=200, restore=True, tool=False, order="random", xml=False, fit=True, token=False, media_late=None, ts=False),
    dict(os="14", gap=30, restore=False, tool=False, order="asc", xml=True, fit=True, token=False, media_late=None, ts=False),
    dict(os="12", gap=400, restore=False, tool=False, order="asc", xml=True, fit=False, token=False, media_late=300, ts=False),
    dict(os="10", gap=100, restore=True, tool=True, order="asc", xml=True, fit=False, token=False, media_late=None, ts=True),
    dict(os="16", gap=2, restore=True, tool=True, order="asc", xml=False, fit=True, token=True, media_late=None, ts=False),
]
USER0_XML = b'<?xml version="1.0" encoding="utf-8"?>' + bytes([10]) + b'<user id="0" created="0" />' + bytes([10])
BATCH = 400
NATIVE = 100
CALLS_RESTORED = 80
CALLS_NATIVE = 40
SYSTEM_PACKAGES = 16
ACQUIRED_AFTER_SETUP_DAYS = 200


# ---------------------------------------------------------------- building blocks
def db_bytes(build):
    """Build a SQLite database with build(connection) and return the file bytes."""
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "x.db")
        con = sqlite3.connect(path)
        build(con)
        con.commit()
        con.close()
        with open(path, "rb") as f:
            return f.read()


def write_zip(path, members):
    """members: list of (name, bytes, mtime epoch seconds). Deterministic: sorted, fixed attributes,
    the file time is stored in the extended-timestamp field and in the DOS fields."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data, mtime in sorted(members, key=lambda m: m[0]):
            dt = datetime.datetime.fromtimestamp(int(mtime), UTC)
            zi = zipfile.ZipInfo(name, date_time=(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = 0o100644 << 16
            zi.extra = struct.pack("<HHBi", 0x5455, 5, 1, int(mtime))
            z.writestr(zi, data)


def order_batch(items, order, rng):
    items = list(items)
    if order == "desc":
        items.reverse()
    elif order == "random":
        rng.shuffle(items)
    return items


def package_names(i):
    system = ["com.example.system%02d" % k for k in range(SYSTEM_PACKAGES)]
    user = ["com.example.app%02d" % k for k in range(15)]
    return system, user


def xml_or_abx(root, children, as_xml):
    """children: list of (tag, attrs). Plain XML text or ABX bytes."""
    if as_xml:
        out = ['<?xml version="1.0" encoding="utf-8"?>', "<%s>" % root]
        for tag, attrs in children:
            out.append("<%s %s />" % (tag, " ".join('%s="%s"' % (k, v) for k, v in attrs.items())))
        out.append("</%s>" % root)
        return "\n".join(out).encode("utf-8")
    ev = [["start", root, {}]]
    for tag, attrs in children:
        ev.append(["start", tag, dict(attrs)])
        ev.append(["end", tag])
    ev.append(["end", root])
    return abx.dump(ev)


# ---------------------------------------------------------------- one Android device
def android_members(i, spec, seed):
    rng = random.Random(seed * 1000 + i)
    W = START + i * 20 * DAY
    U = W + int(spec["gap"] * DAY)
    acq = U + ACQUIRED_AFTER_SETUP_DAYS * DAY
    R = U + 1800  # restore half an hour after setup
    members = []
    members.append(("data/misc/bootstat/factory_reset", b"", W))
    # ---- packages
    system, user = package_names(i)
    pk_attrs, pr_attrs = [], []
    for k, name in enumerate(system):
        pk_attrs.append(("package", dict(name=name, codePath="/system/app/%s" % name, publicFlags=1)))
        pr_attrs.append(("pkg", dict(name=name, **({"first-install-time": (W - 90 * DAY) * 1000} if spec["fit"] else {}))))
    for k, name in enumerate(user):
        pk_attrs.append(("package", dict(name=name, codePath="/data/app/%s" % name, publicFlags=0)))
        if k < 3:
            t, ir = U + k * 60, 3  # installed during setup
        elif k < 9 and spec["restore"]:
            t, ir = R + k * 5, 2  # restored
        elif k < 13:
            t, ir = U + (k * 7 + 3) * DAY, 4  # user
        else:
            t, ir = U + (k * 9) * DAY, 0  # no reason recorded
        attrs = dict(name=name, **({"install-reason": ir} if spec["os"] not in ("10", "12") else {}))
        if spec["fit"]:
            attrs["first-install-time"] = t * 1000
        pr_attrs.append(("pkg", attrs))
    if spec["xml"]:  # plain XML carries the install time in hexadecimal
        for _, a in pr_attrs:
            if "first-install-time" in a:
                a["first-install-time"] = "%x" % a["first-install-time"]
    members.append(("data/system/packages.xml", xml_or_abx("packages", pk_attrs, spec["xml"]), acq))
    members.append(("data/system/users/0/package-restrictions.xml",
                    xml_or_abx("package-restrictions", pr_attrs, spec["xml"]), acq))
    members.append(("data/system/users/0.xml", USER0_XML, acq))
    members.append(("data/system/users/0/settings_secure.xml",
                    xml_or_abx("settings", [("setting", dict(name="user_setup_complete", value="1"))], True), acq))
    members.append(("data/system/users/0/settings_global.xml",
                    xml_or_abx("settings", [("setting", dict(name="device_provisioned", value="1"))], True), acq))
    # ---- accounts: one account whose password was last entered at setup, one add action in the debug log
    def accounts(con):
        con.execute("CREATE TABLE accounts (_id INTEGER PRIMARY KEY AUTOINCREMENT, last_password_entry_time_millis_epoch INTEGER DEFAULT 0)")
        con.execute("CREATE TABLE debug_table (_id INTEGER PRIMARY KEY, action_type TEXT, time TEXT, table_name TEXT)")
        con.execute("INSERT INTO accounts(last_password_entry_time_millis_epoch) VALUES (?)", ((U + 3600) * 1000,))
        stamp = datetime.datetime.fromtimestamp(U + 1200, UTC).strftime("%Y-%m-%d %H:%M:%S")
        con.execute("INSERT INTO debug_table(action_type, time, table_name) VALUES ('action_account_add', ?, 'accounts')", (stamp,))
    members.append(("data/system_de/0/accounts_de.db", db_bytes(accounts), acq))
    # ---- backup record
    if i != 2:
        token = 1 if spec["token"] else 0
        members.append(("data/backup/ancestral", struct.pack(">iqqi", 1, token, token, 0), acq))
    if spec["ts"]:
        members.append(("data/backup/initialSetupTimestamp.txt", str((U + 30 * DAY) * 1000).encode("ascii"), acq))
    # ---- usage statistics: ten daily files before acquisition
    for k in range(10):
        members.append(("data/system/usagestats/0/daily/%d" % ((acq - (10 - k) * DAY) * 1000), b"", acq))
    # ---- messages
    created = TOOL_PREFIX if spec["tool"] else DEFAULT_APP
    batch_dates = sorted(R - int(rng.uniform(1, 365) * DAY) for _ in range(BATCH)) if spec["restore"] else []
    batch = order_batch(batch_dates, spec["order"], rng)
    native = sorted(U + int(rng.uniform(0.1, 150) * DAY) for _ in range(NATIVE))
    rows = [(d, created) for d in batch] + [(d, DEFAULT_APP if k % 4 else CARRIER_APP) for k, d in enumerate(native)]

    def messages(con):
        con.execute("CREATE TABLE sms (_id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, date INTEGER, type INTEGER, creator TEXT)")
        con.executemany("INSERT INTO sms(thread_id, date, type, creator) VALUES (?,?,?,?)",
                        [(k % 20, d * 1000, 1 + k % 2, c) for k, (d, c) in enumerate(rows)])
    members.append(("data/user_de/0/com.android.providers.telephony/databases/mmssms.db", db_bytes(messages), acq))
    # ---- calls
    call_rows = ([R - int(rng.uniform(1, 300) * DAY) for _ in range(CALLS_RESTORED)] if spec["restore"] else [])
    call_rows = sorted(call_rows) + sorted(U + int(rng.uniform(0.1, 150) * DAY) for _ in range(CALLS_NATIVE))

    def calls(con):
        con.execute("CREATE TABLE calls (_id INTEGER PRIMARY KEY AUTOINCREMENT, date INTEGER, duration INTEGER, type INTEGER)")
        con.executemany("INSERT INTO calls(date, duration, type) VALUES (?,?,?)",
                        [(d * 1000, 10 + k % 90, 1 + k % 3) for k, d in enumerate(call_rows)])
    members.append(("data/user_de/0/com.android.providers.contacts/databases/calllog.db", db_bytes(calls), acq))
    # ---- media index: three items at the start, native items after setup, restored items taken before W
    start = W if spec["media_late"] is None else W + int(spec["media_late"] * DAY)
    media = [(start + 60 * k, (start + 60 * k) * 1000, 1) for k in range(3)]
    for k in range(40):
        taken = U + int(rng.uniform(0.1, 150) * DAY)
        media.append((taken + 5, taken * 1000, 1 if k % 5 else 3))
    if spec["restore"]:
        for k in range(30):
            taken = W - int(rng.uniform(5, 400) * DAY)
            media.append((R + k, taken * 1000, 1))

    def external(con):
        con.execute("CREATE TABLE files (_id INTEGER PRIMARY KEY AUTOINCREMENT, date_added INTEGER, datetaken INTEGER, media_type INTEGER)")
        con.executemany("INSERT INTO files(date_added, datetaken, media_type) VALUES (?,?,?)", media)
    members.append(("data/user_de/0/com.android.providers.media.module/databases/external.db", db_bytes(external), acq))
    return members


# ---------------------------------------------------------------- bug reports
def bugreport_text(i, with_reasons, n_restored, seed):
    T = START + (400 + i * 30) * DAY
    lines = ["== dumpstate: %s" % datetime.datetime.fromtimestamp(T, UTC).strftime("%Y-%m-%d %H:%M:%S"),
             "Ancestral: 0", "DUMP OF SERVICE package:"]
    for k in range(10):
        lines += ["  Package [com.example.system%02d] (%06x):" % (k, k), "    flags=[ SYSTEM HAS_CODE ]",
                  "    firstInstallTime=%s" % datetime.datetime.fromtimestamp(START, UTC).strftime("%Y-%m-%d %H:%M:%S"),
                  "    User 0: installed=true", "      installReason=0" if with_reasons else "      enabled=0"]
    for k in range(20):
        restored = with_reasons and k < n_restored
        t = START + (300 + (0 if restored else k * 3)) * DAY
        lines += ["  Package [com.example.app%02d] (%06x):" % (k, 100 + k), "    flags=[ HAS_CODE ]",
                  "    firstInstallTime=%s" % datetime.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M:%S"),
                  "    User 0: installed=true",
                  ("      installReason=%d" % (2 if restored else 4)) if with_reasons else "      enabled=0"]
    lines += ["DUMP OF SERVICE other:", "  nothing here"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- iOS
CORE_DATA_EPOCH = 978307200


def ios_members(i, with_marker, seed):
    rng = random.Random(seed * 1000 + 500 + i)
    M = START + (100 + 40 * i) * DAY
    members = []
    if with_marker:
        members.append(("private/var/mobile/Library/Caches/Backup/RestoreFromBackupLock", b"", M))
        members.append(("private/var/mobile/Library/Preferences/completionOfPerBackupRestoreLaunchTask_a1", b"", M + 600))

    def dates(n_old, n_new):
        return ([M - int(rng.uniform(1, 800) * DAY) for _ in range(n_old)] +
                [M + int(rng.uniform(1, 200) * DAY) for _ in range(n_new)])
    old = 0 if i == 3 else 150 * (i + 1)
    msgs = dates(old, 100)

    def sms(con):
        con.execute("CREATE TABLE message (ROWID INTEGER PRIMARY KEY AUTOINCREMENT, date INTEGER)")
        con.executemany("INSERT INTO message(date) VALUES (?)", [((t - CORE_DATA_EPOCH) * 10 ** 9,) for t in msgs])
    members.append(("private/var/mobile/Library/SMS/sms.db", db_bytes(sms), M + 5 * DAY))
    calls_ = dates(30 if i % 2 else 0, 40)

    def calls(con):
        con.execute("CREATE TABLE ZCALLRECORD (Z_PK INTEGER PRIMARY KEY, ZDATE REAL)")
        con.executemany("INSERT INTO ZCALLRECORD(ZDATE) VALUES (?)", [(float(t - CORE_DATA_EPOCH),) for t in calls_])
    members.append(("private/var/mobile/Library/CallHistoryDB/CallHistory.storedata", db_bytes(calls), M + 5 * DAY))
    photos = dates(200, 50)

    def ph(con):
        con.execute("CREATE TABLE ZASSET (Z_PK INTEGER PRIMARY KEY, ZDATECREATED REAL)")
        con.executemany("INSERT INTO ZASSET(ZDATECREATED) VALUES (?)", [(float(t - CORE_DATA_EPOCH),) for t in photos])
    members.append(("private/var/mobile/Media/PhotoData/Photos.sqlite", db_bytes(ph), M + 5 * DAY))
    return members


# ---------------------------------------------------------------- entry point
def generate(out_dir, seed=DEFAULT_SEED):
    """Write the invented archives and a configuration file (config.json) into out_dir."""
    os.makedirs(out_dir, exist_ok=True)
    cfg = {"migration_creator_prefixes": [TOOL_PREFIX], "android": [], "bug_reports": [], "ios": []}
    for i, spec in enumerate(DEVICES):
        name = "android_%02d.zip" % (i + 1)
        write_zip(os.path.join(out_dir, name), android_members(i, spec, seed))
        cfg["android"].append({"id": "a%02d" % (i + 1), "path": name})
    for i, (reasons, n_restored) in enumerate([(True, 12), (True, 0), (False, 0)]):
        name = "bugreport_%02d.zip" % (i + 1)
        write_zip(os.path.join(out_dir, name), [("bugreport-invented.txt", bugreport_text(i, reasons, n_restored, seed).encode("utf-8"), START)])
        cfg["bug_reports"].append({"id": "b%02d" % (i + 1), "path": name})
    for i in range(4):
        name = "ios_%02d.zip" % (i + 1)
        write_zip(os.path.join(out_dir, name), ios_members(i, i != 3, seed))
        cfg["ios"].append({"id": "i%02d" % (i + 1), "path": name})
    with open(os.path.join(out_dir, "config.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cfg, f, indent=1, sort_keys=True)
        f.write("\n")
    return cfg


if __name__ == "__main__":
    import sys
    generate(sys.argv[1] if len(sys.argv) > 1 else "invented_archives")
