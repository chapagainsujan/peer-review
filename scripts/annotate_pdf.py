#!/usr/bin/env python3
"""Insert ledger comments into a text-layer PDF as highlight annotations with pop-up notes.

    python annotate_pdf.py MANUSCRIPT.pdf LEDGER.json --out-dir OUT [--author NAME]

  * Writes <stem>_annotated.pdf and <stem>_anchoring_report.json; the input PDF is never
    modified (SHA-256 checked) and a pristine copy <stem>_original.pdf is placed in OUT.
  * Anchoring precision is reported per comment:
        exact      - the full quote was located and highlighted
        partial    - only the beginning of the quote was located
        page-note  - quote not found, but the page is known: a sticky note is placed on the page
        unanchored - not placed in the PDF; stays in the ledger only
  * Page numbers are PDF page indices (1 = first physical page), which may differ from the
    journal's printed page numbers. Line numbers are never invented.
  * audience == "editor" comments are never inserted.

Requires PyMuPDF:  pip install pymupdf   (AGPL-3.0 licensed; see README for alternatives).
Scanned (image-only) PDFs have no text layer to search: use the ledger instead.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

try:
    import pymupdf  # type: ignore
except ImportError:
    try:
        import fitz as pymupdf  # type: ignore  # older PyMuPDF
    except ImportError:
        sys.exit("PyMuPDF is required for PDF annotation: pip install pymupdf")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def variants(q: str):
    """Yield (search_string, precision) from strict to loose."""
    base = " ".join(q.split())
    yield base, "exact"
    ascii_q = (base.replace("\u2018", "'").replace("\u2019", "'")
                   .replace("\u201c", '"').replace("\u201d", '"'))
    if ascii_q != base:
        yield ascii_q, "exact"
    words = base.split()
    if len(words) > 8:
        yield " ".join(words[:8]), "partial"   # opening words only
    if len(words) >= 5:                         # line breaks/hyphenation can split a quote
        yield " ".join(words[:4]), "partial"
        yield " ".join(words[-4:]), "partial"


def note_text(c: dict) -> str:
    parts = [f"[{c['id']}] {c['severity']} | {c.get('category', '')} | {c['status']}",
             c["comment"].strip()]
    for k, lab in (("rationale", "Why it matters"), ("required_revision", "Required revision"),
                   ("suggested_correction", "Suggested wording (example, not verified fact)"),
                   ("evidence_needed", "Evidence needed")):
        if c.get(k):
            parts.append(f"{lab}: {c[k].strip()}")
    return "\n\n".join(parts)


COLORS = {"Critical": (1, 0.55, 0.55), "Major": (1, 0.78, 0.4),
          "Minor": (1, 1, 0.45), "Optional": (0.7, 0.9, 1)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("manuscript")
    ap.add_argument("ledger")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--author", default="AI Reviewer (Claude)")
    a = ap.parse_args()
    src = Path(a.manuscript)
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    before = sha256(src)
    ledger = json.loads(Path(a.ledger).read_text(encoding="utf-8"))
    comments = [c for c in ledger["comments"] if c.get("audience", "author") == "author"]
    doc = pymupdf.open(str(src))
    if doc.needs_pass:
        sys.exit("The PDF is encrypted; cannot annotate.")
    n_pages = len(doc)
    report = []
    for c in sorted(comments, key=lambda c: c["id"]):
        q = (c.get("quote") or "").strip()
        hint = c.get("location", {}).get("page")
        pages = [int(hint) - 1] if isinstance(hint, int) or str(hint).isdigit() else []
        pages = [p for p in pages if 0 <= p < n_pages]
        search_pages = pages + [i for i in range(n_pages) if i not in pages]
        placed = None
        if q:
            for v, prec in variants(q):
                for pi in search_pages:
                    rects = doc[pi].search_for(v)
                    if rects:
                        placed = (pi, rects, prec)
                        break
                if placed:
                    break
        if placed:
            pi, rects, prec = placed
            page = doc[pi]           # keep a reference: annotations die with their Page object
            ann = page.add_highlight_annot(rects)
            ann.set_colors(stroke=COLORS.get(c["severity"], (1, 1, 0.5)))
            ann.set_info(title=a.author, content=note_text(c), subject=c["id"])
            ann.update()
            report.append({"id": c["id"], "anchoring": prec, "page": pi + 1})
        elif pages:
            pg = doc[pages[0]]
            pt = pymupdf.Point(pg.rect.x0 + 20, pg.rect.y0 + 30)
            ann = pg.add_text_annot(pt, note_text(c))
            ann.set_info(title=a.author, subject=c["id"])
            ann.update()
            report.append({"id": c["id"], "anchoring": "page-note", "page": pages[0] + 1,
                           "note": "quote not found on that page; sticky note placed"})
        else:
            report.append({"id": c["id"], "anchoring": "unanchored",
                           "note": "not placed in PDF; see ledger"})
    out = out_dir / f"{src.stem}_annotated.pdf"
    doc.save(str(out), garbage=3, deflate=True)
    doc.close()
    shutil.copyfile(src, out_dir / f"{src.stem}_original.pdf")
    if sha256(src) != before:
        sys.exit("FATAL: the original file changed during annotation.")
    (out_dir / f"{src.stem}_anchoring_report.json").write_text(
        json.dumps({"original_sha256": before, "author": a.author, "comments": report},
                   indent=2), encoding="utf-8")
    cnt = Counter(r["anchoring"] for r in report)
    print(f"wrote {out}")
    print("anchoring: " + ", ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
    if cnt.get("unanchored"):
        print("NOTE: unanchored comments are NOT in the PDF:",
              [r["id"] for r in report if r["anchoring"] == "unanchored"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
