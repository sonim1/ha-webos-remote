import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';
import assert from 'node:assert/strict';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = name => readFileSync(join(root, name), 'utf8');
assert.ok(existsSync(join(root, 'ha-webos-remote.js')));
assert.equal(read('ha-webos-remote.js'), read('src/lg-webos-remote-card.js'), 'Build output must match source');
const hacs = JSON.parse(read('hacs.json'));
assert.equal(hacs.filename, 'ha-webos-remote.js');
assert.equal(JSON.parse(read('package.json')).license, 'MIT');
const dockerfile = read('lg_webos_remote/Dockerfile');
for (const filename of ['server.py','pairing.py','protocol.py','pointer_session.py','requirements.txt']) {
  assert.ok(existsSync(join(root,'lg_webos_remote',filename)), `${filename} missing`);
  assert.ok(dockerfile.includes(filename), `${filename} missing from Dockerfile`);
}
const js = read('ha-webos-remote.js');
assert.ok(js.includes("customElements.define('lg-webos-remote'"), 'Missing card registration');
execFileSync(process.execPath, ['--check', join(root,'ha-webos-remote.js')], {stdio:'inherit'});
execFileSync(process.execPath, ['--check', join(root,'src/lg-webos-remote-card.js')], {stdio:'inherit'});
console.log('Repository layout and dashboard build verified');
