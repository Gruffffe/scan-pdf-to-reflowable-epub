# Reducing image-heavy EPUB size

Read when an EPUB is unexpectedly large or scan-reference images dominate the package. Distinguish file/storage size from actual reader RAM use; a smaller ZIP does not by itself prove lower peak decoding memory.

## Diagnose before changing content

Run `python3 scripts/inspect_epub_size.py input.epub` from the skill folder to list compressed and uncompressed payload by extension, largest resources, and archive size. Inspect the dominant assets' dimensions, color modes, actual colors, and source encoding. ZIP compression alone usually provides little benefit for already-compressed JPEG/PNG.

Keep the previous deliverable as a comparison baseline and produce a separate candidate. For an image-only optimization, reuse the completed XHTML; re-running OCR can change wording without helping compression.

## Select encoding by image content

- For genuinely bilevel scans, test 1-bit PNG before JPEG. Rendering a monochrome source to RGB JPEG can enlarge it while adding ringing and gray noise. Do not infer that an image is bilevel just because it looks black and white: inspect its actual decoded pixel values.
- Prefer a decoder-normalized native bitmap from the source PDF when it preserves the visible page. Direct reuse is safe only after checking image placement, orientation, masks, decode/polarity, page crops, and overlays. A single image resource does not prove that it is the complete visible page. Fall back to rendering when placement or compositing is ambiguous.
- For an exact 0/255 grayscale bitmap, convert to 1-bit without dithering and verify decoded pixel equality. Keep native resolution where possible. Do not threshold an antialiased grayscale image and call the result lossless.
- For wordhead/IPA crops with identical RGB channels, store grayscale PNG and verify the decoded result against the original. This can remove redundant channels without losing small pronunciation marks. Preserve color where channels differ.
- For photographic/color material, retain appropriate color encoding and compare candidate sizes and readability. PNG is not universally smaller than JPEG. Do not use EPUB-incompatible embedded image formats merely because the source PDF compresses well with them.

Use source geometry for extraction; do not transplant crop coordinates between native bitmaps, resized renders, and rectified OCR crops. Compare full pages for clipping, and enlarged small glyphs for quality. A thumbnail can detect orientation or polarity mistakes but cannot prove pixel fidelity or readable IPA.

“Lossless” must identify its baseline: exact to the decoded source bitmap, or exact to the previous EPUB image. Replacing a low-resolution JPEG with a native bitmap may improve fidelity, but it is not pixel-identical to that JPEG. Record image dimensions and before/after bytes alongside the applicable equality check.

## Full-reference and lightweight editions

Optimize image encoding before removing promised reference material. When a lighter reading edition would be useful, make its omissions explicit and keep a full-reference option. Do not require two editions for every request.

A reading edition can retain every reflow entry and its IPA crops while omitting duplicate body scans. Decide separately whether front matter and scanned indexes remain useful. Preserve printed-page labels as plain text where their scan target is removed; explain that they are locators rather than active links.

When removing scan assets, update all affected resources together:

- OPF manifest and spine;
- XHTML links and image references;
- EPUB navigation and any NCX/page-list/guide references;
- explanatory text and retained source-page return links.

If changing an image extension, update both the path and manifest media type. Parse structured attributes rather than assuming their serialized order. Do not remove an image still used by front matter, a wordhead, or another retained document.

In legacy NCX, navigation points sharing the same target must share `playOrder` when that attribute is present. Sequentially renumbering every point can fail EPUBCheck when a group and its first entry target the same document. Preserve valid ordering or assign it by target; verify the result.

## Verify the completed candidate

1. Compare every retained content document's visible text with the previous completed EPUB, independently of the optimizer's internal strings. Check entry/chapter count and reading order. Limit documented differences to intentionally changed instructions/navigation and omitted scan documents.
2. Verify decoded pixel equality for images claimed to be exact; visually compare source and output for polarity, clipping, orientation, small characters, and IPA. Check any deliberately lossy changes separately.
3. Finish/close the package before checking it. Preserve the first, uncompressed `mimetype` entry. Run strict resource/link/XML validation and EPUBCheck on each edition.
4. Preview both text and retained scans in a narrow viewport. Test one source jump and return, plus the lightweight version's inactive page labels. After a package-only repair, confirm previewed XHTML/assets match the final package; rerender if they changed.
5. Report original/final bytes, units, percentage reduction, retained/omitted material, equality checks, validation results, final checksum, and device-test status. Do not report an improvement in reader RAM without measuring it.
