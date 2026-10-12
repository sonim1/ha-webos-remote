"""Registration regression tests (no physical TV required)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lg_webos_remote'))
from pairing import PairingError, PairingKeyStorage, pairing_event, pairing_manifest, save_pairing_key, load_pairing_key
from bscpylgtv import WebOsClient
from unittest.mock import AsyncMock, patch

class PairingTests(unittest.TestCase):
    def test_immediate_registered_response(self):
        self.assertEqual(pairing_event({'type': 'registered', 'payload': {'client-key': 'test-credential'}}), ('paired','test-credential'))
    def test_pairing_pending(self):
        self.assertEqual(pairing_event({'type': 'response', 'payload': {'pairingType': 'PROMPT'}}),('pending',None))
    def test_rejection_has_only_code(self):
        self.assertEqual(pairing_event({'type': 'error', 'errorCode': '403', 'payload': {'sensitive':'x'}}),('error','403'))
    def test_key_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'keys'/'key.json'
            self.assertIsNone(load_pairing_key(path))
            save_pairing_key(path, 'test-credential')
            self.assertEqual(load_pairing_key(path),'test-credential')
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
    def test_manifest_has_required_permissions(self):
        self.assertIn('CONTROL_MOUSE_AND_KEYBOARD',pairing_manifest()['permissions'])
        self.assertIn('CONTROL_INPUT_TEXT',pairing_manifest()['permissions'])
    def test_corrupt_key_file_is_treated_as_unpaired(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'key.json'
            for raw in ('[]', 'null', '"invalid"', '{broken'):
                path.write_text(raw)
                self.assertIsNone(load_pairing_key(path))
    def test_rejection_does_not_return_arbitrary_tv_text(self):
        self.assertEqual(pairing_event({'type': 'error', 'error': 'private-tv-data'}),
                         ('error', 'unknown'))

class StorageTests(unittest.IsolatedAsyncioTestCase):
    async def test_library_reuses_existing_json_and_persists_updated_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'webos-client-key.json'
            save_pairing_key(path, 'test-credential')
            storage = PairingKeyStorage(path, '127.0.0.1')
            with patch('bscpylgtv.storage_sqlitedict.StorageSqliteDict.create',
                       new_callable=AsyncMock) as sqlite:
                client = await WebOsClient.create('127.0.0.1', storage=storage, states=[])
                self.assertEqual(client.client_key, 'test-credential')
                sqlite.assert_not_awaited()
            await storage.set_key('127.0.0.1', 'updated-test-credential')
            restarted = PairingKeyStorage(path, '127.0.0.1')
            self.assertEqual(await restarted.get_key('127.0.0.1'), 'updated-test-credential')
            self.assertIsNone(await restarted.get_key('other-tv'))
            self.assertEqual(await restarted.list_keys(), {'127.0.0.1': 'updated-test-credential'})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

if __name__ == '__main__': unittest.main()
