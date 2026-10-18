# Manuscript annotation

Read at Stage 7 (annotation). Core rule: **never claim comments were inserted into a document
unless a script or tool actually did it and `verify_annotations.py` passed.** When insertion is
not possible, deliver the ledger and say so.

## Contents
1. What to deliver
2. Format decision table
3. Standard workflow (DOCX and PDF)
4. Locators: IDs, pages, lines
5. Anchoring precision and what to tell the user
6. DOCX specifics and limits
7. PDF specifics and limits
8. Markdown / text / other formats
9. Fallback: ledger-only delivery
10. Tracked changes and editing the author's text

## 1. What to deliver

| File | Purpose |
|---|---|
| `<stem>_original.<ext>` | Byte-identical pristine copy |
| `<stem>_annotated.<ext>` | Same document with review comments |
| `<stem>_ledger.json` / `.md` / `.csv` | Every comment with ID, severity, location, quote, rationale, revision (the single source of truth) |
| `<stem>_anchoring_report.json` | How each comment was anchored (exact / run-expanded / partial / paragraph / section / unanchored) |
| `<stem>_review_report.md` (or .docx on request) | The structured peer-review report (`report-template.md`) |

Generate the report's comment list **from the ledger** so the annotated file, ledger and report
cannot disagree.

## 2. Format decision table

| Input | Annotate how | Tool |
|---|---|---|
| `.docx` | Native Word comments anchored to quoted text | `scripts/annotate_docx.py` (python-docx >= 1.2) |
| `.pdf` with text layer | Highlights with pop-up notes | `scripts/annotate_pdf.py` (PyMuPDF) |
| `.pdf` scanned | No text layer: ledger only (OCR is out of scope) | - |
| `.doc` / `.rtf` / `.odt` | Convert first: `soffice --headless --convert-to docx file` then treat as DOCX; say the review is on a converted copy | LibreOffice |
| `.tex` / `.md` / `.txt` | Deliver ledger with line numbers; optionally a copy with `% REVIEW[C-001]: ...` / `<!-- C-001 -->` markers *only if requested* | manual |
| Google Docs / Word online link | Cannot be annotated from here unless a connector with comment-write access is present; use ledger; say so | - |

If code execution or file access is not available in this session, do not pretend: produce
the ledger/report in chat or as text, and explain how to apply comments manually.

## 3. Standard workflow

1. Copy inputs to a working directory. Do not edit in place.
2. `python scripts/extract_manuscript.py paper.docx --out-dir work/` -> block map with IDs
   (`P12`, `T1.r2c3`, `pg3`) and warnings (tracked changes, existing comments, text boxes,
   equations, figures not read, hidden text, injection-like text).
3. Read `work/paper.blocks.txt` and the whole manuscript; draft comments in the ledger JSON.
   Copy quotes **verbatim** from the block text; quote only what is needed.
4. `python scripts/ledger.py validate ledger.json --map work/paper.map.json`
   Fix every ERROR (e.g. a quote that is not in the manuscript). Read WARNs.
5. `python scripts/annotate_docx.py paper.docx ledger.json --out-dir out/`
   (or `annotate_pdf.py`).
6. `python scripts/verify_annotations.py --original paper.docx --annotated out/paper_annotated.docx --ledger ledger.json --report out/paper_anchoring_report.json --render`
   Must end with `ALL CHECKS PASSED`. If not, fix and rerun; do not deliver a failing file.
6b. **Page and line numbers** (before annotating, so they appear in the comments and report):
   `python scripts/line_locator.py paper.docx ledger.json --out ledger.located.json` - uses a LibreOffice
   rendering where the document's own line numbering is drawn; the numbers are exact for that rendering and may
   differ slightly in Word (the script records `line_source`; say so in the report). Tables have no line numbers.
7. `python scripts/ledger.py render ledger.json --md out/paper_ledger.md --csv out/paper_ledger.csv --audience author`
7b. **Word report**: `python scripts/build_report_docx.py --ledger ledger.json --report report.json --refs work/refs_audit.json --images work/images_audit.json --out out/paper_review_report.docx`
   (and `--audience editor` for the confidential note). Render it to PDF and look at a page or two.
