# Paragraph and numbered-block reconstruction

Use this reference when OCR lines, numbered items, cross-page prose, or browser previews show suspicious breaks. The objective is to recover semantic blocks without editing visible wording.

## The failure pattern

A common bad EPUB maps each indented OCR line to a separate `<p>`. It often looks acceptable in source-page coordinates but produces large gaps and broken sentences after reflow. Numbered material is especially vulnerable because at least three different structures can share the same prefix:

- a multi-line list item, such as `（3）……`;
- a numbered subheading followed by a new body paragraph, such as `1. 某主题`;
- an ordinary digit or note marker that is not a block boundary.

Do not repair this by deleting all breaks after numbers. That fixes wrapped list items while swallowing numbered subheadings and their following prose.

## Reconstruct with block state

Track the active semantic block—body paragraph, numbered item, numbered subheading, quotation, verse, caption, or note—instead of classifying every physical line independently.

For each page, estimate rather than assume:

- ordinary left edge and first-line indent;
- numbered-marker edge;
- hanging-continuation edge;
- ordinary interline gap and larger block gap;
- main-text and note-region font/line-height proxies.

Use book-relative distributions or calibrated page-family values. Fixed coordinates and one universal gap threshold are fragile across trim sizes and scans.

### Continue an active numbered item

Join the next OCR row to the current item when several signals agree:

- the next row does not begin a new peer marker;
- the previous text is syntactically incomplete, or the next row uses the established hanging-continuation indent;
- the vertical gap resembles ordinary line spacing;
- font and main-column membership match;
- no heading, note region, illustration, language boundary, or other page role intervenes.

The continuation may cross a source page. Keep the page event inside the same paragraph:

```html
<p class="list-item">……社<span epub:type="pagebreak" id="page-117" title="117"></span>会的……</p>
```

Do not move the page anchor outside the paragraph merely to simplify markup.

### End a numbered item or preserve a numbered subheading

Start a new block when stronger boundary evidence appears:

- a new peer or nested marker begins;
- the gap after the numbered line is materially larger than ordinary interline spacing;
- the numbered line is short and typographically heading-like;
- the following row has the book's normal body first-line indent;
- the preceding item is complete and the discourse changes;
- the printed contents or repeated typography identifies a heading.

Vertical gap can override a lexical `looks-like-list` match. A marker regex proposes a numbered block; it does not decide whether the block is a list item or a heading.

## Repair workflow

1. Locate the visible phrase in the EPUB and identify the containing XHTML file.
2. Inspect adjacent tags and classes. Confirm whether physical OCR rows became sibling paragraphs.
3. Find the corresponding source page and the following page when the sentence crosses a page boundary.
4. Inspect OCR coordinates, confidence, baseline, indent, and vertical gap alongside the rendered scan.
5. Classify the block from converging layout and syntax evidence.
6. Fix the reconstruction rule or state transition, not the book phrase. Preserve a narrow task-local override only when the source is genuinely exceptional.
7. Build a new artifact version; retain the previous artifact for comparison.
8. Compare visible-text fingerprints while ignoring only declared layout whitespace and generated tokens.
9. Run strict package/link validation and EPUBCheck.
10. Render the corrected location plus at least one counterexample, such as a numbered subheading that must remain separate from its body.

## Candidate audit

Run the conservative EPUB audit after building:

```bash
python3 scripts/audit_reflow.py output/book.epub --json work/reflow-audit.json
```

It reports numbered paragraphs that end without terminal punctuation and are followed by another paragraph. These are review candidates, not automatic proof of an error: a numbered subheading may intentionally have exactly that form. Use `--fail-on-candidates` only in a book-specific pipeline whose expected candidates have been resolved or allowlisted.

## Preview trap

EPUB content is XHTML, but a standalone browser preview is usually parsed as HTML. In HTML, a self-closing non-void tag such as `<span/>` can absorb following text until another closing tag, making valid content appear missing. When exporting XHTML fragments for browser QA, serialize page anchors as explicit `<span></span>` pairs. Do not confuse a preview-parser artifact with an EPUB content loss.

## Completion evidence

A reliable repair records:

- source pages inspected;
- old and new block structure;
- the rule and counterexample used;
- visible-character count and fingerprint result;
- candidate-audit result;
- strict validator and EPUBCheck result;
- rendered sample result;
- whether an actual target reader was tested.
