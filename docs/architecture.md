# Proposed WordPress implementation — after preview approval

## Platform

Keep Cloudways, WordPress, WooCommerce and Elementor Free. Use a Hello Elementor
child theme for shared markup, the fixed header/footer, responsive styling and
WooCommerce support. A small VIVIES companion plugin owns reusable functionality
and settings. Do not modify core or dependency files.

The standalone preview establishes layout and interaction behavior only.
An optional [administrator-only WordPress trial](../wordpress/TRY-IN-WORDPRESS.md)
now embeds that same design in an isolated plugin page without replacing the
public theme. This trial is not an importable Elementor template or a production
WooCommerce integration.
See [reference review and implementation mapping](reference-review.md) for the
latest preview refinement and the remaining live-reference access limitation.

## Editing responsibilities

| Area | Editing interface | Implementation |
| --- | --- | --- |
| Hero | Elementor Free | Native container with editable image, sizing and visibility controls; test optional native video support before promising it |
| Shop by Category heading and eight cards | Elementor Free | Native responsive containers, image and heading widgets; each card is individually editable/reorderable |
| Category destination chooser | Elementor widget controls | If a native link control is insufficient for selecting taxonomy terms, use a small category-card widget with editable media, title, term and style controls |
| First and second editorial images | Elementor Free | Separate native image widgets/containers with image and alt-text controls |
| Four featured tiles | Elementor Free | Native image and text widgets with editable links; product links use real WooCommerce permalinks |
| Shop Now | Elementor Free | Native button with documented action class, or a small widget exposing the caption and styles; opens the shared navigation |
| Logo, header settings and palette | WordPress settings | Media-library logo selection; dimensions preserve source proportions; configurable colors and spacing |
| Drawer labels and hierarchy | WooCommerce categories + WordPress settings | Stable term IDs, explicit sibling ordering, public archive links generated with WordPress functions |
| Contact panel | WordPress settings | Configurable email and selected Contact/FAQ pages; no fabricated details |
| Footer | WordPress menus/settings | Editable Help and Information link groups; policy content remains in native editable pages |
| Products, prices, stock, categories, sizes | WooCommerce | Native products, taxonomy, attributes and variations |
| Archives and product layouts | Child-theme styling + WooCommerce hooks | Preserve native pagination, prices, gallery, quantity, variation and stock logic |
| Cart, checkout, orders | WooCommerce | Native cart/checkout pages and supported gateway configuration; no custom payment processor |

Elementor Free does not supply Pro Theme Builder for visually designing global
headers/footers or WooCommerce archive/product templates. These areas will have
WordPress settings and maintainable theme integration. Custom widgets are only
individually draggable widgets; their internal structure is not a set of native
draggable elements. Most homepage content remains genuinely native.

Optional Elementor Pro benefits: Theme Builder editing of the global header and
footer, and its WooCommerce template tools for archive/product presentation.
The bespoke progressive drawer still needs custom behavior and testing. Pro is
not required by the proposed implementation.

## Taxonomy and navigation

Create the exact requested `product_cat` tree through a capability-protected,
nonce-checked setup action. Make it idempotent using parent-aware term lookup and
stable slugs such as `men-clothes-t-shirts` and `women-clothes-t-shirts`. Preserve
visible labels including Gile, Scarfs and Dress. Do not reuse ambiguous leaf names
across genders or duplicate existing correctly mapped terms. Validate collisions
before creation, report conflicts instead of silently rewriting existing data.

Generate links from term IDs, not hardcoded archive URLs. A WordPress setting
stores explicit order matching the brief. Men and Women are the only initial
drawer choices. Clothes and Accessories progressively reveal their child terms;
Shoes/Bags/Heels open their own archives. Parent archives can use native descendant
listing, while leaf archives display their own assigned catalog.

## Interaction and accessibility

Use small vanilla JavaScript for the header fade, left/right panels and shared
Shop Now navigator. Support background inertness, scroll locking, Escape,
overlay/Close controls, focus trapping/restoration and reduced motion. Long menus
scroll internally. Logo centering is independent of unequal control groups.

Use native product search (`post_type=product`), rendered results and product
permalinks. Use WooCommerce cart fragments or Store API/cart events appropriate
to the installed version; verify count updates for both classic and block-based
cart/checkout behavior rather than assuming event compatibility.

## Remaining stages and validation

1. Present the prototype, receive feedback, and revise only requested areas.
2. After approval, build the child theme, companion plugin and genuine Elementor
   templates against compatible installed WordPress/WooCommerce/Elementor versions.
3. Test template editing, safe category initialization, archive assignment, simple
   and variable products, catalog search, cart count/quantity/removal and checkout.
   Use clearly labeled development fixtures, never presented as real inventory.
4. Run PHP syntax and integration checks, browser/accessibility checks and the five
   requested viewport checks. Verify installable ZIPs and supported Elementor JSON
   imports in an actual WordPress instance.
5. Provide upload/import/setup instructions and test in Cloudways staging. Secure
   access can be arranged at that stage; credentials are never requested in chat.
6. Live deployment requires explicit user approval. Payment methods and credentials
   are configured later through WooCommerce; payment testing is a separate outcome.

Current untested capabilities: WordPress installation, Elementor editing/import,
real WooCommerce category assignment, catalog search, cart transactions, checkout,
orders, gateways, Cloudways caching and deployment. No production packages have
been finalized at this preview stage.
