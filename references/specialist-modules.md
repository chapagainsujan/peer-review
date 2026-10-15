# Specialist review modules

Read at Stage 1/3 after identifying the manuscript's discipline and study type. **Activate only
the modules that fit.** They are prompts for what a specialist would look at, not checklists to
be forced onto every paper. If the manuscript lies outside these modules, use section 10 to
derive a module on the fly. If you lack the specialist knowledge to judge a point, say so in the
report ("outside what I can assess reliably: ...") instead of bluffing.

## Contents
1. Activation matrix
2. Field and greenhouse experiments (agronomy, crop science)
3. Plant pathology and plant-pathogen interactions
4. Plant breeding, quantitative genetics, germplasm evaluation
5. Crop physiology and abiotic stress
6. Phenotyping, UAV/remote sensing and machine learning
7. Genomics, transcriptomics, molecular biology, bioinformatics
8. Soil science, sustainable agriculture, agronomic management
9. Statistical modelling and reproducible scientific computing
10. Deriving a module for an unfamiliar discipline

## 1. Activation matrix

| If the manuscript... | Activate |
|---|---|
| tests treatments in pots, benches, chambers, plots or farms | 2 |
| inoculates, scores disease, tests resistance or fungicides | 3 (+2) |
| compares genotypes, estimates heritability, QTL/GWAS, selection | 4 (+7 if molecular) |
| imposes drought/heat/salt/nutrient stress, measures physiology | 5 (+2) |
| uses sensors, images, UAVs, spectral indices, deep learning | 6 (+ statistical-review.md section 8) |
| uses sequencing, qPCR, transformation, editing, proteomics | 7 |
| measures soil properties, carbon, nutrients, microbiome, practices | 8 (+2) |
| is mainly simulation, modelling or software | 9 |

---

## 2. Field and greenhouse experiments

Check:
- **Experimental unit and replication** (see `statistical-review.md`): how many independent
  plots/pots/benches per treatment; **treatments applied to whole benches, chambers, fields or
  plots without replication are confounded** with that unit.
- Layout: randomisation, blocking, border rows, plot size and harvested area, position effects
  (bench edges, light gradients, field gradients), rotation of pots.
- Replication in time/space: number of seasons, years, sites; a single season/site supports
  local conclusions only. Greenhouse results are not field results: check extrapolation.
- Management reported: sowing date and density, fertiliser (rate, form, timing), irrigation
  (amount, method, scheduling), pesticide use, weed control, cultivar/seed lot, previous crop.
- Environment: temperature, light, humidity, rainfall, soil type at the site; growth stage
  definitions (BBCH/Zadoks/Feekes).
- Yield definitions: grain moisture standard, harvest area, units, treatment of border/edge,
  yield components analysed with matching design.
- Economic or agronomic recommendations only if costs, variability, and practicality are in the
  analysis.

Typical flaws: pseudoreplication; unreplicated treatment application; blocks ignored;
repeated measures treated as independent; "optimal rate" claimed from 2-3 rates without
response modelling; conclusions about "farmers" from one pot experiment.

Avoid demanding: multi-year field validation for a clearly framed greenhouse screen.

## 3. Plant pathology and plant-pathogen interactions

