# Peer review report (SYNTHETIC EXAMPLE)

*Generated with the scientific-peer-review skill from `sample_ledger.json`. Draft for a human reviewer to check and adopt.*

## 1. Manuscript identification
Title: Biochar amendment effects on grain yield and Fusarium crown rot severity in winter wheat: a greenhouse study.
Study type: greenhouse pot experiment, one cultivar, one isolate. Discipline: crop science / plant pathology. Journal: not supplied (no journal-specific rules applied).
Files reviewed: main text only. No supplementary material, raw data, code or figure image (Figure 1 not viewable).

## 2. Summary of the submission
The authors apply four biochar rates (0, 5, 10, 20 t ha-1 equivalent) to wheat grown in pots and inoculated with *Fusarium culmorum*, measure grain yield per pot and crown rot severity (0-5 score, four dates), and conclude that 10 t ha-1 raises yield and suppresses crown rot through improved soil water retention, recommending its use by farmers.

## 3. Overall assessment
The question is relevant and the growth conditions and soil are described adequately (Section 2.1). However, the design confounds biochar rate with greenhouse bench (C-001), which affects every result; the analysis also treats repeated measurements as independent (C-002), a key statistic is misreported (C-003), and the Abstract, Discussion and Conclusions go beyond the evidence (C-004 to C-006). In my assessment the central design problem cannot be repaired by reanalysis of the present data.

## 4. Major comments
1. **C-001 (Critical, confirmed): treatment confounded with bench** (Section 2.2). One bench per rate; pots are subsamples. Requires clarification of the experimental unit and, unless benches were replicated, a replicated randomised experiment.
2. **C-002 (Major, confirmed): repeated measures analysed as independent** (Section 2.4; F(3,92) implies 96 observations from 24 pots). Analyse with pot as the unit (mixed/repeated-measures model or per-pot summary).
3. **C-003 (Major, confirmed): P-value inconsistent** (Section 3.1). F(3,20) = 2.91 gives P of about 0.060, not 0.012; the yield conclusion changes at alpha = 0.05.
4. **C-004 (Major, confirmed): 23% in the Abstract vs 18.5%** in Table 1 and Section 3.1.
5. **C-005 (Major, confirmed): mechanism asserted without measurement** (Discussion).
6. **C-006 (Major, confirmed): farm recommendation not supported** and in tension with the authors' own limitation.
7. **C-007 (Major, confirmed): inoculation and scoring methods insufficient** (isolate, dose, mock control, scale definition, blinding; ordinal scores analysed as continuous).

## 5. Minor comments
C-008 unprotected LSD (and the omnibus F is not significant if P is about 0.06); C-009 undefined "+/-" in Table 1; C-010 non-monotonic severity described as a decrease; C-011 software versions and data availability; C-012 unit conversions; C-013 (optional) effect sizes with CIs and a dose-response model.

## 6. Section-by-section notes
Abstract: C-004, C-005, C-006 apply. Introduction: appropriate, no concerns (single placeholder citation; no novelty claim made). Methods: C-001, C-002, C-007, C-008, C-011, C-012; growth conditions and soil analysis adequately reported. Results: C-003, C-009, C-010; the soil pH result and the degrees of freedom for yield are internally consistent. Discussion: C-005, C-006; the stated limitation about one cultivar and isolate is appropriate. Conclusions: align with C-006. Figures: Figure 1 not viewable, so not assessed.

## 7. Statistical and reproducibility assessment
Experimental unit: unclear/confounded (C-001). Analysis does not match the design (C-002). Verification performed with `stat_checks.py`: F(3,20) = 2.91 -> P = 0.060 (reported 0.012: inconsistent); (5.71 - 4.82)/4.82 = 18.5% (Abstract 23%: inconsistent); F(3,92) = 6.84 -> P = 0.0003 and F(3,20) = 0.84 -> P = 0.49 (both consistent with the reported values); error df of 20 and 92 match 24 pots and 96 pot-by-date observations. Data and code availability: none stated (C-011).

## 8. Suggested revisions (examples; authors to check)
Abstract: "...increased grain yield by [percentage, 95% CI] relative to the control..." (C-004). Discussion: "One possible explanation is improved soil water retention, which was not measured here." (C-005).

## 9. What this review could not assess
No supplement, raw data or code (so numbers could only be checked for internal consistency); Figure 1 not viewable; no literature search was run because the manuscript makes no novelty claim and cites one placeholder reference; no journal guidelines were applied.

## 10. Recommendation
**Reject (encourage resubmission after a replicated, randomised experiment)**, confidence 4/5. Driver: C-001 cannot be remedied with the existing data; the reporting inconsistencies (C-003, C-004) additionally need correction. If the editor prefers a revision route, the claims must be reduced to a descriptive report of an unreplicated bench comparison. What would change this: evidence that benches were replicated and randomised.

---
*Confidential comments to the editor* are in the ledger (C-014, audience = editor) and are not part of the author-facing report or the annotated file.
