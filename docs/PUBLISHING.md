# Publish LG webOS Remote for Home Assistant

This repository is **https://github.com/sonim1/ha-webos-remote**.

## Verify and push source

On a machine with Node.js 22+, Python 3.13+, git and GitHub access:

```sh
git clone https://github.com/sonim1/ha-webos-remote.git
cd ha-webos-remote
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r lg_webos_remote/requirements.txt pyyaml
npm run build
npm run verify
python3 -m unittest discover -s tests -v
python3 -m py_compile lg_webos_remote/*.py
git status --short
git diff --check
```

For an existing checkout, start from its current state instead of cloning or initializing over it. Inspect changes, stage only public source files, and commit the verified changes on `main`. The ZIP includes tracked Git files only, so stage new public files before packaging:

```sh
git diff --cached --stat
python3 scripts/package.py
git push origin main
```

Inspect the ZIP: it must include `ha-webos-remote/ha-webos-remote.js`, all four Bridge Python modules, `Dockerfile`, `requirements.txt`, manifests and licensing notices. It must exclude `.git`, `.venv`, `.env`, app options, private keys, databases, backups and QA artifacts. Reconcile existing remotes/commits and never force-push. The archive does not contain installed third-party packages; keep their upstream notices when distributing a built app image.

Run a dependency audit and review every finding before tagging; see [the documented sqlitedict advisory and mitigation](../SECURITY.md#known-dependency-advisory). An audit finding must not be described as a clean scan.

## HACS metadata

The repository must have Topics set in GitHub's About panel, for example `home-assistant`, `hacs`, `webos`, and `lovelace`. Its README must embed a UI image; the existing preview uses sample configuration. The JavaScript filename is `ha-webos-remote.js` and the HACS category is `plugin` (shown as Dashboard in HACS). See [HACS validation requirements](https://hacs.xyz/docs/publish/include/).

## Publish v1.0.0

After the `main` branch CI and HACS structure checks pass, create and push an **annotated release tag**:

```sh
git tag -a v1.0.0 -m 'LG webOS Remote for Home Assistant v1.0.0'
git push origin v1.0.0
```

The tag workflow checks the tag against `VERSION`, validates agreement with `package.json` and the app manifest, installs Python dependencies, runs verification and HACS validation, and creates a **non-prerelease** GitHub Release containing `ha-webos-remote.js` and `ha-webos-remote-v1.0.0.zip`. A failure before publication stops the release. Releases require `contents: write`.

After pushing the tag, confirm both tag workflows pass, the Release is public and not a draft/prerelease, and its assets match the tagged sources. Inspect the downloaded ZIP content and compare its JavaScript with the separate card asset. Never replace an existing published tag or Release to hide a failed validation; investigate first and use a new version for subsequent fixes.

## Install

- **HACS Dashboard card:** HACS → Custom repositories → `https://github.com/sonim1/ha-webos-remote` → **Dashboard**. Use `custom:lg-webos-remote` in a dashboard card.
- **TV Bridge app:** Settings → Apps → Install app → add `https://github.com/sonim1/ha-webos-remote` as a custom app repository → install **LG webOS Remote Bridge**.
- Set TV IP, Wi-Fi MAC, port, and random authentication token. Use the token in the dashboard card. Keep the token secret and port 8788 within a trusted LAN.
- **Existing local Alpha 5 installation:** see [Upgrade guide](UPGRADE_FROM_ALPHA5.md) before replacing the old local app or deleting data.

This project is unaffiliated with LG Electronics or Home Assistant. It has not been accepted to the official HACS catalog and not all TV/app combinations have been tested.

CI/HACS structural validation is not a fresh-install or hardware test. Fresh HACS installation, HAOS app installation on Raspberry Pi 5, and long-running pointer/application compatibility require device verification. Preserve this distinction in release notes.
