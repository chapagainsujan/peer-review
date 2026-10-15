# Review framework

Read this at Stage 3-5 of the workflow. It defines what to evaluate, in what order, and how to
turn findings into a recommendation. Statistics, discipline modules, annotation mechanics and
comment wording have their own files.

## Contents
1. Intake and completeness check
2. First-pass reading: build a claim-evidence map
3. Dimensions A-G (what to check, and what a *good* answer looks like)
4. Cross-checking for internal consistency
5. Reporting standards by study type
6. Journal-specific requirements
7. Fatal versus fixable limitations
8. Recommendation logic

---

## 1. Intake and completeness check

Record, before judging anything:

| Item | How to establish it |
|---|---|
| Files supplied | Main text, supplementary files, figures, data, code, cover letter, journal instructions |
| Format | DOCX / PDF / Markdown / other (see `manuscript-annotation.md`) |
| Manuscript type | Original research, short communication, review, meta-analysis, methods, data paper, registered report |
| Discipline and study type | Field trial, greenhouse/growth-chamber, lab assay, omics, modelling, remote sensing + ML, survey, review... |
| Journal / scope | Only if supplied or verifiably accessible. Never guess a journal's rules |
| What the user wants | Full review, quick screen, annotated copy, comment ledger, editor letter, or one section only |

Then state, in one short paragraph, **what can and cannot be assessed**. Typical limits:
figures not viewable; supplementary data absent; code not provided; raw data not provided; no
access to cited papers; discipline-specific knowledge you cannot supply. These limits go into
the report's "What this review could not assess" section, and they cap your confidence. A review
that silently skips what it could not see reads like a complete review and misleads the editor.

If the supplied text is under ~1,000 characters, scanned without a text layer, or obviously not a
manuscript, stop and tell the user. Do not review a fragment as if it were a paper.

## 2. First-pass reading: build a claim-evidence map

Read the whole manuscript (and supplements) once before writing any comment. Early impressions
are often corrected by a later section: the "missing" control may be in the supplement.

While reading, fill in this map (keep it in your working notes; summarise it in the report):

| # | Claim (as the authors state it) | Where stated (abstract / results / discussion / conclusion) | Evidence offered | Does the evidence reach the claim? |
|---|---|---|---|---|

Also note: the research question, hypotheses, the **experimental unit**, the factor structure,
the number of independent replicates at each level, the primary outcome(s), the analysis used,
and the stated limitations. Claims in the abstract and conclusions get the closest scrutiny
because readers rely on them most.

## 3. Dimensions A-G

Apply a dimension only when it is relevant to this study. For each, the question is not "is
every box ticked?" but "could a competent reader trust the conclusion on this point?"

### A. Contribution and novelty
- Is there a clear question or hypothesis, and a specific knowledge gap?
- Is the advance more than describing known observations in a new place, cultivar or season?
  Incremental work can still be publishable; the issue is overclaiming, not incrementalism.
- Are novelty claims ("first", "novel", "for the first time") checked against the literature?
  Use search (see `literature-and-integrity.md`); never assert prior art you did not find.
- Is the relationship to previous work fair: the strongest competing explanations and prior
  results are cited, not just convenient ones?

### B. Design and methods
- Does the design answer the question? A treatment effect needs replication of the treatment
  at the level it was applied (the experimental unit), controls, and a way to separate it from
  confounders (time, position, operator, batch, bench, field, year).
- Replication: biological vs technical vs pseudo-replication; independent repeats of the
  experiment in time/space; number of sites/seasons for field claims.
- Randomisation, blocking, blinding (e.g. disease scoring), and allocation concealment where
  subjective scoring is involved. "Randomised" without a method is a clarification request, not
  a flaw by itself.
- Sampling: how units were chosen, inclusion/exclusion, sample size rationale, bias.
- Materials and conditions sufficient to reproduce: genotype/cultivar identity and source,
  isolate IDs, inoculum dose, soil/substrate, environment, dates, instruments and settings,
  software versions.
- Missing data and attrition: reported and handled?

### C. Statistical and computational analysis
Summarised here; the full guidance is in `statistical-review.md`. Core rule: **establish the
design and data structure first; judge the analysis against that**, never against a preferred
method. Check: analysis matches design; assumptions and diagnostics; dependence handled;
multiplicity; uncertainty and effect sizes; correct interpretation of P; leakage/overfitting
and validation for predictive models; reproducible code and workflow.

### D. Results, tables and figures
- Methods, text, tables, figures and supplements agree (sample sizes, treatment names, units,
  time points).
- Tables/figures are interpretable alone: units, N, dispersion measure (SD vs SE vs CI), letters
  explained, axis scales honest (truncated axes, dual axes), colour-blind-safe where relevant.
- Reported statistics are internally consistent. Verify with `scripts/stat_checks.py`
  (recompute P from the statistic and df, percent changes, expected df for the design, GRIM for
  integer-valued means) **before** writing a comment about numerical inconsistency.
- Results are reported completely: primary outcomes, non-significant results, all time points,
  excluded observations. Selective reporting is a concern to raise as a question unless you
  can show it.
- Figures you cannot see: say so. Do not infer what an image shows from its caption.

### E. Discussion and interpretation
- Conclusions follow from the results; association is not written as causation; mechanisms are
  not asserted without measurements that address them.
- Alternative explanations and confounders are discussed.
- Comparison with earlier work is fair and accurate.
- Generalisation matches the sampling: one cultivar, one season or one site supports local
  statements, not "farmers should adopt".
- The discussion explains significance rather than restating results.
- Limitations are real, not a fig leaf; and a glaring limitation is not omitted.