8. Visually spot-check: convert the annotated DOCX to PDF (LibreOffice) and look at a page or
   two if tools allow. Say what you checked.

Order of operations matters: finish and QC the ledger (`quality-control.md`) **before**
annotating, so you annotate once.

## 4. Locators: IDs, pages, lines

- **Block IDs** from the extractor are always reliable references into *that* extraction and
  are good for internal use. Authors cannot see them; they need a quote and a section.
- **Quote** every comment's target passage verbatim (short). The quote is the primary locator
  for authors and for the anchoring script.
- **Section/heading** is always available.
- **Page numbers**: reliable for PDFs (physical page index; may differ from printed page
  numbers if the PDF has a title page offset). **Not reliable for DOCX** by themselves: pagination depends on
  fonts and Word version. `line_locator.py` obtains them from a rendered copy; label them "in the rendered copy".
- **Line numbers**: use only line numbers read from a rendered copy (`line_locator.py`), printed in the
  supplied PDF, or true line numbers of a text file. Never compute or guess them. If the
  manuscript has line numbers but you cannot read them from the file, quote the passage and name
  the section instead, and say line numbers were not available.
- If pagination changes (you converted or re-saved), distinguish "original page" from "page
  in the annotated copy" in the report.

## 5. Anchoring precision and what to tell the user

`exact` = only the quoted words are anchored. `run-expanded` = the quote was found but a run holding
tabs, breaks, fields or images could not be split safely, so the anchor is a little wider (the
verifier accepts this only when it is reported). Always report the counts per precision.

Report the anchoring summary from the report file, e.g. "18 of 21 comments are attached to the
exact quoted words, 2 to a whole paragraph, 1 is not in the document (ledger only)". Do not
say "all comments inserted" if any is `unanchored`. Editor-only comments are never inserted.

## 6. DOCX specifics and limits

- Comments are native Word comments (`comments.xml`), author "AI Reviewer (Claude)" by default
  (change with `--author`; transparency about AI authorship is intended).
- Author text, tables, figures, equations, references and formatting are untouched; runs are
  split only at quote boundaries, and the verifier checks that visible text is identical.
- Not handled: text boxes, footnotes/endnotes, text inside equations, content controls; runs
  containing tabs/breaks/images are anchored whole. Those comments fall back to the
  paragraph or heading and are reported as such.
- Existing comments and tracked changes in the manuscript are preserved. Paragraphs containing
  tracked changes or hyperlinks may anchor at paragraph level.
- Figures are not read by the scripts. To judge a figure, render the document/PDF to an image
  and view it; if you cannot, say you did not assess the figure itself.
- Optional extra check (if available in the environment): validate the package XML against
  the OOXML schema with the environment's docx validator.

## 7. PDF specifics and limits

- Highlights + pop-up notes use PyMuPDF text search; two-column layouts, hyphenation, ligatures
  and special characters can defeat exact matches (the script tries looser variants and then
  falls back to a page note, and reports which).
- Page numbers are physical. Some PDF viewers show pop-up notes differently; the highlight
  colour encodes severity (red Critical, orange Major, yellow Minor, blue Optional).
- PyMuPDF is AGPL-3.0: fine for personal/internal use; see the README for licensing
  considerations before redistributing it inside a product.

## 8. Markdown / text / other

The extractor records true line numbers for `.md`/`.txt`. Provide the ledger with those line
numbers. If asked for an annotated copy, insert HTML comments (`<!-- [C-001] ... -->`) on the
line **above** the target passage in a copy named `*_annotated.md`; never alter the original.

## 9. Fallback: ledger-only delivery

When annotation is impossible or partly failed: state the limitation in one sentence, deliver
the ledger (Markdown table + CSV), include exact quotes and section/page references, and tell
the user how to apply them (e.g. add a Word comment on the quoted text). Never label a
ledger-only delivery as an annotated manuscript.

## 10. Tracked changes and editing the author's text

The default is to **comment, not edit**. Do not insert tracked changes or replace text unless
the user explicitly asks for suggested edits (e.g. language editing). If asked, make them
tracked changes only, with a different author name, and keep scientific-content comments
separate from language edits. Suggested replacement wording belongs *in the comment*
(clearly marked as an example), not in the author's text.
