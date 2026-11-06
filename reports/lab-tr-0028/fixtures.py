"""Fixture generator and labelling rules of LAB-TR-0028 (Section 3.4, Section 3.5, Table 9).

A fixture is a real SQLite table built the way the Android message and call providers build theirs:
an INTEGER PRIMARY KEY AUTOINCREMENT identifier and a writer-supplied integer date in milliseconds.
Records are inserted in the order a scenario says they were written. Native records arrive as a Poisson
process (3 per day for 180 days after the first boot); a restored batch of 1,500 records is written in one
burst at the restore time R, with creation dates spread over the 365 days before R (or, for a gradual
sync, 50 chunks written over 14 days between native writes). The rules see only (identifier, date); the
labels are kept outside the table.

Time unit of the scenario parameters: days from the first boot record W (W = 0).
Standard library only.
"""
import math
import random
import sqlite3

DAY_MS = 86400000

# name -> g: days from W to the restore R (None: no restore); order: insertion order of the batch;
#         d0: age in days of the newest record in the batch at the restore; clock_step: days (see below)
SCENARIOS = {
    "S1 at setup, ascending": dict(g=0.02, order="asc", d0=0.0),
    "S2 at setup, descending": dict(g=0.02, order="desc", d0=0.0),
    "S3 at setup, by thread": dict(g=0.02, order="thread", d0=0.0),
    "S4 at setup, random": dict(g=0.02, order="random", d0=0.0),
    "S5 day 3, ascending": dict(g=3.0, order="asc", d0=1.0),
    "S6 day 30, ascending": dict(g=30.0, order="asc", d0=1.0),
    "S7 day 30, by thread": dict(g=30.0, order="thread", d0=1.0),
    "S11 gradual sync, 14 days": dict(g=0.02, order="chunks", d0=0.0),
    "S8 no restore": dict(g=None, order=None, d0=0.0),
    "S9 no restore, clock step": dict(g=None, order=None, d0=0.0, clock_step=-2.0),
    "S10 setup, ascending, clock step": dict(g=0.02, order="asc", d0=0.0, clock_step=-2.0),
}
# scenarios without a restore: recall is undefined
NO_RESTORE = ("S8 no restore", "S9 no restore, clock step")
# the clock is stepped back by clock_step days (two days) for ten days, starting at a random day
CLOCK_STEP_LEN_DAYS = 10.0

LIFE_DAYS = 180.0
NATIVE_RATE = 3.0
BATCH_SIZE = 1500
HISTORY_DAYS = 365.0
THREADS = 60
GRADUAL_CHUNKS = 50
GRADUAL_DAYS = 14.0
ORDER_DELTA_DAYS = 0.5  # R2: more than 12 hours below the highest earlier date
# Boundary errors in days (positive = boundary placed too late). Table 9 uses the exact boundary (0) in
# every scenario; the three statements of Section 5.7 use the extra errors below for two scenarios.
EXTRA_BOUNDARY_ERRORS = {
    "S8 no restore": (3.0, 14.0, -3.0),
    "S1 at setup, ascending": (-3.0,),
}
DEFAULT_SEED = 2810
DEFAULT_REPS = 200


def build(params, rng):
    """Return (rows, truth): rows = [(id, date_ms)] in identifier order; truth[id] = 'restored' | 'native'."""
    g, order, d0 = params["g"], params["order"], params["d0"]
    t = 0.0
    native = []
    while True:
        t += rng.expovariate(NATIVE_RATE)
        if t >= LIFE_DAYS:
            break
        native.append(t)
    step = params.get("clock_step")
    step_at = rng.uniform(20, LIFE_DAYS - 20) if step else None
    events = []  # (write time, kind, payload)
    for x in native:
        d = x
        if step_at is not None and step_at <= x < step_at + CLOCK_STEP_LEN_DAYS:
            d = x + step
        events.append((x, "n", d))
    if g is not None:
        restore = g
        n = BATCH_SIZE
        times = sorted(rng.uniform(restore - HISTORY_DAYS, restore - d0) for _ in range(n))
        thread = [rng.randrange(THREADS) for _ in times]
        idx = list(range(n))
        if order == "desc":
            idx.reverse()
        elif order == "thread":
            idx.sort(key=lambda i: (thread[i], times[i]))
        elif order == "random":
            rng.shuffle(idx)
        if order == "chunks":
            size = n // GRADUAL_CHUNKS
            chunks = [times[k * size:(k + 1) * size] for k in range(GRADUAL_CHUNKS)]
            rng.shuffle(chunks)
            for k, chunk in enumerate(chunks):
                events.append((restore + (k + 1) * (GRADUAL_DAYS / GRADUAL_CHUNKS), "r", chunk))
        else:
            events.append((restore, "r", [times[i] for i in idx]))
    events.sort(key=lambda e: e[0])
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE msgs (_id INTEGER PRIMARY KEY AUTOINCREMENT, date INTEGER)")
    truth = {}
    next_id = 0
    for _, kind, payload in events:
        dates = [payload] if kind == "n" else payload
        con.executemany("INSERT INTO msgs(date) VALUES (?)", [(int(x * DAY_MS),) for x in dates])
        label = "native" if kind == "n" else "restored"
        for _x in dates:
            next_id += 1
            truth[next_id] = label
    rows = con.execute("SELECT _id, date FROM msgs ORDER BY _id").fetchall()
    con.close()
    return rows, truth


