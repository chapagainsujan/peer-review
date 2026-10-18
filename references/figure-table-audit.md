# Figure, table and image audit

Use for every manuscript that contains figures or tables. Figures are evidence: a reviewer who
did not look at them has not reviewed the Results.

## Contents
1. Procedure
2. Image technical quality
3. Figure content (what you must look at)
4. Captions and legends
5. Tables
6. Text <-> figure/table consistency
7. Recording findings

## 1. Procedure

1. `python scripts/image_audit.py paper.docx --out work/images_audit.json --preview-dir work/previews`
   lists every embedded image with pixel size, printed size, **effective dpi**, format,
   mode, alt text and caption, and saves a PNG preview.
2. **Open and look at every preview** with the image viewer. Note in `report.json -> figure_notes`
   which figures you viewed. If you cannot view an image, say so; do not describe it from its
   caption.
3. For PDF manuscripts, run the same script on the PDF; for tables, read the table text from the
   block map and, if layout matters, from a rendered page.
4. Compare each figure and table with the text that cites it (section 6).

## 2. Image technical quality

Defaults (replace with the journal's rules if known):

| Check | Guideline | Report as |
|---|---|---|
| Effective resolution | >= 300 dpi for colour/greyscale images at the printed size; >= 600 dpi for line art (or vector) | Minor (150-300), Major (< 150 or unreadable) |
| Format | vector (PDF/EPS/SVG) or lossless raster (TIFF/PNG) for graphs; avoid JPEG for line art | Optional |
| Size | single column ~8-9 cm, double column ~17-18 cm | Optional |
| Distortion | horizontal and vertical dpi equal | Minor |
| Colour mode | RGB for online, check the journal for CMYK; transparency (RGBA) can render black on some systems | Optional |
| Alt text | present for accessibility where the journal asks | Optional |
| File | image supplied as separate high-resolution files if the journal requires | Optional |

Effective resolution is what matters, not the pixel count: a 1,400 px wide image printed at
6.5 in is about 215 dpi.

## 3. Figure content (what you must look at)

- **Axes**: labelled, units correct, ticks readable, scales honest (truncated axes, log vs
  linear), **dual axes** combining unrelated quantities or units (e.g. temperature in degrees
  C and relative humidity in % on one scale), secondary axis labelled unambiguously.
- **Legend and symbols**: every line, bar, colour and symbol explained; colours distinguishable
  in greyscale and for colour-vision deficiency (red-green pairs are a problem; prefer
  colour-blind-safe palettes or add line types/markers).
- **Text size**: axis and legend text legible at final printed size (>= 6-8 pt after scaling).
- **Uncertainty**: error bars/intervals, n, and what they represent; statistical letters or
  significance marks explained; in heatmaps the correlation values and significance marks are
  given if the text relies on them (colour alone does not support a statement about "significant").
- **Data shown vs claimed**: the text's description (trends, clusters, rankings, "highest in
  July") matches the figure; every variable in the figure is covered by the description (e.g. a
  trait that appears in the dendrogram but is not placed in any cluster in the text).
- **Units and definitions**: same units as the tables and Methods; period of data matches the
  experimental period; data source stated and cited; processing described (e.g. satellite
  reanalysis vs on-site station; daily vs monthly totals).
- **Panel labels** (a, b) present and used in the legend consistently (e.g. "(a) ... (b) ...").
- **Reproduced material**: permission/credit for adapted or third-party images and maps.
- Images of gels, microscopy, plants: scale bars, whole-gel images available, unmanipulated
  images, labelled; photos have scale.

Typical defects: caption says "mm/day" but the axis shows monthly totals in mm; temperature and
humidity forced onto one axis; legend entry names not matching the caption; colour scale limits
unstated; dendrogram method (distance, linkage) not stated; no indication of what the heatmap
cells' significance is.

## 4. Captions and legends

- Starts with "Fig. N" and a title that says what the figure shows; complete sentences; all
  abbreviations defined (or defined once and used consistently); units given; n and the dispersion
  measure stated; method of clustering/ordination/test stated; data source cited.
- Panel descriptions consistent with panel letters; punctuation correct (e.g. a stray comma
  between "(a)" and "(b)"); grammar checked (number agreement: "Dendrogram illustrate").
- The caption alone makes the figure understandable.

## 5. Tables

- Title above table, footnotes below; every abbreviation and symbol (bold, asterisks, letters)
  explained; units in column headers; consistent decimal places and significant digits within a
  column; ranges use one format (`5.76-19.94`, one dash type); thousands separators consistent.
- Internal logic: totals, df, means within ranges; GCV <= PCV; heritability between 0 and 100;
  genetic advance as % of mean consistent with GA and mean; variance components non-negative; sample sizes stated.
  Recompute what you can with `scripts/stat_checks.py` and simple arithmetic (e.g.
  h2 = GV/PV, GAM = GA/mean x 100) and report mismatches with the recomputation.
- Table columns that disagree with the legend (e.g. column "Genotype" vs legend "Landrace"),
  duplicated rows, empty cells explained, stray symbols (zero-width characters, BOM) in cells.
- Significance symbols defined (*, **, ***) and used consistently with the text's alpha.
- Bold/italic meaning explained (e.g. path-analysis diagonal) and applied correctly.
- Description-vs-data: a table of traits with ranges should give the same ranges as the text
  (see `line-by-line-audit.md` s.5).
- Table width/format: tables that cannot be read at page width, merged-cell structure that breaks.
- Supplementary tables: contents match how the main text describes them; numbering
  consistent (S1 in the text vs S1 in the supplementary list).

## 6. Text <-> figure/table consistency

For each figure/table: (1) is it cited in the text, in numerical order; (2) does the paragraph
that cites it describe what it actually shows; (3) do the numbers match; (4) are all
elements of the figure/table covered; (5) are claims based on it justified by its content (a
heatmap supports "positively associated", not "significantly correlated" unless significance is
marked).

## 7. Recording findings

Ledger entries: `category: "figures-tables"`, `location.figure`/`location.table`, `quote` = the
caption's first words or the sentence that cites it, `comment`, `required_revision`. Technical image
flags come from `image_audit.py` (copy the measured numbers into the comment). Figure
observations you made by looking go into `report.json -> figure_notes` (Word report section 8).
