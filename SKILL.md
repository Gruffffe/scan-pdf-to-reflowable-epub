---
name: scan-pdf-to-reflowable-epub
description: Convert legally readable text or scanned PDFs into searchable, reflowable EPUBs with OCR, page-role classification, layout reconstruction, bilingual structure, navigation, notes, content-preservation audits, visual QA, and EPUB validation. Use for PDF-to-EPUB or Kindle reflow conversion, especially Chinese, bilingual, scanned, footnote-heavy, or structurally complex books.
metadata:
  short-description: Rebuild scanned PDFs as validated reflowable EPUBs
---

# Scan PDF to reflowable EPUB

Turn a PDF into an EPUB that behaves like an ebook rather than a stack of page images. Preserve the user's scope and process files locally by default.

## Safety and editing mode

- Process only files the user is authorized to read. Never bypass DRM, passwords, or access controls.
- Do not upload source pages or OCR text unless the user explicitly authorizes it.
- Treat download, installation, and execution of third-party tools as separate actions.
- Keep personal paths, usernames, book-specific page ranges, and device identifiers out of reusable skill files.
- Choose and record one editing mode before reconstruction:
  - `structure-only` (default): change markup, hierarchy, joins, breaks, and links, but do not silently correct, rewrite, modernize, translate, or normalize visible wording.
  - `ocr-correction`: correct only OCR errors supported by the scan, and preserve an audit trail. Use only when the user permits textual correction.
- Report uncertainty honestly. Do not claim complete proofreading or device compatibility without evidence.

## Required workflow

1. Diagnose the source with `scripts/inspect_pdf.py`. Record page count, encryption, text-layer coverage, representative extraction quality, and a checksum in a task-local report.
2. Read [conversion-workflow.md](references/conversion-workflow.md) and create a page-role map before building. Classify cover, title pages, front matter, printed contents, blank pages, body, notes, bibliography, image-only matter, and back cover.
3. If a usable text layer exists, extract it while retaining page boundaries. Otherwise render pages and run local OCR that returns text, coordinates, and confidence when possible. Read [ocr-engines.md](references/ocr-engines.md) before selecting an engine.
4. Establish chapter boundaries from converging evidence. Prefer the printed contents, printed page numbers, and visually confirmed title pages over fixed PDF offsets or OCR heading guesses. Record the resulting chapter/page map.
5. Classify bilingual organization before pairing text: parallel paragraph, facing-page, sequential language parts, or mixed annotations. Do not fabricate paragraph pairs when the source is sequential.
6. Reconstruct hierarchy and flow from coordinates, typography, whitespace, indentation, punctuation, and cross-page continuity. Read [layout-reconstruction.md](references/layout-reconstruction.md). For Chinese publications, also read [chinese-document-structure.md](references/chinese-document-structure.md).
7. Distinguish body numbering from note markers conservatively. Never split a paragraph merely because a digit appears. Read [footnotes-and-numbering.md](references/footnotes-and-numbering.md) whenever notes, citations, or numbered lists occur.
8. Remove repeated running heads, isolated folios, blank pages, and scan-edge noise only after page-role and repetition checks. Preserve meaningful corner notes, captions, references, and bottom notes.
9. Build EPUB 3 with a reachable cover, ordered spine, nested navigation, searchable XHTML, semantic notes where proven, stable section IDs, and page-break anchors placed at the actual source-page transition—even when the transition occurs inside one reconstructed paragraph. Use `scripts/build_epub.py` or an equivalent implementation.
10. In `structure-only` mode, compare a source-derived text inventory with the EPUB using `scripts/text_fingerprint.py` or an equivalent section-level character audit. Explain every intentional difference; whitespace and generated return-arrow exceptions must be explicit.
11. Run `scripts/validate_epub.py --strict` and EPUBCheck when available. Then perform representative visual checks from [epub-qa.md](references/epub-qa.md). Structural validation does not replace visual or content validation.
12. Deliver the EPUB plus a concise report: diagnosis, OCR/tool versions, editing mode, chapter map basis, note-link statistics, text-audit result, validation result, visual samples, known issues, AZW3 status, and whether an actual reader was tested.

## Output requirements

The EPUB should contain valid metadata, a visible and reachable cover, ordered spine, EPUB navigation, searchable text, meaningful hierarchy, working internal links, and stable page/section anchors. Preserve English terms, Chinese explanations, paragraph sequence, images, references, and notes where supported by the source. Keep uncertain notes readable even if they cannot be safely linked.

Do not:

- make every page an image;
- infer chapter starts from a constant page offset alone;
- include a blank page or back cover as body text;
- treat all bottom-of-page text as removable furniture;
- turn every superscript-like digit into a note link;
- claim success solely because EPUBCheck passes.

## Tools and fallbacks

The workflow may use Poppler, Apple Vision, PaddleOCR, Tesseract, Python, EbookLib, lxml, Pillow, EPUBCheck, or Calibre when available. Detect capabilities first. Generate AZW3 only when a suitable local converter is present, and never report Kindle hardware testing unless it actually occurred.

Read only the references needed for the current source, but always read the workflow and QA references:

- [conversion-workflow.md](references/conversion-workflow.md)
- [epub-qa.md](references/epub-qa.md)
- [ocr-engines.md](references/ocr-engines.md)
- [layout-reconstruction.md](references/layout-reconstruction.md)
- [footnotes-and-numbering.md](references/footnotes-and-numbering.md)
- [chinese-document-structure.md](references/chinese-document-structure.md)
