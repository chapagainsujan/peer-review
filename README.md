<div align="center">

# 🔬 scientific-peer-review

### An exhaustive, evidence-grounded Claude Skill for scientific manuscript peer review
#### Reviews the science **and** every line: typos, grammar, unscientific wording, numbers, figures and references

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](#changelog)
[![Tests](https://img.shields.io/badge/tests-25%20passing-brightgreen.svg)](#testing)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](#requirements)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-8A2BE2.svg)](#installation)
[![Status](https://img.shields.io/badge/status-early%20release-orange.svg)](#testing-status-and-known-limitations)

**Author: Sujan Chapagain**

[Overview](#overview) •
[Features](#features) •
[Installation](#installation) •
[Quick start](#quick-start) •
[Scripts](#script-reference) •
[Testing](#testing) •
[Limitations](#testing-status-and-known-limitations) •
[Credits](#credits-and-acknowledgements)

</div>

---


## Overview

**scientific-peer-review** is a [Claude Skill](https://docs.claude.com) that makes Claude review a
scientific manuscript the way an experienced journal referee would. It evaluates scientific
validity, finds substantive weaknesses, attaches each comment to the **actual passage** of the
manuscript, explains **why** the problem matters, and proposes **defensible** fixes, while stating
plainly what it could **not** assess.

It was designed for **agricultural, plant, soil, genomics and quantitative-biology research**
(field and greenhouse trials, plant pathology, breeding, stress physiology, phenotyping, remote
sensing and machine learning, omics), and is adaptable to any other discipline.

It reads **every paragraph, table cell, caption and reference**, reports each confirmed error with the
exact original wording, a correction and a page/line location, audits the reference list entry by entry
(missing volume, pages, DOI, publisher), checks image quality, lists what is missing from the manuscript, and
delivers the result as **Word files** (annotated manuscript + one complete review report).

> **Important:** the output is a **draft for the responsible human reviewer**. It is not a
> final verdict, and it does not replace subject-matter expertise.

### Why this skill exists

Most AI "paper reviewers" produce a generic report that is not tied to the text, may invent
problems or references, and rarely says what it could not check. This skill is built around the
opposite principles:

| Principle | What it means in practice |
|---|---|
| **Verify before asserting** | Quotes must exist in the manuscript; numbers are recomputed with a tool |
| **Label certainty** | Every comment is *confirmed*, *probable*, a *question*, or a *suggestion* |
| **Design before method** | The experimental unit and replication are reconstructed before judging the statistics |
| **Proportion over volume** | No minimum number of criticisms; sound papers get short reviews |
| **Honest about limits** | A "what this review could not assess" section is part of the report |
| **No fabricated actions** | Comments are "in the document" only if a script placed them *and* verification passed |

---

## Features

### Exhaustive line-by-line audit (new in v0.2.0)
-  **Every paragraph, sentence, table cell and caption** is read; every confirmed error is its own comment
  with *original text → correction → reason*
-  Typos, grammar, punctuation, spacing, hyphenation, US/UK mixing, garbled symbols, glued headings
-  **Unscientific and promotional wording** (e.g. "immense", "superfood", "obviously", "proves"), vague
  quantities, absolute statements, causal claims on correlational data, template phrases and connector overuse
-  **Numbers and units**: text vs table mismatches (e.g. 12.93 vs 12.94), wrong units (a length in grams),
  decimal-place inconsistency, P-value notation, undefined or conflicting abbreviations
-  **Cross-references**: wrong table numbers, uncited tables/figures, supplement numbering conflicts
-  Candidate findings come from `lint_text.py`; **every candidate is read and confirmed or rejected**

### Reference and citation audit (new in v0.2.0)
-  Each entry checked for authors, year, title, journal, **volume, issue, pages/article number, DOI**; book
  chapters for editors/publisher/pages; reports for publisher/URL
-  In-text ↔ list cross-check, including "Author et al. [n]" versus entry *n*, uncited entries, out-of-order citation
-  Odd punctuation, inconsistent DOI/journal-abbreviation style, duplicates, self-citation share, reference age
-  Procedure for **verifying entries online** (publisher/PubMed/Crossref) with the source recorded; anything not
  verified is labelled "NOT verified online". Nothing is "corrected" from memory

### Figures, images and tables (new in v0.2.0)
-  Effective resolution (dpi at printed size), format, colour mode, caption and alt text for every image
-  Previews are saved so each figure is **actually viewed** (axes, units, dual axes, colour-vision safety, caption vs
  axis mismatch, text-vs-figure description)
-  Table logic checks (e.g. recompute h², GCV, GA from the ANOVA table)

### Completeness check (new in v0.2.0)
-  Lists what is **missing** and should be added: management details, sampling, formulas, software, model and
  assumptions, limitations, data availability, declarations consistency

### Review capabilities
-  Nine-stage review workflow (intake → completeness → first pass → technical review →
  cross-check → comment drafting → annotation → QC → deliverables)
-  Claim–evidence map built before any criticism is written
-  Dimensions covered: contribution and novelty, design and methods, statistics and computation,
  results/tables/figures, discussion and interpretation, references and integrity, structure
  and reporting
-  Design-first statistical review: pseudoreplication, repeated measures, blocking, split-plot,
  multi-environment trials, counts/proportions/ordinal scores, multiple comparisons, effect sizes,
  data leakage and spatial validation in machine learning
-  Internal-consistency pass: abstract ↔ results ↔ conclusions, methods ↔ results, text ↔ tables,
  units, degrees of freedom versus design
-  Fatal-versus-fixable reasoning and a transparent recommendation logic
  (Accept / Minor / Major / Reject)

### Specialist modules (activated only when relevant)
Field and greenhouse experiments · Plant pathology · Plant breeding and quantitative genetics ·
Crop physiology and abiotic stress · Phenotyping, UAV/remote sensing and ML · Genomics,
transcriptomics and bioinformatics · Soil science and sustainable agriculture · Statistical
modelling and reproducible computing · A method for deriving a module for an unfamiliar field

### Manuscript annotation
-  **Native Word comments** for `.docx`, anchored to the exact quoted words
-  **Highlight annotations with pop-up notes** for text-layer `.pdf` (colour = severity)
-  Original file **never modified**; a byte-identical pristine copy is saved
-  **Anchoring report** stating how each comment was placed
  (`exact`, `partial`, `paragraph`, `section`, `page-note`, `unanchored`)
-  Independent **verification script** (author text unchanged, anchors match quotes, no
  editor-only comment leaked into the manuscript, optional render test)
-  Page numbers only where reliable; line numbers are **never guessed**

### Integrity safeguards
-  Ledger validator **rejects quotes that are not in the manuscript**
-  Warns when suggested wording contains **numbers not present** in the manuscript
-  Detects near-duplicate comments and severity/certainty mismatches
-  Flags hidden text and **instructions embedded in the manuscript** aimed at AI reviewers
  (treated as untrusted data, never followed)
-  Author-facing and **editor-only (confidential)** comments are kept separate

### Word deliverables (new in v0.2.0)
-  `*_annotated.docx` with native comments (page/line from `line_locator.py`)
-  `*_review_report.docx`: summary, assessment, recommendation, major comments, minor comments,
  **line-by-line corrections table**, **reference audit table**, **figure/table audit**, **missing-content table**,
  statistical and reproducibility assessment, limitations, ledger appendix
-  Separate confidential `*_editor_note.docx`

### Statistics checker
`stat_checks.py` verifies numerical complaints before they are written: recompute a P-value from a
test statistic and degrees of freedom (rounding-aware), percent change, expected degrees of freedom
for balanced designs (CRD, RCBD, Latin square, split-plot), the GRIM test for integer-valued
means, and confidence-interval consistency.

---

## How it works

```
 ┌────────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────────────┐
 │ 1 Intake   │ → │ 2 Complete-  │ → │ 3 First     │ → │ 4 Technical      │
 │            │   │   ness check │   │   pass      │   │   review         │
 └────────────┘   └──────────────┘   └─────────────┘   └──────────────────┘
                                                                │
 ┌────────────┐   ┌──────────────┐   ┌─────────────┐   ┌────────▼─────────┐
 │ 9 Deliver  │ ← │ 8 QC pass    │ ← │ 7 Annotate  │ ← │ 5 Cross-check    │
 │            │   │ (negatives)  │   │ (DOCX/PDF)  │   │ 6 Draft comments │
 └────────────┘   └──────────────┘   └─────────────┘   └──────────────────┘
```

Detailed review guidance is split into reference files that Claude loads **only when needed**
(progressive disclosure), keeping the core `SKILL.md` short.

**Deliverables for a full review**

| File | Purpose |
|---|---|
| `<name>_annotated.docx` / `.pdf` | Manuscript with review comments |
| `<name>_original.docx` / `.pdf` | Byte-identical pristine copy |
| `<name>_ledger.json` / `.md` / `.csv` | Every comment with ID, severity, location, quote, rationale, revision |
| `<name>_anchoring_report.json` | How each comment was anchored |
| `<name>_review_report.md` | Structured peer-review report |
| Confidential editor note | Only if requested; kept separate from author-facing content |

---

## Requirements

| Component | Needed for | Notes |
|---|---|---|
| Claude with **code execution and file creation** (Claude.ai) or **Claude Code** | Running scripts and producing files | Chat-only mode still works, delivering the ledger as text |
| Python **3.9+** | All scripts | |
| `Pillow` | `image_audit.py` | |
| `pyspellchecker` *(optional)* | `lint_text.py --spell` | |
| `python-docx >= 1.2` | DOCX annotation (native comments) | |
| `scipy` | `stat_checks.py` | |
| `PyMuPDF` *(optional)* | PDF annotation and verification | **AGPL-3.0** licensed; see [NOTICE.md](NOTICE.md) |
| LibreOffice *(optional)* | `--render` verification | |
| Web search *(optional)* | Novelty and citation checks | Without it these checks are reported as *not done* |

---

## Installation

### Option A: Claude.ai / Claude app
1. Download `scientific-peer-review.zip` from the [Releases](../../releases) page.
2. Make sure the archive contains the folder `scientific-peer-review/` with `SKILL.md` inside it.
3. Go to **Settings → Capabilities → Skills** and upload the zip.
4. Enable **code execution and file creation** so the annotation scripts can run.

### Option B: Claude Code
```bash
# personal (all projects)
git clone https://github.com/YOUR-USER/scientific-peer-review.git \
    ~/.claude/skills/scientific-peer-review

# or project-level
git clone https://github.com/YOUR-USER/scientific-peer-review.git \
    .claude/skills/scientific-peer-review
```

### Install script dependencies
```bash
pip install "python-docx>=1.2" scipy pillow pyspellchecker
pip install pymupdf        # PDF support and page/line numbers
```

### Verify the installation
```bash
cd scientific-peer-review
python -m unittest discover -s tests -v    # expect: Ran 25 tests ... OK
```

---

## Quick start

1. Attach your manuscript (`.docx` or `.pdf`) and any supplementary files or journal guidelines.
2. Ask Claude, for example:

> *"Review this manuscript as a referee for a plant-science journal. Give me an annotated Word
> file, the comment ledger and a structured report."*

3. Claude will state what it can and cannot assess, review, annotate, verify, and return the files
   with an honest summary (for example, "13 of 13 comments anchored to the exact quoted words").

---

## Usage examples

| Goal | Example prompt |
|---|---|
| Full review | "Review this manuscript. Annotated DOCX, ledger and report please." |
| Statistics only | "Check only the experimental design and statistics of this paper." |
| Quick screen | "Give me a quick editorial screen: is this reviewable, and what are the two biggest problems?" |
| PDF only | "I only have the PDF. Annotate it with highlights and notes." |
| Editor letter | "Write confidential comments to the editor, kept separate from the author report." |
| Consistency check | "Check that the numbers in the abstract, text and tables agree." |
| Journal rules | "Review against these author guidelines." (paste or attach them) |

### Using the scripts manually
Run from the skill folder. Replace `paper.docx` and `ledger.json` with your files.

```bash
# 1. Extract a block map (IDs, sections, warnings)
python scripts/extract_manuscript.py paper.docx --out-dir work

# 1b. Line-level, reference and image audits (candidates to confirm by reading)
python scripts/lint_text.py work/paper.map.json --out work/candidates.json --spell
python scripts/audit_references.py work/paper.map.json --out work/refs_audit.json --authors "Surname1,Surname2"
python scripts/image_audit.py paper.docx --out work/images_audit.json --preview-dir work/previews

# 2. Validate the ledger against the manuscript (quotes must exist)
python scripts/ledger.py validate ledger.json --map work/paper.map.json

# 2b. Add page and line numbers from a rendered copy
python scripts/line_locator.py paper.docx ledger.json --out ledger.located.json

# 3. Insert comments (DOCX) or highlights (PDF)
python scripts/annotate_docx.py paper.docx ledger.json --out-dir out
python scripts/annotate_pdf.py  paper.pdf  ledger.json --out-dir out

# 4. Verify the result independently
python scripts/verify_annotations.py --original paper.docx \
    --annotated out/paper_annotated.docx --ledger ledger.json \
    --report out/paper_anchoring_report.json --render

# 4b. Build the complete Word review report (and the editor note)
python scripts/build_report_docx.py --ledger ledger.located.json --report report.json \
    --refs work/refs_audit.json --images work/images_audit.json --out out/paper_review_report.docx
python scripts/build_report_docx.py --ledger ledger.located.json --report report.json \
    --audience editor --out out/paper_editor_note.docx

# 5. Render the ledger for authors
python scripts/ledger.py render ledger.json --md out/ledger.md --csv out/ledger.csv --audience author

# 6. Verify a suspected numerical problem
python scripts/stat_checks.py pvalue --test F --stat 2.91 --df1 3 --df2 20 --reported 0.012
```

---

## Script reference

| Script | Purpose | Key options |
|---|---|---|
| `extract_manuscript.py` | DOCX / PDF / MD / TXT → block map with IDs, sections and warnings (tracked changes, existing comments, hidden text, scanned PDFs, embedded instructions) | `--out-dir` |
| `lint_text.py` | Candidate line-level findings: spacing, repeated words, tone, causal claims, abbreviations, units, cross-references, text↔table number near-misses, spelling | `--spell`, `--out` |
| `audit_references.py` | Reference completeness, in-text↔list and author↔number cross-check, duplicates, age, self-citation | `--authors`, `--submission-year` |
| `image_audit.py` | Effective dpi, format, caption, alt text; PNG previews | `--preview-dir` |
| `line_locator.py` | Page and line numbers from a rendered copy (LibreOffice) or the supplied PDF | `--out` |
| `build_report_docx.py` | The complete Word review report, or the editor note | `--refs`, `--images`, `--audience` |
| `ledger.py validate` | Schema check; rejects quotes not found in the manuscript; warns on invented numbers, near-duplicates, severity mismatches | `--map` |
| `ledger.py render` | Markdown and CSV from the ledger | `--md`, `--csv`, `--audience` |
| `annotate_docx.py` | Native Word comments anchored to quoted words; original untouched; anchoring report | `--out-dir`, `--author`, `--initials` |
| `annotate_pdf.py` | PDF highlights and notes with anchoring report | `--out-dir`, `--author` |
| `verify_annotations.py` | Re-opens output, checks text unchanged, anchors, no leakage, optional render | `--original`, `--annotated`, `--ledger`, `--report`, `--render` |
| `stat_checks.py` | `pct`, `pvalue`, `grim`, `df`, `ci` consistency checks | see `-h` |

Exit codes: `0` success / consistent, `1` failure / inconsistent, `2` usage problem.

---

## The comment ledger

The ledger (JSON) is the **single source of truth**. The report, the annotated file and the CSV are
all generated from it so they cannot disagree.

```json
{
  "id": "C-003",
  "severity": "Major",
  "status": "confirmed",
  "category": "statistics",
  "audience": "author",
  "location": { "section": "3.1 Grain yield", "block": "P17" },
  "quote": "F(3,20) = 2.91, P = 0.012",
  "comment": "F(3,20) = 2.91 corresponds to P of about 0.060, not 0.012.",
  "rationale": "At alpha = 0.05 the conclusion changes.",
  "required_revision": "Check which value is wrong and revise the conclusion.",
  "suggested_correction": "Optional example wording with [placeholders].",
  "evidence_needed": "The ANOVA table."
}
```

---

## Severity and certainty definitions

**Severity** is defined by *scientific consequence*, not by how much can be written about it.

| Level | Meaning |
|---|---|
| **Critical** | Invalidates a central conclusion, or cannot be repaired with the existing data |
| **Major** | Substantially affects reliability, interpretation or reproducibility; fixable by reanalysis, clarification, added analyses or tempered claims |
| **Minor** | Localised reporting, clarity or formatting issue |
| **Optional** | Suggestion the authors may take or leave |

**Certainty (status)**

| Status | Meaning |
|---|---|
| `confirmed` | Shown directly from the manuscript (quote and recomputation or contradiction) |
| `probable` | Strongly implied, but a missing detail could change the verdict |
| `question` | Cannot be judged from what is reported; author clarification requested |
| `suggestion` | Optional improvement |

---

## Supported formats

| Input | Annotation method | Notes |
|---|---|---|
| `.docx` | Native Word comments | Text boxes, footnotes and equations are not anchored |
| `.pdf` (text layer) | Highlights + pop-up notes | Requires PyMuPDF; scanned PDFs get a ledger only |
| `.doc`, `.rtf`, `.odt` | Convert to DOCX with LibreOffice first | Review is on the converted copy |
| `.md`, `.txt`, `.tex` | Ledger with true line numbers | Annotated copy only on request |
| Online documents (Google Docs links, etc.) | Ledger only | Not annotated unless a connector with write access exists |

---

## Repository structure

```
scientific-peer-review/
├── SKILL.md                         # Workflow, rules, tool use (Claude reads this first)
├── README.md                        # This file
├── LICENSE                          # MIT
├── NOTICE.md                        # Attribution and third-party licences
├── references/                      # Loaded on demand
│   ├── review-framework.md          # Dimensions A–G, consistency checks, recommendation logic
│   ├── statistical-review.md        # Design-first statistics, ML/computational review
│   ├── specialist-modules.md        # Discipline modules + how to derive new ones
│   ├── line-by-line-audit.md        # Exhaustive mode: per-paragraph checklist, tone, numbers, abbreviations
│   ├── reference-audit.md           # Entry completeness, cross-check, online verification
│   ├── figure-table-audit.md        # Image quality, figure content, tables
│   ├── completeness-checklist.md    # What is missing and should be added
│   ├── comment-writing-guide.md     # Fields, severity/status, strong vs weak comments
│   ├── manuscript-annotation.md     # Formats, locators, anchoring limits, fallback
│   ├── literature-and-integrity.md  # Retrieval discipline, citations, retractions, ethics
│   ├── quality-control.md           # Per-comment QC, negative controls, multi-lens passes
│   └── report-template.md           # Author report and editor note templates
├── scripts/
│   ├── extract_manuscript.py
│   ├── ledger.py
│   ├── annotate_docx.py
│   ├── annotate_pdf.py
│   ├── verify_annotations.py
│   ├── stat_checks.py
│   ├── lint_text.py
│   ├── audit_references.py
│   ├── image_audit.py
│   ├── line_locator.py
│   └── build_report_docx.py
├── tests/
│   ├── test_scripts.py              # 15 tests: stats, ledger, annotation, verification, PDF
│   └── test_audits.py               # 10 tests: linter, references, images, Word report, locator
├── examples/                        # SYNTHETIC data only
│   ├── sample_manuscript.docx
│   ├── sample_ledger.json / .md / .csv
│   ├── sample_review_report.md / .docx   # Word report example
│   ├── sample_report.json
│   ├── sample_answer_key.md
│   ├── make_sample_manuscript.py
│   ├── annotated/                   # Annotated DOCX, original copy, anchoring report
│   └── annotated_pdf/               # Annotated PDF, anchoring report
└── docs/
    ├── SOURCE_INVENTORY_AND_SYNTHESIS.md
    └── QA_REPORT.md
```

---

## Examples included

The `examples/` folder holds a **synthetic** biochar-and-crown-rot manuscript with 13 planted flaws
and 6 deliberately sound passages (negative controls), plus the full set of outputs:

- the review ledger (`sample_ledger.json`, `.md`, `.csv`)
- an annotated DOCX (13 of 13 comments anchored exactly) and an annotated PDF
- a structured report (`sample_review_report.md`)
- an answer key (`sample_answer_key.md`)

All text, data and references in the example are **invented**. No real study or real unpublished
manuscript is included.

---

## Adapting the skill

| To adapt… | Do this |
|---|---|
| A new discipline | Add a module to `references/specialist-modules.md` using the five derivation questions in its section 10, and a row in the activation matrix |
| Journal-specific rules | Paste or attach the author guidelines; they are applied only when supplied or retrievable |
| Severity wording / recommendation vocabulary | Edit `references/comment-writing-guide.md` and `references/review-framework.md` (section 8) |
| Reporting standards | Extend the table in `references/review-framework.md` (section 5) |
| Annotation author name | `--author "Your Name"` on the annotate scripts |

---

## Testing

```bash
python -m unittest discover -s tests -v
```

**25 automated tests** cover: P-value recomputation (including a planted error), GRIM, expected
degrees of freedom, CLI exit codes, extraction, ledger validation (invented quotes rejected),
DOCX annotation (exact anchoring across split runs, tables, typographic quotes, editor-comment
exclusion, original untouched), verification (including a **tampered file that must fail**),
LibreOffice rendering, a PDF round trip, the line-level linter (planted problems **and a clean-text negative
control**), reference completeness and cross-checks, effective-dpi calculation, Word report content with
author/editor separation, a run-splitting regression, and page/line location.

Testing also found and fixed fourteen bugs across v0.1.0 and v0.2.0 (listed in
[`docs/QA_REPORT.md`](docs/QA_REPORT.md)).

---

## Testing status and known limitations

This is an **early release (v0.2.0)**. Please read this section before relying on the skill.

**Verified**
- Script behaviour (25/25 tests passing)
- A full exhaustive run on one **real manuscript** (supplied for testing; not included in this repository):
  143 comments, all quotes validated, 141 comments placed as Word comments (140 exact), independent verification
  passed, 29-page Word report inspected visually; two references verified against journal records
- End-to-end workflow on one synthetic manuscript (13/13 DOCX comments anchored exactly; PDF
  12 exact + 1 partial; verification passed; rendering inspected visually)

**Not yet verified**
- Review quality against **human referees**: both tests (synthetic and real) were run by the skill's author,
  so they show the workflow and tooling work, not independent validation; false-positive rate not measured
- Opening annotated files in **Microsoft Word** (tested with python-docx and LibreOffice)
- Two-column journal PDFs and scanned PDFs
- Automatic triggering of the skill from the description
- Subagent / multi-lens mode

**Known limitations**
- Figures are not *understood* by the scripts: image quality is measured, but legibility and content require
  viewing the previews (the skill requires this and records which figures were viewed)
- Reference correctness can only be confirmed with web access; without it findings are marked
  "not verified online". Typically only a subset of references is checked online
- Linter output is **candidates**; patterns can misfire (e.g. cultivar names, equation placeholders)
- Text boxes, footnotes and equations are not anchored; runs containing tabs, breaks or images are
  anchored whole
- Literature and novelty checks require web search; otherwise they are reported as not done
- Expected-degrees-of-freedom formulas assume balanced designs
- A single model run is **not** an independent panel of reviewers
- Specialist modules have not yet been reviewed by domain experts

Full details: [`docs/QA_REPORT.md`](docs/QA_REPORT.md).

---

## Responsible and confidential use

- Manuscripts under review are **confidential**. Check your journal's policy on uploading
  manuscripts to AI tools **before** using this skill on a submission.
- The skill's output is a **draft**. The responsible human reviewer must verify it, adopt or
  reject each comment, and take responsibility for the final review.
- Integrity concerns (image duplication, implausible data, text overlap) are described as
  **neutral observations** and routed to the editor-only channel. The skill never accuses authors
  of misconduct.
- Manuscript text is treated as **untrusted data**; instructions hidden inside a manuscript are
  ignored and reported.

---

## Roadmap

- [ ] Evaluate on several real manuscripts, including sound published papers, and measure the false-positive rate
- [ ] Optional Crossref/PubMed lookup script for networked environments (currently verification is manual via web search)
- [ ] Compare severity and coverage against expert reviews
- [ ] Test annotated files in Microsoft Word and Google Docs
- [ ] Support two-column PDF layouts and tracked-change suggestions
- [ ] Expert review of specialist modules (plant science, statistics, bioinformatics)
- [ ] Description-trigger optimisation
- [ ] Additional reporting-guideline checklists

---

## Contributing

Contributions are welcome.

1. Fork the repository and create a branch: `git checkout -b feature/your-feature`
2. Make your changes. For review content, keep guidance **specific, verifiable and proportionate**
   (no inflated criticism, no fabricated references)
3. Run the tests: `python -m unittest discover -s tests -v`
4. If you change a script, add or update a test for it
5. Open a pull request describing the change and its motivation

**Particularly valuable contributions:** domain-expert review of `references/specialist-modules.md`,
anonymised or synthetic test manuscripts with answer keys, and reports of failures on real
documents (attach only material you are permitted to share).

---

## Changelog

### v0.2.0
- **Exhaustive line-by-line mode** (default for full reviews): every paragraph, table cell, caption and reference
- New references: line-by-line audit, reference audit, figure/table audit, completeness checklist
- New scripts: `lint_text.py`, `audit_references.py`, `image_audit.py`, `line_locator.py`, `build_report_docx.py`
- Complete Word report and editor note; page/line numbers from a rendered copy
- Fix: runs starting with `w:lastRenderedPageBreak` are now split exactly; residual over-wide anchors are reported
  as `run-expanded` instead of "exact"
- 25 automated tests

### v0.1.0 (first release)
- Nine-stage review workflow and eight reference documents
- Six tested scripts: extraction, ledger, DOCX annotation, PDF annotation, verification, statistics checks
- Synthetic example manuscript with annotated outputs and answer key
- Source inventory and synthesis matrix; QA report

---

## License

Released under the **MIT License**. See [LICENSE](LICENSE).

Third-party components and ideas are credited in [NOTICE.md](NOTICE.md). Note that the optional
**PyMuPDF** dependency is AGPL-3.0 licensed; it is not bundled.

---

## Citation

If you use this skill in your work, please cite:

```bibtex
@software{chapagain_scientific_peer_review_2026,
  author  = {Chapagain, Sujan},
  title   = {scientific-peer-review: an evidence-grounded Claude Skill for scientific manuscript peer review},
  year    = {2026},
  version = {0.2.0},
  url     = {https://github.com/YOUR-USER/scientific-peer-review}
}
```

---

## Credits and acknowledgements

### Author and maintainer
**Sujan Chapagain**: concept, requirements, scientific direction, and project ownership.

### Tools and libraries
[python-docx](https://github.com/python-openxml/python-docx) ·
[SciPy](https://scipy.org) ·
[PyMuPDF](https://github.com/pymupdf/PyMuPDF) ·
[LibreOffice](https://www.libreoffice.org)

### Methodological references named in the skill
Hurlbert (1984) on pseudoreplication · Benjamini and Hochberg (1995) on false-discovery-rate control ·
Brown and Heathers (2017) on the GRIM test.

---

<div align="center">

**Created and maintained by Sujan Chapagain**

*Built to make scientific peer review more rigorous, transparent and honest.*

</div>
