#!/usr/bin/env python3
"""Regression tests for numbered-block continuation auditing."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_reflow", ROOT / "scripts" / "audit_reflow.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def xhtml(body: str) -> bytes:
    return (
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops"><body>'
        f"{body}</body></html>"
    ).encode("utf-8")


def main() -> None:
    broken = xhtml(
        '<p class="list-item">（3）一个仍未结束的条目</p>'
        '<p class="body">在这里继续并结束。</p>'
    )
    findings = MODULE.audit_xhtml(broken, "broken.xhtml")
    assert len(findings) == 1
    assert findings[0]["following"] == "在这里继续并结束。"

    repaired = xhtml(
        '<p class="list-item">（3）一个仍未结束的条目在这里继续并结束。</p>'
        '<p class="body">这是列表后的新段。</p>'
    )
    assert MODULE.audit_xhtml(repaired, "repaired.xhtml") == []

    next_item = xhtml(
        '<p class="list-item">（3）第一个条目即使没有句号</p>'
        '<p class="list-item">（4）下一个条目。</p>'
    )
    assert MODULE.audit_xhtml(next_item, "next-item.xhtml") == []

    note = xhtml(
        '<section epub:type="endnotes"><p class="note">1 一条未加句号的注释</p>'
        '<p class="note">注释续文。</p></section>'
    )
    assert MODULE.audit_xhtml(note, "notes.xhtml") == []
    print("PASS: numbered-block continuation audit regression cases")


if __name__ == "__main__":
    main()
