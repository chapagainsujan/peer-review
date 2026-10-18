#!/usr/bin/env python3
"""Add real page and line numbers to ledger comments by locating each quote in a rendered copy.

    python line_locator.py MANUSCRIPT.docx LEDGER.json --out LEDGER.located.json

Why: journals review with line numbers; authors expect "page 4, lines 112-114". DOCX files have no
fixed pagination, so the numbers are taken from a RENDERED copy (LibreOffice -> PDF) in which the
document's own line numbering (w:lnNumType) is drawn in the margin. For a PDF manuscript pass the
PDF itself: printed margin numbers are read directly.

Honest limits (recorded in each comment as location.line_source):
  * Word and LibreOffice paginate slightly differently. The numbers are exact for the rendered
    copy, and usually identical or off by a few lines/one page in Word. Say so in the report.
  * If the document has no line numbering, only the page number is added.
  * Lines inside tables are not numbered by Word; those comments get a page only.
  * A quote that cannot be found in the rendering is left without page/line (never guessed).

Requires PyMuPDF and (for DOCX) LibreOffice (soffice).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    import pymupdf  # type: ignore
except ImportError:
    sys.exit("PyMuPDF is required: pip install pymupdf")


def render(docx: Path, outdir: Path) -> Path:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("LibreOffice (soffice) not found; cannot render the DOCX. Provide a PDF instead.")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(docx)],
                   capture_output=True, timeout=240)
    pdf = outdir / (docx.stem + ".pdf")
    if not pdf.exists():
        sys.exit("Rendering failed.")
    return pdf


def margin_numbers(page) -> list[tuple[float, int]]:
    words = page.get_text("words")
    text_words = [w for w in words if not re.fullmatch(r"\d{1,4}", w[4])]
    if not text_words:
        return []
    left = min(w[0] for w in text_words)
    out = []
    for w in words:
        if re.fullmatch(r"\d{1,4}", w[4]) and w[2] < left - 1:
            out.append(((w[1] + w[3]) / 2, int(w[4])))
    return out


def line_of(rect, nums) -> int | None:
    yc = (rect.y0 + rect.y1) / 2
    best = None
    for y, n in nums:
        d = abs(y - yc)
        if d < 5 and (best is None or d < best[0]):
            best = (d, n)
    return best[1] if best else None


def variants(q: str):
    base = " ".join(q.split())
    yield base
    asc = base.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    if asc != base:
        yield asc
    w = base.split()
    if len(w) > 8:
        yield " ".join(w[:8])
    if len(w) >= 5:
        yield " ".join(w[:4])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("manuscript")
    ap.add_argument("ledger")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src = Path(a.manuscript)
    led = json.loads(Path(a.ledger).read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp())
    try:
        if src.suffix.lower() == ".docx":
            has_ln = b"lnNumType" in zipfile.ZipFile(src).read("word/document.xml")
            pdf = render(src, tmp)
            source = "LibreOffice rendering of the DOCX (Word pagination/line numbers may differ slightly)"
        else:
            has_ln = True
            pdf = src
            source = "printed in the supplied PDF"
        doc = pymupdf.open(str(pdf))
        pages = [(p, margin_numbers(p)) for p in doc]
        placed = page_only = missing = 0
        for c in led["comments"]:
            q = (c.get("quote") or "").strip()
            if not q:
                continue
            hit = None
            for v in variants(q):
                for p, nums in pages:
                    rects = p.search_for(v)
                    if rects:
                        hit = (p, rects, nums)
                        break
                if hit:
                    break
            if not hit:
                missing += 1
                continue
            p, rects, nums = hit
            loc = c.setdefault("location", {})
            loc["page"] = p.number + 1
            if has_ln:
                l1, l2 = line_of(rects[0], nums), line_of(rects[-1], nums)
                if l1:
                    loc["line"] = f"{l1}" if (not l2 or l1 == l2) else f"{l1}-{l2}"
            loc["line_source"] = source
            if loc.get("line"):
                placed += 1
            else:
                page_only += 1
        Path(a.out).write_text(json.dumps(led, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"page+line for {placed} comment(s); page only for {page_only}; not found {missing}")
        print("Source of numbers:", source)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
