---
name: scan-pdf-to-reflowable-epub
description: Convert legally readable text or scanned PDFs into searchable, reflowable EPUBs with OCR, page-role classification, layout reconstruction, bilingual structure, navigation, notes, content-preservation audits, visual QA, and EPUB validation. Use for PDF-to-EPUB or Kindle reflow conversion, especially Chinese, bilingual, scanned, footnote-heavy, dictionary, or structurally complex books. Also use to reduce oversized image-heavy EPUBs while preserving content.
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
3. If a usable text layer exists, extract it while retaining page boundaries and geometry. Judge extraction quality from representative prose, headings, indexes, and complex pages—not coverage alone. Otherwise render pages and run local OCR that returns text, coordinates, and confidence when possible. Read [ocr-engines.md](references/ocr-engines.md) before selecting an engine. For OCR-derived text layers, figures, or multi-column back matter, read [text-layer-and-complex-pages.md](references/text-layer-and-complex-pages.md). For long runs, selective re-OCR, or scan-reference appendices, read [local-ocr-and-source-links.md](references/local-ocr-and-source-links.md).
4. Establish chapter boundaries from converging evidence. Prefer the printed contents, printed page numbers, and visually confirmed title pages over fixed PDF offsets or OCR heading guesses. Record the resulting chapter/page map. For dictionaries or multicolumn indexes, read [dictionaries-and-multicolumn.md](references/dictionaries-and-multicolumn.md) and reconcile entry boundaries against both index and body evidence.
5. Classify bilingual organization before pairing text: parallel paragraph, facing-page, sequential language parts, or mixed annotations. Do not fabricate paragraph pairs when the source is sequential.
6. Reconstruct hierarchy and flow from coordinates, typography, whitespace, indentation, punctuation, and cross-page continuity. Treat block reconstruction as a stateful decision: a wrapped line inherits its active body, list, heading, quotation, or note role until stronger boundary evidence appears. Read [layout-reconstruction.md](references/layout-reconstruction.md). When OCR lines, numbered items, or cross-page prose are involved, also read [paragraph-and-list-reconstruction.md](references/paragraph-and-list-reconstruction.md). For Chinese publications, read [chinese-document-structure.md](references/chinese-document-structure.md).
7. Distinguish body numbering from note markers conservatively. Never split a paragraph merely because a digit appears. Read [footnotes-and-numbering.md](references/footnotes-and-numbering.md) whenever notes, citations, or numbered lists occur.
8. Remove repeated running heads, isolated folios, blank pages, and scan-edge noise only after page-role and repetition checks. Log every removed text-bearing row with page, text, and reason; review unusually long removals against rendered pages. Preserve meaningful corner notes, captions, references, and bottom notes. Never rely on one universal top/bottom coordinate threshold.
9. Build EPUB 3 with a reachable cover, ordered spine, nested navigation, searchable XHTML, semantic notes where proven, stable section IDs, and page-break anchors placed at the actual source-page transition—even when the transition occurs inside one reconstructed paragraph. Use `scripts/build_epub.py` or an equivalent implementation.
10. In either editing mode, preserve a source-derived inventory independent of the output serializer. Record the post-classification, post-furniture-removal visible text before packaging and compare it in reading order with the EPUB using `scripts/compare_text_inventory.py`. Use `scripts/text_fingerprint.py` for EPUB-to-EPUB rebuild comparisons. Reconcile row/block coverage, including image-preserved and excluded content, and review the deletion ledger. For `ocr-correction`, account for changes through an explicit correction ledger. Explain every intentional exclusion or generated token; exact equality of the declared inventory is preferred over character-count similarity. A match to OCR does not prove accurate or complete recognition of the scan.
11. Run `scripts/audit_reflow.py` to surface suspicious numbered-block splits, then run `scripts/validate_epub.py --strict`, ZIP integrity checks, and EPUBCheck when available. Review candidates against source geometry; never auto-join solely because the audit reports one. Perform representative visual checks from [epub-qa.md](references/epub-qa.md), including both the repaired pattern and a counterexample that must remain separate. Sample ordinary prose, every special layout family, complex images/tables, multi-column back matter, and the last included pages. Structural validation does not replace visual or content validation.
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

For an oversized existing EPUB or image-heavy output, read [epub-size-optimization.md](references/epub-size-optimization.md) before reducing image resolution or removing scan references. Diagnose compressed resource sizes first; preserve text and verify any lightweight edition separately.

## Tools and fallbacks

The workflow may use Poppler, Apple Vision, PaddleOCR, Tesseract, Python, EbookLib, lxml, Pillow, EPUBCheck, or Calibre when available. Detect capabilities first. Generate AZW3 only when a suitable local converter is present, and never report Kindle hardware testing unless it actually occurred.

Read only the references needed for the current source, but always read the workflow and QA references:

- [conversion-workflow.md](references/conversion-workflow.md)
- [epub-qa.md](references/epub-qa.md)
- [ocr-engines.md](references/ocr-engines.md)
- [layout-reconstruction.md](references/layout-reconstruction.md)
- [paragraph-and-list-reconstruction.md](references/paragraph-and-list-reconstruction.md)
- [text-layer-and-complex-pages.md](references/text-layer-and-complex-pages.md)
- [footnotes-and-numbering.md](references/footnotes-and-numbering.md)
- [chinese-document-structure.md](references/chinese-document-structure.md)

Conditional references:

- [dictionaries-and-multicolumn.md](references/dictionaries-and-multicolumn.md): entry segmentation, crop geometry, IPA, and dictionary navigation.
- [local-ocr-and-source-links.md](references/local-ocr-and-source-links.md): resumable OCR, source links, image fidelity, and completed-build validation.
- [epub-size-optimization.md](references/epub-size-optimization.md): image encoding, lightweight editions, size inspection, and preservation checks.
