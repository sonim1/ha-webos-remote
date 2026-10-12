# Security policy

**Community-maintained software.** No third-party audit has been performed; use on a trusted local network only.

- The app binds to `0.0.0.0:8788` by default and authenticates incoming WebSocket connections with a random 40+ character token. **It does not encrypt `ws://` traffic.**
- Never forward port 8788 to the internet; use network controls and TLS termination if providing remote access.
- Home Assistant card configuration contains a secret token. Keep backups and screenshots private. Pairing credentials are stored in the app's data volume, not in GitHub.
- Do not report secrets, device identifiers, or unredacted logs in public issues.
- If you believe you found a vulnerability, use the GitHub private security advisory feature once the public repository is configured. Otherwise, contact the repository maintainer privately.
- Dependency versions are pinned in `lg_webos_remote/requirements.txt`; review security updates before increasing versions.

This repository does not include the CC BY-NC-ND-licensed Lovelace Touchpad Card or Pointer Bridge implementation; see NOTICE.md.

## Known dependency advisory

`bscpylgtv==0.5.5` installs `sqlitedict==2.1.0` transitively. [CVE-2024-35515 / GHSA-g4r7-86gm-pgqc](https://github.com/advisories/GHSA-g4r7-86gm-pgqc) concerns pickle deserialization of an attacker-controlled SQLite database. No patched sqlitedict release was listed during v1.0.0 preparation.

The Bridge supplies its own JSON storage adapter to bscpylgtv and never opens its SQLite pairing database. It preserves the existing `/data/webos-client-key.json` format, writes with mode `0600`, and reuses the key after restart. Existing `pairing.sqlite` files are not migrated, deserialized, or deleted. Do not import untrusted pairing files, database files, or Home Assistant backups.

The vulnerable dependency remains installed by the library, so dependency scanners still report this advisory. This mitigation removes the Bridge's SQLite/pickle path; it does not patch the upstream package or constitute an independent security audit. Monitor upstream dependency updates. Run a full audit without suppressing this finding:

```sh
python -m pip install pip-audit
python -m pip_audit -r lg_webos_remote/requirements.txt
```