Check:
- Pathogen identity: isolate IDs and source, molecular confirmation (multi-locus where
  relevant), culture maintenance, pathogenicity verified (Koch's postulates where claimed),
  number of isolates (one isolate limits generality).
- Inoculation: method, inoculum type and concentration (spores/mL, CFU), volume, stage of host,
  mock-inoculated controls, environmental conditions (humidity, temperature, leaf wetness).
- Host: genotype identity, susceptible and resistant checks, seed source, plant age.
- Disease assessment: scale defined (ordinal vs % area; use of standard area diagrams),
  assessors, **blinding**, timing; AUDPC calculation described (and dependence on time
  interval); incidence vs severity distinguished.
- Resistance terminology: resistance (limits pathogen) vs tolerance (limits yield loss) vs
  escape; qualitative vs quantitative resistance; race/isolate specificity.
- Repeat of the whole experiment at another time (greenhouse infection assays are noisy);
  how experiments were combined.
- Fungicide / biocontrol efficacy: dose-response and EC50 with CIs, formulations, controls
  with the carrier alone, resistance monitoring, field relevance; in vitro vs in planta.
- Microbiome/endophyte claims: sampling, controls for contamination, compositional-data
  statistics, relative vs absolute abundance, causal language.
- Epidemiology: spatial/temporal models appropriate to the data; inference on dispersal or
  spread supported by design.

Typical flaws: no mock control; single isolate generalised to the species; ordinal scores
analysed as interval; unblinded subjective scoring; resistance claimed from one experiment;
efficacy in vitro extrapolated to field.

## 4. Plant breeding, quantitative genetics, germplasm evaluation

Check:
- Population: size, structure, relatedness, how selected (selection bias), parents, checks.
- Phenotyping: replication, design (augmented, alpha-lattice), environments (MET), trait
  measurement protocol, adjustments (spatial, covariate).
- Model: genotype as fixed vs random reasons; BLUEs vs BLUPs, one-stage vs two-stage analysis
  (and weighting of stage-1 estimates); G x E modelled; stability methods applied correctly
  (AMMI/GGE interpretation limits).
- Heritability: type declared (broad-sense, entry-mean basis vs plot basis), variance
  components and standard errors; a heritability from a single environment is inflated by G x E
  confounded with G.
- QTL/GWAS: marker density, LD, population structure control, significance thresholds,
  confidence intervals/physical positions, effect sizes (beware Beavis effect for small
  populations), validation across populations/environments, candidate-gene claims from
  association alone.
- Genomic selection: training/validation relationship, cross-validation scheme (random vs
  family-aware), accuracy defined (correlation with what: BLUEs, true breeding values),
  response-to-selection claims.
- Germplasm: accession provenance and legal access (ABS/Nagoya), diversity sampled,
  duplicate accessions.

Typical flaws: heritability without design information; random CV in related populations
overstating accuracy; association presented as causation; one environment.

## 5. Crop physiology and abiotic stress

Check:
- Stress imposition is **quantified**: soil water content/potential or field capacity percentage,
  VPD/temperature measured, duration, stage; control genuinely unstressed; recovery phase if
  claimed.
- Timing and stage of measurement; diurnal effects; leaf age; measurement protocols and
  instrument settings (gas exchange, chlorophyll fluorescence, water potential).
- Tolerance indices (SSI, STI, etc.): limits acknowledged; relative vs absolute performance.
- Mechanistic claims (osmotic adjustment, ROS scavenging, hormone signalling) supported by
  measurements that test the mechanism, not just correlation with tolerance.
- Pot size and soil volume effects; edge effects in growth chambers; chamber replication
  (one chamber per treatment = confounded).
- Translation from seedling/hydroponic assays to field performance not assumed.
- Combined stresses are not additive; check designs that test interactions.

## 6. Phenotyping, UAV / remote sensing and machine learning

Check (with `statistical-review.md` section 8):
- Sensor and platform specifications, altitude, GSD, overlap, calibration panels,
  illumination conditions, timing relative to ground truth.
- Ground truth quality, sampling matched spatially/temporally to imagery, annotation process
  and inter-annotator agreement.
- Spatial autocorrelation and leakage between neighbouring plots/dates; independent test fields
  or seasons.
- Index choice justified; saturation of NDVI at high biomass noted when relevant.
- Deep learning: dataset size and diversity, augmentation, split by plant/plot/field not by
  image, class imbalance, comparison with simple baselines, failure cases shown, performance
  across conditions (cultivar, growth stage, lighting).
- Claims about phenotyping "throughput" or "accuracy" report error in original units.

## 7. Genomics, transcriptomics, molecular biology, bioinformatics

Check:
- Biological replicates (not only technical), sample collection and handling, randomisation of
  processing (batch confounded with treatment is a design flaw), RNA/DNA quality.
- Sequencing depth, library prep, reference genome and annotation versions, software versions
  and parameters, filtering thresholds.
- Differential expression: count-based methods on raw counts; design formula including
  batch; normalisation; FDR threshold and effect size cut-offs justified; validation of key
  genes by independent method (qPCR with reference-gene stability, MIQE) where claims rest on
  them.
- Enrichment analyses: correct background gene set; multiple testing; interpretation not
  overstated.
- Gene function claims: knockouts/overexpression with multiple independent lines, appropriate
  controls, off-target assessment for editing, segregation analysis, complementation where
  claimed; expression correlation alone does not prove function.
- Data deposition: accession numbers (GEO/SRA/ENA), code for pipelines.
- Western blots/gels: full uncropped images available, loading controls, quantification
  replicates. Report image concerns neutrally and to the editor.

## 8. Soil science, sustainable agriculture, agronomic management

Check:
- Sampling design: depth, number of cores, compositing, timing, spatial independence,
  replication at the level of the management unit (e.g. fields), not only samples within one
  field; long-term trials often have limited true replication: ask how this was handled.
- Methods: analytical methods stated and appropriate (e.g. organic carbon method and carbonate
  handling), detection limits, quality controls, laboratory.
- Carbon/nutrient stocks: bulk density measured and stocks calculated on an equivalent soil
  mass basis when management changes density; depth increments consistent.
- Soil microbiome: see plant pathology microbiome notes; link to function needs measurements.
- Sustainability claims (carbon sequestration, emissions, biodiversity, water use): scope,
  system boundary, time horizon, baseline; life-cycle or economic assessments report
  assumptions and uncertainty; permanence and additionality language cautious.
- Practice comparisons (tillage, cover crops, amendments, biochar): confounding with site,
  history and farmer choice in observational comparisons; matched pairs or paired design.

## 9. Statistical modelling and reproducible scientific computing

Check: model specification and identifiability, parameter estimation and uncertainty,
calibration against independent data, sensitivity analysis, validation versus fitting,
numerical stability, code availability with versions and seeds, archived data/model outputs,
and whether conclusions extrapolate beyond the calibrated range.

## 10. Deriving a module for an unfamiliar discipline

Ask, in order: (1) What is the unit of replication in this field, and what would
pseudoreplication look like here? (2) What are the standard controls and negative/positive
checks? (3) What are the known measurement pitfalls and confounders? (4) What reporting
standards or minimum-information guidelines exist? (5) What claims does this field consider
too strong for the type of evidence offered? Use web search to confirm field conventions
rather than inventing them, cite what you retrieved, and mark remaining gaps as "outside my
reliable expertise".
