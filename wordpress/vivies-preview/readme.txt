=== Vivies Private Design Preview ===
Requires at least: 6.4
Requires PHP: 7.4
Stable tag: 0.1.0
License: GPL-2.0-or-later

Administrator-only design trial. Not a production storefront or Elementor template.

== Installation ==
1. In WordPress, open Plugins > Add New Plugin > Upload Plugin.
2. Upload vivies-preview.zip (keep the ZIP compressed), install and activate.
3. Open Tools > Vivies Preview > Open Vivies preview.
4. Close the preview tab to return to the dashboard.

Only administrators with manage_options can open the preview URL. It sends
private/no-store headers and uses DONOTCACHEPAGE. If your host/CDN caches logged-in
query-string requests despite these controls, exclude vivies_design_preview from
caching before use. Do not share administrator accounts.

No theme is switched. No posts, settings, categories, products or orders are
created or changed. No activation, deactivation or uninstall mutations are used.
Assets are loaded exclusively on the isolated preview page. Deactivate and delete
the plugin to remove it. The original transparent logo is bundled unchanged.

== Trial scope ==
This preserves the standalone preview styling, navigation and motion in an
isolated WordPress page. Images, prices and products are placeholders; search
explores preview categories; purchasing is disabled. Your actual store remains
outside the trial. This does not import editable Elementor containers or connect
the WooCommerce catalog, cart or checkout. Those belong to the next implementation
stage after design review.