### F. References and scientific integrity
- Citations are relevant and support the claims attached to them. Check the ones that carry
  an important claim, especially "X has been shown to..." statements. Do not claim a cited
  paper says something unless you read it or retrieved its text or abstract; say which.
- Essential literature missing: name it only if you actually found it.
- Transparency: data/code availability, ethics approvals (human, animal, field permits,
  Nagoya/ABS for genetic resources where applicable), funding and conflicts of interest,
  author contributions, disclosure of AI assistance where the journal requires it.
- Integrity concerns (image duplication, implausible data, text overlap, undisclosed
  duplicate publication): do not accuse. Describe the observation, say what clarification or
  evidence is needed, and route sensitive concerns to the **editor-only** channel.

### G. Structure, reporting and writing
- Title, abstract, keywords, section structure and supplements fit the paper type; the
  abstract states question, design, key quantitative results and conclusion without claims the
  paper does not support.
- Terminology precise and consistent (e.g. "resistance" vs "tolerance"; "yield" definition;
  "heritability" broad vs narrow sense).
- Writing issues matter when they block understanding or accuracy. Fix patterns, not every
  instance: one comment per recurring issue with 2-3 examples. Do not rewrite the paper.
- Reporting guideline fit (section 5), when applicable.

## 4. Cross-checking for internal consistency

Authors often miss disagreements between parts of their own paper, and AI reviewers that focus
on external literature often miss them too. Do a dedicated pass:

1. **Abstract <-> results <-> conclusion**: same numbers, same direction, same strength of claim.
2. **Methods <-> results**: every method has results; every reported analysis was described;
   sample sizes and df agree with the design (use `stat_checks.py df`).
3. **Text <-> tables/figures**: cited values match; percentages recompute; totals/means match
   rows (identify arithmetic vs weighted mean before judging; ignore rounding differences);
   speedups/ratios/changes match their raw values.
4. **Figure/table numbering and citation**: every item is cited and interpreted; none missing.
5. **Terminology and notation**: same symbol or treatment label always means the same thing.
6. **Units**: consistent (t/ha vs kg/ha; Mg/ha), plausible orders of magnitude.

Report a disagreement as a disagreement between two places ("Abstract says 23%; Table 2 and
Results give 18.5%") without guessing which is right. For arithmetic, show the recomputation.
Values read from a plot are approximate: say so and do not flag differences within reading
error. If you only have extracted text, you cannot see figures: limit checks to what is in the
text and captions.

## 5. Reporting standards by study type

Name a guideline only when the study type clearly matches, and say "consider reporting
according to...". Do not demand a checklist the journal does not use.

| Study type | Common guideline |
|---|---|
| Randomised controlled trial | CONSORT |
| Observational (cohort, case-control, cross-sectional) | STROBE |
| Systematic review / meta-analysis | PRISMA |
| Animal experiments | ARRIVE |
| Diagnostic accuracy | STARD |
| Prediction models (incl. ML) | TRIPOD / TRIPOD+AI |
| ML in biology | DOME recommendations |
| qPCR | MIQE |
| Microarray / sequencing experiments | MIAME / MINSEQE |
| Plant phenotyping experiments (metadata) | MIAPPE |
| Qualitative research | COREQ / SRQR |
| Data and code sharing (any) | FAIR principles; journal data policy |

Field and greenhouse agronomy rarely has a mandatory checklist; the checks in
`specialist-modules.md` play that role.

## 6. Journal-specific requirements

Apply journal instructions only if (a) the user supplied them, or (b) you can retrieve the
journal's current author guidelines and cite the URL you used. If neither, say that no
journal-specific rules were applied and review against general standards. Typical checkable
items: word/figure limits, structured abstract, reference style, data availability statement,
ethics statement, statistical reporting rules, reporting-checklist requirements,
anonymisation for double-blind review (names, affiliations, self-citations written in the
first person, identifying acknowledgements, document metadata).

## 7. Fatal versus fixable limitations

Decide for every major problem which kind it is, because it changes the recommendation:

- **Fixable by rewriting or clarifying**: missing details, ambiguous wording, overstated
  conclusions the data can support when toned down.
- **Fixable by reanalysis of the existing data**: wrong model for the design, uncorrected
  multiplicity, missing effect sizes, leakage that can be removed by re-splitting.
- **Fixable only with new data**: treatment not replicated at the experimental-unit level;
  confounded design; no controls; too few independent replicates for the claim; no
  independent validation set.
- **Not fixable**: the data cannot answer the stated question at all (say so plainly; the
  authors may reframe a smaller, honest claim).

Do not suggest that everything can be repaired with better statistics. A confounded design
cannot be rescued by a mixed model. If the surviving claim is narrower, say what it is.

## 8. Recommendation logic

Use the journal's vocabulary if known; otherwise:

| Recommendation | When |
|---|---|
| **Accept** | No unresolved Critical or Major issues; only Minor/Optional edits. Rare on a first round |
| **Minor revision** | Conclusions are supported; remaining issues are reporting, clarity, or small analyses |
| **Major revision** | The question is worthwhile and the data may support a (possibly narrower) conclusion, but one or more Major issues need reanalysis, new analyses, additional data that are feasible, or substantial rewriting |
| **Reject** (or reject-and-resubmit) | A Critical issue invalidates the central conclusion and cannot be fixed without a new study; or the contribution is below the journal's threshold *and* revision would not change that |

Rules of thumb: any unresolved Critical -> Major revision at best, usually Reject, depending
on whether the fix is feasible new data or impossible. Several Major issues that all stem
from one design flaw count as one problem, not several. State the decision, the one or two
findings that drove it, and what would change it. The recommendation is the human reviewer's
to confirm: you provide a draft with reasons.

Confidence: say how sure you are and why (discipline fit, missing materials, unverifiable
citations). Lower it for each thing you could not assess.
