"""SVG figures of the report, written with the standard library.

fig1_pipeline()        report Figure 1, the measurement pipeline
fig2_horizons(rows)    report Figure 2, box plot of horizons on a log axis; rows from fig2_rows()
fig3_reach(rows)       report Figure 3, share of devices whose store reaches back 30 days; rows from fig3_rows()
Rows are built either from the values printed in report Tables 4 and 5 (data/paper_tables_4_5.json) or from the
cells of a runner report.
"""
import math
from xml.sax.saxutils import escape

STYLE = ("<style>text{font:8px sans-serif;fill:#1a1a1a}.m{fill:#555}.mid{text-anchor:middle}.end{text-anchor:end}"
         ".b{font-weight:bold}.grid{stroke:#ddd;stroke-width:.6}.ink{stroke:#222;fill:none;stroke-width:.8}"
         ".box{fill:#cfe3f5;stroke:#222;stroke-width:.8}.med{stroke:#c33;stroke-width:1.6}.lim{stroke:#c60;fill:none;"
         "stroke-width:1}.bar{fill:#2a6fb0}.dash{stroke-dasharray:3 2;stroke:#222;stroke-width:.6}"
         ".panel{fill:#f4f4f4;stroke:#555;stroke-width:.8}.panela{fill:#fbe9d0;stroke:#555;stroke-width:.8}"
         ".arrow{stroke:#222;fill:none;stroke-width:.9}.head{fill:#222}</style>")


def _open(w, h, tid, title, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" role="img" '
            'aria-labelledby="%s-t %s-d">%s<title id="%s-t">%s</title><desc id="%s-d">%s</desc>'
            '<rect width="100%%" height="100%%" fill="#fff"/>' % (w, h, 2 * w, tid, tid, STYLE, tid, escape(title), tid,
                                                              escape(desc)))


# ---------------------------------------------------------------- rows
FIG2_ORDER = [
    ("iOS", "Unified log, Persist", "ul_persist", None), ("iOS", "Powerlog archives", "powerlog_archives", None),
    ("iOS", "Unified log, Signpost", "ul_signpost", None), ("iOS", "Unified log, Special", "ul_special", None),
    ("iOS", "knowledgeC, others", "knowledgec_other", None), ("iOS", "Biome App.InFocus", "biome_appinfocus", None),
    ("iOS", "knowledgeC, all", "knowledgec", None), ("iOS", "interactionC", "interactionc", None),
    ("Android", "Notification history", "notif_history", 1), ("Android", "DropBox entries", "dropbox", 3),
    ("Android", "Process stats", "procstats", None), ("Android", "Usage stats, daily", "usage_daily", 10),
    ("Android", "Battery hist. (vendor)", "vendor_battery_hist", None), ("Android", "Network stats", "netstats", 90),
    ("Android", "Usage stats, any", "usage_any", None),
    ("Bug report", "Event log", "logcat_events", None), ("Bug report", "System log", "logcat_system", None),
]
FIG3_ORDER = [
    ("iOS", "Unified log, Persist", "ul_persist"), ("iOS", "Powerlog archives", "powerlog_archives"),
    ("iOS", "Unified log, Special", "ul_special"), ("iOS", "knowledgeC, others", "knowledgec_other"),
    ("iOS", "Biome App.InFocus", "biome_appinfocus"), ("iOS", "interactionC", "interactionc"),
    ("Android", "Usage stats, daily", "usage_daily"), ("Android", "DropBox entries", "dropbox"),
    ("Android", "Battery hist. (vendor)", "vendor_battery_hist"), ("Android", "Network stats", "netstats"),
    ("Bug report", "System log", "logcat_system"),
]
_PLAT = {"iOS": "ios", "Android": "android", "Bug report": "bugreport"}


def rows_from_cells(cells):
    """Build the figure rows from the cells of a runner report ({cell name: cell})."""
    by = {c["cell"]: c for c in cells}
    r2, r3 = [], []
    for g, lab, key, lim in FIG2_ORDER:
        c = by.get("%s|%s|all" % (_PLAT[g], key))
        if c and not c.get("suppressed"):
            r2.append({"group": g, "label": lab, "n": c["n"], "median": c["median_d"], "q1": c["q1"], "q3": c["q3"],
                       "min": c["min"], "max": c["max"], "limit": lim})
    for g, lab, key in FIG3_ORDER:
        c = by.get("%s|%s|all" % (_PLAT[g], key))
        if c and not c.get("suppressed"):
            k, n, p, a, b = c["ge30d"]
            r3.append({"group": g, "label": lab, "k": k, "n": n, "p": p, "lo": a, "hi": b})
    return r2, r3


