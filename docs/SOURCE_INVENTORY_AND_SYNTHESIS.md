# Source inventory and synthesis matrix

Four ZIP archives were supplied. All four extracted without error (774 files in total).
This document records what each contained, what was actually read, what was not, and what
happened to each idea.

## 1. Archive inventory

| Archive | Files | What it is | Licence |
|---|---|---|---|
| `ai-peer-review-skill-main.zip` | 9 | A Claude Code skill (`paper-review`) that spawns N parallel reviewer subprocesses with randomised "lens" seeds, then a meta-review and concerns table | MIT |
| `AI-paper-reviewer-main.zip` | 49 | A prompt toolkit for pre-submission self-audit of ML conference papers (10 dimensions, 4 severity tiers, double-blind, IEEE format, rebuttal, reproducibility checklist); Chinese originals and English translations | MIT |
| `ai-paper-review-main.zip` | 109 | A Python/Flask application: a database of 200 reviewer personas per field, selection, clustering and ranking of comments across reviewers, a Writing-Clarity/consistency reviewer (G001), validation against human reviews, aggregation | MIT |
| `open-scholar-peer-main.zip` | 607 | Community implementation of Google's ScholarPeer: a 7-step, search-grounded protocol (summary, 3-round literature retrieval, historian, baseline scout, Q&A, review) installed into ~21 coding agents; MCP search server; per-tool adapter directories for 21 tools that are copies of one canonical set (`extensions/_shared`) | MIT |

## 2. What was read, and what was not

I do not claim more than this table.

| Archive | Read in full or substantially | Skimmed / sampled | Not read |
|---|---|---|---|
| ai-peer-review-skill | SKILL.md, README, all 3 prompts, `arxiv_search.py`; first 60 of 143 lines of `spawn_reviewers.py` | - | rest of `spawn_reviewers.py` (process orchestration; behaviour inferred from SKILL.md) |
| AI-paper-reviewer | README_EN, `severity_tiers.md`, `10_dimensions_explained.md` (first ~150 lines), English prompts 00-02, 06, 13, 14 in full; prompts 03-05, 07 in near-full | prompts 08-12 and `usage_guide.md`, examples, CONTRIBUTING (first ~45 lines each); heading-structure comparison of the Chinese originals against the English versions (Chinese prompts are the source of the translations, with extra headings; not read line by line) | star-history script/workflow/tests, Google-verification HTML (repository infrastructure, no review content) |
| ai-paper-review | README (first 110 lines), `shared_reviewer_system.md`, `writing_clarity_system.md`, `database_generation.md`, `human_review_extraction_system.md`, docs on pipeline/output format/aggregation/validation (first ~60 lines each); persona section of the ML config; `ranking.py` | `clustering.py` (header, function list) | Python source for LLM clients, web UI, templates, validation metrics, tests, `batch_alignment_*` prompts beyond the first line, Computer-Architecture database |
| open-scholar-peer | README, MANIFESTO, ARTIFACT_CONTRACTS, KNOWN_LIMITATIONS (first ~50 lines of 249), all 8 `_shared` persona skills (orchestrator, summary, literature, historian, baseline scout, query, answer generator, reviewer), `osp-rules.md`, review-guideline and Q&A defaults, onboarding and review commands (first ~75 / ~40 lines), PDF paper text extracted with `pdftotext` (abstract, ablation, limitations sections read), session template | commands 1, 2, 5 (headings), CONTRIBUTING/TROUBLESHOOTING/ARCHITECTURE (headings), MCP `core.py` (error-reason handling) | `install*.sh`, sync/test scripts, other MCP provider code, `kia-context` development logs, brain/adapters for non-Claude tools (hash-compared against `_shared`: 21 adapters are copies with frontmatter-only differences), images (`robot.png`, `support.png`, `agents.png`; not inspected) |

Binary content: the ScholarPeer PDF was extracted to text (184 KB). Images were not inspected.

## 3. Synthesis matrix

Decision key: **Retain** (kept essentially as designed), **Combine**, **Revise**, **Convert**
(became a supporting resource or script), **Exclude**.

