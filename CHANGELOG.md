# Changelog

## v1.0.0 — Initial public release

- First public MIT-licensed release: LG webOS Remote for Home Assistant.
- Dashboard remote with independent pointer session, click, scroll, Page Up/Down, adjustable sensitivity, D-pad, vertical volume and quick apps.
- Wake-on-LAN power-on and webOS power-off; token-authenticated local Bridge.
- English/Korean Send input and experimental Live mode (some third-party apps do not support text injection).
- GitHub Actions for CI, HACS structure validation and tag-based release ZIP publishing.
- Home Assistant application repository manifests and migration instructions.
- Tested on one LG StanbyME Max 2 with community-maintained software; other models are not guaranteed.

# Changelog

## v0.1.0-alpha.6 — Public repository preparation

- Preserves the v0.1.0-alpha.5 app, pointer and dashboard implementation.
- Adds `repository.yaml` and a root-level `lg_webos_remote/` app folder for Home Assistant app repository discovery.
- Adds GitHub CI, HACS structure validation, tag-based prereleases, issue template and release ZIP tooling.
- Adds clean installation and upgrade guidance and preserves contributor/security notices.
- Does **not** claim that all features have been validated on all LG webOS models.

## v0.1.0-alpha.5 — UI refinements

- Power icon, Settings icon and Quick App alignment refinements.
- Taller touchpad; ×2/×4 cursor controls; Page Up/Down scrolling direction fix.
- Experimental debounced live text synchronization for compatible TV text fields.
- Includes independent pointer session and Docker COPY fix from earlier alpha builds.
