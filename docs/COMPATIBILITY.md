# Device compatibility

LG webOS Remote is designed for LG webOS TVs, not only the StanbyME Max 2. The Bridge uses LG's local SSAP/WebSocket control protocol and has no model whitelist. Compatibility depends on the TV's local API, firmware and individual features.

## Device families

| Device family | Status in this project |
| --- | --- |
| LG StanbyME Max 2 | Tested during development: pairing, full-screen pointer movement, click, Wake-on-LAN, power-off and English/Korean text insertion in the browser. |
| LG OLED webOS TVs | Intended targets subject to the requirements below; no individual model has been tested by this project. |
| LG QNED webOS TVs | Intended targets subject to the requirements below; no individual model has been tested by this project. |
| LG NanoCell webOS TVs | Intended targets subject to the requirements below; no individual model has been tested by this project. |
| LG UHD webOS TVs | Intended targets subject to the requirements below; no individual model has been tested by this project. |
| Other StanbyME models, projectors, smart monitors, commercial displays and third-party webOS Hub TVs | Unverified. Sharing the webOS name does not prove that the required TV control API is available. |
| LG NetCast TVs and non-webOS TVs | Outside this project's supported platform. |

LG identifies OLED, QNED, NanoCell and UHD as webOS TV families in its [webOS 6.0 announcement](https://www.lg.com/us/press-release/CES%202021-LG-webOS-6.0-FINAL.pdf). This establishes the platform, not successful tests of this remote on every model.

## Connection requirements

- The TV must expose the LG webOS local control API and accept pairing.
- The Bridge uses **secure WebSocket port 3001** for pairing and control. There is no fallback to plain WebSocket port 3000. A TV that only offers port 3000 cannot connect to this release.
- The Bridge must reach the TV on the local network. Turn the TV on for initial pairing and approve its permission prompt. Enable **LG Connect Apps** where that setting exists.
- The Dashboard card connects to the Bridge on port 8788 by default. This is separate from the TV's port 3001.

The [Home Assistant webOS integration](https://www.home-assistant.io/integrations/webostv/#supported-devices) lists webOS 2.0 and newer as its supported platform. That is a useful starting point for investigating a TV, **not this project's minimum-version guarantee**: the secure transport and feature requirements above still apply. This Bridge connects directly to the TV; installing that integration is not required.

The upstream [bscpylgtv library](https://github.com/chros73/bscpylgtv#bscpylgtv) targets webOS-based LG TVs. Upstream capability and successful Home Assistant integration pairing do not establish full compatibility with this project's separate pointer session.

## Feature differences

| Feature | What to verify on another TV |
| --- | --- |
| Navigation, volume and power-off | Pairing succeeds and the TV accepts the corresponding commands. |
| Magic Touchpad and click | The TV provides a pointer input socket; test movement across the entire screen in a pointer-enabled app such as the browser. Some apps use directional navigation only. |
| Wheel, two-finger scroll and Page Up/Down | Test direction and behavior in each app. The current Page Up/Down mapping was selected for the StanbyME test device. |
| Netflix, Internet, YouTube and Gallery+ | The application must be installed and launchable on that model and in its region. Shortcuts resolve against the TV's installed apps; Gallery+ is not available everywhere. |
| English/Korean text and Live mode | Focus a text field that accepts the webOS IME service. Browser input was tested; Netflix and YouTube may use custom input interfaces. Live mode is experimental. |
| Reconnection and long sessions | Test standby, network interruption and extended pointer use; automated tests do not replace hardware validation. |

## Power-on

The Bridge sends a Wake-on-LAN magic packet without requiring an active TV connection. Use the MAC address of the TV's active network interface; Ethernet and Wi-Fi interfaces can have different addresses.

Wi-Fi wake was confirmed on the StanbyME Max 2. Other TVs may require Ethernet or a different network wake setting. The TV must remain powered and able to receive the packet in standby. Keep the Bridge and TV on the same subnet unless your network is configured to forward broadcasts.

LG documents **TV On With Mobile / Turn On via Wi-Fi** in its [ThinQ setup guide](https://www.lg.com/us/support/help-library/lg-tv-how-to-set-up-the-lg-thinq-app-on-your-lg-smart-tv--20152745625356). Its ThinQ power-on support statement is not a guarantee that every model accepts this Bridge's Wake-on-LAN packets; this Bridge does not use Bluetooth or the ThinQ cloud.

Home Assistant's [power-on guidance](https://www.home-assistant.io/integrations/webostv/#turning-on-the-tv-from-home-assistant) describes Ethernet Wake-on-LAN and model-dependent settings. Its [wake troubleshooting](https://www.home-assistant.io/integrations/webostv/#wakeonlan-does-not-work) also notes that some 2025+ models require **Settings → Support → IP control settings → Wake on LAN**. Menu names differ by firmware and region; check the TV's own help if a listed setting is absent.

## Reporting device results

Use the [bug report form](https://github.com/sonim1/ha-webos-remote/issues/new?template=bug_report.yml) for failures. For a successful compatibility report, open an issue with:

- Full TV model, webOS version, firmware version and project version.
- Ethernet or Wi-Fi connection and the relevant network wake setting.
- Separate results for pairing, navigation, volume, full-screen pointer movement, click, scrolling/Page Up/Down, wake, power-off, app shortcuts and text input.
- App names used for pointer, scroll and English/Korean text tests; mark untested features explicitly.
- Whether pairing is reused after a Bridge restart, and the duration of any long-running test.

Remove IP/MAC addresses, tokens, pairing keys and other private data from reports, logs and screenshots. Only actual results can move a device from an intended target to project-tested hardware.

Sources reviewed on 2026-10-12. See the [README](../README.md#compatibility) for the short compatibility summary.
