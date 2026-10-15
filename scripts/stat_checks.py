#!/usr/bin/env python3
"""Small, auditable consistency checks for numbers reported in a manuscript.

Use these to VERIFY a suspected numerical problem before writing a comment. A comment
that says "reported P = 0.012 does not match F(3,20) = 2.91 (recomputed P = 0.059)" is
verifiable; "the statistics look wrong" is not. A failed check means the reported numbers
are mutually inconsistent, not which one is wrong - ask the authors.

Subcommands
  pct      percent change:  pct --old 4.82 --new 5.71 --reported 23
  pvalue   recompute P from a test statistic (rounding-aware, statcheck-style):
           pvalue --test F --stat 2.91 --df1 3 --df2 20 --reported 0.012
           pvalue --test t --stat 2.10 --df1 38 --reported "<0.05" [--one-tailed]
           tests: t, F, chi2, z, r   (for r pass --df1 = n-2)
  grim     can a mean of integer data (n, optional items/scale points) have this value?
           grim --mean 3.47 --n 25 [--items 1]
  df       expected error df for a balanced design:
           df --design crd --t 4 --r 6 [--reported 20]
           designs: crd (t,r) | rcbd (t,b) | latin (t) | splitplot (a,b,r)
  ci       is a reported confidence interval consistent with mean, SD, n?
           ci --mean 5.7 --sd 0.6 --n 6 --lo 5.1 --hi 6.3 [--level 0.95]
Exit status: 0 consistent, 1 inconsistent, 2 usage problem.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from decimal import ROUND_HALF_UP, Decimal


def _decimals(s: str) -> int:
    s = s.strip().lstrip("<>=~ ").replace("−", "-")
    return len(s.split(".")[1]) if "." in s else 0


def _round_half_up(x: float, d: int) -> float:
    q = Decimal(1).scaleb(-d)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


def p_from_stat(test: str, stat: float, df1: float | None, df2: float | None,
                one_tailed: bool = False) -> float:
    from scipy import stats
    test = test.lower()
    if test == "t":
        p = stats.t.sf(abs(stat), df1)
        p = p if one_tailed else 2 * p
    elif test == "z":
        p = stats.norm.sf(abs(stat))
        p = p if one_tailed else 2 * p
    elif test == "f":
        p = stats.f.sf(stat, df1, df2)
    elif test in ("chi2", "x2", "chisq"):
        p = stats.chi2.sf(stat, df1)
    elif test == "r":
        t = stat * math.sqrt(df1 / max(1e-12, 1 - stat * stat))
        p = stats.t.sf(abs(t), df1)
        p = p if one_tailed else 2 * p
    else:
        raise ValueError(f"unknown test {test!r}")
    return float(p)


def check_pvalue(test, stat_str, df1, df2, reported, one_tailed=False):
    """Return (consistent, p_central, (p_low, p_high), message)."""
    stat = float(stat_str)
    d = _decimals(stat_str)
    half = 0.5 * 10 ** (-d)
    ps = [p_from_stat(test, stat + s, df1, df2, one_tailed) for s in (-half, 0, half)]
    p_lo, p_hi, p_c = min(ps), max(ps), ps[1]
    rep = reported.strip().replace(" ", "")
    m = re.match(r"^(<=|>=|<|>|=)?(\d*\.?\d+(?:[eE]-?\d+)?)$", rep)
    if not m:
        raise ValueError(f"cannot parse reported P {reported!r}")
    op, val = (m.group(1) or "="), float(m.group(2))
    if op in ("<", "<="):
        ok = p_lo < val or (op == "<=" and p_lo <= val)
    elif op in (">", ">="):
        ok = p_hi > val or (op == ">=" and p_hi >= val)
    else:
        dec = _decimals(m.group(2))
        lo_r, hi_r = _round_half_up(p_lo, dec), _round_half_up(p_hi, dec)
        ok = min(lo_r, hi_r) - 1e-12 <= val <= max(lo_r, hi_r) + 1e-12
    g = lambda v: f"{v:g}"
    msg = (f"{test.upper() if test.lower() in ('f',) else test.lower()}={stat_str}" +
           (f", df=({g(df1)},{g(df2)})" if df2 is not None
            else f", df={g(df1)}" if df1 is not None else "") +
           f": recomputed P = {p_c:.4g} (range {p_lo:.4g}-{p_hi:.4g} given rounding of the "
           f"statistic); reported P {reported} -> " + ("consistent" if ok else "INCONSISTENT"))
    # decision-level flag: does significance at 0.05 flip?
    if not ok and m:
        flips = (p_c < 0.05) != (val < 0.05 if op in ("=", "<", "<=") else val >= 0.05)
        if flips:
            msg += " (the conclusion at alpha = 0.05 would change)"
    return ok, p_c, (p_lo, p_hi), msg


def grim(mean: float, n: int, decimals: int, items: int = 1) -> tuple[bool, list[float]]:
    """GRIM test (Brown & Heathers 2017): is mean attainable from integer data?"""
    total_n = n * items
    target = Decimal(repr(mean))
    cands = []
    approx = int(round(mean * total_n))
    for s in range(approx - 2, approx + 3):
        m = _round_half_up(s / total_n, decimals)
        cands.append(m)
        if Decimal(repr(m)) == target.quantize(Decimal(1).scaleb(-decimals)):
            return True, cands
    return False, cands


def expected_df(design: str, **k) -> dict:
    d = design.lower()
    if d == "crd":
        t, r = k["t"], k["r"]
        return {"treatment": t - 1, "error": t * (r - 1), "total": t * r - 1}
    if d == "rcbd":
        t, b = k["t"], k["r"]
        return {"treatment": t - 1, "block": b - 1, "error": (t - 1) * (b - 1),
                "total": t * b - 1}
    if d == "latin":
        t = k["t"]
        return {"treatment": t - 1, "error": (t - 1) * (t - 2), "total": t * t - 1}
    if d == "splitplot":
        a, b, r = k["a"], k["b"], k["r"]
        return {"whole_plot_factor": a - 1, "whole_plot_error": (a - 1) * (r - 1),
                "subplot_factor": b - 1, "interaction": (a - 1) * (b - 1),
                "subplot_error": a * (b - 1) * (r - 1), "total": a * b * r - 1}
    raise ValueError("design must be crd, rcbd, latin or splitplot")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pct")
    p.add_argument("--old", type=float, required=True)
    p.add_argument("--new", type=float, required=True)
    p.add_argument("--reported", type=float, required=True)
    p.add_argument("--tol", type=float, default=0.6, help="tolerance in percentage points")
    q = sub.add_parser("pvalue")
    q.add_argument("--test", required=True)
    q.add_argument("--stat", required=True, help="as printed, e.g. 2.91 (decimals matter)")
    q.add_argument("--df1", type=float)
    q.add_argument("--df2", type=float)
    q.add_argument("--reported", required=True)
    q.add_argument("--one-tailed", action="store_true")
    g = sub.add_parser("grim")
    g.add_argument("--mean", required=True)
    g.add_argument("--n", type=int, required=True)
    g.add_argument("--items", type=int, default=1)
    f = sub.add_parser("df")
    f.add_argument("--design", required=True)
    for k in ("t", "r", "a", "b"):
        f.add_argument(f"--{k}", type=int)
    f.add_argument("--reported", type=int, help="reported error df")
    c = sub.add_parser("ci")
    c.add_argument("--mean", type=float, required=True)
    c.add_argument("--sd", type=float, required=True)
    c.add_argument("--n", type=int, required=True)
    c.add_argument("--lo", type=float, required=True)
    c.add_argument("--hi", type=float, required=True)
    c.add_argument("--level", type=float, default=0.95)
    a = ap.parse_args()
    try:
        if a.cmd == "pct":
            calc = (a.new - a.old) / a.old * 100
            ok = abs(calc - a.reported) <= a.tol
            print(f"({a.new} - {a.old}) / {a.old} = {calc:.2f}%; reported {a.reported}% -> "
                  + ("consistent" if ok else "INCONSISTENT"))
            return 0 if ok else 1
        if a.cmd == "pvalue":
            ok, _, _, msg = check_pvalue(a.test, a.stat, a.df1, a.df2, a.reported, a.one_tailed)
            print(msg)
            return 0 if ok else 1
        if a.cmd == "grim":
            ok, cands = grim(float(a.mean), a.n, _decimals(a.mean), a.items)
            print(f"mean {a.mean}, n={a.n}" + (f", items={a.items}" if a.items > 1 else "")
                  + (": attainable with integer data" if ok else
                     f": NOT attainable with integer data (nearest attainable means: "
                     f"{sorted(set(cands))})"))
            return 0 if ok else 1
        if a.cmd == "df":
            e = expected_df(a.design, t=a.t, r=a.r, a=a.a, b=a.b)
            print("expected df:", e)
            if a.reported is not None:
                key = "error" if "error" in e else "subplot_error"
                ok = e[key] == a.reported
                print(f"reported error df {a.reported} vs expected {e[key]} -> "
                      + ("consistent" if ok else "INCONSISTENT (check the experimental unit "
                         "and whether repeated measures were treated as independent)"))
                return 0 if ok else 1
            return 0
        if a.cmd == "ci":
            from scipy import stats
            se = a.sd / math.sqrt(a.n)
            tcrit = stats.t.ppf(0.5 + a.level / 2, a.n - 1)
            lo, hi = a.mean - tcrit * se, a.mean + tcrit * se
            half_rep = (a.hi - a.lo) / 2
            print(f"t-based {a.level:.0%} CI from mean/SD/n: {lo:.3f} to {hi:.3f}; reported "
                  f"{a.lo} to {a.hi}")
            if abs(lo - a.lo) < 0.06 * (hi - lo) and abs(hi - a.hi) < 0.06 * (hi - lo):
                print("-> consistent")
                return 0
            hints = []
            if abs(half_rep - a.sd) < 0.1 * a.sd:
                hints.append("the interval half-width is about one SD (SD used as if it were a CI?)")
            if abs(half_rep - se) < 0.1 * se:
                hints.append("half-width is about one SE (SE used as if it were a CI?)")
            if abs(half_rep - 1.96 * se) < 0.05 * 1.96 * se and a.n < 30:
                hints.append("normal (1.96) rather than t critical value was used")
            print("-> INCONSISTENT" + (": " + "; ".join(hints) if hints else ""))
            return 1
    except (ValueError, TypeError, KeyError) as e:
        print("usage problem:", e, file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
