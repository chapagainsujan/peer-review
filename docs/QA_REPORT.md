# Quality-assurance report

Date of testing: 15-17 October 2026 (v0.1.0 on 15 Oct; v0.2.0 additions on 17 Oct). Environment: Linux container, Python 3, python-docx 1.2,
PyMuPDF (pip), scipy 1.17, LibreOffice (headless), poppler. Microsoft Word was **not** available.

## 1. Summary

| Area | Status |
|---|---|
| Source audit (4 archives) | Done, with stated limits on depth (see SOURCE_INVENTORY_AND_SYNTHESIS.md s.2) |
| Skill structure and frontmatter | Passed `quick_validate.py`; name 22 chars, description 708 chars, compatibility 249 chars; SKILL.md 128 lines |
| Script unit and end-to-end tests | 25 of 25 pass (v0.2.0) |
| Functional review test on a synthetic manuscript | Completed; **not independent** (see s.4) |
| Test on real manuscripts | **Not done** |
| Blind comparison with human reviewers / baseline Claude | **Not done** |
| Description-trigger evaluation | **Not done** |
| Test in Microsoft Word | **Not done** |

Overall: the tooling is tested; the review *quality* is only smoke-tested. Treat the skill as a
well-engineered draft that still needs field testing on real manuscripts.

## 2. Structural tests

- `SKILL.md` is at the root of the skill directory; frontmatter validated by the skill-creator
  validator.
- Specification check: name <= 64 chars, matches directory, lowercase-hyphen; description <= 1024;
  compatibility <= 500; body well under 500 lines; references are one level deep from SKILL.md.
  **Caveat:** I confirmed these constraints from reproductions of the open Agent Skills
  specification found by web search (aggregator pages), not from the canonical repository. Re-check
  against the current official documentation before publishing.
- Cross-reference check: every `references/*`, `scripts/*`, `examples/*`, `docs/*` path cited in
  SKILL.md, README.md and the references exists (0 broken).
- Duplicated or contradictory instructions: reviewed by reading; the severity definitions
  live in `comment-writing-guide.md` and are summarised (not redefined) in SKILL.md.

## 3. Script tests (`python -m unittest discover -s tests -v`)

15 tests, all pass: P-value recomputation (planted error caught; correct and inequality values
accepted; rounding tolerance), GRIM, expected df for CRD/RCBD/Latin/split-plot, CLI exit codes,
extraction block IDs, ledger validation (invented quote rejected; invented number warned; missing
rationale rejected; editor notes exempt), DOCX annotation (exact anchoring across split runs
with curly-vs-straight quotes, table cells, section fallback for absence comments, editor
comment excluded, original byte-identical), verification (passes on good file, **fails on a
deliberately tampered file**), LibreOffice render, and a PDF round trip (exact highlight, page-note
fallback, editor exclusion, verification).

### Bugs found by testing and fixed
1. PDF annotator lost annotations because the PyMuPDF page object was garbage-collected.
2. Extractor used an XPath namespace argument unsupported by python-docx elements.
3. "Invented number" check matched substrings ("31" inside "0.31"); now whole numeric tokens.
4. Ledger validator wrongly demanded quote/rationale from free-form editor notes.
5. PDF annotator could not anchor a quote broken by hyphenation at a line end; added looser
   fallback searches (reported as `partial`).

## 4. Functional review test (synthetic sample)

Material: `examples/sample_manuscript.docx` (synthetic; 13 planted flaws, 6 negative-control
passages; answer key in `examples/sample_answer_key.md`).

