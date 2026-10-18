# Line-by-line audit (exhaustive mode)

Use this for every full review and whenever the user asks for "word by word", "line by line",
"every error", "typos", "grammar", "unscientific language" or "improve the paper quality". In
**exhaustive mode nothing is skipped**: every paragraph, sentence, table cell, caption and
reference is read, and every confirmed problem becomes its own ledger entry with the exact
original wording and a corrected version. (The default "standard" mode groups recurring style
issues; exhaustive mode does not.)

Why this exists: scientific-content review alone leaves authors with a manuscript that is still
full of typos, sloppy wording, undefined abbreviations, inconsistent numbers, and references that
cannot be located. Journals and editors judge these first. This file makes the language and
reporting audit as strict as the science audit, without inventing problems.

## Contents
1. Procedure (what to do, in order)
2. Per-paragraph checklist
3. Scientific language: wording that must be flagged
4. Typical error patterns (language, typography, notation)
5. Numbers, units and statistics notation
6. Abbreviations, terminology and consistency
7. Claims, support and citations inside the text
8. Writing every correction safely
9. Severity for line-level issues
10. Coverage statement and anti-fabrication rules

---

## 1. Procedure

1. Run `scripts/extract_manuscript.py`, then `scripts/lint_text.py --spell` on the map. The
   linter gives **candidates**; it never replaces reading.
2. Read the manuscript in order, paragraph by paragraph (use `<stem>.blocks.txt`). For each
   paragraph apply section 2, write ledger entries immediately, and keep a running tally
   (paragraphs read / with issues / clean).
3. Then go through every **table, table footnote, figure caption and legend**, then the
   **reference list** (see `reference-audit.md`), then supplementary lists, declarations,
   acknowledgements, author contributions and data availability.
4. Go through the linter candidates one by one: confirm (read the sentence), reject (false
   positive), or merge into an existing comment. Do not copy unverified candidates.
5. Run the global consistency passes (section 6) that need the whole text: abbreviations,
   terminology, hyphenation, spelling variety, citation style, numbering.
6. Run the figure/table audit (`figure-table-audit.md`) and the completeness check
   (`completeness-checklist.md`).
7. Quality-control pass (`quality-control.md`), then annotate and build the Word report.

## 2. Per-paragraph checklist

For each paragraph, in this order:

| # | Question | Typical finding |
|---|---|---|
| 1 | **Spelling and typing**: every word | typos, wrong word (affect/effect, principle/principal), missing letters |
| 2 | **Grammar**: agreement, tense, articles, prepositions, plural/singular | "it does not explains", "phenotypic variance account", "Data was", "a ... variable ... they" |
| 3 | **Punctuation and spacing** | missing/double spaces, comma splices, missing space before `[n]`, stray full stops |
| 4 | **Sentence structure** | run-ons, fragments, 40+ word sentences, ambiguous "This/These/It", dangling modifier |
| 5 | **Word choice and tone** (section 3) | promotional, informal, vague, absolute, causal claims on correlational data |
| 6 | **Terminology** | same thing named differently; wrong technical term; symbol without definition |
| 7 | **Numbers and units** (section 5) | wrong unit, inconsistent decimals, text vs table mismatch, range wrong |
| 8 | **Cross-references** | "Table 1" where Table 4 is meant; supplement number swapped; missing figure/table citation |
| 9 | **Support**: does each factual or interpretive claim have evidence or a citation? | generic statements with no citation; causal claim with no test |
| 10 | **Logic and flow**: does the paragraph do what its topic sentence says; does it contradict another paragraph? | contradiction between Results and Discussion; conclusion not matched by data |
| 11 | **Missing**: what should be here and is absent? | undefined term, missing method detail, missing citation, missing statistic |

If a paragraph is clean, move on (and count it as clean). Do not invent a comment to "show effort".

## 3. Scientific language: wording that must be flagged

Flag each occurrence once per sentence, explain why, and give a neutral replacement.

