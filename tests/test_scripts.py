"""Tests for the scientific-peer-review scripts.  Run:  python -m unittest discover -s tests -v

Covers: statistics checks (known values), ledger validation (including the 'quote must exist'
rule), DOCX annotation (exact anchoring across split runs, tables, typographic quotes,
paragraph fallback, editor-comment exclusion, original untouched), verification (including a
deliberately tampered file that MUST fail), and PDF annotation (skipped if PyMuPDF or
LibreOffice is missing).
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import ledger as L  # noqa: E402
import stat_checks as S  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


class TestStats(unittest.TestCase):
    def test_pvalue_catches_planted_error(self):
        ok, p, _, msg = S.check_pvalue("F", "2.91", 3, 20, "0.012")
        self.assertFalse(ok)
        self.assertAlmostEqual(p, 0.0598, places=3)
        self.assertIn("conclusion at alpha", msg)

    def test_pvalue_accepts_correct_and_inequality(self):
        self.assertTrue(S.check_pvalue("F", "2.91", 3, 20, "0.059")[0])
        self.assertTrue(S.check_pvalue("t", "3.50", 38, None, "<0.01")[0])
        self.assertFalse(S.check_pvalue("t", "1.50", 38, None, "<0.05")[0])

    def test_pvalue_rounding_tolerance(self):
        # t = 2.02 (df 38) -> p between 0.0499 and 0.0510 depending on rounding of t
        self.assertTrue(S.check_pvalue("t", "2.02", 38, None, "0.050")[0])

    def test_grim(self):
        self.assertFalse(S.grim(3.47, 25, 2)[0])
        self.assertTrue(S.grim(3.48, 25, 2)[0])
        self.assertTrue(S.grim(3.5, 10, 1)[0])

    def test_df(self):
        self.assertEqual(S.expected_df("crd", t=4, r=6)["error"], 20)
        self.assertEqual(S.expected_df("rcbd", t=4, r=6)["error"], 15)
        self.assertEqual(S.expected_df("latin", t=4)["error"], 6)
        sp = S.expected_df("splitplot", a=2, b=3, r=4)
        self.assertEqual((sp["whole_plot_error"], sp["subplot_error"]), (3, 12))

    def test_cli_exit_codes(self):
        self.assertEqual(run(SCRIPTS / "stat_checks.py", "pct", "--old", "4.82", "--new", "5.71",
                             "--reported", "23").returncode, 1)
        self.assertEqual(run(SCRIPTS / "stat_checks.py", "pct", "--old", "4.82", "--new", "5.71",
                             "--reported", "18.5").returncode, 0)


def make_docx(path: Path):
    from docx import Document
    d = Document()
    d.add_heading("Methods", 1)
    p = d.add_paragraph()
    p.add_run("Plants were grown in ")
    r = p.add_run("four greenhouse benches")
    r.bold = True
    p.add_run(", one bench per \u201cbiochar rate\u201d, and analysed by one-way ANOVA.")
    d.add_paragraph("Disease severity was scored on a 0\u20135 scale; no scale definition is given.")
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text = "Treatment"
    t.cell(0, 1).text = "Yield (t/ha)"
    t.cell(1, 0).text = "Control"
    t.cell(1, 1).text = "4.82 \u00b1 0.31"
    d.add_heading("Results", 1)
    d.add_paragraph("Biochar increased yield by 23% (Table 1).")
    d.save(str(path))


LEDGER = {
    "manuscript": "t.docx",
    "comments": [
        {"id": "C-001", "severity": "Critical", "status": "confirmed", "category": "design",
         "location": {"section": "Methods", "block": "P1"},
         "quote": "one bench per \"biochar rate\"",       # straight quotes vs curly in file
         "comment": "Treatment is confounded with bench.",
         "rationale": "No replication at the level the treatment was applied.",
         "required_revision": "State the experimental unit; address pseudoreplication."},
        {"id": "C-002", "severity": "Minor", "status": "confirmed", "category": "reporting",
         "location": {"section": "Methods", "block": "P2"},
         "quote": "no scale definition is given",
         "comment": "Define the 0-5 scale."},
        {"id": "C-003", "severity": "Major", "status": "confirmed", "category": "consistency",
         "location": {"table": "Table 1", "block": "T0.r1c1"},
         "quote": "4.82 \u00b1 0.31", "comment": "State whether +/- is SD or SE.",
         "rationale": "Unlabelled dispersion cannot be interpreted.",
         "required_revision": "Label the dispersion measure."},
        {"id": "C-004", "severity": "Major", "status": "confirmed", "category": "consistency",
         "location": {"section": "Results", "block": "P4"},
         "quote": "increased yield by 23%", "comment": "Does not match table.",
         "rationale": "Recomputed change is 18.5%.", "required_revision": "Correct it."},
        {"id": "C-005", "severity": "Minor", "status": "question", "category": "reporting",
         "audience": "editor", "location": {"section": "Results"},
         "comment": "Editor-only note: possible overlap with prior submission."},
        {"id": "C-006", "severity": "Major", "status": "probable", "category": "reproducibility",
         "location": {"section": "Methods", "absent": True},
         "comment": "Inoculum concentration is not reported.",
         "rationale": "Needed for replication.", "required_revision": "Report it."},
    ],
}


class TestEditorNotes(unittest.TestCase):
    def test_editor_comment_needs_no_quote_or_rationale(self):
        led = {"comments": [{"id": "C-001", "severity": "Major", "status": "confirmed",
                             "category": "design", "audience": "editor",
                             "location": {"section": "Methods"}, "comment": "Confidential."}]}
        errs, warns = L.validate(led)
        self.assertEqual(errs, [])
        self.assertEqual(warns, [])


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.src = cls.tmp / "t.docx"
        make_docx(cls.src)
        cls.led = cls.tmp / "ledger.json"
        cls.led.write_text(json.dumps(LEDGER), encoding="utf-8")
        cls.out = cls.tmp / "out"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_1_extract(self):
        r = run(SCRIPTS / "extract_manuscript.py", self.src, "--out-dir", self.tmp)
        self.assertIn("Extracted", r.stdout, r.stderr)
        m = json.loads((self.tmp / "t.map.json").read_text())
        ids = [b["id"] for b in m["blocks"]]
        self.assertIn("P1", ids)
        self.assertIn("T0.r1c1", ids)

    def test_2_ledger_validates_and_rejects_invented_quote(self):
        r = run(SCRIPTS / "ledger.py", "validate", self.led, "--map", self.tmp / "t.map.json")
        self.assertEqual(r.returncode, 0, r.stdout)
        bad = json.loads(json.dumps(LEDGER))
        bad["comments"][1]["quote"] = "a sentence that is not in the manuscript at all"
        errs, _ = L.validate(bad, str(self.tmp / "t.map.json"))
        self.assertTrue(any("NOT FOUND" in e for e in errs))

    def test_3_ledger_flags_invented_numbers_and_missing_fields(self):
        bad = json.loads(json.dumps(LEDGER))
        bad["comments"][3]["suggested_correction"] = "Biochar increased yield by 31%."
        _, warns = L.validate(bad, str(self.tmp / "t.map.json"))
        self.assertTrue(any("31" in w for w in warns))
        bad2 = {"comments": [{"id": "C-001", "severity": "Major", "status": "confirmed",
                              "category": "design", "location": {"section": "x"},
                              "comment": "x"}]}
        errs, _ = L.validate(bad2)
        self.assertTrue(any("rationale" in e for e in errs))

    def test_4_annotate_docx(self):
        run(SCRIPTS / "extract_manuscript.py", self.src, "--out-dir", self.tmp)
        r = run(SCRIPTS / "annotate_docx.py", self.src, self.led, "--out-dir", self.out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = json.loads((self.out / "t_anchoring_report.json").read_text())
        prec = {c["id"]: c["anchoring"] for c in rep["comments"]}
        self.assertEqual(prec["C-001"], "exact")      # across split run + curly quotes
        self.assertEqual(prec["C-003"], "exact")      # table cell
        self.assertEqual(prec["C-006"], "section")    # absence comment -> heading
        self.assertNotIn("C-005", prec)               # editor-only comment not inserted
        self.assertTrue((self.out / "t_original.docx").exists())

    def test_5_verify_passes_and_detects_tampering(self):
        args = ["--original", self.src, "--annotated", self.out / "t_annotated.docx",
                "--ledger", self.led, "--report", self.out / "t_anchoring_report.json"]
        r = run(SCRIPTS / "verify_annotations.py", *args)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("anchored exactly", r.stdout)
        # tamper: change author text in the annotated copy -> verification must FAIL
        from docx import Document
        d = Document(str(self.out / "t_annotated.docx"))
        d.paragraphs[2].runs[0].text = "Altered text. "
        tampered = self.tmp / "tampered.docx"
        d.save(str(tampered))
        args2 = ["--original", self.src, "--annotated", tampered, "--ledger", self.led]
        r2 = run(SCRIPTS / "verify_annotations.py", *args2)
        self.assertNotEqual(r2.returncode, 0)
        self.assertIn("text differs", r2.stdout)

    def test_6_original_untouched(self):
        import hashlib
        rep = json.loads((self.out / "t_anchoring_report.json").read_text())
        self.assertEqual(rep["original_sha256"],
                         hashlib.sha256(self.src.read_bytes()).hexdigest())

    def test_7_render_with_libreoffice(self):
        if not shutil.which("soffice"):
            self.skipTest("LibreOffice not installed")
        r = run(SCRIPTS / "verify_annotations.py", "--original", self.src, "--annotated",
                self.out / "t_annotated.docx", "--ledger", self.led, "--render")
        self.assertIn("renders", r.stdout, r.stdout + r.stderr)


class TestPdf(unittest.TestCase):
    def test_pdf_roundtrip(self):
        try:
            import pymupdf  # noqa: F401
        except ImportError:
            self.skipTest("PyMuPDF not installed")
        soffice = shutil.which("soffice")
        if not soffice:
            self.skipTest("LibreOffice not installed")
        tmp = Path(tempfile.mkdtemp())
        try:
            src = tmp / "t.docx"
            make_docx(src)
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(tmp),
                            str(src)], capture_output=True, timeout=180)
            pdf = tmp / "t.pdf"
            self.assertTrue(pdf.exists())
            led = tmp / "l.json"
            pdf_ledger = {"comments": [
                {"id": "C-001", "severity": "Major", "status": "confirmed", "category": "design",
                 "location": {"section": "Methods", "page": 1},
                 "quote": "four greenhouse benches", "comment": "Bench confounded.",
                 "rationale": "r", "required_revision": "r"},
                {"id": "C-002", "severity": "Minor", "status": "confirmed", "category": "writing",
                 "location": {"section": "Results", "page": 1},
                 "quote": "this exact phrase is not in the pdf", "comment": "page note case"},
                {"id": "C-003", "severity": "Minor", "status": "question", "category": "writing",
                 "audience": "editor", "location": {"section": "x"}, "comment": "editor only"}]}
            led.write_text(json.dumps(pdf_ledger))
            out = tmp / "out"
            r = run(SCRIPTS / "annotate_pdf.py", pdf, led, "--out-dir", out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rep = json.loads((out / "t_anchoring_report.json").read_text())
            prec = {c["id"]: c["anchoring"] for c in rep["comments"]}
            self.assertEqual(prec["C-001"], "exact")
            self.assertEqual(prec["C-002"], "page-note")
            self.assertNotIn("C-003", prec)
            v = run(SCRIPTS / "verify_annotations.py", "--original", pdf, "--annotated",
                    out / "t_annotated.pdf", "--ledger", led, "--report",
                    out / "t_anchoring_report.json")
            self.assertEqual(v.returncode, 0, v.stdout + v.stderr)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
