# Contributing

Contributions should improve the reusable conversion workflow without adding
book-specific data, private paths, copyrighted source material, or unverified
claims.

## Before opening a pull request

1. Keep `SKILL.md` concise and route detailed knowledge to `references/`.
2. Preserve the default `structure-only` rule unless a change explicitly
   addresses the opt-in OCR-correction mode.
3. Never commit PDFs, OCR dumps, generated ebooks, API keys, account data, or
   absolute user paths.
4. Run the repository checks and smoke test:

   ```bash
   python3 scripts/repo_check.py
   python3 tests/smoke_test.py
   ```

5. If a script changed, include a focused test or a reproducible validation
   command in the pull request description.
6. Describe any platform-specific dependency or behavior. Do not present a
   macOS-only OCR path as universally available.

Use small commits and explain changes to visible-text preservation, footnotes,
page anchors, navigation, or validation behavior especially carefully.
