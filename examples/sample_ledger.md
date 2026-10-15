# Review comment ledger - sample_manuscript.docx

Counts: Critical 1, Major 6, Minor 5, Optional 1

| ID | Severity | Status | Category | Location | Comment (short) |
|---|---|---|---|---|---|
| C-001 | Critical | confirmed | design | 2.2 Treatments, [P10] | Biochar rate was applied to whole benches, one bench per rate. Rate is therefore completely confounded with be... |
| C-002 | Major | confirmed | statistics | 2.4 Statistical analysis, [P14] | Crown rot was scored on the same pots at four dates (2.3), yet each pot-by-date observation is analysed as an ... |
| C-003 | Major | confirmed | statistics | 3.1 Grain yield, [P17] | F(3,20) = 2.91 corresponds to P of about 0.060 (recomputed; 0.059-0.060 allowing for rounding of F), not 0.012... |
| C-004 | Major | confirmed | consistency | Abstract, [P3] | The abstract reports a 23% yield increase. Table 1 means (4.82 and 5.71 t ha-1) give 18.5% ((5.71-4.82)/4.82),... |
| C-005 | Major | confirmed | interpretation | 4. Discussion, [P25] | Soil water-holding capacity, soil moisture and plant water status were not measured or reported, so the mechan... |
| C-006 | Major | confirmed | interpretation | 4. Discussion, [P26] | A farm-level recommendation is drawn from one greenhouse experiment with one cultivar, one isolate and no fiel... |
| C-007 | Major | confirmed | reproducibility | 2.3 Inoculation and disease assessment, [P12] | In the files supplied, the inoculation and scoring methods are insufficient to reproduce or interpret the dise... |
| C-008 | Minor | probable | statistics | 2.4 Statistical analysis, [P14] | Unadjusted LSD across the six pairwise comparisons inflates the family-wise error rate; its protection also pr... |
| C-009 | Minor | confirmed | figures-tables | Table 1, [T0.r1c1] | The dispersion measure after "±" is not defined (SD, SE or CI), and the table legend does not state it. |
| C-010 | Minor | confirmed | consistency | 3.2 Crown rot severity, [P20] | The reported means (3.9, 3.4, 2.6, 2.8) are not monotonic: severity is slightly higher at 20 than at 10 t ha-1... |
| C-011 | Minor | question | reproducibility | 2.4 Statistical analysis, [P14] | No software version, packages or model code are given, and no data availability statement is included (none se... |
| C-012 | Minor | question | reporting | 2.3 Inoculation and disease assessment, [P12] | The conversion from yield per 5 L pot (and from biochar t ha-1 equivalent in Section 2.2) to per-hectare value... |
| C-013 | Optional | suggestion | statistics | 3.1 Grain yield, [P17] | With four ordered rates, a dose-response analysis (regression on rate, possibly with a plateau) would use the ... |

### C-001 - Critical (confirmed, design)
**Location:** 2.2 Treatments, [P10]
**Original passage:** "Each biochar rate was applied to one greenhouse bench, and six pots per rate were placed on that bench."
**Reviewer comment:** Biochar rate was applied to whole benches, one bench per rate. Rate is therefore completely confounded with bench (light, temperature and irrigation position can differ between benches), and the six pots on a bench are subsamples of one treatment application, not independent replicates of the rate.
**Scientific rationale:** Differences among rates cannot be separated from bench differences, and every P-value based on pots overstates precision (pseudoreplication). This affects all results and both main conclusions.
**Required revision:** State the experimental unit and how benches were assigned and arranged. If benches were not replicated, the study cannot support inference about biochar rate; restrict the paper to a descriptive report with the confounding acknowledged, or repeat the experiment with rates randomised to replicated benches or with pots randomised within benches (blocks).
**Evidence or verification needed:** Greenhouse layout and randomisation procedure; any bench-effect data (e.g. uniform-control pots on each bench).

### C-002 - Major (confirmed, statistics)
**Location:** 2.4 Statistical analysis, [P14]
**Original passage:** "treating each pot-by-date observation as a replicate"
**Reviewer comment:** Crown rot was scored on the same pots at four dates (2.3), yet each pot-by-date observation is analysed as an independent replicate. The reported F(3,92) in 3.2 corresponds to 96 observations (24 pots x 4 dates), confirming that repeated measurements were treated as independent.
**Scientific rationale:** Repeated measures on one pot are correlated; treating them as independent inflates the error degrees of freedom and shrinks P-values.
**Required revision:** Analyse with the pot as the unit: for example a repeated-measures or mixed model with pot as a random effect (and a suitable covariance structure), or a per-pot summary such as AUDPC. Report the model structure, assumptions and the df method. Note that the ordinal 0-5 score also needs an appropriate model (see C-007).
**Evidence or verification needed:** Model formula, software and package, diagnostics.

### C-003 - Major (confirmed, statistics)
**Location:** 3.1 Grain yield, [P17]
**Original passage:** "F(3,20) = 2.91, P = 0.012"
**Reviewer comment:** F(3,20) = 2.91 corresponds to P of about 0.060 (recomputed; 0.059-0.060 allowing for rounding of F), not 0.012. The reported statistic, df and P cannot all be correct.
**Scientific rationale:** At alpha = 0.05 the conclusion changes: with P about 0.06 the omnibus test for yield is not significant, which undermines the statement that biochar rate affected yield and the LSD letters in Table 1.
**Required revision:** Check which value is wrong (statistic, df or P), correct it, and revise the yield conclusions accordingly.
**Evidence or verification needed:** The ANOVA table (SS, MS, df, F, P).

### C-004 - Major (confirmed, consistency)
**Location:** Abstract, [P3]
**Original passage:** "increased grain yield by 23% relative to the control"
**Reviewer comment:** The abstract reports a 23% yield increase. Table 1 means (4.82 and 5.71 t ha-1) give 18.5% ((5.71-4.82)/4.82), which is also what Section 3.1 states.
**Scientific rationale:** The headline quantitative result in the abstract disagrees with the data and the Results text.
**Required revision:** Reconcile the values and state how the percentage was computed (ratio of means, or mean of per-replicate ratios).
**Suggested correction:** Example wording: "...increased grain yield by [percentage, 95% CI] relative to the control..."
**Evidence or verification needed:** Per-pot yields.

### C-005 - Major (confirmed, interpretation)
**Location:** 4. Discussion, [P25]
**Original passage:** "are explained by improved soil water-holding capacity under biochar"
**Reviewer comment:** Soil water-holding capacity, soil moisture and plant water status were not measured or reported, so the mechanism is a hypothesis, not a result. The statement is also written as established ("explained by").
**Scientific rationale:** A mechanistic claim without measurements that test it can mislead readers; the same text reappears in the abstract.
**Required revision:** Present water retention as one possible explanation among others (e.g. effects on microbial communities, nutrient availability), or add measurements (soil moisture, water retention curves, plant water status). Adjust the abstract accordingly.
**Suggested correction:** Example wording: "One possible explanation is improved soil water retention, which was not measured here."

### C-006 - Major (confirmed, interpretation)
**Location:** 4. Discussion, [P26]
**Original passage:** "biochar should be applied at 10 t ha-1 by farmers to control crown rot and increase yield"
**Reviewer comment:** A farm-level recommendation is drawn from one greenhouse experiment with one cultivar, one isolate and no field validation. The previous sentence of the same paragraph says the results "may not transfer to field conditions". The abstract and Conclusions repeat the recommendation without this caveat.
**Scientific rationale:** The recommendation exceeds the evidence and contradicts the authors' own stated limitation; it also depends on a yield effect whose significance is in doubt (C-003).
**Required revision:** Limit conclusions to the tested conditions and present agronomic recommendations as hypotheses for field testing; align Abstract, Discussion and Conclusions.

### C-007 - Major (confirmed, reproducibility)
**Location:** 2.3 Inoculation and disease assessment, [P12]
**Original passage:** "Plants were inoculated with Fusarium culmorum at tillering."
**Reviewer comment:** In the files supplied, the inoculation and scoring methods are insufficient to reproduce or interpret the disease data: isolate identity/source, inoculum type and concentration, inoculation method, mock-inoculated controls, the definition of the 0-5 scale, and whether scoring was blinded are not reported. The ordinal 0-5 scores are also analysed as continuous means.
**Scientific rationale:** Disease severity is a primary outcome; without these details its validity and reproducibility cannot be judged, and unblinded subjective scoring can bias treatment comparisons.
**Required revision:** Report these details (and any supplement that contains them); state how bias was controlled; justify analysing ordinal scores with ANOVA or use an ordinal model, or a validated conversion to percent area.
**Evidence or verification needed:** Isolate ID, inoculum dose, scale definition or diagrams, blinding statement.

### C-008 - Minor (probable, statistics)
**Location:** 2.4 Statistical analysis, [P14]
**Original passage:** "Fisher's LSD test at P < 0.05 for all pairwise comparisons"
**Reviewer comment:** Unadjusted LSD across the six pairwise comparisons inflates the family-wise error rate; its protection also presumes a significant omnibus F, which does not hold if P is about 0.06 (C-003).
**Required revision:** Use a method that controls the family-wise error for the question asked (e.g. Tukey for all pairs, Dunnett for comparisons with the control) or justify LSD.

### C-009 - Minor (confirmed, figures-tables)
**Location:** Table 1, [T0.r1c1]
**Original passage:** "4.82 ± 0.31"
**Reviewer comment:** The dispersion measure after "±" is not defined (SD, SE or CI), and the table legend does not state it.
**Required revision:** State the measure in the legend and give n; report mean differences with confidence intervals.

### C-010 - Minor (confirmed, consistency)
**Location:** 3.2 Crown rot severity, [P20]
**Original passage:** "decreased with increasing biochar rate"
**Reviewer comment:** The reported means (3.9, 3.4, 2.6, 2.8) are not monotonic: severity is slightly higher at 20 than at 10 t ha-1.
**Required revision:** Describe the pattern accurately (e.g. lowest at 10 t ha-1, no further reduction at 20 t ha-1) and state whether 10 and 20 differ.

### C-011 - Minor (question, reproducibility)
**Location:** 2.4 Statistical analysis, [P14]
**Original passage:** "Analyses were done in R."
**Reviewer comment:** No software version, packages or model code are given, and no data availability statement is included (none seen in the files supplied).
**Required revision:** Report versions and packages, and deposit data and code or state why they cannot be shared (check the journal's data policy).

### C-012 - Minor (question, reporting)
**Location:** 2.3 Inoculation and disease assessment, [P12]
**Original passage:** "converted to t ha-1"
**Reviewer comment:** The conversion from yield per 5 L pot (and from biochar t ha-1 equivalent in Section 2.2) to per-hectare values is not described.
**Required revision:** State the area basis and plant density used for both conversions, and note that pot-based yield extrapolation to field values is approximate.

### C-013 - Optional (suggestion, statistics)
**Location:** 3.1 Grain yield, [P17]
**Original passage:** "an increase of 18.5%"
**Reviewer comment:** With four ordered rates, a dose-response analysis (regression on rate, possibly with a plateau) would use the information better than pairwise comparison, and effect estimates with 95% confidence intervals would show the uncertainty.
**Required revision:** Optional: report the estimated difference and 95% CI, and consider a response-curve model once the experimental-unit issue is resolved.
