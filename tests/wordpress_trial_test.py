"""Install the actual ZIP into disposable WordPress and verify private isolation.

Requires Docker, Python Playwright and /usr/bin/chromium. Never targets a live site.
"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
TAG = 'vivies-trial-' + secrets.token_hex(4)
DB, WP, NET = TAG + '-db', TAG + '-wp', TAG + '-net'
PORT = int(os.environ.get('WP_TRIAL_PORT', '4175'))
URL = f'http://127.0.0.1:{PORT}'
PASSWORD = secrets.token_urlsafe(24)


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True, stderr=subprocess.STDOUT).strip()


def php(code):
    return docker('exec', WP, 'php', '-r', code)


def snapshot():
    # WordPress creates dashboard Quick Draft auto-drafts on admin/editor login.
    # Compare actual content, excluding those core-generated empty drafts.
    return json.loads(php("require '/var/www/html/wp-load.php'; global $wpdb; echo json_encode(array('theme'=>get_option('stylesheet'),'front'=>get_option('show_on_front'),'posts'=>$wpdb->get_var(\"SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_status <> 'auto-draft'\"),'terms'=>$wpdb->get_var('SELECT COUNT(*) FROM '.$wpdb->terms)));"))


try:
    docker('network', 'create', NET)
    docker('run', '-d', '--name', DB, '--network', NET, '-e', 'MARIADB_RANDOM_ROOT_PASSWORD=1', '-e', 'MARIADB_DATABASE=wordpress', '-e', 'MARIADB_USER=wordpress', '-e', f'MARIADB_PASSWORD={PASSWORD}', 'mariadb:11.4')
    docker('run', '-d', '--name', WP, '--network', NET, '-p', f'127.0.0.1:{PORT}:80', '-e', f'WORDPRESS_DB_HOST={DB}', '-e', 'WORDPRESS_DB_USER=wordpress', '-e', f'WORDPRESS_DB_PASSWORD={PASSWORD}', '-e', 'WORDPRESS_DB_NAME=wordpress', '-e', f'VIVIES_TEST_PASSWORD={PASSWORD}', 'wordpress:php8.3-apache')
    for attempt in range(60):
        try:
            with urlopen(URL + '/wp-admin/install.php', timeout=2) as response:
                if response.status == 200:
                    break
        except (URLError, HTTPError, TimeoutError, ConnectionError):
            pass
        time.sleep(0.5)
    else:
        raise RuntimeError('Disposable WordPress did not start')
    php("define('WP_INSTALLING',true); require '/var/www/html/wp-load.php'; require '/var/www/html/wp-admin/includes/upgrade.php'; wp_install('Vivies trial test','vivies_trial_admin','trial@example.invalid',false,'',getenv('VIVIES_TEST_PASSWORD')); update_option('siteurl','" + URL + "'); update_option('home','" + URL + "');")
    print('Installed disposable WordPress', php("require '/var/www/html/wp-load.php'; echo $wp_version;"))
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        page.goto(URL + '/wp-login.php')
        page.locator('#user_login').fill('vivies_trial_admin')
        page.locator('#user_pass').fill(PASSWORD)
        page.locator('#wp-submit').click()
        page.wait_for_url('**/wp-admin/')
        page.goto(URL + '/wp-admin/plugin-install.php?tab=upload')
        baseline = snapshot()
        page.locator('#pluginzip').set_input_files(str(ROOT / 'wordpress/vivies-preview.zip'))
        page.locator('#install-plugin-submit').click()
        page.get_by_role('link', name='Activate Plugin').click()
        assert 'No syntax errors' in docker('exec', WP, 'php', '-l', '/var/www/html/wp-content/plugins/vivies-preview/vivies-preview.php')
        after = snapshot()
        assert after == baseline, f'Activation changed theme, front page, posts or taxonomy: {baseline} -> {after}'
        page.goto(URL + '/wp-admin/tools.php?page=vivies-preview')
        expect(page.get_by_role('heading', name='Vivies private design trial')).to_be_visible()
        link = page.get_by_role('link', name='Open Vivies preview').get_attribute('href')
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        response = page.goto(link)
        assert response.status == 200
        assert 'no-store' in response.headers['cache-control'] and 'private' in response.headers['cache-control']
        assert 'noindex' in response.headers['x-robots-tag']
        expect(page.locator('h1')).to_have_text('Your campaign title')
        assert page.locator('.wordmark img').get_attribute('src').startswith(URL + '/wp-content/plugins/vivies-preview/assets/')
        assert page.locator('.wordmark img').evaluate('(img) => img.complete && img.naturalWidth === 1000')
        page.get_by_role('button', name='Menu', exact=True).click()
        page.get_by_role('button', name='Men', exact=True).click()
        page.get_by_role('button', name='Clothes', exact=True).click()
        page.get_by_role('link', name='T-Shirts', exact=True).click()
        expect(page.locator('h1')).to_have_text('T-Shirts')
        page.get_by_role('button', name='Search', exact=True).click()
        page.get_by_role('searchbox').fill('women bags')
        expect(page.locator('#panel-content').get_by_role('link', name='Bags')).to_be_visible()
        page.get_by_role('button', name='Close panel').click()
        page.get_by_role('button', name='Contact us', exact=True).click()
        expect(page.locator('#panel-title')).to_have_text('Contact us')
        page.get_by_role('button', name='Close panel').click()
        for width in (1440, 1024, 768, 390, 360):
            page.set_viewport_size({'width': width, 'height': 1000})
            page.goto(link)
            expect(page.locator('h1')).to_have_text('Your campaign title')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}'
            box = page.locator('.wordmark').bounding_box()
            assert abs(box['x'] + box['width'] / 2 - width / 2) < 2
        assert not errors, errors
        # Requests without an administrator session cannot access the design.
        anonymous = browser.new_context()
        denied = anonymous.request.get(link)
        assert denied.status == 403 and 'Your campaign title' not in denied.text()
        assert 'no-store' in denied.headers['cache-control']
        public = anonymous.request.get(URL + '/')
        assert public.status == 200 and 'vivies-preview/assets' not in public.text()
        php("require '/var/www/html/wp-load.php'; wp_insert_user(array('user_login'=>'trial_editor','user_pass'=>getenv('VIVIES_TEST_PASSWORD'),'role'=>'editor')); ")
        editor = browser.new_context()
        editor_page = editor.new_page()
        editor_page.goto(URL + '/wp-login.php')
        editor_page.locator('#user_login').fill('trial_editor')
        editor_page.locator('#user_pass').fill(PASSWORD)
        editor_page.locator('#wp-submit').click()
        editor_page.wait_for_url('**/wp-admin/')
        assert editor.request.get(link).status == 403
        php("require '/var/www/html/wp-load.php'; require_once '/var/www/html/wp-admin/includes/plugin.php'; deactivate_plugins('vivies-preview/vivies-preview.php');")
        assert snapshot() == baseline
        assert 'vivies-preview/assets' not in context.request.get(link).text()
        browser.close()
    print('PASS: ZIP upload/activation, original logo, navigation/search/contact, 5 viewports, admin-only access, private cache headers, unchanged public theme/content, clean deactivation.')
finally:
    for container in (WP, DB):
        subprocess.run(['docker', 'rm', '-f', '-v', container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['docker', 'network', 'rm', NET], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
