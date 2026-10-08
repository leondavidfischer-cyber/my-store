# VIVIES first design preview

This repository contains the interactive prototype requested for design approval.
It is not a WordPress theme, Elementor import or functioning e-commerce store.

## Publish the design preview with GitHub Pages

In `leondavidfischer-cyber/my-store` on GitHub, open **Settings → Pages**. Under
**Build and deployment**, select **Deploy from a branch**, choose **main** and
**/(root)**, then **Save**. Wait for GitHub to report the deployment and use the
link shown there. Do not assume the site is live before deployment succeeds.
GitHub Pages availability depends on repository visibility and the account plan.

Only the static prototype is hosted. This does not install anything in WordPress
or connect a payment gateway. Relative asset links and hash-based navigation
support hosting under the repository's project path without a custom domain.

## Open the preview

Open `index.html` directly in a modern browser. All navigation works without a
server, network requests or external fonts/images. Downloadable packaging uses
`npm run package`; extract the ZIP and open its `index.html`.

For development, use the existing checkout:

```sh
cd /workspace/my-store
npm start
```

The dependency-free Node server uses port 4173 (`PORT` overrides it). Stop it with
Ctrl+C. It serves only the preview document, CSS, JavaScript and logo and has no commerce endpoints.
No npm install step is needed. Node 18 or later is sufficient.

## Validation

```sh
npm run check
npm test
npm run package
```

Browser tests require Python with Playwright and a Chromium executable. This
cloud machine already supplies both. Tests default to `/usr/bin/chromium` and
port 4173; override with `CHROMIUM_PATH` and `PREVIEW_URL` when necessary.
Run the development server before the browser tests. Screenshots and results
are generated in ignored `artifacts/`. Packaging uses Python's standard library.

Motion checks sample the rendered header and drawer during their fades, verify
outgoing/incoming menu levels, check spacing above parent archive links, and test
closing mid-transition and reduced-motion behavior. The header fades over 420ms,
drawers slide/fade over 480ms, and menu levels fade out over 140ms then in over
280ms. Menu/Search icons are 16px while click targets remain comfortably sized.

The browser suite covers all 33 leaf destinations, parent archives, gender-specific
paths, search, modal keyboard behavior, responsive layouts at 1440/1024/768/390/360,
and extracted-package launch over HTTP. Direct file launch is attempted separately;
the cloud browser blocks file URLs by administrator policy, so local double-click
launch remains unverified here. It does not test WordPress or WooCommerce integration.

## Temporary decisions and scope

- The original transparent `Vivies.png` is used unchanged in the header and footer.
  Its transparent outer margins are clipped by a CSS display frame based on the
  visible artwork bounds (50, 377)–(939, 615) within the 1000×1000 source. The image
  scales uniformly; its visible proportions and source bytes are preserved.
- Available screenshots show the top header, first-level menu, nested Men menu
  and contact panel. Remaining reference states have not been supplied.
- Media areas are abstract neutral placeholders, not final campaign artwork.
- Eight card labels and destinations are temporary; destination selections and
  featured links are listed at the top of `preview.js` for prototype development.
  Final homepage changes will happen in Elementor, not source files.
- Contact email is intentionally unavailable until configured. No address is
  invented. Informational and policy pages contain explicit placeholders.
- Search explores categories only; product search awaits WooCommerce.
- Product layout examples contain no real inventory or prices. Cart and checkout
  are explanatory views. Purchasing is disabled; there is no separate fake cart.
- Palette values are CSS variables for this prototype; the final site will expose
  settings and Elementor controls without requiring source edits.

See [the implementation architecture](docs/architecture.md). Development stops
after the first complete preview for user feedback; packaging for WordPress and
Cloudways deployment remain subsequent approved stages.
