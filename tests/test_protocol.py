import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lg_webos_remote'))
from protocol import ALLOWED_KEYS, clean_apps, int_range, magic_packet, valid_mac, split_relative_move, page_scroll_delta

class ProtocolTests(unittest.TestCase):
    def test_wol(self):
        mac='02:12:34:56:78:9a'
        self.assertTrue(valid_mac(mac))
        self.assertEqual(len(magic_packet(mac)),102)
        self.assertEqual(magic_packet(mac)[:6],b'\xff'*6)
        self.assertEqual(magic_packet(mac)[6:12],bytes.fromhex('02123456789a'))
    def test_reject_mac(self):
        for invalid in ('', '12:34:56:78:90', 'ZZ:11:22:33:44:55', '../x'):
            self.assertFalse(valid_mac(invalid))
            with self.assertRaises(ValueError): magic_packet(invalid)
    def test_apps(self):
        self.assertEqual(clean_apps([{'id':'a','title':'Gallery+'}, {'name':'Broken'},'oops']),[{'id':'a','title':'Gallery+'}])
    def test_bounds(self):
        self.assertEqual(int_range(2.6,-5,5),3)
        for x in (None,float('nan'),True,100):
            with self.assertRaises(ValueError): int_range(x,-5,5)
    def test_pointer_chunks(self):
        for dx, dy in ((0, 0), (250, 0), (3, -250), (-250, -100), (40, 40)):
            parts = split_relative_move(dx, dy)
            self.assertEqual(sum(a for a, _ in parts), dx)
            self.assertEqual(sum(b for _, b in parts), dy)
            self.assertTrue(all(abs(a) <= 40 and abs(b) <= 40 for a, b in parts))

    def test_page_direction(self):
        self.assertEqual(page_scroll_delta('up'),24)
        self.assertEqual(page_scroll_delta('down'),-24)
        with self.assertRaises(ValueError): page_scroll_delta('unknown')

    def test_keys(self):
        self.assertIn('HOME',ALLOWED_KEYS)
        self.assertNotIn('FACTORY_RESET',ALLOWED_KEYS)

if __name__=='__main__':unittest.main()
