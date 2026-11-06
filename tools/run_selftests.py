#!/usr/bin/env python3
"""Run the self-test of every package under reports/ (standard library only).

For each reports/lab-tr-*/ the runner picks, in this order:
  1. selftest.py
  2. tests.py
  3. the entry named in the package README (table ENTRIES below, curated from the READMEs;
     otherwise the first README command line that names a test, verify or check script)
Packages with none of these are reported as SKIP ("no self-test").

Each command runs with cwd = the package folder, a 600 s timeout and sys.executable.
Writes tools/selftest_results.json (list of {id, command, status, seconds}); exit 1 if any FAIL.

Usage: python tools/run_selftests.py [--only lab-tr-0030,lab-tr-0012] [--timeout 600]
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
RESULTS = os.path.join(ROOT, "tools", "selftest_results.json")

# Entries named by the package READMEs, for packages without selftest.py / tests.py.
# "{tmp}" is replaced by a fresh temporary directory so that the run does not write into the package.
ENTRIES = {
    "lab-tr-0013": ["test_reader.py"],
    "lab-tr-0032": ["run_synthetic.py", "--quick"],          # README: --quick runs a reduced grid
    "lab-tr-0033": ["tests/test_roundtrip.py", "--n", "40"],
    "lab-tr-0034": ["verify_calculus.py", "{tmp}/verify_report.json"],
    "lab-tr-0035": ["run_synthetic.py", "{tmp}"],
    "lab-tr-0036": ["code/tr36_synth.py", "300", "{tmp}/fixtures_report.json"],
    "lab-tr-0037": ["tests/test_parse_and_faults.py", "--n", "30"],
    "lab-tr-0038": ["verify_calculus.py", "{tmp}/verify_report.json"],
    "lab-tr-0039": ["check.py", "--demo"],
    "lab-tr-0040": ["verify.py", "{tmp}/verify_report.json"],
}


# Packages whose self-test writes result files into its own folder: run on a temporary copy so the
# committed results are never overwritten (lab-tr-0032: --quick rewrites synthetic_results.json).
ISOLATE = {"lab-tr-0032"}


def readme_entry(pkg_dir):
    """Fallback: first 'python SCRIPT ...' line in the README whose script looks like a test."""
    path = os.path.join(pkg_dir, "README.md")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"\s*python3?\s+(?:-I\s+)?(\S+\.py)\b(.*)", line)
            if not m:
                continue
            script, rest = m.group(1), m.group(2).split("#")[0]
            if re.search(r"test|verify|check|selftest", os.path.basename(script)) \
                    and os.path.isfile(os.path.join(pkg_dir, script)):
                return [script] + shlex.split(rest)
    return None


def pick_command(pkg_id, pkg_dir):
    for name in ("selftest.py", "tests.py"):
        if os.path.isfile(os.path.join(pkg_dir, name)):
            return [name]
    if pkg_id in ENTRIES:
        return list(ENTRIES[pkg_id])
    return readme_entry(pkg_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated package ids, e.g. lab-tr-0030,lab-tr-0012")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    ids = sorted(d for d in os.listdir(REPORTS)
                 if d.startswith("lab-tr-") and os.path.isdir(os.path.join(REPORTS, d)))
    if only:
        unknown = only - set(ids)
        if unknown:
            print("unknown package(s): " + ", ".join(sorted(unknown)), file=sys.stderr)
            return 2
        ids = [i for i in ids if i in only]

    rows = []
    for pid in ids:
        pdir = os.path.join(REPORTS, pid)
        args = pick_command(pid, pdir)
        if not args:
            rows.append({"id": pid, "command": "no self-test", "status": "SKIP", "seconds": 0.0})
            print("[%s] SKIP  no self-test" % pid, flush=True)
            continue
        tmp = tempfile.mkdtemp(prefix=pid + "_")
        args = [x.replace("{tmp}", tmp) for x in args]
        shown = "python " + " ".join(x.replace(tmp, "{tmp}") for x in args)
        print("[%s] RUN   %s" % (pid, shown), flush=True)
        run_dir = pdir
        if pid in ISOLATE:
            run_dir = os.path.join(tmp, "pkg")
            shutil.copytree(pdir, run_dir)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        t0 = time.time()
        try:
            cp = subprocess.run([sys.executable] + args, cwd=run_dir, timeout=a.timeout, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            status = "PASS" if cp.returncode == 0 else "FAIL"
            out = cp.stdout.decode("utf-8", "replace")
        except subprocess.TimeoutExpired as e:
            status = "FAIL"
            out = (e.stdout or b"").decode("utf-8", "replace") + "\n[timeout after %d s]" % a.timeout
        secs = round(time.time() - t0, 1)
        shutil.rmtree(tmp, ignore_errors=True)
        if status == "FAIL":
            print("---- output tail of %s ----" % pid)
            print("\n".join(out.splitlines()[-25:]))
            print("----", flush=True)
        rows.append({"id": pid, "command": shown, "status": status, "seconds": secs})
        print("[%s] %s  %.1f s" % (pid, status, secs), flush=True)

    w = max([len(r["id"]) for r in rows] + [7])
    c = max([len(r["command"]) for r in rows] + [7])
    print("\n%-*s  %-*s  %-6s  %s" % (w, "package", c, "command", "result", "seconds"))
    for r in rows:
        print("%-*s  %-*s  %-6s  %7.1f" % (w, r["id"], c, r["command"], r["status"], r["seconds"]))
    n = {s: sum(1 for r in rows if r["status"] == s) for s in ("PASS", "FAIL", "SKIP")}
    print("\nPASS %d  FAIL %d  SKIP %d" % (n["PASS"], n["FAIL"], n["SKIP"]))
    with open(RESULTS, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
