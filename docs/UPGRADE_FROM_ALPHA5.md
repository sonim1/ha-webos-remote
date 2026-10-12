# Upgrade a local Alpha 5 installation to v1.0.0

**Important:** First back up Home Assistant and stop the installed `LG webOS Remote Bridge`. Do not remove its app or data. Your existing authentication token and TV pairing credentials live outside these source files and should be preserved.

1. Upload the v1.0.0 ZIP into Home Assistant `/config` and extract it to `/config/ha-webos-v100`:

```sh
python3 -m zipfile -e /config/ha-webos-remote-v1.0.0.zip /config/ha-webos-v100
```

2. On the Home Assistant Terminal & SSH app, back up the **existing local app code**, copy the new code and rebuild the app container:

```sh
set -e
STAMP=$(date +%Y%m%d%H%M%S)
cp -a /local_apps/lg_webos_remote "/config/lg_webos_remote_backup_$STAMP"
cp -a /config/ha-webos-v100/ha-webos-remote/lg_webos_remote/. /local_apps/lg_webos_remote/
```

3. From Settings → Apps → LG webOS Remote Bridge: **Rebuild**, then **Start**. The app reports version `1.0.0` and should reuse your existing configuration and private pairing key.

The private JSON key at `/data/webos-client-key.json` keeps its format and path. v1.0.0 uses this file for the library's storage as well; it does not read, import, or delete an old `pairing.sqlite`. Keep the app data volume and existing options. If the JSON key is missing, the TV must approve a new pairing; do not copy credentials from an unrelated Bridge.

4. Back up and update the dashboard JavaScript:

```sh
STAMP=$(date +%Y%m%d%H%M%S)
cp /config/www/ha-webos-remote/ha-webos-remote.js "/config/ha-webos-remote-ui-backup-$STAMP.js"
cp /config/ha-webos-v100/ha-webos-remote/ha-webos-remote.js /config/www/ha-webos-remote/ha-webos-remote.js
```

5. In Home Assistant → Settings → Dashboards → Resources, update **only** the Remote resource to `/local/ha-webos-remote/ha-webos-remote.js?v=100` (JavaScript module); hard-refresh the dashboard.
6. Confirm pairing, mouse cursor, clicks, directional/volume keys, app shortcuts, power-on/off and optional Live typing. TV model compatibility remains unverified outside devices actually tested.

**Never** paste your token or pairing key into a support issue.

If the update fails, stop the Bridge, restore the backed-up source files to the same local app directory, rebuild, and start it. Restore the backed-up dashboard JavaScript and refresh its resource. Preserve app options and `/data` throughout rollback. Installing from the GitHub app repository may create a separate app identity; do not uninstall the local app until you have verified the new installation and a backup.