| Pattern | Problem | Neutral alternative |
|---|---|---|
| obviously, clearly, of course, naturally | asserts what should be shown | delete, or state the evidence |
| immense, huge, tremendous, amazing, remarkable | promotional/non-quantitative | give the measured size |
| tedious, simple, easy, trivial | subjective | state time, cost, or steps |
| prove(s), proven | data rarely prove | indicate, suggest, support |
| superfood, miracle, wonder crop | marketing language | state the nutrient content with numbers and citation |
| novel, unique, first (self-assessed) | novelty is for readers to judge | state the concrete difference from earlier work, after checking the literature |
| very, highly, extremely, a lot of | vague intensifiers | quantify |
| well known / widely accepted (no citation) | unsupported authority | cite, or delete |
| numerous studies, many researchers, recent years | vague | cite and give the period |
| best, ideal, optimal, perfect | superlative without comparison | state the comparison and the data |
| always, never, all, every, none | absolute | check it is literally true |
| due to, caused by, leads to, responsible for, explained by | causal claim | needs a design or measurement that supports causality; otherwise "associated with", "possibly because" |
| reflects, indicates, shows (applied to speculation) | interpretation presented as result | "may reflect", "is consistent with" |
| significant / significantly without a test | statistical term used loosely | give the test and P, or use "marked/substantial" |
| we believe/feel, in our opinion | opinion | evidence-based statement |
| should be (applied by farmers/breeders) from a single-environment trial | recommendation beyond evidence | "may be considered", and state the limits |
| it is necessary / it is essential / crucial (many times) | emphasis inflation | say what is gained |

Also flag **template and translation-like prose** (adapted from the sources): sentence-initial
"Thus,/Similarly,/Moreover," repeated across a paragraph; "in terms of", "with respect to",
"plays a major/critical role", "It can be seen that", "In recent years", "numerous studies have
shown", "state-of-the-art", "extensive experiments"; three consecutive sentences with the same
structure; stacked near-synonyms (important, crucial, essential). Report the pattern with 2-3
examples and the paragraph, then rewrite the weakest one.

## 4. Typical error patterns

- **Subject-verb and verb forms**: "does not explains", "account for" with singular subject,
  "was performed ... were" mixing.
- **Tense**: Methods/Results in past tense; established facts in present; do not alternate within
  a paragraph without reason.
- **Articles and prepositions**: missing "the", "a"; "in terms of yield improvement" vs
  "for yield improvement".
- **Plurals**: data (plural), "traits were", "an immense avenue" (idiomatic problems).
- **Spacing and punctuation**: double spaces, missing space after full stop, space before comma,
  citation attached to a word (`Nepal[16-19]`), heading text glued to the last sentence of the
  previous section.
- **Hyphenation**: broad-sense heritability (adjective) vs broad sense; thousand-seed weight;
  cream-coloured; be consistent.
- **Spelling variety**: US vs UK within one document (analyzed/analysed, color/colour).
- **Capitalisation**: Latin names (italic genus/species, capitalised genus only), trait names in
  legends capitalised inconsistently, "Table"/"Fig." in text.
- **Sentence-initial numerals or symbols**.
- **Garbled symbols** from copy-paste: lost multiplication signs (`5 m2 m`), lost Greek letters,
  empty brackets around equations, superscripts lost (`m2`, `h2b`, `t ha-1`).
- **Typos in names and cultivars**: spelling of cultivar/landrace names must be identical across
  text, tables and legends (check each).
- **Repeated or contradictory statements** in neighbouring paragraphs.

## 5. Numbers, units and statistics notation

- Every number in the text that appears in a table must **equal** the table (check ranges,
  means, percentages, counts; show both values when they differ).
- Units: correct for the trait (a length in cm, not g; a count has no unit); SI style
  (t ha-1 or Mg ha-1, one style throughout; "ton" vs "t"); superscripts rendered; space between
  number and unit; degree sign style for coordinates identical everywhere.
- Decimal places consistent within a column and between text and tables; significant digits
  justified; range endpoints with the same precision.
- Statistical notation: italic *P*, *F*, *t*, *n*; "P < 0.001" vs "P = 0.0004"; mean ± SD/SE
  stated; df reported with F; the same alpha level used; "P ≤ 0.05" in the abstract vs
  "P < 0.001" in the results must be the same statement or explained.
