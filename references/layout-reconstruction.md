# Layout reconstruction

## Build a page-role map first

Assign every source page a role before global cleanup: cover, title/copyright, front matter, contents, blank, body, notes, bibliography/index, illustration, or back cover. A page can have a secondary role, but it must not drift into the body merely because OCR returned text.

Use the page-role map as the boundary for all later joins. Never join across a cover, blank page, chapter start, language-part boundary, or back cover.

## Chapter and heading evidence

Rank evidence in this order:

1. printed contents plus printed folio;
2. visually confirmed chapter-title page;
3. repeated typographic and whitespace pattern;
4. OCR wording and lexical similarity;
5. inferred fixed PDF offset.

Require at least two independent signals for ambiguous boundaries. Treat a fixed PDF-to-print offset as a convenience, not proof; inserts, Roman-numbered front matter, and missing blank pages often break it.

A heading may wrap across physical lines. Merge those lines into one semantic heading only when font/position, spacing, syntax, and the contents entry agree. Accumulate consecutive heading rows and emit one heading element; do not promote each physical row separately. OCR maximum span size is weak evidence because one distorted glyph can inflate it. This is a markup operation in `structure-only` mode, not permission to change characters.

## Paragraph reconstruction

Use coordinates, line baselines, indentation, vertical gaps, font-size proxies, punctuation, and page continuity. Join lines when they form one syntactic unit; preserve a break for headings, lists, block quotations, verse, tables, captions, notes, and references.

Do not classify each OCR row independently. Maintain the active block role and require stronger evidence to leave it. In particular, a numbered item's hanging-indent continuation is often farther right than an ordinary first-line indent; indentation alone must not split it. Conversely, a short numbered subheading followed by a visibly larger gap and normally indented prose must not absorb that prose. Read [paragraph-and-list-reconstruction.md](paragraph-and-list-reconstruction.md) for the decision model and repair procedure.

Join a page's final line to the next page only when all of these hold:

- neither page is a structural boundary;
- punctuation and syntax support continuation;
- indentation and typography match;
- there is no heading, list reset, note block, or illustration boundary.

Keep a source-page event even when a paragraph continues. Put the page-break anchor at the exact transition inside the paragraph rather than moving it before or after the whole paragraph.

Calibrate gaps and indents against the current page family or book. Prefer ratios and distributions over universal coordinate thresholds. Test a positive continuation case and a negative numbered-subheading case before applying a rule globally.

## Furniture and noise

Detect running heads, running feet, and folios through repetition, location, and style. Delete only the repeated furniture instance, not every matching string. Record every removed text-bearing row and review sentence-like or unusually long deletions against rendered pages. A fixed edge threshold can erase legitimate continuation lines. Bottom and corner regions can contain notes, marginalia, captions, or reference continuations.

For multi-column indexes, bibliographies, or glossaries, preserve raw rows until columns are assigned. Never merge same-baseline text across a gutter and then attempt to recover columns afterward.

Treat isolated speckles, crop marks, OCR fragments outside the main text region, and blank-page artifacts as noise only after a visual sample check.

## Bilingual sources

Classify the book before aligning languages:

- paragraph-by-paragraph parallel;
- facing-page parallel;
- sequential language parts;
- main text plus translated annotations;
- genuinely mixed text.

Preserve the source organization unless the user explicitly requests a different editorial product. Sequential halves should have separate navigation groups; do not pretend they are parallel translations.
