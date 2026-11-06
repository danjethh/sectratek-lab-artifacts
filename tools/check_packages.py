#!/usr/bin/env python3
"""Structure and hygiene check of the packages under reports/ (standard library only).

Checks, per package reports/lab-tr-*/:
  - README.md exists
  - code packages (any .py file) have LICENSE-CODE and LICENSE-DATA
    (spelling variants such as LICENSE, LICENSE-code, LICENSE-DATA.md are accepted with a warning)
  - no file larger than 5 MB (warning)
  - no absolute Windows path, no e-mail address other than the allowed one,
    and no occurrence of the words "client" or "Boatwright" (case-insensitive) in any text file

Exit status 1 if any error was found; warnings do not fail the check.
Usage: python tools/check_packages.py [--only lab-tr-0030,...]
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
ALLOWED_EMAIL = "daniel@prudentialassociates.com"
MAX_BYTES = 5 * 1024 * 1024

WIN_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\{1,2}[A-Za-z0-9_.$ -]")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
WORDS = re.compile(r"client|boatwright", re.I)
# Technical uses of "client" that are not people: the iOS shutdown-log field "clients" (LAB-TR-0036) and the
# TCC "access.client" column (LAB-TR-0035). They are blanked before the word scan; Boatwright is never allowed.
TECH_CLIENT = re.compile(
    r"clients[\"']?\s*[=:]"                               # clients=6, "clients": 6, clients=0
    r"|\[.clients.\]"                                 # cur['clients']
    r"|remaining client"                              # 'remaining client pid' log line
    r"|these clients are"
    r"|SELECT DISTINCT client FROM access"
    r"|client_type")

BINARY_EXT = {".sqlite", ".sqlite-wal", ".sqlite-shm", ".db", ".zip", ".gz", ".tar", ".png", ".jpg", ".jpeg",
              ".gif", ".pdf", ".plist", ".bin", ".pyc", ".ttf", ".woff", ".woff2", ".7z"}


def is_text(path):
    if os.path.splitext(path)[1].lower() in BINARY_EXT:
        return False
    with open(path, "rb") as fh:
        return b"\0" not in fh.read(8192)


def find_license(names, exact, variants):
    low = {n.lower(): n for n in names}
    if exact.lower() in low:
        return exact, False
    for v in variants:
        if v.lower() in low:
            return low[v.lower()], True
    return None, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    errors, warnings = [], []

    if not os.path.isdir(REPORTS):
        print("no reports/ directory", file=sys.stderr)
        return 2
    ids = sorted(d for d in os.listdir(REPORTS)
                 if d.startswith("lab-tr-") and os.path.isdir(os.path.join(REPORTS, d)))
    if only:
        ids = [i for i in ids if i in only]

    for pid in ids:
        pdir = os.path.join(REPORTS, pid)
        top = os.listdir(pdir)
        has_code = False
        for dp, dn, fn in os.walk(pdir):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in fn:
                path = os.path.join(dp, f)
                rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
                if f.endswith(".py"):
                    has_code = True
                size = os.path.getsize(path)
                if size > MAX_BYTES:
                    warnings.append("%s: %.1f MB (over 5 MB)" % (rel, size / 1048576))
                if not is_text(path):
                    continue
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for n, line in enumerate(fh, 1):
                        for m in WIN_PATH.finditer(line):
                            errors.append("%s:%d: absolute Windows path %r" % (rel, n, m.group(0)))
                        for m in EMAIL.finditer(line):
                            if m.group(0).lower() != ALLOWED_EMAIL:
                                errors.append("%s:%d: e-mail address %r" % (rel, n, m.group(0)))
                        for m in WORDS.finditer(TECH_CLIENT.sub(" ", line)):
                            errors.append("%s:%d: forbidden word %r" % (rel, n, m.group(0)))
        if "README.md" not in top:
            errors.append("%s: README.md missing" % pid)
        if has_code:
            lic, v1 = find_license(top, "LICENSE-CODE", ["LICENSE", "LICENSE.txt", "LICENSE.md"])
            if lic is None:
                errors.append("%s: LICENSE-CODE missing" % pid)
            elif v1:
                warnings.append("%s: code licence is named %s (expected LICENSE-CODE)" % (pid, lic))
            lic, v2 = find_license(top, "LICENSE-DATA",
                                   ["LICENSE-DATA.md", "LICENSE-DATA.txt", "LICENSE-data-and-text"])
            if lic is None:
                errors.append("%s: LICENSE-DATA missing" % pid)
            elif v2:
                warnings.append("%s: data licence is named %s (expected LICENSE-DATA)" % (pid, lic))

    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("\n%d package(s) checked, %d error(s), %d warning(s)" % (len(ids), len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