- Table vs text vs abstract vs conclusion: all quantitative statements agree (run the
  cross-check in `review-framework.md` s.4 and `scripts/stat_checks.py`).
- Verify arithmetic you rely on: percentages, ratios, means of ranges, df.

## 6. Abbreviations, terminology and consistency (whole-document passes)

- Define each abbreviation at first use in the **abstract and main text separately** (many
  journals require both), and in each table/figure legend if used there. Report: used but
  undefined; defined but never used; one code with two meanings; two codes for one thing; an
  expansion that differs between text and legend (e.g. "variance" vs "variation").
- One name per concept: landrace/accession/genotype, cultivar/variety, trait names, method
  names. List the variants found.
- Technical meaning: do not use heritability and genetic advance interchangeably; "genetic
  gain" vs "genetic advance"; correlation is not causation; path analysis decomposes correlations
  under an assumed causal model, it does not prove causality; "significant" is statistical;
  "resistance" vs "tolerance"; "yield attributing/contributing" consistent.
- Table/figure/section numbering is sequential, every item is cited and interpreted, every
  citation resolves (section 7 of `figure-table-audit.md`), and supplementary tables have the
  content the text says they have.

## 7. Claims, support and citations inside the text

- Each non-obvious factual statement needs a citation; each citation must plausibly support
  the sentence it follows (verify the important ones, `literature-and-integrity.md` s.4).
- Statements about other work ("consistent with X et al.") must match what that work found;
  if you could not check, ask.
- Mechanistic/biological explanations in the Discussion need evidence from the study or a
  citation, and must be worded as hypotheses when untested.
- Recommendations must follow from the data and conditions of the study. Flag any sentence in
  the Abstract/Conclusion that is stronger than the Results.
- Check for **contradiction between sections** (e.g. negative association interpreted as "short
  plants are productive" while the same paragraph says correlations were non-significant).
- Statements of novelty, importance or gap need support.
- Text that appears copied from a standard definition without citation: ask for a citation.

## 8. Writing every correction safely

- Quote the **exact** original words (short, but enough to find: a clause or sentence).
- Give `suggested_correction` as the corrected wording of that same span, preserving meaning.
  For plain typos and grammar the correction is the fact; for rewording, mark it as an
  example. When the meaning is unclear, do not guess: make the comment a `question`.
- Do not change numbers, names or claims in a correction. If a number conflicts with a table,
  say which two places disagree and ask the authors; do not decide which is right.
- One finding per ledger entry. For a recurring pattern (e.g. 'Similarly' x9) give one entry for
  the pattern **plus** one entry per instance only when each needs its own correction.
- Keep the tone neutral and specific.

## 9. Severity for line-level issues

| Issue | Severity |
|---|---|
| Typo, spacing, punctuation, hyphenation, capitalisation, spelling variety | Minor |
| Grammar error that does not change meaning | Minor |
| Wording that is ambiguous or changes the scientific meaning | Major (Minor if the meaning is recoverable) |
| Wrong unit; text value different from table; wrong table/figure/supplement reference; undefined or conflicting abbreviation used in a result | Major if it affects interpretation, else Minor |
| Unscientific/promotional wording in Abstract, Conclusion or a key claim | Major; elsewhere Minor |
| Causal/mechanistic claim without support | Major (see the science review) |
| Template phrases, connector overuse | Optional/Minor |
| Missing citation for a specific factual claim | Minor to Major depending on how load-bearing it is |

## 10. Coverage statement and anti-fabrication rules

- The report must state coverage: "N paragraphs, M tables (C cells), K figure captions and R
  references read in full; the linter produced X candidates, Y confirmed."
- A comment is allowed only if you can point at the exact words. No "this paper has many
  grammar errors" without examples; no invented errors.
- Do not flag as error what is a valid variant (e.g. serial comma, `ear head` vs `earhead`) unless
  it is inconsistent within the paper or against a stated journal style.
- Domain names (cultivars, landraces, places, species authorities) are spelled by the authors:
  do not "correct" them unless they differ between locations in the same manuscript.
- If a correction would change the science, route it to the science comments.
