import { copyFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
copyFileSync(path.join(root,'src','lg-webos-remote-card.js'), path.join(root,'ha-webos-remote.js'));
console.log('LG webOS Remote for Home Assistant built: ha-webos-remote.js (no NPM dependencies)');
