# EPUB QA checklist

Validation has four independent layers. Passing one does not imply the others passed.

## Package and link integrity

- `mimetype` is the first ZIP entry, uncompressed, with the exact EPUB MIME value.
- Container, OPF, manifest, spine, navigation, XHTML, images, and fragment targets resolve.
- XHTML parses as XML; IDs are unique within each document.
- The cover image is identified and a cover page is reachable from the spine.
- EPUBCheck reports zero fatal errors, errors, and warnings when available.

Run `scripts/validate_epub.py output.epub --strict --epubcheck /path/to/epubcheck.jar`.

## Structural integrity

- Navigation follows the printed contents and reaches the intended chapter/subheading.
- Front matter, body, notes, bibliography, illustrations, and back cover have the right roles.
- Spine order and language-part order match the source.
- Page anchors are unique, ordered, and located at the actual transition—even inside a continuing paragraph.
- Blank pages and back covers are not silently emitted as body chapters.
- Note links reach the correct note and return to the correct marker; uncertain notes remain readable.

## Content integrity

In `structure-only` mode, create a source-derived text fingerprint before packaging and compare the result afterward. Ignore only declared layout whitespace and declared generated tokens. Investigate missing, duplicated, reordered, or newly invented visible text.

Fingerprints are an alarm, not proof of semantic correctness. When restructuring intentionally changes generated headings or moves notes, compare logical sections or explain the expected difference in the QA report.

## Visual sampling

Render or preview representative locations:

- cover and title/front-matter page;
- printed contents and one nested navigation branch;
- ordinary Chinese prose crossing a source-page boundary;
- ordinary English or mixed-language prose;
- a numbered list and a digit that must not become a note;
- a multi-line numbered item, plus a numbered subheading whose following body must remain separate;
- a paragraph or list item continuing across a source-page anchor;
- a confirmed note link and an unresolved note candidate;
- an image/caption or other complex page;
- the final body page and back cover.

Check font size, indentation, paragraph spacing, line wrapping, heading hierarchy, image scaling, orphan artifacts, and whether page anchors disturb reflow.

For a reported reflow defect, render the exact repaired location and at least one counterexample affected by the same rule. When XHTML fragments are copied into a standalone HTML preview, serialize non-void elements such as page-break `<span>` anchors with explicit closing tags; HTML parsing of `<span/>` can hide following text and create a false failure.

## Report

Record source diagnosis, OCR engine/version, editing mode, chapter-map evidence, sample scope, note statistics, text-audit status, EPUBCheck version/result, known OCR or layout errors, AZW3 availability, and whether actual Kindle/device testing occurred.
