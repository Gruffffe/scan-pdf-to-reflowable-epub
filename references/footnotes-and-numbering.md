# Footnotes and numbering

## Evidence threshold

Do not split paragraphs on digits. Create a note link only when the marker has strong contextual evidence and a matching note target. Useful signals include marker shape/style, baseline or superscript position, adjacency to a word or punctuation, a separator or note region, numbering continuity, and an identifiable note body.

When the evidence is incomplete, preserve the text without a link and record it as an unresolved note candidate. A readable unlinked note is better than a confidently wrong hyperlink.

## Common false positives

Do not interpret these as footnote calls solely because they contain a small number:

- ordered-list items such as `1.`、`（1）`、`1）` or `一、`;
- quantities and measurements such as `3倍`, `1.8米`, percentages, dates, years, pages, volumes, and ranges;
- dictionary senses or argument numbering where `1` means “first”;
- digits embedded in URLs, identifiers, formulas, bibliographic data, or filenames;
- OCR substitutions inside English words, especially apostrophe or capital `I` recognized as `1`;
- a circled number used as an ordinary enumerator rather than a note call.

Inspect the surrounding phrase and the page geometry. Regex shape alone is insufficient.

## Note linking

For confirmed notes:

- give marker and note unique stable IDs;
- use `epub:type="noteref"` on the source link and `epub:type="footnote"` or `endnote` on the note;
- provide a return link when the reading system supports it;
- preserve note order and visible marker form;
- avoid duplicating the note text when consolidating notes.

Report counts for detected note bodies, strongly linked notes, and retained-but-unlinked candidates. Manually sample at least one correct link and one rejected false-positive class when notes are numerous.
