# LG webOS Remote Bridge

The Bridge connects an LG webOS TV to the LG webOS Remote Dashboard card. Install the card separately through HACS using `https://github.com/sonim1/ha-webos-remote` with category **Dashboard**.

Compatible LG OLED, QNED, NanoCell, UHD and StanbyME webOS TVs are intended targets. The Bridge requires the TV's local control API over secure WebSocket port 3001. LG StanbyME Max 2 is the project-tested device; other models and individual features require validation. See [device compatibility](https://github.com/sonim1/ha-webos-remote/blob/main/docs/COMPATIBILITY.md).

## Configuration

```yaml
tv_ip: "YOUR_TV_IP"
mac_address: "YOUR_TV_NETWORK_MAC"
listen_port: 8788
broadcast_address: "255.255.255.255"
auth_token: "YOUR_RANDOM_TOKEN"
```

- `tv_ip`: the TV's IP on your local network.
- `mac_address`: the MAC of the TV's active Ethernet or Wi-Fi interface for Wake-on-LAN. Wireless wake support varies by model; enable the TV's network wake setting where available.
- `listen_port`: the port the Dashboard card connects to.
- `broadcast_address`: keep the default unless your network requires another address.
- `auth_token`: a random secret of at least 40 characters; use the same value in the card.

Save the configuration and select **Start**. Turn on the TV and approve pairing if prompted. The Bridge saves the TV-issued key privately at `/data/webos-client-key.json` and reuses it after restart.

## Dashboard card

```yaml
type: custom:lg-webos-remote
name: Living Room TV
url: ws://YOUR_HOME_ASSISTANT_IP:8788
token: "YOUR_RANDOM_TOKEN"
sensitivity: 1
scrollSensitivity: 1
```

The URL uses the **Home Assistant IP**, not the TV IP. Replace the placeholders with your own values.

## Connection checks

- **Connection error / Disconnected:** start the Bridge and check its log for `LG webOS Remote listening on port 8788`. Confirm the card URL and port.
- **Invalid token:** match the card token to `auth_token`.
- **TV Off · Wake ready:** the Bridge is connected; use Power to wake the TV.
- **Pairing unavailable:** turn on the TV, check its IP and approve the Allow prompt.

Preserve app configuration and data during updates. Use a trusted local network; plain `ws://` is unencrypted. HTTPS dashboards may require a WSS proxy. Do not expose the Bridge directly to the internet or share tokens/pairing keys.

See the [installation guide](https://github.com/sonim1/ha-webos-remote#installation) and [update instructions](https://github.com/sonim1/ha-webos-remote/blob/main/docs/UPDATING.md).