# ---------------------------------------------------------------- rules (see only _id and date)
def rule_boundary(rows, boundary_days):
    """R1: restored if dated before the boundary (days from W)."""
    limit = boundary_days * DAY_MS
    return {i for i, d in rows if d < limit}


def rule_order(rows, delta_days=ORDER_DELTA_DAYS):
    """R2: restored if dated more than delta below the highest date among records with lower identifiers."""
    out = set()
    highest = None
    delta = delta_days * DAY_MS
    for i, d in rows:
        if highest is not None and d < highest - delta:
            out.add(i)
        highest = d if highest is None else max(highest, d)
    return out


def rule_hull(flagged, rows):
    """Close a flagged set over the identifier interval it spans (a batch is written in one burst)."""
    if not flagged:
        return set()
    lo, hi = min(flagged), max(flagged)
    return {i for i, _ in rows if lo <= i <= hi}


RULES = {
    "R1": lambda rows, b: rule_boundary(rows, b),
    "R2": lambda rows, b: rule_order(rows),
    "R3": lambda rows, b: rule_boundary(rows, b) | rule_order(rows),
    "R4": lambda rows, b: rule_hull(rule_boundary(rows, b) | rule_order(rows), rows),
}


def score(flagged, truth):
    tp = sum(1 for i in flagged if truth[i] == "restored")
    fp = sum(1 for i in flagged if truth[i] == "native")
    n_restored = sum(1 for v in truth.values() if v == "restored")
    n_native = len(truth) - n_restored
    return tp, fp, n_restored, n_native


def run(seed=DEFAULT_SEED, reps=DEFAULT_REPS, extra_errors=EXTRA_BOUNDARY_ERRORS):
    """Return {(scenario, rule, boundary_error_days): (mean recall % or None, mean native flagged %)}.

    The fixture of repetition r of scenario s depends only on (seed, s, r), so one fixture is built
    once and every rule and every boundary error is evaluated on it.
    """
    acc = {}
    for si, (name, params) in enumerate(SCENARIOS.items()):
        errors = (0.0,) + tuple(extra_errors.get(name, ()))
        for be in errors:
            for rn in RULES:
                acc[(name, rn, be)] = ([], [])
        for rep in range(reps):
            rng = random.Random(seed * 1000 + si * 100 + rep)
            rows, truth = build(params, rng)
            for be in errors:
                for rn, rule in RULES.items():
                    tp, fp, n_r, n_n = score(rule(rows, be), truth)
                    rec, fpr = acc[(name, rn, be)]
                    if n_r:
                        rec.append(tp / n_r)
                    fpr.append(fp / n_n if n_n else 0.0)
    out = {}
    for k, (rec, fpr) in acc.items():
        out[k] = (100.0 * sum(rec) / len(rec) if rec else None, 100.0 * sum(fpr) / len(fpr))
    return out


def table9(results):
    """Rows of Table 9 (exact boundary): scenario, then 'recall / native flagged' per rule, percent."""
    rows = []
    for name in SCENARIOS:
        cells = []
        for rn in RULES:
            rec, fpr = results[(name, rn, 0.0)]
            cells.append(("-" if rec is None else "%.1f" % rec) + " / %.1f" % fpr)
        rows.append([name] + cells)
    return rows


def boundary_error_rows(results):
    """The three boundary-error statements of Section 5.7 (R1 native flagged / recall)."""
    return [
        ("S8 no restore, boundary +3 d (too late): native flagged %", results[("S8 no restore", "R1", 3.0)][1]),
        ("S8 no restore, boundary +14 d (too late): native flagged %", results[("S8 no restore", "R1", 14.0)][1]),
        ("S8 no restore, boundary -3 d (too early): native flagged %", results[("S8 no restore", "R1", -3.0)][1]),
        ("S1 at setup, ascending, boundary -3 d (too early): recall %", results[("S1 at setup, ascending", "R1", -3.0)][0]),
    ]


def _self_check():
    rows, truth = build(SCENARIOS["S1 at setup, ascending"], random.Random(1))
    assert [i for i, _ in rows] == list(range(1, len(rows) + 1))
    assert sum(1 for v in truth.values() if v == "restored") == BATCH_SIZE
    assert math.isfinite(len(rows))


if __name__ == "__main__":
    _self_check()
    res = run(reps=5)
    for r in table9(res):
        print(" | ".join(r))