# ---------------------------------------------------------------- Figure 1
def fig1_pipeline():
    boxes = [
        (8, 12, 98, 44, ["1 Archive index", "read-only scan,", "fixed store list"]),
        (121, 12, 98, 44, ["2 Date each store", "header, file name", "or SQL column"]),
        (234, 12, 98, 44, ["3 Acquisition time", "extraction record", "or container time"]),
        (62, 92, 98, 48, ["4 Clock rule", "newest record in", "[-72 h, +1 h]"]),
        (178, 92, 98, 48, ["5 Horizon and cells", "n >= 5 devices,", "intervals"]),
    ]
    desc = ("Five steps. 1 Read the archive central directory and keep only the members of the fixed store list. "
            "2 Date each store by its own field. 3 Take the acquisition time from the extraction record, or the "
            "container file time. 4 Clock rule: keep a device only if its newest record lies between 72 hours "
            "before and 1 hour after acquisition. 5 Horizon per store and device, then cells of at least five devices.")
    o = [_open(340, 150, "f1", "Measurement pipeline", desc)]
    for i, (bx, by, bw, bh, lines) in enumerate(boxes):
        o.append('<rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="3"/>' % ("panela" if i == 3 else "panel",
                                                                                   bx, by, bw, bh))
        for j, t in enumerate(lines):
            o.append('<text class="mid%s" x="%d" y="%d">%s</text>' % (" b" if j == 0 else "", bx + bw // 2,
                                                                      by + 15 + j * 12, escape(t)))
    o.append('<line class="arrow" x1="106" y1="34" x2="116" y2="34"/><line class="arrow" x1="219" y1="34" x2="229" y2="34"/>')
    o.append('<line class="arrow" x1="160" y1="116" x2="173" y2="116"/>')
    o.append('<path class="arrow" d="M 283 56 L 283 74 L 111 74 L 111 86"/>')
    for d in ("M 121 34 L 115 31 L 115 37 Z", "M 234 34 L 228 31 L 228 37 Z", "M 178 116 L 172 113 L 172 119 Z",
              "M 111 92 L 108 86 L 114 86 Z"):
        o.append('<path class="head" d="%s"/>' % d)
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- Figure 2
LO, HI = 0.01, 1000.0
X0, X1 = 146.0, 320.0


def _x(v):
    v = min(max(v, LO), HI)
    return X0 + (math.log10(v) - math.log10(LO)) / (math.log10(HI) - math.log10(LO)) * (X1 - X0)


def _fmt(v):
    if v < 0.01:
        return "under 0.01"
    if v < 1:
        return "%.2f" % v
    if v < 100:
        return "%.1f" % v
    return "%.0f" % v


