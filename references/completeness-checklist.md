# Completeness check: what is missing and should be added

Authors cannot fix what the reviewer does not name. In every full review, list what is **absent**
from the manuscript and what the authors should add to improve quality, reproducibility and
credibility. Each missing item is a ledger entry (`location.absent: true`, anchored to the
relevant heading) and a row in the Word report section "Missing content". Mark an item as missing
only after checking the main text, tables, legends and supplementary files you were given; if
the supplement was not supplied, say "not reported in the files supplied".

## Contents
1. Front matter and abstract
2. Introduction
3. Materials and methods (general)
4. Experimental field/greenhouse studies
5. Genetic/breeding studies
6. Statistics and software
7. Results and discussion
8. Back matter and declarations
9. How to write the entries

## 1. Front matter and abstract
Title specific (organism, trait, design, location where relevant); author affiliations complete
(department, institution, city, country); corresponding author contact; ORCID format valid;
keywords not duplicating the title; structured abstract elements (background/aim, design,
key quantitative results with statistics, conclusion, limits); abbreviations defined in the
abstract; abstract claims supported by results (no results appear only in the abstract).

## 2. Introduction
Clear knowledge gap; objective and hypothesis stated (aim + hypothesis/prediction); relevant
literature for the study system (not only other species); a citation for each factual claim;
definitions of the key concepts; statement of what is new relative to the **authors' own related
publications** (overlap, shared data) with citations.

## 3. Materials and methods (general)
Enough detail for another group to repeat: materials (source, identity, seed lot/accession IDs,
number of entries and how they were chosen, checks/controls), site (coordinates, altitude, soil
properties with method, climate data source and period), dates (sowing, transplanting, harvest),
design (type, number of replications, randomisation method, plot size and shape written clearly,
plant density, border rows, harvest area), management (seed rate, fertilizer rate/form/timing,
irrigation, weed/pest/disease control, previous crop), measurement protocols for every trait
(how many plants/plots sampled, when, instrument, definition, units), how data were cleaned,
ethics/permits/ABS statements.

## 4. Experimental field/greenhouse studies
Replication in time/space (years, seasons, locations) or an explicit statement of the limitation;
weather during the experiment summarised in text with the data source, not only in a figure;
soil analysis methods; stress or disease pressure documented; how plants were sampled within
plots; missing data handling; yield definition (moisture standard, harvested area, conversion
to t/ha); border-effect handling; presence of check varieties.

## 5. Genetic/breeding studies
Check cultivar(s) and why chosen; number of environments and the G x E consideration; model
used to estimate variance components (fixed/random effects, formula) and its software;
how heritability, genetic advance and correlations were computed (equations written out, with
the symbols defined and the assumptions stated); intensity of selection constant (k) stated;
standard errors/confidence intervals for variance components and heritability; classification
thresholds and their source; handling of unbalanced data; population structure or relatedness if
relevant; justification for the interpretation of path analysis (assumed causal structure,
multicollinearity diagnostics such as VIF, residual effect meaning); sample size adequacy.

## 6. Statistics and software
Software and package versions (and the exact functions/models used); the statistical model
formula; assumption checking (normality of residuals, homogeneity of variance) and what was done
about violations; multiple-comparison procedure; exact P-values or thresholds; effect sizes
and measures of dispersion; alpha level; ANOVA table including SS/df/F/P (not only mean squares);
code and data availability.

## 7. Results and discussion
Every table/figure cited and described; negative or non-significant results reported; results
with measures of uncertainty; discussion that compares with the strongest comparable literature
(same crop, similar environments) and explains **disagreements** as well as agreements;
limitations section (single location/season, number of genotypes, broad-sense vs narrow-sense
heritability caveat, plot size, pot vs field, correlation vs causation); practical implications
tied to data; future work concrete; conclusions that do not introduce new information.

## 8. Back matter and declarations
Data availability statement that meets the journal policy (repository + DOI preferred over "on
request"); code availability; ethics statement consistent with the work; funding statement
internally consistent (e.g. "no funding" vs "funded by ...", and author contributions
mentioning "funding acquisition"); competing interests; acknowledgements naming sources of
material; author contribution roles consistent with the funding statement; supplementary
material described accurately and cited; permissions for third-party material; consistent
numbering of declarations; references complete (see `reference-audit.md`).

## 9. How to write the entries
- One row per missing item: **what** to add, **where**, **why it matters** (consequence for
  reproducibility, validity or reader understanding), and a [placeholder] example sentence if
  useful ("Seed rate was [x kg ha-1]").
- Severity: Major if the omission prevents reproduction or interpretation of a main result;
  Minor otherwise; Optional for improvements.
- Contradictions you find while checking completeness (funding vs contribution statements; data
  said to be in supplement but not described) go in the ledger as `consistency` entries.
- Do not ask for items irrelevant to the study type (e.g. randomisation procedure for a
  descriptive survey, multi-year data for a one-season proof-of-concept) unless the claim needs it.
