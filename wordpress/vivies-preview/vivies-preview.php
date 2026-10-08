<?php
/**
 * Plugin Name: Vivies Private Design Preview
 * Description: Administrator-only, isolated design trial. Does not change your theme, pages or WooCommerce data.
 * Version: 0.1.0
 * Requires at least: 6.4
 * Requires PHP: 7.4
 * License: GPL-2.0-or-later
 */

defined( 'ABSPATH' ) || exit;

add_action( 'admin_menu', 'vivies_trial_admin_menu' );
function vivies_trial_admin_menu() {
    add_management_page( 'Vivies Preview', 'Vivies Preview', 'manage_options', 'vivies-preview', 'vivies_trial_admin_page' );
}

function vivies_trial_admin_page() {
    if ( ! current_user_can( 'manage_options' ) ) {
        wp_die( 'Administrator access required.', '', array( 'response' => 403 ) );
    }
    $url = add_query_arg( 'vivies_design_preview', '1', home_url( '/' ) );
    ?>
    <div class="wrap">
        <h1>Vivies private design trial</h1>
        <p>This preview is visible only to logged-in administrators. Your public theme, homepage, products and orders are unchanged.</p>
        <p><a class="button button-primary" target="_blank" rel="noopener" href="<?php echo esc_url( $url ); ?>">Open Vivies preview</a></p>
        <p>Try the Menu, Search, Contact panel, scrolling and mobile layouts. All images and catalog views remain design placeholders.</p>
        <p>This is a design trial, not the final Elementor/WooCommerce implementation. Checkout and purchasing are unavailable in the preview.</p>
        <p>Close the preview tab to return here. Deactivate or delete this plugin to remove the trial; it stores no settings or content.</p>
        <p>If a caching plugin or CDN caches query-string pages, exclude <code>vivies_design_preview</code> from caching. The preview also sends private, no-store headers.</p>
    </div>
    <?php
}

// Runs only for the explicitly requested preview URL. No public assets or content filters.
add_action( 'template_redirect', 'vivies_trial_render', 0 );
function vivies_trial_render() {
    if ( ! isset( $_GET['vivies_design_preview'] ) || '1' !== $_GET['vivies_design_preview'] ) {
        return;
    }
    if ( ! defined( 'DONOTCACHEPAGE' ) ) {
        define( 'DONOTCACHEPAGE', true );
    }
    nocache_headers();
    header( 'Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0', true );
    header( 'X-Robots-Tag: noindex, nofollow, noarchive', true );
    header( 'Vary: Cookie', false );
    if ( ! current_user_can( 'manage_options' ) ) {
        wp_die( 'This design preview is available only to logged-in administrators.', 'Private preview', array( 'response' => 403 ) );
    }
    status_header( 200 );
    header( 'Content-Type: text/html; charset=UTF-8', true );
    $template = file_get_contents( __DIR__ . '/preview.html' );
    $assets = array( 'styles.css', 'preview.js', 'Vivies.png' );
    foreach ( $assets as $asset ) {
        $path = __DIR__ . '/assets/' . $asset;
        $version = substr( hash_file( 'sha256', $path ), 0, 12 );
        $url = add_query_arg( 'ver', $version, plugins_url( 'assets/' . $asset, __FILE__ ) );
        $template = str_replace( '{{' . $asset . '}}', esc_url( $url ), $template );
    }
    // This bundled template is generated from the reviewed preview, never user input.
    echo $template; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
    exit;
}
