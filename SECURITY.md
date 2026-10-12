# Security policy

Use the Bridge on a trusted local network. No independent security audit has been performed.

- The app binds to `0.0.0.0:8788` by default and authenticates incoming WebSocket connections with a random 40+ character token. **It does not encrypt `ws://` traffic.**
- Never forward port 8788 to the internet; use network controls and TLS termination if providing remote access.
- Home Assistant card configuration contains a secret token. Keep backups and screenshots private. Pairing credentials are stored in the app's data volume, not in GitHub.
- Do not report secrets, device identifiers, or unredacted logs in public issues.
- Report suspected vulnerabilities privately to the maintainer. Use GitHub's private vulnerability reporting if available; do not disclose sensitive details in a public issue.
- Dependency versions are pinned in `lg_webos_remote/requirements.txt`; review security updates before increasing versions.

## Dependency advisory

`bscpylgtv==0.5.5` installs `sqlitedict==2.1.0` transitively. [CVE-2024-35515 / GHSA-g4r7-86gm-pgqc](https://github.com/advisories/GHSA-g4r7-86gm-pgqc) concerns pickle deserialization of an attacker-controlled SQLite database. No patched version was listed when v1.0.0 was released.

The Bridge supplies a JSON storage adapter to bscpylgtv and does not open a SQLite pairing database. Keys are written to `/data/webos-client-key.json` with mode `0600` and reused after restart. Do not import untrusted pairing files or Home Assistant backups.

The dependency remains installed, so scanners still report the advisory. The Bridge avoids the affected SQLite/pickle path; the upstream package is not patched. Monitor dependency updates and run the audit without suppressing the finding:

```sh
python -m pip install pip-audit
python -m pip_audit -r lg_webos_remote/requirements.txt
```
