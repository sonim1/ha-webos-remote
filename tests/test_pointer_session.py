import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch
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

    async def test_open_registers_once_and_keeps_separate_pointer_socket(self) -> None:
        control = AsyncMock()
        pointer = AsyncMock()
        control.recv.side_effect = [json.dumps(reply) for reply in (
            {'type': 'response', 'payload': {'pairingType': 'PROMPT'}},
            {'type': 'registered'},
            {'type': 'response', 'id': 'unrelated'},
            {'type': 'response', 'id': 'rd_pointer_socket',
             'payload': {'socketPath': 'ws://127.0.0.1:3000/pointer'}},
        )]
        session = PointerSession('127.0.0.1', 'test-credential')
        with patch('pointer_session.connect', new_callable=AsyncMock,
                   side_effect=[control, pointer]) as connect:
            await session.open()
            await session.send('type:move\ndx:30\ndy:0\n\n')
            await session.send('type:click\n\n')
            self.assertEqual(connect.await_count, 2)
            registration, request = [json.loads(call.args[0]) for call in control.send.await_args_list]
            self.assertEqual(registration['payload']['client-key'], 'test-credential')
            self.assertEqual(request['uri'], 'ssap://com.webos.service.networkinput/getPointerInputSocket')
            self.assertIs(session.control, control)
            self.assertIs(session.pointer, pointer)
            self.assertEqual(pointer.send.await_count, 2)
            await session.close()
            control.close.assert_awaited_once()
            pointer.close.assert_awaited_once()

    async def test_cancelled_open_closes_control_socket(self) -> None:
        control = AsyncMock()
        receiving = asyncio.Event()

        async def blocked_receive() -> str:
            receiving.set()
            await asyncio.Future()
            return ''

        control.recv.side_effect = blocked_receive
        session = PointerSession('127.0.0.1', 'test-credential')
        with patch('pointer_session.connect', new_callable=AsyncMock, return_value=control):
            task = asyncio.create_task(session.open())
            await asyncio.wait_for(receiving.wait(), timeout=3)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            control.close.assert_awaited_once()
            self.assertIsNone(session.control)

if __name__=='__main__': unittest.main()
