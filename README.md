# LG webOS Remote for Home Assistant

A dashboard remote for LG webOS TVs with a Magic Touchpad, app shortcuts, English/Korean text input, and Wake-on-LAN.

Designed for compatible **LG OLED, QNED, NanoCell, UHD and StanbyME webOS TVs**. See [device compatibility](docs/COMPATIBILITY.md) for requirements and tested hardware.

**Current release: [v1.0.0](https://github.com/sonim1/ha-webos-remote/releases/tag/v1.0.0)** · **License: [MIT](LICENSE)**

## Install with an AI agent

Copy this prompt into your AI assistant or coding agent. An agent with access to your Home Assistant can help perform the setup; otherwise, it can guide you through the same steps. Follow the [manual installation guide](#installation) below if you prefer.

<details>
<summary><strong>Show the installation prompt</strong></summary>

```text
Help me install LG webOS Remote for Home Assistant from:
https://github.com/sonim1/ha-webos-remote

Read its current README, docs/COMPATIBILITY.md, docs/UPDATING.md and
SECURITY.md before making changes. Use the published stable release.

1. Inspect my existing setup first: Home Assistant installation type,
   CPU architecture, HACS configuration, existing Bridge/card installs,
   and whether the dashboard uses HTTP or HTTPS. This repository's app
   installation requires Home Assistant OS on aarch64 or amd64.
2. Check the TV model, network connection and local control requirements.
   Ask only for missing setup information. The Bridge needs the TV's IP;
   the card needs the Home Assistant host reachable from my browser.
3. Install both components: LG webOS Remote Bridge via the Home Assistant
   app repository, and the Dashboard card via HACS custom repositories
   (category Dashboard). Both use the repository URL above. If HACS is
   absent, guide me through its official installation and configuration.
4. Configure the Bridge using tv_ip, mac_address, listen_port (8788),
   broadcast_address and auth_token. Use the active TV network interface's
   MAC and generate a random token locally with at least 40 characters.
   Set the same token in the card. Keep private values out of chat, logs,
   screenshots and commits; use placeholders in shared examples.
5. Have me turn on the TV and approve pairing. Start the Bridge, check its
   log, and enable Start on boot. Register the card's JavaScript module
   once, then add custom:lg-webos-remote to my dashboard with the documented
   YAML keys. For HTTPS, use an existing trusted WSS route if available;
   explain any remaining connection requirement before proceeding.
6. Verify the card shows TV On and test Home, volume and pointer movement
   in the TV browser. Then test power-off and Wake-on-LAN separately.
   Report each result as observed, failed or untested. Do not assume every
   TV app accepts pointer or text input.

Preserve existing configuration and pairing data. Back up before replacing
an installation; ask before removing an existing Bridge or changing shared
network settings. Do not run two Bridges on the same port or expose the
Bridge to the public internet. No Home Assistant API token is needed by
the Bridge. If you lack access to perform a step, give me the exact UI
instructions and verify my result instead of claiming it was completed.
```

</details>

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

### Before you start

- Use a Home Assistant administrator account. The app repository instructions below require **Home Assistant OS**; Home Assistant Container/Core has no app store.
- Install and configure **HACS** first if it is not already in your sidebar. Follow the [official download guide](https://www.hacs.dev/docs/use/download/download/), then [initial configuration](https://www.hacs.dev/docs/use/configuration/basic/), including restarting Home Assistant and authorizing HACS with your GitHub account.
- Keep the TV, Home Assistant and the device displaying the dashboard on a network where they can reach each other. Turn on the TV for pairing and check the [device requirements](docs/COMPATIBILITY.md#connection-requirements).
- Find the **TV IP and active interface's MAC** in the TV's network information or your router's device list. Find the **Home Assistant local IP/hostname** in the router or the address used to open its dashboard locally; a remote/cloud dashboard URL is not the Bridge address. A DHCP reservation can keep these addresses stable.
- If you already have a Bridge or manual card installation, follow [updating or changing installation sources](docs/UPDATING.md) first. Avoid duplicate card resources or two Bridges using the same port.
- If your dashboard uses **HTTPS**, plan a trusted WSS proxy route for the card. An HTTPS browser session can block the default plain WebSocket connection; see [SECURITY.md](SECURITY.md).

Use this repository URL for both installations:

```text
https://github.com/sonim1/ha-webos-remote
```

### 1. Install the Bridge app

1. Open **Settings → Apps → Install app**. Older Home Assistant versions call this **Add-ons**.
2. Select **⋮ → Repositories**, add the URL above, and select **Add**. Close the dialog, locate **LG webOS Remote Bridge** in the new repository section, and select **Install**. Refresh the app store if the repository does not appear immediately.
3. Open the app's **Configuration** tab. Fill in the fields, or use the YAML editor if available, and save:

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

Replace every `YOUR_...` value. Keep the generated token private and copy the same value into the card configuration later. It is a new Bridge token, not a Home Assistant access token or TV pairing key.

4. Turn on the TV and select **Start** in the Bridge app. Approve the TV's pairing prompt if shown.
5. Open the **Log** tab. `LG webOS Remote listening on port 8788` means the Bridge server is running; `TV paired/connected` confirms the TV connection. Pairing is stored privately and reused after restarts.
6. Enable **Start on boot** on the app's **Info** tab so the Bridge starts after Home Assistant restarts.

Use the MAC of the TV's active network interface (Ethernet or Wi-Fi) for Wake-on-LAN. Wireless wake support varies by model; enable the TV's network wake setting where available. Keep the default broadcast address unless your network requires another value. See [power-on compatibility](docs/COMPATIBILITY.md#power-on) and [Home Assistant repository installation](https://www.home-assistant.io/common-tasks/os/#installing-a-third-party-app-repository).

### 2. Install the Dashboard card

1. Open **HACS → ⋮ → Custom repositories**.
2. Add the same repository URL, select **Dashboard**, and select **Add**.
3. Search HACS for **LG webOS Remote for Home Assistant**, open it, select **Download**, choose **v1.0.0**, and confirm the download. Reload the browser when prompted.

This project is installed as a custom repository; it is not in the HACS default catalog. See [HACS custom repositories](https://www.hacs.dev/docs/faq/custom_repositories/).

If HACS does not add the resource automatically, open **Settings → Dashboards → Resources** and add:

```text
/hacsfiles/ha-webos-remote/ha-webos-remote.js
```

Select **JavaScript module**. Register the card resource once.

If the resource menu is hidden, enable **Advanced mode** in your Home Assistant user profile. If the dashboard uses YAML-managed resources, add the same URL with `type: module` in that resource configuration instead. See [Home Assistant resource registration](https://developers.home-assistant.io/docs/frontend/custom-ui/registering-resources/).

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

Use the Home Assistant host with the Bridge port, for example `ws://YOUR_HOME_ASSISTANT_IP:8788`; do not include the dashboard path or its usual port 8123. With a WSS proxy, use that proxy's configured `wss://` URL instead. Select **Save**, then finish dashboard editing. The editor's "Visual editor not supported" message is expected for this card.

| Card option | Description | Default |
| --- | --- | --- |
| `name` | Display name | `LG webOS TV` |
| `url` | Bridge WebSocket URL | Required |
| `token` | Same secret as the Bridge's `auth_token` | Required |
| `sensitivity` | Pointer movement scale; the 2x/4x buttons multiply it | `1` |
| `scrollSensitivity` | Desktop mouse-wheel scale | `1` |

Once connected, the card shows **TV On** or **TV Off · Wake ready**. Power can wake an offline TV without an active TV connection.

### 4. Check the installation

1. With the TV on, confirm the card shows **TV On**. Test Home and volume, then open the TV browser and test pointer movement and click.
2. Test Power to turn the TV off, then wait for **TV Off · Wake ready** and test Power again to wake it. If waking fails, check the MAC and the TV's network wake setting in the [compatibility guide](docs/COMPATIBILITY.md#power-on).
3. Reload the dashboard and confirm it reconnects. You can test text input by focusing a browser text field on the TV and sending a short message.

**TV Off · Wake ready** means the card can reach the Bridge and offer a wake action; it does not prove the TV will accept Wake-on-LAN. **Disconnected / Connection error** means the card cannot establish its Bridge connection, even if the TV is off. Use the checks below to find the failing connection.

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
