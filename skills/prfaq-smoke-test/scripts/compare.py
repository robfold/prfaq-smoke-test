#!/usr/bin/env python3
"""Size and read a landing-page smoke test. Standard library only.

Before launch, size the test:
  compare.py plan --base 0.03 --target 0.06 [--variants 3] [--alpha 0.05]
                  [--power 0.8] [--cpc 0.80]

After the test, compare variants from a CSV:
  compare.py results.csv [--metric signups] [--min-visitors 400]
                         [--min-rate 0.04] [--alpha 0.05]

The CSV needs a header row with `variant`, `visitors`, and the metric column
(default `signups`). A `spend` column, if present, adds cost per conversion.
Visitors are unique visitor ids that fired `view`, not raw page loads.
"""

import argparse
import csv
import math
import sys
from itertools import combinations
from statistics import NormalDist

Z = NormalDist()


def wilson(successes, n, alpha):
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    z = Z.inv_cdf(1 - alpha / 2)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def two_prop_p(x1, n1, x2, n2):
    """Two-sided p-value of a pooled two-proportion z-test."""
    pooled = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    if se == 0:
        return 1.0
    z = (x1 / n1 - x2 / n2) / se
    return 2 * (1 - Z.cdf(abs(z)))


def plan(argv):
    ap = argparse.ArgumentParser(prog="compare.py plan", description="Visitors needed per variant.")
    ap.add_argument("--base", type=float, required=True, help="expected rate of the weaker variant, e.g. 0.03")
    ap.add_argument("--target", type=float, required=True, help="rate you need to tell apart from base, e.g. 0.06")
    ap.add_argument("--variants", type=int, default=3)
    ap.add_argument("--alpha", type=float, default=0.05, help="family-wise, split across all pairs")
    ap.add_argument("--power", type=float, default=0.8)
    ap.add_argument("--cpc", type=float, help="expected cost per visitor, to estimate budget")
    a = ap.parse_args(argv)

    if not (0 < a.base < 1 and 0 < a.target < 1) or a.base == a.target:
        sys.exit("error: --base and --target must be different rates between 0 and 1")
    if a.variants < 2:
        sys.exit("error: --variants must be at least 2")

    pairs = a.variants * (a.variants - 1) // 2
    alpha_pair = a.alpha / pairs
    z_a = Z.inv_cdf(1 - alpha_pair / 2)
    z_b = Z.inv_cdf(a.power)
    p1, p2 = a.base, a.target
    pbar = (p1 + p2) / 2
    num = z_a * math.sqrt(2 * pbar * (1 - pbar)) + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    n = math.ceil(num * num / (p1 - p2) ** 2)

    print(f"To tell {p1:.1%} from {p2:.1%} with {a.power:.0%} power")
    print(f"(alpha {a.alpha} split over {pairs} pairs = {alpha_pair:.4f} per pair):")
    print(f"  visitors per variant: {n}")
    print(f"  visitors in total:    {n * a.variants}")
    if a.cpc:
        print(f"  budget at {a.cpc} per visitor: {n * a.variants * a.cpc:,.2f} in total, {n * a.cpc:,.2f} per variant")
    print("A smaller budget can only detect a bigger gap. Rerun with a larger --target to see what it can detect.")


def compare(argv):
    ap = argparse.ArgumentParser(prog="compare.py", description="Compare smoke-test variants.")
    ap.add_argument("csv")
    ap.add_argument("--metric", default="signups", help="conversion column, e.g. signups or cta_clicks")
    ap.add_argument("--min-visitors", type=int, default=0, help="from test-plan.md; below it the test is UNDECIDED")
    ap.add_argument("--min-rate", type=float, help="from test-plan.md; the bar a winner must clear")
    ap.add_argument("--alpha", type=float, default=0.05, help="family-wise, split across all pairs")
    a = ap.parse_args(argv)

    with open(a.csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 2:
        sys.exit("error: need at least two variant rows")
    for col in ("variant", "visitors", a.metric):
        if col not in rows[0]:
            sys.exit(f"error: missing column '{col}' (have: {', '.join(rows[0])})")
    names = [r["variant"].strip() for r in rows]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        sys.exit(f"error: variant listed more than once: {', '.join(dupes)} (sum each variant into one row)")

    variants = []
    for r in rows:
        n, x = int(r["visitors"]), int(r[a.metric])
        if n < 0 or x < 0 or x > n:
            sys.exit(f"error: variant {r['variant']}: {a.metric}={x} must be between 0 and visitors={n}")
        spend = float(r["spend"]) if r.get("spend") not in (None, "") else None
        variants.append({"name": r["variant"], "n": n, "x": x, "spend": spend})

    pairs = list(combinations(range(len(variants)), 2))
    alpha_pair = a.alpha / len(pairs)

    print(f"metric: {a.metric} per visitor, 95% Wilson interval")
    print(f"{'variant':<10}{'visitors':>9}{a.metric:>12}{'rate':>8}   {'interval':<17}{'cost/conv':>10}")
    for v in variants:
        rate = v["x"] / v["n"] if v["n"] else float("nan")
        lo, hi = wilson(v["x"], v["n"], 0.05)
        cost = f"{v['spend'] / v['x']:,.2f}" if v["spend"] is not None and v["x"] else "-"
        v["rate"] = rate
        print(f"{v['name']:<10}{v['n']:>9}{v['x']:>12}{rate:>8.2%}   {lo:>6.2%} – {hi:<6.2%}  {cost:>10}")

    print(f"\npairwise two-proportion z-tests, alpha {a.alpha} split over {len(pairs)} pairs = {alpha_pair:.4f} each")
    beats = {i: set() for i in range(len(variants))}
    for i, j in pairs:
        vi, vj = variants[i], variants[j]
        if vi["n"] == 0 or vj["n"] == 0:
            print(f"  {vi['name']} vs {vj['name']}: no visitors, skipped")
            continue
        p = two_prop_p(vi["x"], vi["n"], vj["x"], vj["n"])
        sig = p < alpha_pair
        if sig:
            hi_i, lo_i = (i, j) if vi["rate"] > vj["rate"] else (j, i)
            beats[hi_i].add(lo_i)
        print(f"  {vi['name']} vs {vj['name']}: p = {p:.4f} {'(different)' if sig else '(not distinguishable)'}")

    short = [v["name"] for v in variants if v["n"] < a.min_visitors or v["n"] == 0]
    leader_i = max(range(len(variants)), key=lambda k: (variants[k]["rate"] if variants[k]["n"] else -1))
    leader = variants[leader_i]

    if short:
        verdict = f"UNDECIDED: {', '.join(short)} below {a.min_visitors} visitors"
    elif a.min_rate is not None and leader["rate"] < a.min_rate:
        verdict = f"BELOW_BAR: best variant {leader['name']} at {leader['rate']:.2%} is under the bar {a.min_rate:.2%}"
    elif len(beats[leader_i]) == len(variants) - 1:
        verdict = f"WINNER: {leader['name']} at {leader['rate']:.2%} beats every other variant"
    else:
        tied = [leader["name"]] + [variants[k]["name"] for k in range(len(variants))
                                    if k != leader_i and k not in beats[leader_i]]
        verdict = f"TIE: {', '.join(tied)} cannot be told apart at this sample size"
    print(f"\nverdict: {verdict}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "plan":
        plan(args[1:])
    elif args and args[0] not in ("-h", "--help"):
        compare(args)
    else:
        print(__doc__)
