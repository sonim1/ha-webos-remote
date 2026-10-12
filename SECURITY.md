# Security policy

**Community-maintained software.** No third-party audit has been performed; use on a trusted local network only.

- The app binds to `0.0.0.0:8788` by default and authenticates incoming WebSocket connections with a random 40+ character token. **It does not encrypt `ws://` traffic.**
- Never forward port 8788 to the internet; use network controls and TLS termination if providing remote access.
- Home Assistant card configuration contains a secret token. Keep backups and screenshots private. Pairing credentials are stored in the app's data volume, not in GitHub.
- Do not report secrets, device identifiers, or unredacted logs in public issues.
- If you believe you found a vulnerability, use the GitHub private security advisory feature once the public repository is configured. Otherwise, contact the repository maintainer privately.
- Dependency versions are pinned in `lg_webos_remote/requirements.txt`; review security updates before increasing versions.

This repository does not include the CC BY-NC-ND-licensed Lovelace Touchpad Card or Pointer Bridge implementation; see NOTICE.md.
