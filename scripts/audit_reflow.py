#!/usr/bin/env python3
"""Flag conservative paragraph-continuation candidates in an EPUB.

The audit never edits content. Its default signal is intentionally narrow:
a numbered paragraph ends without terminal punctuation and is immediately
followed by another ordinary paragraph. Source geometry must decide whether
the pair is a broken list item or a valid numbered subheading plus body.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

EPUB_NS = "http://www.idpf.org/2007/ops"
NUMBERED_START = re.compile(
    r"^(?:（[一二三四五六七八九十百]+）|[一二三四五六七八九十百]+、|（\d+）|\d+[.、)])"
)
TERMINAL = set("。！？.!?；;：:）)】》”’\"")
SKIP_CLASSES = {"note", "footnote", "endnote", "caption", "verse", "verse-line", "ref", "reference"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalized_text(element: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def class_tokens(element: ET.Element) -> set[str]:
    return set(element.get("class", "").split())


def is_numbered_paragraph(element: ET.Element, text: str) -> bool:
    return "list-item" in class_tokens(element) or bool(NUMBERED_START.match(text))


def is_skipped(element: ET.Element) -> bool:
    classes = class_tokens(element)
    epub_type = set(element.get(f"{{{EPUB_NS}}}type", "").split())
    return bool(classes & SKIP_CLASSES or epub_type & {"footnote", "endnote"})


def terminal_sentence(text: str) -> bool:
    return bool(text and text[-1] in TERMINAL)


def audit_xhtml(data: bytes, document: str) -> list[dict[str, object]]:
    root = ET.fromstring(data)
    findings: list[dict[str, object]] = []
    for parent in root.iter():
        children = list(parent)
        for index, current in enumerate(children[:-1]):
            following = children[index + 1]
            if local_name(current.tag) != "p" or local_name(following.tag) != "p":
                continue
            if is_skipped(current) or is_skipped(following):
                continue
            current_text = normalized_text(current)
            following_text = normalized_text(following)
            if not current_text or not following_text:
                continue
            if not is_numbered_paragraph(current, current_text):
                continue
            if is_numbered_paragraph(following, following_text):
                continue
            if terminal_sentence(current_text):
                continue
            pagebreaks = [
                node.get("title") or node.get("id") or "unlabelled"
                for node in current.iter()
                if "pagebreak" in node.get(f"{{{EPUB_NS}}}type", "").split()
            ]
            findings.append({
                "document": document,
                "reason": "numbered-block ends nonterminal before a new paragraph",
                "current": current_text[:240],
                "following": following_text[:240],
                "pagebreaks_in_current": pagebreaks,
            })
    return findings


def audit_epub(path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.lower().endswith((".xhtml", ".html", ".htm")):
                findings.extend(audit_xhtml(archive.read(name), name))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--fail-on-candidates", action="store_true")
    args = parser.parse_args()

    if not args.epub.is_file():
        parser.error(f"EPUB not found: {args.epub}")
    try:
        findings = audit_epub(args.epub)
    except (zipfile.BadZipFile, ET.ParseError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = {"epub": str(args.epub), "candidate_count": len(findings), "candidates": findings}
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(output + "\n", encoding="utf-8")
    return 1 if args.fail_on_candidates and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
