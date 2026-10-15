import { copyFile, mkdir, readFile, rm } from 'node:fs/promises';

const root = new URL('./', import.meta.url);
const output = new URL('./dist/', root);
const html = await readFile(new URL('index.html', root), 'utf8');
if (!html.includes('src="../docs/remote-preview.png"')) {
  throw new Error('Update the website build when changing the remote preview asset path.');
}

await rm(output, { recursive: true, force: true });
await mkdir(new URL('docs/', output), { recursive: true });
await mkdir(new URL('assets/', output), { recursive: true });
await copyFile(new URL('index.html', root), new URL('index.html', output));
await copyFile(new URL('../docs/remote-preview.png', root), new URL('docs/remote-preview.png', output));
await copyFile(new URL('_headers', root), new URL('_headers', output));
await copyFile(new URL('robots.txt', root), new URL('robots.txt', output));
await copyFile(new URL('sitemap.xml', root), new URL('sitemap.xml', output));
await copyFile(new URL('assets/home-assistant.svg', root), new URL('assets/home-assistant.svg', output));
console.log('Built landing page and public remote preview in website/dist.');
