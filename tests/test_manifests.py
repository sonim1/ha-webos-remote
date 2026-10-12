import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_release_versions_match(self) -> None:
        version = (ROOT / 'VERSION').read_text().strip()
        package = json.loads((ROOT / 'package.json').read_text())
        addon = yaml.safe_load((ROOT / 'lg_webos_remote/config.yaml').read_text())
        self.assertEqual(package['version'], version)
        self.assertEqual(addon['version'], version)

    def test_app_repository_and_options_are_consistent(self) -> None:
        repository = yaml.safe_load((ROOT / 'repository.yaml').read_text())
        addon = yaml.safe_load((ROOT / 'lg_webos_remote/config.yaml').read_text())
        self.assertEqual(repository['url'], addon['url'])
        self.assertEqual(addon['slug'], 'lg_webos_remote')
        self.assertTrue(addon['host_network'])
        self.assertFalse(addon['homeassistant_api'])
        self.assertEqual(set(addon['arch']), {'aarch64', 'amd64'})
        self.assertEqual(set(addon['options']), set(addon['schema']))
        self.assertEqual(addon['schema']['auth_token'], 'password')
        self.assertEqual(addon['options']['auth_token'], '')
        self.assertEqual(addon['options']['tv_ip'], '')
        self.assertEqual(addon['options']['mac_address'], '')
