# Writing review comments

Read at Stage 6 (comment drafting). A good comment lets an author find the passage, understand
the problem, see why it matters, and know what would resolve it, without guessing.

## Contents
1. Comment fields
2. Severity definitions
3. Status definitions (confirmed / probable / question / suggestion)
4. Weak vs strong comments
5. Worked examples
6. Suggested-wording rules
7. Tone
8. What not to comment on

## 1. Comment fields

| Field (ledger key) | Required for | Notes |
|---|---|---|
| `id` | all | `C-001`, unique, stable across report/annotation |
| `severity` | all | Critical / Major / Minor / Optional |
| `status` | all | confirmed / probable / question / suggestion |
| `category` | all | design, statistics, data, interpretation, literature, reproducibility, integrity, reporting, writing, figures-tables, consistency, novelty, ethics |
| `audience` | optional | `author` (default) or `editor` (confidential, never annotated into the manuscript) |
| `location` | all | section; block ID; page/line only if reliable; table/figure; `absent: true` for missing information |
| `quote` | all except absence/table/figure | Verbatim, short. The ledger validator rejects quotes not found in the manuscript |
| `comment` | all | The precise problem, one issue per comment |
| `rationale` | Critical, Major | Why it matters and what it affects |
| `required_revision` | Critical, Major | The concrete action |
| `suggested_correction` | when justified | Example wording or approach; placeholders for unknowns |
| `evidence_needed` | when useful | Data, diagnostic, citation or clarification that would resolve it |

Simple language or typo fixes need only `comment` (and a quote). Do not pad them.

## 2. Severity definitions

| Severity | Meaning | Examples |
|---|---|---|
| **Critical** | Invalidates a central conclusion, or the problem cannot be repaired with the existing data | Treatment confounded with its only replicate (one bench per rate); no control for the key comparison; data inconsistency that questions data integrity (after verification) |
| **Major** | Substantially affects reliability, interpretation or reproducibility, but can be addressed by reanalysis, added analyses, clarification, or tempering claims | Wrong error term for the design; repeated measures as independent; mechanistic claim without measurements; key method missing |
| **Minor** | Localised reporting, clarity, labelling or formatting issue that does not change conclusions | Undefined abbreviation; unlabelled SD/SE; inconsistent units |
| **Optional** | Improvement the authors may take or leave | Additional figure, alternative visualisation, extra reference |

Calibrate against the *consequence*, not the number of words you can write about it. A
single Critical belongs only where you can state why it is not fixable by revision of text or
analysis. If you are unsure between two levels, choose the lower and explain the uncertainty.

## 3. Status definitions

Use the status to show how sure you are. Authors and editors treat these differently.

- **confirmed**: you can show it from the manuscript (quote + recomputation or direct
  contradiction). Phrase as a finding.
- **probable**: the manuscript's description strongly implies a problem but a detail could
  change the verdict. Phrase as "appears", and say what detail would resolve it.
- **question**: you cannot tell from what is reported. Phrase as a request for clarification and
  state why the answer matters.
- **suggestion**: optional improvement.

Critical comments should be `confirmed` or at least `probable` with the reason stated. A concern
that only needs author clarification is rarely Critical. Never present an unverified suspicion
(possible duplication, data fabrication, plagiarism) as fact: describe the observation neutrally
and put the concern in an `audience: editor` comment.

## 4. Weak vs strong

**Weak**: "The statistical analysis is inadequate. Please improve it." (No location, no
reason, no action.)

**Strong** (assuming the manuscript actually has the described design): "Methods state that
treatment means were compared by one-way ANOVA, but each pot was measured on four dates
(Methods, 'sampling at 14, 28, 42 and 56 days'). Please clarify whether date and the
within-pot dependence were included. If these are repeated measurements, treating every
observation as independent inflates the degrees of freedom (the F-test df of 3 and 92 imply
96 independent observations from 24 pots). Report the experimental unit, the model structure
and assumptions, and the post hoc method. The analytical choice should reflect the design; a
repeated-measures or mixed model, or an analysis of a per-pot summary, are options."

