# LG webOS Remote for Home Assistant roadmap

## v1.0.0 — first public release
- [x] Independently written JavaScript dashboard card and Python Bridge under MIT
- [x] Token-protected WebSocket; separate persistent pointer connection
- [x] Magic cursor, clicks, wheel, two-finger scroll, Page Up/Down, ×2/×4 sensitivity
- [x] Power-on via Wake-on-LAN and power-off via webOS (validated on one StanbyME)
- [x] Netflix, Internet, YouTube and Gallery+ app discovery shortcuts
- [x] One-line Send/Enter and optional experimental Live input
- [x] Source tests, GitHub Actions, HACS-compatible custom card and app repository layout
- [x] Real loopback WebSocket authentication/validation tests, private JSON storage, and release ZIP exclusion tests
- [ ] Fresh HACS and Home Assistant OS app installation on Raspberry Pi 5
- [ ] Long-running pointer stability and reconnection after standby or Wi-Fi interruption
- [ ] Upstream removal or patch of the unused sqlitedict dependency advisory (see SECURITY.md)
- [ ] Confirm keyboard support in Netflix and YouTube (known limitation)
- [ ] Multi-device compatibility and broader webOS model validation
- [ ] HACS default catalog acceptance (custom repository works independently)
- [ ] Independent security and license review

## Future releases
- [ ] Visual configuration editor and automatic TV discovery
- [ ] Device status, volume indicator and pairing diagnostics
- [ ] WSS proxy guidance, scoped per-device tokens, rate limiting
- [ ] Keyboard application compatibility improvements
- [ ] Internationalization and accessibility testing
- [ ] Integration tests with simulated webOS protocol and multiple TVs
