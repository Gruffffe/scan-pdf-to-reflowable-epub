# OCR text layers and complex pages

Use this reference when a PDF already contains OCR text, when diagrams or tables depend on spatial layout, or when indexes and bibliographies use multiple columns.

## Decide whether to reuse the text layer

Text-layer coverage is not text-layer quality. Sample at least:

- ordinary prose from early, middle, and late body pages;
- a chapter opening and wrapped subheading;
- a page with running furniture;
- an illustration, chart, or table;
- bibliography and index pages;
- the last nonblank pages.

Reuse the layer when its reading order and character quality are broadly serviceable. Rerun OCR only for deficient pages or regions when possible. Whole-book OCR can replace acceptable text with a different set of errors.

Keep coordinates and page identity even when the visible words are good. They remain necessary for furniture removal, paragraph reconstruction, column order, page anchors, and image placement.

## Separate line collection from semantic merging

Preserve raw line rows before grouping same-baseline fragments. Different page families need different grouping orders:

- ordinary prose: merge fragments on the same baseline within the main column;
- two-column indexes: assign each raw row to a column first, then sort and join inside that column;
- tables and charts: do not flatten cells or labels into prose merely because text extraction returned them.

Joining left and right index columns by baseline creates false entries. Detect column boundaries from horizontal clusters or calibrated gutters, read the first column top-to-bottom, then the next column.

## Remove page furniture with an audit trail

Running heads and folios are positional and repetitive, not simply “all text near an edge.” Body lines can begin unusually close to the top on continuation pages.

For every removed text-bearing row, record:

- source page;
- exact extracted text;
- reason;
- coordinates or region;
- rule or repeated pattern that justified removal.

Review the deletion ledger after building. Long rows, sentence-like text, uncommon one-off strings, and rows near a threshold are mandatory visual candidates. Calibrate thresholds from that book's page families and test pages where body text begins highest. A one-coordinate adjustment can prevent systematic loss, but the reusable rule is the audit-and-sample process—not a particular pixel value.

Chapter-opening titles represented by generated EPUB headings should be logged separately from repeated furniture. Their intentional removal must remain distinguishable from noise deletion.

## Recognize headings conservatively

OCR span-size maxima are unreliable because one distorted glyph can inflate a whole row. Prefer median/distributional font proxies together with whitespace, width, alignment, capitalization, syntax, repetition, and contents evidence.

A wrapped heading is one semantic heading. Accumulate consecutive heading-like rows until the typography or block role changes, then emit one heading element. Do not make each physical title line a separate heading, and do not promote an ordinary prose continuation merely because one word has a large OCR size.

## Preserve spatially dependent pages

Keep a page or cropped region as an image when meaning depends on positions, lines, arrows, cells, handwriting, or artwork. Common examples include graphs, sociograms, complex tables, facsimiles, and posters.

This is compatible with a reflowable EPUB when used selectively:

- retain reflowable XHTML for ordinary prose;
- use image blocks only for spatially dependent pages or regions;
- avoid duplicating the same page as both noisy extracted prose and an image;
- provide concise alternative text and preserve captions as searchable text when they can be separated safely;
- scale images responsively and prevent awkward breaks;
- record which pages remain image-based in the report.

For mixed prose-and-figure pages, prefer a cropped figure plus reflowed prose. A full-page image is acceptable for a small number of tightly integrated pages when cropping would risk omission or duplicated text.

## Dehyphenate without editing the book

Line-end hyphen removal is layout reconstruction, but genuine compounds must survive. Log every join. Prefer a dictionary-backed joined form, optionally extended by conservative inflection checks. Leave ambiguous forms unchanged in `structure-only` mode. Do not use dehyphenation as permission to correct unrelated OCR spelling.

## Compare a declared visible-text inventory

Record plain visible text at the moment after page-role classification, furniture removal, block joining, and declared image substitution, but before EPUB packaging. Then compare the normalized sequence against spine-visible EPUB text.

Use `scripts/compare_text_inventory.py` and explicitly exclude only generated elements that are absent from the inventory, for example:

```bash
python3 scripts/compare_text_inventory.py \
  work/source-visible.txt output/book.epub \
  --exclude-tag h1 \
  --exclude-tag figure \
  --exclude-epub-type pagebreak \
  --json work/content-inventory.json
```

An exact normalized match proves that packaging preserved the declared sequence. It does not prove OCR correctness, accurate page classification, or good reader layout. Review the removal ledger and rendered samples independently.

## Minimum QA evidence

Record:

- text-layer sampling decision;
- removed-row counts by reason and reviewed deletion candidates;
- pages or regions preserved as images;
- heading and multi-column sampling results;
- inventory character/word counts and exact-match result;
- strict validation, EPUBCheck, and ZIP integrity results;
- actual readers tested, if any;
- inherited OCR errors and unsearchable labels that remain.
