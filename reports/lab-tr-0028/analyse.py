"""Analysis of LAB-TR-0028 on reader output (Sections 3.3, 5.1 to 5.6 and 5.8).

Input: the list of dictionaries that readers.py returns (Android archives, bug reports, iOS archives),
optionally with an "id" per item. Output: a dictionary of aggregates from which Tables 4 to 8 and the data
of Figures 2 and 3 are taken. Only counts, shares and day offsets are produced. Standard library only.
"""
import datetime
import statistics

import fixtures

DAY = 86400.0
HOUR = 3600.0
MIN_OK = datetime.datetime(2009, 1, 1, tzinfo=datetime.timezone.utc).timestamp()  # dates before are not dates
IR_RESTORE, IR_SETUP, IR_USER = 2, 3, 4  # PackageManager.INSTALL_REASON_DEVICE_RESTORE / _DEVICE_SETUP / _USER
MEDIA_IMAGE, MEDIA_VIDEO = 1, 3


def med(xs):
    return statistics.median(xs) if xs else None


def rnd(x, n=1):
    return None if x is None else round(x, n)


def spread(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "median": rnd(med(xs)), "min": rnd(min(xs)), "max": rnd(max(xs))}


def _ok_ms(v):
    return v is not None and v / 1000.0 > MIN_OK


def device_view(raw):
    """Derive the indicator times (epoch seconds) of one Android item.

    W first boot record; S first media index; Pw oldest password time; Ad first account add; Pn first
    install of a non-system package after W; Rr, Rs earliest install with reason restore / setup;
    U the earliest of the four upper bounds (Ad, Pw, Pn, Rr, Rs).
    """
    d = {"id": raw.get("id")}
    w = raw.get("W")
    W = w if (w and w > MIN_OK) else None
    d["W"] = W
    added = [x for x in raw["media"]["added_s"] if x and x > MIN_OK]
    d["S"] = min(added) if added else None
    pw = [x / 1000.0 for x in raw["acc_pw_ms"] if x and x / 1000.0 > MIN_OK]
    d["Pw"] = min(pw) if pw else None
    adds = [x for x in raw["acc_add_s"] if x]
    d["Ad"] = min(adds) if adds else None
    pk = raw["packages"]
    nonsys = [p for p in pk if not p["system"]]
    fits = [p["fit_ms"] / 1000.0 for p in nonsys if _ok_ms(p["fit_ms"])]
    d["n_nonsys"] = len(nonsys)
    d["n_nonsys_with_fit"] = len(fits)
    if W:
        after = [t for t in fits if t >= W - HOUR]
        d["Pn"] = min(after) if after else None
        d["nonsys_before_W"] = sum(1 for t in fits if t < W - HOUR)
    else:
        d["Pn"] = min(fits) if fits else None
        d["nonsys_before_W"] = None
    d["ir_known"] = raw["restrictions_present"]
    d["ir"] = [p["ir"] or 0 for p in nonsys]
    rr = [p["fit_ms"] / 1000.0 for p in pk if p["ir"] == IR_RESTORE and _ok_ms(p["fit_ms"])]
    rs = [p["fit_ms"] / 1000.0 for p in pk if p["ir"] == IR_SETUP and _ok_ms(p["fit_ms"])]
    d["Rr"], d["Rs"] = (min(rr) if rr else None), (min(rs) if rs else None)
    d["n_ir2"], d["n_ir3"] = len(rr), len(rs)
    d["ir_recorded"] = any(p["ir"] in (IR_RESTORE, IR_SETUP, IR_USER) for p in nonsys)
    anc = raw.get("ancestral")
    d["anc_nonzero"] = None if not anc else bool(anc["ancestral_nonzero"])
    d["ist"] = raw.get("setup_ts_s")
    d["setup_flags"] = tuple(raw.get("setup_flags", (None, None)))
    d["user_created"] = raw.get("user_created")
    usage = raw.get("usage_daily_s", [])
    d["usage_oldest"] = min(usage) if usage else None
    s = raw["sms"]
    rows = [(i, t, m) for i, t, m in zip(s["id"], s["date_ms"], s["tool"]) if t and t / 1000.0 > MIN_OK]
    d["sms_id"] = [i for i, _, _ in rows]
    d["sms"] = [t / 1000.0 for _, t, _ in rows]
    d["tool"] = [bool(m) for _, _, m in rows]
    c = raw["calls"]
    crow = [(i, t) for i, t in zip(c["id"], c["date_ms"]) if t and t / 1000.0 > MIN_OK]
    d["calls_id"] = [i for i, _ in crow]
    d["calls"] = [t / 1000.0 for _, t in crow]
    m = raw["media"]
    d["media"] = list(zip(m["added_s"], m["taken_ms"], m["type"]))
    cands = [d[k] for k in ("Ad", "Pw", "Pn", "Rr", "Rs") if d.get(k)]
    if W:
        cands = [x for x in cands if x >= W - HOUR]
    d["U"] = min(cands) if cands else None
    return d


