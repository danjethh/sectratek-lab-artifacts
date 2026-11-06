"""Statistics used by the report (standard library only).

median_ci   distribution-free interval for the median from order statistics (achieved coverage is returned)
wilson      Wilson score interval for a proportion
quart       quartiles by linear interpolation
spearman    rank correlation with mid-ranks
cell        the summary of one stratum of horizons: n, median and interval, quartiles, range, shares reaching 1/7/30 days
"""
import math


def binom_cdf(k, n):
    """P(X <= k) for X ~ Binomial(n, 1/2)."""
    return sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n


def median_ci(xs):
    """Return (median, lower, upper, achieved coverage) with the widest-needed order statistics for >= 95%."""
    xs = sorted(xs)
    n = len(xs)
    med = (xs[(n - 1) // 2] + xs[n // 2]) / 2
    lo = 0
    for j in range(1, n // 2 + 1):
        if binom_cdf(j - 1, n) <= 0.025:
            lo = j
    if lo == 0:
        return med, xs[0], xs[-1], 1 - 2 * 0.5 ** n
    return med, xs[lo - 1], xs[n - lo], 1 - 2 * binom_cdf(lo - 1, n)


def achieved_coverage(n):
    """Coverage of the interval median_ci uses for a sample of n values."""
    return median_ci(list(range(n)))[3]


def quart(xs):
    xs = sorted(xs)

    def q(p):
        k = (len(xs) - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        return xs[f] + (xs[c] - xs[f]) * (k - f)
    return q(0.25), q(0.75)


def wilson(k, n, z=1.96):
    """Return (p, lower, upper) or None when n is 0."""
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def _ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = _ranks(a), _ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


MIN_CELL = 5


def cell(xs, name):
    """Summary of a list of horizons in days. A cell of fewer than MIN_CELL devices is suppressed."""
    n = len(xs)
    if n < MIN_CELL:
        return {"cell": name, "n": n, "suppressed": True}
    med, lo, hi, cov = median_ci(xs)
    q1, q3 = quart(xs)
    c = {"cell": name, "n": n, "median_d": round(med, 2), "ci_lo": round(lo, 2), "ci_hi": round(hi, 2),
         "ci_cov": round(cov, 3), "q1": round(q1, 2), "q3": round(q3, 2), "min": round(min(xs), 2),
         "max": round(max(xs), 2)}
    for thr in (1, 7, 30):
        k = sum(1 for x in xs if x >= thr)
        p, a, b = wilson(k, n)
        c["ge%dd" % thr] = [k, n, round(p, 3), round(a, 3), round(b, 3)]
    return c
