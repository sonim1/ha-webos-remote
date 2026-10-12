# Updating LG webOS Remote

The Bridge app and Dashboard card update separately. Back up Home Assistant before changing either component.

## Bridge app

1. Open **Settings → Apps → LG webOS Remote Bridge**.
2. Install the available update and start the app.
3. Check its log and confirm the dashboard reconnects.

Keep the app configuration and data volume. The pairing key is stored at `/data/webos-client-key.json`; an in-place update should reuse it. If the key is missing or the TV revoked it, turn on the TV and approve pairing again.

## Dashboard card

1. Open the project in HACS and download the desired release.
2. Reload the browser or Home Assistant Companion app.
3. Check the resource points to `/hacsfiles/ha-webos-remote/ha-webos-remote.js` and is registered once.

Keep the existing card YAML, Bridge URL and token unless you intentionally change the Bridge settings.

## Changing installation sources

A manually installed Bridge and a repository-installed Bridge can have separate app identities and data. Stop the existing Bridge before starting another on the same port. Keep its backup and data until the replacement works; a new installation may require TV pairing.

For manual installations, back up the source and card files, replace them with files from the chosen public release, and rebuild the Bridge image. Restarting alone does not rebuild changed source.

## Rollback

If an update fails, restore the Home Assistant backup. For the card, HACS also lets you select an available earlier release and reload the dashboard. Manual installations can restore their backed-up files and rebuild. Keep private configuration and pairing data out of public support requests.
