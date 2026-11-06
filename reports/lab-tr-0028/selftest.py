"""Self test: copy the package to two clean temporary directories, run run_all.py in each with the fixed
seeds, compare the SHA-256 of every output file, and check the documented key outputs.

    python selftest.py

Exit code 0 only if both runs give identical, non-empty files and every check passes. About a minute.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# Table 9 of the report: recall of restored records / share of native records flagged, percent (R1 R2 R3 R4)
TABLE9 = {
    "S1 at setup, ascending": ["100.0 / 0.0", "5.0 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S2 at setup, descending": ["100.0 / 0.0", "99.8 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S3 at setup, by thread": ["100.0 / 0.0", "98.0 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S4 at setup, random": ["100.0 / 0.0", "99.4 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S5 day 3, ascending": ["99.4 / 0.0", "100.0 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S6 day 30, ascending": ["92.1 / 0.0", "100.0 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S7 day 30, by thread": ["92.1 / 0.0", "100.0 / 0.0", "100.0 / 0.0", "100.0 / 0.0"],
    "S11 gradual sync, 14 days": ["100.0 / 0.0", "98.9 / 0.0", "100.0 / 0.0", "100.0 / 7.6"],
    "S8 no restore": ["- / 0.0", "- / 0.0", "- / 0.0", "- / 0.0"],
    "S9 no restore, clock step": ["- / 0.0", "- / 0.7", "- / 0.7", "- / 0.7"],
    "S10 setup, ascending, clock step": ["100.0 / 0.0", "7.0 / 0.6", "100.0 / 0.6", "100.0 / 48.5"],
}
# Section 5.7: boundary 3 days too late flags 1.7%, 14 days too late 7.7%, 3 days too early none; loses 0.8% of S1
BOUNDARY = ["1.7", "7.7", "0.0", "99.2"]
# Documented result of the run on the invented archives (not a finding of the report)
INVENTED_GAPS = [0.5, 2.0, 30.0, 60.0, 100.0, 120.0, 200.0, 400.0]


def copy_package(dst):
    shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__", "sample_output", "*.pyc"))


def sha_tree(root):
    out = {}
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            p = os.path.join(base, name)
            with open(p, "rb") as f:
                data = f.read()
            out[os.path.relpath(p, root).replace(os.sep, "/")] = (hashlib.sha256(data).hexdigest(), len(data))
    return out


def check(cond, msg, failures):
    if not cond:
        failures.append(msg)


def unit_checks(pkg, failures):
    """Small checks of the building blocks, run in a subprocess inside the copy."""
    code = r'''
import random, struct, zipfile, io, os, tempfile
import abx, fixtures, zipscan, gen_archives
ev = [["start", "a", {"x": 5, "y": 2 ** 40, "s": "t", "b": True}], ["start", "c", {}], ["end", "c"], ["end", "a"]]
back = [e for e in abx.parse(abx.dump(ev))]
assert back == ev, back
rows = [(1, 100 * 86400000), (2, 99 * 86400000), (3, 50 * 86400000), (4, 101 * 86400000)]
assert fixtures.rule_boundary(rows, 60) == {3}
assert fixtures.rule_order(rows) == {2, 3}
assert fixtures.rule_hull({2, 3}, rows) == {2, 3}
assert fixtures.rule_hull({1, 3}, rows) == {1, 2, 3}
rng = random.Random(1)
r1, t1 = fixtures.build(fixtures.SCENARIOS["S1 at setup, ascending"], rng)
assert [i for i, _ in r1] == list(range(1, len(r1) + 1))
d = tempfile.mkdtemp()
p = os.path.join(d, "t.zip")
gen_archives.write_zip(p, [("data/x/a", b"hello", 1704067200), ("data/x/b", b"", 1704153600)])
ents = {e["name"]: e for e in zipscan.scan(p, lambda n: True)}
assert ents["data/x/a"]["mtime"] == 1704067200 and ents["data/x/a"]["mtime_src"] == "UT"
assert zipscan.read_member(p, ents["data/x/a"]) == b"hello"
print("unit ok")
'''
    r = subprocess.run([sys.executable, "-c", code], cwd=pkg, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    check(r.returncode == 0 and "unit ok" in r.stdout, "unit checks failed: " + (r.stderr or r.stdout)[-400:], failures)


def main():
    failures = []
    roots = [tempfile.mkdtemp(prefix="st28_"), tempfile.mkdtemp(prefix="st28_")]
    try:
        procs = []
        for k, root in enumerate(roots):
            pkg = os.path.join(root, "pkg")
            copy_package(pkg)
            procs.append(subprocess.Popen(
                [sys.executable, "run_all.py", "--out", os.path.join(root, "out")], cwd=pkg,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")))
        for k, p in enumerate(procs):
            so, se = p.communicate()
            check(p.returncode == 0, "run %d failed: %s" % (k + 1, se[-500:]), failures)
        if not failures:
            a, b = sha_tree(os.path.join(roots[0], "out")), sha_tree(os.path.join(roots[1], "out"))
            check(a == b, "the two runs differ: %s" % sorted(set(a) ^ set(b) | {k for k in a if k in b and a[k] != b[k]}), failures)
            check(len(a) > 0 and all(n > 0 for _, n in a.values()), "empty or no outputs", failures)
            out = os.path.join(roots[0], "out")
            with open(os.path.join(out, "table9_fixtures.md"), encoding="utf-8") as f:
                rows = {}
                for line in f:
                    if line.startswith("| S") and not line.startswith("| Scenario"):
                        cells = [c.strip() for c in line.strip().strip("|").split("|")]
                        rows[cells[0]] = cells[1:]
            check(rows == TABLE9, "Table 9 differs from the report: %s" % {k: v for k, v in rows.items() if TABLE9.get(k) != v}, failures)
            with open(os.path.join(out, "boundary_error_statements.csv"), encoding="utf-8") as f:
                vals = [line.rstrip("\n").rsplit(",", 1)[1] for line in list(f)[1:]]
            check(vals == BOUNDARY, "boundary statements %s" % vals, failures)
            with open(os.path.join(out, "pipeline", "report.json"), encoding="utf-8") as f:
                rep = json.load(f)
            check(rep["android"]["gap_WU"]["values"] == INVENTED_GAPS, "invented gaps differ", failures)
            rules = rep["android"]["rules_vs_creator"]["rules"]
            check([rules[k]["recall_pct"] for k in ("R1_W", "R1_U", "R2", "R3_U", "R4_U")] == [88.94, 100.0, 24.94, 100.0, 100.0],
                  "invented rule recalls", failures)
            check(rep["android"]["restore_signals"]["at_least_one"] == 5 and rep["android"]["restore_signals"]["none"] == 3,
                  "invented restore signals", failures)
            check(rep["android"]["n"] == 8 and rep["bugreports"]["n"] == 3 and rep["ios"]["n"] == 4, "invented counts", failures)
            check(not any("__pycache__" in k for k in a), "pycache in output", failures)
            unit_checks(os.path.join(roots[0], "pkg"), failures)
    finally:
        for root in roots:
            shutil.rmtree(root, ignore_errors=True)
    if failures:
        for m in failures:
            print("FAIL:", m)
        return 1
    print("selftest ok: two runs identical; Table 9 and Section 5.7 statements as in the report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
