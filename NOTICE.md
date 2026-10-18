# Notice and attribution

**Author and maintainer: Sujan Chapagain.**

This skill was designed by auditing four open-source repositories supplied by the user. **No
source code or prompt text was copied verbatim**; ideas were adapted, rewritten and in several
cases deliberately rejected (see `docs/SOURCE_INVENTORY_AND_SYNTHESIS.md`). Each source is MIT
licensed at the time of audit (the licence file in each archive was checked). They are credited
here as a courtesy and for traceability.

| Source | Ideas adapted |
|---|---|
| `ai-peer-review-skill` (paper-review skill) | Multiple review lenses and meta-review synthesis; "do not average, do not soften" synthesis rule; cite only retrieved identifiers |
| `AI-paper-reviewer` | Cross-section numeric/claim consistency checks; claim-hedging and "significant needs a test" heuristics; reproducibility-checklist idea; severity-tier concept (redefined here) |
| `ai-paper-review` | Writing-clarity and internal-consistency reviewer (recompute and show arithmetic; report both locations; approximate plot readings); structured comment schema; commonality x severity consolidation idea; "draft aid, not a verdict" framing |
| `open-scholar-peer` (community implementation of Google's ScholarPeer) | Claim-oriented summary before review; time-anchored literature retrieval; baseline/comparator scouting; retraction and cutoff-date discipline; "error is not empty"; "What this review did not have"; fail-loudly and human-signs-the-review principles |

The ScholarPeer method is described in: *ScholarPeer: A Context-Aware Multi-Agent Framework for
Automated Peer Review* (Google; arXiv). Cite the original paper if you build on that method.

Other references named in the skill are standard methodological literature (e.g. Hurlbert 1984 on
pseudoreplication; Benjamini and Hochberg 1995 on false-discovery-rate control; Brown and
Heathers 2017 on the GRIM test). Their names are included as pointers, not as quotations.

## Third-party dependencies (not bundled)
- python-docx (MIT), scipy (BSD), Pillow (HPND), pyspellchecker (MIT), lxml/PyYAML (BSD/MIT) - permissive.
- **PyMuPDF (AGPL-3.0, or commercial licence from Artifex)** - optional, used only by
  `annotate_pdf.py` and PDF verification. Using it in internal workflows is fine; if you
  redistribute a *product* that bundles it, check the AGPL terms or obtain a commercial licence.
  The DOCX tooling does not need it.
- LibreOffice (MPL-2.0) - optional, used for render checks.