| Check from the brief | Result |
|---|---|
| 1 Identify a genuine methodological concern without inventing one | C-001 (bench confounding) and C-002 (repeated measures) found; ledger quotes validated against the manuscript |
| 2 Statistical vs practical significance | Addressed in C-003 (conclusion flips at alpha 0.05) and C-013 (effect sizes/CI); weakly exercised |
| 3 Inconsistencies between methods and results | Abstract vs table (C-004), P vs F (C-003), df vs design (C-002), text vs means (C-010): all found, each verified with `stat_checks.py` |
| 4 Precise, actionable comments | 13 author comments with quote, rationale, revision |
| 5 Improved wording without fabricating | Example wordings contain no invented numbers (placeholders used); invented-number check passes |
| 6 Reasonable severity | Matches the planted levels (author-assigned) |
| 7 No duplication between report and ledger | Report generated around ledger IDs; near-duplicate check passes |
| 8 Limits that cannot be resolved from the evidence | C-001/C-014 state it cannot be repaired by reanalysis |
| 9 Coherent recommendation | Reject / resubmit, driver and "what would change it" stated |
| 10 Author vs editor separation | C-014 is editor-only: verified absent from annotated DOCX and PDF |
| Negative controls | 0 comments on the 6 sound passages; verified visually in the annotated PDF |

Annotation results: DOCX 13/13 exact anchors, verification ALL CHECKS PASSED including a
LibreOffice render; margin comments inspected visually. PDF (rendered from the same DOCX):
12 exact + 1 partial anchor, verification passed; highlights inspected visually.

### Why this is not validation
- The same person wrote the flaws, the key and the review. A reviewer who knows the answer is
  not a test of discovery. The review was made by following the skill's own method, but the
  skill has **not** been run by a fresh model session without knowledge of the key.
- One short, simple manuscript. Real papers have supplements, figures, multi-column PDFs, tracked
  changes, long reference lists and subtler flaws.
- The negative-control rule is only meaningfully tested if the skill is run on genuinely sound
  papers and its false-positive rate is measured.

## 5. Known limitations and unresolved issues

