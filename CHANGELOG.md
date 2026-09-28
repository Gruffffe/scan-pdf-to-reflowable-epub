# Changelog

All notable changes to this project will be documented here.

## Unreleased

- Add an OCR-text-layer and complex-page reconstruction guide covering audited
  running-head removal, multi-line headings, selective image preservation,
  column-first index ordering, and conservative dehyphenation.
- Add ordered source-visible-to-EPUB inventory comparison with explicit
  generated-element exclusions and regression tests.
- Require deletion-ledger review so exact post-cleanup text matches cannot hide
  text removed before the inventory was recorded.
- Add stateful paragraph and numbered-block reconstruction guidance.
- Distinguish hanging-indent list continuations from numbered subheadings by
  combining syntax, relative indentation, typography, and vertical gaps.
- Document inline cross-page anchors and the XHTML-to-HTML preview trap.
- Add a conservative reflow-candidate audit and regression tests.

## 0.1.0 - 2026-09-13

- Publish the evidence-first PDF diagnosis and page-role workflow.
- Add rules for Chinese structure, bilingual books, numbering, notes, images,
  page anchors, OCR confidence, and representative visual QA.
- Add EPUB building, package validation, text-fingerprint, PDF inspection, and
  page-rendering utilities.
- Add privacy-aware repository checks, a smoke test, and GitHub Actions CI.
