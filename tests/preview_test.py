"""Browser checks for the prototype, not claims of WordPress integration."""
import json
import os
import pathlib
import functools
import http.server
import subprocess
import sys
import tempfile
import threading
import zipfile
from playwright.sync_api import sync_playwright, expect, Error

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = os.environ.get('PREVIEW_URL', 'http://127.0.0.1:4173')
ARTIFACTS = ROOT / 'artifacts'
ARTIFACTS.mkdir(exist_ok=True)
TREE = {
    'Men': {
        'Clothes': ['T-Shirts', 'Polos', 'Long Sleeve Shirts', 'Hoodies', 'Shorts', 'Jeans', 'Casual Pants', 'Suit Set', 'Jackets', 'Gile'],
        'Shoes': None, 'Bags': None, 'Accessories': ['Belts', 'Hats', 'Sunglasses'],
    },
    'Women': {
        'Accessories': ['Belts', 'Bracelets', 'Rings', 'Earrings', 'Scarfs', 'Sunglasses'],
        'Bags': None, 'Shoes': None, 'Heels': None,
        'Clothes': ['T-Shirts', 'Tank Tops', 'Vests', 'Sweaters', 'Skirts', 'Trousers', 'Jeans', 'Dress', 'Jackets'],
    },
}
checks = []
errors = []
blocked = []
def passed(label):
    checks.append(label)
    print('PASS:', label)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE)
    expect(page.locator('.category-card')).to_have_count(8)
    expect(page.locator('.feature-card')).to_have_count(4)
    assert page.locator('.category-grid').evaluate('(el) => getComputedStyle(el).gridTemplateColumns.split(" ").length') == 4
    order = page.locator('#main > section').evaluate_all('(els) => els.map(el => el.className)')
    assert order == ['hero', 'section categories-section', 'editorial first', 'section featured', 'editorial second']
    passed('Exact homepage section order, eight category cards, four feature cards, four desktop columns')

    page.evaluate('window.scrollTo(0, 500)')
    expect(page.locator('#header')).to_have_class('header scrolled')
    assert page.locator('#header').bounding_box()['y'] == 0
    page.evaluate('window.scrollTo(0, 0)')
    expect(page.locator('#header')).to_have_class('header')
    passed('Fixed header changes background on scroll and returns to transparent at the top')

    for gender, groups in TREE.items():
        for group, leaves in groups.items():
            for leaf in (leaves or [None]):
                page.goto(BASE)
                page.get_by_role('button', name='Menu', exact=True).click()
                expect(page.locator('.menu-items > *')).to_have_text(['Men›', 'Women›'])
                page.locator('#panel').get_by_role('button', name=gender, exact=True).click()
                visible = page.locator('.menu-items > *').all_text_contents()
                assert [x.replace('›', '') for x in visible] == list(groups)
                if leaves:
                    page.locator('#panel').get_by_role('button', name=group, exact=True).click()
                    assert [x.replace('›', '') for x in page.locator('.menu-items > *').all_text_contents()] == leaves
                    page.locator('#panel .menu-items').get_by_role('link', name=leaf, exact=True).click()
                    expect(page.locator('h1')).to_have_text(leaf)
                else:
                    page.locator('#panel .menu-items').get_by_role('link', name=group, exact=True).click()
                    expect(page.locator('h1')).to_have_text(group)
                expect(page.locator('.breadcrumb')).to_contain_text(gender)
                expect(page.locator('.breadcrumb')).to_contain_text(group)
                expect(page.locator('.empty-state')).to_contain_text('Catalog not connected')
    passed('All 33 leaf destinations navigate correctly; exact hierarchy and requested menu order preserved')

    # Gender paths and branch archives are distinct even when labels match.
    for gender in ('men', 'women'):
        for group, leaf in [('clothes', 't-shirts'), ('accessories', 'sunglasses')]:
            page.goto(f'{BASE}/#/category/{gender}/{group}/{leaf}')
            expect(page.locator('.page-intro')).to_contain_text(gender.title())
    for gender, groups in TREE.items():
        page.goto(f'{BASE}/#/category/{gender.lower()}')
        expect(page.locator('.subcategories a')).to_have_count(len(groups))
        for group, leaves in groups.items():
            if leaves:
                page.goto(f'{BASE}/#/category/{gender.lower()}/{group.lower()}')
                expect(page.locator('.subcategories a')).to_have_count(len(leaves))
    passed('Men/Women T-Shirts and Sunglasses routes remain distinct; branch archives list correct subcategories')

    page.goto(BASE)
    menu = page.get_by_role('button', name='Menu', exact=True)
    menu.click()
    page.locator('#panel').get_by_role('button', name='Men', exact=True).click()
    page.locator('#panel').get_by_role('button', name='Clothes', exact=True).click()
    page.get_by_role('button', name='Back to previous menu level').click()
    expect(page.locator('#panel-title')).to_have_text('Men')
    page.get_by_role('button', name='Back to previous menu level').click()
    expect(page.locator('#panel-title')).to_have_text('Explore Vivies')
    assert page.locator('#site').evaluate('(el) => el.inert')
    assert page.evaluate('document.body.style.overflow') == 'hidden'
    page.locator('#close').focus()
    page.keyboard.press('Shift+Tab')
    assert page.evaluate('document.activeElement.closest("#panel") !== null')
    page.keyboard.press('Tab')
    expect(page.locator('#close')).to_be_focused()
    page.keyboard.press('Escape')
    expect(menu).to_be_focused()
    assert not page.locator('#site').evaluate('(el) => el.inert')
    menu.click()
    page.locator('#overlay').click(position={'x': 1300, 'y': 500})
    expect(menu).to_be_focused()
    menu.click()
    page.get_by_role('button', name='Close panel').click()
    expect(menu).to_be_focused()
    passed('Back navigation, inert background, scroll lock, focus trapping/restoration, Escape, overlay and Close')

    page.get_by_role('button', name='Contact us', exact=True).click()
    expect(page.locator('#panel')).to_have_class('panel right open')
    expect(page.locator('#panel')).to_contain_text('Contact email awaiting configuration.')
    assert page.locator('#panel').bounding_box()['width'] == 720
    page.locator('#panel').get_by_role('link', name='FAQ', exact=True).click()
    expect(page.locator('h1')).to_have_text('FAQ')
    passed('Half-width right contact panel and FAQ destination; missing email clearly identified')

    page.get_by_role('button', name='Search', exact=True).click()
    page.get_by_role('searchbox').fill('men sunglasses')
    expect(page.locator('.search-results a')).to_have_count(1)
    expect(page.locator('.search-results a')).to_have_attribute('href', '#/category/men/accessories/sunglasses')
    page.get_by_role('searchbox').fill('women sunglasses')
    expect(page.locator('.search-results a')).to_have_attribute('href', '#/category/women/accessories/sunglasses')
    page.get_by_role('searchbox').press('Enter')
    expect(page.locator('h1')).to_have_text('Search')
    expect(page.get_by_role('searchbox')).to_have_value('women sunglasses')
    page.get_by_role('searchbox').fill('<script>alert(1)</script>')
    expect(page.locator('.search-results a')).to_have_count(0)
    assert page.locator('#main script').count() == 0
    passed('Live category search, gender distinction, results page, empty results and safe user text')

    page.goto(BASE)
    page.get_by_role('button', name='Shop Now', exact=True).click()
    expect(page.locator('.menu-items > *')).to_have_count(2)
    expect(page.locator('#panel-title')).to_have_text('Explore Vivies')
    page.keyboard.press('Escape')
    passed('Shop Now reuses the complete menu hierarchy')

    for width in [1440, 1024, 768, 390, 360]:
        page.set_viewport_size({'width': width, 'height': 900})
        page.goto(BASE)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
        logo = page.locator('.wordmark').bounding_box()
        assert abs(logo['x'] + logo['width']/2 - width/2) < 1
        left = page.locator('.header-left').bounding_box()
        right = page.locator('.header-right').bounding_box()
        assert left['x'] + left['width'] <= logo['x'] and logo['x'] + logo['width'] <= right['x']
        assert page.locator('.category-grid').evaluate('(el) => getComputedStyle(el).gridTemplateColumns.split(" ").length') == (2 if width <= 768 else 4)
        page.screenshot(path=str(ARTIFACTS/f'homepage-{width}.png'), full_page=True)
        page.get_by_role('button', name='Menu', exact=True).click()
        page.locator('#panel').get_by_role('button', name='Men', exact=True).click()
        page.locator('#panel').get_by_role('button', name='Clothes', exact=True).click()
        expect(page.locator('#panel .menu-items a')).to_have_count(10)
        assert page.locator('#panel').bounding_box()['width'] <= width
        page.locator('#panel').evaluate('(el) => el.scrollTop = el.scrollHeight')
        expect(page.locator('#panel').get_by_role('link', name='Gile', exact=True)).to_be_in_viewport()
        page.keyboard.press('Escape')
        for route in ['category/women/clothes/skirts', 'product/simple', 'product/variable', 'cart', 'checkout', 'page/faq']:
            page.goto(f'{BASE}/#/{route}')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, route)
        passed(f'{width}px: centered logo without overlaps, grids, long menu, page layouts and no horizontal overflow')

    page.goto(f'{BASE}/#/product/variable')
    page.locator('#size').select_option(label='M · placeholder')
    expect(page.locator('#variation-status')).to_contain_text('M · placeholder selected')
    expect(page.get_by_role('button', name='Add to Cart · not connected')).to_be_disabled()
    page.goto(f'{BASE}/#/cart')
    expect(page.locator('h1')).to_have_text('Shopping bag')
    page.get_by_role('link', name='View checkout placeholder').click()
    expect(page.locator('h1')).to_have_text('Checkout')
    assert page.locator('input').count() == 0
    passed('Simple/variable layout views; honest unconnected cart/checkout without personal-data collection')

    page.emulate_media(reduced_motion='reduce')
    page.get_by_role('button', name='Menu', exact=True).click()
    assert page.locator('#panel').evaluate('(el) => getComputedStyle(el).transitionDuration') == '0s'
    page.keyboard.press('Escape')
    passed('Reduced-motion preference suppresses transitions')

    # All homepage and footer links resolve to a named view.
    page.goto(BASE)
    hrefs = page.locator('#site a[href^="#/"]').evaluate_all('(els) => [...new Set(els.map(el => el.getAttribute("href")))]')
    for href in hrefs:
        page.goto(BASE + '/' + href)
        expect(page.locator('h1')).not_to_have_text('Page not found')
    passed('All homepage tiles and footer destinations resolve')
    # The downloaded preview must run by opening index.html, without a server.
    try:
        page.goto((ROOT / 'index.html').as_uri())
        page.get_by_role('button', name='Menu', exact=True).click()
        expect(page.locator('.menu-items > *')).to_have_count(2)
        passed('Direct file preview launch')
    except Error as error:
        if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(error):
            raise
        blocked.append('Direct file:// launch is blocked by the cloud browser policy; local double-click launch is unverified.')
        print('BLOCKED:', blocked[-1])
    # A failed policy navigation can leave the Chromium error page navigating.
    # Use a new page for the independent extracted-package check.
    page.close()
    page = browser.new_page(viewport={'width': 390, 'height': 900})
    page.on('pageerror', lambda error: errors.append(str(error)))
    # Test the actual downloadable package through a temporary HTTP server.
    subprocess.run([sys.executable, str(ROOT / 'tools/package_preview.py')], check=True)
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    with tempfile.TemporaryDirectory(prefix='vivies-package-') as directory:
        with zipfile.ZipFile(ARTIFACTS / 'vivies-preview.zip') as package:
            package.extractall(directory)
        handler = functools.partial(QuietHandler, directory=directory)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            page.goto(f'http://127.0.0.1:{server.server_port}/vivies-preview/index.html')
            page.get_by_role('button', name='Menu', exact=True).click()
            expect(page.locator('.menu-items > *')).to_have_count(2)
            page.keyboard.press('Escape')
            page.get_by_role('button', name='Search', exact=True).click()
            page.get_by_role('searchbox').fill('skirts')
            expect(page.locator('.search-results a')).to_have_count(1)
            passed('Extracted downloadable ZIP launches with working navigation and search over HTTP')
        finally:
            server.shutdown()
            server.server_close()
    assert not errors, errors
    passed('No JavaScript runtime errors during the browser suite')
    browser.close()

(ARTIFACTS / 'test-results.json').write_text(json.dumps({'passed': checks, 'blocked': blocked, 'runtime_errors': errors}, indent=2))
print(f'Completed {len(checks)} check groups; {len(blocked)} blocked check. WordPress, WooCommerce and payment tests remain unrun.')
