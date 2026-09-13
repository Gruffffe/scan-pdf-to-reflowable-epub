#!/usr/bin/env python3
"""Validate EPUB packaging, XML, resources, links, and skill-specific invariants."""
from __future__ import annotations

import argparse
import json
import posixpath
import subprocess
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

CONTAINER = "META-INF/container.xml"
CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
EPUB_NS = "http://www.idpf.org/2007/ops"
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def resolve(source: str, href: str) -> tuple[str, str]:
    parts = urlsplit(href)
    if parts.scheme in EXTERNAL_SCHEMES:
        return "", ""
    target = unquote(parts.path)
    target = source if not target else posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
    return target, unquote(parts.fragment)


def parse_xml(zf: zipfile.ZipFile, name: str, errors: list[str]) -> ET.Element | None:
    try:
        return ET.fromstring(zf.read(name))
    except KeyError:
        errors.append(f"missing file: {name}")
    except ET.ParseError as exc:
        errors.append(f"invalid XML {name}: {exc}")
    return None


def inspect_epub(path: Path, strict: bool) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    metrics = {
        "manifest_items": 0,
        "spine_documents": 0,
        "xhtml_documents": 0,
        "internal_links": 0,
        "pagebreaks": 0,
        "noterefs": 0,
        "footnotes": 0,
        "images_referenced": 0,
        "ncx_points": 0,
    }

    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        return {"epub": str(path), "errors": [f"invalid ZIP: {exc}"], "warnings": [], "metrics": metrics}

    with zf:
        names = zf.namelist()
        name_set = set(names)
        if not names or names[0] != "mimetype":
            errors.append("mimetype is not the first ZIP entry")
        elif zf.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            errors.append("mimetype is compressed")
        elif zf.read("mimetype") != b"application/epub+zip":
            errors.append("mimetype has the wrong value")

        container = parse_xml(zf, CONTAINER, errors)
        if container is None:
            return {"epub": str(path), "errors": errors, "warnings": warnings, "metrics": metrics}
        rootfile = container.find(f".//{{{CONTAINER_NS}}}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            errors.append("container.xml has no rootfile")
            return {"epub": str(path), "errors": errors, "warnings": warnings, "metrics": metrics}

        opf_path = rootfile.get("full-path", "")
        opf = parse_xml(zf, opf_path, errors)
        if opf is None:
            return {"epub": str(path), "errors": errors, "warnings": warnings, "metrics": metrics}

        manifest: dict[str, dict[str, str]] = {}
        href_to_id: dict[str, str] = {}
        for item in (node for node in opf.iter() if local_name(node.tag) == "item"):
            item_id, href = item.get("id"), item.get("href")
            if not item_id or not href:
                errors.append("manifest item is missing id or href")
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), unquote(href)))
            manifest[item_id] = {
                "href": resolved,
                "media_type": item.get("media-type", ""),
                "properties": item.get("properties", ""),
            }
            href_to_id[resolved] = item_id
            if resolved not in name_set:
                errors.append(f"manifest resource missing from ZIP: {resolved}")
        metrics["manifest_items"] = len(manifest)

        spine_ids = [node.get("idref", "") for node in opf.iter() if local_name(node.tag) == "itemref"]
        for item_id in spine_ids:
            if item_id not in manifest:
                errors.append(f"spine references missing manifest id: {item_id}")
        spine_files = [manifest[item_id]["href"] for item_id in spine_ids if item_id in manifest]
        metrics["spine_documents"] = len(spine_files)

        xhtml_roots: dict[str, ET.Element] = {}
        ids_by_file: dict[str, set[str]] = {}
        for item in manifest.values():
            if item["media_type"] != "application/xhtml+xml":
                continue
            name = item["href"]
            root = parse_xml(zf, name, errors)
            if root is None:
                continue
            xhtml_roots[name] = root
            raw_ids = [node.get("id") for node in root.iter() if node.get("id")]
            for duplicate in sorted(key for key, count in Counter(raw_ids).items() if count > 1):
                errors.append(f"duplicate id in {name}: #{duplicate}")
            ids_by_file[name] = set(raw_ids)
        metrics["xhtml_documents"] = len(xhtml_roots)

        for source, root in xhtml_roots.items():
            for node in root.iter():
                epub_type = node.get(f"{{{EPUB_NS}}}type", "").split()
                if "pagebreak" in epub_type:
                    metrics["pagebreaks"] += 1
                    if not node.get("id"):
                        errors.append(f"pagebreak without id in {source}")
                if "noteref" in epub_type:
                    metrics["noterefs"] += 1
                if "footnote" in epub_type or "endnote" in epub_type:
                    metrics["footnotes"] += 1

                for attr in ("href", "src"):
                    value = node.get(attr)
                    if not value:
                        continue
                    target, fragment = resolve(source, value)
                    if not target:
                        continue
                    if attr == "href":
                        metrics["internal_links"] += 1
                    if local_name(node.tag) == "img" and attr == "src":
                        metrics["images_referenced"] += 1
                    if target not in name_set:
                        errors.append(f"broken {attr} in {source}: {value}")
                        continue
                    if target not in href_to_id:
                        errors.append(f"unmanifested resource referenced by {source}: {target}")
                    if fragment:
                        if target not in ids_by_file:
                            target_root = parse_xml(zf, target, errors)
                            if target_root is not None:
                                ids_by_file[target] = {n.get("id") for n in target_root.iter() if n.get("id")}
                        if fragment not in ids_by_file.get(target, set()):
                            errors.append(f"broken fragment in {source}: {value}")

        nav_items = [item for item in manifest.values() if "nav" in item["properties"].split()]
        cover_images = [item for item in manifest.values() if "cover-image" in item["properties"].split()]
        ncx_items = [item for item in manifest.values() if item["media_type"] == "application/x-dtbncx+xml"]
        for ncx_item in ncx_items:
            ncx_root = parse_xml(zf, ncx_item["href"], errors)
            if ncx_root is None:
                continue
            for node in (node for node in ncx_root.iter() if local_name(node.tag) == "content"):
                metrics["ncx_points"] += 1
                src = node.get("src", "")
                if not src:
                    errors.append(f"empty NCX target in {ncx_item['href']}")
                    continue
                target, fragment = resolve(ncx_item["href"], src)
                if target not in name_set:
                    errors.append(f"broken NCX target in {ncx_item['href']}: {src}")
                elif fragment and fragment not in ids_by_file.get(target, set()):
                    errors.append(f"broken NCX fragment in {ncx_item['href']}: {src}")
        if not spine_files:
            errors.append("spine is empty")
        if strict:
            if not nav_items:
                errors.append("strict: no EPUB navigation document")
            if not cover_images:
                errors.append("strict: no manifest cover-image")
            else:
                cover_href = cover_images[0]["href"]
                cover_reachable = False
                for spine_file in spine_files:
                    root = xhtml_roots.get(spine_file)
                    if root is None:
                        continue
                    for node in root.iter():
                        if local_name(node.tag) != "img" or not node.get("src"):
                            continue
                        target, _ = resolve(spine_file, node.get("src", ""))
                        if target == cover_href:
                            cover_reachable = True
                if not cover_reachable:
                    errors.append("strict: cover image is not reachable from a spine document")
            if metrics["noterefs"] and not metrics["footnotes"]:
                errors.append("strict: noteref links exist but no semantic footnotes/endnotes were found")

    return {"epub": str(path), "errors": errors, "warnings": warnings, "metrics": metrics}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("epub", type=Path)
    ap.add_argument("--epubcheck", type=Path, help="Path to epubcheck.jar")
    ap.add_argument("--strict", action="store_true", help="Require navigation and a spine-reachable cover")
    ap.add_argument("--json", type=Path, dest="json_path", help="Write a machine-readable report")
    args = ap.parse_args()

    if not args.epub.is_file():
        raise SystemExit(f"EPUB not found: {args.epub}")
    report = inspect_epub(args.epub, args.strict)

    if args.epubcheck:
        if not args.epubcheck.is_file():
            report["errors"].append(f"EPUBCheck JAR not found: {args.epubcheck}")
        else:
            run = subprocess.run(
                ["java", "-jar", str(args.epubcheck), str(args.epub)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            report["epubcheck"] = {"exit_code": run.returncode, "output": run.stdout[-12000:]}
            if run.returncode:
                report["errors"].append(f"EPUBCheck failed with exit code {run.returncode}")
    else:
        report["epubcheck"] = {"status": "not run"}
        report["warnings"].append("EPUBCheck was not run")

    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
