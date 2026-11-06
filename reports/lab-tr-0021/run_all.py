"""Reproduce everything that can be reproduced without the corpus.

  python run_all.py --out DIR [--seed N] [--keep-archives]

DIR/paper/       report items rebuilt from the values the report prints (Table 2, Figures 1 to 3, the 30 d columns
                 of Table 4, the checks of Listing 1 and of the interval coverage)
DIR/synthetic/   the full pipeline on invented archives: report.md/json, per-device records, figures, recovery.json
                 (how well the readers recover the invented horizons). This shows the pipeline, not the findings.
"""
import argparse
import json
import os
import shutil
import tempfile

import paper_items
import run_corpus
import synth

STRICT_TOL_D = 3e-5     # one second, in days
LOOSE_TOL_D = 0.006     # knowledgeC "other streams" horizon is reported to two decimals


def recovery(cfg, recs):
    """Compare the horizons the readers found with the invented ones. Returns per-store maximum absolute error."""
    by = {r["id"]: r for r in recs}
    err, n, head = {}, {}, {"strays_exact": 0, "strays_total": 0}
    for d in cfg["devices"]:
        r = by[d["id"]]
        for key, truth in sorted(d.get("truth", {}).items()):
            if key == "head_strays":
                head["strays_total"] += 1
                head["strays_exact"] += int(r["stores"]["logcat_system"]["head_strays"] == truth)
                continue
            if key == "interactionc_nowal":
                got = r["stores"]["interactionc"]["nowal_horizon_d"]
            elif key == "logcat_system_oldest_line":
                got = r["stores"]["logcat_system"]["oldest_line_horizon_d"]
            else:
                got = r["stores"][key]["horizon_d"]
            err[key] = max(err.get(key, 0.0), abs(got - truth))
            n[key] = n.get(key, 0) + 1
    out = {"max_abs_error_days": {k: round(v, 7) for k, v in sorted(err.items())},
           "devices_compared": dict(sorted(n.items())), "head_strays": head}
    out["within_tolerance"] = all(v <= (LOOSE_TOL_D if k == "knowledgec_other" else STRICT_TOL_D)
                                  for k, v in err.items())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--keep-archives", action="store_true", help="also write the invented archives to OUT/synthetic")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    paper_items.run(os.path.join(a.out, "paper"))
    work = tempfile.mkdtemp(prefix="tr21all")
    try:
        cfg = synth.make_corpus(work, a.seed)
        cfg_path = os.path.join(work, "config.json")
        with open(cfg_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cfg, f, indent=1)
        sdir = os.path.join(a.out, "synthetic")
        rep, recs = run_corpus.run(cfg_path, sdir, "# LAB-TR-0021 runner report on invented archives (seed %d)" % a.seed)
        shutil.copyfile(cfg_path, os.path.join(sdir, "config.json"))
        rec = recovery(cfg, recs)
        with open(os.path.join(sdir, "recovery.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
            f.write("\n")
        if a.keep_archives:
            shutil.copytree(os.path.join(work, "archives"), os.path.join(sdir, "archives"))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("recovery within tolerance:", rec["within_tolerance"])
    print("errors:", len(rep["errors"]))


if __name__ == "__main__":
    main()