1. **Microsoft Word compatibility unverified.** python-docx writes standard `comments.xml`;
   it opens in python-docx and LibreOffice. Word should read it, but I did not test Word
   (Word's "reply" threading and `commentsExtended` parts are not produced).
2. **Figures and images are not read** by any script. The skill instructs to render and view
   them or to state they were not assessed.
3. **Not anchored:** text boxes, footnotes/endnotes, equations; runs with tabs/breaks/images are
   anchored whole; paragraphs with tracked changes/hyperlinks may fall back to paragraph level.
4. **PDF:** tested only on a clean single-column LibreOffice-generated PDF. Two-column journal
   layouts, ligatures, hyphenation and scanned PDFs are expected to need fallbacks (reported as
   `partial`, `page-note` or `unanchored`). PyMuPDF is AGPL.
5. **`stat_checks.py` assumptions:** expected-df formulas are for balanced designs; p-value
   recomputation covers t, F, chi-square, z and r only; GRIM applies to integer-valued data.
6. **Literature checks** depend on web search being available; the search procedure was
   not exercised in testing (no manuscript with a novelty claim).
7. **Description triggering** (will Claude invoke the skill when it should, and not when it should
   not) was not evaluated; the skill-creator's description-optimisation loop needs the `claude` CLI.
8. **Multi-lens / subagent mode** is described but untested.
9. Specialist modules reflect general domain knowledge written for this skill; they have not been
   reviewed by domain experts, and may miss field-specific conventions.
10. The Chinese prompt originals in one source and parts of several sources were skimmed rather than
    read line by line (SOURCE_INVENTORY s.2).

## 6. Recommended next steps
1. Run the skill, in fresh sessions, on 5-10 real manuscripts (including at least two sound,
   published papers and two with known post-publication corrections) and compare with expert reviews.
2. Measure false-positive rate on sound papers and agreement of severity with experts.
3. Open annotated DOCX files in Microsoft Word and Google Docs; test two-column PDFs and tracked-change files.
4. Run the description-optimisation loop in Claude Code.
5. Have a plant scientist, a statistician and a bioinformatician review the specialist modules.


---

## 7. v0.2.0 addendum: exhaustive line-by-line mode

**Why:** v0.1.0 deliberately avoided line-level language, typo and reference-format comments ("fix patterns, not
every instance") and treated the citation/style prompts in the supplied repositories as cosmetic. That was a
design error for a full review. v0.2.0 adds an exhaustive mode (default for full reviews) and the tools to support it.

**Added:** `references/line-by-line-audit.md`, `reference-audit.md`, `figure-table-audit.md`,
`completeness-checklist.md`; scripts `lint_text.py`, `audit_references.py`, `image_audit.py`,
`line_locator.py`, `build_report_docx.py`; ledger categories for language, typo, terminology,
unscientific wording, references, citations, abbreviations, completeness; Word report with tables for
line corrections, reference audit, figure audit and missing content.

**Automated tests:** 10 new tests (linter planted problems, negative control with clean text, number
text-vs-table near-miss, equation tolerance, reference completeness and cross-checks, effective dpi,
Word report content and editor/author separation, run-splitting regression, page/line locator).

**Bugs found and fixed in v0.2.0 development**
1. Glued-heading rule fired on genuine headings such as "2.5.1 Estimation..." (regex fixed).
2. Narrative-citation check treated "Himalayan Superfood [20]" as an author name (now requires an author-like form
   or a surname that exists in the list).
3. Table-row numbers matched as "near" table values (now requires a decimal table value; coordinates skipped).
4. Chapter entries starting "In ..." were not classified; publisher check was too lenient (fixed).
5. Duplicate findings per entry (de-duplicated).
6. Annotator could not split runs beginning with `w:lastRenderedPageBreak` and mislabelled the resulting
   over-wide anchors "exact"; now splits them, and labels any residual case `run-expanded` (found by the
   independent verifier).
7. Reference classification missed "Journal. 2020:55-60" entries without DOI (volume missing), then over-reached
   to organisational reports; refined with a journal-like-container test.
8. Word report table widths were ignored (55-page report); fixed with fixed layout and grid widths (29 pages).
9. Ledger validator demanded corrections for global formatting entries and rejected free-form editor notes (relaxed).

**Functional test on a real sample manuscript supplied by the user for skill testing**
(not included in this package; unpublished; 37,405 characters, 5 tables, 2 figures, 47 references).
Workflow run end to end: extraction; linter (152 candidates, all dispositioned); reference audit (27 offline
findings; 2 entries verified online); image audit and viewing of both figures; recomputation of all ten rows of
the genetic-parameter table from the ANOVA table; 143-comment ledger (33 Major, 107 Minor, 3 Optional, 2 of which
editor-only), all quotes validated against the manuscript; page/line numbers; native Word comments
(140 exact, 1 paragraph-level, 2 editor-only not inserted); independent verification passed (author text identical,
original unchanged, LibreOffice renders); 29-page Word report and a separate editor note, inspected visually.
Findings the tools made verifiable included: an ANOVA F ratio whose P-value contradicts the table asterisks,
a genetic-parameter row that cannot be reproduced from the ANOVA, a 100-fold scaling error in two variance
entries, text-versus-table number discrepancies, a length reported in grams, a count reported in cm,
contradictory funding statements, and incomplete references (two confirmed against journal records).

**Limits of that test (important)**
- One manuscript, one reviewer (the skill's author, using the skill's own method): not independent validation,
  no measured false-positive rate, no comparison with human referee reports.
- Several comments rest on the reviewer's domain knowledge (e.g. the agro-ecology of Nepal's mid-hills,
  fodder value of finger millet straw) and are marked probable/question; they were not verified against sources.
- Only 2 of 47 references were checked online; the rest are marked "not verified".
- Supplementary files were not available.
- Page/line numbers come from a LibreOffice rendering and may differ in Word.
- The tool cannot judge legibility or correctness of figure content; that relied on viewing previews at reduced
  resolution (marked probable where small text mattered).
- The review was not checked by a human subject-matter expert.
