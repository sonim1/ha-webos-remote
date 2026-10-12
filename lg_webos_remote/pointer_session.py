"""Standalone webOS pointer channel using the documented SSAP register / pointer socket protocol.

Copyright (c) 2026 LG webOS Remote contributors. MIT License.
Uses the existing Remote Bridge's own saved pairing credential; no old bridge code.
"""
import asyncio
import json
import ssl

from websockets.asyncio.client import connect

from pairing import pairing_manifest


class PointerSessionError(Exception):
    pass


class PointerSession:
    """Own webOS control session plus its pointer socket, both persistent."""

    def __init__(self, ip: str, client_key: str):
        self.ip = ip
        self.key = client_key
        self.control = None
        self.pointer = None

    async def open(self):
        # webOS TV uses its own self-signed local TLS certificate.
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        tls.check_hostname = False
        tls.verify_mode = ssl.CERT_NONE
        try:
            self.control = await asyncio.wait_for(
                connect(f'wss://{self.ip}:3001', ssl=tls, open_timeout=5,
                        close_timeout=2, ping_interval=None), timeout=7)
            registration = {
                'type': 'register', 'id': 'rd_pointer_register',
                'payload': {
                    'pairingType': 'PROMPT', 'forcePairing': False,
                    'client-key': self.key, 'manifest': pairing_manifest(),
                },
            }
            await self.control.send(json.dumps(registration))
            # The TV can deliver a pending response before `registered`.
            accepted = False
            for _ in range(8):
                reply = json.loads(await asyncio.wait_for(self.control.recv(), timeout=3))
                event = reply.get('type')
                if event == 'registered':
                    accepted = True
                    break
                if event == 'error':
                    raise PointerSessionError('TV refused pointer-only registration')
            if not accepted:
                raise PointerSessionError('Pointer-only registration timed out')
            await self.control.send(json.dumps({
                'type':'request', 'id':'rd_pointer_socket',
                'uri':'ssap://com.webos.service.networkinput/getPointerInputSocket',
            }))
            path = None
            for _ in range(6):
                reply = json.loads(await asyncio.wait_for(self.control.recv(), timeout=3))
                if reply.get('id') != 'rd_pointer_socket':
                    continue
                if reply.get('type') == 'error':
                    raise PointerSessionError('TV refused native pointer socket request')
                payload = reply.get('payload') or {}
                path = payload.get('socketPath')
                break
            if not isinstance(path, str) or not path.startswith(('ws://', 'wss://')):
                raise PointerSessionError('TV did not return a pointer socket')
            pointer_tls = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if path.startswith('wss://') else None
            if pointer_tls is not None:
                pointer_tls.check_hostname = False
                pointer_tls.verify_mode = ssl.CERT_NONE
            self.pointer = await asyncio.wait_for(
                connect(path, ssl=pointer_tls, origin='https://www.lge.com',
                        ping_interval=20, close_timeout=2, open_timeout=5), timeout=7)
        except (Exception, asyncio.CancelledError):
            await self.close()
            raise

    async def send(self, payload: str):
        if self.pointer is None:
            raise PointerSessionError('Pointer socket is not connected')
        await self.pointer.send(payload)

    async def close(self):
        for name in ('pointer','control'):
            conn = getattr(self,name)
            setattr(self,name,None)
            if conn is not None:
                try:
                    await asyncio.wait_for(conn.close(), timeout=3)
                except Exception:
                    pass
