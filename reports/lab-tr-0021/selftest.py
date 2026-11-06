"""Self test: run the package twice in clean copies with the fixed seed, compare every output file byte for byte
(SHA-256), and check the key outputs the synthetic run is documented to give.  Exit code 0 only if all hold."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

SEED = 21
HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"__pycache__", "sample_output"}


def copy_package(dst):
    for name in sorted(os.listdir(HERE)):
        if name in SKIP:
            continue
        src = os.path.join(HERE, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dst, name), ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, os.path.join(dst, name))


def run_once(tag, root):
    pkg = os.path.join(root, "pkg_" + tag)
    out = os.path.join(root, "out_" + tag)
    os.makedirs(pkg)
    copy_package(pkg)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "run_all.py", "--out", out, "--seed", str(SEED)], cwd=pkg, env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("run_all.py failed")
    return out


def hashes(out):
    h = {}
    for r, _ds, fs in os.walk(out):
        for f in sorted(fs):
            p = os.path.join(r, f)
            data = open(p, "rb").read()
            if not data:
                raise SystemExit("empty output file: " + os.path.relpath(p, out))
            h[os.path.relpath(p, out).replace(os.sep, "/")] = hashlib.sha256(data).hexdigest()
    return h


def expect(cond, msg, fails):
    if not cond:
        fails.append(msg)


def unit_tests(fails):
    sys.path.insert(0, HERE)
    import stats
    import stores
    # Wilson interval printed in the report text: 0 of 19 allows up to 17 percent
    expect(round(100 * stats.wilson(0, 19)[2]) == 17, "wilson 0/19", fails)
    expect(stats.wilson(0, 0) is None, "wilson n=0", fails)
    # median interval: n = 7 uses the extreme values, coverage 1 - 2/128
    med, lo, hi, cov = stats.median_ci([1, 2, 3, 4, 5, 6, 7])
    expect((med, lo, hi) == (4, 1, 7) and abs(cov - (1 - 2 / 128)) < 1e-12, "median_ci n=7", fails)
    expect(stats.cell([1, 2, 3, 4], "x").get("suppressed") is True, "cell below five suppressed", fails)
    expect(abs(stats.spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1) < 1e-12, "spearman", fails)
    # clock rule boundaries and record filter
    t = 10_000_000.0
    expect(stores.clock_rule(t - 72 * 3600, t)[0] == "pass" and stores.clock_rule(t - 72 * 3600 - 1, t)[0] == "fail",
           "clock rule lower bound", fails)
    expect(stores.clock_rule(t + 3600, t)[0] == "pass" and stores.clock_rule(t + 3601, t)[0] == "fail",
           "clock rule upper bound", fails)
    s = stores.summarise_times([100.0, stores.MIN_PLAUSIBLE + 5, stores.MIN_PLAUSIBLE + 50, 2e9], 1.9e9, "x")
    expect(s["n_clock_err_low"] == 1 and s["n_clock_err_high"] == 1 and s["oldest"] == stores.MIN_PLAUSIBLE + 5,
           "record filter", fails)
    # body of a log section: 3 head strays days before a body of 1,000 lines every 2 s
    body = [1_000_000.0 + 2 * i for i in range(1000)]
    strays = [100.0, 200.0, 5000.0]
    b, k = stores.body_start(strays + body)
    expect(b == body[0] and k == 3, "body start with strays", fails)
    b, k = stores.body_start(body)
    expect(b == body[0] and k == 0, "body start without strays", fails)
    # strays above 0.5 percent of the lines are not strays
    b, k = stores.body_start([100.0] * 8 + body)
    expect(k == 0, "stray fraction cap", fails)


def main():
    fails = []
    unit_tests(fails)
    root = tempfile.mkdtemp(prefix="tr21self")
    try:
        a = run_once("a", root)
        b = run_once("b", root)
        ha, hb = hashes(a), hashes(b)
        expect(ha == hb, "outputs of the two runs differ: %s" % sorted(k for k in set(ha) | set(hb) if ha.get(k) != hb.get(k)), fails)
        expect(len(ha) >= 20, "too few output files (%d)" % len(ha), fails)
        pc = json.load(open(os.path.join(a, "paper", "printed_checks.json")))
        expect(pc["table4_wilson_30d_rows_compared"] == 8 and pc["table4_wilson_30d_mismatches"] == [], "Table 4 intervals for 30 d", fails)
        expect(pc["fig2_rows"] == 17, "Figure 2 rows", fails)
        expect(pc["wilson_0_of_19_upper_pct"] == 17, "0 of 19 interval", fails)
        expect(pc["min_coverage"] == 0.957, "minimum interval coverage 95.7 percent", fails)
        expect(pc["clock_rule"] == {"newest_1h_01_after": "fail", "newest_1h_after": "pass", "newest_72h_01_before": "fail",
                                    "newest_72h_before": "pass", "no_records": "no-anchor"}, "Listing 1 boundaries", fails)
        rec = json.load(open(os.path.join(a, "synthetic", "recovery.json")))
        expect(rec["within_tolerance"] is True, "readers recover the invented horizons", fails)
        expect(rec["head_strays"] == {"strays_exact": 6, "strays_total": 6}, "head strays recovered", fails)
        rep = json.load(open(os.path.join(a, "synthetic", "report.json")))
        sm = rep["sample"]
        expect((sm["ios"]["extractions"], sm["ios"]["devices"], sm["ios"]["clock_checked"]) == (16, 15, 14), "iOS sample", fails)
        expect((sm["android"]["devices"], sm["android"]["clock_checked"]) == (10, 10), "Android sample", fails)
        expect((sm["bugreport"]["devices"], sm["bugreport"]["clock_checked"]) == (6, 6), "bug-report sample", fails)
        expect(rep["checks"]["ios|interactionc|wal_changes_oldest"] == [9, 14], "interactionC log changes oldest", fails)
        expect(rep["checks"]["ios|knowledgec|wal_changes_oldest"] == [0, 14], "knowledgeC log changes nothing", fails)
        expect(rep["posthoc"]["bugreport_reports_with_head_strays"] == [4, 6], "head strays in 4 of 6 reports", fails)
        expect(rep["posthoc"]["bugreport_body_stable_to_2pct"] == [3, 6], "body start stable on the grid", fails)
        expect(rep["errors"] == [], "reader errors", fails)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    if fails:
        print("SELFTEST FAILED")
        for f in fails:
            print(" -", f)
        return 1
    print("SELFTEST PASSED: two runs identical (%d files), key outputs as documented" % len(ha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