def _shares(ts, W, U):
    a = sum(1 for t in ts if t < W - HOUR)
    b = sum(1 for t in ts if U and W - HOUR <= t < U)
    return {"n": len(ts), "pre_W": a, "between": b, "after": len(ts) - a - b}


def _runs(ids, ts, limit):
    order = sorted(range(len(ids)), key=lambda k: ids[k])
    flags = [ts[k] < limit for k in order]
    n_pre = sum(flags)
    if not n_pre:
        return None
    runs, cur = [], 0
    for f in flags:
        if f:
            cur += 1
        elif cur:
            runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    pre = [ts[k] for k, f in zip(order, flags) if f]
    asc = sum(1 for a, b in zip(pre, pre[1:]) if b >= a)
    first_post = next((k for k, f in enumerate(flags) if not f), None)
    last_pre = max(k for k, f in enumerate(flags) if f)
    return {"n_pre": n_pre, "runs": len(runs),
            "asc_share": (asc / (len(pre) - 1)) if len(pre) > 1 else None,
            "prefix": first_post is None or last_pre < first_post}


def analyse_android(raws):
    devs = [device_view(r) for r in raws]
    R = {"n": len(devs)}
    prev = {
        "first_boot_record": sum(1 for d in devs if d["W"]),
        "first_media_index": sum(1 for d in devs if d["S"]),
        "account_add_log": sum(1 for d in devs if d["Ad"]),
        "account_password_time": sum(1 for d in devs if d["Pw"]),
        "first_user_install_after_W": sum(1 for d in devs if d["n_nonsys_with_fit"] and d["Pn"]),
        "install_reasons_recorded": sum(1 for d in devs if d["ir_recorded"]),
        "reason_restore_any": sum(1 for d in devs if d["n_ir2"]),
        "reason_setup_any": sum(1 for d in devs if d["n_ir3"]),
        "both_setup_flags_set": sum(1 for d in devs if d["setup_flags"] == ("1", "1")),
        "backup_record_readable": sum(1 for d in devs if d["anc_nonzero"] is not None),
        "backup_token_nonzero": sum(1 for d in devs if d["anc_nonzero"]),
        "setup_timestamp_file": sum(1 for d in devs if d["ist"]),
        "oldest_usage_file_reaches_W": sum(1 for d in devs if d["usage_oldest"] and d["W"] and d["usage_oldest"] <= d["W"] + DAY),
        "user_creation_time_nonzero": sum(1 for d in devs if d["user_created"] not in (None, "0")),
    }
    tool_dev = [i for i, d in enumerate(devs) if any(d["tool"])]
    prev["messages_by_migration_tool"] = len(tool_dev)
    prev["devices_with_messages"] = sum(1 for d in devs if d["sms"])
    R["prevalence"] = prev

    def offsets(key):
        return [(d[key] - d["W"]) / DAY for d in devs if d.get(key) and d["W"]]
    R["offsets"] = {}
    for k in ("S", "Ad", "Pw", "Pn", "Rr", "Rs", "ist", "U"):
        o = offsets(k)
        s = spread(o)
        s["le1d"] = sum(1 for x in o if x <= 1)
        s["gt30d"] = sum(1 for x in o if x > 30)
        R["offsets"][k] = s
    gap = [(d["U"] - d["W"]) / DAY for d in devs if d["U"] and d["W"]]
    R["gap_WU"] = dict(spread(gap), le1d=sum(1 for g in gap if g <= 1), at_least_30d=sum(1 for g in gap if g >= 30),
                       at_least_100d=sum(1 for g in gap if g >= 100), values=sorted(round(g, 1) for g in gap))
    # agreement of the user-setup traces with one another
    pairs = {}

    def get(d, k):
        if k == "Rx":
            c = [x for x in (d.get("Rr"), d.get("Rs")) if x]
            return min(c) if c else None
        return d.get(k)
    for a_, b_ in (("Pw", "Pn"), ("Pw", "Rx"), ("Pw", "Ad")):
        diffs = []
        for d in devs:
            x, y = get(d, a_), get(d, b_)
            if x and y and (not d["W"] or (x >= d["W"] - HOUR and y >= d["W"] - HOUR)):
                diffs.append(abs(x - y) / DAY)
        pairs["%s-%s" % (a_, b_)] = {"both": len(diffs), "within_1d": sum(1 for z in diffs if z <= 1)}
    R["pairs_user_group"] = pairs
    # records before the boundaries (Table 6)
    rec = {}
    for name in ("sms", "calls"):
        rows_ = []
        for d in devs:
            if d[name] and d["W"]:
                s = _shares(d[name], d["W"], d["U"])
                rows_.append(s)
        tot = sum(r["n"] for r in rows_)
        pre = sum(r["pre_W"] for r in rows_)
        sh = [r["pre_W"] / r["n"] for r in rows_]
        rec[name] = {"devices": len(rows_), "total": tot, "pre_W": pre, "between": sum(r["between"] for r in rows_),
                     "devices_with_pre": sum(1 for r in rows_ if r["pre_W"] > 0),
                     "devices_majority_pre": sum(1 for x in sh if x > 0.5),
                     "median_pct": rnd(100 * med(sh)) if sh else None, "min_pct": rnd(100 * min(sh)) if sh else None,
                     "max_pct": rnd(100 * max(sh)) if sh else None, "pooled_pct": rnd(100 * pre / tot) if tot else None,
                     "shares": sh}
    mrows = []
    for d in devs:
        if not d["W"] or not d["media"]:
            continue
        items = [(a, b) for a, b, m in d["media"] if m in (MEDIA_IMAGE, MEDIA_VIDEO) and b and b / 1000.0 > MIN_OK and a and a > MIN_OK]
        if not items:
            continue
        mrows.append({"n": len(items), "pre_W": sum(1 for a, b in items if b / 1000.0 < d["W"] - HOUR),
                      "late": sum(1 for a, b in items if b / 1000.0 >= d["W"] - HOUR and a - b / 1000.0 > 7 * DAY)})
    tot, pre = sum(r["n"] for r in mrows), sum(r["pre_W"] for r in mrows)
    sh = [r["pre_W"] / r["n"] for r in mrows]
    rec["media"] = {"devices": len(mrows), "total": tot, "pre_W": pre,
                    "devices_with_pre": sum(1 for r in mrows if r["pre_W"]),
                    "devices_majority_pre": sum(1 for x in sh if x > 0.5),
                    "median_pct": rnd(100 * med(sh)) if sh else None, "min_pct": rnd(100 * min(sh)) if sh else None,
                    "max_pct": rnd(100 * max(sh)) if sh else None, "pooled_pct": rnd(100 * pre / tot) if tot else None,
                    "late_total": sum(r["late"] for r in mrows), "shares": sh}
    arow = []
    for d in devs:
        if d["ir_known"] and d["n_nonsys"]:
            arow.append({"n": len(d["ir"]), "restore": sum(1 for x in d["ir"] if x == IR_RESTORE),
                         "setup": sum(1 for x in d["ir"] if x == IR_SETUP), "user": sum(1 for x in d["ir"] if x == IR_USER),
                         "none": sum(1 for x in d["ir"] if x == 0)})
    tot, r2 = sum(r["n"] for r in arow), sum(r["restore"] for r in arow)
    sh = [r["restore"] / r["n"] for r in arow if r["n"]]
    rec["apps"] = {"devices": len(arow), "total": tot, "restore": r2, "setup": sum(r["setup"] for r in arow),
                   "user": sum(r["user"] for r in arow), "none": sum(r["none"] for r in arow),
                   "devices_restore": sum(1 for r in arow if r["restore"]),
                   "median_pct": rnd(100 * med(sh)) if sh else None, "max_pct": rnd(100 * max(sh)) if sh else None,
                   "min_pct": rnd(100 * min(sh)) if sh else None, "pooled_pct": rnd(100 * r2 / tot) if tot else None,
                   "shares": sh}
    R["records"] = rec
    # restore signals (Table 7)
    sig = []
    for d in devs:
        W = d["W"]
        pre_s = bool(W and any(t < W - HOUR for t in d["sms"]))
        pre_c = bool(W and any(t < W - HOUR for t in d["calls"]))
        pre_m = bool(W and any(m in (MEDIA_IMAGE, MEDIA_VIDEO) and b and MIN_OK < b / 1000.0 < W - HOUR for a, b, m in d["media"]))
        sig.append({"restored_apps": bool(d["n_ir2"]), "token": bool(d["anc_nonzero"]), "tool": any(d["tool"]),
                    "before_W": pre_s or pre_c or pre_m})
    R["restore_signals"] = {
        "restored_apps": sum(s["restored_apps"] for s in sig), "token_nonzero": sum(s["token"] for s in sig),
        "tool_messages": sum(s["tool"] for s in sig), "records_before_W": sum(s["before_W"] for s in sig),
        "at_least_one": sum(1 for s in sig if any(s.values())), "none": sum(1 for s in sig if not any(s.values())),
        "restored_and_before_W": sum(1 for s in sig if s["restored_apps"] and s["before_W"]),
        "restored_no_before_W": sum(1 for s in sig if s["restored_apps"] and not s["before_W"]),
        "before_W_no_restored": sum(1 for s in sig if s["before_W"] and not s["restored_apps"])}
    # rules against the creator field (Table 8), devices with tool-written messages pooled
    tot = {"tool": 0, "other": 0, "rules": {}}
    for name in ("R1_W", "R1_U", "R2", "R3_U", "R4_U"):
        tot["rules"][name] = {"tool_flagged": 0, "other_flagged": 0}
    for i in tool_dev:
        d = devs[i]
        if not d["W"] or not d["U"]:
            continue
        rows_ = [(k, int(t * 1000)) for k, t in zip(d["sms_id"], d["sms"])]
        truth = {k: ("tool" if m else "other") for (k, _), m in zip(rows_, d["tool"])}
        r1w = fixtures.rule_boundary(rows_, d["W"] * 1000.0 / fixtures.DAY_MS)
        r1u = fixtures.rule_boundary(rows_, d["U"] * 1000.0 / fixtures.DAY_MS)
        r2 = fixtures.rule_order(rows_)
        r3u = r1u | r2
        r4u = fixtures.rule_hull(r3u, rows_)
        tot["tool"] += sum(d["tool"])
        tot["other"] += len(d["tool"]) - sum(d["tool"])
        for name, fl in (("R1_W", r1w), ("R1_U", r1u), ("R2", r2), ("R3_U", r3u), ("R4_U", r4u)):
            tot["rules"][name]["tool_flagged"] += sum(1 for k in fl if truth[k] == "tool")
            tot["rules"][name]["other_flagged"] += sum(1 for k in fl if truth[k] == "other")
    for v in tot["rules"].values():
        v["recall_pct"] = rnd(100.0 * v["tool_flagged"] / tot["tool"], 2) if tot["tool"] else None
    R["rules_vs_creator"] = tot
    # how restored batches are written (Section 5.6)
    struct_ = []
    order_native = {"stores": 0, "records": 0, "flagged": 0}
    for d in devs:
        W = d["W"]
        if not W:
            continue
        for ids, ts in ((d["sms_id"], d["sms"]), (d["calls_id"], d["calls"])):
            if not ts:
                continue
            ri = _runs(ids, ts, W - HOUR)
            if ri:
                struct_.append(ri)
            else:
                rows_ = [(k, int(t * 1000)) for k, t in zip(ids, ts)]
                order_native["stores"] += 1
                order_native["records"] += len(rows_)
                order_native["flagged"] += len(fixtures.rule_order(rows_))
    R["structure"] = {
        "device_stores": len(struct_),
        "ascending": sum(1 for s in struct_ if s["asc_share"] is not None and s["asc_share"] >= 0.9),
        "descending": sum(1 for s in struct_ if s["asc_share"] is not None and s["asc_share"] <= 0.1),
        "one_run": sum(1 for s in struct_ if s["runs"] == 1), "several_runs": sum(1 for s in struct_ if s["runs"] > 1),
        "all_before_later": sum(1 for s in struct_ if s["prefix"])}
    R["order_rule_where_no_record_before_W"] = order_native
    return R


