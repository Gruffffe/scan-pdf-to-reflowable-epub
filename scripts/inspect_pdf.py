#!/usr/bin/env python3
"""Evidence-first PDF inspection; does not modify the source PDF."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_pdfinfo(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip().lower().replace(" ", "_")] = value.strip()
    return result


def sample_pages(page_count: int, count: int) -> list[int]:
    if page_count <= 0:
        return []
    count = max(2, min(count, page_count))
    return sorted({1 + round(index * (page_count - 1) / (count - 1)) for index in range(count)})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--sample-count", type=int, default=9, help="Evenly distributed pages to test for extractable text")
    args = ap.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")

    try:
        import pymupdf  # type: ignore
    except ImportError:
        pymupdf = None

    data: dict = {
        "path": str(args.pdf.resolve()),
        "bytes": args.pdf.stat().st_size,
        "sha256": file_sha256(args.pdf),
        "tools": {
            **{name: shutil.which(name) for name in ("pdfinfo", "pdftotext", "pdftoppm")},
            "pymupdf": getattr(pymupdf, "__version__", None),
        },
    }

    page_count = 0
    if data["tools"]["pdfinfo"]:
        result = run(["pdfinfo", str(args.pdf)])
        data["pdfinfo_exit_code"] = result.returncode
        data["pdfinfo"] = parse_pdfinfo(result.stdout)
        data["pdfinfo_stderr"] = result.stderr.strip() or None
        page_count = int(data["pdfinfo"].get("pages", "0") or 0)
        data["pages"] = page_count or None
        data["encrypted"] = data["pdfinfo"].get("encrypted", "").lower().startswith("yes")

    document = None
    if not page_count and pymupdf:
        document = pymupdf.open(args.pdf)
        page_count = document.page_count
        data["pages"] = page_count
        data["encrypted"] = bool(document.needs_pass)

    if (data["tools"]["pdftotext"] or pymupdf) and page_count:
        samples = []
        extraction_engine = "pdftotext" if data["tools"]["pdftotext"] else "PyMuPDF"
        if extraction_engine == "PyMuPDF" and document is None:
            document = pymupdf.open(args.pdf)
        for page in sample_pages(page_count, args.sample_count):
            if extraction_engine == "pdftotext":
                result = run(["pdftotext", "-f", str(page), "-l", str(page), str(args.pdf), "-"])
                text, exit_code, stderr = result.stdout, result.returncode, result.stderr.strip() or None
            else:
                try:
                    text, exit_code, stderr = document[page - 1].get_text(), 0, None
                except Exception as exc:  # extraction diagnostics must survive one bad page
                    text, exit_code, stderr = "", 1, str(exc)
            non_whitespace = sum(not char.isspace() for char in text)
            samples.append({
                "page": page,
                "exit_code": exit_code,
                "characters": len(text),
                "non_whitespace_characters": non_whitespace,
                "replacement_characters": text.count("\ufffd"),
                "stderr": stderr,
            })
        populated = sum(sample["non_whitespace_characters"] >= 40 for sample in samples)
        coverage = populated / len(samples) if samples else 0.0
        if coverage == 0:
            status = "none_in_sample"
        elif coverage < 0.35:
            status = "sparse"
        elif coverage < 0.8:
            status = "mixed"
        else:
            status = "broad"
        data["text_layer"] = {
            "engine": extraction_engine,
            "status": status,
            "sampled_pages": len(samples),
            "populated_pages": populated,
            "sample_coverage": round(coverage, 3),
            "samples": samples,
            "caveat": "Character counts do not prove that extracted text matches visible glyphs; visually compare representative pages.",
        }
    else:
        data["text_layer"] = {"status": "not_tested", "reason": "no text extractor or page count available"}

    if document is not None:
        document.close()

    rendered = json.dumps(data, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
