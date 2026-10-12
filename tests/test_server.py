import asyncio
import json
import secrets
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from websockets.asyncio.client import connect, ClientConnection
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lg_webos_remote'))
import server
from pairing import PairingError, save_pairing_key
from protocol import magic_packet


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bridge = server.LGWebOSRemoteServer({
            'tv_ip': '127.0.0.1', 'mac_address': '02:00:00:00:00:01',
            'auth_token': secrets.token_urlsafe(32),
        })
        self.listener = await serve(self.bridge.handle, '127.0.0.1', 0,
                                    max_size=8192, compression=None)
        self.addAsyncCleanup(self.listener.__aexit__, None, None, None)
        port = self.listener.sockets[0].getsockname()[1]
        self.endpoint = f'ws://127.0.0.1:{port}'

    async def authenticate(self, ws: ClientConnection) -> None:
        await ws.send(json.dumps({'type': 'auth', 'token': self.bridge.token}))
        for kind in ('auth-ok', 'status', 'apps'):
            reply = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
            self.assertEqual(reply['type'], kind)

    async def test_invalid_auth_cannot_dispatch_commands(self) -> None:
        with patch.object(self.bridge, 'wake') as wake:
            for raw in ('not-json', '[]', '{"type":"power"}',
                        '{"type":"auth","token":"wrong"}',
                        '{"type":"auth","token":"한글"}'):
                with self.subTest(raw=raw):
                    async with connect(self.endpoint, proxy=None) as ws:
                        await ws.send(raw)
                        await asyncio.wait_for(ws.wait_closed(), timeout=3)
                        self.assertEqual(ws.close_code, 1008)
            wake.assert_not_called()
            self.assertFalse(self.bridge.connections)

    async def test_authenticated_status_and_apps_round_trip(self) -> None:
        async with connect(self.endpoint, proxy=None) as ws:
            await self.authenticate(ws)
            for kind in ('status', 'apps'):
                await ws.send(json.dumps({'type': kind}))
                reply = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                self.assertEqual(reply['type'], kind)

    async def test_malformed_commands_are_rejected_and_connection_survives(self) -> None:
        self.bridge.online = True
        self.bridge.client = Mock()
        with patch.object(self.bridge, '_send_pointer', new_callable=AsyncMock) as pointer:
            async with connect(self.endpoint, proxy=None) as ws:
                await self.authenticate(ws)
                for raw in ('not-json', '[]', '{"type":"factory-reset"}',
                            '{"type":"move","dx":true,"dy":0}',
                            '{"type":"move","dx":251,"dy":0}',
                            '{"type":"key","key":"FACTORY_RESET"}',
                            '{"type":"text","text":"","replace":false}',
                            '{"type":"page","direction":"unknown"}'):
                    with self.subTest(raw=raw):
                        await ws.send(raw)
                        reply = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                        self.assertEqual(reply['type'], 'error')
                await ws.send('{"type":"status"}')
                reply = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                self.assertTrue(reply['online'])
                pointer.assert_not_awaited()

    async def test_offline_power_sends_wol_without_tv_client(self) -> None:
        async with connect(self.endpoint, proxy=None) as ws:
            await self.authenticate(ws)
            with patch('server.socket.socket') as socket_factory:
                sock = socket_factory.return_value.__enter__.return_value
                await ws.send('{"type":"power"}')
                replies = [json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                           for _ in range(2)]
                self.assertEqual([reply['type'] for reply in replies], ['status', 'notice'])
                sock.sendto.assert_called_once_with(
                    magic_packet('02:00:00:00:00:01'), ('255.255.255.255', 9))
                self.assertIsNone(self.bridge.client)

    async def test_oversized_message_closes_connection(self) -> None:
        async with connect(self.endpoint, proxy=None) as ws:
            await self.authenticate(ws)
            await ws.send('x' * 8193)
            with self.assertRaises(ConnectionClosed):
                await asyncio.wait_for(ws.recv(), timeout=3)
            self.assertEqual(ws.close_code, 1009)

    async def test_native_pointer_session_is_opened_once_and_reused(self) -> None:
        self.bridge.online = True
        self.bridge.client = Mock()
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            save_pairing_key(data / 'webos-client-key.json', 'test-credential')
            pointer = AsyncMock()
            with patch.object(server, 'DATA', data), patch.object(
                server, 'PointerSession', return_value=pointer,
            ) as factory:
                await self.bridge._send_pointer('type:click\n\n')
                await self.bridge._move_pointer(100, -80)
                factory.assert_called_once_with('127.0.0.1', 'test-credential')
                pointer.open.assert_awaited_once()
                packets = [call.args[0] for call in pointer.send.await_args_list]
                self.assertEqual(packets[0], 'type:click\n\n')
                parts = [dict(line.split(':', 1) for line in packet.strip().splitlines())
                         for packet in packets[1:]]
                self.assertEqual(sum(int(part['dx']) for part in parts), 100)
                self.assertEqual(sum(int(part['dy']) for part in parts), -80)
                self.assertTrue(all('down' not in part for part in parts))
                await self.bridge._disconnect_tv()
                pointer.close.assert_awaited_once()
                self.assertIsNone(self.bridge.pointer_session)

    async def test_reconnect_reuses_json_key_without_opening_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            save_pairing_key(data / 'webos-client-key.json', 'test-credential')
            client = AsyncMock()
            client.client_key = 'test-credential'
            client.get_apps.return_value = [{'id': 'fixture.gallery', 'title': 'Gallery+'}]
            with patch.object(server, 'DATA', data), patch.object(
                server.WebOsClient, 'create', new_callable=AsyncMock, return_value=client,
            ) as create, patch.object(server, 'pair_with_tv', new_callable=AsyncMock) as pair, patch(
                'bscpylgtv.storage_sqlitedict.StorageSqliteDict.create',
                new_callable=AsyncMock,
            ) as sqlite:
                await self.bridge._connect()
                pair.assert_not_awaited()
                sqlite.assert_not_awaited()
                self.assertEqual(create.call_args.kwargs['client_key'], 'test-credential')
                self.assertTrue(self.bridge.online)

    async def test_text_app_and_page_payloads_preserve_protocol(self) -> None:
        self.bridge.online = True
        self.bridge.client = AsyncMock()
        self.bridge.apps = [{'id': 'fixture.browser', 'title': 'Internet'}]
        await self.bridge._perform({'type': 'text', 'text': 'Hello 한글', 'replace': False})
        self.bridge.client.insert_text.assert_awaited_once_with('Hello 한글', replace=False)
        await self.bridge._perform({'type': 'launch', 'alias': 'internet'})
        self.bridge.client.launch_app.assert_awaited_once_with('fixture.browser')
        with patch.object(self.bridge, '_send_pointer', new_callable=AsyncMock) as pointer:
            await self.bridge._perform({'type': 'page', 'direction': 'down'})
            pointer.assert_awaited_once_with('type:scroll\ndx:0\ndy:-12\n\n')

    async def test_connection_logs_keep_pairing_guidance_and_hide_raw_errors(self) -> None:
        for error, expected in ((PairingError('TV did not respond to pairing request'),
                                 'TV did not respond to pairing request'),
                                (OSError('private-device-fixture'), 'OSError')):
            with self.subTest(error=type(error).__name__), patch.object(
                self.bridge, '_connect', new_callable=AsyncMock, side_effect=error,
            ), patch('server.asyncio.sleep', new_callable=AsyncMock,
                     side_effect=asyncio.CancelledError), self.assertLogs(server.LOG, level='INFO') as logs:
                with self.assertRaises(asyncio.CancelledError):
                    await self.bridge.connect_loop()
                self.assertIn(expected, logs.output[0])
                self.assertNotIn('private-device-fixture', logs.output[0])
