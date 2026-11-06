"""Run the readers and the analysis on the archives named in a configuration file.

    python run_corpus.py CONFIG.json --out DIR [--keep-raw]

CONFIG.json (paths relative to the file's own directory, or absolute):

    {"migration_creator_prefixes": ["package.name.prefix"],
     "android":     [{"id": "a1", "path": "device_a1.zip"}],
     "bug_reports": [{"id": "b1", "path": "report_b1.zip"}],
     "ios":         [{"id": "i1", "path": "device_i1.zip"}]}

There is no default path. The report holds counts, shares and day offsets only. With --keep-raw the lists of
integers that the readers return (dates, identifiers, flags; no names or content) are also written, so that
the analysis can be repeated without opening the archives again.
"""
import argparse
import json
import os

import analyse
import figures
import readers
import tables


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    for key in ("android", "bug_reports", "ios"):
        for item in cfg.get(key, []):
            if not os.path.isabs(item["path"]):
                item["path"] = os.path.join(base, item["path"])
    return cfg


def read_all(cfg):
    prefixes = tuple(cfg.get("migration_creator_prefixes", ()))
    android, bugs, ios = [], [], []
    for item in cfg.get("android", []):
        r = readers.read_android(item["path"], prefixes)
        r["id"] = item["id"]
        android.append(r)
    for item in cfg.get("bug_reports", []):
        r = readers.read_bugreport(item["path"])
        r["id"] = item["id"]
        bugs.append(r)
    for item in cfg.get("ios", []):
        r = readers.read_ios(item["path"])
        r["id"] = item["id"]
        ios.append(r)
    return android, bugs, ios


def write_outputs(out_dir, analysis, banner):
    """Write report.json, report.md and the SVG files of Figures 2 and 3."""
    os.makedirs(out_dir, exist_ok=True)
    A = analysis["android"]
    slim = json.loads(json.dumps(analysis, sort_keys=True))
    if A:  # the per-device share lists belong to the figures, not to the report
        for key in ("sms", "calls", "media", "apps"):
            slim["android"]["records"][key].pop("shares", None)
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(slim, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(tables.pipeline_report(A, analysis["bugreports"], analysis["ios"], banner) + "\n")
    if A:
        with open(os.path.join(out_dir, "fig2_gap.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(figures.fig2_gap(A["gap_WU"]["values"]))
        with open(os.path.join(out_dir, "fig3_shares.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(figures.fig3_shares(A["records"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep-raw", action="store_true")
    args = ap.parse_args()
    cfg = load_config(args.config)
    android, bugs, ios = read_all(cfg)
    analysis = analyse.analyse(android, bugs, ios)
    write_outputs(args.out, analysis, "Run on the archives named in the configuration file.")
    if args.keep_raw:
        with open(os.path.join(args.out, "raw_readers.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"android": android, "bug_reports": bugs, "ios": ios}, f)
    for group in (android, bugs, ios):
        for r in group:
            if r.get("errors"):
                print("%s: unreadable parts: %s" % (r.get("id"), "; ".join(r["errors"])))


if __name__ == "__main__":
    main()
