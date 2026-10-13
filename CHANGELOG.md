# Changelog

## v1.0.1

- Increased the touchpad minimum height from 178px to 196px.
- Doubled Page Up/Down scroll amounts while preserving direction and repeat timing.
- Added an authenticated Bridge regression test for both native page-scroll packets.
- Added a copyable AI-agent installation prompt and clearer prerequisites, setup checkpoints and first-use verification.
- Refreshed the remote screenshot, setup examples, troubleshooting and update documentation.
- Added Bridge configuration help for the Home Assistant app's Documentation tab.
- Documented intended LG webOS TV families, tested hardware, transport requirements and model-dependent features; generalized setup examples and Wake-on-LAN MAC guidance.

## v1.0.0

- Initial MIT-licensed LG webOS Remote for Home Assistant.
- Magic Touchpad with an independent persistent pointer session, click, scroll, Page Up/Down and adjustable sensitivity.
- Navigation, volume, mute and installed-app shortcuts for Netflix, Internet, YouTube and Gallery+.
- Wake-on-LAN power-on and webOS power-off.
- English/Korean text input with Enter/Send and experimental Live mode.
- Token-authenticated Bridge with private JSON pairing storage and sanitized diagnostics.
- HACS Dashboard card and Home Assistant app repository installation.
- Automated source, protocol, packaging and HACS checks; GitHub Releases include the card and installation ZIP.

Tested during development on an LG StanbyME Max 2. App and model compatibility varies; see [README.md](README.md#compatibility) and [SECURITY.md](SECURITY.md).
