"""Hand-written SVG figures for LAB-TR-0028 (no plotting library).

fig1_timeline   Figure 1, the boundaries on a device timeline (a schematic, drawn from fixed positions)
fig2_gap        Figure 2, days from W to U per device, sorted (input: analysis["android"]["gap_WU"]["values"])
fig3_shares     Figure 3, share of records dated before W, one dot per device and store
fig4_recall     Figure 4, recall of R2 against R1 for the scenarios with a restore (input: fixtures.run result)
All functions return the SVG text. Standard library only.
"""
from xml.sax.saxutils import escape

INK, MUTED, ACCENT, WARN = "#1b1b1b", "#6b6b6b", "#1f5fbf", "#b55a00"
FONT = "font-family:sans-serif;font-size:9px"


def _doc(w, h, title, desc, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img">\n'
            '<title>%s</title><desc>%s</desc>\n<rect width="%d" height="%d" fill="#ffffff"/>\n%s\n</svg>\n'
            % (w, h, w * 2, h * 2, escape(title), escape(desc), w, h, "\n".join(body)))


def _t(x, y, s, anchor="start", color=INK, weight="normal"):
    return ('<text x="%.1f" y="%.1f" text-anchor="%s" fill="%s" font-weight="%s" style="%s">%s</text>'
            % (x, y, anchor, color, weight, FONT, escape(s)))


def _line(x1, y1, x2, y2, color=MUTED, width=0.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"%s/>' % (x1, y1, x2, y2, color, width, d)


def fig1_timeline():
    b = [_line(10, 118, 330, 118, INK, 1.0)]
    b.append(_t(12, 12, "Restored batch, written at R, creation dates kept"))
    for x, lab, l1, l2 in ((92, "W", "first boot", "record"), (168, "U", "first user", "setup"), (188, "R", "restore", "")):
        b.append(_line(x, 30, x, 124))
        b.append(_t(x, 26, lab, "middle", INK, "bold"))
        b.append(_t(x if lab != "R" else 214, 136, l1, "middle"))
        if l2:
            b.append(_t(x, 146, l2, "middle"))
    b.append(_t(310, 136, "acquisition", "middle"))
    b.append('<rect x="12" y="34" width="176" height="22" rx="2" fill="none" stroke="%s"/>' % INK)
    b.append(_t(50, 48, "dated before W", "middle"))
    b.append(_t(140, 48, "dated W to R", "middle"))
    b.append('<rect x="188" y="76" width="140" height="22" rx="2" fill="none" stroke="%s"/>' % ACCENT)
    b.append(_t(258, 90, "native records, device clock", "middle"))
    b.append(_t(12, 72, "Native records"))
    b.append(_t(12, 110, "earlier handset", color=MUTED))
    b.append(_t(100, 110, "this device", color=MUTED))
    return _doc(340, 150, "Boundaries on a device timeline",
                "A restored batch is written in one burst at R and keeps creation dates that begin before the first boot "
                "record W. W comes first on the device clock, the first evidence of user setup U later, then the restore R "
                "and native records until acquisition.", b)


def fig2_gap(values):
    vals = sorted(values)
    n = len(vals)
    top = max(vals + [1.0])
    x0, y0, x1, y1 = 40.0, 14.0, 330.0, 110.0
    b = [_line(x0, y1, x1, y1, INK, 1.0), _line(x0, y0, x0, y1, INK, 1.0)]
    for frac in (0.0, 0.5, 1.0):
        y = y1 - frac * (y1 - y0)
        b.append(_line(x0, y, x1, y, "#dddddd", 0.4))
        b.append(_t(x0 - 3, y + 3, "%d" % round(frac * top), "end", MUTED))
    w = (x1 - x0) / max(n, 1)
    for k, v in enumerate(vals):
        h = v / top * (y1 - y0)
        b.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (x0 + k * w + 1, y1 - h, max(w - 2, 1), h, ACCENT))
    b.append(_t((x0 + x1) / 2, 128, "devices, sorted by days from W to U", "middle", MUTED))
    b.append(_t(2, 10, "days"))
    return _doc(340, 134, "Days from the first boot record to user setup",
                "One bar per device, sorted by the number of days from W to U. Values: %s." % ", ".join("%.1f" % v for v in vals), b)


def fig3_shares(rec):
    """rec: analysis["android"]["records"]; one row per store, one dot per device (share in percent)."""
    rows = [("Messages", rec["sms"]["shares"]), ("Calls", rec["calls"]["shares"]),
            ("Media capture", rec["media"]["shares"]), ("Restored apps", rec["apps"]["shares"])]
    x0, x1 = 90.0, 325.0
    b = []
    for k, (lab, shares) in enumerate(rows):
        y = 24 + k * 26
        b.append(_t(4, y + 3, "%s (n %d)" % (lab, len(shares))))
        b.append(_line(x0, y, x1, y, "#dddddd", 0.6))
        for s in shares:
            b.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="%s" fill-opacity="0.7"/>' % (x0 + s * (x1 - x0), y, ACCENT))
    for frac in (0, 0.5, 1.0):
        b.append(_t(x0 + frac * (x1 - x0), 130, "%d%%" % round(100 * frac), "middle", MUTED))
    return _doc(340, 138, "Share of records dated before W",
                "One dot per device that holds the store, on a scale from 0 to 100 percent. Rows: "
                + "; ".join("%s: %s" % (lab, ", ".join("%.0f" % (100 * s) for s in sh)) for lab, sh in rows) + ".", b)


def fig4_recall(results, scenarios, no_restore):
    """results: fixtures.run(); recall of R2 (x) against R1 (y), exact boundary, scenarios with a restore."""
    x0, y0, x1, y1 = 40.0, 14.0, 300.0, 124.0
    b = [_line(x0, y1, x1, y1, INK, 1.0), _line(x0, y0, x0, y1, INK, 1.0)]
    for frac in (0.0, 0.5, 1.0):
        b.append(_t(x0 - 3, y1 - frac * (y1 - y0) + 3, "%d" % round(100 * frac), "end", MUTED))
        b.append(_t(x0 + frac * (x1 - x0), y1 + 11, "%d" % round(100 * frac), "middle", MUTED))
    pts = []
    for name in scenarios:
        if name in no_restore:
            continue
        r1, r2 = results[(name, "R1", 0.0)][0], results[(name, "R2", 0.0)][0]
        px, py = x0 + r2 / 100.0 * (x1 - x0), y1 - r1 / 100.0 * (y1 - y0)
        pts.append((name, r2, r1))
        b.append('<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s" fill-opacity="0.75"/>' % (px, py, ACCENT))
        b.append(_t(px + 4, py - 3, name.split(" ")[0], "start", MUTED))
    b.append(_t((x0 + x1) / 2, 148, "recall of R2, order rule (percent)", "middle", MUTED))
    b.append(_t(2, 10, "recall of R1 (percent)"))
    return _doc(340, 154, "Recall of the order rule against the boundary rule",
                "Each point is a scenario with a restore, exact boundary. " + "; ".join(
                    "%s: R2 %.1f, R1 %.1f" % p for p in pts) + ".", b)
