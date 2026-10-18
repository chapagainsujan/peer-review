#!/usr/bin/env python3
"""Line-level audit helper: scan EVERY block of the manuscript for checkable problems.

    python lint_text.py MANUSCRIPT.map.json --out candidates.json [--spell] [--ref-start P103]

Output: candidates.json with one entry per finding:
    {block, rule, confidence, quote, message, suggestion}
These are CANDIDATES. A reviewer (you) must read the sentence, confirm each one, and then write
the confirmed ones into the ledger (category language / typo / terminology / consistency /
figures-tables ...). Never paste candidates into the report unchecked: patterns misfire on
legitimate text (e.g. a deliberately unusual species name, equation placeholders).

Rules (deterministic, no network):
  spacing/punctuation   double spaces, missing space after , ; . or before [n], space before
                        punctuation, space before %, unbalanced () [] (skipped near equations)
  repeated/garbled      repeated words, glued headings ("[21].2.4 Data collection"),
                        lost multiplication signs ("5 m2 m"), stray ";" in volume/pages
  language              "data was/is", US/UK spelling mixed, hyphenation variants
                        (broad-sense / broad sense), very long sentences, overused connectors
  scientific tone       overclaiming/informal/promotional words, "significant" without a test
                        nearby, causal/mechanistic wording to verify against evidence
  abbreviations         used but never defined; defined but never reused; same code with different
                        expansions
  units                 trait code followed by a number with a unit that contradicts the unit
                        stated in the table/abbreviation list (e.g. a length given in grams)
  cross references      Table/Fig./Supplementary items cited but not present, present but not
                        cited, cited out of order, S-table numbering conflicts
  numbers               values in the text that differ slightly (<=1%) from a table value
                        (possible transcription error); P-value notation inconsistencies
  spelling (--spell)    words not in the English word list, ignoring acronyms and repeated terms

Exit code 0 always (it is an aid, not a gate).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ABBR_ALLOW = {"DNA", "RNA", "PCR", "USA", "UK", "FAO", "ORCID", "SD", "SE", "CV", "GPS", "NASA",
              "ANOVA", "RCBD", "CRD", "LSD", "QTL", "GWAS", "SNP", "PCA", "II", "III", "IV", "CI",
              "NS", "ID", "URL", "DOI", "ISSN", "PDF", "MS", "AABB", "UN", "EU", "WHO", "NPK",
              "SI", "UV", "CO2", "OK", "AM", "PM", "TIFF", "JPEG", "PNG"}

TONE = {
    r"\bobvious(ly)?\b": ("high", "Delete or give the argument; 'obviously' signals a missing justification."),
    r"\bclearly\b": ("medium", "Replace by evidence-based wording or delete."),
    r"\bvery\b": ("low", "Imprecise intensifier; use a quantity or a stronger exact term."),
    r"\b(huge|immense|tremendous|enormous|massive|amazing|remarkabl[ey]|excellent)\b":
        ("high", "Promotional/informal; replace by the measured quantity."),
    r"\btedious\b": ("medium", "Subjective; state the cost/time quantitatively or cite."),
    r"\bnaturally\b": ("medium", "Informal sentence adverb; delete or rephrase."),
    r"\b(prove[sd]?|proven|proof)\b": ("high", "Observational/field data support, not prove; use 'indicate/suggest'."),
    r"\bnovel\b": ("medium", "Self-assessed novelty; state the concrete difference from prior work."),
    r"\b(super ?food|miracle|wonder crop|magic)\b": ("high", "Marketing term; use a defined nutritional statement with data."),
    r"\b(very important|extremely important|highly important)\b": ("medium", "Vague; state why and cite."),
    r"\b(crucial|vital|pivotal|paramount|essential)\b": ("low", "Overused emphasis word; check each use is justified."),
    r"\b(it is (well|widely|generally) (known|recognized|recognised|accepted|established)|well[- ]known)\b":
        ("medium", "Needs a citation or deletion."),
    r"\ba lot of\b": ("medium", "Informal; use 'many'/'much' or a quantity."),
    r"\b(interesting(ly)?|surprising(ly)?)\b": ("low", "Subjective; state why the finding matters."),
    r"\b(best|perfect|ideal|optimal|optimum)\b": ("low", "Superlative needs evidence (compared against what?)."),
    r"\b(always|never|all the studied|every)\b": ("low", "Absolute wording; check it is literally true for all cases."),
    r"\b(we believe|we feel|we think|in our opinion)\b": ("low", "Replace by evidence-based statement."),
    r"\bin recent years\b": ("low", "Vague time reference; give the period or citations."),
    r"\bnumerous studies\b": ("medium", "Vague; cite representative studies."),
}
CAUSAL = {
    r"\b(is|are|was|were) due to\b": "causal claim: is it supported by design/measurement?",
    r"\b(stems?|stemmed) from\b": "causal/mechanistic claim: evidence?",
    r"\b(is|are) (governed|controlled|determined|regulated) by\b": "mechanism asserted: evidence?",
    r"\b(explains?|explained by)\b": "explanatory claim: tested?",
    r"\breflects?\b": "interpretive verb: does the evidence demonstrate this?",
    r"\bresponsible for\b": "causal attribution: evidence?",
    r"\b(leads?|led) to\b": "causal wording from correlational data?",
    r"\bindicat(es|ing|ed)\b": None,   # too common; ignored
}
UKUS = [("analyz", "analys"), ("center", "centre"), ("color", "colour"), ("behavior", "behaviour"),
        ("fertiliz", "fertilis"), ("organiz", "organis"), ("labor", "labour"),
        ("favor", "favour"), ("program", "programme"), ("grey", "gray")]
CONNECTORS = ["Thus", "Similarly", "Therefore", "Moreover", "Furthermore", "Hence", "However",
              "Additionally", "As a result", "In contrast"]


def sentences(text: str):
    # keep it simple: split on ". " / "? " / "! " followed by capital or bracket
    parts = re.split(r"(?<=[a-z0-9\]\)])[.!?]\s+(?=[A-Z\[(])", text)
    return [p.strip() for p in parts if p.strip()]


def ctx(text: str, start: int, end: int, pad: int = 25) -> str:
    a, b = max(0, start - pad), min(len(text), end + pad)
    return text[a:b].strip()


class Finder:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, block, rule, confidence, quote, message, suggestion=""):
        self.items.append({"block": block, "rule": rule, "confidence": confidence,
                           "quote": " ".join(quote.split()) if quote else "",
                           "message": message, "suggestion": suggestion})


def lint(m: dict, ref_start: str | None, spell: bool) -> list[dict]:
    F = Finder()
    blocks = m["blocks"]
    paras = [b for b in blocks if b["type"] == "paragraph" and b["text"].strip()]
    ids = [b["id"] for b in blocks]
    # reference list start ---------------------------------------------------------------
    if ref_start is None:
        for b in paras:
            if re.fullmatch(r"(\d+\s*)?references?|bibliography|literature cited", b["text"].strip(), re.I):
                ref_start = b["id"]
    ref_ids = set()
    if ref_start and ref_start in ids:
        ref_ids = {b["id"] for b in blocks[ids.index(ref_start):] if b["type"] == "paragraph"}
    body = [b for b in blocks if b["text"].strip() and b["id"] not in ref_ids]
    body_paras = [b for b in paras if b["id"] not in ref_ids]
    full_body = "\n".join(b["text"] for b in body)

    # ------------------------------------------------ spacing / punctuation / garbling
    cite_style = Counter()
    for b in body + [x for x in paras if x["id"] in ref_ids]:
        t, i = b["text"], b["id"]
        in_ref = i in ref_ids
        has_eq = bool(b.get("equations"))
        for mt in re.finditer(r"(?<=\S)  +(?=\S)", t):
            F.add(i, "double-space", "high", ctx(t, mt.start(), mt.end()), "Double space.",
                  "Use a single space.")
        if not in_ref:
            for mt in re.finditer(r"\b[a-z]{3,}[,;](?=[A-Za-z])", t):
                if "http" in ctx(t, mt.start(), mt.end(), 40):
                    continue
                F.add(i, "missing-space-after-punct", "high", ctx(t, mt.start(), mt.end()),
                      "Missing space after comma/semicolon.", "Insert a space.")
            for mt in re.finditer(r"\b[a-z]{3,}\.(?=[A-Z][a-z])", t):
                if "http" in ctx(t, mt.start(), mt.end(), 40):
                    continue
                F.add(i, "missing-space-after-period", "high", ctx(t, mt.start(), mt.end()),
                      "Missing space after full stop (or merged sentences/heading).", "Insert a space.")
            for mt in re.finditer(r"[\]\)a-z]\.\d{1,2}(\.\d{1,2})+\s+[A-Z][a-z]", t):
                F.add(i, "glued-heading", "high", ctx(t, mt.start(), mt.end(), 30),
                      "A section heading appears glued to the preceding sentence.",
                      "Start the heading on a new line.")
            for mt in re.finditer(r"\s[,;.](?=\s|$)", t):
                F.add(i, "space-before-punct", "medium", ctx(t, mt.start(), mt.end()),
                      "Space before punctuation mark.", "Remove the space.")
            for mt in re.finditer(r"\d\s%", t):
                F.add(i, "space-before-percent", "low", ctx(t, mt.start(), mt.end()),
                      "Space between number and %.", "Use a consistent style (e.g. 20%).")
            for mt in re.finditer(r"\d+\s?m2?\s?m2?\b(?=\))", t):
                if re.search(r"\d+\s?m2\s?m\b", mt.group(0)):
                    F.add(i, "garbled-dimension", "high", ctx(t, mt.start(), mt.end()),
                          "Plot size looks garbled (multiplication sign/unit lost).",
                          "Write dimensions explicitly, e.g. '5 m × 2 m'.")
            for mt in re.finditer(r"\b(\w+)\s+\1\b", t, re.I):
                w = mt.group(1)
                if w.isdigit() or len(w) < 2:
                    continue
                F.add(i, "repeated-word", "high", ctx(t, mt.start(), mt.end()),
                      f"Repeated word '{w}'.", "Delete one.")
            if not has_eq:
                for op, cl, nm in (("(", ")", "parentheses"), ("[", "]", "square brackets")):
                    if t.count(op) != t.count(cl):
                        F.add(i, "unbalanced-brackets", "medium", t[:70] + "...",
                              f"Unbalanced {nm} ({t.count(op)} open, {t.count(cl)} close).",
                              "Check for a lost symbol or equation.")
            for mt in re.finditer(r"([A-Za-z])\[(\d)", t):
                cite_style["nospace"] += 1
            for mt in re.finditer(r"([A-Za-z]) \[(\d)", t):
                cite_style["space"] += 1
        # data was/is
        for mt in re.finditer(r"\b[Dd]ata (was|is|has been)\b", t):
            F.add(i, "data-singular", "medium", ctx(t, mt.start(), mt.end()),
                  "'Data' is plural in most journal styles.", "Use 'data were/are/have been' "
                  "(or 'the dataset was').")
        # tone / red flags
        if not in_ref:
            for pat, (conf, msg) in TONE.items():
                for mt in re.finditer(pat, t, re.I):
                    F.add(i, "tone", conf, ctx(t, mt.start(), mt.end()),
                          f"Wording to reconsider: '{mt.group(0)}'. {msg}")
            for pat, msg in CAUSAL.items():
                if not msg:
                    continue
                for mt in re.finditer(pat, t, re.I):
                    F.add(i, "causal-claim", "medium", ctx(t, mt.start(), mt.end()),
                          f"Check support: {msg}")
            for mt in re.finditer(r"\bsignifican(t|tly|ce)\b", t, re.I):
                window = t[max(0, mt.start() - 120): mt.end() + 120]
                if not re.search(r"[pP]\s*[<≤=>]|\bP\b\s*[<≤=>]|\bF\s*\(|\bt\s*=|test|ANOVA|\bCI\b|"
                                 r"Table|Fig", window):
                    F.add(i, "significant-no-test", "medium", ctx(t, mt.start(), mt.end(), 40),
                          "'Significant' used without a test, P-value or table nearby.",
                          "Report the test/P-value, or use 'substantial'/'marked' if not statistical.")
            for s in sentences(t):
                n = len(s.split())
                if n > 45:
                    F.add(i, "long-sentence", "low", s[:90] + "...",
                          f"Very long sentence ({n} words).", "Split into two sentences.")

    # --------------------------------------------------------------- citation spacing
    if cite_style["nospace"] and cite_style["space"]:
        minority = "nospace" if cite_style["nospace"] < cite_style["space"] else "space"
        for b in body_paras:
            pat = r"[A-Za-z]\[\d" if minority == "nospace" else r"[A-Za-z] \[\d"
            for mt in re.finditer(pat, b["text"]):
                F.add(b["id"], "citation-spacing", "medium", ctx(b["text"], mt.start(), mt.end()),
                      f"Citation bracket spacing is inconsistent ({cite_style['space']} with a space, "
                      f"{cite_style['nospace']} without).", "Use one style throughout.")

    # --------------------------------------------------- connector overuse (per paragraph)
    for b in body_paras:
        for c in CONNECTORS:
            n = len(re.findall(r"(?:^|\.\s)" + c + r"\b", b["text"]))
            if n >= 3:
                F.add(b["id"], "connector-overuse", "low", c + "...",
                      f"'{c}' opens {n} sentences in one paragraph.", "Vary sentence openings.")
    tot = {c: len(re.findall(r"(?:^|\.\s)" + c + r"\b", full_body)) for c in CONNECTORS}
    for c, n in tot.items():
        if n >= 6:
            F.add("(global)", "connector-overuse", "low", c + ",", f"'{c}' opens {n} sentences in the "
                  "body text.", "Reduce repetition of sentence-initial connectors.")

    # --------------------------------------------------------- US/UK spelling consistency
    low = full_body.lower()
    for us, uk in UKUS:
        if re.search(us, low) and re.search(uk, low):
            F.add("(global)", "us-uk-mix", "medium", f"{us}*/{uk}*", f"Both US ('{us}...') and UK "
                  f"('{uk}...') spellings are used.", "Choose one variety (check the journal).")

    # ------------------------------------------------------------ hyphenation variants
    hy = Counter(re.findall(r"\b[a-z]{3,}-[a-z]{3,}\b", low))
    for h, n in hy.items():
        a, b2 = h.split("-")
        sp = len(re.findall(r"\b" + a + r" " + b2 + r"\b", low))
        if sp:
            F.add("(global)", "hyphenation-variant", "low", f"{h} ({n}x) / {a} {b2} ({sp}x)",
                  "Same compound written with and without hyphen.", "Use one form consistently.")

    # ----------------------------------------------------------------- P-value notation
    pforms = Counter()
    for mt in re.finditer(r"\b([pP])\s*([<≤=>])\s*0?\.\d+", full_body):
        pforms[mt.group(1)] += 1
    if len(pforms) > 1:
        F.add("(global)", "p-notation", "medium", f"p: {pforms['p']}x, P: {pforms['P']}x",
              "P-value symbol is written both as 'p' and 'P'.", "Use one (italic P is common).")
    levels = set(re.findall(r"\b[pP]\s*[<≤]\s*(0?\.\d+)", full_body))
    if len(levels) > 3:
        F.add("(global)", "p-notation", "low", ", ".join(sorted(levels)),
              "Several different significance thresholds are used.",
              "State the alpha level once and report exact P where possible.")

    # ------------------------------------------------------------------ abbreviations
    defs: dict[str, set] = defaultdict(set)
    def_block: dict[str, str] = {}
    for b in body:
        t = b["text"]
        for mt in re.finditer(r"((?:[A-Za-z][\w\-]*\s+){1,6}[A-Za-z][\w\-]*)\s*\(\s*([A-Za-z][A-Za-z0-9]{1,7})\s*\)", t):
            code = mt.group(2)
            if code.upper() == code or re.search(r"[A-Z].*[A-Z]", code):
                words = mt.group(1).split()
                k = len(re.sub(r"[a-z0-9]", "", code)) or len(code)
                defs[code].add(" ".join(words[-max(k, 2):]).lower())
                def_block.setdefault(code, b["id"])
        for mt in re.finditer(r"\b([A-Z][A-Za-z0-9]{1,7})\s*:\s*([A-Za-z][A-Za-z \-/]+?)(?:\s*\(([^)]*)\))?\s*(?:;|\.|$)", t):
            defs[mt.group(1)].add(mt.group(2).strip().lower())
            def_block.setdefault(mt.group(1), b["id"])
    # table header "Name | CODE" pairs are not parsed (layout-specific)
    codes_in_tables = set()
    for b in blocks:
        if b["type"] == "table_cell":
            for tok in re.findall(r"\b[A-Z]{2,6}\b", b["text"]):
                codes_in_tables.add(tok)
    skip_sec = re.compile(r"author contribution|acknowledg|orcid|declaration|funding|competing", re.I)
    abbr_body = "\n".join(b["text"] for b in body
                          if not skip_sec.search(b.get("section", "")) and b["text"].strip()[:6] != "ORCID")
    used = Counter(re.findall(r"\b[A-Z][A-Z0-9]{1,6}\b", abbr_body))
    for code, n in used.items():
        if code in ABBR_ALLOW or code.isdigit() or re.fullmatch(r"S\d+", code):
            continue
        if code not in defs and code not in codes_in_tables:
            first = next(b for b in body if re.search(r"\b" + code + r"\b", b["text"])
                         and not skip_sec.search(b.get("section", "")))
            F.add(first["id"], "abbrev-undefined", "medium", code,
                  f"Abbreviation '{code}' is used ({n}x) but not defined anywhere I could find.",
                  "Define at first use or in the table/figure legend.")
    for code, exps in defs.items():
        if len(code) < 2 or code in ABBR_ALLOW:
            continue
        norm = {re.sub(r"[^a-z ]", "", e).strip() for e in exps}
        norm = {e for e in norm if e}
        if len({e.replace("variance", "variation") for e in norm}) > 1 or len(norm) > 1:
            # differ beyond capitalisation?
            F.add(def_block.get(code, "(global)"), "abbrev-inconsistent", "medium", code,
                  f"'{code}' is expanded in different ways: " + "; ".join(sorted(exps)),
                  "Use one expansion everywhere.")
        total = len(re.findall(r"\b" + re.escape(code) + r"\b", full_body))
        if total <= 1 and code not in codes_in_tables:
            F.add(def_block.get(code, "(global)"), "abbrev-unused", "low", code,
                  f"'{code}' is defined but never used again.", "Remove the abbreviation or use it.")

    # --------------------------------------------------------------------- unit check
    unit_of: dict[str, str] = {}
    for b in blocks:
        for mt in re.finditer(r"\b([A-Z]{2,5})\s*:\s*[A-Za-z \-]+?\s*\(([^)]+)\)", b["text"]):
            unit_of.setdefault(mt.group(1), mt.group(2).strip().lower())
        for mt in re.finditer(r"\b([A-Z]{2,5})\s*:\s*[A-Za-z \-]+?(?:;|\.|$)", b["text"]):
            unit_of.setdefault(mt.group(1), "")   # no unit -> dimensionless/count
    for b in body_paras:
        for s in sentences(b["text"]):
            for mt in re.finditer(r"\b([A-Z]{2,5})\b[^.;]{0,60}?(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*(cm|g|kg|mm|m|days|t/ha|%)\b", s):
                code, unit = mt.group(1), mt.group(4).lower()
                if code in unit_of:
                    exp = unit_of[code]
                    if exp and unit != exp and unit not in exp:
                        F.add(b["id"], "unit-mismatch", "high", s[:110],
                              f"{code} is defined as ({exp}) elsewhere but given in '{unit}' here.",
                              f"Check the unit of {code}.")
                    if not exp and exp == "":
                        F.add(b["id"], "unit-mismatch", "medium", s[:110],
                              f"{code} appears to be a count/dimensionless trait, but '{unit}' is attached.",
                              f"Check the unit of {code}.")

    # --------------------------------------------------------------- cross-references
    cap = {}
    for b in body_paras:
        mt = re.match(r"\s*(Table|Fig(?:ure)?\.?)\s+(S?\d+)\b", b["text"])
        if mt:
            kind = "Table" if mt.group(1).startswith("T") else "Fig"
            cap[(kind, mt.group(2))] = b["id"]
    cited_order: list[tuple] = []
    cited = defaultdict(list)
    for b in body_paras:
        if re.match(r"\s*(Table|Fig(?:ure)?\.?)\s+S?\d+\b", b["text"]):
            continue
        for mt in re.finditer(r"\b(Table|Tables|Fig\.|Figs\.|Figure|Figures)\s+(S?\d+)((?:\s*(?:,|and|&|–|-)\s*S?\d+)*)", b["text"]):
            kind = "Table" if mt.group(1).startswith("T") else "Fig"
            nums = [mt.group(2)] + re.findall(r"S?\d+", mt.group(3))
            for n in nums:
                cited[(kind, n)].append(b["id"])
                cited_order.append((kind, n))
    for key, bl in cited.items():
        if key not in cap and not key[1].startswith("S"):
            F.add(bl[0], "xref-missing-item", "high", f"{key[0]} {key[1]}",
                  f"{key[0]} {key[1]} is cited but no caption was found.", "Check numbering.")
    for key, bid in cap.items():
        if key not in cited and not key[1].startswith("S"):
            F.add(bid, "xref-uncited-item", "high", f"{key[0]} {key[1]}",
                  f"{key[0]} {key[1]} has a caption but is never cited in the text.", "Cite it in the text.")
    for kind in ("Table", "Fig"):
        seq = []
        for k, n in cited_order:
            if k == kind and not n.startswith("S") and n not in seq:
                seq.append(n)
        nums = [int(x) for x in seq]
        if nums != sorted(nums):
            F.add("(global)", "xref-order", "medium", f"{kind} first-citation order: {seq}",
                  f"{kind}s are not first cited in numerical order.", "Renumber or reorder.")
    # supplementary tables: which are cited and with what content?
    sup = defaultdict(set)
    for b in body_paras:
        for mt in re.finditer(r"\b(Table|Fig\.)\s*(S\d+)\b", b["text"]):
            sup[mt.group(2)].add(b["id"])
    for s, bl in sup.items():
        pass  # content cross-check is done by the reviewer; see message below
    if sup:
        F.add("(global)", "xref-supplement", "low", ", ".join(sorted(sup)),
              "Supplementary items are cited. Verify against the supplementary list that each S-number "
              "has the content the text claims (e.g. correlations vs soil properties).",
              "Reviewer to check the supplementary file list.")

    # ------------------------------------------------------------ numbers: near matches
    table_nums = []
    for b in blocks:
        if b["type"] == "table_cell":
            for n in re.findall(r"(?<![\w.])-?\d+\.\d+|(?<![\w.])-?\d+(?![\w.])", b["text"].replace("−", "-")):
                table_nums.append((float(n), n, b["id"]))
    tset = {v for v, _, _ in table_nums}
    for b in body_paras:
        for mt in re.finditer(r"(?<![\w.\[])-?\d+\.\d{2,}(?![\w.])", b["text"].replace("−", "-")):
            v = float(mt.group(0))
            if v in tset:
                continue
            if re.match(r"\s*°", b["text"][mt.end():mt.end() + 3]) or \
                    re.match(r"\s*°", b["text"][mt.end():mt.end() + 1]):
                continue                      # coordinates are compared by the reviewer, not here
            near = [(abs(tv - v), tv, ts, bid) for tv, ts, bid in table_nums
                    if tv != 0 and "." in ts and abs(tv - v) / abs(tv) <= 0.01]
            if near:
                _, tv, ts, bid = min(near)
                F.add(b["id"], "number-near-table", "medium", ctx(b["text"], mt.start(), mt.end(), 40),
                      f"Value {mt.group(0)} is not in any table but is within 1% of {ts} ({bid}).",
                      "Check for a transcription/rounding discrepancy between text and table.")

    # --------------------------------------------------------------------- spelling
    if spell:
        try:
            from spellchecker import SpellChecker
            sp = SpellChecker()
            words = re.findall(r"\b[a-z]{4,}\b", full_body.lower())
            freq = Counter(words)
            unknown = sp.unknown(set(words))
            for w in sorted(unknown):
                if freq[w] <= 2:
                    blk = next(b for b in body if re.search(r"\b" + w + r"\b", b["text"], re.I))
                    F.add(blk["id"], "spelling-candidate", "low", w,
                          f"'{w}' is not in the English word list ({freq[w]}x).",
                          "Check spelling (may be a valid technical term or cultivar name).")
        except ImportError:
            print("pyspellchecker not installed: pip install pyspellchecker", file=sys.stderr)
    return F.items


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("map")
    ap.add_argument("--out", default="candidates.json")
    ap.add_argument("--spell", action="store_true")
    ap.add_argument("--ref-start", help="block ID where the reference list starts (auto-detected)")
    a = ap.parse_args()
    m = json.loads(Path(a.map).read_text(encoding="utf-8"))
    items = lint(m, a.ref_start, a.spell)
    # de-duplicate identical (block, rule, quote)
    seen, out = set(), []
    for it in items:
        k = (it["block"], it["rule"], it["quote"])
        if k not in seen:
            seen.add(k)
            out.append(it)
    Path(a.out).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    cnt = Counter(i["rule"] for i in out)
    print(f"{len(out)} candidate findings written to {a.out}")
    for r, n in cnt.most_common():
        print(f"  {r}: {n}")
    print("These are candidates: read each sentence, confirm, then add confirmed ones to the ledger.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
