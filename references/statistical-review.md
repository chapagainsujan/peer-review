# Statistical and computational review

Read at Stage 4 (technical review) whenever the manuscript reports data analysis.

## Contents
1. Principle: design first, method second
2. Establish the design (the five questions)
3. Design -> analysis compatibility
4. Assumptions and diagnostics
5. Multiplicity, effect sizes, uncertainty, power
6. Interpreting P-values
7. Missing data, outliers, transformations
8. Predictive, ML and computational analyses
9. Reproducibility of analysis
10. Verifying numbers before commenting
11. Asking versus prescribing

---

## 1. Principle: design first, method second

Never impose a method mechanically. A reviewer who writes "use a mixed model" without knowing
the design is guessing. First reconstruct what was done; then judge whether the analysis
respects it; then, if it does not, explain the specific mismatch and name defensible options.
If the manuscript does not give enough to reconstruct the design, that is the comment.

## 2. Establish the design (the five questions)

1. **What is the experimental unit** (the smallest unit that independently received a
   treatment)? Pot, plot, bench, field, tray, plant, animal, site-year? Subsamples within a
   unit (plants per pot, leaves per plant, technical replicates) are not independent replicates.
2. **How many independent units per treatment**, and were the repeats independent in time
   (separate experiments/seasons/sites)?
3. **What is the treatment structure** (single factor, factorial, split-plot, nested,
   covariates, gradients) and the **blocking/randomisation structure** (CRD, RCBD, Latin square,
   alpha-lattice, augmented, strip-plot)?
4. **Is there dependence**: repeated measurements on the same unit, spatial or temporal
   autocorrelation, shared environment (bench, chamber, field block), relatedness (pedigree,
   kinship), clustering (sites, batches, operators)?
5. **What is the response** (continuous, count, proportion, ordinal score, time-to-event,
   multivariate, high-dimensional) and what is the primary hypothesis?

## 3. Design -> analysis compatibility

| Situation | Typical problem | Defensible direction (not a mandate) |
|---|---|---|
| Treatment applied to a group (bench, chamber, field) but individual pots/plants analysed as replicates | Pseudoreplication (Hurlbert 1984); inflated df and false precision | Analyse at the unit that received the treatment; if only one group per treatment exists, the effect is confounded with group and cannot be separated by analysis |
| Same units measured at several dates | Treated as independent observations (df too large) | Repeated-measures / mixed model with unit as random effect and a suitable covariance structure (e.g. AR(1)), or analyse a summary (AUDPC, slope) per unit |
| Blocked design (RCBD, lattice) | Block ignored | Include block (random or fixed per design intent) |
| Split-plot / strip-plot | Single error term | Separate error strata (whole-plot vs sub-plot) or mixed model with matching random terms |
| Multi-environment trial | Environments pooled without G x E, or fixed-effects only when random is appropriate | Model genotype, environment, G x E; mixed models for unbalanced data; report heritability on the stated basis (entry-mean vs plot) |
| Counts | Normal ANOVA on small counts | Poisson / negative binomial GLM(M); check overdispersion |
| Proportions / incidence | ANOVA on percentages near 0 or 100 | Binomial/beta GLM(M); arcsine transformation is outdated and criticised |
| Ordinal disease scores (e.g. 0-5) | Treated as interval; mean of scores | Ordinal model or non-parametric methods; or a validated conversion (e.g. midpoint % of area scales) with justification |
| Dose-response / EC50 | Linear regression on a nonlinear relationship | Nonlinear dose-response model; report CI of EC50 |
| Time-to-event (germination, survival) | Compared at one time point | Survival / time-to-event analysis |
| Many correlated traits | Many univariate tests | Multivariate analysis (PCA, MANOVA/PERMANOVA, canonical) with attention to assumptions |
| Spatially arranged field data | Independence assumed | Spatial model, row-column terms, or blocking adequate to the heterogeneity |
| Pedigree/related genotypes | Independence assumed | Include kinship/relationship matrix in mixed models |
| Small n with normality tests | Choosing the test by a normality test on raw data | Look at residuals and design; permutation or robust approaches are acceptable |

## 4. Assumptions and diagnostics

- Assumptions concern model **residuals** (or random effects), not raw data pooled over groups.
  Graphical diagnostics (residual vs fitted, Q-Q plots) carry more weight than a single
  Shapiro-Wilk P-value, which is unreliable at both small and large n.
- Heterogeneous variance: Levene/Brown-Forsythe, variance-weighted or heteroscedastic models.
- ANOVA is fairly robust to mild non-normality with balanced data; do not demand
  transformations without evidence of a problem. Do ask whether diagnostics were checked.
- Report the software, model formula/structure, df method (e.g. Kenward-Roger, Satterthwaite),
  and how random effects were specified.

## 5. Multiplicity, effect sizes, uncertainty, power

