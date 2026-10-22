#!/usr/bin/env python3
"""Read-only EPUB ZIP size inventory; standard library only."""
import argparse
import collections
import json
from pathlib import Path
import zipfile


def inspect(path, largest=10):
    path = Path(path)
    with zipfile.ZipFile(path) as package:
        entries = [entry for entry in package.infolist() if not entry.is_dir()]
    groups = collections.defaultdict(lambda: dict(files=0, uncompressed_bytes=0, compressed_bytes=0))
    total = sum(entry.compress_size for entry in entries)
    for entry in entries:
        kind = Path(entry.filename).suffix.lower() or '(no extension)'
        group = groups[kind]
        group['files'] += 1
        group['uncompressed_bytes'] += entry.file_size
        group['compressed_bytes'] += entry.compress_size
    for group in groups.values():
        group['payload_percent'] = round(100 * group['compressed_bytes'] / total, 2) if total else 0
    return dict(
        archive_bytes=path.stat().st_size,
        compressed_payload_bytes=total,
        zip_overhead_bytes=path.stat().st_size - total,
        files=len(entries),
        by_extension=dict(sorted(groups.items(), key=lambda item: item[1]['compressed_bytes'], reverse=True)),
        largest=[dict(path=entry.filename, compressed_bytes=entry.compress_size,
                      uncompressed_bytes=entry.file_size)
                 for entry in sorted(entries, key=lambda entry: entry.compress_size, reverse=True)[:largest]],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('epub', type=Path)
    parser.add_argument('--largest', type=int, default=10)
    args = parser.parse_args()
    if args.largest < 0:
        parser.error('--largest must be nonnegative')
    try:
        result = inspect(args.epub, args.largest)
    except (OSError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
