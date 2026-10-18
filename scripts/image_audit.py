#!/usr/bin/env python3
"""Audit the technical quality of figures embedded in a DOCX or PDF, and save viewable previews.

    python image_audit.py MANUSCRIPT.docx --out images_audit.json --preview-dir previews/
    python image_audit.py MANUSCRIPT.pdf  --out images_audit.json --preview-dir previews/

For every embedded image it reports: format, pixel size, colour mode, file size, printed size on
the page (from the document), EFFECTIVE resolution (pixels / printed inches), aspect distortion,
whether alt text exists, and the caption paragraph that follows it (DOCX).

Typical journal thresholds used for flags (adjust to the journal's guidelines when known):
  photographs / colour images   >= 300 dpi at final size
  line art / graphs             >= 600 dpi (or vector)    (1-bit images are treated as line art)
  width                         <= ~7 in for a double-column figure (<= ~3.5 in single column)
  lossy JPEG for graphs/line art flagged (compression artefacts around text)

What it cannot do: judge legibility of axis text, label correctness, colour-blind safety or
whether error bars are shown. Those need LOOKING at the figure: the preview PNGs are written so
you can open and inspect each one with the image viewer, and the report must say which figures
you actually viewed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

EMU_IN = 914400.0


def flags_for(fmt, mode, px, inch, desc, caption, filesize):
    out = []
    if not inch[0] or not inch[1]:
        return out
    dpi_x, dpi_y = px[0] / inch[0], px[1] / inch[1]
    line_art = mode in ("1", "L") and fmt in ("TIFF", "PNG", "GIF")
    need = 600 if mode == "1" else 300
    if min(dpi_x, dpi_y) < need:
        out.append(("low-resolution", "Major" if min(dpi_x, dpi_y) < 150 else "Minor",
                    f"Effective resolution {min(dpi_x, dpi_y):.0f} dpi at the printed size "
                    f"(guideline >= {need} dpi{' for line art' if mode == '1' else ''})."))
    if dpi_x and dpi_y and abs(dpi_x - dpi_y) / max(dpi_x, dpi_y) > 0.05:
        out.append(("aspect-distortion", "Minor", f"Horizontal {dpi_x:.0f} vs vertical {dpi_y:.0f} dpi: "
                    "the image appears stretched."))
    if fmt == "JPEG":
        out.append(("lossy-format", "Optional", "JPEG is lossy; vector (PDF/EPS/SVG) or TIFF/PNG is preferred "
                    "for graphs and line art."))
    if inch[0] > 7.3:
        out.append(("oversize", "Optional", f"Printed width {inch[0]:.1f} in exceeds a typical double-column width."))
    if not desc:
        out.append(("no-alt-text", "Optional", "No alternative text (accessibility)."))
    if caption is not None and not re.match(r"\s*(Fig|Figure)\b", caption or "", re.I):
        out.append(("no-caption-found", "Minor", "No 'Fig./Figure N' caption found next to the image."))
    return out


def audit_docx(path: Path, preview_dir: Path | None):
    from docx import Document
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    doc = Document(str(path))
    z = zipfile.ZipFile(path)
    rels = {r.rId: r for r in doc.part.rels.values()}
    body = list(doc.element.body.iterchildren())
    results = []
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
    R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    for idx, el in enumerate(body):
        if el.tag != qn("w:p"):
            continue
        for dr in el.iter(qn("w:drawing")):
            blip = next(dr.iter(A + "blip"), None)
            if blip is None:
                continue
            rid = blip.get(R + "embed")
            rel = rels.get(rid)
            if rel is None:
                continue
            name = rel.target_ref
            data = z.read("word/" + name) if not name.startswith("/") else z.read(name.lstrip("/"))
            ext = next(dr.iter(WP + "extent"), None)
            inch = (int(ext.get("cx")) / EMU_IN, int(ext.get("cy")) / EMU_IN) if ext is not None else (0, 0)
            dp = next(dr.iter(WP + "docPr"), None)
            desc = (dp.get("descr") or "").strip() if dp is not None else ""
            import io
            try:
                im = Image.open(io.BytesIO(data))
                fmt, mode, px = im.format, im.mode, im.size
                info_dpi = im.info.get("dpi")
                comp = im.info.get("compression")
            except Exception as e:  # noqa: BLE001
                results.append({"image": name, "error": str(e)})
                continue
            # caption: this paragraph's text, else next non-empty paragraph
            cap = Paragraph(el, doc).text.strip()
            j = idx + 1
            while not cap and j < len(body):
                if body[j].tag == qn("w:p"):
                    cap = Paragraph(body[j], doc).text.strip()
                j += 1
                if j - idx > 4:
                    break
            if not re.match(r"\s*(Fig|Figure)\b", cap or "", re.I):
                # sometimes the caption sits ABOVE
                k = idx - 1
                while k >= 0 and k > idx - 3:
                    if body[k].tag == qn("w:p"):
                        t = Paragraph(body[k], doc).text.strip()
                        if re.match(r"\s*(Fig|Figure)\b", t, re.I):
                            cap = t
                            break
                    k -= 1
            prev = None
            if preview_dir:
                preview_dir.mkdir(parents=True, exist_ok=True)
                prev = preview_dir / (Path(name).stem + ".png")
                v = im.convert("RGB") if im.mode not in ("RGB", "L") else im
                if v.width > 1800:
                    v = v.resize((1800, int(v.height * 1800 / v.width)))
                v.save(prev)
            fl = flags_for(fmt, mode, px, inch, desc, cap, len(data))
            results.append({
                "image": name, "format": fmt, "mode": mode, "pixels": px, "file_kb": round(len(data) / 1024),
                "printed_inches": [round(inch[0], 2), round(inch[1], 2)],
                "effective_dpi": [round(px[0] / inch[0]), round(px[1] / inch[1])] if inch[0] and inch[1] else None,
                "embedded_dpi_metadata": [round(float(x), 1) for x in info_dpi] if info_dpi else None, "tiff_compression": comp,
                "alt_text": desc, "caption": cap[:200], "preview": str(prev) if prev else None,
                "flags": [{"issue": a, "severity_suggestion": b, "message": c} for a, b, c in fl]})
    return results


def audit_pdf(path: Path, preview_dir: Path | None):
    import pymupdf
    d = pymupdf.open(str(path))
    results = []
    for pno, page in enumerate(d, start=1):
        for info in page.get_image_info(xrefs=True):
            w, h = info["width"], info["height"]
            bb = info["bbox"]
            inch = ((bb[2] - bb[0]) / 72, (bb[3] - bb[1]) / 72)
            if inch[0] < 0.4 and inch[1] < 0.4:
                continue          # ignore icons/rules
            prev = None
            if preview_dir:
                preview_dir.mkdir(parents=True, exist_ok=True)
                prev = preview_dir / f"page{pno}_img{info['xref']}.png"
                page.get_pixmap(clip=pymupdf.Rect(bb), dpi=150).save(prev)
            fl = flags_for("", "RGB", (w, h), inch, "x", "Fig", 0)
            results.append({"page": pno, "pixels": [w, h], "printed_inches": [round(inch[0], 2), round(inch[1], 2)],
                            "effective_dpi": [round(w / inch[0]), round(h / inch[1])], "preview": str(prev) if prev else None,
                            "flags": [{"issue": a, "severity_suggestion": b, "message": c} for a, b, c in fl
                                      if a in ("low-resolution", "aspect-distortion", "oversize")]})
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("manuscript")
    ap.add_argument("--out", default="images_audit.json")
    ap.add_argument("--preview-dir")
    a = ap.parse_args()
    src = Path(a.manuscript)
    pd = Path(a.preview_dir) if a.preview_dir else None
    if src.suffix.lower() == ".docx":
        res = audit_docx(src, pd)
    elif src.suffix.lower() == ".pdf":
        res = audit_pdf(src, pd)
    else:
        sys.exit("Only .docx and .pdf are supported.")
    Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(res)} image(s) found.")
    for r in res:
        if "error" in r:
            print("  ERROR", r["image"], r["error"])
            continue
        print(f"  {r.get('image', 'page ' + str(r.get('page')))}: {r['pixels']} px, printed "
              f"{r['printed_inches']} in, effective {r['effective_dpi']} dpi"
              + (f", {r['format']}/{r['mode']}" if r.get("format") else ""))
        for f in r["flags"]:
            print(f"     [{f['severity_suggestion']}] {f['issue']}: {f['message']}")
    if pd:
        print(f"Previews in {pd}: OPEN AND LOOK AT EACH ONE; the audit cannot judge legibility, labels, "
              "error bars or colour-blind safety.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
