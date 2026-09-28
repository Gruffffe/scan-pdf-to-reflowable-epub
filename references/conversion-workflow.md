# Conversion workflow and failure modes

This reference captures reusable lessons from converting text-layer and scanned books into reflowable EPUBs. Keep book-specific filenames, page numbers, and OCR output in the task workspace, not here.

## Phase 1: diagnose and preserve evidence

1. Hash the source and inspect encryption, page count, dimensions, text coverage, and representative extraction.
2. Render representative pages: cover, contents, ordinary body, a complex page, notes, and the final pages.
3. Choose `structure-only` or `ocr-correction` mode.
4. Preserve page identities through OCR and normalization. Do not flatten the whole book into an untraceable text stream.

Key risk: a PDF can technically contain text while that layer is incomplete, scrambled, duplicated, or unrelated to visible glyphs. Test quality, not only presence. When reusing OCR-derived text or handling complex pages, follow [text-layer-and-complex-pages.md](text-layer-and-complex-pages.md).

## Phase 2: map the book before cleaning it

Create two task-local tables:

- page-role map: PDF index, printed folio, role, language, extraction/OCR status, confidence, notes;
- structure map: part/chapter/subheading, title as printed, start page, evidence, destination ID.

Use the original contents and visual chapter pages as primary evidence. Reconcile disagreements explicitly. Page offsets often change after plates, Roman-numbered front matter, or omitted blanks.

Key risk: cleanup performed before classification can erase page numbers needed to locate chapters, remove corner notes as noise, or append a back cover to the last paragraph.

## Phase 3: OCR and layout reconstruction

Run OCR only where needed. Retain coordinates and confidence when the engine supplies them. Normalize lines into semantic blocks with conservative cross-page joining. Mark uncertain spans for sampling.

Separate three decisions:

1. What characters are present?
2. Which physical lines belong to the same semantic block?
3. What EPUB role does the block have?

Do not let a decision at one layer silently rewrite another. In `structure-only` mode, line joining may remove layout whitespace but must not invent words or punctuation. Keep raw rows until page-family decisions are complete: prose may merge same-baseline fragments, but indexes must be separated into columns before row joining.

Key risks include two-line headings mistaken for two sections, notes merged into body text, list numbers treated as note calls, English punctuation recognized as digits, and chart labels flattened into paragraphs. Preserve spatially dependent pages or regions as images when semantic reconstruction would be less faithful.

## Phase 4: construct EPUB semantics

Build EPUB 3 with:

- explicit metadata and language;
- cover image plus a spine-reachable cover page;
- one ordered spine with sensible document granularity;
- hierarchical navigation matching the source organization;
- stable chapter, subheading, note, image, and page-break IDs;
- page breaks at exact source transitions;
- conservative semantic note links;
- CSS that supports reflow without encoding source-page geometry.

For bilingual works, preserve sequential or parallel organization as found. Do not manufacture sentence or paragraph alignment without evidence.

## Phase 5: audit in four layers

1. Package/link audit: ZIP, OPF, manifest, spine, XHTML, resources, IDs, and targets.
2. Structural audit: chapter map, navigation, page roles, page anchors, notes, images, and language grouping.
3. Content audit: post-classification source-visible sequence versus packaged spine-visible text in the declared editing mode. Prefer an exact normalized match with explicit exclusions for generated elements.
4. Visual audit: representative rendered pages, including difficult and terminal cases.

Run EPUBCheck, but treat it as syntax and packaging validation. It cannot confirm that a chapter begins on the correct source page, a digit is not a false note, or the wording stayed unchanged.

## Completion standard

The conversion is complete only when the artifact and QA report agree. The report should state what was checked, what was not checked, known limitations, and whether any output format or device test was unavailable.
