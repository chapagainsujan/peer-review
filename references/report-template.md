# Review report (Word) and editor note

Read at the final stage. The complete review is delivered as **one Word file** built by
`scripts/build_report_docx.py` from three inputs: the ledger (all comments), `report.json` (the
narrative parts you write), and the audit outputs (`refs_audit.json`, `images_audit.json`). Do not
retype comments: the report is generated from the ledger so the annotated manuscript, the ledger and
the report cannot disagree.

## 1. Write `report.json`

```json
{
  "title": "Manuscript title",
  "manuscript_file": "paper.docx",
  "journal": "not supplied",
  "date": "2026-10-16",
  "depth": "Exhaustive: 152 paragraphs, 5 tables (561 cells), 2 figures, 47 references read",
  "summary": "Neutral 1-2 paragraphs: question, design (experimental unit, replication), principal findings, claimed contribution.",
  "overall_assessment": "Importance, fit, the one or two problems that matter most.",
  "strengths": ["specific, real strengths"],
  "weaknesses": ["main limitations"],
  "recommendation": {
    "decision": "Major revision",
    "drivers": ["finding 1 (C-004)", "finding 2 (C-010)"],
    "would_change": "what evidence would change the decision",
    "confidence": "3/5: no supplement; 12 references not verified online"
  },
  "stat_reproducibility": "Design, analysis vs design, assumptions, multiplicity, effect sizes, data/code availability, checks run.",
  "missing_items": [{"item": "Seed rate, fertiliser rates, irrigation", "section": "2.3 Experimental design", "why": "needed to repeat the experiment"}],
  "figure_notes": [{"figure": "Fig. 1", "viewed": true, "note": "what you saw: axes, units, colours, caption match"}],
  "reference_verification": [{"entry": 16, "status": "differs", "note": "record at <URL> gives vol. 12, pp. 3355-3360"}],
  "limitations": ["what could not be assessed and the consequence"],
  "editor_summary": "Used only with --audience editor"
}
```

## 2. Build

```
python scripts/build_report_docx.py --ledger ledger.json --report report.json \
    --refs work/refs_audit.json --images work/images_audit.json --out out/paper_review_report.docx
python scripts/build_report_docx.py --ledger ledger.json --report report.json \
    --audience editor --out out/paper_editor_note.docx        # only if requested/appropriate
```
Then convert to PDF with LibreOffice and look at a few pages (tables not truncated, landscape pages fine).

## 3. What the Word report contains

1. Identification and review scope (file, journal, date, depth, comment counts)
2. Summary of the submission
3. Overall assessment: strengths, main limitations
4. Recommendation: decision, drivers, what would change it, confidence
5. Major comments (Critical/Major): location, quote, comment, rationale, required revision, suggested correction, evidence needed
6. Minor and optional comments (table: ID, severity, category, location with page/line, original, comment, correction)
7. **Line-by-line corrections** (table: original, correction, reason) for language, typo, terminology, formatting, unscientific wording
8. **Reference audit** (table: entry, severity, issue, finding, verification status)
9. **Figures and tables audit** (technical image flags + what you saw)
10. **Missing content and recommended additions**
11. Statistical and reproducibility assessment
12. What this review could not assess (coverage statement)
Appendix A: complete ledger

## 4. Rules

- Every major comment states why it matters and what would address it.
- Keep confirmed errors, probable problems, questions and suggestions distinct (the `status` column).
- Author-facing report excludes editor-only comments; they go only in the separate editor note.
- The report states coverage and what was **not** checked (figures not viewed, references not verified
  online, supplement not supplied, journal rules not applied).
- Include the draft-for-human-reviewer note (added automatically in the title block).
- If a fatal limitation cannot be remedied with the existing data, say so in the assessment and the
  recommendation, and state the narrower claim the data can support.
