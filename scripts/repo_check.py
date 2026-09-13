#!/usr/bin/env python3
"""Check skill structure, syntax, local links, and common publication leaks."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/conversion-workflow.md",
    "references/epub-qa.md",
)
FORBIDDEN_SUFFIXES = {".pdf", ".epub", ".azw3", ".mobi"}
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__"}
LEAK_PATTERNS = {
    "macOS private absolute path": re.compile(r"/Users/[^/\s]+/"),
    "Linux private absolute path": re.compile(r"/home/[^/\s]+/"),
    "Windows private absolute path": re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\s]+\\\\"),
    "secret-like assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def tracked_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts)
    ]


def check_frontmatter(errors: list[str]) -> None:
    path = ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append("SKILL.md: missing YAML frontmatter delimiters")
        return
    frontmatter = text.split("\n---\n", 1)[0][4:]
    name = re.search(r"(?m)^name:\s*([^\s]+)\s*$", frontmatter)
    description = re.search(r"(?ms)^description:\s*(.+?)(?:\n[a-zA-Z_-]+:|\Z)", frontmatter)
    if not name:
        errors.append("SKILL.md: missing name")
    elif name.group(1) != ROOT.name:
        errors.append(f"SKILL.md: name {name.group(1)!r} does not match folder {ROOT.name!r}")
    if not description or not description.group(1).strip():
        errors.append("SKILL.md: missing description")


def check_links(path: Path, text: str, errors: list[str]) -> None:
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if not (path.parent / target).resolve().is_file():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {raw_target!r}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    check_frontmatter(errors)
    files = tracked_files()
    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"publication artifact must not be committed: {relative}")
        if path.name.startswith(".env") and path.name != ".env.example":
            errors.append(f"environment file must not be committed: {relative}")
        if path.stat().st_size > 2_000_000:
            warnings.append(f"large file needs review: {relative} ({path.stat().st_size} bytes)")

        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(relative))
            except (SyntaxError, UnicodeDecodeError) as exc:
                errors.append(f"{relative}: Python parse failed: {exc}")

        if path.suffix.lower() not in {".md", ".py", ".yaml", ".yml", ".txt", ""}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # This checker necessarily contains the literal leak-detection patterns.
        if path.resolve() != Path(__file__).resolve():
            for label, pattern in LEAK_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"{relative}: possible {label}")
        if path.suffix.lower() == ".md":
            check_links(path, text, errors)

    print(f"Checked {len(files)} files in {ROOT.name}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED with {len(errors)} error(s)")
        return 1
    print("PASS: repository structure, syntax, links, and privacy patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
