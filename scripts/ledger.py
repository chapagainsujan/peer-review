#!/usr/bin/env python3
"""Validate and render the review-comment ledger.

The ledger (JSON) is the single source of truth for review comments. The report,
the annotated DOCX/PDF and the CSV are all generated from it, so comments cannot
drift apart between deliverables.

    python ledger.py validate LEDGER.json --map MANUSCRIPT.map.json
    python ledger.py render   LEDGER.json --md out.md [--csv out.csv] [--audience author]

`validate` exits non-zero on errors. Its most important check: every quoted passage
must exist in the manuscript. A quote that cannot be found is either a typo or an
invented passage, and neither may reach the authors.

Ledger shape:
{
  "manuscript": "paper.docx",
  "comments": [
    {
      "id": "C-001",
      "severity": "Critical|Major|Minor|Optional",
      "status":   "confirmed|probable|question|suggestion",
      "category": "design|statistics|data|interpretation|literature|reproducibility|
                   integrity|reporting|writing|figures-tables|consistency",
      "audience": "author" (default) | "editor",
      "location": {"section": "...", "block": "P12" | "T1.r2c3" | "pg3",
                   "page": 3, "line": "12-14", "table": "Table 2", "figure": "Fig. 1",
                   "absent": false},
      "quote": "exact passage, kept short",
      "comment": "what is wrong or unclear",
      "rationale": "why it matters",
      "required_revision": "what the authors should do",
      "suggested_correction": "optional wording; use [placeholders] for unknown values",
      "evidence_needed": "data/diagnostic/citation that would resolve it"
    }
  ]
}
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

SEVERITIES = ["Critical", "Major", "Minor", "Optional"]
STATUSES = ["confirmed", "probable", "question", "suggestion"]
CATEGORIES = {"design", "statistics", "data", "interpretation", "literature",
              "reproducibility", "integrity", "reporting", "writing",
              "figures-tables", "consistency", "novelty", "ethics"}
ID_RE = re.compile(r"^C-\d{3,}$")


def norm(s: str) -> str:
    """Whitespace/typography-insensitive form used for matching quotes."""
    s = (s.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"')
          .replace("\u201d", '"').replace("\u00a0", " ").replace("\u2011", "-")
          .replace("\u2010", "-").replace("\u00ad", ""))
    s = re.sub(r"-\s*\n\s*", "", s)        # PDF end-of-line hyphenation
    return re.sub(r"\s+", " ", s).strip().lower()


def load_map_text(map_path: str | None) -> tuple[str, dict]:
    if not map_path:
        return "", {}
    m = json.loads(Path(map_path).read_text(encoding="utf-8"))
    by_id = {b["id"]: norm(b["text"]) for b in m["blocks"]}
    return norm(" ".join(b["text"] for b in m["blocks"])), by_id


def validate(ledger: dict, map_path: str | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    comments = ledger.get("comments")
    if not isinstance(comments, list) or not comments:
        return ["Ledger has no 'comments' list."], warns
    full, by_id = load_map_text(map_path)
    seen: set[str] = set()
    for c in comments:
        cid = c.get("id", "<missing id>")
        pre = f"{cid}: "
        if not ID_RE.match(str(cid)):
            errors.append(pre + "id must look like C-001")
        if cid in seen:
            errors.append(pre + "duplicate id")
        seen.add(cid)
        sev, st = c.get("severity"), c.get("status")
        if sev not in SEVERITIES:
            errors.append(pre + f"severity must be one of {SEVERITIES}, got {sev!r}")
        if st not in STATUSES:
            errors.append(pre + f"status must be one of {STATUSES}, got {st!r}")
        if c.get("category") not in CATEGORIES:
            warns.append(pre + f"unusual category {c.get('category')!r}")
        if c.get("audience", "author") not in ("author", "editor"):
            errors.append(pre + "audience must be 'author' or 'editor'")
        if not str(c.get("comment", "")).strip():
            errors.append(pre + "comment text is empty")
        loc = c.get("location") or {}
        if not isinstance(loc, dict) or not (loc.get("section") or loc.get("block")
                                             or loc.get("table") or loc.get("figure")
                                             or loc.get("absent")):
            errors.append(pre + "location needs at least a section, block, table/figure, or "
                                "absent=true")
        editor = c.get("audience", "author") == "editor"
        if sev in ("Critical", "Major") and not editor:   # editor notes are free-form
            for f in ("rationale", "required_revision"):
                if not str(c.get(f, "")).strip():
                    errors.append(pre + f"{sev} comments need '{f}'")
            if st in ("question", "suggestion"):
                warns.append(pre + f"{sev} severity but status '{st}': a concern that only needs "
                                   "author clarification is usually Minor or Major-question; "
                                   "check that severity matches the evidence.")
            if sev == "Critical" and st != "confirmed":
                warns.append(pre + "Critical but not 'confirmed': justify or downgrade.")
        # quote must exist -----------------------------------------------------
        q = str(c.get("quote", "")).strip()
        if not q and not editor and not (loc.get("absent") or loc.get("table")
                                         or loc.get("figure")):
            warns.append(pre + "no quote and not an absence/table/figure comment; the authors may "
                               "not be able to find the passage")
        if q and full:
            nq = norm(q)
            blk = loc.get("block")
            if blk and blk in by_id:
                ok = nq in by_id[blk]
                if not ok and nq in full:
                    warns.append(pre + f"quote exists but not in block {blk}; fix the block ID")
                elif not ok:
                    errors.append(pre + "quote NOT FOUND in the manuscript (possible typo or "
                                        "invented passage): " + q[:70])
            elif nq not in full:
                errors.append(pre + "quote NOT FOUND in the manuscript (possible typo or "
                                    "invented passage): " + q[:70])
            if len(q) > 400:
                warns.append(pre + "quote is long; quote only what is needed")
        # invented numbers in suggested wording ---------------------------------
        sug = str(c.get("suggested_correction", ""))
        if sug and full:
            ms_numbers = set(re.findall(r"\d+(?:\.\d+)?", full))   # whole numeric tokens only
            for num in set(re.findall(r"\d+(?:\.\d+)?", sug)):
                if num not in ms_numbers and "[" not in sug:
                    warns.append(pre + f"suggested wording contains number {num} that is not in "
                                       "the manuscript; use a [placeholder] unless it is a "
                                       "recomputed value you can show")
    # near-duplicates --------------------------------------------------------------
    def toks(c):
        return set(re.findall(r"[a-z]{4,}", (c.get("comment", "") + " " +
                                              c.get("quote", "")).lower()))
    for i, a in enumerate(comments):
        for b in comments[i + 1:]:
            ta, tb = toks(a), toks(b)
            if ta and tb and len(ta & tb) / len(ta | tb) > 0.6 and \
                    a.get("audience", "author") == b.get("audience", "author"):
                warns.append(f"{a.get('id')} and {b.get('id')} look like near-duplicates; merge "
                             "them or make the distinction explicit")
    return errors, warns


def fmt_loc(loc: dict) -> str:
    parts = []
    if loc.get("section"):
        parts.append(str(loc["section"]))
    for k, lab in (("page", "p."), ("line", "l."), ("table", ""), ("figure", ""), ("block", "[")):
        if loc.get(k):
            parts.append(f"{lab}{loc[k]}" + ("]" if k == "block" else ""))
    if loc.get("absent"):
        parts.append("(information absent)")
    return ", ".join(parts) or "n/a"


def render_md(ledger: dict, audience: str | None) -> str:
    cs = [c for c in ledger["comments"]
          if audience is None or c.get("audience", "author") == audience]
    order = {s: i for i, s in enumerate(SEVERITIES)}
    cs = sorted(cs, key=lambda c: (order.get(c["severity"], 9), c["id"]))
    n = Counter(c["severity"] for c in cs)
    out = [f"# Review comment ledger - {ledger.get('manuscript', '')}", "",
           "Counts: " + ", ".join(f"{s} {n.get(s, 0)}" for s in SEVERITIES), ""]
    out += ["| ID | Severity | Status | Category | Location | Comment (short) |",
            "|---|---|---|---|---|---|"]
    for c in cs:
        short = c["comment"].replace("|", "/").replace("\n", " ")
        short = short[:110] + ("..." if len(short) > 110 else "")
        out.append(f"| {c['id']} | {c['severity']} | {c['status']} | {c.get('category', '')} | "
                   f"{fmt_loc(c.get('location', {}))} | {short} |")
    out.append("")
    for c in cs:
        out.append(f"### {c['id']} - {c['severity']} ({c['status']}, {c.get('category', '')})")
        out.append(f"**Location:** {fmt_loc(c.get('location', {}))}")
        if c.get("quote"):
            out.append(f"**Original passage:** \"{c['quote']}\"")
        out.append(f"**Reviewer comment:** {c['comment']}")
        for key, lab in (("rationale", "Scientific rationale"),
                         ("required_revision", "Required revision"),
                         ("suggested_correction", "Suggested correction"),
                         ("evidence_needed", "Evidence or verification needed")):
            if c.get(key):
                out.append(f"**{lab}:** {c[key]}")
        out.append("")
    return "\n".join(out)


def write_csv(ledger: dict, path: str, audience: str | None) -> None:
    cols = ["id", "severity", "status", "category", "audience", "section", "block", "page",
            "line", "table", "figure", "quote", "comment", "rationale", "required_revision",
            "suggested_correction", "evidence_needed"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for c in ledger["comments"]:
            if audience and c.get("audience", "author") != audience:
                continue
            loc = c.get("location", {})
            row = {**c, **{k: loc.get(k, "") for k in
                           ("section", "block", "page", "line", "table", "figure")}}
            row.setdefault("audience", "author")
            w.writerow([row.get(k, "") for k in cols])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("ledger")
    v.add_argument("--map")
    r = sub.add_parser("render")
    r.add_argument("ledger")
    r.add_argument("--md")
    r.add_argument("--csv")
    r.add_argument("--audience", choices=["author", "editor"])
    a = ap.parse_args()
    ledger = json.loads(Path(a.ledger).read_text(encoding="utf-8"))
    if a.cmd == "validate":
        errs, warns = validate(ledger, a.map)
        for e in errs:
            print("ERROR:", e)
        for w in warns:
            print("WARN: ", w)
        n = Counter(c.get("severity") for c in ledger.get("comments", []))
        print(f"{len(ledger.get('comments', []))} comments: " +
              ", ".join(f"{s} {n.get(s, 0)}" for s in SEVERITIES))
        if not a.map:
            print("NOTE: no --map given, so quotes were NOT checked against the manuscript.")
        print("RESULT:", "FAIL" if errs else "PASS")
        return 1 if errs else 0
    if a.md:
        Path(a.md).write_text(render_md(ledger, a.audience), encoding="utf-8")
        print("wrote", a.md)
    if a.csv:
        write_csv(ledger, a.csv, a.audience)
        print("wrote", a.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
