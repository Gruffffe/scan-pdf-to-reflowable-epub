# Local OCR operations and source-page links

Read for long OCR runs, selective re-recognition, or embedded scan-reference editions.

## Resumable OCR

Reuse a usable existing text layer after checking its reading order and glyph fidelity. For mixed-quality PDFs, choose extraction or OCR per page/region instead of blindly recognizing the whole book again.

Persist page/column OCR results with source checksum, engine configuration, render scale, crop/transform version, and stable row IDs. Resume only results whose provenance matches the current job; file existence alone cannot establish that a cache is valid. Prefer atomic writes and validate JSON before marking a unit complete.

Bound worker concurrency to local resources. A producer-finished signal does not prove OCR completion: reconcile expected units against valid outputs, then retry missing/failed units. Keep progress counts, failure records, and a resumable command/checkpoint so interrupted work resumes rather than starts over. Separate raw results from revised results and record which version is authoritative.

When a sample reveals clipped letters or merged columns, repair geometry before increasing OCR resolution or rewriting recognized words. Reprocess the affected units, and invalidate only dependent layout and package outputs.

## Scan references

Keep source-page anchors at actual transitions even inside continuous prose. Maintain PDF page identity separately from printed folios; use printed folios only where verified. Label links clearly, for example “原书扫描页（PDF 第 n 页）”, and explain that they are verification links, not error flags. Provide a return to the relevant text where feasible.

Choose scan retention according to source complexity and the user's goal. Full-page appendices improve traceability but may dominate file size; selective complex-page images or tight glyph crops can be more appropriate. Do not silently remove promised reference material to meet an assumed size target. State the chosen retention and size, and offer a lighter edition only if useful.

Where native bilevel extraction is unambiguous, compare lossless 1-bit PNG before expanding it to grayscale/RGB JPEG. Render to explicit grayscale/RGB when direct extraction has polarity, placement, masking, or compositing ambiguity. For encoding choices and lightweight editions, read [epub-size-optimization.md](epub-size-optimization.md). Inspect background polarity, orientation, edge clipping, and small text after compression. Reuse assets rather than embedding duplicate copies of the same scan. Do not assume a specific transfer service or device size limit without checking it when relevant.

## Build completion

Write a package to a temporary path, finish and close the ZIP, then validate it before promoting it to the final deliverable. Do not validate a file still being written or deliver a stale artifact after a rebuild. Final validation and screenshots must refer to the same completed build; record its checksum or build ID in the report.
