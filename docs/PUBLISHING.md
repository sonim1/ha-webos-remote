# Publish LG webOS Remote for Home Assistant

This repository is **https://github.com/sonim1/ha-webos-remote**.

## Verify and push source

On a machine with Node.js 22+, Python 3.13+, git and GitHub access:

```sh
npm run build
npm run verify
python3 -m py_compile lg_webos_remote/*.py
python3 scripts/package.py

git init
git branch -M main
git add .
git commit -m 'Release LG webOS Remote for Home Assistant v1.0.0'
git remote add origin https://github.com/sonim1/ha-webos-remote.git
git push -u origin main
```

If the repository already has a remote or commits, reconcile first rather than force-pushing. Do not upload pairing keys, tokens, real TV IP/MAC or Home Assistant backups. The package contains none of these.

## Publish v1.0.0

After the `main` branch CI and HACS structure checks pass, create and push an **annotated release tag**:

```sh
git tag -a v1.0.0 -m 'LG webOS Remote for Home Assistant v1.0.0'
git push origin v1.0.0
```

The tag workflow verifies `VERSION`, runs checks, and creates a **non-prerelease** GitHub Release containing the JavaScript dashboard card and a ZIP. Check the GitHub Actions tab for workflow permissions; releases require `contents: write`.

## Install

- **HACS Dashboard card:** HACS → Custom repositories → `https://github.com/sonim1/ha-webos-remote` → **Dashboard**. Use `custom:lg-webos-remote` in a dashboard card.
- **TV Bridge app:** Settings → Apps → Install app → add `https://github.com/sonim1/ha-webos-remote` as a custom app repository → install **LG webOS Remote Bridge**.
- Set TV IP, Wi-Fi MAC, port, and random authentication token. Use the token in the dashboard card. Keep the token secret and port 8788 within a trusted LAN.
- **Existing local Alpha 5 installation:** see [Upgrade guide](UPGRADE_FROM_ALPHA5.md) before replacing the old local app or deleting data.

This project is unaffiliated with LG Electronics or Home Assistant. It has not been accepted to the official HACS catalog and not all TV/app combinations have been tested.
