# Publishing this skill on GitHub

This repository is prepared for either GitHub's browser upload or a terminal
push. The terminal route is recommended because it preserves hidden files such
as `.github/` and makes the exact commit easy to review.

## 1. Run the release checks

From the repository root:

```bash
python3 scripts/repo_check.py
python3 tests/smoke_test.py
```

Review the file list before staging anything:

```bash
find . -maxdepth 3 -type f -not -path './.git/*' | sort
```

The checks reject common private absolute paths, secret-like assignments,
source PDFs, OCR dumps, and generated ebook formats. They reduce risk but do
not replace a human review.

## 2. Create an empty GitHub repository

Suggested settings:

- Repository name: `scan-pdf-to-reflowable-epub`
- Description: `A privacy-aware Codex skill for rebuilding scanned or text PDFs as audited reflowable EPUBs.`
- Visibility: Public for open distribution, or Private for personal use
- Do not initialize it with another README, `.gitignore`, or license because
  those files already exist locally.

## 3A. Publish with GitHub CLI

Authenticate in the terminal yourself, then run from this directory:

```bash
git init
git add .
git status --short
git commit -m "Initial release: PDF to reflowable EPUB skill"
git branch -M main
gh repo create scan-pdf-to-reflowable-epub --public --source=. --remote=origin --push
```

Change `--public` to `--private` if needed. Inspect `git status --short` before
the commit; no PDF, OCR dump, generated ebook, credential, or private path
should appear.

## 3B. Publish with Git

After creating an empty repository in the browser:

```bash
git init
git add .
git status --short
git commit -m "Initial release: PDF to reflowable EPUB skill"
git branch -M main
git remote add origin https://github.com/OWNER/scan-pdf-to-reflowable-epub.git
git push -u origin main
```

Replace `OWNER` with your GitHub user or organization name. Login and the final
push are intentionally left to the repository owner.

## 3C. Browser upload

Create an empty repository, choose **uploading an existing file**, and upload
the contents of this folder. Confirm that `.github/workflows/validate.yml` is
present afterward; file pickers can hide dot-directories. Do not upload this
project as one ZIP file because GitHub will store the archive instead of
expanding it into a usable repository.

## 4. Verify the published repository

Confirm that:

- `SKILL.md`, `agents/`, `references/`, and `scripts/` are visible;
- the Actions validation workflow passes;
- the README links work;
- the public repository contains no source book, OCR output, generated ebook,
  credentials, private path, or personal identifier;
- a clean clone passes `python3 scripts/repo_check.py` and
  `python3 tests/smoke_test.py` after dependencies are installed.

Do not distribute only the Raw URL for `SKILL.md`: this skill depends on its
reference documents and scripts, so consumers need the complete repository.

## 5. Maintain releases

For later changes:

```bash
git add .
git status --short
git commit -m "Describe the workflow improvement"
git push
```

Update `CHANGELOG.md`, rerun validation, and tag a stable release when the
behavior materially changes.

## References

- [Chinese walkthrough used as a publishing reference](https://jishuzhan.net/article/2035545613656457218)
- [GitHub: adding locally hosted code](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [GitHub: building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
