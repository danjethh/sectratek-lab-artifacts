"""Items of the report that can be reproduced without the corpus, from the values the report itself prints.

table2.md                   Table 2, from the store registry in stores.py
fig1_pipeline.svg           Figure 1
fig2_horizons.svg           Figure 2, from the medians, quartiles and ranges printed in Tables 4 and 5
fig3_reach30.svg            Figure 3, from the counts printed in Table 4 and Section 5.6 (intervals recomputed)
table4_reach30.md           the 30 d columns of Table 4: counts, shares and Wilson intervals recomputed
printed_checks.json         recomputed values compared with the printed ones, and the clock-rule checks of Listing 1
"""
import json
import os

import figures
import stats
import stores

HERE = os.path.dirname(os.path.abspath(__file__))


def load_printed():
    with open(os.path.join(HERE, "data", "paper_tables_4_5.json"), encoding="utf-8") as f:
        return json.load(f)["rows"]


def run(out):
    os.makedirs(out, exist_ok=True)
    rows = load_printed()
    checks = {}
    # Table 2
    with open(os.path.join(out, "table2.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("Table 2 (store registry of stores.py)\n\n" + stores.table2_markdown())
    # Figure 1
    with open(os.path.join(out, "fig1_pipeline.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(figures.fig1_pipeline())
    # Figure 2 from printed medians, quartiles and ranges
    r2 = [{"group": g, "label": lab, "n": r["n"], "median": r["median"], "q1": r["q1"], "q3": r["q3"],
           "min": r["min"], "max": r["max"], "limit": lim}
          for g, lab, key, lim in figures.FIG2_ORDER for r in rows if r["key"] == key]
    with open(os.path.join(out, "fig2_horizons.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(figures.fig2_horizons(r2))
    checks["fig2_rows"] = len(r2)
    # Figure 3 and the 30 d columns of Table 4: Wilson intervals recomputed from the printed counts
    r3, md, mism = [], ["| Store | n | reach 30 d | share | Wilson 95% | printed |", "|---|---|---|---|---|---|"], []
    by = {r["key"]: r for r in rows}
    for g, lab, key in figures.FIG3_ORDER:
        r = by[key]
        p, lo, hi = stats.wilson(r["ge30"], r["n"])
        r3.append({"group": g, "label": lab, "k": r["ge30"], "n": r["n"], "p": p, "lo": lo, "hi": hi})
    for r in rows:
        if r["ge30"] is None:
            continue
        p, lo, hi = (round(v, 3) for v in stats.wilson(r["ge30"], r["n"]))  # three decimals first, as the runner does
        pr = r["printed_ci30_pct"]
        md.append("| %s | %d | %d | %.2f | %d%%-%d%% | %s |" % (stores.LABELS[r["key"]], r["n"], r["ge30"], p,
                                                               round(100 * lo), round(100 * hi),
                                                               ("%d%%-%d%%" % tuple(pr)) if pr else "(not printed)"))
        if pr and (round(100 * lo), round(100 * hi)) != tuple(pr):
            mism.append(r["key"])
    with open(os.path.join(out, "fig3_reach30.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(figures.fig3_reach(r3))
    with open(os.path.join(out, "table4_reach30.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    checks["table4_wilson_30d_rows_compared"] = sum(1 for r in rows if r["printed_ci30_pct"])
    checks["table4_wilson_30d_mismatches"] = mism
    # the report states a text value: 0 of 19 allows up to 17%
    checks["wilson_0_of_19_upper_pct"] = round(100 * stats.wilson(0, 19)[2])
    # "the achieved coverage is at least 95.7% for every interval shown in Tables 4 and 5"
    cov = {str(n): round(stats.achieved_coverage(n), 3) for n in sorted({r["n"] for r in rows})}
    checks["order_statistic_coverage_by_n"] = cov
    checks["min_coverage"] = min(cov.values())
    # Listing 1: boundaries of the clock rule (acquisition time T = 1,000,000 s)
    t = 1_000_000.0
    h = 3600.0
    checks["clock_rule"] = {
        "newest_72h_before": stores.clock_rule(t - 72 * h, t)[0], "newest_72h_01_before": stores.clock_rule(t - 72.1 * h, t)[0],
        "newest_1h_after": stores.clock_rule(t + h, t)[0], "newest_1h_01_after": stores.clock_rule(t + 1.01 * h, t)[0],
        "no_records": stores.clock_rule(None, t)[0]}
    with open(os.path.join(out, "printed_checks.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(checks, f, indent=1, sort_keys=True)
        f.write("\n")
    return checks
