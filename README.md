<div align="center">

# scientific manuscript peer review


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](#changelog)
[![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen.svg)](#testing)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](#requirements)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-8A2BE2.svg)](#installation)
[![Status](https://img.shields.io/badge/status-early%20release-orange.svg)](#testing-status-and-known-limitations)

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

**peer-review** is a [Claude Skill](https://docs.claude.com) that makes Claude review a
scientific manuscript the way an experienced journal referee would. It evaluates scientific
validity, finds substantive weaknesses, attaches each comment to the **actual passage** of the
manuscript, explains **why** the problem matters, and proposes **defensible** fixes, while stating
plainly what it could **not** assess.

It was designed for **agricultural, plant, soil, genomics and quantitative-biology research**
(field and greenhouse trials, plant pathology, breeding, stress physiology, phenotyping, remote
sensing and machine learning, omics), and is adaptable to any other discipline.

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
pip install "python-docx>=1.2" scipy
pip install pymupdf        # optional, PDF support only
```

### Verify the installation
```bash
cd scientific-peer-review
python -m unittest discover -s tests -v    # expect: Ran 15 tests ... OK
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

# 2. Validate the ledger against the manuscript (quotes must exist)
python scripts/ledger.py validate ledger.json --map work/paper.map.json

# 3. Insert comments (DOCX) or highlights (PDF)
python scripts/annotate_docx.py paper.docx ledger.json --out-dir out
python scripts/annotate_pdf.py  paper.pdf  ledger.json --out-dir out

# 4. Verify the result independently
python scripts/verify_annotations.py --original paper.docx \
    --annotated out/paper_annotated.docx --ledger ledger.json \
    --report out/paper_anchoring_report.json --render

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
│   └── stat_checks.py
├── tests/
│   └── test_scripts.py              # 15 automated tests
├── examples/                        # SYNTHETIC data only
│   ├── sample_manuscript.docx
│   ├── sample_ledger.json / .md / .csv
│   ├── sample_review_report.md
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

**15 automated tests** cover: P-value recomputation (including a planted error), GRIM, expected
degrees of freedom, CLI exit codes, extraction, ledger validation (invented quotes rejected),
DOCX annotation (exact anchoring across split runs, tables, typographic quotes, editor-comment
exclusion, original untouched), verification (including a **tampered file that must fail**),
LibreOffice rendering, and a PDF round trip.

Testing also found and fixed five bugs before release (listed in
[`docs/QA_REPORT.md`](docs/QA_REPORT.md)).

---

## Testing status and known limitations

This is an **early release (v0.1.0)**. Please read this section before relying on the skill.

**Verified**
- Script behaviour (15/15 tests passing)
- End-to-end workflow on one synthetic manuscript (13/13 DOCX comments anchored exactly; PDF
  12 exact + 1 partial; verification passed; rendering inspected visually)

**Not yet verified**
- Review quality on **real manuscripts** (the synthetic test was designed and reviewed by the same
  author, so it is a smoke test, not independent validation)
- Opening annotated files in **Microsoft Word** (tested with python-docx and LibreOffice)
- Two-column journal PDFs and scanned PDFs
- Automatic triggering of the skill from the description
- Subagent / multi-lens mode

**Known limitations**
- Figures and images are not read by the scripts; Claude must render and view them, or state that
  they were not assessed
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

- [ ] Evaluate on real manuscripts, including sound published papers, and measure the false-positive rate
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
  version = {0.1.0},
  url     = {https://github.com/chapagainsujan/peer-review}
}
```

---

## Credits and acknowledgements

### Author and maintainer
**Sujan Chapagain**: concept, requirements, scientific direction, and project ownership.

### Design sources
The skill's design was informed by an audit of four open-source (MIT-licensed) projects. No code or
prompt text was copied verbatim; ideas were adapted, rewritten, or deliberately rejected. The
full decision record is in
[`docs/SOURCE_INVENTORY_AND_SYNTHESIS.md`](docs/SOURCE_INVENTORY_AND_SYNTHESIS.md).

| Project | Ideas adapted |
|---|---|
| `ai-peer-review-skill` | Multiple review lenses, meta-review synthesis, cite only retrieved identifiers |
| `AI-paper-reviewer` | Cross-section consistency checks, claim-hedging heuristics, reproducibility-checklist idea |
| `ai-paper-review` | Writing-clarity and internal-consistency reviewer, structured comment schema, consolidation by severity |
| `open-scholar-peer` | Claim-oriented summaries, time-anchored literature retrieval, comparator scouting, "error is not empty", "what this review did not have" |

The `open-scholar-peer` project is a community implementation of Google's **ScholarPeer** method.
Please cite the original ScholarPeer paper if you build on that approach.

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
