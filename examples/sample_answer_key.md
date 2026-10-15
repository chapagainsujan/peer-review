# Answer key for the synthetic sample manuscript

Written by the skill's author together with the manuscript generator. **The same author also ran the
review below, so this is a smoke test of the workflow and tooling, not independent validation.**

## Planted flaws and where the sample review found them

| Key | Planted flaw | Expected severity | Found as |
|---|---|---|---|
| K1 | Biochar rate applied to one bench each (treatment confounded with bench; pots are subsamples) | Critical | C-001 |
| K2 | Repeated measures (4 dates) analysed as independent (F df 3,92 = 96 obs from 24 pots) | Major | C-002 |
| K3 | Reported P = 0.012 inconsistent with F(3,20) = 2.91 (recomputed 0.060) | Major | C-003 |
| K4 | Abstract 23% vs Table 1 / Results 18.5% | Major | C-004 |
| K5 | Water-holding-capacity mechanism asserted without measurement | Major | C-005 |
| K6 | Farm recommendation from one greenhouse study; contradicts own limitation sentence | Major | C-006 |
| K7 | Inoculum, isolate, scale definition, blinding, mock control missing; ordinal scores as continuous | Major | C-007 |
| K8 | Unprotected LSD across pairwise comparisons | Minor | C-008 |
| K9 | Undefined "+/-" in Table 1 | Minor | C-009 |
| K10 | "Decreased with increasing rate" but 2.6 -> 2.8 | Minor | C-010 |
| K11 | No software version / data availability | Minor | C-011 |
| K12 | Unit conversions (pot to t/ha) not described | Minor | C-012 |
| K13 | Effect sizes with CIs / dose-response (optional) | Optional | C-013 |

## Negative controls (sound passages: must NOT be criticised)

| Key | Passage | Why it is acceptable |
|---|---|---|
| N1 | Section 2.1 soil and growth conditions (cultivar, seed lot, pH, OC method, temperatures, photoperiod) | Adequately specified |
| N2 | "F(3,20) = 2.91" degrees of freedom for yield | Consistent with 4 rates x 6 pots (error df 20), checked with `stat_checks.py df` |
| N3 | Section 3.3 soil pH, F(3,20) = 0.84, P = 0.49 | Recomputed P = 0.488: consistent |
| N4 | "Because only one cultivar and one isolate ... may not transfer to field conditions" | An appropriate limitation (the contradiction is with the *following* sentence) |
| N5 | "Soil pH was not altered by biochar, so a liming effect is unlikely" | Hedged and based on a measurement |
| N6 | F(3,92) = 6.84, P < 0.001 | Recomputed P = 0.0003: the number is consistent (the problem is the df, covered by K2) |

## Result
Recall 13/13 planted flaws; 0 comments attached to the negative-control passages;
severity matches the planted level for all 13. Not independent evidence of performance on
real manuscripts: see docs/QA_REPORT.md.
