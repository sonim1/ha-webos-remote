# LG webOS Remote for Home Assistant

A dashboard remote for LG webOS TVs with a Magic Touchpad, app shortcuts, English/Korean text input, and Wake-on-LAN.

Designed for compatible **LG OLED, QNED, NanoCell, UHD and StanbyME webOS TVs**. See [device compatibility](docs/COMPATIBILITY.md) for requirements and tested hardware.

**Current release: [v1.0.0](https://github.com/sonim1/ha-webos-remote/releases/tag/v1.0.0)** · **License: [MIT](LICENSE)**

## Remote preview

<p align="center">
  <img src="docs/remote-preview.png" alt="LG webOS remote with app shortcuts, Magic Touchpad, navigation, volume and text input" width="360">
</p>

The keyboard panel is expanded in this preview. Toggle it with the Keyboard button. The TV name is configurable; the model shown is an example.

## Features

- **Magic Touchpad:** relative pointer movement, click, mouse wheel, two-finger scroll, Page Up/Down, and 1x/2x/4x sensitivity.
- **Remote controls:** Back, Home, Settings, D-pad, OK, volume and mute.
- **Quick Apps:** Netflix, Internet, YouTube and Gallery+, resolved from the TV's installed apps.
- **Text input:** send English or Korean text with Enter or Send; optional Live mode is experimental.
- **Power:** Wake-on-LAN when the TV is off and webOS power-off when it is on.

## Installation

Install both parts: the **Bridge app** connects to the TV, and the **HACS Dashboard card** connects to the Bridge. Home Assistant OS is supported on aarch64 and amd64, including Raspberry Pi 5.

Use this repository URL for both installations:

```text
https://github.com/sonim1/ha-webos-remote
```

### 1. Install the Bridge app

1. Open **Settings → Apps → Install app**. Older Home Assistant versions call this **Add-ons**.
2. Select **⋮ → Repositories**, add the URL above, and install **LG webOS Remote Bridge**.
3. Open **Configuration**, enter your TV settings, and save:

```yaml
tv_ip: "YOUR_TV_IP"
mac_address: "YOUR_TV_NETWORK_MAC"
listen_port: 8788
broadcast_address: "255.255.255.255"
auth_token: "YOUR_RANDOM_TOKEN"
```

Use a random token of at least 40 characters. Generate one on a computer with Python:

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

4. Turn on the TV and select **Start** in the Bridge app. Approve the TV's pairing prompt if shown.
5. Check the app log for `LG webOS Remote listening on port 8788`. Pairing is stored privately and reused after restarts.

Use the MAC of the TV's active network interface (Ethernet or Wi-Fi) for Wake-on-LAN. Wireless wake support varies by model; enable the TV's network wake setting where available. Keep the default broadcast address unless your network requires another value. See [power-on compatibility](docs/COMPATIBILITY.md#power-on) and [Home Assistant repository installation](https://www.home-assistant.io/common-tasks/os/#installing-a-third-party-app-repository).

### 2. Install the Dashboard card

1. Open **HACS → ⋮ → Custom repositories**.
2. Add the same repository URL and select **Dashboard**.
3. Find **LG webOS Remote for Home Assistant**, download **v1.0.0**, and reload the browser.

This project is installed as a custom repository; it is not in the HACS default catalog. See [HACS custom repositories](https://www.hacs.dev/docs/faq/custom_repositories/).

If HACS does not add the resource automatically, open **Settings → Dashboards → Resources** and add:

```text
/hacsfiles/ha-webos-remote/ha-webos-remote.js
```

Select **JavaScript module**. Register the card resource once.

### 3. Add the remote to your dashboard

Open your dashboard, select **Edit → Add card → Manual**, and paste:

```yaml
type: custom:lg-webos-remote
name: Living Room TV
url: ws://YOUR_HOME_ASSISTANT_IP:8788
token: "YOUR_RANDOM_TOKEN"
sensitivity: 1
scrollSensitivity: 1
```

**The card URL uses the Home Assistant IP, not the TV IP.** Its token must match the Bridge's `auth_token`. Replace every placeholder before saving. This release uses the YAML editor; a visual configuration editor is planned.

| Card option | Description | Default |
| --- | --- | --- |
| `name` | Display name | `LG webOS TV` |
| `url` | Bridge WebSocket URL | Required |
| `token` | Same secret as the Bridge's `auth_token` | Required |
| `sensitivity` | Pointer movement scale; the 2x/4x buttons multiply it | `1` |
| `scrollSensitivity` | Desktop mouse-wheel scale | `1` |

Once connected, the card shows **TV On** or **TV Off · Wake ready**. Power can wake an offline TV without an active TV connection.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| **Connection error / Disconnected** | Start the Bridge app, check its log, and confirm the card URL uses the Home Assistant IP and configured port. |
| **Invalid token** | Use the same token in the Bridge and card. The Bridge requires at least 40 characters. |
| **TV offline** | Check the TV IP and network connectivity. Use Power to wake it; confirm the active interface's MAC and TV remote power-on settings. |
| **Pairing prompt** | Keep the TV awake and approve Allow. Preserve the app's data when updating. |
| **Text does not appear** | Focus a compatible text field on the TV. Netflix and YouTube may not accept external text input. |
| **HTTPS dashboard cannot connect** | Browsers can block plain `ws://` from HTTPS pages. Use a trusted WSS proxy. |
| **Card still shows an older layout** | Reload the browser and check that only the current HACS resource is registered. |

## Compatibility

This remote is not exclusive to StanbyME. It uses the LG webOS local control protocol without a model whitelist.

| Device family | Project compatibility status |
| --- | --- |
| **LG StanbyME Max 2** | Tested during development: pairing, full-screen pointer movement, click, power-on/off and English/Korean input in the TV browser. |
| **LG OLED, QNED, NanoCell and UHD webOS TVs** | Intended targets when they provide the required local control API and secure WebSocket port 3001. Individual models have not yet been tested by this project. |
| **Other StanbyME models and other webOS displays** | Not yet verified; the webOS name alone does not establish compatibility. |
| **LG NetCast TVs and non-webOS TVs** | Outside the supported platform. |

**All models and all features are not guaranteed.** This Bridge requires `wss://TV:3001`; TVs offering only plain WebSocket port 3000 cannot connect to v1.0.0. Pointer/scroll behavior, installed apps, text input and network wake can vary by model, firmware and app. See the [compatibility guide and sources](docs/COMPATIBILITY.md).

Live input is a beta feature. Long-running pointer stability, reconnection after network interruptions, and broader TV compatibility remain on the [roadmap](docs/ROADMAP.md).

Use the Bridge on a trusted local network. Plain `ws://` is unencrypted; keep tokens private and do not expose port 8788 to the internet. See [SECURITY.md](SECURITY.md), including the documented dependency advisory.

## Updates and development

- [Updating and rollback](docs/UPDATING.md)
- [Contributing and local development](CONTRIBUTING.md)
- [Release workflow](docs/PUBLISHING.md)
- [Changelog](CHANGELOG.md)

## License

This independently implemented project is MIT-licensed. Third-party dependencies and attribution are listed in [NOTICE.md](NOTICE.md). It does not include source from the CC BY-NC-ND Lovelace Touchpad Card project.

Community project, unaffiliated with LG Electronics or Home Assistant.
