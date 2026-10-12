"""Build a release ZIP that can be uploaded to Home Assistant Studio Code Server."""
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys

root = Path(__file__).resolve().parents[1]
version = (root / 'VERSION').read_text().strip()
archive = root / '.release' / f'ha-webos-remote-v{version}.zip'
archive.parent.mkdir(parents=True, exist_ok=True)
exclude = {'.git','.release','__pycache__','node_modules'}
with ZipFile(archive, 'w', ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(x in exclude for x in path.relative_to(root).parts) or path.suffix in {'.pyc','.sqlite'}:
            continue
        zf.write(path, f'ha-webos-remote/{path.relative_to(root)}')
print(archive)
