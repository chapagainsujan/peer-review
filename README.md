# scientific-peer-review (Claude Skill)

A Claude Skill that reviews scientific manuscripts like an experienced journal referee: it
checks design, statistics, results, interpretation and references; anchors each comment to the
exact passage; explains why the problem matters; proposes defensible fixes; and says plainly what
it could not assess. Built for agricultural, plant, soil, genomics and quantitative-biology
papers, and adaptable to other fields. Output is a **draft for the human reviewer**.

## What it does
- Staged review: intake, completeness check, claim-evidence map, technical review,
  cross-checking, comment drafting, annotation, QC pass, deliverables.
- Design-first statistics (pseudoreplication, repeated measures, split-plot/MET, ordinal
  scores, omics, spatial leakage in remote-sensing ML) rather than a fixed method list.
- Discipline modules activated only when relevant (field/greenhouse, plant pathology, breeding,
  stress physiology, phenotyping/ML, genomics, soil/sustainability, modelling).
- Severity (Critical / Major / Minor / Optional) and certainty (confirmed / probable /
  question / suggestion) on every comment.
- **Native Word comments** for DOCX and **highlight annotations** for text-layer PDFs, with an
  anchoring report and an independent verification script. The original is never modified.
- A comment **ledger** (JSON, Markdown, CSV) that is the single source of truth for the report
  and the annotated file; quotes are checked to exist in the manuscript.
- `stat_checks.py` recomputes P-values, percent changes, expected df, GRIM and CI consistency
  so numerical complaints are verified.
- Author-facing and editor-only comments kept apart.

## Limits (read these)
- It cannot see figures unless you provide images or it can render them; it says so.
- Literature and novelty checks need web search; without it they are reported as not done.
- It does not replace subject-matter expertise: it flags where it is outside its depth.
- Annotation covers DOCX and text-layer PDF. Text boxes, footnotes and equations are not
  anchored; scanned PDFs get a ledger only. Page numbers are reliable for PDFs only; line numbers
  are never guessed.
- A single model run is not an independent panel. Agreement across its "lenses" is not
  independent confirmation.
- Check your journal's policy on uploading manuscripts to AI tools before using this on a
  confidential submission.

## Install
**Claude.ai / Claude app:** zip the folder so that `scientific-peer-review/SKILL.md` is at the top
level of the archive, then Settings -> Capabilities -> Skills -> upload (code execution and file
creation must be enabled for the annotation scripts).
**Claude Code:** copy the folder to `~/.claude/skills/scientific-peer-review/` (personal) or
`.claude/skills/` in a project.
**Dependencies for the scripts:** Python 3.9+; `pip install "python-docx>=1.2" scipy pymupdf`
(`pymupdf` only for PDFs; see NOTICE.md for its AGPL licence). LibreOffice optional for render checks.

## Use
Attach the manuscript (and supplements, journal guidelines if you have them) and ask, for example:
- "Review this manuscript as a referee for a plant-science journal. Give me an annotated Word file,
  the comment ledger and a report."
- "Check only the statistics and design of this paper."
- "Write confidential comments to the editor, keep them separate."
- "I only have the PDF: annotate it with highlights."

Manual script use (from the skill folder):
```
python scripts/extract_manuscript.py paper.docx --out-dir work
python scripts/ledger.py validate ledger.json --map work/paper.map.json
python scripts/annotate_docx.py paper.docx ledger.json --out-dir out
python scripts/verify_annotations.py --original paper.docx --annotated out/paper_annotated.docx \
       --ledger ledger.json --report out/paper_anchoring_report.json --render
python scripts/ledger.py render ledger.json --md out/ledger.md --csv out/ledger.csv --audience author
python scripts/stat_checks.py pvalue --test F --stat 2.91 --df1 3 --df2 20 --reported 0.012
```

## Layout
```
scientific-peer-review/
  SKILL.md                      workflow, rules, tool use (read first)
  references/                   loaded on demand
    review-framework.md         dimensions A-G, consistency checks, recommendation logic
    statistical-review.md       design-first statistics, ML/computational review
    specialist-modules.md       discipline modules and how to derive new ones
    comment-writing-guide.md    comment fields, severity/status, strong vs weak examples
    manuscript-annotation.md    formats, locators, anchoring limits, fallback
    literature-and-integrity.md retrieval discipline, citations, retractions, integrity, confidentiality
    quality-control.md          per-comment QC, negative controls, multi-lens passes
    report-template.md          author report and editor note
  scripts/                      extract_manuscript, ledger, annotate_docx, annotate_pdf,
                                verify_annotations, stat_checks
  tests/test_scripts.py         python -m unittest discover -s tests -v
  examples/                     SYNTHETIC manuscript, ledger, annotated DOCX/PDF, report, answer key
  docs/                         source inventory and synthesis matrix; QA report
```

## Adapting
- New discipline: add a module to `references/specialist-modules.md` (use the five derivation
  questions in section 10) and a row to its activation matrix.
- Journal rules: paste the author guidelines into the chat, or have Claude fetch them; they
  are applied only when supplied or retrievable.
- Severity wording or recommendation vocabulary: edit `comment-writing-guide.md` and
  `review-framework.md` s.8.

## Testing status
Scripts: 15 automated tests pass (see docs/QA_REPORT.md). Workflow: smoke-tested on one
synthetic manuscript written by the skill's author, not independent validation. No test on real
manuscripts, no blind comparison with human reviewers. See docs/QA_REPORT.md for details.

## Licence and attribution
MIT (LICENSE). Design ideas adapted from four MIT-licensed repositories, credited in NOTICE.md.