| Source file(s) | Core idea | Strength | Limitation for this goal | Overlap | Decision | Where it went and why |
|---|---|---|---|---|---|---|
| AI-paper-reviewer / severity tiers | 4-tier severity with decision tree | Clear, actionable levels | Calibrated for conference rejection risk; stylistic items (e.g. "we are the first") rated Critical | Open ScholarPeer (guideline-driven), ai-paper-review (major/moderate/minor) | **Revise** | Severity redefined by *scientific consequence* (Critical = invalidates a conclusion / not repairable with the data); `comment-writing-guide.md` s.2 |
| AI-paper-reviewer / 10 dimensions | Reviewing the same text through independent lenses | Systematic coverage; numbers/claims/notation consistency | ML/IEEE/double-blind specifics; language-purity and anti-"AI smell" are cosmetic | Dimensions A-G of the brief | **Combine/Revise** | Logic, empirical rigour, citations, notation, structure folded into dimensions A-G; formatting/anti-AI-smell/Chinese-residue **excluded** |
| AI-paper-reviewer / 06 experiments, 13 reproducibility checklist | Cross-table number consistency matrix, fairness of baselines, metric definitions; Yes/No/NA with evidence | Concrete, verifiable | ML-specific (21-item NeurIPS checklist) | ai-paper-review G001 | **Combine/Convert** | Consistency pass (`review-framework.md` s.4) and `stat_checks.py`; reproducibility asks in `statistical-review.md` s.9; the ML checklist itself not copied |
| AI-paper-reviewer / 14 red flags, 03/04/07 section audits | Hedging vs overclaim, vague adjectives need numbers, empty figure references | Good claim-calibration heuristics | Several are stylistic preferences and presented as rejection risks | Dimension E | **Revise** | "Significant needs a test", overgeneralised claims, empty figure references kept as *claim-evidence* checks; stylistic lists excluded |
| AI-paper-reviewer / 08 double-blind, 09 IEEE, 10 LaTeX math, 11 anti-AI-smell, 12 rebuttal | Pre-submission and author-side tools | Useful for authors | Author-side or venue-specific; not scientific review | - | **Exclude** (double-blind kept as a short journal-compliance item) | `review-framework.md` s.6 mentions anonymisation checks only when the journal requires them |
| ai-peer-review-skill / reviewer.md, SSoT seeds | Random hex seed -> random lens and adversarial stance | Increases viewpoint diversity of identical panels | Random lens assignment is unrelated to the manuscript; "a review that finds nothing is a failed review" pushes manufactured criticism; p < .005 prior is a field convention | ai-paper-review personas | **Exclude** (idea of lens diversity retained) | Lenses are **chosen by study type** (`quality-control.md` s.5); explicit negative-control rule replaces "must find faults" |
| ai-peer-review-skill / reviewer_alignment_forum.md | Red-team checklist: distinguishing test, cherry-picking, post-hoc hypotheses, baselines, ablations, alternative explanations, "what did this update?" | Excellent evidence-scrutiny questions | ML-paper framing; strong adversarial prior | Dimension C/E | **Revise** | Evidence questions folded into dimensions B, C, E and the comment guide; adversarial prior dropped |
| ai-peer-review-skill / metareview.md, spawn_reviewers.py | N parallel reviewers, concerns-by-reviewer table, meta-review; `claude -p` subprocess parallelism | Common/unique concern synthesis; do not average verdicts | Needs the Claude Code CLI and subprocess spawning; not available in claude.ai; independence is illusory (same model) | ai-paper-review clustering | **Convert** | Optional multi-lens passes with synthesis in the main thread and the "do not soften / do not average" rule (`quality-control.md` s.5); the spawn script is **not** included (cannot be tested here) |
| ai-peer-review-skill / arxiv_search.py | Cite only IDs seen in search output; silent fallback on error | Anti-fabrication rule | arXiv only; requires network and `arxiv` package; silent fallback hides gaps | OSP retrieval rules | **Revise** | Citation rules kept; *silent* fallback replaced by "report the gap"; script excluded (agricultural literature is mostly outside arXiv) |
| ai-paper-review / persona database, selection, clustering, ranking | 200 field-specific personas; keyword selection; cross-reviewer clustering ranked by commonality x severity | Principled consolidation of overlapping comments | Heavy infrastructure; no agriculture database; persona counts inflate comments (authors say expect to reject about half) | Multi-lens passes | **Convert** | De-duplication by root cause and ranking by consequence (`quality-control.md` s.4); the app and databases excluded |
| ai-paper-review / writing_clarity_system.md (G001) | Reviewer scoped to writing *and internal consistency*: recompute arithmetic, show the recomputation, flag approximate plot readings, report both locations without picking a side | Fills ScholarPeer's admitted gap (misses internal inconsistencies) | Capped at 5-20 comments; paper-type specific wording | OSP lacks it | **Retain** | Consistency pass and `stat_checks.py`; `review-framework.md` s.4, `comment-writing-guide.md` |
| ai-paper-review / shared_reviewer_system.md, output schema | Strict structured comment schema (severity, category, section, summary, description, keywords); do not pad | Machine-readable; honest minimum | Format is for their parser | Brief's comment framework | **Revise** | Ledger JSON schema (`scripts/ledger.py`) with more fields (status, quote, rationale, revision, evidence, audience) |
| ai-paper-review / human_review_extraction | Verbatim preservation when reshaping text | Principle of not paraphrasing the source | Used for validation against human reviews | - | **Exclude** (principle retained in "quote verbatim") | Quote-existence validation in `ledger.py` |
| ai-paper-review / validation, aggregation, calibration | Compare AI vs human reviews; tune personas | Measures calibration | Needs human review corpora and the app | - | **Exclude** | Documented in the README as a future evaluation path |
| ai-paper-review / README "intended use" | Draft-polishing aid; every comment is a suggestion; expect to reject about half | Honest framing | - | OSP rule 9 | **Retain** | Non-negotiable rules and final-message reminder |
| open-scholar-peer / summary agent | Review-oriented compression into claims / method / evidence | Prevents "lost in the middle"; ablation shows large effect | - | - | **Retain** | Claim-evidence map (`review-framework.md` s.2) |
| open-scholar-peer / literature agent (3 rounds), historian | Live retrieval anchored by sub-domain, method, recent window; chronological narrative; open problems; what counts as significant | Addresses stale-knowledge novelty errors | Heavy 3-round pipeline; MCP search server not available in claude.ai; bound to ML/biomed databases | Novelty dimension | **Revise** | Retrieval queries with sub-domain / method / recent windows when search exists (`literature-and-integrity.md` s.2); full pipeline excluded |
| open-scholar-peer / baseline scout | Adversarial search for missing baselines/datasets; misreported comparisons; retraction check; code release check; do not flag work after the cutoff date | Very strong honesty discipline | ML "baselines" framing | Dimension A/F | **Revise** | "Missing comparators" for experimental science (checks, controls, standards); retraction and cutoff rules kept |
| open-scholar-peer / query + answer generator | Interrogate claims with probing questions; verify; `[DISCREPANCY]`; "not verified" never "consistent" | Active verification; isolates verification from question framing | Needs subagents; self-reflection fallback is weaker (documented) | Stage 4/8 | **Combine** | Per-comment QC test and status labels; subagent isolation optional |
| open-scholar-peer / reviewer agent | Synthesis only, no new findings; "What this review did not have" section; confidence lowered by gaps | Honest thin reviews | - | - | **Retain** | "What this review could not assess" in the report; confidence rule |
| open-scholar-peer / MANIFESTO, rules, ARTIFACT_CONTRACTS | Never invent citations; fail loudly; user can skip steps but gaps are recorded; error is not empty; drafts, the reviewer signs | Excellent principles | `.brain/` session machinery and 21-tool installers are infrastructure | - | **Retain principles / Exclude machinery** | Non-negotiable rules 1, 5, 6, 9; tool errors vs empty results |
| open-scholar-peer / KNOWN_LIMITATIONS, paper | ScholarPeer misses internal inconsistencies; latency; diversity gap | Tells us what to add | - | G001 | **Retain** | Internal-consistency stage added by design |
| open-scholar-peer / MCP server, install/sync/test scripts, adapters (21 tool directories of copies) | Search providers; multi-tool installation | Engineering | Not a Claude.ai skill; network-dependent; untestable offline | - | **Exclude** | Reported as out of scope |

