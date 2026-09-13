#!/usr/bin/env python3
"""Create or compare normalized visible-text fingerprints for an EPUB spine."""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize(text: str, ignore_whitespace: bool, ignored_tokens: list[str]) -> str:
    for token in ignored_tokens:
        text = text.replace(token, "")
    return re.sub(r"\s+", "", text) if ignore_whitespace else text


def visible_text(root: ET.Element) -> str:
    pieces: list[str] = []

    def walk(node: ET.Element) -> None:
        if local_name(node.tag) in {"script", "style", "nav"}:
            return
        if node.text:
            pieces.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                pieces.append(child.tail)

    for body in (node for node in root.iter() if local_name(node.tag) == "body"):
        walk(body)
    return "".join(pieces)


def snapshot(epub_path: Path, ignore_whitespace: bool, ignored_tokens: list[str]) -> dict:
    with zipfile.ZipFile(epub_path) as zf:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        rootfile = container.find(f".//{{{CONTAINER_NS}}}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("container.xml has no rootfile")
        opf_path = rootfile.get("full-path", "")
        opf = ET.fromstring(zf.read(opf_path))

        manifest: dict[str, tuple[str, str, str]] = {}
        for node in opf.iter():
            if local_name(node.tag) != "item" or not node.get("id") or not node.get("href"):
                continue
            href = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), node.get("href", "")))
            manifest[node.get("id", "")] = (href, node.get("media-type", ""), node.get("properties", ""))

        documents = []
        whole: list[str] = []
        for node in opf.iter():
            if local_name(node.tag) != "itemref":
                continue
            item = manifest.get(node.get("idref", ""))
            if not item or item[1] != "application/xhtml+xml" or "nav" in item[2].split():
                continue
            href = item[0]
            root = ET.fromstring(zf.read(href))
            text = normalize(visible_text(root), ignore_whitespace, ignored_tokens)
            whole.append(text)
            documents.append({
                "href": href,
                "characters": len(text),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            })

    all_text = "".join(whole)
    return {
        "format": 1,
        "source_name": epub_path.name,
        "normalization": {"ignore_whitespace": ignore_whitespace, "ignored_tokens": ignored_tokens},
        "whole_book": {
            "characters": len(all_text),
            "sha256": hashlib.sha256(all_text.encode("utf-8")).hexdigest(),
        },
        "documents": documents,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("epub", type=Path)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, help="Write a fingerprint snapshot")
    group.add_argument("--compare", type=Path, help="Compare against a snapshot")
    ap.add_argument("--ignore-whitespace", action="store_true")
    ap.add_argument("--ignore-token", action="append", default=[])
    args = ap.parse_args()

    if args.compare:
        expected = json.loads(args.compare.read_text(encoding="utf-8"))
        normalization = expected.get("normalization", {})
        actual = snapshot(
            args.epub,
            bool(normalization.get("ignore_whitespace")),
            list(normalization.get("ignored_tokens", [])),
        )
        matched = expected.get("whole_book") == actual.get("whole_book")
        print(json.dumps({"matched": matched, "expected": expected.get("whole_book"), "actual": actual.get("whole_book")}, indent=2))
        raise SystemExit(0 if matched else 1)

    result = snapshot(args.epub, args.ignore_whitespace, args.ignore_token)
    args.write.parent.mkdir(parents=True, exist_ok=True)
    args.write.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["whole_book"], indent=2))


if __name__ == "__main__":
    main()
