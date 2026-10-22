#!/usr/bin/env python3
"""Check read-only resource accounting and CLI failure modes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'inspect_epub_size.py'


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'fixture.epub'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as package:
            package.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            package.writestr('EPUB/chapter.xhtml', '<p>Example</p>')
            package.writestr('EPUB/images/a.png', b'abc' * 1000)
            package.writestr('EPUB/images/B.PNG', b'def' * 500)
        baseline = path.read_bytes()
        result = run(path, '--largest', 2)
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data['files'] == 4 and data['by_extension']['.png']['files'] == 2
        with zipfile.ZipFile(path) as package:
            expected = sum(item.compress_size for item in package.infolist())
        assert data['compressed_payload_bytes'] == expected
        assert data['archive_bytes'] == len(baseline)
        assert data['zip_overhead_bytes'] + expected == len(baseline)
        assert len(data['largest']) == 2
        assert data['largest'][0]['compressed_bytes'] >= data['largest'][1]['compressed_bytes']
        assert not json.loads(run(path, '--largest', 0).stdout)['largest']
        assert run(path, '--largest', -1).returncode != 0
        assert run(Path(directory) / 'missing.epub').returncode != 0
        bad = Path(directory) / 'invalid.epub'
        bad.write_text('not a ZIP')
        assert run(bad).returncode != 0
        assert path.read_bytes() == baseline
    print('PASS: EPUB resource size accounting, read-only behavior and CLI errors')


if __name__ == '__main__':
    main()
