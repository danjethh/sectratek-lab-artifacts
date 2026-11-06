"""Text tables for LAB-TR-0028: Table 9 and the boundary-error statements (fixtures), and Tables 4 to 8 with
the record-structure and bug-report and iOS summaries (from analyse.analyse). Standard library only."""
import fixtures


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def csv_text(header, rows):
    return "\n".join(",".join('"%s"' % str(c) if "," in str(c) else str(c) for c in r) for r in [header] + rows) + "\n"


def table9(results):
    header = ["Scenario", "R1", "R2", "R3", "R4"]
    return header, fixtures.table9(results)


def boundary_errors(results):
    return ["Statement", "Percent"], [[k, "%.1f" % v] for k, v in fixtures.boundary_error_rows(results)]


def _rng(s, nd=1):
    return "-" if not s.get("n") else "%s to %s" % (s["min"], s["max"])


def pipeline_report(A, B, I, banner):
    """Markdown of Tables 4 to 8 and the summaries of Sections 5.6 and 5.8 from an analysis dictionary."""
    L = [banner, ""]
    if A:
        p, n = A["prevalence"], A["n"]
        L += ["## Table 4 (prevalence of the traces; devices of %d)" % n, "",
              md_table(["Trace", "Devices"], [
                  ["First boot record (W)", p["first_boot_record"]], ["First media index", p["first_media_index"]],
                  ["Account add log", p["account_add_log"]], ["Account password time", p["account_password_time"]],
                  ["First user install after W", p["first_user_install_after_W"]],
                  ["Install reasons recorded", p["install_reasons_recorded"]],
                  ["  reason restore on at least one non-system app", p["reason_restore_any"]],
                  ["  reason setup on at least one non-system app", p["reason_setup_any"]],
                  ["Both setup flags set", p["both_setup_flags_set"]],
                  ["Backup record readable / token non-zero", "%d / %d" % (p["backup_record_readable"], p["backup_token_nonzero"])],
                  ["Setup timestamp file", p["setup_timestamp_file"]],
                  ["Messages written by a migration tool (of %d with messages)" % p["devices_with_messages"], p["messages_by_migration_tool"]],
                  ["Oldest usage file reaches W", p["oldest_usage_file_reaches_W"]],
                  ["System user creation time non-zero", p["user_creation_time_nonzero"]]]), ""]
        names = [("S", "First media index"), ("Ad", "Account add log"), ("Pw", "Account password time"),
                 ("Pn", "First user install"), ("Rr", "Earliest restore install"), ("Rs", "Earliest setup install"),
                 ("ist", "Setup timestamp file"), ("U", "U (earliest of four bounds)")]
        rows = []
        for k, lab in names:
            s = A["offsets"][k]
            rows.append([lab, s["n"], s.get("median", "-"), _rng(s), s.get("le1d", "-"), s.get("gt30d", "-")])
        g = A["gap_WU"]
        L += ["## Table 5 (offset from W, days)", "",
              md_table(["Trace", "Devices", "Median", "Range", "<= 1 day", "> 30 days"], rows), "",
              "Gap W to U: median %s, range %s; at least 30 days on %d, at least 100 days on %d, within a day on %d (of %d)."
              % (g.get("median"), _rng(g), g["at_least_30d"], g["at_least_100d"], g["le1d"], g["n"]), ""]
        rec = A["records"]
        rows = []
        for key, lab in (("sms", "Messages"), ("calls", "Calls"), ("media", "Media capture"), ("apps", "Restored apps")):
            r = rec[key]
            some = r["devices_with_pre"] if key != "apps" else r["devices_restore"]
            maj = r.get("devices_majority_pre", "-")
            rows.append([lab, r["devices"], some, maj, r["median_pct"], "%s to %s" % (r["min_pct"], r["max_pct"]), r["pooled_pct"]])
        L += ["## Table 6 (share of records dated before W, percent)", "",
              md_table(["Store", "Devices", "Some", "Majority", "Median %", "Range %", "Pooled %"], rows), ""]
        s = A["restore_signals"]
        L += ["## Table 7 (restore signals)", "",
              md_table(["Restore evidence", "Devices"], [
                  ["Apps installed with reason restore", s["restored_apps"]], ["Backup record, non-zero token", s["token_nonzero"]],
                  ["Messages written by a migration tool", s["tool_messages"]], ["Records before W", s["records_before_W"]],
                  ["At least one of the four", s["at_least_one"]], ["None of the four", s["none"]]]), ""]
        v = A["rules_vs_creator"]
        L += ["## Table 8 (rules against the creator field; %d tool-written, %d other messages)" % (v["tool"], v["other"]), "",
              md_table(["Rule", "Tool-written flagged", "Recall %", "Other flagged"],
                       [[k.replace("_", ", B = "), x["tool_flagged"], x["recall_pct"], x["other_flagged"]] for k, x in v["rules"].items()]), ""]
        st = A["structure"]
        L += ["## Section 5.6 (how restored batches are written)", "",
              "Device-stores with records before W: %(device_stores)d; ascending %(ascending)d, descending %(descending)d; "
              "one run of identifiers %(one_run)d, several runs %(several_runs)d; all before every later record %(all_before_later)d." % st,
              "Order rule on stores with no record before W: %(flagged)d flagged of %(records)d records in %(stores)d stores."
              % A["order_rule_where_no_record_before_W"], ""]
    if B:
        L += ["## Section 5.8, bug reports", "",
              "Reports %(n)d; with install reasons %(with_install_reasons)d; restored installs per report %(restore_counts)s; "
              "restore window in days %(restore_window_days)s; backup token zero in %(tokens_zero)d." % B, ""]
    if I:
        L += ["## Section 5.8, iOS probe", "", "Archives %(n)d; with a marker %(with_marker)d." % I, "",
              md_table(["Store", "Devices", "Some before M", "Majority before M", "Median %", "Range %"],
                       [[k, I[k]["devices"], I[k]["some_before_M"], I[k]["majority_before_M"], I[k]["median_pct"],
                         "%s to %s" % (I[k]["min_pct"], I[k]["max_pct"])] for k in ("messages", "calls", "photos")]), ""]
    return "\n".join(L)
