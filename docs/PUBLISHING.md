# Publishing a release

Repository: [sonim1/ha-webos-remote](https://github.com/sonim1/ha-webos-remote).

## Prepare

1. Use the [development setup](../CONTRIBUTING.md#local-setup).
2. Set the same new version in `VERSION`, `package.json` and `lg_webos_remote/config.yaml`.
3. Move the relevant Unreleased changelog entries under that version.
4. Review compatibility notes, license attribution and [dependency advisories](../SECURITY.md#dependency-advisory).

Run:

```sh
npm run build
npm run verify
python3 -m py_compile lg_webos_remote/*.py
git diff --check
```

Stage only public files, inspect the staged changes, and generate the archive:

```sh
git diff --cached --stat
python3 scripts/package.py
```

The ZIP includes tracked Git files. Check that it contains the built card, all Bridge modules, Dockerfile, requirements, installation manifests and license notices. Private configuration, environments, keys, databases and backups must be excluded.

Commit the verified changes and push `main` normally. Wait for source/release checks, artifact upload and HACS validation to pass.

## Tag and publish

Use a new annotated tag matching the version files:

```sh
RELEASE_VERSION=$(cat VERSION)
git tag -a "v$RELEASE_VERSION" -m "LG webOS Remote v$RELEASE_VERSION"
git push origin "v$RELEASE_VERSION"
```

The release workflow checks the tag, builds and verifies the project, validates HACS and publishes the card and ZIP. Tags containing a hyphen produce prereleases; normal version tags produce stable releases. GitHub workflow permissions must allow `contents: write`.

Confirm:

- Both tag workflows succeed.
- The Release has the intended stable/prerelease status.
- `ha-webos-remote.js` and `ha-webos-remote-v<VERSION>.zip` are attached.
- Downloaded assets match the tagged source and ZIP contents.

Use a new version for changes to published code. Do not move a published tag or replace its code assets. Release notes may be corrected separately. Keep Unreleased entries out of a published version's notes.

## HACS requirements

Keep repository Topics such as `home-assistant`, `hacs`, `webos` and `lovelace`. The README must show a remote image. The card filename must remain `ha-webos-remote.js`, and its category is `plugin`, displayed as Dashboard in HACS. See [HACS validation requirements](https://hacs.xyz/docs/publish/include/).

Structural CI checks do not establish compatibility with every TV or application. Record actual device testing and known limits in release notes.
