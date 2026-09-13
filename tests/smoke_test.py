#!/usr/bin/env python3
"""Build and validate a synthetic EPUB without using copyrighted source data."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    completed = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode:
        print(completed.stdout)
        raise SystemExit(completed.returncode)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="epub-skill-test-") as temporary:
        work = Path(temporary)
        manifest = {
            "identifier": "synthetic-smoke-test",
            "title": "EPUB Smoke Test",
            "author": "Contributors",
            "language": "zh-CN",
            "cover": str(ROOT / "tests" / "fixtures" / "cover.svg"),
            "cover_href": "images/cover.svg",
            "sections": [
                {
                    "id": "chapter-1",
                    "title": "第一章",
                    "part": "正文",
                    "language": "zh-CN",
                    "epub_type": ["chapter"],
                    "html": (
                        '<h2 id="section-1">第一节</h2>'
                        '<p>这是合成测试文本<span id="page-1" epub:type="pagebreak" title="1"></span>。</p>'
                        '<p>正文编号 1 不应自动变成脚注。'
                        '<a id="ref-1" epub:type="noteref" href="#note-1"><sup>①</sup></a></p>'
                        '<aside id="note-1" epub:type="footnote"><p>① 合成脚注。'
                        '<a href="#ref-1">↩</a></p></aside>'
                    ),
                    "toc": [{"title": "第一节", "fragment": "section-1"}],
                }
            ],
        }
        manifest_path = work / "manifest.json"
        epub_path = work / "smoke.epub"
        fingerprint = work / "fingerprint.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        run(sys.executable, "scripts/build_epub.py", str(manifest_path), str(epub_path))
        run(sys.executable, "scripts/validate_epub.py", str(epub_path), "--strict")
        run(sys.executable, "scripts/text_fingerprint.py", str(epub_path), "--write", str(fingerprint), "--ignore-whitespace")
        run(sys.executable, "scripts/text_fingerprint.py", str(epub_path), "--compare", str(fingerprint))
        print("PASS: synthetic EPUB build, strict validation, and fingerprint round trip")


if __name__ == "__main__":
    main()
