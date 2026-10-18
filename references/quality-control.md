# Quality control

Read at Stage 8 (independent QC pass), before annotating and before delivering. The goal is
to remove errors and inflation from your own review. A review is judged by the accuracy of
its comments, not their number.

## Contents
1. The per-comment QC test
2. Negative controls: do not manufacture criticism
3. Severity calibration
4. De-duplication and consolidation
5. Multi-lens passes (optional, for long or high-stakes reviews)
6. Report-level checks
7. "What this review could not assess"
8. Final delivery checklist

## 1. The per-comment QC test

For every comment in the ledger answer all of these. Fix or delete on any "no".

1. **Real?** Does the quoted passage exist verbatim (validator) and say what I claim?
2. **Verified or labelled?** Is the status honest (confirmed / probable / question)?
3. **Checked elsewhere?** Did I look in the supplement, other sections, and figure/table
   legends where the information might be?
4. **Right severity?** Does the severity follow from the consequence (section 3)?
5. **Specific and actionable?** Can the author tell what to do?
6. **Defensible?** Would a specialist agree it is a genuine problem, not a style preference?
7. **Numbers recomputed?** Any number I cite was recomputed from the manuscript or the tool.
8. **No invention?** No reference, quote, value or method that is not in the evidence.
9. **Not duplicated?** One comment per root cause.
10. **Right audience?** Integrity and confidential concerns are `editor`; nothing accusatory is
    in an author-facing comment.

## 1b. Coverage QC for exhaustive mode

Before delivering, confirm and state: every paragraph, table, caption and reference entry was read
(counts); every linter candidate was confirmed, rejected or merged; every figure was viewed (or listed as
not viewed); every reference-list entry was audited and the ones checked online are named; the completeness
checklist was applied; each line-level comment has a correction that does not change the science. If any
part was not done, say it in "What this review could not assess".

## 2. Negative controls: do not manufacture criticism

Before finalising, list 3-5 passages that you judge **scientifically acceptable** (a
well-described design element, a hedged claim, a correct analysis). Confirm you have not
commented on them and that your report names them as strengths. A review of a sound
manuscript can legitimately conclude "minor revision" with few comments; there is no minimum
number of criticisms and a clean paper does not need padding. Conversely, if you find nothing
for a major section, say you checked it and found no problem.

Typical false positives to avoid: demanding a different valid analysis; "needs more
replicates" without saying why the existing number cannot support the claim; asking for
experiments outside scope; treating transformations or LSD with protection as errors; calling
a cautious statement overclaiming; flagging "missing" content that is in the supplement;
flagging differences within rounding or plot-reading error; assuming a mistake where a method
is merely unusual.

## 3. Severity calibration

Re-read the definitions in `comment-writing-guide.md` section 2. Heuristics:
- Count of Critical comments is usually 0-2 and each should have a "cannot be fixed by
  rewriting or reanalysis" justification. Several Major comments caused by one flaw are one
  problem: merge or cross-reference, and describe the root cause once.
- Downgrade when the effect on conclusions is unclear; upgrade when the problem affects the
  headline claim.
- If a verified problem affects only a secondary result, it is not Critical.

## 4. De-duplication and consolidation

- The report's major comments and the ledger are the same objects; do not write them twice.
- Cluster by root cause. Recurrent writing issues are one comment with examples.
- Rank major issues by how much they affect the conclusions (importance), then by how many
  claims they touch.

## 5. Multi-lens passes (optional)

For long, high-stakes or multi-method manuscripts, run separate passes with different
lenses before merging, instead of one undifferentiated read. A single model reviewing from
several angles is cheaper than multiple "reviewers" but is **not** independent evidence: its
agreement does not add confidence the way independent human reviewers would. Suggested lenses,
chosen by the study type (not randomly):

1. Design and replication
2. Statistics and computation
3. Claim-evidence and interpretation
4. Internal consistency (numbers, tables, figures, units)
5. Literature, novelty and integrity
6. Reproducibility and reporting

Merge outputs into one ledger, de-duplicate by root cause, rank by consequence. In
environments with subagents, lenses may be run by separate agents given only the manuscript
and the lens instructions; synthesis stays in the main thread so it can weigh each finding
against the evidence. Do not average verdicts: report the strongest well-supported concern.

## 6. Report-level checks

- Summary is neutral and accurate (re-read the abstract against it).
- Strengths are specific and real; weaknesses are not duplicated in minor comments.
- Recommendation follows from the findings and states the driving issues and what would
  change it; uncertainty and limitations of the review are stated.
- Author-facing and editor-facing content are separated.
- The report does not claim actions that were not done (annotation, searches, figure review).
- The report length is proportionate: no padding, no restating the manuscript.

## 7. "What this review could not assess"

List every limitation that reduces coverage, each with its consequence for the review: figures
not viewed; supplementary data or code unavailable; no literature search possible (or which
sources were used/failed); discipline-specific expertise gaps; journal rules not applied;
tools unavailable for annotation; scanned or partial file. This section makes a thin review
honest; omit it only when nothing was limited.

## 8. Final delivery checklist

- [ ] Ledger validated against the manuscript map (no errors; warnings read)
- [ ] Every number cited was recomputed or taken from the manuscript
- [ ] Negative controls listed; no comments on acceptable passages
- [ ] Annotated file verified (`ALL CHECKS PASSED`), or ledger-only delivery stated plainly
- [ ] Anchoring summary reported honestly (counts by precision, unanchored listed)
- [ ] Original preserved unmodified
- [ ] Editor-only comments absent from the annotated file and author-facing report
- [ ] Limitations and confidence stated; draft-for-human-reviewer note included
- [ ] Final chat message lists the files, what was and was not done, and what the user must check
