"""Independent Home Assistant addon for LG webOS Remote for Home Assistant (MIT).

TV control is delegated to the MIT-licensed bscpylgtv library; the original
Lovelace Touchpad Card and webOS Pointer Bridge source are not used.
"""
import asyncio
import hmac
import json
import logging
import os
import socket
from pathlib import Path

from bscpylgtv import WebOsClient
from pairing import PairingError, PairingKeyStorage, pairing_manifest, load_pairing_key, save_pairing_key, pair_with_tv
from pointer_session import PointerSession
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

from protocol import ALLOWED_KEYS, clean_apps, int_range, magic_packet, valid_mac, page_scroll_delta

LOG = logging.getLogger('lg_webos_remote')
OPTIONS = Path('/data/options.json')
DATA = Path('/data')


class LGWebOSRemoteServer:
    def __init__(self, settings):
        self.tv_ip = settings['tv_ip']
        self.mac = settings['mac_address']
        self.token = settings['auth_token']
        self.listen_port = int(settings.get('listen_port', 8788))
        self.broadcast = settings.get('broadcast_address') or '255.255.255.255'
        self.client = None
        self.pointer_ws = None
        self.pointer_session = None
        self.pointer_lock = asyncio.Lock()
        self.online = False
        self.apps = []
        self.tv_lock = asyncio.Lock()
        self.connections = set()
        self.last_error = ''

    async def connect_loop(self):
        while True:
            if not self.online:
                try:
                    await self._connect()
                except Exception as exc:
                    reason = str(exc) if isinstance(exc, PairingError) else type(exc).__name__
                    if reason != self.last_error:
                        LOG.info('TV connection unavailable; retrying (%s)', reason[:180])
                        self.last_error = reason
                await asyncio.sleep(8)
            else:
                try:
                    if not self.client or not self.client.is_connected():
                        raise ConnectionError('TV connection closed')
                    # Lightweight state probe. Treat the TV as offline on errors.
                    await asyncio.wait_for(self.client.get_power_state(), timeout=4)
                except Exception:
                    self.online = False
                    await self._notify_status()
                    await self._disconnect_tv()
                await asyncio.sleep(8)

    async def _connect(self):
        # Pair independently first. Some TVs return `registered` immediately;
        # bscpylgtv 0.5.5 doesn't handle that initial reply when no key exists.
        # Never copy keys from other apps or print the returned TV credential.
        key_path = DATA / 'webos-client-key.json'
        key = load_pairing_key(key_path)
        if not key:
            LOG.info('Requesting TV pairing (the TV may show an Allow prompt)')
            key = await pair_with_tv(self.tv_ip)
            save_pairing_key(key_path, key)
            LOG.info('TV pairing credentials saved privately')

        storage = PairingKeyStorage(key_path, self.tv_ip)
        client = await WebOsClient.create(
            self.tv_ip, client_key=key, storage=storage,
            states=[], ping_interval=None, timeout_connect=4,
            connect_retry_attempts=2, connect_retry_interval_ms=350,
        )
        # Use the same application identity for registration and control.
        client.manifest = pairing_manifest()
        try:
            await asyncio.wait_for(client.connect(), timeout=18)
            # The library may treat unexpected registration replies as success
            # when a cached key exists. Verify a real authenticated API call.
            await asyncio.wait_for(client.get_power_state(), timeout=5)
        except Exception:
            await client.disconnect()
            raise
        if client.client_key and client.client_key != key:
            save_pairing_key(key_path, client.client_key)
        self.client = client
        self.online = True
        self.last_error = ''
        LOG.info('TV paired/connected')
        await self._refresh_apps()
        await self._notify_status()

    async def _send_pointer(self, payload: str):
        """Send input on an independent registered webOS control and pointer channel.

        This keeps native pointer messages away from the bscpylgtv session used for
        TV status, application and power commands, to diagnose cursor resets.
        """
        async with self.pointer_lock:
            if self.pointer_session is None:
                if not self.client or not self.online:
                    raise ConnectionError('TV session not available')
                saved_key = load_pairing_key(DATA / 'webos-client-key.json')
                if not saved_key:
                    raise ConnectionError('No saved TV pairing credential')
                ps = PointerSession(self.tv_ip, saved_key)
                await ps.open()
                self.pointer_session = ps
                LOG.info('Independent webOS pointer session established')
            try:
                await self.pointer_session.send(payload)
            except Exception:
                await self._close_pointer()
                raise

    async def _close_pointer(self):
        if self.pointer_session is not None:
            ps = self.pointer_session
            self.pointer_session = None
            await ps.close()

    async def _move_pointer(self, x: int, y: int):
        # LG webOS pointer movement is relative and non-linear on large deltas.
        # Small packets prevent jumps. This deliberately does not send down:0.
        from protocol import split_relative_move
        for dx, dy in split_relative_move(x, y, max_delta=40):
            await self._send_pointer(f'type:move\ndx:{dx}\ndy:{dy}\n\n')

    async def _disconnect_tv(self):
        await self._close_pointer()
        client = self.client
        self.client = None
        if client:
            try:
                await asyncio.wait_for(client.disconnect(), timeout=3)
            except Exception:
                pass

    async def _refresh_apps(self):
        if not self.client or not self.online:
            return
        try:
            self.apps = clean_apps(await asyncio.wait_for(self.client.get_apps(), timeout=8))
            if not any('gallery' in (a['title']+' '+a['id']).lower() for a in self.apps):
                try:
                    hidden = clean_apps(await asyncio.wait_for(self.client.get_apps_all(), timeout=8))
                    known = {a['id'] for a in self.apps}
                    self.apps.extend(a for a in hidden if a['id'] not in known)
                except Exception:
                    pass
            LOG.info('TV provided %d app entries', len(self.apps))
        except Exception as exc:
            LOG.warning('TV app discovery unavailable: %s', type(exc).__name__)
            self.apps = []
        await self._notify_apps()

    async def _notify_status(self):
        await self._broadcast({'type':'status','online':self.online})

    async def _notify_apps(self):
        await self._broadcast({'type':'apps','apps':self.apps})

    async def _broadcast(self, message):
        payload = json.dumps(message, ensure_ascii=False)
        for ws in tuple(self.connections):
            try:
                await ws.send(payload)
            except ConnectionClosed:
                self.connections.discard(ws)

    def wake(self):
        packet = magic_packet(self.mac)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(packet, (self.broadcast, 9))
        LOG.info('Wake-on-LAN packet sent')

    async def _perform(self, message):
        kind = message.get('type')
        if kind == 'status':
            return {'type':'status','online':self.online}
        if kind == 'apps':
            if self.online and not self.apps: await self._refresh_apps()
            return {'type':'apps','apps':self.apps}
        if kind == 'power':
            if self.online and self.client:
                try:
                    await asyncio.wait_for(self.client.power_off(),timeout=7)
                    self.online = False
                    await self._disconnect_tv()
                except Exception:
                    # If the TV is disconnecting, this can mean power-off succeeded.
                    self.online=False
                    await self._disconnect_tv()
            else:
                self.wake()
            await self._notify_status()
            return {'type':'notice','message':'Power command sent'}
        if not self.online or not self.client:
            return {'type':'error','message':'TV is offline. Use the Power button to wake it.'}
        tv = self.client
        if kind == 'move':
            x = int_range(message.get('dx'), -250, 250)
            y = int_range(message.get('dy'), -250, 250)
            if x or y: await self._move_pointer(x, y)
        elif kind == 'scroll':
            x = int_range(message.get('dx'), -40, 40)
            y = int_range(message.get('dy'), -40, 40)
            if x or y: await self._send_pointer(f'type:scroll\ndx:{x}\ndy:{y}\n\n')
        elif kind == 'page':
            direction = message.get('direction')
            dy = page_scroll_delta(direction)
            await self._send_pointer(f'type:scroll\ndx:0\ndy:{dy}\n\n')
        elif kind == 'click':
            await self._send_pointer('type:click\n\n')
        elif kind == 'key':
            key = message.get('key')
            if key not in ALLOWED_KEYS: raise ValueError('Unsupported key')
            await self._send_pointer(f'type:button\nname:{key}\n\n')
        elif kind == 'text':
            text=message.get('text')
            replace=message.get('replace',False)
            if not isinstance(replace,bool): raise ValueError('replace must be boolean')
            if not isinstance(text,str) or len(text)>500 or (not text and not replace):
                raise ValueError('Text must be 1–500 chars, or empty when replacing')
            # TV IME only works in apps that expose a compatible focused text field.
            await asyncio.wait_for(tv.insert_text(text,replace=replace),timeout=8)
        elif kind == 'volume':
            action=message.get('action')
            if action=='up': await tv.volume_up()
            elif action=='down': await tv.volume_down()
            elif action=='mute': await tv.set_mute(not bool(await tv.get_muted()))
            else: raise ValueError('Unsupported volume action')
        elif kind == 'launch':
            alias=message.get('alias')
            if alias not in {'netflix','internet','youtube','gallery'}:
                raise ValueError('Unsupported app shortcut')
            def matches(app):
                value=(app['title']+' '+app['id']).lower()
                if alias=='internet': return 'browser' in value or 'internet' in value
                if alias=='gallery': return 'gallery' in value
                return alias in value
            candidate=next((a for a in self.apps if matches(a)),None)
            if candidate is None: raise ValueError('App not found on this TV')
            await tv.launch_app(candidate['id'])
        else:
            raise ValueError('Unknown command')
        return None

    async def handle(self, ws):
        try:
            # Require authentication as first message; no token in URL or logs.
            first = await asyncio.wait_for(ws.recv(),timeout=5)
            data = json.loads(first)
            if not isinstance(data,dict) or data.get('type')!='auth' or not isinstance(data.get('token'),str) or not hmac.compare_digest(data['token'],self.token):
                await ws.close(code=1008,reason='Unauthorized');return
        except (asyncio.TimeoutError,ValueError,TypeError,ConnectionClosed):
            await ws.close(code=1008,reason='Unauthorized');return
        self.connections.add(ws)
        try:
            await ws.send(json.dumps({'type':'auth-ok'}))
            await ws.send(json.dumps({'type':'status','online':self.online}))
            await ws.send(json.dumps({'type':'apps','apps':self.apps},ensure_ascii=False))
            async for raw in ws:
                try:
                    data=json.loads(raw)
                    if not isinstance(data,dict): raise ValueError('Expected JSON object')
                    # Serialize TV commands; hard cap their duration and input size.
                    async with self.tv_lock:
                        reply=await asyncio.wait_for(self._perform(data),timeout=13)
                    if reply is not None:
                        await ws.send(json.dumps(reply,ensure_ascii=False))
                except (ValueError,TypeError,KeyError) as exc:
                    await ws.send(json.dumps({'type':'error','message':str(exc)[:160]}))
                except (asyncio.TimeoutError,Exception) as exc:
                    LOG.warning('TV command failed: %s',type(exc).__name__)
                    await ws.send(json.dumps({'type':'error','message':'TV did not accept that command'}))
        except ConnectionClosed:
            pass
        finally:
            self.connections.discard(ws)

    async def start(self):
        loop=asyncio.create_task(self.connect_loop())
        try:
            async with serve(self.handle,'0.0.0.0',self.listen_port,max_size=8192,max_queue=16,compression=None,open_timeout=5) as _:
                LOG.info('LG webOS Remote listening on port %d (local network only)',self.listen_port)
                await asyncio.Future()
        finally:
            loop.cancel()
            await self._disconnect_tv()


def load_options():
    with OPTIONS.open(encoding='utf-8') as fp:
        data=json.load(fp)
    if not isinstance(data,dict): raise ValueError('Invalid app configuration')
    if not data.get('tv_ip') or not valid_mac(data.get('mac_address')):
        raise ValueError('Set TV IP and valid MAC address first')
    if not isinstance(data.get('auth_token'),str) or len(data['auth_token'])<40:
        raise ValueError('Configure a random auth_token of 40+ characters first')
    port=int(data.get('listen_port',8788))
    if not (1024<=port<=65535): raise ValueError('Invalid port')
    socket.inet_aton(data['tv_ip'])
    socket.inet_aton(data.get('broadcast_address') or '255.255.255.255')
    return data

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    asyncio.run(LGWebOSRemoteServer(load_options()).start())
