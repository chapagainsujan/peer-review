#!/usr/bin/env python3
"""Build the complete peer-review report as ONE Word (.docx) file.

    python build_report_docx.py --ledger ledger.json --report report.json --out review_report.docx
        [--refs refs_audit.json] [--images images_audit.json] [--audience author|editor]

Sections produced (empty ones are omitted):
  1 Manuscript identification and review scope     6 Reference audit (table, with verification status)
  2 Summary of the submission                      7 Figures and tables audit
  3 Overall assessment, strengths, limitations     8 Missing content and recommended additions
  4 Major comments (Critical/Major) in full        9 Statistical and reproducibility assessment
  5 Minor comments and line-by-line corrections   10 What this review could not assess / Recommendation
  Appendix A: complete comment ledger

--audience author (default) leaves out editor-only comments. --audience editor writes a SEPARATE
confidential note containing only the editor-only comments and the confidential summary.

report.json keys (all optional except title):
  title, manuscript_file, journal, date, reviewer_note, depth,
  summary, overall_assessment, strengths[], weaknesses[],
  recommendation {decision, drivers[], would_change, confidence},
  stat_reproducibility, missing_items[{item, section, why}],
  figure_notes[{figure, viewed, note}], reference_verification[{entry, status, note}],
  limitations[], editor_summary
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.section import WD_ORIENT, WD_SECTION
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:
    sys.exit("python-docx >= 1.2 is required: pip install 'python-docx>=1.2'")

EDIT_CATS = {"language", "typo", "terminology", "formatting", "unscientific-language", "writing", "abbreviation"}
SEV_ORDER = {"Critical": 0, "Major": 1, "Minor": 2, "Optional": 3}
SEV_COLOR = {"Critical": "F4B6B6", "Major": "FAD7A0", "Minor": "FCF3CF", "Optional": "D6EAF8"}


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def add_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("AI-assisted draft review - confidential     Page ")
    run.font.size = Pt(8)
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        r = p.add_run()
        r.font.size = Pt(8)
        if tag:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), tag)
            r._r.append(f)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            r._r.append(it)


def set_landscape(section):
    section.orientation = WD_ORIENT.LANDSCAPE
    w, h = section.page_width, section.page_height
    if w < h:
        section.page_width, section.page_height = h, w
    for m in ("left_margin", "right_margin"):
        setattr(section, m, Cm(1.6))
    section.top_margin = section.bottom_margin = Cm(1.6)


def set_portrait(section):
    section.orientation = WD_ORIENT.PORTRAIT
    w, h = section.page_width, section.page_height
    if w > h:
        section.page_width, section.page_height = h, w
    section.left_margin = section.right_margin = Cm(2.2)
    section.top_margin = section.bottom_margin = Cm(2.0)


def table(doc, headers, rows, widths_cm, sev_col=None, font=8.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(font)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(c, "2E4A62")
    repeat_header(t.rows[0])
    for row in rows:
        cells = t.add_row().cells
        no_split(t.rows[-1])
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            run = p.add_run(str(v) if v is not None else "")
            run.font.size = Pt(font)
            if sev_col is not None and i == sev_col and v in SEV_COLOR:
                shade(cells[i], SEV_COLOR[v])
                run.bold = True
    # fixed layout + explicit grid widths: Word and LibreOffice both honour these
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    for i, w in enumerate(widths_cm):
        t.columns[i].width = Cm(w)
    for row in t.rows:
        for i, w in enumerate(widths_cm):
            row.cells[i].width = Cm(w)
    return t


def para(doc, text, bold=False, italic=False, size=10.5, color=None, space_after=4, style=None):
    p = doc.add_paragraph(style=style)
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    p.paragraph_format.space_after = Pt(space_after)
    return p


def labelled(doc, label, text, italic=False):
    if not text:
        return
    p = doc.add_paragraph()
    r = p.add_run(label + " ")
    r.bold = True
    r.font.size = Pt(10)
    r2 = p.add_run(text)
    r2.italic = italic
    r2.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(2)


def bullets(doc, items):
    for it in items or []:
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(it)
        r.font.size = Pt(10)


def loc_str(loc: dict) -> str:
    parts = []
    if loc.get("page"):
        parts.append(f"p. {loc['page']}")
    if loc.get("line"):
        parts.append(f"l. {loc['line']}")
    if loc.get("section"):
        parts.append(str(loc["section"]))
    for k in ("table", "figure"):
        if loc.get(k):
            parts.append(str(loc[k]))
    if loc.get("absent"):
        parts.append("(information absent)")
    return "; ".join(parts) or "-"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--refs")
    ap.add_argument("--images")
    ap.add_argument("--audience", choices=["author", "editor"], default="author")
    a = ap.parse_args()
    led = json.loads(Path(a.ledger).read_text(encoding="utf-8"))
    rep = json.loads(Path(a.report).read_text(encoding="utf-8"))
    refs = json.loads(Path(a.refs).read_text(encoding="utf-8")) if a.refs else None
    imgs = json.loads(Path(a.images).read_text(encoding="utf-8")) if a.images else None
    comments = [c for c in led["comments"] if c.get("audience", "author") == a.audience]
    comments.sort(key=lambda c: (SEV_ORDER.get(c["severity"], 9), c["id"]))

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    sec = doc.sections[0]
    set_portrait(sec)
    add_page_number(sec)

    # ---------------------------------------------------------------- title block
    h = doc.add_heading("Peer-review report" if a.audience == "author" else
                        "Confidential comments to the editor", 0)
    para(doc, rep.get("title", ""), bold=True, size=13)
    para(doc, rep.get("reviewer_note",
         "Draft prepared with AI assistance (scientific-peer-review skill). To be checked, edited and "
         "adopted by the responsible human reviewer."), italic=True, size=9, color="7F7F7F")
    ident = [("Manuscript file", rep.get("manuscript_file", "-")), ("Journal", rep.get("journal", "not supplied")),
             ("Review date", rep.get("date", "-")), ("Review depth", rep.get("depth", "-"))]
    cnt = {s: sum(1 for c in comments if c["severity"] == s) for s in SEV_ORDER}
    ident.append(("Comments", ", ".join(f"{s} {n}" for s, n in cnt.items())))
    table(doc, ["Item", "Value"], ident, [4.0, 12.0], font=9.5)

    if a.audience == "editor":
        para(doc, "", space_after=2)
        para(doc, rep.get("editor_summary", ""), size=10.5)
        doc.add_heading("Confidential observations", 1)
        for c in comments:
            labelled(doc, f"{c['id']} ({c['severity']}, {c['status']}):", c["comment"])
            if c.get("quote"):
                labelled(doc, "Location:", loc_str(c.get("location", {})))
        doc.save(a.out)
        print("wrote", a.out)
        return 0

    # -------------------------------------------------------------------- 2-3 narrative
    if rep.get("summary"):
        doc.add_heading("1. Summary of the submission", 1)
        para(doc, rep["summary"])
    if rep.get("overall_assessment") or rep.get("strengths") or rep.get("weaknesses"):
        doc.add_heading("2. Overall assessment", 1)
        para(doc, rep.get("overall_assessment", ""))
        if rep.get("strengths"):
            para(doc, "Strengths", bold=True)
            bullets(doc, rep["strengths"])
        if rep.get("weaknesses"):
            para(doc, "Main limitations", bold=True)
            bullets(doc, rep["weaknesses"])
    rec = rep.get("recommendation")
    if rec:
        doc.add_heading("3. Recommendation", 1)
        t = table(doc, ["Decision", "Main drivers", "What would change it", "Confidence"],
                  [[rec.get("decision", ""), "; ".join(rec.get("drivers", [])), rec.get("would_change", ""),
                    rec.get("confidence", "")]], [3.0, 6.0, 4.5, 2.6], font=9.5)

    # --------------------------------------------------------------------- major comments
    majors = [c for c in comments if c["severity"] in ("Critical", "Major") and c.get("category") not in EDIT_CATS]
    if majors:
        doc.add_heading("4. Major comments", 1)
        for c in majors:
            p = doc.add_paragraph()
            r = p.add_run(f"{c['id']}  |  {c['severity']}  |  {c.get('category', '')}  |  {c['status']}")
            r.bold = True
            r.font.size = Pt(10.5)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.keep_with_next = True
            labelled(doc, "Location:", loc_str(c.get("location", {})))
            if c.get("quote"):
                labelled(doc, "Original passage:", "\u201c" + c["quote"] + "\u201d", italic=True)
            labelled(doc, "Reviewer comment:", c["comment"])
            labelled(doc, "Scientific rationale:", c.get("rationale"))
            labelled(doc, "Required revision:", c.get("required_revision"))
            labelled(doc, "Suggested correction (example, not verified fact):", c.get("suggested_correction"))
            labelled(doc, "Evidence or verification needed:", c.get("evidence_needed"))

    # ---------------------------------------------------------- landscape: tables from here
    sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
    set_landscape(sec2)
    minors = [c for c in comments if c["severity"] in ("Minor", "Optional") and c.get("category") not in EDIT_CATS
              or (c["severity"] in ("Critical", "Major") and c.get("category") in EDIT_CATS)]
    if minors:
        doc.add_heading("5. Minor and optional comments", 1)
        rows = [[c["id"], c["severity"], c.get("category", ""), loc_str(c.get("location", {})),
                 c.get("quote", ""), c["comment"] + (" " + c["required_revision"] if c.get("required_revision") else ""),
                 c.get("suggested_correction", "")] for c in minors]
        table(doc, ["ID", "Severity", "Category", "Location", "Original passage", "Comment / required revision",
                    "Suggested correction"], rows, [1.4, 1.7, 2.1, 3.3, 5.0, 8.0, 5.2], sev_col=1)
    edits = [c for c in comments if c.get("category") in EDIT_CATS and c not in minors]
    if edits:
        doc.add_heading("6. Line-by-line language, typographical and terminology corrections", 1)
        para(doc, "Every item gives the original wording, the correction and the reason. Page/line numbers "
                  "come from a rendered copy and may differ slightly in Word.", italic=True, size=9)
        rows = [[c["id"], loc_str(c.get("location", {})), c.get("quote", ""), c.get("suggested_correction", ""),
                 c["comment"]] for c in edits]
        table(doc, ["ID", "Location", "Original", "Correction", "Reason"], rows, [1.4, 3.6, 7.0, 7.0, 7.7])

    if refs:
        doc.add_heading("7. Reference audit", 1)
        s = refs["summary"]
        para(doc, f"{s['n_entries']} references ({s['style']} style); {s['with_doi']} with DOI; "
                  f"year range {s.get('year_range', ['-', '-'])[0]}-{s.get('year_range', ['-', '-'])[1]}; "
                  f"{int(100 * s.get('share_last_5_years', 0))}% from the last five years.", size=9.5)
        ver = {str(v["entry"]): v for v in rep.get("reference_verification", [])}
        rows = []
        for f in sorted(refs["findings"], key=lambda f: (f["entry"] is None, f["entry"] or 0)):
            v = ver.get(str(f["entry"]))
            status = (v["status"] + (": " + v["note"] if v.get("note") else "")) if v else (
                "from the text alone" if f["verify"] == "none" else "NOT verified online")
            rows.append([f"[{f['entry']}]" if f["entry"] else "list", f["severity_suggestion"], f["issue"],
                         f["message"], status])
        have = {f["entry"] for f in refs["findings"] if f["entry"]}
        for v in rep.get("reference_verification", []):          # verified entries with no offline finding
            if v["entry"] not in have:
                rows.append([f"[{v['entry']}]", "-", "checked online", v.get("note", ""), v["status"]])
        table(doc, ["Ref", "Severity", "Issue", "Finding", "Verification"], rows, [1.5, 1.8, 3.0, 13.0, 5.5],
              sev_col=1)
    if imgs or rep.get("figure_notes"):
        doc.add_heading("8. Figures and tables audit", 1)
        rows = []
        for r in imgs or []:
            if "error" in r:
                continue
            fl = "; ".join(f["message"] for f in r["flags"]) or "no technical flags"
            rows.append([r.get("image", f"page {r.get('page')}"), f"{r['pixels'][0]}x{r['pixels'][1]} px; "
                         f"{r['printed_inches'][0]}x{r['printed_inches'][1]} in; {r['effective_dpi'][0]} dpi",
                         (r.get("caption") or "")[:90], fl])
        if rows:
            table(doc, ["Image file", "Size / effective resolution", "Caption", "Technical flags"], rows,
                  [3.4, 5.6, 7.5, 9.0])
        if rep.get("figure_notes"):
            para(doc, "", space_after=2)
            table(doc, ["Figure / table", "Viewed?", "Observations"],
                  [[n.get("figure", ""), "yes" if n.get("viewed") else "NO", n.get("note", "")]
                   for n in rep["figure_notes"]], [4.0, 2.0, 19.5])
    if rep.get("missing_items"):
        doc.add_heading("9. Missing content and recommended additions", 1)
        table(doc, ["#", "Missing / recommended addition", "Where", "Why it matters"],
              [[i + 1, m.get("item", ""), m.get("section", ""), m.get("why", "")]
               for i, m in enumerate(rep["missing_items"])], [1.0, 10.0, 4.0, 10.5])

    sec3 = doc.add_section(WD_SECTION.NEW_PAGE)
    set_portrait(sec3)
    if rep.get("stat_reproducibility"):
        doc.add_heading("10. Statistical and reproducibility assessment", 1)
        para(doc, rep["stat_reproducibility"])
    if rep.get("limitations"):
        doc.add_heading("11. What this review could not assess", 1)
        bullets(doc, rep["limitations"])
    # ------------------------------------------------------------------ appendix ledger
    sec4 = doc.add_section(WD_SECTION.NEW_PAGE)
    set_landscape(sec4)
    doc.add_heading("Appendix A. Complete comment ledger", 1)
    rows = [[c["id"], c["severity"], c["status"], c.get("category", ""), loc_str(c.get("location", {})),
             c["comment"][:260] + ("..." if len(c["comment"]) > 260 else "")] for c in comments]
    table(doc, ["ID", "Severity", "Status", "Category", "Location", "Comment (short)"], rows,
          [1.4, 1.8, 2.0, 2.4, 5.6, 12.3], sev_col=1)
    doc.save(a.out)
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
