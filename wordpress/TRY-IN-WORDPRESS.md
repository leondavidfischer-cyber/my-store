# Try the design in WordPress

This is an **administrator-only design trial**, packaged as a plugin. It keeps
your public theme and homepage in place. It is not the final editable Elementor
homepage or connected WooCommerce storefront.

1. Download `vivies-preview.zip`. Leave it compressed.
2. Sign in to WordPress as an administrator.
3. Open **Plugins → Add New Plugin → Upload Plugin**.
4. Choose the ZIP, click **Install Now**, then **Activate Plugin**.
5. Open **Tools → Vivies Preview → Open Vivies preview**.

The preview opens in another tab. Try scrolling, Menu → Men → Clothes, Search,
Contact us and a narrow/mobile window. Customers and non-administrator accounts
cannot open the design page. To remove it, deactivate and delete the plugin.

Some managed WordPress sites restrict plugin uploads. If Upload Plugin is absent,
use your host's supported plugin installation process; do not change hosting
security settings just for this trial. An existing full-page cache/CDN should
exclude the `vivies_design_preview` query parameter if it ignores WordPress's
logged-in bypass and private/no-store response headers.

All imagery, products and prices in this preview are still placeholders.
Purchasing is disabled in the trial. Search is for preview categories. The next
stage is a maintainable theme/plugin integration, native editable Elementor
homepage sections and native WooCommerce products, search, cart and checkout.

## For developers

Build: `python tools/package_wordpress_trial.py`.

Integration check: `python tests/wordpress_trial_test.py`. Requires Docker,
Python Playwright and `/usr/bin/chromium`; choose another unused loopback port
with `WP_TRIAL_PORT` if 4175 is busy. Pull `wordpress:php8.3-apache` and
`mariadb:11.4` first. The test creates its own disposable database/WordPress
containers with generated test-only credentials, uploads the actual ZIP through
the dashboard, and removes its containers/volumes/network in a finally block.
It never connects to the user's WordPress site.

The plugin itself stores no options or content and uses no activation/uninstall
mutations. It registers one capability-protected Tools page and an isolated
`template_redirect` handler for the requested preview URL. Its standalone
document intentionally excludes theme and third-party frontend scripts/styles,
so this verifies the design within WordPress rather than compatibility of the
eventual storefront with every live plugin. Assets and the original logo are
bundled from the same reviewed frontend; asset URLs have content-hash versions.

Verified in disposable WordPress 7.1.3/PHP 8.3: actual dashboard ZIP upload and
activation, PHP syntax, administrator access, denied visitor/editor access,
private cache/noindex headers, unchanged public theme/front-page/content/taxonomy,
original logo, menu/search/contact interactions, five viewport sizes, no browser
script errors, and clean deactivation. The user's live site's plugin stack,
hosting cache and WordPress version have not been tested.
