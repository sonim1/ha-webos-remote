import asyncio
import unittest
from unittest.mock import AsyncMock
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lg_webos_remote'))
from pointer_session import PointerSession, PointerSessionError

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_send_before_open_rejected(self):
        p=PointerSession('127.0.0.1','test')
        with self.assertRaises(PointerSessionError):
            await p.send('type:move\ndx:1\ndy:0\n\n')
    async def test_send_passes_native_payload_unchanged(self):
        p=PointerSession('127.0.0.1','test')
        p.pointer=AsyncMock()
        packet='type:move\ndx:25\ndy:0\n\n'
        await p.send(packet)
        p.pointer.send.assert_awaited_once_with(packet)
    async def test_close_both_sockets(self):
        p=PointerSession('127.0.0.1','test')
        p.pointer=AsyncMock(); p.control=AsyncMock()
        await p.close()
        self.assertIsNone(p.pointer)
        self.assertIsNone(p.control)

if __name__=='__main__': unittest.main()
