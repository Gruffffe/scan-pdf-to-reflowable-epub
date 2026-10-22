# Dictionaries and multicolumn sources

Read for dictionaries, glossaries, or dense multicolumn indexes. Keep thresholds, source-specific exceptions, and page ranges in the task workspace.

## Pilot and reading order

For an unfamiliar layout, build a small set of complete entries before the full run: a normal entry, a wrapped headword, and an entry crossing a column or page. Include a redirect-only entry when present. A pilot is an implementation check; do not impose a new approval gate when full conversion is already authorized.

Determine reading order from the scan. For independent newspaper-style columns, OCR each column separately and concatenate left-to-right in the source order. A bilingual comparison table may instead require row-wise pairing; do not flatten it as independent columns without checking.

Inspect gutter position at multiple heights. A fixed midpoint crop can clip wordheads on shifted or tilted pages. Where a separator is sloped, rectify/deskew before cropping, or use a sloped crop boundary. Inspect both sides after correction. Re-OCR affected crops only; do not copy one book's pixel thresholds to another.

Record crop bounds and any affine transform with each OCR result. Headword images and OCR coordinates must use the same crop version; otherwise a corrected OCR box may select the wrong image region.

## Entry boundaries and navigation

Use a printed word index as an independent candidate inventory, then reconcile it with body wordheads, typography, field labels, and source page positions. The index itself is OCR input and can miss or corrupt entries; zero unmatched index items alone is not proof of completeness. Scan for unmatched body wordheads and suspicious duplicate definition blocks too.

Separate three fields: display headword, matching key, and alphabetic navigation key. Matching may normalize punctuation, apostrophes, case, or parenthesized articles without silently changing displayed text. A headword beginning with a parenthesized article must not create a punctuation-only navigation group. Determine grouping from the book's indexing convention.

Retain wrapped wordheads, pronunciation continuations, and redirect-only entries. Do not require a definition label for every entry. Verify the first and last entry, entry order, and boundaries spanning columns/pages. Resolve ambiguous candidates from scans rather than taking the highest fuzzy-match score as sufficient evidence.

## Internal structure

Track the active field: definition, etymology, examples, or cross-reference. A word such as “词源” at the start of an ordinary continuation line is not automatically a new heading. Require the source's complete label pattern (such as brackets), or corroborating typography and position. Keep a negative example in regression checks.

Circled example numbers can be misrecognized or placed after adjacent words by OCR. Check geometry and the scan before splitting; do not invent missing numbering or mechanically move every circled digit. Preserve the relation between English examples and their Chinese explanations.

For unreliable IPA or special glyphs, a tight source crop can preserve the original wordhead while a searchable headword supplies navigation. Disclose which parts are image-only; this does not make pronunciation searchable or fully accessible. Track those rows as image-preserved, rather than silently omitting them from the content audit.

Treat English end-of-line hyphens conservatively. A dictionary/lexicon hit is supporting evidence, not proof that a compound hyphen should disappear. Keep proper names and ambiguous compounds unchanged; record removed hyphens and inspect representative joins and preserved compounds. Do not let page-anchor tokens interfere with joining or field recognition.

## Completion checks

- Every retained OCR row has exactly one content assignment; image-preserved and excluded rows have explicit roles and reasons.
- Entry candidates from index and body are reconciled in both directions; boundary uncertainties are listed.
- Navigation groups and spine order agree with the resolved entry order.
- Sample ordinary, wrapped, parenthesized, redirect-only, cross-column/page, and final entries in a narrow viewport, and compare with scans.
- Report separately entry count, text preservation, image-only content, OCR uncertainty, and actual reader testing.