def fig2_horizons(rows):
    rh, top, gap = 13.0, 38.0, 9.0
    ys, y, prev = [], top, None
    for r in rows:
        if prev is not None and r["group"] != prev:
            y += gap
        ys.append(y)
        y += rh
        prev = r["group"]
    bottom = y + 4
    H = bottom + 30
    desc = "; ".join("%s %s: n %d, median %s, quartiles %s to %s, range %s to %s days%s" % (
        r["group"], r["label"], r["n"], _fmt(r["median"]), _fmt(r["q1"]), _fmt(r["q3"]), _fmt(r["min"]),
        _fmt(r["max"]), ("; source limit %s days" % r["limit"]) if r.get("limit") else "") for r in rows)
    o = [_open(340, int(H), "f2", "Retention horizon per store, days before acquisition, log scale",
               "Box plot on a logarithmic axis from 0.01 to 1,000 days, one row per store. " + desc + ".")]
    o.append('<rect class="box" x="120" y="6" width="14" height="7"/><line class="med" x1="127" y1="5" x2="127" y2="14"/>'
             '<text x="138" y="13">quartiles, median</text>')
    o.append('<line class="ink" x1="232" y1="9.5" x2="246" y2="9.5"/><text x="249" y="13">range</text>')
    o.append('<path class="lim" d="M 289 5.5 L 293 9.5 L 289 13.5 L 285 9.5 Z"/><text x="296" y="13">limit</text>')
    for v, t in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100"), (1000, "1,000")):
        o.append('<line class="grid" x1="%.1f" y1="%.0f" x2="%.1f" y2="%.0f"/>' % (_x(v), top - 6, _x(v), bottom))
        o.append('<text class="m mid" x="%.1f" y="%.0f">%s</text>' % (_x(v), bottom + 11, t))
    for v in (7, 30):
        o.append('<line class="dash" x1="%.1f" y1="%.0f" x2="%.1f" y2="%.0f"/>' % (_x(v), top - 6, _x(v), bottom))
        o.append('<text class="m mid" x="%.1f" y="%.0f">%d d</text>' % (_x(v), top - 8, v))
    o.append('<text class="m mid" x="%.0f" y="%.0f">days before acquisition (log scale)</text>' % ((X0 + X1) / 2, bottom + 24))
    prev = None
    for r, yy in zip(rows, ys):
        cy = yy + rh / 2
        if r["group"] != prev:
            o.append('<text class="b" x="4" y="%.1f">%s</text>' % (yy - 1.5, escape(r["group"])))
            prev = r["group"]
        o.append('<text x="10" y="%.1f">%s</text>' % (cy + 3.5, escape(r["label"])))
        o.append('<text class="m end" x="%.0f" y="%.1f">%d</text>' % (X0 - 3, cy + 3.5, r["n"]))
        o.append('<line class="ink" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (_x(r["min"]), cy, _x(r["max"]), cy))
        bx0, bx1 = _x(r["q1"]), _x(r["q3"])
        o.append('<rect class="box" x="%.1f" y="%.1f" width="%.1f" height="8"/>' % (bx0, cy - 4, max(bx1 - bx0, 1.2)))
        o.append('<line class="med" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (_x(r["median"]), cy - 5,
                                                                                   _x(r["median"]), cy + 5))
        if r.get("limit"):
            dx = _x(r["limit"])
            o.append('<path class="lim" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z"/>' % (
                dx, cy - 4.5, dx + 4, cy, dx, cy + 4.5, dx - 4, cy))
    o.append('<text class="m end" x="%.0f" y="%.0f">n</text>' % (X0 - 3, top - 8))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- Figure 3
def fig3_reach(rows):
    x0, x1 = 140.0, 296.0

    def xb(p):
        return x0 + p * (x1 - x0)
    rh, top = 14.0, 22.0
    ys, y, prev = [], top, None
    for r in rows:
        if prev is not None and r["group"] != prev:
            y += 8
        ys.append(y)
        y += rh
        prev = r["group"]
    bottom = y + 2
    H = bottom + 28
    desc = "; ".join("%s %s: %d of %d (%d percent; interval %d to %d)" % (
        r["group"], r["label"], r["k"], r["n"], round(r["p"] * 100), round(r["lo"] * 100), round(r["hi"] * 100))
        for r in rows)
    o = [_open(340, int(H), "f3", "Share of devices whose store reaches back 30 days, with Wilson 95 percent intervals",
               "Horizontal bars, 0 to 100 percent. " + desc + ".")]
    for p in (0, 0.25, 0.5, 0.75, 1.0):
        o.append('<line class="grid" x1="%.1f" y1="%.0f" x2="%.1f" y2="%.0f"/>' % (xb(p), top - 4, xb(p), bottom))
        o.append('<text class="m mid" x="%.1f" y="%.0f">%d</text>' % (xb(p), bottom + 11, int(p * 100)))
    o.append('<text class="m mid" x="%.0f" y="%.0f">percent of clock-checked devices reaching 30 days</text>' % (
        (x0 + x1) / 2, bottom + 23))
    prev = None
    for r, yy in zip(rows, ys):
        cy = yy + rh / 2
        if r["group"] != prev:
            o.append('<text class="b" x="4" y="%.1f">%s</text>' % (yy - 1, escape(r["group"])))
            prev = r["group"]
        o.append('<text x="10" y="%.1f">%s</text>' % (cy + 3.5, escape(r["label"])))
        if r["p"] > 0:
            o.append('<rect class="bar" x="%.1f" y="%.1f" width="%.1f" height="8"/>' % (x0, cy - 4, xb(r["p"]) - x0))
        o.append('<line class="ink" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (xb(r["lo"]), cy, xb(r["hi"]), cy))
        for e in (r["lo"], r["hi"]):
            o.append('<line class="ink" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (xb(e), cy - 3, xb(e), cy + 3))
        o.append('<text x="%.0f" y="%.1f">%d/%d</text>' % (x1 + 6, cy + 3.5, r["k"], r["n"]))
    o.append("</svg>")
    return "".join(o)