def analyse_bugreports(raws):
    out = {"n": len(raws), "with_install_reasons": 0, "restore_counts": [], "restore_window_days": [], "tokens_zero": 0}
    for r in raws:
        ns = [p for p in r["packages"] if not p["system"]]
        if any(p["ir"] is not None for p in ns):
            out["with_install_reasons"] += 1
        ir2 = [p["fit"] for p in ns if p["ir"] == IR_RESTORE and p["fit"]]
        out["restore_counts"].append(len(ir2))
        out["restore_window_days"].append(rnd((max(ir2) - min(ir2)) / DAY) if ir2 else None)
        if r["ancestral_token"] in ("0", "0x0"):
            out["tokens_zero"] += 1
    return out


def analyse_ios(raws):
    rows = []
    for r in raws:
        marks = r["marker_task_s"] + r["marker_lock_s"]
        M = min(marks) if marks else None
        row = {"has_marker": M is not None}
        for key in ("sms_s", "calls_s", "photos_s"):
            ts = [t for t in r[key] if t and t > 1.2e9]
            row[key + "_n"] = len(ts)
            row[key + "_pre"] = sum(1 for t in ts if t < M - HOUR) if M is not None else None
        rows.append(row)
    mk = [r for r in rows if r["has_marker"]]
    out = {"n": len(rows), "with_marker": len(mk)}
    for key, label in (("sms_s", "messages"), ("calls_s", "calls"), ("photos_s", "photos")):
        have = [r for r in mk if r[key + "_n"]]
        sh = [r[key + "_pre"] / r[key + "_n"] for r in have]
        out[label] = {"devices": len(have), "some_before_M": sum(1 for r in have if r[key + "_pre"]),
                      "majority_before_M": sum(1 for x in sh if x > 0.5),
                      "median_pct": rnd(100 * med(sh)) if sh else None,
                      "min_pct": rnd(100 * min(sh)) if sh else None, "max_pct": rnd(100 * max(sh)) if sh else None}
    return out


def analyse(android, bugreports, ios):
    """android, bugreports, ios: lists of reader dictionaries."""
    R = {"android": analyse_android(android) if android else None,
         "bugreports": analyse_bugreports(bugreports) if bugreports else None,
         "ios": analyse_ios(ios) if ios else None}
    return R
