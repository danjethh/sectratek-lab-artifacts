"""Per-device processing and the aggregate report (report Sections 3.3 to 3.5 and 5).

process_device(dev, work)  reads one archive (read-only) and returns a device record with horizons and the clock check
build_report(records)      aggregates the records into cells, prevalence, checks and the post hoc counts
report_markdown(rep)       tables in the layout of report Tables 3 to 7
Device records hold the identifier given in the configuration, times and counts only.
"""
import datetime
import json
import os

import stats
import stores
from stats import cell, spearman, wilson
from stores import DAY

KIND = {"ios_ffs": "ios", "android_ffs": "android", "bugreport": "bugreport"}
KIND_LABEL = {"ios": "iOS file system", "android": "Android file system", "bugreport": "Android bug report"}
STORE_ORDER = {
    "ios": ["ul_persist", "ul_signpost", "ul_special", "ul_highvolume", "powerlog_archives", "biome_appinfocus",
            "knowledgec", "knowledgec_other", "interactionc"],
    "android": ["usage_daily", "usage_any", "notif_history", "dropbox", "netstats", "procstats",
                "vendor_battery_hist"],
    "bugreport": ["logcat_system", "logcat_events"],
}
# limits stated in public sources, days (report Table 2 and Table 5); used for the "within" counts only
SOURCE_LIMIT_BAND = {"usage_daily": (0, 10.2), "notif_history": (0, 1.5), "dropbox": (0, 3.1), "netstats": (75, 105)}


