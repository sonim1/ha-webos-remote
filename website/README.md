# Project website

A static, English-language introduction and installation guide for LG webOS Remote for Home Assistant, published at <https://webos.royjen.com/>. It reuses the public remote screenshot and current v1.0.1 instructions.

## Local preview

From the repository root, run:

```sh
python3 -m http.server 8899 --bind 127.0.0.1
```

Open <http://127.0.0.1:8899/website/>. Keep the server running while previewing. The page follows the system theme; add `?theme=light` or `?theme=dark` to preview either appearance.

The HTML includes its CSS and JavaScript, with no browser dependencies, remote fonts or analytics. The image is referenced from `../docs/remote-preview.png`; the deployment build copies it into `dist/docs/remote-preview.png`. Copy buttons require clipboard permission; when unavailable, the text is selected for manual copying.

The remote image is a static preview. This page does not connect to Home Assistant or a TV, store credentials, or perform installations. Links and examples guide users through the Bridge app and HACS card installations separately. See [DESIGN.md](DESIGN.md) for the page's design contract.

## Cloudflare deployment

The site uses Workers Static Assets through the Cloudflare CLI (`cf`). `cloudflare.config.ts` keeps the `ha-webos-remote-site` Worker, custom domain `webos.royjen.com`, compatibility date, observability and routing settings. `wrangler.config.ts` supplies only the static asset directory (`./dist`) to the existing Wrangler build implementation, which `cf` invokes internally. Cloudflare manages the domain's DNS record and HTTPS certificate. The site's dependencies are isolated from the Home Assistant card and Bridge build.

Use Node.js 22.18 or later. Volta users automatically use the version pinned in this directory's `package.json`; the repository's Home Assistant tooling is unaffected. Run these commands from the repository root:

```sh
cd website
npm ci
cf auth login
npm run check:deploy
npm run deploy
```

Sign in once with the Cloudflare account owning the active `royjen.com` zone; `cf` does not reuse a Wrangler login. Confirm authentication with `cf auth whoami`. Creating the Worker requires Workers creation permission; attaching its hostname requires Workers Routes write permission on that zone. Keep credentials out of source and chat. See [Cloudflare CLI authentication](https://developers.cloudflare.com/cf/get-started/#sign-in) and [Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/).

`check:deploy` type-checks both configuration files, builds the public assets, and runs `cf deploy --dry-run` without uploading. `npm run build` produces Cloudflare Build Output in `.cloudflare/output/v0/`. `npm run preview` serves the packaged assets through `cf dev`; use the local URL printed by the CLI. Both `cf` and its build implementation are pinned because `cf` is in beta.

The build copies only the landing HTML, public screenshot, official Home Assistant logomark, robots.txt, sitemap.xml and header rules. The logo's separate copyright and trademark notice is recorded in [assets/NOTICE.md](assets/NOTICE.md). Repository files, application code, configuration, dependencies and private QA artifacts are not uploaded. Missing paths return 404. The default workers.dev and version-preview URLs are disabled.

### Automatic deployment from GitHub

The [Website workflow](../.github/workflows/website.yml) runs when website files, the remote preview image, or the workflow change. Pull requests install locked dependencies, type-check configuration, build once and validate that build without credentials. A push to `main` deploys the same checked build to <https://webos.royjen.com/> and compares the public HTML and images with the build output. Production deployments run one at a time. You can also choose **Run workflow** on `main` in [GitHub Actions](https://github.com/sonim1/ha-webos-remote/actions/workflows/website.yml).

One-time setup in [repository Actions secrets](https://github.com/sonim1/ha-webos-remote/settings/secrets/actions):

- `CLOUDFLARE_ACCOUNT_ID`: the account containing `ha-webos-remote-site` and the `royjen.com` zone.
- `CLOUDFLARE_API_TOKEN`: a dedicated deployment API token. Local `cf auth login` credentials are not used by GitHub Actions.

Create the deployment token in [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens). Use only the deployment account and `royjen.com` zone; grant **Account → Workers Scripts → Edit**, **Zone → Workers Routes → Edit** and **Zone → Zone → Read**. If Worker-level scoping is available, restrict Worker editing to `ha-webos-remote-site`. No KV, database, storage or DNS-edit permissions are needed by this static website. Store the token directly as the GitHub secret; never paste it into chat, source, an issue or a workflow file. Follow the [official cf CI guide](https://developers.cloudflare.com/cf/ci/) and [Workers permissions reference](https://developers.cloudflare.com/workers/authorization/workers/).

Missing credentials fail the deployment step with a setup message while leaving the existing public site running. After adding or rotating a secret, rerun the workflow on `main`. Pull requests, including forks, never receive deployment secrets or deploy to production. This workflow does not create Home Assistant releases or change installed Bridge/card versions.

After a deployment, verify the HTTPS page, screenshot, navigation and copy buttons. Compare missing-path 404 responses as well as successful asset responses.

### Roll back a deployment

From `website/`, list deployments and identify the known-good **version ID**, which differs from the deployment ID:

```sh
npm run deployments
```

Restore that version to 100% of traffic:

```sh
npm run rollback -- --versions '[{"version_id":"<KNOWN_GOOD_VERSION_ID>","percentage":100}]'
```

This creates a deployment using existing code and assets. It does not change DNS or restore other resource data. Do not bypass deployment safety checks. Keep the pre-migration version available until the migrated deployment is verified. See [Wrangler-to-cf migration](https://developers.cloudflare.com/cf/wrangler/migrate/) for the configuration conversion and [Worker rollbacks](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/) for limitations.
