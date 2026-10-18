# Reference and citation audit

Use for every full review. A reference that cannot be found, is incomplete, or does not support
the sentence it is attached to is a defect in the paper, and a reference list is checked entry by
entry, not skimmed.

## Contents
1. Run the automatic audit
2. What every entry must contain
3. In-text <-> list cross-check
4. Verifying that an entry is correct (web procedure)
5. Format consistency
6. Quality of the evidence base
7. How to record findings
8. Hard rules

---

## 1. Run the automatic audit

```
python scripts/audit_references.py work/paper.map.json --out work/refs_audit.json \
    --authors "Surname1,Surname2" --submission-year 2026
```
It parses every entry, guesses its type, lists missing fields, cross-checks numbered or
author-year citations against the list, tests "Author et al. [n]" against entry n, detects duplicates,
and reports self-citation share and age of references. Findings have `verify: none` (a fact
visible in the text, e.g. "no volume") or `verify: web` (a suspicion until checked online).
It cannot tell you that a volume, year or page range is *wrong*: that needs section 4.

## 2. What every entry must contain

| Type | Required fields |
|---|---|
| Journal article | all authors (or journal's limit + et al.), year, article title, journal name (consistent full or abbreviated form), **volume**, **issue if the journal uses it**, **page range or article number**, **DOI** (if one exists) |
| Book | authors/editors, year, title, edition (if not first), publisher, place |
| Book chapter | chapter authors, year, chapter title, **editors**, book title, publisher, place, **page range** |
| Report / grey literature | organisation or authors, year, title, report number, publisher/place, **URL or repository**, access date for web-only items |
| Conference paper | authors, year, title, proceedings title, place/date or publisher, pages |
| Thesis | author, year, title, degree, institution |
| Dataset / software | authors, year, title, repository, version, DOI/URL |
| Web page | author/organisation, year, title, URL, access date |
| In press / preprint | state it, with DOI/URL; do not cite as published |

Typical defects to report, each per entry: missing volume; missing pages/article number;
missing year; missing DOI where one exists; chapter without editors/publisher/pages; a report
with no publisher or link ("cannot be located"); `et al.` inside the list where the journal wants
all authors; one author name run into another; page range with unusual punctuation
(`2010;1;489-499`); truncated title; journal name left out; year after submission date; same
reference listed twice; wrong order for numbered styles.

## 3. In-text <-> list cross-check

- Every number cited must exist in the list; every listed entry must be cited at least once
  (or removed). Numbered (Vancouver) styles require numbering in order of **first citation**.
- A narrative citation must match the entry: "Gadi et al. [38]" requires entry 38 to start with
  Gadi. Check all narrative citations, not a sample.
- Author-year: surname and year in the text must match the list; "a/b" suffixes consistent.
- Citations inside table footnotes, figure legends and supplementary text count too.
- Citation placement and punctuation are consistent (`[1, 2]` vs `[1,2]` vs `[1-2]`; space before
  bracket).
- Statements that need a citation and have none (see `line-by-line-audit.md` s.7).

## 4. Verifying that an entry is correct (web procedure)

Do this for entries the audit marked `verify: web`, entries that carry an important claim, and
every entry that looks odd (wrong-looking volume/pages/year, predatory-sounding journal, very
generic title). Use web search first, then fetch the DOI/publisher/PubMed/Crossref page if a URL
appeared in results.

1. Search "title + first author + year" (or the DOI). Open the publisher, PubMed, Crossref,
   Google Scholar, or DOAJ record.
2. Compare: authors, year, title, journal, volume, issue, pages/article number, DOI.
3. Record the outcome per entry in `report.json -> reference_verification`:
   `verified (source URL)`, `differs: <what the record says>`, or `not found`, or `not checked`.
4. Only a mismatch you saw in a retrieved record becomes a confirmed comment ("The record at
   <URL> gives volume 12, issue 11, pp. 3355-3360"). Without retrieval it is a question: "please
   check volume/pages".
5. Check retraction status for entries that carry a central claim, using the publisher page,
   Retraction Watch Database or OpenAlex `is_retracted`; if you cannot check, say it was not run.
6. Journal quality: if a reference comes from an unfamiliar journal, you may note that, but do
   not call a journal predatory without a source; say "please confirm the journal is
   reputable/indexed".
7. If search is unavailable or fails, **say so** ("online verification not possible in this
   session"); failure is not evidence that the reference is correct or wrong.

Never write a "corrected" reference from memory. Quote the retrieved record, or say the field is
missing and must be supplied by the authors.

## 5. Format consistency

- One reference style for the whole list (match the journal's if known): author format, initials,
  year position, title capitalisation, journal abbreviation or full name, volume/issue/pages
  punctuation, DOI presentation (`https://doi.org/...`), trailing full stops, `et al.` rules.
- Journal names either all abbreviated (ISO 4 / NLM) or all full; abbreviations spelled the same
  way every time the journal recurs.
- Pages: en dash (or the journal style) throughout; article numbers formatted consistently.
- Titles: sentence case vs title case consistent; Latin names italic if the journal requires it;
  species, genes and symbols formatted correctly.
- In the DOCX, DOIs/links consistent in being hyperlinked or not.

## 6. Quality of the evidence base

Report as Minor/Optional unless it undermines a claim:
- Share of references from the last 5 years and the oldest/newest year (very old sources for
  current-state statements; missing recent work, found only through search).
- Over-reliance on one group, one country, or the authors' own work (self-citation share).
- Heavy use of grey literature, working papers or non-peer-reviewed sources for central claims.
- Primary vs secondary: claims cited to reviews or unrelated crops/species (e.g. wheat or mustard
  literature cited for a finger-millet mechanism) - ask whether species-appropriate evidence
  exists, without implying it is wrong.
- Duplicate or near-duplicate entries; the manuscript's own related papers cited correctly and
  their overlap with the present data explained.

## 7. How to record findings

Each finding is a ledger entry with `category: "reference"` (or `citation` for the in-text side),
`location.block` = the reference paragraph ID, `quote` = the opening words of that entry,
`comment` = the defect, `required_revision` = what to supply, `evidence_needed` = the record
you checked (or "not verified online"). Group identical problems only when the correction is
identical (e.g. "No DOI for [23]-[26], [33], [35]..."): list the numbers, and add the individual
quote for the first one.

In the Word report, section 7 (reference audit table) is generated from `refs_audit.json`
and `report.json -> reference_verification`.

## 8. Hard rules

- Do not invent bibliographic data, DOIs, volumes or page numbers.
- Do not accuse authors of fabricating a reference; say "I could not locate it" and describe the
  search.
- State the verification status of every reference-related comment.
- A citation check of the whole list is mandatory in exhaustive mode; report how many entries
  were checked online and how many were not.
