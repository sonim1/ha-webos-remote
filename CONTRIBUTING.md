# Contributing

Discuss larger features in an issue first. Include the TV model, firmware, project version, reproduction steps and sanitized logs when reporting a problem.

## Local setup

Use Node.js 22+, Python 3.13+ and Git:

```sh
git clone https://github.com/sonim1/ha-webos-remote.git
cd ha-webos-remote
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r lg_webos_remote/requirements.txt pyyaml
```

Run the existing checks before submitting a change:

```sh
npm run build
npm run verify
python3 -m py_compile lg_webos_remote/*.py
git diff --check
```

Edit the card in `src/lg-webos-remote-card.js` and rebuild `ha-webos-remote.js`. The distribution file must match the source.

## Changes and tests

- Preserve the independent pointer session and existing card/Bridge message protocol.
- Add regression coverage for behavior changes. Tests use real loopback WebSockets, synthetic configuration and mocked TV/WOL side effects.
- Keep hardware observations separate from automated results. Pairing, pointer behavior and application compatibility need actual TV testing.
- Keep configuration keys compatible and record user-visible changes in `CHANGELOG.md`.
- ZIP packaging includes tracked Git files only. Stage new public files before packaging and inspect the archive contents.

## Licensing and private data

Keep the project independently authored. Do not copy CC BY-NC-ND Lovelace Touchpad Card or Pointer Bridge source. Preserve the project license and required dependency notices in [NOTICE.md](NOTICE.md).

Do not commit tokens, pairing keys, real device IP/MAC addresses, local configuration or Home Assistant backups. For vulnerability reporting, see [SECURITY.md](SECURITY.md).

Maintainers publish releases through the [release workflow](docs/PUBLISHING.md).
