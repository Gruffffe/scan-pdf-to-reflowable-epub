#!/usr/bin/env python3
"""Build an EPUB 3 from normalized section JSON produced by a layout stage."""
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import posixpath
import re
from collections import OrderedDict
from pathlib import Path

from ebooklib import epub

DEFAULT_CSS = """
body { font-family: serif; line-height: 1.65; margin: 5%; }
section.chapter { margin: 0; padding: 0; }
h1 { font-size: 1.55em; line-height: 1.3; margin: 1.8em 0 1.2em; text-align: center; }
h2 { font-size: 1.25em; line-height: 1.4; margin: 1.6em 0 0.8em; }
p { margin: 0 0 0.65em; text-indent: 2em; }
p.no-indent, p.ref, p.caption, p.note { text-indent: 0; }
p.ref { margin-left: 2em; text-indent: -2em; }
blockquote { margin: 1em 1.5em; }
.scan, .cover-page { text-align: center; text-indent: 0; }
.cover-page img, img { max-width: 100%; height: auto; }
.pagebreak { display: inline; }
sup a { text-decoration: none; }
:lang(en) { word-break: normal; hyphens: auto; }
""".strip()


def source_path(manifest_path: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    beside_manifest = manifest_path.parent / path
    return beside_manifest if beside_manifest.exists() else path


def safe_href(value: str, suffix: str | None = None) -> str:
    normalized = posixpath.normpath(value.replace("\\", "/"))
    if normalized.startswith("/") or normalized == ".." or normalized.startswith("../"):
        raise ValueError(f"unsafe EPUB path: {value}")
    if suffix and not normalized.endswith(suffix):
        raise ValueError(f"EPUB path must end in {suffix}: {value}")
    return normalized


def safe_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value):
        raise ValueError(f"invalid XML/EPUB id: {value}")
    return value


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))

    language = manifest.get("language", "zh-CN")
    book = epub.EpubBook()
    book.set_identifier(manifest.get("identifier", "local-pdf-epub"))
    book.set_title(manifest["title"])
    book.set_language(language)
    if manifest.get("author"):
        book.add_author(manifest["author"])

    css = manifest.get("css", DEFAULT_CSS)
    if manifest.get("css_file"):
        css = source_path(args.manifest, manifest["css_file"]).read_text(encoding="utf-8")
    style = epub.EpubItem(uid="style", file_name="style/book.css", media_type="text/css", content=css.encode("utf-8"))
    book.add_item(style)

    known_hrefs = {"style/book.css"}
    for index, resource in enumerate(manifest.get("resources", [])):
        href = safe_href(resource["href"])
        if href in known_hrefs:
            raise ValueError(f"duplicate resource href: {href}")
        resource_id = safe_id(resource.get("id", f"resource-{index:04d}"))
        media_type = resource.get("media_type") or mimetypes.guess_type(href)[0] or "application/octet-stream"
        data = source_path(args.manifest, resource["source"]).read_bytes()
        book.add_item(epub.EpubItem(uid=resource_id, file_name=href, media_type=media_type, content=data))
        known_hrefs.add(href)

    spine: list = ["nav"]
    toc_entries: list = []
    cover = manifest.get("cover")
    if cover:
        cover_path = source_path(args.manifest, cover)
        cover_href = safe_href(manifest.get("cover_href", "images/cover.jpg"))
        if cover_href in known_hrefs:
            raise ValueError(f"cover href duplicates another resource: {cover_href}")
        book.set_cover(cover_href, cover_path.read_bytes(), create_page=False)
        known_hrefs.add(cover_href)
        cover_title = manifest.get("cover_title", "封面" if language.lower().startswith("zh") else "Cover")
        cover_page = epub.EpubHtml(uid="cover-page", title=cover_title, file_name="text/cover.xhtml", lang=language)
        relative_cover = posixpath.relpath(cover_href, "text")
        cover_page.content = (
            '<html xmlns="http://www.w3.org/1999/xhtml"><head>'
            f'<title>{html.escape(cover_title)}</title>'
            '<link rel="stylesheet" href="../style/book.css" type="text/css"/>'
            '</head><body class="cover-page">'
            f'<img src="{html.escape(relative_cover, quote=True)}" alt="{html.escape(cover_title, quote=True)}"/>'
            '</body></html>'
        ).encode("utf-8")
        book.add_item(cover_page)
        spine.append(cover_page)

    chapter_entries: list[tuple[str | None, object]] = []
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for index, section in enumerate(manifest["sections"]):
        section_id = safe_id(section.get("id", f"c{index:04d}"))
        if section_id in seen_ids:
            raise ValueError(f"duplicate section id: {section_id}")
        seen_ids.add(section_id)
        file_name = safe_href(section.get("file_name", f"text/c{index:04d}.xhtml"), ".xhtml")
        if file_name in seen_files or file_name in known_hrefs:
            raise ValueError(f"duplicate section file: {file_name}")
        seen_files.add(file_name)

        title = section["title"]
        section_language = section.get("language", language)
        chapter = epub.EpubHtml(uid=section_id, title=title, file_name=file_name, lang=section_language)
        section_type = " ".join(section.get("epub_type", ["chapter"])) if isinstance(section.get("epub_type", ["chapter"]), list) else section.get("epub_type", "chapter")
        heading = f'<h1>{html.escape(title)}</h1>' if section.get("show_title", True) else ""
        chapter.content = (
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
            f'xml:lang="{html.escape(section_language, quote=True)}" lang="{html.escape(section_language, quote=True)}">'
            f'<head><title>{html.escape(title)}</title><link rel="stylesheet" href="../style/book.css" type="text/css"/></head>'
            f'<body><section id="{section_id}" class="chapter" epub:type="{html.escape(section_type, quote=True)}">'
            f'{heading}{section["html"]}</section></body></html>'
        ).encode("utf-8")
        book.add_item(chapter)
        spine.append(chapter)

        child_links = []
        for child_index, child in enumerate(section.get("toc", [])):
            fragment = safe_id(child["fragment"])
            child_links.append(epub.Link(f"{file_name}#{fragment}", child["title"], f"{section_id}-sub-{child_index:03d}"))
        entry = (chapter, tuple(child_links)) if child_links else chapter
        if section.get("include_in_toc", True):
            chapter_entries.append((section.get("part"), entry))

    grouped: OrderedDict[str, tuple[str | None, list]] = OrderedDict()
    for index, (part, entry) in enumerate(chapter_entries):
        key = f"part:{part}" if part is not None else f"single:{index}"
        grouped.setdefault(key, (part, []))[1].append(entry)
    for part, entries in grouped.values():
        if part is None:
            toc_entries.append(entries[0])
        else:
            first = entries[0][0] if isinstance(entries[0], tuple) else entries[0]
            toc_entries.append((epub.Section(part, first.file_name), tuple(entries)))

    book.toc = tuple(toc_entries)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine
    args.output.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(args.output), book, {"epub3_pages": False})


if __name__ == "__main__":
    main()