def _epoch(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return datetime.datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()


def process_device(dev, work):
    """dev: one entry of the configuration. Returns the device record."""
    kind = KIND[dev["kind"]]
    rec = {"id": dev["id"], "kind": kind, "os_major": dev.get("os_major"), "device_class": dev.get("device_class"),
           "vendor_group": dev.get("vendor_group"), "same_device_group": dev.get("same_device_group")}
    try:
        path = dev["path"]
        if kind == "bugreport":
            res = stores.read_bugreport(path)
            rec["tacq_src"] = "report header"
        else:
            tacq = _epoch(dev.get("acq_time"))
            if tacq is not None:
                rec["tacq_src"] = dev.get("acq_source", "record")
            else:
                tacq, rec["tacq_src"] = os.path.getmtime(path), "file"
            res = stores.read_ios(path, tacq, work) if kind == "ios" else stores.read_android(path, tacq)
            res["tacq"] = tacq
        rec.update(res)
        _finish(rec)
        rec["status"] = "ok"
    except Exception as ex:  # a reader that fails is reported as unavailable, never as empty
        rec["status"] = "error"
        rec["error"] = type(ex).__name__ + ": " + str(ex)[:120]
    return rec


def _finish(rec):
    """Horizons (acquisition minus oldest record) and the clock check."""
    tacq = rec["tacq"]
    if rec["kind"] == "bugreport":
        steps = sum(v for k, v in rec["checks"].items() if k.endswith("backward_steps_over_hour"))
        rec["clock_check"] = "pass-same-clock" if steps == 0 else "flag-backward-step"
    else:
        rec["clock_check"], lag = stores.clock_rule(rec.get("device_newest"), tacq)
        if lag is not None:
            rec["anchor_lag_h"] = lag
    for s in rec["stores"].values():
        if "oldest" not in s:
            continue
        start = s.get("body_start", s["oldest"])  # bug-report logs are counted from the start of the body
        s["horizon_d"] = (tacq - start) / DAY
        s["newest_lag_d"] = (tacq - s["newest"]) / DAY
        if s.get("body_start") is not None:
            s["oldest_line_horizon_d"] = (tacq - s["oldest"]) / DAY
        if "p01" in s:
            s["horizon_first_pct_d"] = (tacq - s["p01"]) / DAY
        if s.get("infocus_min"):
            s["infocus_horizon_d"] = (tacq - s["infocus_min"]) / DAY
        if s.get("nowal_min"):
            s["nowal_horizon_d"] = (tacq - s["nowal_min"]) / DAY
    deep = rec.get("deep_knowledgec") or {}
    if deep.get("horizon_excl_signals_sync_d") is not None:
        rec["stores"]["knowledgec_other"] = {"kind": "derived", "horizon_d": deep["horizon_excl_signals_sync_d"],
                                             "newest_lag_d": rec["stores"]["knowledgec"].get("newest_lag_d")}


def mark_same_device(records):
    """Within a same_device_group only the extraction with the latest acquisition time counts for distributions."""
    best = {}
    for r in records:
        g = r.get("same_device_group")
        if g and r["status"] == "ok" and (g not in best or r["tacq"] > best[g]["tacq"]):
            best[g] = r
    for r in records:
        g = r.get("same_device_group")
        r["same_device_drop"] = bool(g and r["status"] == "ok" and best[g] is not r)


# ---------------------------------------------------------------- aggregate
def _count(d, k):
    d[k] = d.get(k, 0) + 1


def build_report(records):
    mark_same_device(records)
    rep = {"sample": {}, "prevalence": {}, "cells": [], "strata": [], "checks": {}, "clock": {}, "correlations": {},
           "reach30": {}, "sensitivity": {}, "posthoc": {}, "errors": []}
    for short in ("ios", "android", "bugreport"):
        rs = [r for r in records if r["kind"] == short]
        ok = [r for r in rs if r["status"] == "ok"]
        dev = [r for r in ok if not r["same_device_drop"] and r["clock_check"] in ("pass", "pass-same-clock")]
        smp = {"extractions": len(rs), "readable": len(ok), "errors": len(rs) - len(ok),
               "devices": len([r for r in ok if not r["same_device_drop"]]), "clock_checked": len(dev),
               "tacq_src": {}, "clock_check": {}}
        for r in ok:
            _count(smp["tacq_src"], r["tacq_src"])
            _count(smp["clock_check"], r["clock_check"])
        rep["sample"][short] = smp
        if not ok:
            continue
        names = [s for s in STORE_ORDER[short] if any(s in r["stores"] for r in ok)]
        rep["prevalence"][short] = {s: [sum(1 for r in ok if "horizon_d" in r["stores"].get(s, {})), len(ok)]
                                    for s in names}
        lags = sorted(r["anchor_lag_h"] for r in ok if "anchor_lag_h" in r and not r["same_device_drop"]
                      and r["clock_check"] == "pass")
        clk = {"records_before_floor": sum(s.get("n_clock_err_low", 0) for r in ok for s in r["stores"].values()),
               "records_after_acq": sum(s.get("n_clock_err_high", 0) for r in ok for s in r["stores"].values())}
        if lags:
            clk.update(anchor_lag_h_median_min_max_n=[round(lags[len(lags) // 2], 2), round(lags[0], 2),
                                                      round(lags[-1], 2), len(lags)])
        clk["clock_failed"] = sum(1 for r in ok if r["clock_check"] == "fail" and not r["same_device_drop"])
        rep["clock"][short] = clk
        for s in names:
            base = [r for r in dev if "horizon_d" in r["stores"].get(s, {})]
            hz = [r["stores"][s]["horizon_d"] for r in base]
            rep["cells"].append(dict(cell(hz, "%s|%s|all" % (short, s)), store=s, platform=short))
            for fld in ("os_major", "device_class", "vendor_group"):
                vals = sorted({r.get(fld) for r in base if r.get(fld) is not None}, key=str)
                for v in vals:
                    sub = [r["stores"][s]["horizon_d"] for r in base if r.get(fld) == v]
                    if len(sub) == len(base):  # the stratum is the whole sample
                        continue
                    rep["strata"].append(dict(cell(sub, "%s|%s|%s=%s" % (short, s, fld, v)), store=s, platform=short))
            p01 = [r["stores"][s]["horizon_first_pct_d"] for r in base if "horizon_first_pct_d" in r["stores"][s]]
            if p01:
                rep["sensitivity"]["%s|%s|p01" % (short, s)] = cell(p01, "p01")
            rep["sensitivity"]["%s|%s|newest_lag" % (short, s)] = cell([r["stores"][s]["newest_lag_d"] for r in base],
                                                                       "newest_lag")
            iff = [r["stores"][s]["infocus_horizon_d"] for r in base if "infocus_horizon_d" in r["stores"][s]]
            if iff:
                rep["sensitivity"]["%s|%s|infocus" % (short, s)] = cell(iff, "infocus")
            if short == "bugreport":
                old = [r["stores"][s]["oldest_line_horizon_d"] for r in base]
                rep["sensitivity"]["%s|%s|oldest_line" % (short, s)] = cell(old, "oldest_line")
            nw = [(r["stores"][s]["nowal_horizon_d"], r["stores"][s]["horizon_d"]) for r in base
                  if r["stores"][s].get("nowal_horizon_d") is not None]
            if nw:
                rep["checks"]["%s|%s|wal_changes_oldest" % (short, s)] = [sum(1 for a, b in nw if abs(a - b) > 1e-6),
                                                                          len(nw)]
        agg = {}
        for r in ok:
            for k, v in r["checks"].items():
                a = agg.setdefault(k, [0, 0])
                if isinstance(v, list):
                    a[0] += v[0]
                    a[1] += v[1]
                else:
                    a[0] += 1 if v else 0
                    a[1] += 1
        rep["checks"].update({"%s|%s" % (short, k): v for k, v in sorted(agg.items())})
        cov = [max((s.get("horizon_d", -1) for s in r["stores"].values()), default=-1) for r in dev]
        if cov:
            k = sum(1 for x in cov if x >= 30)
            rep["reach30"][short] = [k, len(cov)] + [round(v, 3) for v in wilson(k, len(cov))]
    _correlations(rep, records)
    _posthoc(rep, records)
    rep["errors"] = [{"id": r["id"], "kind": r["kind"], "error": r.get("error")} for r in records
                     if r["status"] != "ok"]
    return rep


def _correlations(rep, records):
    pr = [(r["stores"]["ul_persist"]["bytes"], r["stores"]["ul_persist"]["horizon_d"]) for r in records
          if r["kind"] == "ios" and r["status"] == "ok" and not r["same_device_drop"] and r["clock_check"] == "pass"
          and "horizon_d" in r["stores"].get("ul_persist", {})]
    if len(pr) >= stats.MIN_CELL:
        rep["correlations"]["persist_bytes_vs_horizon_spearman_n"] = [round(spearman([a for a, b in pr],
                                                                                     [b for a, b in pr]), 3), len(pr)]
        rate = sorted(a / b for a, b in pr if b > 0)
        rep["correlations"]["persist_bytes_per_day_median_min_max"] = [round(rate[len(rate) // 2], 1),
                                                                       round(rate[0], 1), round(rate[-1], 1)]


def _posthoc(rep, records):
    ph = rep["posthoc"]
    ok = [r for r in records if r["status"] == "ok" and not r["same_device_drop"]
          and r["clock_check"] in ("pass", "pass-same-clock")]

    def band(kind, s, lo, hi):
        xs = [r["stores"][s]["horizon_d"] for r in ok if r["kind"] == kind and "horizon_d" in r["stores"].get(s, {})]
        return [sum(1 for x in xs if lo <= x <= hi), len(xs)]
    for s, (lo, hi) in SOURCE_LIMIT_BAND.items():
        ph["android_%s_within_%s_to_%s_d" % (s, lo, hi)] = band("android", s, lo, hi)
    ph["ios_interactionc_166_to_170_d"] = band("ios", "interactionc", 166, 170)
    ph["ios_knowledgec_gt_365_d"] = band("ios", "knowledgec", 365.0001, 1e9)
    # which knowledgeC stream sets the oldest record (report Section 5.7)
    deep = [r["deep_knowledgec"] for r in ok if r["kind"] == "ios" and r.get("deep_knowledgec", {}).get("streams")]
    if deep:
        ph["knowledgec_oldest_stream_is_signals"] = [sum(1 for d in deep
                                                         if d.get("oldest_stream_name") == "/discoverability/signals"),
                                                     len(deep)]
        sh = sorted(d["share_older_than_30_days"] for d in deep if d.get("share_older_than_30_days") is not None)
        if sh:
            ph["knowledgec_share_records_older_30d_median_min_max"] = [sh[len(sh) // 2], sh[0], sh[-1]]
    # bug-report logs (report Section 5.4)
    br = [r for r in ok if r["kind"] == "bugreport" and "logcat_system" in r["stores"]]
    if br:
        syst = [r["stores"]["logcat_system"] for r in br]
        ph["bugreport_head_strays_system"] = sorted(s["head_strays"] for s in syst)
        ph["bugreport_reports_with_head_strays"] = [sum(1 for s in syst if s["head_strays"]), len(syst)]
        ph["bugreport_system_body_ge_1d"] = [sum(1 for s in syst if s["horizon_d"] >= 1), len(syst)]
        ph["bugreport_system_oldest_line_ge_1d"] = [sum(1 for s in syst if s["oldest_line_horizon_d"] >= 1), len(syst)]
        ph["bugreport_oldest_over_body_ratio"] = sorted(round(s["oldest_line_horizon_d"] / s["horizon_d"])
                                                        for s in syst if s["head_strays"] and s["horizon_d"] > 0)
        grids = [s["body_grid"] for s in syst]
        ph["bugreport_body_stable_to_2pct"] = [sum(1 for g in grids if g["same_up_to_2pct"]), len(grids)]
        ph["bugreport_body_changes_on_grid"] = [sum(1 for g in grids if g["same_as_default"] < g["pairs"]), len(grids)]
        lines = sorted(s["n_records"] for s in syst)
        ph["bugreport_system_lines_min_median_max"] = [lines[0], lines[len(lines) // 2], lines[-1]]
        if len(syst) >= stats.MIN_CELL:
            ph["bugreport_spearman_lines_vs_body_horizon"] = round(
                spearman([s["n_records"] for s in syst], [s["horizon_d"] for s in syst]), 3)
    # devices with every store under one day
    ph["ios_devices_every_store_under_1d"] = sum(1 for r in ok if r["kind"] == "ios" and r["stores"] and all(
        s.get("horizon_d", 0) < 1 for s in r["stores"].values() if "horizon_d" in s))
    # interactionC read without its log
    d = {"nowal_older": 0, "wal_older": 0, "same": 0}
    diffs = []
    for r in ok:
        s = r["stores"].get("interactionc", {})
        if s.get("nowal_horizon_d") is not None and s.get("horizon_d") is not None:
            diff = s["nowal_horizon_d"] - s["horizon_d"]
            diffs.append(diff)
            d["nowal_older" if diff > 1e-6 else "wal_older" if diff < -1e-6 else "same"] += 1
    ph["interactionc_wal_direction"] = d
    if diffs:
        diffs.sort()
        ph["interactionc_nowal_minus_wal_d_min_median_max"] = [round(diffs[0], 2), round(diffs[len(diffs) // 2], 2),
                                                               round(diffs[-1], 2)]


# ---------------------------------------------------------------- markdown tables
def _row(c):
    if c.get("suppressed"):
        return None
    return ("| %s | %d | %s [%s, %s] | %s to %s | %s to %s | %d | %d [%d%%, %d%%] |" % (
        c["store_label"], c["n"], _f(c["median_d"]), _f(c["ci_lo"]), _f(c["ci_hi"]), _f(c["q1"]), _f(c["q3"]),
        _f(c["min"]), _f(c["max"]), c["ge7d"][0], c["ge30d"][0], round(100 * c["ge30d"][3]), round(100 * c["ge30d"][4])))


def _f(v):
    return "<0.01" if v < 0.005 else ("%.2f" % v if v < 1 else "%.1f" % v)


def _table(cells, title):
    out = ["", "### " + title, "", "| Store | n | Median [95% CI] | Q1 to Q3 | Min to max | >=7 d | >=30 d [CI] |",
           "|---|---|---|---|---|---|---|"]
    for c in cells:
        c = dict(c, store_label=stores.LABELS.get(c["store"], c["store"]))
        r = _row(c)
        if r:
            out.append(r)
    return out


def report_markdown(rep, heading):
    L = [heading, "", "Invented or measured data as given to the runner; aggregates only. Days = acquisition minus the "
         "oldest retained record (bug-report logs: start of the body).", ""]
    L += ["## Sample (Table 3 layout)", "", "| Class | Extractions | Devices | Time source | Clock-checked |",
          "|---|---|---|---|---|"]
    for short, smp in rep["sample"].items():
        src = ", ".join("%s %d" % (k, v) for k, v in sorted(smp["tacq_src"].items()))
        L.append("| %s | %d | %d | %s | %d |" % (KIND_LABEL[short], smp["extractions"], smp["devices"], src,
                                                   smp["clock_checked"]))
    L += ["", "## Prevalence: extractions that hold a dated record, of those readable", ""]
    for short, v in rep["prevalence"].items():
        L.append("- %s: %s" % (KIND_LABEL[short], ", ".join("%s %d/%d" % (stores.LABELS[s], a, b)
                                                           for s, (a, b) in v.items())))
    for short in ("ios", "android", "bugreport"):
        cs = [c for c in rep["cells"] if c["platform"] == short and c["cell"].endswith("|all")]
        if cs:
            L += _table(cs, {"ios": "iOS horizons in days (Table 4 layout)",
                             "android": "Android horizons in days (Table 5 layout)",
                             "bugreport": "Bug-report horizons in days (Table 5 layout)"}[short])
    st = [c for c in rep["strata"] if not c.get("suppressed")]
    L += ["", "## Strata of at least five devices (Table 6 layout)", "", "| Stratum | Store | n | Median | Q1 to Q3 | Min to max |",
          "|---|---|---|---|---|---|"]
    for c in st:
        L.append("| %s | %s | %d | %s | %s to %s | %s to %s |" % (c["cell"].split("|")[0] + " " + c["cell"].split("|")[2],
                                                           stores.LABELS.get(c["store"], c["store"]), c["n"],
                                                           _f(c["median_d"]), _f(c["q1"]), _f(c["q3"]), _f(c["min"]),
                                                           _f(c["max"])))
    L += ["", "## Reach of 30 days: at least one store (clock-checked devices; k, n, share, Wilson 95%)", "",
          "```", _j(rep["reach30"]), "```", "", "## Consistency and clock checks (Table 7 layout; k of n)", "", "```",
          _j(rep["checks"]), "```", "", "## Clock", "", "```", _j(rep["clock"]), "```", "",
          "## Sensitivity (first percentile, newest lag, in-focus stream, oldest line)", "", "```",
          _j({k: v for k, v in rep["sensitivity"].items() if not v.get("suppressed")}), "```", "",
          "## Correlations", "", "```", _j(rep["correlations"]), "```", "", "## Post hoc counts", "", "```",
          _j(rep["posthoc"]), "```", "", "## Errors", "", "```", _j(rep["errors"]), "```", ""]
    return "\n".join(L)


def _j(x):
    return json.dumps(x, indent=1, sort_keys=True)
