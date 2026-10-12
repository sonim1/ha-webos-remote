import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


class PackageTests(unittest.TestCase):
    def test_archive_excludes_local_credentials_and_environments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            shutil.copyfile(Path(__file__).resolve().parents[1] / 'scripts/package.py',
                            root / 'scripts/package.py')
            (root / 'VERSION').write_text('1.0.0\n')
            (root / 'README.md').write_text('Public release fixture\n')
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            for name in ('.env', 'webos-client-key.json', '.venv/dependency.txt',
                         '.qa/evidence.txt', 'docs/private-notes.txt'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('private fixture; never distribute\n')
            subprocess.run([sys.executable, str(root / 'scripts/package.py')],
                           check=True, capture_output=True, text=True)
            with ZipFile(root / '.release/ha-webos-remote-v1.0.0.zip') as archive:
                self.assertEqual(set(archive.namelist()), {
                    'ha-webos-remote/VERSION', 'ha-webos-remote/README.md',
                    'ha-webos-remote/scripts/package.py',
                })
                self.assertEqual(archive.read('ha-webos-remote/README.md'),
                                 b'Public release fixture\n')
