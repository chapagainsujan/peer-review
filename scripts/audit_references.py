#!/usr/bin/env python3
"""Audit the reference list and in-text citations of a manuscript.

    python audit_references.py MANUSCRIPT.map.json --out refs_audit.json
        [--ref-start P103] [--authors "Chapagain,Kandel"] [--submission-year 2026]

What it checks (offline, deterministic)
  Per entry     type guess (journal / chapter / book-report / conference / web / unknown) and the
                fields that type needs: authors, year, title, container (journal/book), volume,
                pages or article number, DOI/URL; odd punctuation (e.g. "2010;1;489-499"),
                inconsistent DOI style, text that looks truncated.
  Cross-check   numeric style: citations cited but missing from the list, listed but never cited,
                first-citation order, author named in the text vs the entry at that number
                ("Gadi et al. [38]"); author-year style: surname+year pairs present/absent.
  List level    duplicates (same DOI or near-identical title), self-citation share (--authors),
                age distribution of references, share of entries with a DOI.

It CANNOT verify that a volume, page range or year is *correct*. A missing field is a fact; a wrong
field is a suspicion until you check the publisher/Crossref/PubMed record with web search or fetch
(see references/reference-audit.md). Findings carry "verify": "none" (certain from the text) or
"web" (needs lookup before it becomes a confirmed comment).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

YEAR = re.compile(r"\b(?:19|20)\d{2}[a-z]?\b")
DOI = re.compile(r"10\.\d{4,9}/[^\s]+")


def expand(nums: str) -> list[int]:
    out: list[int] = []
    for part in re.split(r"\s*,\s*", nums.strip()):
        m = re.fullmatch(r"(\d+)\s*[–\-—]\s*(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if 0 < b - a < 80:
                out.extend(range(a, b + 1))
            else:
                out.extend([a, b])
        elif part.isdigit():
            out.append(int(part))
    return out


def classify(t: str) -> str:
    low = t.lower()
    if re.search(r"\bproceedings\b|\bproc\.|\bconference\b|\bsymposium\b|\bcongress\b", low):
        return "conference"
    if re.search(r"(^|\.\s)In[: ]\s*[A-Z]|\beds?\.|\beditors?\b", t) and not re.search(r"\b\d{4};\d+[:(]", t):
        return "chapter"
    mj = re.search(r"\.\s+([A-Z][\w .&()\-]{2,60})\.\s+(19|20)\d{2}\s*:\s*\d", t)
    if mj:                                    # 'Journal. 2020:55-60' = year then pages, volume missing
        words = [w for w in mj.group(1).split() if w.isalpha()]
        caps = sum(1 for w in words if w[0].isupper())
        if words and len(words) <= 6 and caps / len(words) >= 0.7:   # abbreviated journal-like container
            return "journal"
    if re.search(r"\b(19|20)\d{2};\s*[\w\-]+\s*(\(\w+\))?\s*[:;]", t) or re.search(
            r"\bvol\.?\s*\d+|\b\d+\(\d+\)\s*[:,]", t):
        return "journal"
    if re.search(r"https?://(?!doi\.org)", t) and not DOI.search(t):
        return "web"
    if DOI.search(t) and not re.search(r"publisher|press|rome|editor", low):
        return "journal"
    if re.search(r"\b(press|publisher|publishing|rome|alliance|institute|council|report|working group|"
                 r"thesis|dissertation|university)\b", low):
        return "book-report"
    return "unknown"


def parse_entry(t: str) -> dict:
    d: dict = {"text": t, "type": classify(t)}
    d["years"] = YEAR.findall(t)
    d["year"] = d["years"][0] if d["years"] else None
    m = DOI.search(t)
    d["doi"] = m.group(0).rstrip(".,;") if m else None
    d["doi_trailing_period"] = bool(m and m.group(0).endswith("."))
    d["url"] = bool(re.search(r"https?://", t))
    # Vancouver/Springer "Year;Vol(Issue):pages" family
    mv = re.search(r"((?:19|20)\d{2})[a-z]?\s*;\s*([\w\-]+)\s*(?:\(([\w\-]+)\))?\s*[:;,]?\s*([\w\-–]+)?", t)
    d["volume"] = d["issue"] = d["pages"] = None
    if mv:
        d["volume"], d["issue"], d["pages"] = mv.group(2), mv.group(3), mv.group(4)
    mv2 = re.search(r"\bvol\.?\s*(\d+)", t, re.I)
    if mv2 and not d["volume"]:
        d["volume"] = mv2.group(1)
    mv3 = re.search(r"\b(\d{1,4})\s*\((\d{1,4})\)\s*[:,]?\s*([\w\-–]+)?", t)
    if mv3 and not d["volume"]:
        d["volume"], d["issue"], d["pages"] = mv3.group(1), mv3.group(2), mv3.group(3)
    mp = re.search(r"(?:pp?\.?\s*)?(\d{1,6})\s*[–\-—]\s*(\d{1,6})", re.sub(DOI, "", t))
    if mp and not d["pages"]:
        d["pages"] = f"{mp.group(1)}–{mp.group(2)}"
    if re.search(r"\b(e\d{4,}|art\.?\s*no\.?\s*\w+|article\s*\w+)\b", t, re.I):
        d["pages"] = d["pages"] or "article-number"
    # authors: text before first period that ends an author block
    ma = re.match(r"^([^.]*?(?:\b[A-Z]{1,3}\b|et al)[^.]*)\.", t)
    d["authors"] = ma.group(1).strip() if ma else None
    d["first_author"] = re.match(r"^([A-Z][A-Za-z'\-]+(?:\s+[A-Z][a-z'\-]+)?)", t).group(1) if \
        re.match(r"^[A-Z][A-Za-z'\-]+", t) else None
    return d


def audit(m: dict, ref_start: str | None, style: str, authors: list[str], sub_year: int) -> dict:
    blocks = m["blocks"]
    ids = [b["id"] for b in blocks]
    paras = [b for b in blocks if b["type"] == "paragraph"]
    if ref_start is None:
        for b in paras:
            if re.fullmatch(r"(\d+\s*)?references?|bibliography|literature cited", b["text"].strip(), re.I):
                ref_start = b["id"]
    if not ref_start or ref_start not in ids:
        return {"error": "Could not find the reference list; pass --ref-start BLOCK_ID"}
    start = ids.index(ref_start)
    entries_blocks = [b for b in blocks[start + 1:] if b["type"] == "paragraph" and b["text"].strip()]
    body = [b for b in blocks[:start] if b["text"].strip()]
    findings: list[dict] = []

    def F(entry, block, issue, sev, msg, verify="none"):
        findings.append({"entry": entry, "block": block, "issue": issue, "severity_suggestion": sev,
                         "message": msg, "verify": verify})

    # style detection ------------------------------------------------------------------
    body_text = "\n".join(b["text"] for b in body if b["type"] == "paragraph")
    numeric_hits = re.findall(r"\[\s*\d+(?:\s*[–\-,]\s*\d+)*\s*\]", body_text)
    if style == "auto":
        style = "numeric" if len(numeric_hits) >= 5 else "author-year"

    parsed = []
    for i, b in enumerate(entries_blocks, start=1):
        t = re.sub(r"^\s*\[?\d+[\].)]\s+", "", b["text"].strip())
        e = parse_entry(t)
        e["n"], e["block"] = i, b["id"]
        parsed.append(e)

    # ---- per-entry completeness -------------------------------------------------------
    doi_styles = Counter()
    for e in parsed:
        n, blk, ty = e["n"], e["block"], e["type"]
        tag = f"[{n}] "
        if not e["authors"] and ty != "web":
            F(n, blk, "authors", "Minor", tag + "Author block not recognised (organisation author? missing?).")
        if not e["year"]:
            F(n, blk, "year", "Major", tag + "No publication year found.")
        if ty == "journal":
            if not e["volume"]:
                F(n, blk, "volume", "Major", tag + "Journal article without a volume number.", "web")
            if not e["pages"]:
                F(n, blk, "pages", "Major", tag + "Journal article without page range or article number.", "web")
            if not e["doi"]:
                old = bool(e["year"] and int(e["year"][:4]) < 1990)
                F(n, blk, "doi", "Optional" if old else "Minor", tag + (
                    "No DOI (pre-1990 article: a DOI may not exist; check Crossref)." if old else
                    "No DOI given (add it if one exists; Crossref lookup)."), "web")
            if re.search(r"\d{4};\s*\d+\s*;\s*\d+", e["text"]):
                F(n, blk, "punctuation", "Minor", tag + "Unusual punctuation in the volume/pages block "
                  "(semicolon where colon or comma is expected).")
            if e["pages"] and re.fullmatch(r"\d{1,2}", str(e["pages"])) and not re.search(
                    r"e\d|art|;\s*\d+\s*:\s*\d+\.", e["text"]):
                F(n, blk, "pages", "Minor", tag + f"Single page value '{e['pages']}': page range or article "
                  "number may be incomplete.", "web")
            if re.search(r"\b(19|20)\d{2}:\s*\d", e["text"]) and not e["volume"]:
                F(n, blk, "volume", "Major", tag + "Year is followed directly by page numbers with no volume.", "web")
        elif ty == "chapter":
            for pat, lab in ((r"\bed(s)?\b\.?|editor", "editor(s)"), (r"\b(press|publisher|springer|elsevier|wiley|"
                              r"cabi|cambridge|oxford|rome|london|new york)\b", "publisher/place"),
                             (r"\d+\s*[–\-]\s*\d+", "page range")):
                if not re.search(pat, e["text"], re.I):
                    F(n, blk, "chapter-" + lab.split("/")[0], "Major", tag + f"Book chapter without {lab}.", "web")
        elif ty in ("book-report", "unknown"):
            if not re.search(r"\b(press|publisher|publishing|institute|alliance|council|rome|"
                             r"university)\b", e["text"], re.I) and not e["url"] and not e["doi"]:
                F(n, blk, "publisher", "Major", tag + "No publisher/place/URL: the source cannot be located.", "web")
            if ty == "book-report" and not e["url"] and not e["doi"]:
                F(n, blk, "access", "Minor", tag + "Grey literature without URL/DOI; give an accessible link "
                  "or repository.", "web")
        if e["doi"]:
            doi_styles["https://doi.org" if "doi.org" in e["text"] else "bare/doi:"] += 1
        if re.search(r"\b(19|20)\d{2}\b", e["text"]) and e["year"] and int(e["year"][:4]) > sub_year:
            F(n, blk, "year", "Major", tag + f"Year {e['year']} is later than the submission year.", "web")
        if len(e["text"]) < 40:
            F(n, blk, "truncated", "Major", tag + "Entry is very short and looks incomplete.")
        if re.search(r"\bet al\b", e["text"][:120]) and ty == "journal":
            F(n, blk, "et-al-in-list", "Optional", tag + "'et al.' in the list; many journals require all "
              "authors (up to a limit).")
        if re.search(r"\bin\s+[A-Z][a-z]+ .* \d{4};\d+\.", e["text"]) and ty != "journal":
            pass
    if len(doi_styles) > 1:
        F(None, None, "doi-style", "Minor", f"DOIs are formatted in different ways: {dict(doi_styles)}.")
    tp = Counter(e["doi_trailing_period"] for e in parsed if e["doi"])
    if len(tp) > 1:
        F(None, None, "doi-punctuation", "Optional",
          f"Some DOIs end with a full stop and some do not ({tp[True]} vs {tp[False]}): make consistent.")
    page_dash = Counter("en" if "–" in (e["pages"] or "") else "hyphen" if "-" in (e["pages"] or "") else "n/a"
                        for e in parsed)
    if page_dash["en"] and page_dash["hyphen"]:
        F(None, None, "page-dash", "Optional", "Page ranges use both hyphens and en dashes.")

    # ---- cross-check in-text <-> list ----------------------------------------------------
    cited_first: dict[int, str] = {}
    cited_all: Counter = Counter()
    if style == "numeric":
        for b in body:
            if b["type"] != "paragraph":
                continue
            for mt in re.finditer(r"\[\s*(\d+(?:\s*[–\-,]\s*\d+)*)\s*\]", b["text"]):
                for k in expand(mt.group(1)):
                    cited_all[k] += 1
                    cited_first.setdefault(k, b["id"])
        n_list = len(parsed)
        for k in sorted(cited_all):
            if k > n_list or k < 1:
                F(None, cited_first[k], "cited-not-in-list", "Major",
                  f"[{k}] is cited in the text but the list has only {n_list} entries.")
        for e in parsed:
            if e["n"] not in cited_all:
                F(e["n"], e["block"], "listed-not-cited", "Major",
                  f"[{e['n']}] is in the reference list but is never cited in the text.")
        order = []
        for b in body:
            if b["type"] == "paragraph":
                for mt in re.finditer(r"\[\s*(\d+(?:\s*[–\-,]\s*\d+)*)\s*\]", b["text"]):
                    for k in expand(mt.group(1)):
                        if k not in order:
                            order.append(k)
        mx = 0
        for k in order:
            if k < mx and k <= n_list:
                F(k, cited_first.get(k), "citation-order", "Minor",
                  f"[{k}] is first cited after [{mx}]: numbered styles number references in order of "
                  "first citation.")
            mx = max(mx, k)
        # narrative author vs number
        list_surnames = {(e["first_author"] or "").split()[0].lower() for e in parsed if e["first_author"]}
        for b in body:
            if b["type"] != "paragraph":
                continue
            for mt in re.finditer(r"\b([A-Z][A-Za-z'\-]+)(?:\s+et al\.?|\s+(?:and|&)\s+([A-Z][A-Za-z'\-]+))?\s*\[\s*(\d+)\s*\]", b["text"]):
                sur, k = mt.group(1), int(mt.group(3))
                if sur in ("Table", "Fig", "Figure", "Ref", "Reference", "Section"):
                    continue
                full = mt.group(0)
                explicit = bool(re.search(r"et al|\band\b|&", full))
                if not explicit and sur.lower() not in list_surnames:
                    continue          # a capitalised word that is not an author name (e.g. "Superfood")
                if 1 <= k <= len(parsed):
                    fa = (parsed[k - 1]["first_author"] or "")
                    if sur.lower() not in parsed[k - 1]["text"][:200].lower():
                        F(k, b["id"], "author-number-mismatch", "Major",
                          f"Text says '{mt.group(0)}' but reference [{k}] begins '{parsed[k-1]['text'][:50]}...'.")
    else:
        lst = [(e["n"], (e["first_author"] or "").split()[-1:] and (e["first_author"] or "").split()[0].lower(),
                (e["year"] or "")[:4]) for e in parsed]
        in_text = set()
        for b in body:
            if b["type"] != "paragraph":
                continue
            for mt in re.finditer(r"([A-Z][A-Za-z'\-]+)(?:\s+et al\.?|\s+(?:and|&)\s+[A-Z][A-Za-z'\-]+)?,?\s*"
                                  r"\(?((?:19|20)\d{2})[a-z]?\)?", b["text"]):
                in_text.add((mt.group(1).lower(), mt.group(2), b["id"]))
        for sur, yr, blk in sorted(in_text):
            if not any(s == sur and y == yr for _, s, y in lst):
                F(None, blk, "cited-not-in-list", "Major", f"'{sur.title()} {yr}' is cited in the text but "
                  "no matching entry was found in the list.")
        txt_pairs = {(s, y) for s, y, _ in in_text}
        for n, s, y in lst:
            if (s, y) not in txt_pairs:
                F(n, parsed[n - 1]["block"], "listed-not-cited", "Major",
                  f"Entry {n} ({s.title()} {y}) is not cited in the text.")

    # ---- list level ---------------------------------------------------------------------
    seen_doi, titles = {}, []
    for e in parsed:
        if e["doi"]:
            k = e["doi"].lower()
            if k in seen_doi:
                F(e["n"], e["block"], "duplicate", "Major", f"[{e['n']}] and [{seen_doi[k]}] have the same DOI.")
            seen_doi[k] = e["n"]
        mt = re.match(r"^[^.]*\.\s*(.+?)\.\s", e["text"])
        titles.append((e["n"], (mt.group(1).lower() if mt else e["text"][:80].lower())))
    for i, (a, ta) in enumerate(titles):
        for b2, tb in titles[i + 1:]:
            if len(ta) > 25 and difflib.SequenceMatcher(None, ta, tb).ratio() > 0.92:
                F(a, parsed[a - 1]["block"], "duplicate", "Major", f"[{a}] and [{b2}] have near-identical titles.")
    seen_f, uniq = set(), []
    for f in findings:                       # one finding per (entry, issue)
        k = (f["entry"], f["issue"])
        if f["entry"] is None or k not in seen_f:
            seen_f.add(k)
            uniq.append(f)
    findings[:] = uniq
    summary = {"style": style, "n_entries": len(parsed),
               "with_doi": sum(1 for e in parsed if e["doi"]),
               "types": dict(Counter(e["type"] for e in parsed))}
    yrs = [int(e["year"][:4]) for e in parsed if e["year"]]
    if yrs:
        summary["year_range"] = [min(yrs), max(yrs)]
        recent = sum(1 for y in yrs if y >= sub_year - 5)
        summary["share_last_5_years"] = round(recent / len(yrs), 2)
        summary["share_older_than_20_years"] = round(sum(1 for y in yrs if y < sub_year - 20) / len(yrs), 2)
    if authors:
        selfc = [e["n"] for e in parsed if any(a.lower() in e["text"][:250].lower() for a in authors)]
        summary["self_citations"] = {"entries": selfc, "share": round(len(selfc) / len(parsed), 2)}
        if len(selfc) / len(parsed) > 0.15:
            F(None, None, "self-citation", "Optional",
              f"{len(selfc)} of {len(parsed)} references ({len(selfc)/len(parsed):.0%}) share an author "
              "with the manuscript: check each is necessary.")
    return {"summary": summary, "entries": [{k: v for k, v in e.items() if k != "text"} | {"text": e["text"]}
                                            for e in parsed], "findings": findings}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("map")
    ap.add_argument("--out", default="refs_audit.json")
    ap.add_argument("--ref-start")
    ap.add_argument("--style", choices=["auto", "numeric", "author-year"], default="auto")
    ap.add_argument("--authors", default="", help="comma-separated surnames of the manuscript authors")
    ap.add_argument("--submission-year", type=int, default=date.today().year)
    a = ap.parse_args()
    m = json.loads(Path(a.map).read_text(encoding="utf-8"))
    res = audit(m, a.ref_start, a.style, [x.strip() for x in a.authors.split(",") if x.strip()],
                a.submission_year)
    if "error" in res:
        print("ERROR:", res["error"])
        return 2
    Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    s = res["summary"]
    print(f"{s['n_entries']} references ({s['style']} style); {s['with_doi']} with DOI; types: {s['types']}")
    cnt = Counter((f["issue"], f["severity_suggestion"]) for f in res["findings"])
    for (iss, sev), n in sorted(cnt.items(), key=lambda x: -x[1]):
        print(f"  {iss} [{sev}]: {n}")
    print(f"{len(res['findings'])} findings written to {a.out}. Findings with verify='web' must be checked "
          "against the publisher/Crossref/PubMed record before they become confirmed comments.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
