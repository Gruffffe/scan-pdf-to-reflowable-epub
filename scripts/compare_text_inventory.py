#!/usr/bin/env python3
"""Compare declared source-visible text with visible EPUB spine text."""
from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
EPUB_TYPE = "{http://www.idpf.org/2007/ops}type"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def element_text(root: ET.Element, excluded_tags: set[str], excluded_epub_types: set[str]) -> str:
    pieces: list[str] = []

    def walk(node: ET.Element) -> None:
        node_types = set(node.get(EPUB_TYPE, "").split())
        if local_name(node.tag) in excluded_tags or node_types & excluded_epub_types:
            return
        if node.text:
            pieces.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                pieces.append(child.tail)

    walk(root)
    return " ".join(pieces)


def epub_visible_text(epub_path: Path, excluded_tags: set[str], excluded_epub_types: set[str]) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(epub_path) as archive:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(f".//{{{CONTAINER_NS}}}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("container.xml has no package rootfile")
        opf_path = rootfile.get("full-path", "")
        opf = ET.fromstring(archive.read(opf_path))

        manifest: dict[str, tuple[str, str, str]] = {}
        for node in opf.iter():
            if local_name(node.tag) != "item" or not node.get("id") or not node.get("href"):
                continue
            href = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), node.get("href", "")))
            manifest[node.get("id", "")] = (href, node.get("media-type", ""), node.get("properties", ""))

        for node in opf.iter():
            if local_name(node.tag) != "itemref":
                continue
            item = manifest.get(node.get("idref", ""))
            if not item or item[1] != "application/xhtml+xml" or "nav" in item[2].split():
                continue
            root = ET.fromstring(archive.read(item[0]))
            for body in (candidate for candidate in root.iter() if local_name(candidate.tag) == "body"):
                chunks.append(element_text(body, excluded_tags, excluded_epub_types))
    return normalize(" ".join(chunks))


def compare(source: str, target: str) -> dict:
    source_words = source.split()
    target_words = target.split()
    source_counts = Counter(source_words)
    target_counts = Counter(target_words)
    return {
        "source_characters": len(source),
        "epub_characters": len(target),
        "source_words": len(source_words),
        "epub_words": len(target_words),
        "exact_normalized_match": source == target,
        "missing_word_occurrences": sum((source_counts - target_counts).values()),
        "extra_word_occurrences": sum((target_counts - source_counts).values()),
        "missing_word_samples": list((source_counts - target_counts).items())[:25],
        "extra_word_samples": list((target_counts - source_counts).items())[:25],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_visible", type=Path, help="UTF-8 plain-text inventory in reading order")
    parser.add_argument("epub", type=Path)
    parser.add_argument("--exclude-tag", action="append", default=[], help="Ignore an element and its descendants")
    parser.add_argument(
        "--exclude-epub-type",
        action="append",
        default=[],
        help="Ignore elements carrying this epub:type token",
    )
    parser.add_argument("--json", dest="json_path", type=Path)
    args = parser.parse_args()

    source = normalize(args.source_visible.read_text(encoding="utf-8"))
    target = epub_visible_text(args.epub, set(args.exclude_tag), set(args.exclude_epub_type))
    report = compare(source, target)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    raise SystemExit(0 if report["exact_normalized_match"] else 1)


if __name__ == "__main__":
    main()
