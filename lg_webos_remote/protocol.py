"""LG webOS Remote protocol helpers. Original work, MIT license."""
import re

ALLOWED_KEYS = frozenset({
    'BACK', 'HOME', 'MENU', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER',
    'PLAY', 'PAUSE', 'EXIT',
})


def valid_mac(value: str) -> bool:
    return bool(re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', value or ''))


def magic_packet(value: str) -> bytes:
    if not valid_mac(value):
        raise ValueError('Invalid MAC address')
    mac_bytes = bytes.fromhex(value.replace(':', ''))
    return b'\xff' * 6 + mac_bytes * 16


def clean_apps(raw):
    """Normalize the app list from the TV; never invent an app identifier."""
    out = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        app_id = item.get('id') or item.get('appId')
        label = item.get('title') or item.get('name') or app_id
        if isinstance(app_id, str) and app_id and isinstance(label, str):
            out.append({'id': app_id[:200], 'title': label[:100]})
    return out


def int_range(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Expected number')
    if value != value or not (low <= value <= high):
        raise ValueError('Value out of range')
    return int(round(value))


def split_relative_move(dx: int, dy: int, max_delta: int = 40):
    """Split relative LG pointer deltas into bounded, sum-preserving steps."""
    import math
    if not isinstance(dx, int) or not isinstance(dy, int):
        raise TypeError('integer pointer deltas required')
    if not isinstance(max_delta, int) or max_delta <= 0:
        raise ValueError('max_delta must be positive')
    steps = max(1, math.ceil(max(abs(dx), abs(dy)) / max_delta))
    last_x = last_y = 0
    out = []
    for step in range(1, steps + 1):
        x = round(dx * step / steps)
        y = round(dy * step / steps)
        part = (x - last_x, y - last_y)
        if part != (0, 0):
            out.append(part)
        last_x, last_y = x, y
    return out


def page_scroll_delta(direction: str) -> int:
    """StanbyME webOS scroll signs run opposite to visual Page Up/Down labels."""
    if direction == 'up':
        return 12
    if direction == 'down':
        return -12
    raise ValueError('Invalid page scroll direction')
