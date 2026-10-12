# LG webOS Remote Bridge

The Bridge connects an LG webOS TV to the LG webOS Remote Dashboard card. Install the card separately through HACS using `https://github.com/sonim1/ha-webos-remote` with category **Dashboard**.

## Configuration

```yaml
tv_ip: "YOUR_TV_IP"
mac_address: "YOUR_TV_WIFI_MAC"
listen_port: 8788
broadcast_address: "255.255.255.255"
auth_token: "YOUR_RANDOM_TOKEN"
```

- `tv_ip`: the TV's IP on your local network.
- `mac_address`: the TV's Wi-Fi MAC for Wake-on-LAN.
- `listen_port`: the port the Dashboard card connects to.
- `broadcast_address`: keep the default unless your network requires another address.
- `auth_token`: a random secret of at least 40 characters; use the same value in the card.

Save the configuration and select **Start**. Turn on the TV and approve pairing if prompted. The Bridge saves the TV-issued key privately at `/data/webos-client-key.json` and reuses it after restart.

## Dashboard card

```yaml
type: custom:lg-webos-remote
name: LG StanbyME Max 2
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
