#!/usr/bin/env python3
"""Render PDF pages to a task-local directory using pdftoppm."""
from __future__ import annotations
import argparse, shutil, subprocess
from pathlib import Path

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("pdf", type=Path); ap.add_argument("out", type=Path); ap.add_argument("--dpi", type=int, default=220); ap.add_argument("--first", type=int); ap.add_argument("--last", type=int); a = ap.parse_args()
    if not shutil.which("pdftoppm"): raise SystemExit("pdftoppm is required")
    a.out.mkdir(parents=True, exist_ok=True)
    cmd = ["pdftoppm", "-r", str(a.dpi), "-jpeg"]
    if a.first: cmd += ["-f", str(a.first)]
    if a.last: cmd += ["-l", str(a.last)]
    subprocess.run(cmd + [str(a.pdf), str(a.out / "page")], check=True)

if __name__ == "__main__": main()
