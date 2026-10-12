"""Build a release ZIP that can be uploaded to Home Assistant Studio Code Server."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess

root = Path(__file__).resolve().parents[1]
version = (root / 'VERSION').read_text().strip()
archive = root / '.release' / f'ha-webos-remote-v{version}.zip'
archive.parent.mkdir(parents=True, exist_ok=True)
files = subprocess.run(
    ['git', 'ls-files', '-z'], cwd=root, check=True, capture_output=True, text=True,
).stdout.split('\0')
with ZipFile(archive, 'w', ZIP_DEFLATED) as zf:
    for name in sorted(filter(None, files)):
        path = root / name
        if path.is_symlink():
            raise RuntimeError(f'Release source must not be a symbolic link: {name}')
        if path.suffix in {'.pyc', '.sqlite'}:
            continue
        zf.write(path, f'ha-webos-remote/{name}')
print(archive)
