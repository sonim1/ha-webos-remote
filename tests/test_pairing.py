"""Registration regression tests (no physical TV required)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lg_webos_remote'))
from pairing import PairingError, pairing_event, pairing_manifest, save_pairing_key, load_pairing_key

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

if __name__ == '__main__': unittest.main()