- **Multiple comparisons**: name the method and its family. All pairwise comparisons: Tukey
  HSD or similar; comparisons with a control: Dunnett; unprotected LSD across many means
  inflates the family-wise error. Many tests (omics, traits): FDR (Benjamini-Hochberg 1995) or
  other stated control. Exploratory analyses are acceptable if labelled exploratory.
- **Effect sizes with uncertainty**: means with SD/SE/CI (state which), differences with CIs,
  not only P-values or letters. SD describes variation; SE describes precision of the mean; do
  not accept an unlabelled "+/-".
- **Statistical vs practical/biological significance**: a small significant difference may be
  agronomically irrelevant; a large non-significant difference in a small trial is
  inconclusive, not evidence of no effect. Ask whether the effect matters (yield, economics,
  resistance durability).
- **Power / sample size**: request justification when the claim depends on a null result or n
  is very small. Post hoc power from observed effect is not informative; do not request it.

## 6. Interpreting P-values

- P is not the probability the hypothesis is true, nor the size of an effect.
- "Not significant" is not "no difference"; "marginally significant" language needs care.
- P just below 0.05 from one small trial with many analyses is weak evidence; ask about the
  number of analyses performed. Do not impose a stricter universal threshold (e.g. 0.005);
  that is a field-specific convention, not a rule.
- Check one-tailed tests are pre-justified; check multiple outcomes/time points were not
  cherry-picked.

## 7. Missing data, outliers, transformations

- Report n analysed per group and reasons for exclusion; removal of outliers needs a
  pre-stated criterion. Mixed models handle some missingness under MAR; say so.
- Transformations should be justified by diagnostics, reported, and results back-transformed
  or interpreted correctly. Means after transformation are not arithmetic means.

## 8. Predictive, ML and computational analyses

Examples: genomic prediction, UAV/remote-sensing phenotyping, image-based disease detection,
yield forecasting.

- **Data leakage**: train/validation/test split must respect the dependence structure.
  Random splits across plots, dates, images from the same plant, relatives (families),
  or neighbouring pixels/plots leak information and inflate accuracy. Look for spatially or
  group-blocked cross-validation, leave-one-year/site/family-out, and an *independent* test set
  (other field, season or population).
- Preprocessing (scaling, feature selection, imputation, hyperparameter tuning) fitted
  on the full data before splitting is leakage.
- **Baselines**: compared against a simple and a strong established method, tuned with a
  comparable budget; naive baselines (e.g. mean, previous-year, vegetation index regression)
  included where relevant.
- **Metrics**: appropriate for the task and class balance (not accuracy alone for rare
  diseases); report variability across folds/seeds/years, calibration where probabilities are
  used, and error in original units (e.g. t/ha), not only R2.
- **Overfitting**: many features, few samples (p >> n) needs regularisation, nested CV, and
  honest reporting; training-set accuracy is not evidence.
- **External validity**: different cultivars, sensors, growth stages, environments;
  state limits of transfer. UAV work: ground sampling distance, flight altitude, radiometric
  calibration, timing relative to ground truth, georeferencing accuracy.
- **Genomic analyses**: GWAS needs control of population structure/relatedness (PCs or
  kinship), multiple-testing control, and cautious language about causal genes (LD);
  RNA-seq needs adequate biological replication, count-based models on raw counts, batch
  handling, FDR control, and an appropriate background for enrichment tests; single-cell
  analyses must not treat cells as replicates of the sample/individual.
- Interpretability or feature-importance claims should not be presented as mechanisms
  without experimental support.

## 9. Reproducibility of analysis

Ask for: code and software versions (or a clear workflow description), seeds for stochastic
procedures, data (or a clear access statement), model formulas, exact filtering thresholds,
and a repository or archive DOI. If code is "available on request", note it as weaker than a
public repository; do not treat it as a flaw on its own unless the journal requires sharing.

## 10. Verifying numbers before commenting

Use `scripts/stat_checks.py` for any numerical inconsistency you intend to report:

```
python scripts/stat_checks.py pvalue --test F --stat 2.91 --df1 3 --df2 20 --reported 0.012
python scripts/stat_checks.py pct --old 4.82 --new 5.71 --reported 23
python scripts/stat_checks.py df --design rcbd --t 4 --r 6 --reported 20
python scripts/stat_checks.py grim --mean 3.47 --n 25
python scripts/stat_checks.py ci --mean 5.7 --sd 0.6 --n 6 --lo 5.1 --hi 6.3
```
A failed check shows mutual inconsistency, not which number is wrong. Report it as "the
reported values cannot all be correct; please check", with the recomputation. Note that
rounding of the printed statistic is handled; unusual designs (unbalanced, covariates,
nonparametric tests) may not match the simple expected-df formulas: say "for a balanced
design" when you use them.

## 11. Asking versus prescribing

- Evidence of a mismatch (you can show it): state it as a finding, with severity.
- Plausible but unconfirmed (design details unclear): ask the authors to clarify the unit,
  model and dependence, and describe what would be appropriate under each reading.
- Several reasonable analyses exist: list them with the condition under which each fits;
  do not choose for the authors. The final analytical choice should reflect the actual design.