## 4. What no source contained (added in this skill)

- Native Word comments anchored to quoted text, PDF highlight annotations, anchoring-precision
  reporting, and an independent verification script (new).
- A ledger with quote-existence and invented-number validation (new).
- Design-first statistical review for experimental agricultural/biological science, including
  pseudoreplication, repeated measures, split-plot/MET, ordinal disease scores, omics,
  spatial-leakage in remote-sensing ML (new; none of the sources address experimental design).
- Discipline modules (field/greenhouse, plant pathology, breeding, stress physiology,
  phenotyping/ML, genomics, soil/sustainability, modelling) (new).
- A numeric consistency tool (`stat_checks.py`: P recomputation, GRIM, df, percent change, CI) (new).
- A negative-control rule and severity defined by scientific consequence (new).
- Fatal-versus-fixable reasoning and recommendation logic (new).
- Environment-honest tool-use rules for claude.ai / Claude Code / chat-only (new).

## 5. Conflicts resolved

| Conflict | Resolution |
|---|---|
| "Find faults" (ai-peer-review-skill) vs "do not pad; fewer is fine" (ai-paper-review, OSP) | No minimum comments; negative controls |
| Style flags as Critical (AI-paper-reviewer) vs consequence-based severity | Consequence-based |
| Silent tool fallback (ai-peer-review-skill) vs fail loudly (OSP) | Fail loudly; report gaps |
| Random lenses vs relevant lenses | Relevant lenses by study type |
| Multiple "independent" reviewers from one model | Treated as lenses, not independent evidence |
| p < .005 for confirmatory results (AAF critic) | Not imposed; field convention |
