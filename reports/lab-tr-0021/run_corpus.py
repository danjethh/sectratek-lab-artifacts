"""Run the readers and the analysis on the archives named in a configuration file (read-only).

  python run_corpus.py --config config.json --out results

Configuration (JSON; relative paths are relative to the configuration file):
  {"devices": [
     {"id": "a1", "kind": "ios_ffs" | "android_ffs" | "bugreport", "path": "archive.zip",
      "acq_time": 1760000000 | "2026-01-31T12:00:00Z",   # optional; default: modification time of the archive
      "acq_source": "record" | "file",                   # optional label for the time source (default "record")
      "os_major": 26, "device_class": "phone", "vendor_group": "g1",   # optional strata labels
      "same_device_group": "x"}],                        # extractions of one device share a label
   "exclude_path_patterns": ["text"]}                    # optional; matched case-insensitively against id and path,
                                                         # before any file is opened
Bug reports take their acquisition time from the dumpstate header; acq_time is ignored for them.
Output: report.json, report.md, devices/<id>.json, fig1_pipeline.svg, fig2_horizons.svg, fig3_reach30.svg.
"""
import argparse
import json
import os
import shutil
import tempfile

import analysis
import figures


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    for d in cfg["devices"]:
        if not os.path.isabs(d["path"]):
            d["path"] = os.path.join(base, d["path"])
    return cfg


def run(config_path, out, heading="# LAB-TR-0021 runner report"):
    cfg = load_config(config_path)
    pats = [p.lower() for p in cfg.get("exclude_path_patterns", [])]
    os.makedirs(os.path.join(out, "devices"), exist_ok=True)
    work = tempfile.mkdtemp(prefix="tr21work")
    recs, excluded = [], 0
    try:
        for dev in cfg["devices"]:
            if any(p in (dev["path"] + "|" + dev["id"]).lower() for p in pats):
                excluded += 1
                continue
            recs.append(analysis.process_device(dev, work))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rep = analysis.build_report(recs)
    rep["excluded_by_pattern"] = excluded
    for r in recs:
        with open(os.path.join(out, "devices", r["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(r, f, indent=1, sort_keys=True)
            f.write("\n")
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(analysis.report_markdown(rep, heading))
    r2, r3 = figures.rows_from_cells(rep["cells"])
    for name, svg in (("fig1_pipeline.svg", figures.fig1_pipeline()), ("fig2_horizons.svg", figures.fig2_horizons(r2)),
                      ("fig3_reach30.svg", figures.fig3_reach(r3))):
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
    return rep, recs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rep, recs = run(a.config, a.out)
    print("devices read: %d, errors: %d" % (len(recs), len(rep["errors"])))


if __name__ == "__main__":
    main()