Notice: location, evidence from the manuscript, consequence, what to report, options without
prescribing a single model.

## 5. Worked examples (generic; adapt to the manuscript)

**Design (Critical, confirmed).** Quote: "each biochar rate was applied to one bench".
Comment: treatment is applied to whole benches with one bench per rate, so rate is completely
confounded with bench (light, temperature, irrigation position). Pots within a bench are
subsamples, not replicates of the rate. Rationale: differences between rates cannot be
separated from bench differences; P-values based on pots overstate precision. Revision:
state the experimental unit; if benches were not replicated, restrict claims to description
and acknowledge confounding, or repeat with replicated, randomised benches. Evidence: layout
diagram and randomisation procedure.

**Consistency (Major, confirmed).** Quote from abstract: "increased grain yield by 23%".
Comment: abstract reports 23% whereas Table 2 means (4.82 and 5.71 t/ha) give 18.5% and the
Results text says 18.5%. Revision: reconcile, and state whether the figure is a ratio of
means or a mean of per-replicate ratios. (Recompute with `stat_checks.py pct` first.)

**Statistics reporting (Major, confirmed).** Quote: "F(3,20) = 2.91, P = 0.012". Comment:
F(3,20) = 2.91 corresponds to P of about 0.060, not 0.012; the conclusion at alpha = 0.05 would
change. Revision: check which value is wrong (statistic, df, or P) and correct the associated
interpretation.

**Interpretation (Major, confirmed).** Quote: "improved water-holding capacity, which
reduced root rot". Comment: neither water-holding capacity nor soil moisture was measured, so
the mechanism is a hypothesis. Revision: present it as a possible explanation, or add the
measurements that test it.

**Reproducibility (Major, probable/question).** `absent: true`. Comment: inoculum
concentration, volume and application method are not reported, and the 0-5 severity scale is
not defined. Revision: report them; state whether scoring was blinded.

**Multiplicity (Minor to Major).** Quote: "pairwise LSD tests". Comment: LSD across 28 pairwise
comparisons without protection inflates false positives. Revision: use a method that controls
the family-wise error (e.g. Tukey, or Dunnett for comparisons to a control) or justify.

**Literature (Major if verified).** Only after retrieval: "[Author, year, DOI] reports X under
comparable conditions, which seems to contradict the statement in the Discussion; please
discuss." If not retrieved, ask the authors to support the claim, and do not name a paper.

**Writing (Minor).** One comment per pattern: "'Significantly' is used without a statistical
test in the Abstract and the Discussion (e.g. '...significantly higher yield...'); report the
test or use non-statistical wording."

**Positive note (not a comment).** Strengths go in the report, not as ledger comments, unless
the user wants them marked in the manuscript.

## 6. Suggested-wording rules

- Preserve the authors' intended meaning where it is scientifically defensible.
- Do not introduce findings, citations, methods or numbers absent from the evidence. Use
  placeholders: "[report the estimated difference and its 95% CI]".
- Distinguish an example from a fact: prefix "Example wording:" and keep the author's
  decision explicit.
- When several reasonable alternatives exist, list them with the condition for each.
- Numbers you introduce must be recomputed from the manuscript's own values and shown (the
  ledger validator warns about numbers not present in the manuscript).

## 7. Tone

Direct, specific, courteous. Describe the manuscript, not the authors ("the Methods do not
state..." not "the authors failed to..."). No sarcasm, no speculation about motives, no
inflation ("fatal", "unacceptable") unless the Critical criteria are met. Each comment should
be understandable without the rest of the report.

## 8. What not to comment on

- Style preferences with no effect on clarity or accuracy.
- Alternative analyses you would merely have chosen, when the one used is valid for the design.
- Requests for experiments outside the paper's stated scope.
- Issues the manuscript already addresses elsewhere (check the supplement first).
- Duplicates: one comment per root cause; cross-reference instead of repeating.
- Anything you could not verify and cannot phrase as a question.
