#!/usr/bin/env python3
"""Regression tests for ordered visible-text inventory comparison."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_fixture(path: Path) -> None:
    container = '''<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="EPUB/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>'''
    opf = '''<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier>fixture</dc:identifier></metadata>
  <manifest><item id="chapter" href="text/chapter.xhtml" media-type="application/xhtml+xml"/></manifest>
  <spine><itemref idref="chapter"/></spine>
</package>'''
    xhtml = '''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<body><h1>Generated title</h1><h2>Visible heading</h2>
<p>Body <span epub:type="pagebreak"></span>text after anchor.</p>
<figure><p>Spatial labels excluded from inventory.</p></figure></body></html>'''
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("EPUB/content.opf", opf)
        archive.writestr("EPUB/text/chapter.xhtml", xhtml)


def run(source: Path, epub: Path, report: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "compare_text_inventory.py"),
            str(source),
            str(epub),
            "--exclude-tag", "h1",
            "--exclude-tag", "figure",
            "--exclude-epub-type", "pagebreak",
            "--json", str(report),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="epub-inventory-test-") as temporary:
        work = Path(temporary)
        epub = work / "fixture.epub"
        source = work / "source.txt"
        report = work / "report.json"
        build_fixture(epub)

        source.write_text("Visible heading Body text after anchor.\n", encoding="utf-8")
        matched = run(source, epub, report)
        assert matched.returncode == 0, matched.stdout
        assert json.loads(report.read_text(encoding="utf-8"))["exact_normalized_match"] is True

        source.write_text("Visible heading Body text.\n", encoding="utf-8")
        mismatched = run(source, epub, report)
        assert mismatched.returncode == 1, mismatched.stdout
        result = json.loads(report.read_text(encoding="utf-8"))
        assert result["exact_normalized_match"] is False
        assert result["extra_word_occurrences"] > 0
    print("PASS: ordered visible-text inventory comparison and exclusions")


if __name__ == "__main__":
    main()
