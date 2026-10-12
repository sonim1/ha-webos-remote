"""Independent LG webOS registration handshake (MIT).

A TV-supplied pairing credential is stored only within the app's private data
folder and is never included in diagnostics or passed to the frontend.
"""

import asyncio
import json
import os
import ssl
from pathlib import Path

from websockets.asyncio.client import connect


class PairingError(Exception):
    pass


def pairing_manifest():
    """Small, unsigned application identity for the webOS TV pairing API."""
    return {
        'manifestVersion': 1,
        'appVersion': '1.0',
        'appId': 'org.homeassistant.community.webosremote',
        'vendorId': 'ha-webos-remote',
        'deviceName': 'LG webOS Remote for Home Assistant',
        'localizedAppNames': {'': 'LG webOS Remote for Home Assistant'},
        'permissions': [
            'LAUNCH', 'CONTROL_MOUSE_AND_KEYBOARD', 'CONTROL_INPUT_TEXT',
            'CONTROL_AUDIO', 'CONTROL_POWER', 'READ_POWER_STATE',
            'READ_INSTALLED_APPS', 'READ_RUNNING_APPS', 'READ_APP_STATUS',
        ],
        'serial': 'ha-webos-remote-v1',
    }


def load_pairing_key(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        key = data.get('client_key')
        return key if isinstance(key, str) and key else None
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return None


def save_pairing_key(path, key):
    if not isinstance(key, str) or not key:
        raise ValueError('A nonempty pairing credential is required')
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Use restrictive permissions, including for an atomic replacement.
    tmp = dest.with_name(dest.name + '.tmp')
    fd = os.open(tmp, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            json.dump({'client_key': key}, file)
        os.replace(tmp, dest)
        os.chmod(dest, 0o600)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def pairing_event(reply, previous_key=None):
    """Parse only protocol state; never return/log raw TV responses."""
    if not isinstance(reply, dict):
        raise PairingError('TV returned an invalid pairing response')
    kind = reply.get('type')
    payload = reply.get('payload')
    payload = payload if isinstance(payload, dict) else {}
    if kind == 'registered':
        key = payload.get('client-key') or previous_key
        if not isinstance(key, str) or not key:
            raise PairingError('TV registered but did not provide a client key')
        return 'paired', key
    if kind == 'response' and payload.get('pairingType') in ('PROMPT', 'COMBINED'):
        return 'pending', None
    if kind == 'error':
        code = reply.get('errorCode', reply.get('error', 'unknown'))
        # Don't include arbitrary TV-supplied text in errors/logs.
        return 'error', str(code)[:32] if isinstance(code, (int, str)) else 'unknown'
    return 'other', None


async def pair_with_tv(ip, *, timeout=32):
    # LG televisions typically use their own self-signed TLS certificate.
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        async with connect(f'wss://{ip}:3001', ssl=ctx, open_timeout=5,
                           close_timeout=3, ping_interval=None) as ws:
            request = {
                'type': 'register', 'id': 'remote_pair',
                'payload': {
                    'pairingType': 'PROMPT',
                    'forcePairing': False,
                    'manifest': pairing_manifest(),
                },
            }
            await ws.send(json.dumps(request))
            deadline = asyncio.get_running_loop().time() + timeout
            while True:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    raise PairingError('TV pairing timed out: check the TV screen')
                raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
                status, value = pairing_event(json.loads(raw))
                if status == 'paired':
                    return value
                if status == 'error':
                    raise PairingError('TV rejected pairing request (error code: ' + value + ')')
                # pending: TV is awaiting user approval. other: continue briefly.
    except asyncio.TimeoutError as e:
        raise PairingError('TV did not respond to pairing request') from e
